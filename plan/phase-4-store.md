# Phase 4 — Reply Store (SQLite)

> Build the dedupe + quota tracking layer. This is the **easiest phase to test** — pure local logic, no network.

## Status: 🔴 Todo

## Goal

A `bot/store.py` module that, given a SQLite path, provides thread-safe dedupe, monthly quota operations, AND a draft-queue for the human-review workflow (Phase 6).

## Tasks

### Core tables (always present)

- [ ] `init_db(path) -> Connection`
  - Enables WAL mode (`PRAGMA journal_mode=WAL`)
  - Creates tables if they don't exist
- [ ] Tables:
  - `replied_tweets (tweet_id TEXT PRIMARY KEY, replied_at TEXT, original_text TEXT, reply_text TEXT, author_username TEXT, keyword TEXT)`
  - `monthly_writes (year_month TEXT PRIMARY KEY, count INTEGER)`

### Core functions

- [ ] `has_replied(tweet_id) -> bool`
- [ ] `mark_replied(tweet_id, original_text, reply_text, author_username, keyword)` (atomic insert)
- [ ] `get_monthly_count(year_month=None) -> int` (defaults to current `YYYY-MM`)
- [ ] `increment_monthly_count()` (atomic UPSERT)
- [ ] `get_recent_replies(limit=50) -> list[dict]` (for debugging / daily summaries)

### Draft mode (when `BOT_DRAFT_MODE=true` or `--draft` flag)

When the bot runs in draft mode, generated replies go to `pending_drafts` instead of being posted immediately. A human reviews them via the `python -m bot.main drafts` CLI subcommand and approves/rejects.

Schema:
```sql
CREATE TABLE pending_drafts (
    draft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_tweet_id TEXT NOT NULL,
    original_text TEXT NOT NULL,
    reply_text TEXT NOT NULL,
    author_username TEXT NOT NULL,
    keyword TEXT NOT NULL,
    generated_at TEXT NOT NULL,           -- ISO 8601 UTC
    status TEXT NOT NULL DEFAULT 'pending', -- pending / approved / rejected / posted
    decided_at TEXT,                       -- when approved or rejected
    posted_tweet_id TEXT                   -- set when status -> posted
);
CREATE INDEX idx_pending_status ON pending_drafts(status, generated_at);
```

Functions:
- [ ] `save_draft(tweet_id, original_text, reply_text, author_username, keyword) -> draft_id`
- [ ] `list_drafts(status='pending', limit=20, keyword=None) -> list[dict]`
- [ ] `get_draft(draft_id) -> dict | None`
- [ ] `approve_draft(draft_id) -> dict` (returns the draft data so caller can post it; sets status='approved', decided_at=now)
- [ ] `reject_draft(draft_id) -> None` (sets status='rejected', decided_at=now)
- [ ] `mark_draft_posted(draft_id, posted_tweet_id) -> None` (sets status='posted', posted_tweet_id=...)
- [ ] `pending_drafts_count() -> int` (for the `status` subcommand)

## Testing

**This is the most testable phase. Aim for >90% coverage.**

Core:
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

Draft mode:
- [ ] `save_draft()` returns a unique `draft_id` for each call
- [ ] `list_drafts(status='pending')` returns only pending, excludes approved/rejected/posted
- [ ] `approve_draft()` sets status to 'approved' and stamps `decided_at`
- [ ] `reject_draft()` sets status to 'rejected' and stamps `decided_at`
- [ ] `mark_draft_posted()` sets status to 'posted' and stores `posted_tweet_id`
- [ ] `pending_drafts_count()` returns the correct count
- [ ] Index `idx_pending_status` exists and speeds up `list_drafts` (verify with `EXPLAIN QUERY PLAN`)

## Exit criteria

- [ ] `pytest tests/test_store.py` passes with ≥90% coverage on `bot/store.py`
- [ ] Atomic check-and-mark verified (concurrent test passes)
- [ ] Draft mode CRUD verified (save/list/approve/reject/mark_posted all work)
- [ ] WAL mode confirmed
- [ ] No thread-safety bugs

## Notes

- Use `sqlite3` from stdlib — no need for SQLAlchemy here. Keep it simple.
- Store `replied_at` and `generated_at` as ISO 8601 strings (`datetime.now(timezone.utc).isoformat()`), not Unix int — easier to debug.
- For the monthly counter, use `YYYY-MM` (e.g., `"2026-08"`) as the PK. Reset is automatic when the month rolls over.
- The `replied_tweets` table is your **audit log**. Keep it forever (or until you run out of disk). If a reply gets you in trouble, you can trace back to what you posted.
- The `pending_drafts` table is **transient by design** — once a draft is approved+posted or rejected, you can vacuum it. But keep at least 30 days for debugging.
- The `tests/test_store.py` file should use pytest's `tmp_path` fixture for a real on-disk DB (faster + more representative than `:memory:` for WAL tests).
- **Draft IDs are local to the bot's DB** — they don't correspond to tweet IDs. Use them only for the `drafts --approve N` / `--reject N` subcommands.
