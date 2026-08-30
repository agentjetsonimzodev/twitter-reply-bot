# Twitter Reply Bot — Plan

Reference docs for each phase of the build. See the root [README](../README.md) for project overview.

## Phases

| #  | Phase                       | Status     | Doc                                                |
|----|-----------------------------|------------|----------------------------------------------------|
| 0  | Accounts & Credentials      | 🔴 Todo   | [phase-0-accounts.md](./phase-0-accounts.md)       |
| 1  | Project Scaffold            | 🟢 Done   | [phase-1-scaffold.md](./phase-1-scaffold.md)       |
| 1.5| Config Loader               | 🔴 Todo   | [phase-1.5-config.md](./phase-1.5-config.md)       |
| 2  | Reads Module (twikit)       | 🔴 Todo   | [phase-2-reads.md](./phase-2-reads.md)             |
| 3  | Writes Module (tweepy)      | 🔴 Todo   | [phase-3-writes.md](./phase-3-writes.md)           |
| 4  | Reply Store (SQLite)        | 🔴 Todo   | [phase-4-store.md](./phase-4-store.md)             |
| 5  | AI Reply Generation         | 🔴 Todo   | [phase-5-ai.md](./phase-5-ai.md)                   |
| 6  | Orchestration + CLI         | 🔴 Todo   | [phase-6-orchestration.md](./phase-6-orchestration.md) |
| 7  | Scheduling                  | 🔴 Todo   | [phase-7-scheduling.md](./phase-7-scheduling.md)   |
| 8  | Observability & Safety      | 🔴 Todo   | [phase-8-observability.md](./phase-8-observability.md) |
| 9  | Deployment                  | 🔴 Todo   | [phase-9-deployment.md](./phase-9-deployment.md)   |
| 10 | Testing & Docs              | 🔴 Todo   | [phase-10-testing-docs.md](./phase-10-testing-docs.md) |

## How to use this folder

Each phase doc is a **working reference** — not a contract. Update it as you learn things.

Standard sections per phase:

- **Status** — Todo / In Progress / Done
- **Goal** — what "done" means for this phase
- **Tasks** — checklist
- **Testing** — how to verify it works (every code phase needs this)
- **Exit criteria** — pass/fail signal to move to the next phase
- **Notes** — gotchas, decisions, links

## Cross-cutting concerns

- **Testing:** every phase that ships code needs unit tests. Phase 10 ties it all together with E2E + CI.
- **Safety:** every phase must respect the monthly/daily caps. See [phase-8-observability.md](./phase-8-observability.md).
- **Ethics:** read the Safety section in the root README before posting anything real.
- **Cost:** LLM calls + $5 VPS. Track per-reply cost in Phase 5; revisit in Phase 10.
- **Draft mode:** Phases 4 and 6 support a human-review workflow (`pending_drafts` table + `python -m bot.main drafts` subcommand). Recommended for the first 1-2 weeks of running, then flip to auto-post. See [phase-6-orchestration.md](./phase-6-orchestration.md).
- **CLI:** Phase 6 introduces a subcommand-based CLI (`run`, `status`, `review`, `drafts`, `export`). It's the primary human interface — logs are for machines.
