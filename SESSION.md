# Session

Session-to-session carryover state. Updated at end of each session to hand off context to the next.

See [SESSIONLOOP.md](./SESSIONLOOP.md) for start/end procedures.

---

## Current Focus

Next session should pick up **[ISSUE-0003](tasks/open/ISSUE-0003.md)** first — still the highest-priority unfinished work (High, affects the README's recommended workaround, contained scope). The three new planning/research tasks created this session (FEAT-0004, DOC-0001, GTSK-0003) are not blocking and can wait.

## In-Flight Tasks

- **[ISSUE-0003](tasks/open/ISSUE-0003.md)** (High) — disambiguate RC-EDIT-PROMPT-2126. Empirical test on current `claude.exe`; either confirms regression and triggers a README deprecation note, or closes the upstream report as not-reproduced. Probe spec exists at [verification-suite.md#p3](tasks/working_artifacts/FEAT-0002/verification-suite.md), but does not need to be built out first — inline minimum-viable repro is fine.
- **[ISSUE-0002](tasks/open/ISSUE-0002.md)** (Medium, security-sensitive) — cd-prefix Bash deny bypass (#59498). If reproduced, route through [FEAT-0003 disclosure pipeline](tasks/working_artifacts/FEAT-0003/PLAN.md#9-reporting-workflow) rather than commenting publicly. Pre-disclosure storage in gitignored `permission-probe-research/`.
- **[GTSK-0002](tasks/open/GTSK-0002.md)** (Medium) — submit RC-XIQ-MATCHER + RC-BYPASS-GATE to Anthropic's VDP. Substrate already exists in [upstream-comment drafts](tasks/working_artifacts/ISSUE-0001/upstream-comments/); needs adaptation to HackerOne format (CVSS, structured fields) + conflict-of-interest disclosure.
- **[FEAT-0004](tasks/open/FEAT-0004.md)** (Medium, **new this session**) — strategic-expansion planning task; broadens contribution scope beyond Claude Code to a permissions/identity portfolio across 12 candidate projects. Touches FEAT-0001/0002/0003 (defines how they generalize per-project). Planning-only deliverable; spawn implementation downstream.
- **[DOC-0001](tasks/open/DOC-0001.md)** (Medium, **new this session**) — create `documentation/open-source-contributing/` adapted from opensource.guide (CC-BY-4.0 with attribution). License scaffolding lands first; 5–7 guide MVP. Can run in parallel with FEAT-0004 or after it.
- **[GTSK-0003](tasks/open/GTSK-0003.md)** (Medium, **new this session**) — research paid bug bounty programs (aggregators + per-project for FEAT-0004's list). Feeds FEAT-0004 prioritization rubric and FEAT-0003 per-project disclosure-channel planning.
- **[FEAT-0001](tasks/open/FEAT-0001.md)** / **[FEAT-0002](tasks/open/FEAT-0002.md)** / **[FEAT-0003](tasks/open/FEAT-0003.md)** — planning bundles complete in `tasks/working_artifacts/FEAT-000X/`. Move to execution phase as bandwidth allows; not blocking the ISSUE/GTSK work above.

## Open Questions

None pending. ESCALATIONS, FEEDBACK, and INSTRUCTIONS are all empty.

**Maintainer reminder carried over:** off-workstation backup of `permission-probe-research/` is the maintainer's responsibility (no cloud sync). Set up encrypted external/cloud backup before doing real security work in that folder.

**Carryover from this session's end:** local branch is ahead of `origin/main` by 7 commits (pre-existing) plus this session's uncommitted intake work. Per the new push-gating rule in [SESSIONLOOP.md](./SESSIONLOOP.md), the push is awaiting an explicit go-ahead from the maintainer. Next session may want to ask whether to push the accumulated planning bundles when starting.

## Recent Sessions

### 2026-05-18 (session 2) — INSTRUCTIONS intake + push-gating rule

- Processed three items from INSTRUCTIONS.md per `tasks/instruction_handling.md`:
  - Item 1 → [FEAT-0004](tasks/open/FEAT-0004.md) (planning task — broaden contribution scope to permissions/identity portfolio).
  - Item 2 → [DOC-0001](tasks/open/DOC-0001.md) (adapt opensource.guide content into `documentation/open-source-contributing/` under CC-BY-4.0).
  - Item 3 → [GTSK-0003](tasks/open/GTSK-0003.md) (paid bug bounty research scoped to FEAT-0004's project list).
- Updated [SESSIONLOOP.md](./SESSIONLOOP.md) push-gating: pulls remain auto, **pushes require explicit per-push go-ahead** from the maintainer (public repo; no standing approval).
- No implementation work started; pure intake + procedure tweak.

### 2026-05-18 (session 1) — Planning bundles + escalation walk-through

- Opened and planned FEAT-0001 (triage workflow), FEAT-0002 (permissions/security KB + verification suite), FEAT-0003 (red-team / disclosure pipeline). Deliverables in `tasks/working_artifacts/FEAT-000{1,2,3}/`.
- Walked all 8 ESCALATIONS items with maintainer; resolved in place.
- Commissioned three follow-up tasks out of resolutions: ISSUE-0002, ISSUE-0003, GTSK-0002.
- Added `SECURITY.md` at repo root (inline, no DOC task ceremony).
- Added gitignored `permission-probe-research/` for pre-disclosure findings; visible counterpart README at `tasks/working_artifacts/FEAT-0003/findings/`.

### 2026-05-16 — ISSUE-0001 closed

Investigation + INVESTIGATION.md + upstream-comment drafts merged. Repo restructured (`app-src/py-helpers/` + `app-src/js-probes/`). Task-manager scaffold added.
