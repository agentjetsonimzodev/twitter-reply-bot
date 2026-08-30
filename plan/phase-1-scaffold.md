# Phase 1 — Project Scaffold

> Set up the package layout, dependency pinning, config template, and importable structure.

## Status: 🟢 Done (commit `678d5b7`)

## Goal

A cloneable, importable, installable Python package with all future modules stubbed and all config documented.

## Tasks

- [x] Create `bot/` package with stub modules
  - [x] `__init__.py` (version marker)
  - [x] `config.py` (Phase 1.5)
  - [x] `reads.py` (Phase 2)
  - [x] `writes.py` (Phase 3)
  - [x] `store.py` (Phase 4)
  - [x] `ai.py` (Phase 5)
  - [x] `main.py` (Phase 6)
- [x] Create `tests/` package
- [x] `.env.example` with all variables from the plan documented
- [x] `.gitignore` covering `.env`, `cookies.json`, `*.db`, Python/IDE/OS junk
- [x] `requirements.txt` with pinned version ranges
- [x] `README.md` with architecture overview, setup, safety notes

## Testing

Even a scaffold should have minimal tests to catch breakage later. Add these in Phase 10, but verify the basics now:

- [ ] `python -c "import bot; print(bot.__version__)"` → prints `0.1.0`
- [ ] `python -c "from bot import reads, writes, store, ai, main, config"` → no `ImportError`
- [ ] `pip install -r requirements.txt` succeeds in a fresh venv
- [ ] `pytest --collect-only` exits 0 (no tests yet, but no collection errors)

Suggested test files to add in Phase 10:
- `tests/test_imports.py` — covers the first two bullets
- `tests/test_requirements.py` — covers the last two (use `subprocess` to run in a fresh venv)

## Exit criteria

- [x] `git clone` → `pip install` → `python -c "import bot"` works on a fresh machine
- [x] Repo is public
- [x] `.env.example` is complete (matches the plan's required vars)

## Notes

- We stopped short of `Dockerfile` and `docker-compose.yml` — those land in Phase 9.
- We didn't add CI yet — that lands in Phase 8 or 10.
- If you want to add a `LICENSE` before going public, do it now (MIT recommended).
- **Phase 1.5 (the config loader) now has its own design doc: [phase-1.5-config.md](./phase-1.5-config.md).** Use that as the source of truth for `bot/config.py` — its API surface, validators, and `get_settings()` factory are fully specified there. The 3 implementation issues (#5, #6, #7) all reference it.
