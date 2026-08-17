# Phase 6 — Orchestration (main loop + CLI)

> Wire the modules together AND build a reviewer-friendly CLI. This phase makes the bot's behavior *visible* to a human, not just log lines.

## Status: 🔴 Todo

## Goal

A `bot/main.py` that runs the full pipeline **AND** a subcommand-based CLI that gives a human clear visibility into what the bot is doing — past (`review`), present (`status`), and future (`drafts`).

## Tasks

### Core orchestration

- [ ] `run_once(config) -> RunSummary` — one full pass
  - For each keyword in `BOT_KEYWORDS`:
    1. Search (via reads)
    2. Filter out already-replied (via store)
    3. For each remaining tweet (up to `BOT_MAX_REPLIES_PER_RUN`):
       - Generate reply (via ai)
       - Length check + bad-reply check
       - **If `--draft` mode (or `BOT_DRAFT_MODE=true`):** save to `pending_drafts`, skip post
       - **Else:** post reply (via writes), mark replied, increment monthly count
       - Jittered sleep (5-30s)
- [ ] `RunSummary` dataclass: `{found, replied, drafted, skipped, errors, started_at, finished_at}`

### CLI structure (subcommands)

Use `argparse` with subcommands (stdlib — no extra dep needed):

```
python -m bot.main run [options]       # do a pass
python -m bot.main status [options]    # show stats
python -m bot.main review [options]    # show past replies
python -m bot.main drafts [options]    # list / approve / reject drafts
python -m bot.main export [options]    # export replies + drafts to JSON/CSV
```

### `run` subcommand

- [ ] `--dry-run` (don't post, don't save to DB, just print what would happen)
- [ ] `--draft` (save to `pending_drafts` instead of posting)
- [ ] `--once` (single pass — implied default)
- [ ] `--max-replies N` (override `BOT_MAX_REPLIES_PER_RUN`)
- [ ] `--keyword X` (override keywords — comma-separated for multiple)
- [ ] `--verbose` (debug logging)

### `status` subcommand

- [ ] Show last 24h summary: found / replied / drafted / errors
- [ ] Show monthly quota: count / cap / percentage
- [ ] Show pending drafts count
- [ ] `--days N` (default 1) to widen the window

### `review` subcommand

- [ ] Show last N replies (default 10) from `replied_tweets`
- [ ] `--days N` to widen the window (default 7)
- [ ] `--limit N` to control row count
- [ ] `--keyword X` to filter
- [ ] `--user Y` to filter by author username

### `drafts` subcommand

- [ ] `python -m bot.main drafts` → list pending drafts (most recent first)
- [ ] `python -m bot.main drafts --approve 5` → approve draft #5
- [ ] `python -m bot.main drafts --reject 7` → reject draft #7 (with optional `--reason`)
- [ ] `python -m bot.main drafts --approve-all` → bulk approve (yolo mode)
- [ ] `python -m bot.main drafts --days 30` → widen the window
- [ ] `python -m bot.main drafts --keyword X` → filter
- [ ] `--show-posted` to include already-posted drafts in the listing (audit mode)

### `export` subcommand

- [ ] `--days N` (default 30)
- [ ] `--format json|csv` (default json)
- [ ] `--output FILE` (default stdout)
- [ ] Includes both `replied_tweets` and `pending_drafts` (one JSON array, or two CSV files)

### Pretty output (using `rich`)

- [ ] `rich.table.Table` for `status` / `review` / `drafts` listings
- [ ] `rich.console.Console` for `run` output (color-coded: candidate tweets dim, drafts cyan, posted green, errors red)
- [ ] Tweet text wrapped at 80 cols with `>` quote indicator
- [ ] Reply drafts shown indented with `→` prefix
- [ ] Each run ends with a summary box

### Example `run --dry-run --once` output:

```
[14:23:01] Searching for "indie hacker"...
[14:23:03] Found 12 tweets

  [ 1/12] @alice_IndieHacker · 2h ago
  > Just shipped my first SaaS — 3 paying customers in week 1!
  → Three customers in week 1 is wild. What was the
    distribution channel that brought the first one in?

  [ 2/12] @bobBuilds · 5h ago
  > Day 30 of building in public — here's what I learned...
  → The 'ship log' angle is underrated. Did you find
    a specific cadence (daily/weekly) that worked?

  ...

╭─ Run summary ─────────────────────────────────────╮
│ Found:     12                                     │
│ Replied:   0  (dry-run)                           │
│ Drafted:   0  (dry-run)                           │
│ Skipped:   0                                      │
│ Errors:    0                                      │
╰───────────────────────────────────────────────────╯
```

