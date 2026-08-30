Invalid configuration in .env:
  - twikit.TWIKIT_2FA_SECRET: Value error, must be base32 (≥16 chars from [A-Z2-7], no padding) or an otpauth:// URL
  - llm: Value error, at least one LLM provider (openai, anthropic, ollama) must be configured
  - bot.jitter_max_s: Value error, must be > jitter_min_s (5), got 3
