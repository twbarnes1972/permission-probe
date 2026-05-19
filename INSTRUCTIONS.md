
# Instructions

---
**Related:**
- [Instruction Handling Workflow](./instruction_handling.md) -- How to process items in this document
- [Task Management](./task_management.md) -- Instructions for Managing Tasks

---

## Items

(none pending)

---

## Processing

| # | Item | Task ID | Status |
|---|------|---------|--------|

---

## Completed

### 2026-05-18 (session 2 close) — `documentation/` tree scaffolded per markdown-documentation convention

| # | Item | Task ID | Status |
|---|------|---------|--------|
| 1 | Create `documentation/claude/mental_model.md` with the provided context-at-session-start description | (no task — direct work) | done |
| 2 | Create `documentation/conventions/` with markdown-documentation convention copied from `C:\Data\twb-z13\documentation\conventions\markdown-documentation.md`; adopt the convention; create `documentation/documentation.md` top index and `documentation/claude/claude.md` section index, all with proper back-links | (no task — direct work) | done |

Files created:
- `documentation/documentation.md` — top-level index (links to README, indexes sections).
- `documentation/claude/claude.md` — section index for claude/.
- `documentation/claude/mental_model.md` — Claude's session-start context description (verbatim from instruction, wrapped with the required back-link + H1 per the adopted convention).
- `documentation/conventions/conventions.md` — section index for conventions/.
- `documentation/conventions/markdown-documentation.md` — verbatim copy of the source convention file (its back-link target `conventions.md` is now valid in the new location).

Convention adoption is partial: per the convention, `README.md` should link to `documentation/documentation.md` from a Documentation section. **Not done in this intake** — README is load-bearing for this repo and any restructure overlaps with the README refactor contemplated in [FEAT-0004](tasks/open/FEAT-0004.md). Surfacing as a separate decision rather than silently editing README.

### 2026-05-18 — broaden contribution scope + add docs + research bounty programs

| # | Item | Task ID | Status |
|---|------|---------|--------|
| 1 | Broaden contribution scope beyond Claude Code CLI to open-source portfolio (Python, Traefik, PostgreSQL, Windmill, Supabase, Restic, Kafka, Pomerium, CoreDNS, FreeRADIUS, Apache Airflow, Firezone) specializing in permissions/access controls/identity; refactor README accordingly; maintain NOTICE.md for closed-source tools | [FEAT-0004](tasks/open/FEAT-0004.md) | created (planning) |
| 2 | Create `documentation/open-source-contributing/` directory with markdown adapted from opensource.guide | [DOC-0001](tasks/open/DOC-0001.md) | created |
| 3 | Research paid bug bounty programs (aggregators + per-project for FEAT-0004's project list) | [GTSK-0003](tasks/open/GTSK-0003.md) | created |

All three are planning/research tasks per user direction at intake. No implementation kicked off in this intake step — each task spawns its own implementation work after plan approval.

---
