# Phase 3 — Writes Module (tweepy)

> Build the post side: OAuth 1.0a auth, post reply, rate-limit handling, monthly quota guard.

## Status: 🔴 Todo

## Goal

A `bot/writes.py` module that, given a tweet ID and reply text, posts a reply and returns the new tweet ID — or refuses if quota is exhausted.

## Tasks

- [ ] `init_client() -> tweepy.Client` (v2 API, OAuth 1.0a user-context)
  - Reads `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` from env
- [ ] `post_reply(client, tweet_id, text) -> dict`
  - Calls `client.create_tweet(text=text, in_reply_to_tweet_id=tweet_id)`
  - Returns `{id, text}` from response
  - **Raises** a custom `RateLimitError` on 429
- [ ] `RateLimitError` exception class
  - Carries `reset_at` (Unix timestamp from `x-rate-limit-reset` header)
- [ ] `QuotaExceededError` exception class
  - Raised when monthly cap is hit (before any network call)
- [ ] `wait_for_rate_limit(reset_at)` helper — sleeps until reset
- [ ] Monthly quota check: refuse to post if `monthly_writes` ≥ `BOT_MONTHLY_REPLY_CAP`
- [ ] Add `tests/test_writes.py`

## Testing

**Unit tests (no network, mocked tweepy):**
- [ ] Mock `tweepy.Client.create_tweet`:
  - Returns fake response → assert `post_reply()` returns parsed dict
  - Raises `tweepy.TooManyRequests` → assert `RateLimitError` raised with `reset_at` extracted from headers
- [ ] Test quota guard:
  - Mock `store.get_monthly_count()` returns `BOT_MONTHLY_REPLY_CAP - 1` → should post
  - Mock it returns `BOT_MONTHLY_REPLY_CAP` → should raise `QuotaExceededError` (no network call)
- [ ] Test `wait_for_rate_limit()` math: given `reset_at = now + 30s`, sleep ~30s (use `time.sleep` mock or `monkeypatch`)

**Integration test (real network):**
- [ ] Post a reply to a tweet owned by the bot itself (self-reply chain is the safest test)
- [ ] Verify the new tweet ID comes back
- [ ] **Delete the test reply manually afterward** (or use a sandbox account)

**Manual smoke test:**
```python
from bot.writes import post_reply, init_client
c = init_client()
# reply to a tweet you own first
result = post_reply(c, "YOUR_OWN_TWEET_ID", "smoke test reply")
print(result)
# then delete it from X web UI
```

## Exit criteria

- [ ] `pytest tests/test_writes.py` passes
- [ ] Manual smoke test posts + verifies a real reply
- [ ] 429 handling verified (temporarily exhaust your rate limit to test)
- [ ] Quota guard works (set `BOT_MONTHLY_REPLY_CAP=0` and confirm refusal without network call)

## Notes

- The **Free tier** allows ~1,500 tweets/month at the app level. Keep `BOT_MONTHLY_REPLY_CAP` at 500 to leave headroom.
- The Free tier also has **read** limits (~100/month) — which is why we use twikit for reads.
- **OAuth 1.0a user-context** is the right auth here, not OAuth 2.0. v2 API endpoints accept both, but user-context posting requires 1.0a.
- If you ever see `403 Forbidden` on a post, the most common cause is the app's permissions weren't upgraded to Read+Write in the dev portal.
- Tweepy's exception hierarchy: `tweepy.TooManyRequests` (429) → check `e.response.headers['x-rate-limit-reset']` for the reset time.
