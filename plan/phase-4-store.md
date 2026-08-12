# Phase 4 — Reply Store (SQLite)

> Build the dedupe + quota tracking layer. This is the **easiest phase to test** — pure local logic, no network.

## Status: 🔴 Todo

## Goal

A `bot/store.py` module that, given a SQLite path, provides thread-safe dedupe and monthly quota operations.

## Tasks

- [ ] `init_db(path) -> Connection`
  - Enables WAL mode (`PRAGMA journal_mode=WAL`)
  - Creates tables if they don't exist
- [ ] Tables:
  - `replied_tweets (tweet_id TEXT PRIMARY KEY, replied_at TEXT, original_text TEXT, reply_text TEXT, author_username TEXT, keyword TEXT)`
  - `monthly_writes (year_month TEXT PRIMARY KEY, count INTEGER)`
- [ ] `has_replied(tweet_id) -> bool`
- [ ] `mark_replied(tweet_id, original_text, reply_text, author_username, keyword)` (atomic insert)
- [ ] `get_monthly_count(year_month=None) -> int` (defaults to current `YYYY-MM`)
- [ ] `increment_monthly_count()` (atomic UPSERT)
- [ ] `get_recent_replies(limit=50) -> list[dict]` (for debugging / daily summaries)
- [ ] Add `tests/test_store.py`

## Testing

**This is the most testable phase. Aim for >90% coverage.**

- [ ] Schema creation is idempotent (run `init_db()` twice, no error)
- [ ] `has_replied()` returns False for new IDs, True after `mark_replied()`
- [ ] `mark_replied()` raises `IntegrityError` on duplicate `tweet_id` (use this for atomic check-and-mark)
- [ ] `increment_monthly_count()` correctly handles:
  - First call of the month → INSERT (count=1)
  - Subsequent calls → UPDATE (count=N)
  - Crossing month boundary → new row inserted (test with explicit `year_month` arg)
- [ ] `get_monthly_count()` returns the right value after a mix of inserts and updates
- [ ] WAL mode verified: `PRAGMA journal_mode` returns `wal` after `init_db()`
- [ ] Concurrent test: spawn 10 threads, each inserts a unique tweet, all succeed without deadlock

**Atomic check-and-mark pattern** (used in Phase 6):
```python
def reply_if_new(tweet_id, ...):
    if store.has_replied(tweet_id):
        return False
    try:
        store.mark_replied(tweet_id, ...)
        return True
    except sqlite3.IntegrityError:
        return False  # another process beat us to it
```
- [ ] Test this pattern explicitly with concurrent calls

## Exit criteria

- [ ] `pytest tests/test_store.py` passes with ≥90% coverage on `bot/store.py`
- [ ] Atomic check-and-mark verified (concurrent test passes)
- [ ] WAL mode confirmed
- [ ] No thread-safety bugs

## Notes

- Use `sqlite3` from stdlib — no need for SQLAlchemy here. Keep it simple.
- Store `replied_at` as ISO 8601 string (`datetime.now(timezone.utc).isoformat()`), not Unix int — easier to debug.
- For the monthly counter, use `YYYY-MM` (e.g., `"2026-08"`) as the PK. Reset is automatic when the month rolls over.
- The dedupe table is also your **audit log**. Keep it forever (or until you run out of disk). If a reply gets you in trouble, you can trace back to what you posted.
- The `tests/test_store.py` file should use pytest's `tmp_path` fixture for a real on-disk DB (faster + more representative than `:memory:` for WAL tests).
