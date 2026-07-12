# Root Causes Registry

Stable IDs for known/suspected root causes in Claude Code's permission + security surface. Foreign-key'd from [registry.md](registry.md) via the `mapped_rc` column.

Each entry: summary → evidence pointer → verified versions → workaround pointer → upstream trackers.

---

## RC-XIQ-MATCHER

**Status:** Verified.
**Verified on:** claude.exe 2.1.143.a06 (Windows native CLI). The same JS bundle is used on macOS and Linux, so cross-platform is presumed but not independently verified per OS.
**Severity:** High (silent failure of a security-relevant boundary — deny rules don't enforce).

### Summary

`claude.exe`'s permission matcher dispatches allow / deny / ask checks through a single predicate `XIq(tool, rule, opts)`. Its first line is:

```js
if (rule.ruleValue.ruleContent !== void 0) return false;
```

This unconditionally rejects every rule that has parens content. `Edit(/path/**)` parses to `{toolName: "Edit", ruleContent: "/path/**"}` — the rejection fires. Result: every path-globbed allow OR deny rule for file-pattern tools is silently no-op. Affects: `Read`, `Edit`, `Write`, `Glob`, `NotebookRead`, `NotebookEdit`, `Skill`, and `mcp__server__tool(arg)`.

Bash and PowerShell rules with content **do** work — they have their own per-tool content matcher (`dz8`) that bypasses `XIq`.

### Evidence

- Full disassembly + four-row reproducer matrix: [INVESTIGATION.md §Finding #1](../ISSUE-0001/INVESTIGATION.md#finding-1--the-xiq-matcher-bug).
- The line itself: `XIq` first instruction. Find via `grep -aob "ruleContent" /path/to/claude.exe`.
- Independent verification picomatch isn't to blame: `app-src/js-probes/probe.js`.

### Workaround

- Bare `Read`, `Edit`, `Write` in `permissions.allow` (the only form the matcher honors).
- `PreToolUse` hook (`app-src/py-helpers/file-deny-guard.py`) to re-implement path-based denies. Lives below `XIq` in the decision flow, so it actually fires.

### Upstream trackers

- [#36884](https://github.com/anthropics/claude-code/issues/36884) — primary thread with full root-cause comment.
- [#57132](https://github.com/anthropics/claude-code/issues/57132) — Linux variant cross-link.
- [#15921](https://github.com/anthropics/claude-code/issues/15921) — multi-bug umbrella.
- [#30519](https://github.com/anthropics/claude-code/issues/30519) — community meta-tracker (≥30 open issues).
- [#27040](https://github.com/anthropics/claude-code/issues/27040) — clean repro by community member.

### Fix shape

`XIq` should not hard-reject `ruleContent !== undefined`. When a `filePatternTool` is checked and the rule has content, picomatch the content against the resolved `file_path`. Symmetric fix needed for the deny matcher `xX8`.

---

## RC-BYPASS-GATE

**Status:** Verified.
**Verified on:** claude.exe 2.1.143.a06.
**Severity:** Medium (UX failure — user's explicit opt-in to bypass mode is silently ignored).

### Summary

The default permission context factory `h0()` initializes `isBypassPermissionsModeAvailable: false`. This flag only flips to `true` when the session is *launched* with `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` on the CLI.

When Claude reads `"defaultMode": "bypassPermissions"` from settings.json on startup and calls `setMode("bypassPermissions")`, the setMode gate checks the flag, sees `false`, rejects the change, logs the rejection at debug level only (no UI surface), and the session silently stays in `default` mode.

Same gate exists for `dontAsk` mode, and the policy flags `disableBypassPermissionsMode` / `disableAutoMode` follow the same opt-in-only pattern.

### Evidence

- Full disassembly + setMode gate analysis: [INVESTIGATION.md §Finding #2](../ISSUE-0001/INVESTIGATION.md#finding-2--the-bypasspermissions-mode-gate).
- The log string: `Ignoring permission update: setMode 'bypassPermissions' rejected — mode is not available (disableBypassPermissionsMode set, or session not launched in bypassPermissions mode)` at approximately offset 111875000 in claude.exe.

### Workaround

Launch with `--dangerously-skip-permissions` on the CLI. Settings.json can't bootstrap into bypass mode by design.

### Upstream trackers

- [#39523](https://github.com/anthropics/claude-code/issues/39523) — community meta-tracker (umbrella for bypass mode failures).
- [#15921](https://github.com/anthropics/claude-code/issues/15921) — same multi-bug umbrella, this finding documented there.
- [#49525](https://github.com/anthropics/claude-code/issues/49525) — hook returning `setMode:"bypassPermissions"` silently dropped in 2.1.110+ (same gate, hook code path).
- [#37420](https://github.com/anthropics/claude-code/issues/37420) — bypass mode resets after PreToolUse hook returns "ask" (related mode-state corruption).

### Fix shape

Either let `defaultMode: bypassPermissions` in settings flip `isBypassPermissionsModeAvailable = true` automatically (the user explicitly opted in; their settings are managed by them), or surface the rejection at warn level so users see why their setting didn't apply. Optionally both.

---

## RC-EDIT-PROMPT-2126

**Status:** Closed — not reproduced on current (2026-07-12, claude.exe 2.1.207).
**Proposed on:** 2026-05-18 from FEAT-0001 research pass.
**Suspected affected versions:** 2.1.126+ (per upstream #55255).
**Severity:** n/a (not reproduced).

### Verification (2026-07-12)

Exact reproducer run on **2.1.207** in an isolated `CLAUDE_CONFIG_DIR` sandbox (no hooks): `permissions.allow: ["Edit"]` bare as the *only* rule, target file under cwd, `--print --debug "permission,tool" --permission-mode default`. Result: Edit auto-approved — `tool_dispatch_start tool=Edit permissionDecisionMs=2`, `outcome=ok`, no prompt, file modified. Bare allows were also observed auto-approving in ConPTY-driven **interactive TUI** sessions during the ISSUE-0004 resolution retest, so the verdict covers both entrypoints.

Of the four hypotheses below, #4 ("different code path") was *real but for MCP tools, not Edit* — confirmed and then fixed upstream (see permission-probe ISSUE-0004). The most likely explanation for #55255 remains #3/#4: the reporter was on a session configuration (possibly TUI-side, possibly the VS Code extension layer) that the 2.1.145–2.1.207 fix wave has since repaired. #55255 itself was stale-closed "not planned" with no maintainer comment; no upstream comment owed. Historical bisection of 2.1.126–2.1.143 judged low-value now that the fix wave has landed.

### Summary

Upstream [#55255](https://github.com/anthropics/claude-code/issues/55255) reports that **bare** `Edit` in `permissions.allow` no longer suppresses prompts in Claude Code 2.1.126+. This contradicts the RC-XIQ-MATCHER finding (from 2.1.143.a06) that bare names work — they were the workaround.

Possibilities:
1. **Regression introduced between 2.1.126 and 2.1.143** (i.e., bare allow was broken in some range, then fixed) — unlikely without it being widely reported.
2. **Regression introduced AFTER 2.1.143** (after our investigation) — needs re-test on current claude.exe.
3. **Reporter misread their own setup** — also possible; their setup details may have included something else that subverted the allow.
4. **Different code path** — bare `Edit` allow works in some session configurations and not others (e.g., interactive vs `--print`, or under specific permission modes).

### Evidence needed

- Re-run probe.js methodology against current claude.exe (whatever version is now installed) and against 2.1.126 specifically if it can be obtained.
- Inspect the `XIq` function in the current binary — has the rejection line changed?
- Check if there's a per-mode override that bypasses the bare-name match in some modes.

### Workaround (interim)

If bare allow truly doesn't work, fall back to permission mode `acceptEdits` (run with `--permission-mode acceptEdits`) — that's a mode bypass, not a rule match, and was empirically verified to work in row 3 of the RC-XIQ-MATCHER reproducer matrix.

### Upstream trackers

- [#55255](https://github.com/anthropics/claude-code/issues/55255) — primary report.

### Investigation pointer

This RC is the motivation for the proposed follow-up task `ISSUE-0003` (see PLAN §8).

---

## How to add a new root cause

1. Pick a stable ID: `RC-<DOMAIN>-<SHORT-NAME>` (e.g., `RC-CD-PREFIX-BYPASS`, `RC-SUBAGENT-DIR-PROPAGATION`).
2. Add a section here with the same template (status, summary, evidence, workaround, trackers, fix shape).
3. Update [registry.md](registry.md) rows whose root cause maps to the new ID.
4. If the RC was discovered via internal investigation, link to the relevant task in `tasks/closed/`.

<!-- version: v2026.05.18.01 -->
