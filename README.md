# 🐦 Twitter Reply Bot

[![CI](https://github.com/agentjetsonimzodev/twitter-reply-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/agentjetsonimzodev/twitter-reply-bot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

Self-hosted bot that searches tweets by keyword and posts AI-generated replies — **$0 in official X API costs** by splitting reads (scraping via `twikit`) from writes (official API via `tweepy`).

> **Status:** Phase 1 — initial scaffold. No functionality yet.

## 🏗️ Architecture

| Concern | Tool | Why |
|---|---|---|
| Search tweets | `twikit` | Scrapes X's internal GraphQL — bypasses API read limits |
| Post replies | `tweepy` | Official X API, OAuth 1.0a user-context, Free tier writes |
| Dedup + quota | SQLite | Lightweight, no server, WAL mode for concurrency |
| AI replies | OpenAI / Anthropic / Ollama | Pluggable client, swap anytime |
| Scheduling | APScheduler or cron | Run every N minutes with jitter |

## 📋 Phases

See the [plan/](./plan/) folder for per-phase reference docs. TL;DR:

0. Accounts & credentials (manual)
1. **← You are here** — project scaffold
2. Reads module (`twikit`)
3. Writes module (`tweepy`)
4. Reply store (SQLite)
5. AI reply generation
6. Orchestration
7. Scheduling
8. Observability & safety
9. Deployment (Docker / systemd)
10. Testing & docs

## 🚀 Setup

### 1. Clone & install

```bash
git clone https://github.com/agentjetsonimzodev/twitter-reply-bot.git
cd twitter-reply-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 2. Configure

```bash
cp .env.example .env
# edit .env — fill in API keys, bot account creds, keywords, persona
```

### 3. Smoke test (once Phase 2+ lands)

```bash
python -m bot.main --dry-run --once
```

## ⚠️ Safety & Ethics

This bot automates engagement. Use responsibly:

- **Age your account** 2+ weeks with manual activity before running the bot
- **Cap volume** low to start (20–50 replies/day max)
- **Mix in organic activity** (likes, original tweets) so the account doesn't look robotic
- **Never spam** — replies should add genuine value to conversations
- **X's ToS** technically prohibit scraping. `twikit` mitigates this with cookie auth from a dedicated account, but the risk is yours

## 📁 Project structure

```
twitter-reply-bot/
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions: ruff + pytest
├── bot/
│   ├── __init__.py
│   ├── reads.py             # twikit search (Phase 2)
│   ├── writes.py            # tweepy post (Phase 3)
│   ├── store.py             # SQLite (Phase 4)
│   ├── ai.py                # LLM client (Phase 5)
│   ├── config.py            # env loading (Phase 1.5)
│   └── main.py              # orchestration (Phase 6)
├── plan/                    # Per-phase reference docs
├── tests/
│   ├── __init__.py
│   └── test_smoke.py        # Always-passing smoke tests
├── .env.example
├── .gitignore
├── pyproject.toml           # ruff + pytest config
├── requirements.txt         # Production deps
├── requirements-dev.txt     # -r requirements.txt + test/lint tooling
└── README.md
```

## 📝 License

TBD
