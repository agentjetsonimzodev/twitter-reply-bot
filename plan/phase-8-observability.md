# Phase 8 — Observability & Safety

> Logging, kill switches, quota warnings, and (optional) webhook alerts.

## Status: 🔴 Todo

## Goal

The bot can detect when something is wrong and stop itself, log useful summaries, and (optionally) ping you on Discord/Telegram.

## Tasks

- [ ] Logging setup (`bot/logging_config.py`):
  - `RotatingFileHandler` for `bot.log` (max 10MB, 5 backups)
  - Console handler for `--verbose`
  - Structured format: `2026-08-12 14:23:01 INFO [reads] found 12 tweets for keyword="indie hacker"`
- [ ] Log events:
  - `found N tweets for keyword=K`
  - `skipped tweet T: already replied`
  - `posted reply to T → R`
  - `rate limited, sleeping Ns`
  - `quota warning: 80% of monthly cap used`
  - `kill switch: N consecutive errors, exiting`
- [ ] Consecutive error counter:
  - Increment on any exception in `run_once()`
  - Reset to 0 on successful post
  - If counter ≥ `BOT_MAX_CONSECUTIVE_ERRORS`, exit non-zero (let the scheduler/restart loop handle it)
- [ ] Quota warnings:
  - 80% → WARNING log
  - 95% → ERROR log + skip remaining replies for the day
  - 100% → refuse to post (already in Phase 3, but verify)
- [ ] Optional: webhook alerts
  - Discord or Telegram webhook URL via env
  - Send on: quota warning, kill switch trigger, daily summary
- [ ] Daily summary (in log + optional webhook):
  - `"Day summary: 47 found, 12 replied, 3 errors, 28% monthly quota used"`
- [ ] Add `tests/test_observability.py`

## Testing

- [ ] Force 5 consecutive errors in a test run → confirm bot exits with non-zero code
- [ ] Set `BOT_MONTHLY_REPLY_CAP=10`, manually mark 8 as replied, run → confirm WARNING log
- [ ] Set `BOT_MONTHLY_REPLY_CAP=10`, mark 10, run → confirm skip behavior
- [ ] `--verbose` shows DEBUG logs, normal mode doesn't
- [ ] Log file rotates at 10MB (force it with a smaller test cap or use `time.sleep` mock)
- [ ] Daily summary log has all 4 numbers correct (found/replied/errors/quota)
- [ ] Webhook (if enabled): test with a real Discord/Telegram bot — send a fake event, verify it lands

## Exit criteria

- [ ] All log events fire at the right times
- [ ] Kill switch works (force it to trigger, verify graceful exit)
- [ ] Quota warnings work at 80%, 95%, 100%
- [ ] Log file is parseable (use `jq` or a regex to extract events)
- [ ] Optional: webhook tested with a real Discord/Telegram bot

## Notes

- **Logs are your lifeline.** If something goes wrong at 3am, the log is the only way to figure out what happened. Use UTC timestamps always.
- The kill switch is intentionally simple. If the bot is failing, stop it. Don't try to auto-recover — that leads to spam-blasting when X changes something.
- The 80% / 95% / 100% thresholds give you early warning before you hit hard limits. Don't tune them too tight.
- Webhooks are great for sanity checks but should never be the only failure signal. **Logs are the source of truth.**
- For webhooks, prefer Telegram over Discord for personal alerts — Telegram's free tier is generous, Discord webhooks have rate limits.
- Daily summary should be logged at a fixed time (e.g., 23:55 local), NOT after every run. This is a small scheduler job of its own.
