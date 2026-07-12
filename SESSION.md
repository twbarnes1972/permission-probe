# Session

Session-to-session carryover state. Updated at end of each session to hand off context to the next.

See [SESSIONLOOP.md](./SESSIONLOOP.md) for start/end procedures.

---

## Current Focus

**Both permission bugs are FIXED upstream — verified 2026-07-12 on claude.exe 2.1.207. The repo is now in deprecation/wind-down mode.**

This session re-ran the full verification against the current release (up from 2.1.143/2.1.144 when the bugs were characterized). Everything resolved:

- **ISSUE-0001 finding #1 (`XIq` matcher):** path-globbed `Edit(...)` allow rules match; path-globbed deny rules override bare allows — verified in both `--print` and interactive TUI. Negative controls held. The reject line is *still in the binary* (minified `pto`, offset ~232912623) — upstream added a parallel content-matching path instead of removing the filter.
- **ISSUE-0001 finding #2 (`bypassPermissions` gate):** `"defaultMode": "bypassPermissions"` in settings.json now activates (caveat: sandbox had `bypassPermissionsModeAccepted: true` seeded — may be conditional on prior dialog acceptance).
- **ISSUE-0004 (TUI drops MCP allow rules):** fixed; bare MCP rules auto-approve in the TUI (`permissionDecisionMs=0`, `entrypoint=cli`).

