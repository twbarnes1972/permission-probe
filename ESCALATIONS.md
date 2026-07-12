# Escalations

Non-blocking agent-to-human feedback queue. Agents write here during autonomous execution when they need awareness or alignment but can continue working.

---

## Pending

### [2026-07-12] Obsolete hooks still wired in live `~/.claude/settings.json` — removal approved but not applied
Both PreToolUse hooks (`file-deny-guard.py`, `mcp-allow-guard.py`) are obsolete as of claude.exe 2.1.207 (see [ISSUE-0004 § Resolution](tasks/closed/ISSUE-0004.md#resolution-2026-07-12)); native path-globbed deny rules and MCP allow rules now work. The maintainer approved retiring both, but the settings.json edit was interrupted mid-session and never applied — the hooks are still live and harmless. **Action:** remove the two `hooks.PreToolUse` entries (or ask the agent to), then restart Claude once. The native `Read/Edit/Write(C:/Data/.../sd/**)` deny rules already in `permissions.deny` take over from `file-deny-guard.py`; verify with one denied-path Read after restart. Until removed, the move/rename hazard in the `project-live-hook-dependency` memory still applies.

### [2026-07-12] Workstation-specific paths are already published at HEAD (public repo)
`git grep` at HEAD finds `C:\Users\tbarnes\...` memory paths and the `twb-z13` sibling-project name in committed `SESSION.md` and `INSTRUCTIONS.md` — the same class of workstation detail the ISSUE-0001 pre-publication scrub deliberately removed from `probe.js` and the upstream drafts. Exposure is mild (username is guessable from the GitHub handle; only the *name* of the protected sibling project leaks, not contents), and these were pushed in prior sessions, so history rewrite is a cost/benefit call for the maintainer, not something done unilaterally. This session's new/rewritten content avoids absolute workstation paths going forward. **Decide:** (a) accept and just keep future content clean (cheapest, recommended), (b) scrub the current files in a normal commit (history still shows old versions), or (c) rewrite history + force-push (breaks clones; probably overkill).

## Resolved

### [2026-05-18] FEAT-0001: Cadence pacing — manual now, `/schedule` after 1 month validation
**Resolution (2026-05-18):** Confirmed — proceed with the planned two-stage rollout. Manual via `scripts/triage-sweep.sh` until ~1 month of stable runs, then wrap in `/schedule` weekly cron.

### [2026-05-18] FEAT-0001: Commenting identity — maintainer personal account with AI-disclosure footer
**Resolution (2026-05-18):** Confirmed — post under @twbarnes1972 with the per-comment AI-assistance disclosure footer kept in every template. No bot account.

### [2026-05-18] FEAT-0001: Commission ISSUE-0002 + ISSUE-0003
**Resolution (2026-05-18):** Both commissioned. Created `tasks/open/ISSUE-0002.md` (cd-prefix Bash bypass, Medium) and `tasks/open/ISSUE-0003.md` (RC-EDIT-PROMPT-2126 disambiguation, High). ISSUE-0002 flagged as potentially security-sensitive — may route through FEAT-0003 disclosure pipeline rather than public commentary.

### [2026-05-18] FEAT-0002: Blog / external writeup policy
**Resolution (2026-05-18):** "Yes, opportunistic." Take natural opportunities (post-release Show HN, security-blog invitation, conference CFP, podcast). Per-piece quality bar + conflict-of-interest disclosure required. Hard constraint: any external writeup that touches a finding before Anthropic's coordinated disclosure window completes is forbidden ([ethical-guardrails G2](tasks/working_artifacts/FEAT-0003/ethical-guardrails.md#g2-no-public-leak-path)). FEAT-0002 PLAN §9 updated accordingly.

### [2026-05-18] FEAT-0002: Public binary baselines
**Resolution (2026-05-18):** Commit publicly. Consistent with existing INVESTIGATION.md posture; baselines are small (KB range) and let any reader follow the change-tracking workflow exactly. change-tracking.md "Open questions" section updated to "Resolved decisions."

### [2026-05-18] FEAT-0003: Pre-disclosure storage location
**Resolution (2026-05-18):** Co-located gitignored folder at the repo root: `permission-probe-research/`. Added to `.gitignore`. Visible counterpart README at `tasks/working_artifacts/FEAT-0003/findings/README.md` (committed) explains the convention publicly. Local README inside `permission-probe-research/` documents the hard rules for working in that folder. **Caveat flagged to maintainer:** with no cloud sync, off-workstation backup is now the maintainer's responsibility — set up encrypted external/cloud backup for that folder before doing actual security work. FEAT-0003 PLAN §7 and finding-template.md updated accordingly.

### [2026-05-18] FEAT-0003: Proactive VDP submission of RC-XIQ-MATCHER + RC-BYPASS-GATE
**Resolution (2026-05-18):** Yes, submit via VDP. Commissioned as `tasks/open/GTSK-0002.md`. Both go to hackerone.com/anthropic-vdp with full disassembly + conflict-of-interest disclosure, adapted from the existing upstream-comment drafts in `tasks/working_artifacts/ISSUE-0001/upstream-comments/`. May be spaced 24-48h apart to avoid brigade-appearance per ethical-guardrails G5.

### [2026-05-18] FEAT-0003: Add SECURITY.md to this repo
**Resolution (2026-05-18):** Added `SECURITY.md` at the repo root. Routes Claude Code vulnerabilities to Anthropic's HackerOne + `disclosure@anthropic.com`; routes vulnerabilities in this repo's own code (the hook script + probe) to GitHub issues / security advisories on `twbarnes1972/permission-probe`. Includes a brief explanation of the security-research charter (FEAT-0003) for context. Written inline rather than spinning up a DOC-0001 task ceremony for a ~30-min file.

