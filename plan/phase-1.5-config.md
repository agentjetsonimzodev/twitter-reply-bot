# Phase 1.5 — Config Loader (`bot/config.py`)

> Single source of truth for the `bot/config.py` design. The 3 code issues (#5 schema, #6 loader, #7 factory) all reference this doc.

## Status

🔴 Todo (in progress; tracks #4, #5, #6, #7)

## Goal

A single `bot/config.py` module that:

- Loads `.env` via `python-dotenv`
- Validates every value via `pydantic`
- Exposes typed `Settings` (5 nested sub-models)
- Uses `SecretStr` for sensitive fields (passwords, tokens)
- Implements `get_settings()` — a cached factory that auto-invalidates on `.env` mtime change
- Raises a clear `ConfigError(ValueError)` on any validation failure, listing ALL problems at once (not just the first)

## Why this design

- **Type safety:** every module gets `settings.x.bearer_token`, `settings.bot.keywords`, etc. — full IDE autocomplete, mypy validation.
- **Single import path:** `from bot.config import get_settings` everywhere.
- **Auto-reload in dev:** changing `.env` and re-calling `get_settings()` picks up new values without restart.
- **Friendly errors:** all validation problems reported at once; never silent.

## API surface

### `Settings` (top-level pydantic model)

```python
class Settings(BaseSettings):
    x: XSettings
    twikit: TwikitSettings
    llm: LLMSettings
    bot: BotSettings
    storage: StorageSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

### `XSettings` — X API credentials

```python
class XSettings(BaseModel):
    api_key: str                       # X_API_KEY
    api_secret: SecretStr              # X_API_SECRET
    access_token: str                  # X_ACCESS_TOKEN
    access_token_secret: SecretStr     # X_ACCESS_TOKEN_SECRET
    bearer_token: SecretStr            # X_BEARER_TOKEN
```

### `TwikitSettings` — cookie auth credentials

```python
class TwikitSettings(BaseModel):
    username: str                      # TWIKIT_USERNAME
    password: SecretStr                # TWIKIT_PASSWORD
    totp_secret: SecretStr             # TWIKIT_2FA_SECRET

    @field_validator("totp_secret")
    @classmethod
    def _validate_totp(cls, v: SecretStr) -> SecretStr:
        raw = v.get_secret_value()
        # Accept either base32 (≥16 chars) or otpauth:// URL
        if raw.startswith("otpauth://"):
            return v
        if not re.match(r"^[A-Z2-7]{16,}$", raw):
            raise ValueError(
                "must be base32 (≥16 chars from [A-Z2-7]) or an otpauth:// URL"
            )
        return v
```

### `LLMSettings` — at-least-one-provider validator

```python
class OpenAISettings(BaseModel):
    api_key: SecretStr | None = None
    model: str = "gpt-4o-mini"


class AnthropicSettings(BaseModel):
    api_key: SecretStr | None = None
    model: str = "claude-3-5-haiku-latest"


class OllamaSettings(BaseModel):
    host: str = "http://localhost:11434"
    model: str = "llama3.1:8b"


class LLMSettings(BaseModel):
    openai: OpenAISettings | None = None
    anthropic: AnthropicSettings | None = None
    ollama: OllamaSettings | None = None

    @model_validator(mode="after")
    def _at_least_one_provider(self) -> "LLMSettings":
        configured: list[str] = []
        if self.openai and self.openai.api_key is not None:
            configured.append("openai")
        if self.anthropic and self.anthropic.api_key is not None:
            configured.append("anthropic")
        if self.ollama is not None:
            configured.append("ollama")
        if not configured:
            raise ValueError(
                "at least one LLM provider (openai, anthropic, ollama) must be configured"
            )
        return self
```

### `BotSettings` — behavior

```python
class BotSettings(BaseModel):
    keywords: list[str]                       # BOT_KEYWORDS (str split on "," or list)
    persona: str                              # BOT_PERSONA
    max_replies_per_run: int = 10             # BOT_MAX_REPLIES_PER_RUN
    daily_reply_cap: int = 20                 # BOT_DAILY_REPLY_CAP
    monthly_reply_cap: int = 500              # BOT_MONTHLY_REPLY_CAP
    jitter_min_s: int = 5                     # BOT_JITTER_MIN_S
    jitter_max_s: int = 30                    # BOT_JITTER_MAX_S

    @field_validator("keywords", mode="before")
    @classmethod
    def _split_keywords(cls, v):
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    @field_validator("jitter_max_s")
    @classmethod
    def _jitter_order(cls, v: int, info) -> int:
        min_s = info.data.get("jitter_min_s")
        if min_s is not None and v <= min_s:
            raise ValueError(f"must be > jitter_min_s ({min_s}), got {v}")
        return v

    @field_validator("keywords")
    @classmethod
    def _non_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("at least one keyword is required")
        for k in v:
            if len(k) > 100:
                raise ValueError(f"keyword too long (max 100 chars): {k!r}")
        return v
```

### `StorageSettings` — paths and logging

```python
class StorageSettings(BaseModel):
    db_path: Path = Path("./bot.db")              # DB_PATH
    cookies_path: Path = Path("./cookies.json")    # COOKIES_PATH
    log_path: Path = Path("./bot.log")            # LOG_PATH
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"  # LOG_LEVEL
```

### `ConfigError` and `get_settings()`

```python
class ConfigError(ValueError):
    """Raised when .env is missing or invalid. Lists all problems at once."""


def load_settings(env_file: str | Path = ".env") -> Settings:
    """Build a Settings from an .env file. Raises ConfigError on any failure."""
    try:
        return Settings(_env_file=str(env_file))
    except ValidationError as e:
        # Format the error nicely and raise as ConfigError
        problems = _format_pydantic_errors(e)
        raise ConfigError("\n".join(problems)) from None
    except FileNotFoundError as e:
        raise ConfigError(
            f".env file not found at: {env_file}\n"
            f"Hint: copy .env.example to {env_file} and fill in your values"
        ) from None


@lru_cache(maxsize=1)
def get_settings(env_file: str | Path = ".env") -> Settings:
    """Load and cache Settings from .env. Use clear_settings_cache() in tests."""
    return load_settings(env_file)


def clear_settings_cache() -> None:
    """Reset the get_settings() cache. Use in tests and after editing .env."""
    get_settings.cache_clear()
```

## Tasks by issue

| Issue | What |
|---|---|
| [#5](https://github.com/agentjetsonimzodev/twitter-reply-bot/issues/5) | Define the 5 sub-models + `Settings` (#5) |
| [#6](https://github.com/agentjetsonimzodev/twitter-reply-bot/issues/6) | `.env` loading + custom `ConfigError` aggregation (#6) |
| [#7](https://github.com/agentjetsonimzodev/twitter-reply-bot/issues/7) | `get_settings()` factory + re-exports + integration tests (#7) |

## Testing

Each issue has its own test file:

- `tests/test_config_schema.py` (issue #5) — every sub-model, validator, SecretStr handling
- `tests/test_config_loader.py` (issue #6) — `.env` parsing, error aggregation, no token leak
- `tests/test_config_integration.py` (issue #7) — full pipeline, caching, mtime invalidation

**Coverage target: ≥95% on `bot/config.py` after all 3 issues land.**

## Exit criteria

Phase 1.5 is done when:

- [ ] All 4 issues (#4, #5, #6, #7) merged
- [ ] `pytest tests/ --cov=bot.config` shows ≥95% coverage
- [ ] CI green (Lint + Typecheck + Test)
- [ ] `python -c "from bot import get_settings; print(get_settings().bot.keywords)"` works with a valid `.env`

## Notes

### Why `SecretStr` not `str`?

`SecretStr` prevents accidental leakage:

- `repr(settings.x)` → `XSettings(...)` (no secrets visible)
- `print(settings.x.api_secret)` → `**********`
- Explicit unwrap required: `settings.x.api_secret.get_secret_value()`

This protects against logging, error messages, and accidental `pprint`.

### Why a custom `ConfigError`?

Pydantic raises `ValidationError` which is verbose and structured (good for libraries, bad for humans). We catch it, extract problem summaries, and re-raise as `ConfigError(ValueError)` with a flat, human-readable message:

```
Invalid configuration in .env:
  - TWIKIT_2FA_SECRET: must be base32 (≥16 chars from [A-Z2-7]) or an otpauth:// URL (got '12345')
  - llm: at least one LLM provider (openai, anthropic, ollama) must be configured
  - bot.jitter_max_s: must be > jitter_min_s (5), got 3
```

**Critical:** never include the actual value of `SecretStr` fields in error messages — the message could end up in logs.

### Why cache `get_settings()`?

- `Settings(...)` does I/O (reads `.env`, runs all validators). Fast but pointless to repeat.
- Modules (`bot/reads`, `bot/writes`, etc.) all call `get_settings()` — caching ensures one validation, many uses.
- `clear_settings_cache()` lets tests start fresh.
- (Note: we may upgrade to mtime-based cache invalidation in a future issue.)

### Why a `Literal` for `log_level`?

Catches typos (`LOG_LEVEL=TRANCE`) at load time instead of failing deep in `logging.basicConfig()`.

### Future work (not in Phase 1.5)

- mtime-based auto-invalidation of `get_settings()` cache (nice-to-have, not blocker)
- Hot-reload `.env` while the bot is running (out of scope)
- Validate LLM API keys are real (we trust the user)
