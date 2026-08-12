"""Orchestration: search -> dedupe -> generate -> post -> log.

TODO (Phase 6):
  - per-keyword loop
  - jittered sleeps (5-30s) between actions to look human
  - CLI flags: --dry-run (no posts), --once (single pass), --max-replies N
"""
