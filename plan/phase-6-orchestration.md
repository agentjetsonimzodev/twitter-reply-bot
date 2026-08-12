# Phase 6 — Orchestration (main loop)

> Wire the modules together: search → dedupe → generate → post → mark → log.

## Status: 🔴 Todo

## Goal

A `bot/main.py` that runs a full pipeline pass: given keywords + config, finds tweets, generates replies, posts them, and respects all caps/jitter.

## Tasks

- [ ] `run_once(config) -> RunSummary` — one full pass
  - For each keyword in `BOT_KEYWORDS`:
    1. Search (via reads)
    2. Filter out already-replied (via store)
    3. For each remaining tweet (up to `BOT_MAX_REPLIES_PER_RUN`):
       - Generate reply (via ai)
       - Length check + bad-reply check
       - Post reply (via writes)
       - Mark replied (via store)
       - Increment monthly count
       - Jittered sleep (5-30s)
- [ ] CLI flags (use `argparse`):
  - `--dry-run` (skip the post step, log what would have been posted)
  - `--once` (single pass, exit)
  - `--max-replies N` (override config)
  - `--keyword X` (override config for testing, comma-separated for multiple)
  - `--verbose` (debug logging)
- [ ] `if __name__ == "__main__":` entrypoint: parse args, call `run_once()` or scheduler (Phase 7)
- [ ] `RunSummary` dataclass: `{found, replied, skipped, errors, started_at, finished_at}`
- [ ] Add `tests/test_main.py`

## Testing

**Unit tests (all modules mocked):**
- [ ] Inject mock `LLMClient`, mock `twikit.Client`, mock `tweepy.Client`, real `store` against `tmp_path` DB
- [ ] Scenarios:
  - 5 tweets found, none replied → 5 replies generated, 5 posts, 5 marks
  - 5 tweets found, 2 already in DB → 3 posts (skipped count = 2)
  - 1 tweet throws in `ai.generate()` → caught, run continues with remaining 4
  - `--max-replies 2` with 5 found → only 2 posts
  - `--dry-run` → 0 calls to `writes.post_reply` (decide: does dry-run still mark DB? See notes)
  - `--keyword "X"` override → only searches for that keyword
  - `RunSummary` returned with correct counts

**Integration test (real everything, sandbox account):**
- [ ] Mark with `@pytest.mark.integration`
- [ ] Use a sandbox X account
- [ ] Set `BOT_KEYWORDS=python` and `--max-replies 1`
- [ ] Verify one real reply was posted
- [ ] Manually delete the reply after the test

**Manual E2E:**
```bash
# dry run first — review what it would do
python -m bot.main --dry-run --once --keyword "indie hacker" --max-replies 3

# then post ONE reply and verify it lands
python -m bot.main --once --keyword "indie hacker" --max-replies 1
```

## Exit criteria

- [ ] `pytest tests/test_main.py` passes
- [ ] Manual E2E with `--dry-run` produces 0-3 sensible replies
- [ ] Manual E2E with one real post lands and looks right
- [ ] All CLI flags work as documented
- [ ] Errors in one step don't cascade (one bad tweet doesn't kill the run)
- [ ] `RunSummary` correctly counts everything

## Notes

- The `try/except per tweet` is critical. One bad AI response or one rate-limited post should not kill the whole run.
- Log every decision: `"skipped {tweet_id}: already replied"`, `"posted {tweet_id} → {reply_id}"`, `"rate limited, sleeping {N}s"`.
- **Design decision for `--dry-run`:** should it mark the DB? Two options:
  - Mark: lets you dry-run repeatedly without re-processing the same tweets (good for iterating on prompts)
  - Don't mark: lets you re-test replies across runs (good for A/B testing prompts)
  - **Recommendation:** don't mark by default; add `--dry-run-mark` flag for the first behavior.
- The `RunSummary` return value should be the input to the daily summary in Phase 8.
