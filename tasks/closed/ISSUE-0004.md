# ISSUE-0004: TUI silently ignores MCP allow rules that `--print`/sdk-cli honors

**Created:** 2026-05-19
**Status:** Closed (fixed upstream; verified on 2.1.207)
**Closed:** 2026-07-12
**Priority:** High
**Category:** Issue

---

## Resolution (2026-07-12)

**Fixed upstream, verified on claude.exe 2.1.207.** Retested alongside [ISSUE-0001](ISSUE-0001.md); both are resolved. The fix landed silently somewhere in 2.1.145–2.1.207 — upstream issues #36884 and #55255 were closed "not planned" and #15921 remains open with no maintainer comment, so no fix version was ever announced.

Verification method (all under an isolated `CLAUDE_CONFIG_DIR` sandbox — no hooks, crafted settings.json, negative controls):

- **MCP allow in TUI (this issue):** a credential-free stub MCP stdio server (`mini`, one tool `ping`) registered only in the sandbox; `"mcp__mini__ping"` bare allow rule; interactive TUI driven programmatically via ConPTY (`pywinpty`), confirming `entrypoint=cli` in the debug log. Result: `tool_dispatch_start tool=mcp__mini__ping permissionDecisionMs=0 ... outcome=ok`, no prompt, `pong` returned. **Fixed.**
- **ISSUE-0001 allow side:** `Edit(<glob>)`-only allow, target outside cwd → edit allowed (`permissionDecisionMs=3`); negative control with no Edit rule → blocked. **Fixed.**
- **ISSUE-0001 deny side:** bare `Edit` allow + `Edit(<glob>)` deny → blocked, in both `--print` and ConPTY-driven TUI (file content confirmed unchanged). **Fixed.**
- **ISSUE-0001 finding #2:** `"defaultMode": "bypassPermissions"` in sandbox settings.json → session started in `ctx.mode=bypassPermissions`, edit succeeded with zero allow rules, no "setMode rejected" log line. **Fixed.** (Caveat: sandbox `.claude.json` had `bypassPermissionsModeAccepted: true` seeded; the gate may be conditional on prior acceptance of the bypass warning dialog.)

Notably, the `XIq` reject filter (`ruleValue.ruleContent!==void 0 → return false`, minified as `pto` in 2.1.207 at offset ~232912623) is **still present** in the binary — the fix added a separate content-matching path rather than removing the broken filter.

Consequences applied 2026-07-12: both workaround hooks (`file-deny-guard.py`, `mcp-allow-guard.py`) retired from the maintainer's live `~/.claude/settings.json` (native path-globbed deny rules take over); README deprecation note added; INVESTIGATION.md compatibility table annotated. The unfiled upstream report is moot. Remaining unchecked acceptance criteria below are superseded by this resolution.

## Summary

In `~/.claude/settings.json` `permissions.allow`, bare MCP tool rules — both `mcp__*` (wildcard) and `mcp__<server>__<tool>` (explicit) — are **honored by the `--print`/sdk-cli code path** but **silently dropped by the interactive TUI code path**, with the same settings, the same minute, the same machine. The TUI surfaces a permission prompt that the matcher should have auto-approved; any input the user gives that isn't an explicit approval is recorded as `user_rejected`, which the assistant sees as "tool use was rejected" with no indication a prompt fired (hence "silent" from the user's perspective).

Verified 2026-05-19 on claude.exe 2.1.144 (Bun-compiled native, Windows). Same shape as ISSUE-0001's `XIq` matcher bug but on a different fork in the binary — the bug is between entrypoints, not in rule parsing.

Workaround in this repo: [`app-src/py-helpers/mcp-allow-guard.py`](../../app-src/py-helpers/mcp-allow-guard.py) — a `PreToolUse` hook with matcher `mcp__.*` that reads `~/.claude/settings.json` and emits `permissionDecision: "allow"` when the MCP tool name matches a configured rule. Wired into `~/.claude/settings.json` 2026-05-19.

## Steps to Reproduce

Setup: `~/.claude/settings.json` `permissions.allow` contains both `"mcp__*"` and at least one explicit `"mcp__<server>__<tool>"` rule (bare, no parens). The MCP server in question is connected (`claude mcp list` shows ✓).

1. **From a `--print` subprocess** (sdk-cli entrypoint):
   ```bash
   claude --print --debug "permission,tool" --debug-file out-sdk.log \
     --permission-mode default \
     -- "Call mcp__<server>__<tool> with no arguments"
   ```
   Result: `permissionDecisionMs=0`, `tool_dispatch_end ... outcome=ok`. No prompt fires. The call returns real data.

2. **From an interactive TUI session** (cli entrypoint), same settings.json, same project:
   ```
   claude --debug "permission,tool" --debug-file out-tui.log
   ```
   At the prompt, type: `Call mcp__<server>__<tool> with no arguments`.
   Result: The call is staged but never auto-approves. The session shows a permission request that, from the user's perspective, is either invisible or hard to identify; any input that isn't an explicit "always allow" / "allow once" registers in the transcript as `user_rejected` and the tool call returns an error to the assistant.

The two logs side-by-side show: identical 40-rule allow list parsed at startup (both paths), identical `gateway:Connection established`, divergent permission decision.

## Expected vs Actual

