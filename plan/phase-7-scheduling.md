# Phase 7 — Scheduling

> Run the orchestration loop on a schedule with jitter to avoid metronomic timing.

## Status: 🔴 Todo

## Goal

A scheduler that fires `run_once()` on a configurable interval, with random jitter to look human.

## Tasks

- [ ] Pick scheduler:
  - **APScheduler** (in-process, single-machine) — recommended for $5 VPS
  - **system cron + bash wrapper** (simpler, OS-level) — recommended for Raspberry Pi
- [ ] If APScheduler:
  - `from apscheduler.schedulers.blocking import BlockingScheduler`
  - `sched.add_job(run_once, 'interval', minutes=30, jitter=60)`
  - Run in `if __name__ == "__main__"` when `--daemon` flag is set
- [ ] If system cron:
  - Write `scripts/run.sh` (sources venv, runs `python -m bot.main --once`)
  - Add crontab line: `*/30 * * * * /path/to/run.sh >> /var/log/twitter-bot.log 2>&1`
  - Use `flock` to prevent overlapping runs
- [ ] Jitter: 30-min interval + ±5min random offset to fire at `:07`, `:34`, `:58`, etc.
- [ ] Add `tests/test_scheduling.py`

## Testing

- [ ] `pytest tests/test_scheduling.py` with a 1-second interval — verify the job fires multiple times in a few seconds
- [ ] Manual: run `--daemon` for 1 hour, verify the log shows ~2 runs (at 30min interval + jitter)
- [ ] Manual: timestamps in logs are NOT perfectly spaced (jitter verified)
- [ ] Manual: kill the process, restart, verify it resumes
- [ ] If using cron: verify `flock` prevents overlapping runs (start a slow run, verify the second invocation skips)

## Exit criteria

- [ ] Scheduler fires reliably for 24 hours in dev
- [ ] Jitter verified (timestamps not perfectly spaced)
- [ ] Restart-safe (no orphaned state)
- [ ] No overlapping runs (cron + flock case)

## Notes

- **APScheduler is fine for a single-process bot.** If you ever need horizontal scaling, switch to Celery + Redis. But you won't.
- If using cron: use `flock -n /tmp/twitter-bot.lock /path/to/run.sh` to prevent overlapping runs if the previous one is still going.
- The jitter prevents X from seeing "this account posts every 30 minutes on the dot" — a classic bot signal.
- Time zone: use UTC internally, log in your local TZ for human readability.
- **Don't use `interval=30` blindly.** A more organic pattern is something like "fire every 25-45 minutes, more often during US business hours, less at night." Add that in Phase 8+ if needed.