## Testing

**Unit tests (all modules mocked, real store against `tmp_path`):**
- [ ] Inject mock `LLMClient`, mock `twikit.Client`, mock `tweepy.Client`, real `store` against `tmp_path` DB
- [ ] Scenarios:
  - 5 tweets found, none replied → 5 replies generated, 5 posts, 5 marks
  - 5 tweets found, 2 already in DB → 3 posts (skipped count = 2)
  - 1 tweet throws in `ai.generate()` → caught, run continues with remaining 4
  - `--max-replies 2` with 5 found → only 2 posts
  - `--dry-run` → 0 calls to `writes.post_reply`, 0 DB writes
  - `--draft` → all replies go to `pending_drafts`, 0 calls to `writes.post_reply`, `RunSummary.drafted` == N
  - `--keyword "X"` override → only searches for that keyword
- [ ] `RunSummary` returned with correct counts in all scenarios

**Subcommand tests (CLI, mocked deps):**
- [ ] `python -m bot.main status --days 7` exits 0, prints formatted output
- [ ] `python -m bot.main review` exits 0, reads from `replied_tweets`
- [ ] `python -m bot.main drafts` exits 0, lists pending
- [ ] `python -m bot.main drafts --approve 5` marks approved, returns the draft for posting
- [ ] `python -m bot.main drafts --reject 7` marks rejected
- [ ] `python -m bot.main drafts --approve-all` approves all pending
- [ ] `python -m bot.main export --format json` produces valid JSON

**Integration test (real everything, sandbox account):**
- [ ] Mark with `@pytest.mark.integration`
- [ ] Use a sandbox X account
- [ ] Set `BOT_KEYWORDS=python` and `--max-replies 1`
- [ ] Verify one real reply was posted
- [ ] Manually delete the reply after the test

**Manual E2E:**
```bash
# dry run first — review what it would do
python -m bot.main run --dry-run --once --keyword "indie hacker" --max-replies 3

# then draft mode — same thing but saved for review
python -m bot.main run --draft --once --keyword "indie hacker" --max-replies 3
python -m bot.main drafts           # review them
python -m bot.main drafts --approve 1  # post the one you like

# then full auto-post
python -m bot.main run --once --keyword "indie hacker" --max-replies 1

# later, audit
python -m bot.main review --days 7
python -m bot.main status
```

## Exit criteria

- [ ] `pytest tests/test_main.py` passes
- [ ] All CLI subcommands (`run`, `status`, `review`, `drafts`, `export`) work and exit 0
- [ ] `--draft` mode saves to DB but doesn't post
- [ ] `drafts --approve N` posts draft N and updates status to `posted`
- [ ] `drafts --reject N` updates status to `rejected` without posting
- [ ] Output is readable and informative (manually verify a `--dry-run`)
- [ ] All existing tests still pass

## Notes

- **Use `rich` for output.** It handles word wrap, tables, and color without us writing terminal-width detection code. ~500KB dep, worth it.
- **The CLI is your daily interface.** If it's not pleasant to use, you'll avoid checking the bot. Spend time on the output formatting.
- **`--draft` is the recommended mode for the first 1-2 weeks.** Review every reply, get a feel for quality, then flip to auto-post. See `plan/phase-8-observability.md` for the kill switch + quota warnings that work with both modes.
- **Draft approval can be scripted.** You could `cron` a daily job that approves all drafts older than 24h, OR leave them in `pending` indefinitely. The choice is yours.
- **The `review` and `export` subcommands are your audit tools.** If X flags you, dump everything and review.
- **The `try/except per tweet` is critical.** One bad AI response or one rate-limited post should not kill the whole run.
- **Log every decision:** "skipped {tweet_id}: already replied", "posted {tweet_id} → {reply_id}", "drafted {tweet_id} as draft #{N}", "rate limited, sleeping {N}s".
- **Design decision for `--dry-run`:** does it mark the DB?
  - Default: don't mark. Lets you re-test replies across runs (good for A/B testing prompts).
  - `--dry-run-mark` flag: does mark. Good for iterating on prompts without re-processing the same tweets.
- **RunSummary** returned values feed into the daily summary log in Phase 8.
