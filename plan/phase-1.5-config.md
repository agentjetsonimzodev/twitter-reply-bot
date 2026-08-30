# Phase 1.5 — Config Loader (`bot/config.py`)

> Single source of truth for the `bot/config.py` design. The 3 code issues (#5 schema, #6 loader, #7 factory) all reference this doc.

## Status

🔴 Todo (in progress; tracks #4, #5, #6, #7)

## Goal

A single `bot/config.py` module that:

- Loads `.env` via `python-dotenv`
- Validates every value via `pydantic` + `pydantic-settings`
- Exposes typed `Settings` (5 nested sub-models)
- Uses `SecretStr` for **every** credential field (no half-SecretStr credential pairs)
- Implements `get_settings()` — a cached factory (call `clear_settings_cache()` after editing `.env` or in tests)
- Raises a clear `ConfigError(ValueError)` on any validation failure, listing ALL problems at once (not just the first)

## Why this design

- **Type safety:** every module gets `settings.x.bearer_token`, `settings.bot.keywords`, etc. — full IDE autocomplete, mypy validation.
- **Single import path:** `from bot.config import get_settings` everywhere.
- **Friendly errors:** all validation problems reported at once; never silent.
- **Per-sub-model env_prefix:** each sub-model reads its own flat env vars (`X_API_KEY`, `TWIKIT_USERNAME`, etc.) — no `__` delimiter needed, no change to `.env.example`.

## Env var loading mechanism

Each sub-model (`XSettings`, `TwikitSettings`, `OpenAISettings`, `AnthropicSettings`, `OllamaSettings`, `BotSettings`, `StorageSettings`) is its own `BaseSettings` with its own `env_prefix`. When `load_settings()` is called, `python-dotenv` populates `os.environ`, then each sub-model independently reads its own keys via pydantic-settings.

The top-level `Settings` is a **plain `BaseModel`** (NOT `BaseSettings`) that composes the sub-models. This keeps the env-var layout flat (no `X__API_KEY` syntax) while still giving us a single typed object.

```python
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

def load_settings(env_file: str | Path = ".env") -> Settings:
    load_dotenv(env_file)  # populates os.environ
    return Settings(
        x=XSettings(),
        twikit=TwikitSettings(),
        llm=LLMSettings(
            openai=OpenAISettings(),
            anthropic=AnthropicSettings(),
            ollama=OllamaSettings(),
        ),
        bot=BotSettings(),
        storage=StorageSettings(),
    )
```

`.env.example` uses the existing flat env var names (`X_API_KEY`, `TWIKIT_USERNAME`, etc.) — no change required.

## API surface

### Imports

```python
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
```

### Sub-models (each is its own `BaseSettings`)

```python
class XSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="X_")
    api_key: SecretStr                 # X_API_KEY
    api_secret: SecretStr              # X_API_SECRET
    access_token: SecretStr            # X_ACCESS_TOKEN
    access_token_secret: SecretStr     # X_ACCESS_TOKEN_SECRET
    bearer_token: SecretStr            # X_BEARER_TOKEN


class TwikitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TWIKIT_")
    username: str                      # TWIKIT_USERNAME
    password: SecretStr                # TWIKIT_PASSWORD
    # The Python field name `totp_secret` is more readable than
    # `tfa_secret` or `two_fa_secret`, but pydantic-settings' default
    # UPPER_SNAKE conversion would produce TWIKIT_TOTP_SECRET. We
    # alias the field to TWIKIT_2FA_SECRET so .env.example stays
    # unchanged while the Python attribute keeps its idiomatic name.
    totp_secret: SecretStr = Field(
        alias="TWIKIT_2FA_SECRET",
        description="TOTP shared secret (base32, no padding) or otpauth:// URL",
    )

    @field_validator("totp_secret")
    @classmethod
    def _validate_totp(cls, v: SecretStr) -> SecretStr:
        # Strip whitespace, remove spaces, uppercase before validation.
        # Real-world TOTP secrets are often pasted with stray whitespace
        # or lowercase letters; without normalization, valid secrets get
        # rejected at setup time.
        raw = v.get_secret_value().strip().replace(" ", "").upper()
        # Accept otpauth:// URIs (RFC 6238). After normalization raw is
        # uppercased, so we compare against the uppercased scheme.
        if raw.startswith("OTPAUTH://"):
            return v
        # Re.fullmatch anchors at start AND end (no trailing-newline
        # ambiguity from $). We intentionally reject "=" padding — RFC
        # 4648 allows it, but no major authenticator app exports padded
        # TOTP secrets; rejecting avoids a class of bugs where a 16-char
        # secret without padding works but a 17+1 padded one doesn't.
        if not re.fullmatch(r"[A-Z2-7]{16,}", raw):
            raise ValueError(
                "must be base32 (≥16 chars from [A-Z2-7], no padding) "
                "or an otpauth:// URL"
            )
        return v


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENAI_")
    api_key: SecretStr | None = None    # OPENAI_API_KEY
    model: str = "gpt-4o-mini"          # OPENAI_MODEL


class AnthropicSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ANTHROPIC_")
    api_key: SecretStr | None = None    # ANTHROPIC_API_KEY
    model: str = "claude-3-5-haiku-latest"  # ANTHROPIC_MODEL


class OllamaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OLLAMA_")
    host: str = "http://localhost:11434"  # OLLAMA_HOST
    model: str = "llama3.1:8b"          # OLLAMA_MODEL
```

### `LLMSettings` (composing model — NOT `BaseSettings`)

```python
class LLMSettings(BaseModel):
    openai: OpenAISettings | None = None
    anthropic: AnthropicSettings | None = None
    ollama: OllamaSettings | None = None

    @model_validator(mode="after")
    def _at_least_one_provider(self) -> "LLMSettings":
        configured: list[str] = []
        # Each sub-model is "configured" iff its required field (api_key
        # for the cloud providers; defaults for Ollama) is non-None.
        # Ollama always counts as configured since all its fields have
        # defaults — a user just sets OLLAMA_MODEL if they want to override.
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

### `BotSettings`

```python
class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")
    keywords: list[str]                       # BOT_KEYWORDS (str split on ",")
    persona: str                              # BOT_PERSONA
    max_replies_per_run: int = 10             # BOT_MAX_REPLIES_PER_RUN
    daily_reply_cap: int = 20                 # BOT_DAILY_REPLY_CAP
    monthly_reply_cap: int = 500              # BOT_MONTHLY_REPLY_CAP
    jitter_min_s: int = 5                     # BOT_JITTER_MIN_S
    jitter_max_s: int = 30                    # BOT_JITTER_MAX_S

    @field_validator("keywords", mode="before")
    @classmethod
    def _split_keywords(cls, v):
        # Accept comma-separated string from env, or pass-through list.
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        return v

    @field_validator("jitter_max_s")
    @classmethod
    def _jitter_order(cls, v: int, info) -> int:
        # info.data has jitter_min_s because it's declared above us in the
        # class body; mode="after" would also work but mode-default
        # matches the surrounding convention.
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

### `StorageSettings` (no env_prefix — uses bare field names in UPPER_SNAKE)

```python
class StorageSettings(BaseSettings):
    # No env_prefix: field "db_path" maps to env var DB_PATH (pydantic
    # default is UPPER_SNAKE_CASE).
    db_path: Path = Path("./bot.db")                # DB_PATH
    cookies_path: Path = Path("./cookies.json")      # COOKIES_PATH
    log_path: Path = Path("./bot.log")              # LOG_PATH
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"  # LOG_LEVEL
```

### Top-level `Settings` (composing model — NOT `BaseSettings`)

```python
class Settings(BaseModel):  # plain BaseModel; sub-models handle their own env loading
    x: XSettings
    twikit: TwikitSettings
    llm: LLMSettings
    bot: BotSettings
    storage: StorageSettings
```

### `ConfigError` and `get_settings()`

```python
class ConfigError(ValueError):
    """Raised when .env is missing or invalid. Lists all problems at once."""


def _format_pydantic_errors(e: ValidationError) -> list[str]:
    """Convert pydantic ValidationError into a flat list of human-readable
    problem strings.

    Contract: must NEVER include the unwrapped value of any SecretStr field.
    The strings end up in error messages that may be logged or printed;
    a leaked secret is unrecoverable. When a SecretStr fails validation,
    emit "<field>: invalid value" rather than the actual content.
    """
    problems: list[str] = []
    for err in e.errors():
        loc = ".".join(str(p) for p in err["loc"])
        msg = err["msg"]
        # pydantic's "input" key carries the raw input that failed — drop
        # it for SecretStr fields, replace with a generic note.
        problems.append(f"{loc}: {msg}")
    return problems


def load_settings(env_file: str | Path = ".env") -> Settings:
    """Build a Settings from an .env file. Raises ConfigError on any failure."""
    env_path = Path(env_file)
    if not env_path.exists():
        raise ConfigError(
            f".env file not found at: {env_path}\n"
            f"Hint: copy .env.example to {env_path} and fill in your values"
        )
    try:
        load_dotenv(env_file)
        return Settings(
            x=XSettings(),
            twikit=TwikitSettings(),
            llm=LLMSettings(
                openai=OpenAISettings(),
                anthropic=AnthropicSettings(),
                ollama=OllamaSettings(),
            ),
            bot=BotSettings(),
            storage=StorageSettings(),
        )
    except ValidationError as e:
        problems = _format_pydantic_errors(e)
        raise ConfigError(
            "Invalid configuration in .env:\n  - " + "\n  - ".join(problems)
        ) from None


@lru_cache(maxsize=1)
def get_settings(env_file: str | Path = ".env") -> Settings:
    """Load and cache Settings from .env.

    Cached for the lifetime of the process. After editing .env, call
    clear_settings_cache() to reload on the next call.
    """
    return load_settings(env_file)


def clear_settings_cache() -> None:
    """Reset the get_settings() cache. Use in tests and after editing .env."""
    get_settings.cache_clear()
```

## Tasks by issue

| Issue | What |
|---|---|
| [#5](https://github.com/agentjetsonimzodev/twitter-reply-bot/issues/5) | Define the 5 sub-models + `Settings` with env_prefix pattern |
| [#6](https://github.com/agentjetsonimzodev/twitter-reply-bot/issues/6) | `.env` loading + custom `ConfigError` aggregation (uses `_format_pydantic_errors`) |
| [#7](https://github.com/agentjetsonimzodev/twitter-reply-bot/issues/7) | `get_settings()` factory + re-exports + integration tests |

## Testing

Each issue has its own test file:

- `tests/test_config_schema.py` (issue #5) — every sub-model, validator, SecretStr handling, env var mapping
- `tests/test_config_loader.py` (issue #6) — `.env` parsing, error aggregation, **no token leak in error messages**
- `tests/test_config_integration.py` (issue #7) — full pipeline, caching, `clear_settings_cache()` semantics

**Coverage target: ≥95% on `bot/config.py` after all 3 issues land.**

## Exit criteria

Phase 1.5 is done when:

- [ ] All 4 issues (#4, #5, #6, #7) merged
- [ ] `pytest tests/ --cov=bot.config` shows ≥95% coverage
- [ ] CI green (Lint + Typecheck + Test)
- [ ] `python -c "from bot import get_settings; print(get_settings().bot.keywords)"` works with a valid `.env`
- [ ] Verified that `Settings(...)` succeeds with only `X_API_KEY=... X_API_SECRET=... X_ACCESS_TOKEN=... X_ACCESS_TOKEN_SECRET=... X_BEARER_TOKEN=... TWIKIT_USERNAME=... TWIKIT_PASSWORD=... TWIKIT_2FA_SECRET=... OPENAI_API_KEY=... BOT_KEYWORDS=... BOT_PERSONA=...` set in the environment (and similar for other providers)

## Notes

### Why `SecretStr` for every credential field?

`SecretStr` prevents accidental leakage:

- `repr(settings.x)` → `XSettings(...)` (no secrets visible)
- `print(settings.x.api_key)` → `**********`
- Explicit unwrap required: `settings.x.api_key.get_secret_value()`

This protects against logging, error messages, and accidental `pprint`. **Every** credential field needs `SecretStr` — half-protecting a credential pair (e.g., `api_key` as `str` and `api_secret` as `SecretStr`) defeats the purpose, because a leaked `api_key` is just as damaging as a leaked `api_secret`.

### Why a custom `ConfigError`?

Pydantic raises `ValidationError` which is verbose and structured (good for libraries, bad for humans). We catch it, extract problem summaries, and re-raise as `ConfigError(ValueError)` with a flat, human-readable message:

```
Invalid configuration in .env:
  - twikit.totp_secret: Value error, must be base32 (≥16 chars from [A-Z2-7], no padding) or an otpauth:// URL
  - llm: Value error, at least one LLM provider (openai, anthropic, ollama) must be configured
  - bot.jitter_max_s: Value error, must be > jitter_min_s (5), got 3
```

**Critical:** `_format_pydantic_errors` must NEVER include the raw input value of a failed `SecretStr` — it strips the `input` key from the error to avoid leaking secrets into error messages.

### Why cache `get_settings()`?

- `load_settings()` does I/O (reads `.env`, runs all validators). Fast but pointless to repeat.
- Modules (`bot/reads`, `bot/writes`, etc.) all call `get_settings()` — caching ensures one validation, many uses.
- `clear_settings_cache()` lets tests start fresh and lets a user pick up `.env` edits after a process restart (in long-running contexts).
- (Note: we do NOT auto-invalidate on `.env` mtime change — that lives in Future work below.)

### Why `Field(alias=...)` for `totp_secret`?

`totp_secret` is more readable than `tfa_secret` or `two_fa_secret`, but with `env_prefix="TWIKIT_"`, pydantic-settings' default UPPER_SNAKE conversion would produce the env var `TWIKIT_TOTP_SECRET`. We use `Field(alias="TWIKIT_2FA_SECRET")` so the Python attribute stays idiomatic while the env var name stays compatible with `.env.example` (which uses `TWIKIT_2FA_SECRET`).

### Why a `Literal` for `log_level`?

Catches typos (`LOG_LEVEL=TRANCE`) at load time instead of failing deep in `logging.basicConfig()`.

### Future work (not in Phase 1.5)

- mtime-based auto-invalidation of `get_settings()` cache (nice-to-have, not blocker)
- Hot-reload `.env` while the bot is running (out of scope)
- Validate LLM API keys are real (we trust the user)
