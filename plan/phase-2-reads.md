# Phase 2 — Reads Module (twikit)

> Build the search side: log in via cookies, search tweets by keyword, return clean dicts.

## Status: 🔴 Todo

## Goal

A `bot/reads.py` module that, given a keyword, returns a list of tweet dicts ready to be filtered and replied to.

## Tasks

- [ ] `login(username, password, totp_secret) -> Client`
  - Uses `pyotp` to generate TOTP from secret
  - Persists cookies to `cookies.json` after first login
  - On subsequent runs, loads `cookies.json` if valid (re-login only if cookies expired)
- [ ] `search_tweets(client, keyword, max_results=20) -> list[dict]`
  - Calls `client.search_tweet(keyword, product='Latest')`
  - Returns dicts shaped: `{id, text, author_id, author_username, created_at, lang}`
  - Filters out: retweets, our own tweets, tweets with no text, non-tweet objects
- [ ] `load_cookies(path) / save_cookies(client, path)` helpers
- [ ] Update `bot/main.py` stub to expose a `run_search_phase()` entry point (for testing)
- [ ] Add `tests/test_reads.py`

## Testing

**Unit tests (no network, mocked twikit):**
- [ ] Mock the `twikit.Client` class entirely
- [ ] Test filters: retweets removed, own tweets removed, empty-text tweets removed
- [ ] Test result shape: every dict has `{id, text, author_id, author_username, created_at, lang}`
- [ ] Test cookie load/save round-trip (write JSON, read it back, assert fields)

**Integration test (real network, sandbox account):**
- [ ] `tests/integration/test_reads_live.py` — mark with `@pytest.mark.integration` so it doesn't run in CI by default
- [ ] Hits X with a real search for `"python"` and asserts ≥ 1 result
- [ ] **Use a throwaway test account, NOT your bot account**

**Manual smoke test:**
```python
from bot.reads import login, search_tweets
c = login("bot_user", "pwd", "TOTP_SECRET")
tweets = search_tweets(c, "indie hacker", max_results=5)
for t in tweets:
    print(t["author_username"], "→", t["text"][:80])
```

## Exit criteria

- [ ] `pytest tests/test_reads.py` passes (all unit tests with mocks)
- [ ] Manual smoke test above returns real tweets
- [ ] Cookies persist across restarts (no re-login needed within ~7 days)
- [ ] Search latency < 5s for 20 results on average

## Notes

- **twikit breaks regularly** when X updates their GraphQL endpoints. Budget for ongoing maintenance. If `search_tweet()` raises unexpected errors, check twikit's GitHub for recent issues first.
- **Rate-limit reads aggressively.** Cap at ~60 searches/minute. If you hammer X, the bot account gets throttled or flagged.
- The `product='Latest'` argument skips the "Top" algorithm and gives chronological results — better for finding fresh tweets to reply to.
- The X Free API tier allows ~100 read requests per month. Using twikit for reads is what makes this $0 — don't accidentally switch to tweepy for searches.
