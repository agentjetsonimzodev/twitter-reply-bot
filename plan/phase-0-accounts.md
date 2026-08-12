# Phase 0 — Accounts & Credentials

> **Manual phase. No code yet.** Goal: get all the keys/tokens you need before building.

## Status: 🔴 Todo

## Goal

Have a working dev environment with all credentials stored in `.env` (never committed) and at least one smoke test passing for each external service.

## Tasks

- [ ] Create dedicated bot X account
  - Use a separate email from your personal X account
  - Username must NOT impersonate a real person
  - Profile pic + bio + 1-2 organic tweets before going further
- [ ] Enable 2FA on the bot account (authenticator app, NOT SMS)
  - **Save the TOTP secret** (the `otpauth://` string, not the 6-digit code) — you need it for `TWIKIT_2FA_SECRET`
- [ ] Age the account 2+ weeks before connecting the bot
  - Manual likes, replies, follows during this period
  - X flags new accounts that immediately start automated activity
- [ ] Apply for X Developer account at https://developer.x.com
  - Use case: "personal automation tool" (or "scheduled content for my brand" if rejected)
  - Approval can take 1-2 weeks
- [ ] Create a Project + App in the Developer Portal
  - App permissions: **Read + Write**
  - **NOT** Elevated access (avoid the $100/mo tier)
- [ ] Run OAuth 1.0a PIN flow (`tweepy` has `OAuth1UserHandler` for this)
  - Capture all 4 tokens: consumer key/secret + access token/secret
  - Store in `.env`
- [ ] Copy `.env.example` → `.env` and fill in:
  - `X_API_KEY`, `X_API_SECRET`
  - `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`, `X_BEARER_TOKEN`
  - `TWIKIT_USERNAME`, `TWIKIT_PASSWORD`, `TWIKIT_2FA_SECRET`
  - Pick ONE LLM provider and fill in its creds

## Testing

This is a **manual phase** — no automated tests, but you do need to verify each credential works end-to-end before moving on.

**Tweepy smoke test** (writes auth):
```python
import tweepy
client = tweepy.Client(bearer_token="YOUR_BEARER_TOKEN")
print(client.get_me())  # should print your bot account
```

**Tweepy OAuth 1.0a smoke test** (user-context auth — required for posting):
```python
import tweepy
auth = tweepy.OAuth1UserHandler("API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
api = tweepy.API(auth)
print(api.verify_credentials())  # should print your bot account
```

**twikit smoke test** (reads auth + cookie persistence):
```python
from twikit import Client
c = Client("en-US")
c.login("bot_username", "bot_password", "TOTP_SECRET")
# verify cookies.json was created
import os; assert os.path.exists("cookies.json")
```

- [ ] All three smoke tests pass
- [ ] `cookies.json` exists locally (proves twikit can authenticate)
- [ ] The bot account can post a test tweet manually via X web UI

## Exit criteria

- [ ] `.env` exists locally with all required values filled
- [ ] All three smoke tests pass
- [ ] `cookies.json` exists
- [ ] The account is at least 2 weeks old OR you've explicitly accepted the risk of starting sooner (not recommended)

## Notes

- **Start this phase FIRST.** X dev approval is slow. You can build/test Phases 1-5 in parallel while waiting.
- **Never use your personal X account.** If the bot gets banned, you lose only the throwaway.
- If the dev account application is rejected, reapply with a more specific use case. Common rejection reasons: vague description, no website, no public profile linked.
- The TOTP secret is reusable — once you have it, you can generate 2FA codes forever. Store it securely (1Password, Bitwarden, etc.).
