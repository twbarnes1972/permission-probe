# Escalations

Non-blocking agent-to-human feedback queue. Agents write here during autonomous execution when they need awareness or alignment but can continue working.

---

## Pending

### [2026-05-18] FEAT-0001: Cadence pacing — manual now, `/schedule` after 1 month validation
Picked "manual on-demand" as Stage 1, with `/schedule` weekly cron as Stage 2 once a `scripts/triage-sweep.sh` exists and has been run manually for ~1 month without failure. Confirm or override — alternatives are: full `/schedule` immediately (riskier; haven't observed failure modes yet), or fully-manual indefinitely (loses the recurring-discipline benefit). Reference: [PLAN §3](tasks/working_artifacts/FEAT-0001/PLAN.md#3-cadence--automation-surface--pick).

### [2026-05-18] FEAT-0001: Commenting identity — defaulted to maintainer's personal account
Drafts land in `tasks/working_artifacts/FEAT-0001/drafts/<gh#>.md` for review; maintainer posts via `gh issue comment` under their own GitHub identity (twbarnes1972). No bot account. Alternative is to create a dedicated bot account — more complexity, somewhat sterilized voice. Defaulted personal; please confirm. Reference: [PLAN §6](tasks/working_artifacts/FEAT-0001/PLAN.md#6-per-cycle-workflow-draft--pick).

### [2026-05-18] FEAT-0001: Two follow-up investigations proposed — ISSUE-0002 (cd-prefix bypass) + ISSUE-0003 (RC-EDIT-PROMPT-2126 disambiguation)
Research surfaced upstream #59498 (novel Bash matcher bypass via cd-prefix stripping) and #55255 (suggests bare Edit allow no longer suppresses prompts in v2.1.126+, contradicting our ISSUE-0001 finding). Both proposed as new internal tasks but not yet created. ISSUE-0003 is the higher-priority disambiguation pass since it affects the README's recommended workaround. Decide if/when to commission these.

### [2026-05-18] FEAT-0002: Blog / external writeup policy — deferred
Whether the maintainer wants to publish blog posts / external writeups of permission-probe research over time. PLAN defaulted "no until you say yes" because this is a personal-brand + time-budget decision. Confirm policy: never / case-by-case / yes (with what venues?). Reference: [FEAT-0002 PLAN §9](tasks/working_artifacts/FEAT-0002/PLAN.md#9-outward-facing-artifacts--pick).

### [2026-05-18] FEAT-0002: Whether to commit binary baselines (offsets + disassembly context) publicly
The change-tracking workflow stores claude.exe symbol offsets + disassembly snippets at `kb/baselines/`. Defaulted "commit publicly" (consistent with existing INVESTIGATION.md posture). Alternative: keep baselines private. Probably non-issue but flagging. Reference: [change-tracking.md](tasks/working_artifacts/FEAT-0002/change-tracking.md).

### [2026-05-18] FEAT-0003: Pre-disclosure storage location — MUST decide before any actual security testing
Three options outlined in [PLAN §7](tasks/working_artifacts/FEAT-0003/PLAN.md#7-pre-disclosure-storage): private GitHub repo, encrypted local files (`age`/`gpg`), or password-manager secure note. Provisional recommendation: private GitHub repo + GPG-encrypt individual high-sensitivity finding files. This is the single decision that must be resolved before any actual finding work begins. Plan is otherwise fully scoped.

### [2026-05-18] FEAT-0003: Proactively submit RC-XIQ-MATCHER + RC-BYPASS-GATE to Anthropic VDP?
The two known root causes from ISSUE-0001 may be bounty-ineligible under HackerOne's "widely publicized zero-day" exclusion (already public at #36884/#57132/#15921) but are still valid VDP submissions. PLAN defaults to "yes, submit through VDP with full conflict-of-interest disclosure" — gives the dev team a structured analysis they can act on. Confirm or veto.

### [2026-05-18] FEAT-0003: Add a SECURITY.md to this repo
PLAN recommends adding `SECURITY.md` at the repo root that (a) routes actual Claude Code vuln reports to Anthropic's HackerOne, and (b) declares this repo's own scope (the hook script — small) for direct PRs / issues. Content needs maintainer review for phrasing before posting. Effort: ~30 min if approved.

## Resolved

