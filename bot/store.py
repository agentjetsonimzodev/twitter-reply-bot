"""SQLite-backed dedupe + quota tracking.

TODO (Phase 4):
  - replied_tweets (tweet_id PK, replied_at, original_text, reply_text,
                   author_username, keyword)
  - monthly_writes (year_month PK, count)
  - atomic check-and-mark (prevents double-replies on retry)
  - WAL mode for safe concurrent reads
"""