**Expected:** Bare `mcp__<server>__<tool>` allow rules should fire across all entrypoints. The compatibility table in [INVESTIGATION.md](../working_artifacts/ISSUE-0001/INVESTIGATION.md#whats-actually-working-in-your-settingsjson) lists `mcp__server__tool (bare)` as "yes" — that's now known to be `--print`-only.

**Actual:** Bare MCP allow rules work in `--print` and fail in interactive TUI. The matcher rule-load is identical between paths (verified via `[DEBUG] Applying permission update: Adding 40 allow rule(s)` in both subprocess debug logs), so the divergence is downstream of rule loading — somewhere in the auto-approval / prompt-routing path that's specific to TUI mode.

## Root Cause

**Provisional** (workaround built without full disassembly because the hook bypasses the gate regardless of which exact branch is responsible). Three observations narrow the search:

1. **Workspace trust is NOT the cause.** `~/.claude.json` shows `"hasTrustDialogAccepted": true` for `C:/Data/Workspace/permission-probe`. The MCP `headersHelper for MCP server '...' executed before workspace trust is confirmed` security check at offset ~131291060 in claude.exe is not what fires here.
2. **Permission mode is `default`** in both the failing session (`{"type":"permission-mode","permissionMode":"default",...}` first line of the session transcript) and the working subprocess (`--permission-mode default` explicit, also tested without the flag with identical success).
3. **Entrypoint values differ:** subprocess logs `cc_entrypoint=sdk-cli`, interactive session records `entrypoint: "cli"` in transcript events. The enum lives at offset ~110431768 (`sdk-ts, sdk-py, sdk-cli, cli, mcp, serve, claude-code-github-action`).

The most likely fork: a TUI-mode-only step in the permission decision flow that fails to consult `mcp__*` allow rules (or applies them with different precedence vs. an "ask" outcome). Disassembly of the TUI-specific permission path is the path to a definite RC; the workaround does not require it.

## Workaround (this repo)

[`app-src/py-helpers/mcp-allow-guard.py`](../../app-src/py-helpers/mcp-allow-guard.py) — a `PreToolUse` hook that runs above the broken TUI gate and emits an explicit `permissionDecision: "allow"` for any MCP tool call whose name matches a rule in `~/.claude/settings.json` `permissions.allow`. Honored rule forms:

- `mcp__server__tool` (bare exact)
- `mcp__server__*` (per-server wildcard)
- `mcp__*` (catch-all)

Deny rules in `permissions.deny` for the same forms are honored symmetrically, with deny taking precedence over allow.

Wiring (added to `~/.claude/settings.json` `hooks.PreToolUse` alongside the existing file-deny-guard entry):

```json
{
  "matcher": "mcp__.*",
  "hooks": [
    {
      "type": "command",
      "command": "python C:/Data/Workspace/permission-probe/app-src/py-helpers/mcp-allow-guard.py"
    }
  ]
}
```

Takes effect on next Claude restart (hook registration requires restart per [CLAUDE.md](../../CLAUDE.md#live-editability-of-deny_patterns)). After registration, the script is re-read on every invocation — edits to allow/deny rules in settings.json are picked up live.

## Relation to ISSUE-0003

[ISSUE-0003](../open/ISSUE-0003.md) tracks upstream [#55255](https://github.com/anthropics/claude-code/issues/55255), which reports that bare `Edit` allow no longer suppresses Edit prompts in 2.1.126+. Hypothesis #4 there was "Different code path — bare allow works in some session configurations and not others." **This investigation confirms that pattern exists in 2.1.144 for MCP tools.** The same TUI-vs-subprocess divergence may explain #55255 if the reporter was on TUI and the team's testing was on `--print`. ISSUE-0003 should re-test bare `Edit` allow specifically in TUI mode to determine whether the same fork affects file-pattern tools.

In this session, bare `Read`/`Edit`/`Write`/`Bash` allow rules were observed working in TUI mode without prompts. So if the bug DOES affect Edit, it's gated on something more specific than tool-class.

## Dependencies

| Blocked By | None |

Adjacent: [ISSUE-0003](../open/ISSUE-0003.md) — re-test bare `Edit` allow in TUI specifically; this finding suggests the right reproducer to use.

## Acceptance Criteria

- [x] Workaround hook (`mcp-allow-guard.py`) implemented, smoke-tested (5 cases), and wired into `~/.claude/settings.json`.
- [ ] Maintainer verifies in a fresh session post-restart that MCP tools no longer silently fail.
- [ ] [INVESTIGATION.md](../working_artifacts/ISSUE-0001/INVESTIGATION.md) compatibility table updated with a TUI column.
- [ ] [README.md](../../README.md) updated to mention the second hook + when each one is needed.
- [ ] Upstream report drafted (analogous to [ISSUE-0001 upstream comments](../working_artifacts/ISSUE-0001/upstream-comments/)); not yet filed.
- [ ] (Optional, follow-up) Full disassembly of the TUI permission code path to pin the exact divergent branch.

## Implementation Notes

- Hook design intentionally narrow (`mcp__.*` matcher) so it doesn't interfere with file-pattern tools or Bash.
- Hook reads `~/.claude/settings.json` on every invocation (no caching), matching the live-editability pattern of `file-deny-guard.py`.
- On JSON parse failure of either stdin or settings.json, the hook fails OPEN — same defensive default as file-deny-guard.
- Memory note: `feedback_powershell_utf8_bom.md` and `project_live_hook_dependency.md` both apply here. The new hook script's path in settings.json must be updated if the repo is ever moved.

## Related

- [ISSUE-0001](ISSUE-0001.md) — methodology source; same `XIq` matcher bug pattern, different fork in the binary.
- [INVESTIGATION.md](../working_artifacts/ISSUE-0001/INVESTIGATION.md) — disassembly methodology used here.
- [ISSUE-0003](../open/ISSUE-0003.md) — may be partially explained by this finding if #55255's reporter was on TUI.
- `app-src/py-helpers/file-deny-guard.py` — sibling hook; same contract and conventions.

<!-- version: v2026.07.12.01 -->
