# Phase 9 — Deployment

> Get the bot running 24/7 on a cheap VPS or Pi.

## Status: 🔴 Todo

## Goal

The bot runs unattended, restarts on crash, and survives reboots.

## Tasks

- [ ] `Dockerfile`:
  - Base: `python:3.11-slim`
  - Copy `requirements.txt`, install
  - Copy `bot/`, `README.md`
  - Non-root user
  - `CMD ["python", "-m", "bot.main", "--daemon"]`
- [ ] `docker-compose.yml`:
  - Mount `.env`, `cookies.json`, `bot.db` as volumes (persist across restarts)
  - `restart: unless-stopped`
  - Resource limits (1 CPU, 512MB RAM is plenty)
- [ ] `scripts/run.sh` (for non-Docker systemd deployment):
  - Sources venv
  - Runs `python -m bot.main --daemon`
  - Logs to `/var/log/twitter-bot/`
- [ ] `deploy/twitter-bot.service` (systemd unit):
  - `Restart=on-failure`
  - `RestartSec=10s`
  - `EnvironmentFile=/etc/twitter-bot/.env`
- [ ] Deployment target:
  - **Hetzner CX22** (~$5/mo, 2GB RAM, EU/US) — recommended
  - DigitalOcean basic droplet (~$6/mo)
  - Raspberry Pi 4/5 at home (free, but you trade uptime for $0)
- [ ] Add `tests/test_deployment.py`

## Testing

- [ ] `docker build -t twitter-reply-bot .` succeeds
- [ ] `docker-compose up` starts, logs show the scheduler ticking
- [ ] `docker-compose down && docker-compose up` — verify `cookies.json` and `bot.db` persist
- [ ] `systemctl status twitter-bot` (if systemd) shows `active (running)`
- [ ] Reboot the VPS, verify the bot comes back up automatically
- [ ] `docker-compose config` (validates compose file syntax)
- [ ] `systemd-analyze verify deploy/twitter-bot.service` (validates unit file)

## Exit criteria

- [ ] Bot runs for 24 hours straight with no manual intervention
- [ ] Reboot the machine → bot comes back up automatically
- [ ] Logs are accessible (`docker logs` or `journalctl`)
- [ ] Volumes persist (`bot.db` and `cookies.json` survive container restarts)
- [ ] Resources stay within limits (check `docker stats`)

## Notes

- **Use Docker if you can.** It makes the dev/prod parity perfect and rolling back is one command.
- The Hetzner CX22 is the sweet spot: $4.85/mo, IPv6, fast NVMe. EU or US regions.
- Don't run Ollama on the same VPS unless you upgrade to a GPU instance. Use OpenAI/Anthropic for LLM calls from the bot.
- Mount `.env` as read-only: `./.env:/app/.env:ro`
- Add a healthcheck: a tiny endpoint or just a "last run timestamp" log line that an external monitor (UptimeRobot, etc.) can ping.
- Backups: `bot.db` is your audit log. Snapshot it weekly (`cron` it). `cookies.json` is sensitive — back it up to a private location only.
- SSH hardening: disable password auth, use keys only, change the default port. Standard VPS hygiene.
