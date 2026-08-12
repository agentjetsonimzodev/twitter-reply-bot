# Phase 10 — Testing & Docs

> The polish phase. End-to-end verification, comprehensive tests, polished README, CI.

## Status: 🔴 Todo

## Goal

The repo is **portfolio-quality**: comprehensive tests, clear docs, easy for someone else to clone-and-run.

## Tasks

- [ ] Add missing tests (from earlier phases — many are referenced but deferred):
  - [ ] `tests/test_imports.py` — verify all modules import
  - [ ] `tests/test_requirements.py` — verify deps install in clean venv
  - [ ] `tests/test_reads.py` (Phase 2)
  - [ ] `tests/test_writes.py` (Phase 3)
  - [ ] `tests/test_store.py` (Phase 4)
  - [ ] `tests/test_ai.py` (Phase 5)
  - [ ] `tests/test_main.py` (Phase 6)
  - [ ] `tests/test_scheduling.py` (Phase 7)
  - [ ] `tests/test_observability.py` (Phase 8)
  - [ ] `tests/test_deployment.py` (Phase 9)
  - [ ] `tests/e2e/test_full_pipeline.py` — full happy path with everything mocked
- [ ] Mock LLM client fixture (for offline tests):
  - [ ] `tests/mocks/mock_llm.py` — returns canned responses
  - [ ] Avoids hitting real LLM in CI
- [ ] `README.md` polish:
  - [ ] Architecture diagram (Mermaid or ASCII)
  - [ ] "How it works" section with a real example
  - [ ] FAQ (Why twikit? Why OAuth 1.0a? How much will this cost?)
  - [ ] Troubleshooting (cookie expired, rate limited, dev portal rejected, etc.)
  - [ ] Screenshots / sample outputs (optional)
- [ ] `.env.example` fully commented (already done in Phase 1, final review)
- [ ] `CONTRIBUTING.md` (if open-sourcing)
- [ ] `LICENSE` (MIT recommended)
- [ ] CI (GitHub Actions):
  - [ ] Run ruff on every push
  - [ ] Run pytest on every push
  - [ ] Block merge on red CI
  - [ ] Add CI badge to README

## Testing

This phase IS testing. Verify it works:

- [ ] `pytest` runs all unit tests, passes, finishes in < 10s
- [ ] `pytest -m integration` runs integration tests, all pass
- [ ] `pytest --cov=bot` shows ≥80% coverage (≥90% for `bot/store.py`)
- [ ] CI pipeline green on a fresh GitHub Actions run (after pushing)
- [ ] E2E test verifies the full happy path: search → dedupe → generate → mark
- [ ] Mock LLM fixture works in CI (no real LLM calls during `pytest`)

## Exit criteria

- [ ] Fresh clone → `pip install -r requirements.txt` → `pytest` → all green
- [ ] README is good enough that a stranger could set this up without asking you
- [ ] No `TODO` comments left in code (all moved to GitHub issues or completed)
- [ ] CI badge in README showing green
- [ ] The project is **portfolio-presentable** (you'd be comfortable sharing the link)

## Notes

- This phase is easy to skip but **don't**. It's the difference between a hackathon project and a real tool.
- Coverage target: **80% overall, ≥95% for `bot/store.py`** (pure logic, easy to test thoroughly).
- The FAQ section is your future self's best friend. Answer the questions you actually asked while building this.
- The "How it works" example should walk through one real reply end-to-end, with screenshots if possible. This is the section that converts a curious visitor to a user.
- Consider recording a short screencast of the bot working — perfect for the imzodev YouTube channel.
- Add a `prompts/` folder with versioned personas you tried during Phase 5. The history of what you tried is valuable.