Method: isolated `CLAUDE_CONFIG_DIR` sandbox (no hooks, crafted settings.json), `--print --debug` for the sdk-cli path, and — new capability this session — **ConPTY-driven interactive TUI sessions** via `pywinpty`, which closes the "can't test the TUI programmatically" gap. Harness + stub MCP server + sandbox recipe preserved at [tasks/working_artifacts/ISSUE-0004/](tasks/working_artifacts/ISSUE-0004/README.md). Full results: [ISSUE-0004 § Resolution](tasks/closed/ISSUE-0004.md#resolution-2026-07-12).

Fix version unknown — landed silently in 2.1.145–2.1.207; #36884 and #55255 were stale-closed "not planned", #15921 open with zero maintainer response.

## First order of business next session

1. **GTSK-0002 (VDP submission) needs re-scoping**: both root causes it was going to submit are now fixed. Options: submit anyway as historical/fixed (low value), convert to a retrospective writeup (feeds FEAT-0002's opportunistic-blog policy), or close as overtaken by events. Maintainer call.
2. The upstream resolution notes for #57132/#15921 are **owned by the open-source-contributing repo** (its ISSUE-0002) — this session filed the verification report into that repo's INSTRUCTIONS.md intake. Nothing owed from this repo; don't duplicate.
3. **One residual verification** (from the resolved hook-removal escalation): in the first post-restart session, try one Read under the path-globbed `permissions.deny` rules and confirm the native deny fires now that the hooks are gone.

## In-Flight Tasks

- **[ISSUE-0002](tasks/open/ISSUE-0002.md)** (Medium, security-sensitive) — cd-prefix Bash deny bypass (#59498). Untouched this session; unaffected by the fix wave (Bash content matching was never broken). If reproduced, route through the FEAT-0003 disclosure pipeline.
- **[GTSK-0002](tasks/open/GTSK-0002.md)** (Medium) — VDP submission. **Needs re-scope, see above.**
- **[FEAT-0004](tasks/open/FEAT-0004.md)** / **[DOC-0001](tasks/open/DOC-0001.md)** / **[GTSK-0003](tasks/open/GTSK-0003.md)** — planning/doc/research tasks, untouched this session. FEAT-0004's "expand beyond Claude Code" thesis got *stronger* now that this repo's core mission is complete.
- **[FEAT-0001](tasks/open/FEAT-0001.md)** / **[FEAT-0002](tasks/open/FEAT-0002.md)** / **[FEAT-0003](tasks/open/FEAT-0003.md)** — planning bundles complete; execution as bandwidth allows. FEAT-0002's verification suite should absorb the new TUI harness (noted in the artifacts README).

## Open Questions

- GTSK-0002 disposition (see above). Both 2026-07-12 escalations were resolved same-session (hooks removed from live settings.json; workstation-paths exposure accepted as option (a), with a new no-workstation-paths convention added to CLAUDE.md).

**Maintainer reminder carried over:** off-workstation backup of `permission-probe-research/` is the maintainer's responsibility (no cloud sync). Set up encrypted external/cloud backup before doing real security work in that folder.

**Repo state at session end:** the deprecation milestone (commit `8165095`, bundling the held-back 2026-05-19 workaround chunk with the 2026-07-12 verification) was committed and **pushed with per-push maintainer approval** per SESSIONLOOP.md. A follow-up commit closes ISSUE-0003 (exact-reproducer confirmation + registry/root-causes bookkeeping).

## Recent Sessions

### 2026-07-12 — Verification session: both bugs fixed on 2.1.207; repo enters deprecation mode

- Re-ran the full reproducer matrix against claude.exe 2.1.207 in an isolated `CLAUDE_CONFIG_DIR` sandbox: ISSUE-0001 (both findings) and ISSUE-0004 all fixed. Negative controls held; auto-mode confirmed inactive in all runs. Static check: the `XIq` reject filter survives in the binary (as `pto`) but is bypassed by a new content-matching path.
- **New capability:** programmatic interactive-TUI testing via ConPTY (`pywinpty`) — spawned real `entrypoint=cli` sessions, typed prompts, watched for permission dialogs vs success markers. Also built a dependency-free stub MCP stdio server so MCP permission rules can be tested without credentials. Both preserved with a sandbox recipe in [tasks/working_artifacts/ISSUE-0004/](tasks/working_artifacts/ISSUE-0004/README.md).
- **Docs:** ISSUE-0004 closed with full resolution section and moved to `tasks/closed/`; README deprecation banner + Status rewrite; INVESTIGATION.md compatibility table annotated as historical (≤2.1.144); task_list updated.
- **ISSUE-0003 closed** (post-close-out addendum, same day): ran the exact reproducer — bare `Edit` as the only allow rule, file under cwd, 2.1.207 — Edit auto-approved (`permissionDecisionMs=2`, no prompt). Closed not-reproduced-on-current; RC-EDIT-PROMPT-2126 → closed in root-causes.md; registry.md #55255 row updated (upstream stale-closed; confidence H). No upstream comment owed (#55255 dead, behavior gone).
- **Hand-off:** verification report filed into `open-source-contributing`'s INSTRUCTIONS.md intake (its ISSUE-0002 was explicitly waiting on it — it owns the upstream resolution notes on #57132/#15921, with a scope caution: our verification covers the native CLI only, not the VS Code extension half of #15921).
- **Not done:** live settings.json hook removal (approved, then the edit was interrupted — escalated); upstream posts (other repo's deliverable).

### 2026-05-19 — Gateway silent-deny RCA + ISSUE-0004 workaround landed

- Diagnosed the TUI-vs-subprocess MCP permission divergence (subprocess probes auto-approved with `permissionDecisionMs=0`; the same call in-session silent-failed as `user_rejected`). Ruled out workspace trust, permission mode, and settings overrides.
- Built [`app-src/py-helpers/mcp-allow-guard.py`](app-src/py-helpers/mcp-allow-guard.py) (sibling of `file-deny-guard.py`; fails open; smoke-tested 5 cases) and wired it into `~/.claude/settings.json` as a second `PreToolUse` entry.
- Created ISSUE-0004 (full RC + reproducer), updated README (both bugs, both hooks), added the entrypoint-dependent footnote to INVESTIGATION.md's compatibility table, updated the `project-live-hook-dependency` memory to cover both hook scripts.
- Disassembly partial: entrypoint enum located; workspace-trust gate ruled out; exact TUI branch not pinned (workaround made RC depth unnecessary — and the 2026-07-12 fix made it moot).

### 2026-05-18 (session 2) — INSTRUCTIONS intake + push-gating rule + `documentation/` scaffold

- Processed three INSTRUCTIONS.md items → [FEAT-0004](tasks/open/FEAT-0004.md), [DOC-0001](tasks/open/DOC-0001.md), [GTSK-0003](tasks/open/GTSK-0003.md).
- Updated [SESSIONLOOP.md](./SESSIONLOOP.md) push-gating: pulls auto, pushes require explicit per-push go-ahead.
- Maintainer feedback item — RCA before fix ("slow is smooth, smooth is fast") — routed to the `feedback-rca-before-fix` memory, cross-linked with the velocity memory.
- Maintainer commissioned the `documentation/` tree (index + `claude/` + `conventions/`, adopting the markdown-documentation convention). README link deferred into FEAT-0004's README refactor. DOC-0001 will slot under `documentation/` following the same pattern.

### 2026-05-18 (session 1) — Planning bundles + escalation walk-through

- Opened and planned FEAT-0001 (triage workflow), FEAT-0002 (permissions/security KB + verification suite), FEAT-0003 (red-team / disclosure pipeline). Deliverables in `tasks/working_artifacts/FEAT-000{1,2,3}/`.
- Walked all 8 ESCALATIONS items with maintainer; resolved in place. Commissioned ISSUE-0002, ISSUE-0003, GTSK-0002.
- Added `SECURITY.md`; added gitignored `permission-probe-research/` for pre-disclosure findings.

### 2026-05-16 — ISSUE-0001 closed

Investigation + INVESTIGATION.md + upstream-comment drafts merged. Repo restructured (`app-src/py-helpers/` + `app-src/js-probes/`). Task-manager scaffold added.
