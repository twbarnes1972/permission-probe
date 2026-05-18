# Session

Session-to-session carryover state. Updated at end of each session to hand off context to the next.

See [SESSIONLOOP.md](./SESSIONLOOP.md) for start/end procedures.

---

## Current Focus

Three new tasks were commissioned last session but not started. Next session should pick up **[ISSUE-0003](tasks/open/ISSUE-0003.md)** first — High priority, affects the README's recommended workaround, contained scope.

## In-Flight Tasks

- **[ISSUE-0003](tasks/open/ISSUE-0003.md)** (High) — disambiguate RC-EDIT-PROMPT-2126. Empirical test on current `claude.exe`; either confirms regression and triggers a README deprecation note, or closes the upstream report as not-reproduced. Probe spec exists at [verification-suite.md#p3](tasks/working_artifacts/FEAT-0002/verification-suite.md), but does not need to be built out first — inline minimum-viable repro is fine.
- **[ISSUE-0002](tasks/open/ISSUE-0002.md)** (Medium, security-sensitive) — cd-prefix Bash deny bypass (#59498). If reproduced, route through [FEAT-0003 disclosure pipeline](tasks/working_artifacts/FEAT-0003/PLAN.md#9-reporting-workflow) rather than commenting publicly. Pre-disclosure storage in gitignored `permission-probe-research/`.
- **[GTSK-0002](tasks/open/GTSK-0002.md)** (Medium) — submit RC-XIQ-MATCHER + RC-BYPASS-GATE to Anthropic's VDP. Substrate already exists in [upstream-comment drafts](tasks/working_artifacts/ISSUE-0001/upstream-comments/); needs adaptation to HackerOne format (CVSS, structured fields) + conflict-of-interest disclosure.
- **[FEAT-0001](tasks/open/FEAT-0001.md)** / **[FEAT-0002](tasks/open/FEAT-0002.md)** / **[FEAT-0003](tasks/open/FEAT-0003.md)** — planning bundles complete in `tasks/working_artifacts/FEAT-000X/`. Move to execution phase as bandwidth allows; not blocking the ISSUE/GTSK work above.

## Open Questions

None pending. ESCALATIONS, FEEDBACK, and INSTRUCTIONS are all empty.

**Maintainer reminder carried over from last session:** off-workstation backup of `permission-probe-research/` is the maintainer's responsibility (no cloud sync). Set up encrypted external/cloud backup before doing real security work in that folder.

## Recent Sessions

### 2026-05-18 — Planning bundles + escalation walk-through

- Opened and planned FEAT-0001 (triage workflow), FEAT-0002 (permissions/security KB + verification suite), FEAT-0003 (red-team / disclosure pipeline). Deliverables in `tasks/working_artifacts/FEAT-000{1,2,3}/`.
- Walked all 8 ESCALATIONS items with maintainer; resolved in place.
- Commissioned three follow-up tasks out of resolutions: ISSUE-0002, ISSUE-0003, GTSK-0002.
- Added `SECURITY.md` at repo root (inline, no DOC task ceremony).
- Added gitignored `permission-probe-research/` for pre-disclosure findings; visible counterpart README at `tasks/working_artifacts/FEAT-0003/findings/`.

### 2026-05-16 — ISSUE-0001 closed

Investigation + INVESTIGATION.md + upstream-comment drafts merged. Repo restructured (`app-src/py-helpers/` + `app-src/js-probes/`). Task-manager scaffold added.
