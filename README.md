# permission-probe

> **⚠️ DEPRECATED — both bugs are fixed upstream as of Claude Code 2.1.207 (verified 2026-07-12).**
> Path-globbed `Edit/Read/Write(...)` allow **and** deny rules, `"defaultMode": "bypassPermissions"` in settings.json, and bare MCP allow rules in the interactive TUI all work natively now. The fix landed silently somewhere in 2.1.145–2.1.207 (upstream never commented on the tracked issues; the old broken `XIq` filter is still in the binary, bypassed by a new content-matching path). Verification method + results: [`tasks/closed/ISSUE-0004.md`](tasks/closed/ISSUE-0004.md#resolution-2026-07-12).
> If you're on an older version, everything below still applies. Otherwise: delete the hook entries from `settings.json` and use native rules.

`PreToolUse` hooks and diagnostics for two related Claude Code permission bugs where bare and path-globbed allow/deny rules in `~/.claude/settings.json` are silently ignored. If you've been hit by Claude Code prompting for files you've explicitly allowed — or by MCP tools silent-failing in interactive sessions despite explicit allow rules — this is why.

Full story (bug 1): [`tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md`](tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md). Upstream tracking: [#36884](https://github.com/anthropics/claude-code/issues/36884) · [#57132](https://github.com/anthropics/claude-code/issues/57132) · [#15921](https://github.com/anthropics/claude-code/issues/15921).
Full story (bug 2, 2026-05-19): [`tasks/closed/ISSUE-0004.md`](tasks/closed/ISSUE-0004.md). Bare `mcp__*` and `mcp__<server>__<tool>` allow rules are honored by the `--print`/sdk-cli code path but silently dropped by the interactive TUI code path. Fixed upstream (see deprecation note above).

## Quick start

In `~/.claude/settings.json`:

```jsonc
{
  "permissions": {
    "allow": ["Read", "Edit", "Write", "..."]    // bare — path-globbed forms are no-ops
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write|NotebookEdit|MultiEdit",
        "hooks": [{
          "type": "command",
          "command": "python /absolute/path/to/app-src/py-helpers/file-deny-guard.py"
        }]
      },
      {
        "matcher": "mcp__.*",
        "hooks": [{
          "type": "command",
          "command": "python /absolute/path/to/app-src/py-helpers/mcp-allow-guard.py"
        }]
      }
    ]
  }
}
```

The first hook covers bug 1: customize the `DENY_PATTERNS` list at the top of `app-src/py-helpers/file-deny-guard.py` for paths you want blocked. Windows / macOS / Linux examples are included as commented-out entries.

The second hook covers bug 2 (MCP TUI silent-fail): no per-user customization needed — the hook reads your existing `permissions.allow`/`permissions.deny` lists and re-applies the bare MCP rules that the TUI matcher drops. If you don't use MCP tools, you can omit this entry.

Restart Claude Code once to register the hooks; after that, edits to `DENY_PATTERNS` and to `permissions.allow`/`permissions.deny` are live (no restart needed).

**Windows:** use forward slashes in the hook command path — `python C:/path/to/app-src/py-helpers/file-deny-guard.py`, not backslashes. The hook runner's shell parsing strips `\\` and you get fail-closed errors on every Read/Edit. Python on Windows accepts forward slashes.

## Also useful as a reference

Beyond the specific bug, this repo doubles as a worked example for two recurring needs:

- **Debugging Claude Code permission issues.** [`tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md`](tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md#methodology) walks through the diagnostic methodology: `claude --print --debug "permission,tool" --debug-file out.log` to capture matcher decisions without UI prompts, plus offset-and-`dd` binary disassembly when the docs disagree with reality. Reusable for any Claude Code permission question, not just this one.
- **Writing a `PreToolUse` hook.** [`app-src/py-helpers/file-deny-guard.py`](app-src/py-helpers/file-deny-guard.py) is a minimal-but-complete hook (~90 lines) with the right error handling (fail-open on parse error, never brick a session), the canonical `hookSpecificOutput` response format, and live editability (script re-read on each invocation, so config changes don't need a Claude restart). Usable as a starting template for `PostToolUse`, `Notification`, and the other hook types — they all follow the same stdin-JSON / stdout-JSON / exit-zero shape. The contract is documented in [`CLAUDE.md`](CLAUDE.md#the-hook-contract--dont-break-it).

## Repository layout

```
app-src/
  py-helpers/
    file-deny-guard.py    # bug 1 PreToolUse hook — customize DENY_PATTERNS
    mcp-allow-guard.py    # bug 2 PreToolUse hook — re-applies MCP allow rules in TUI
  js-probes/
    probe.js              # Node diagnostic, proves picomatch isn't the bug
    package.json          # picomatch dep for probe.js
tasks/
  closed/ISSUE-0001.md    # retrospective task record for bug 1
  closed/ISSUE-0004.md    # bug 2 task record
  working_artifacts/ISSUE-0001/
    INVESTIGATION.md      # full disassembly walkthrough — read for the "why"
    upstream-comments/    # drafts of the three comments posted to anthropics/claude-code
CLAUDE.md                 # guidance for AI assistants (maintenance + portable template)
LICENSE                   # GPL-3.0
NOTICE.md                 # standing Anthropic carve-out on top of the GPL
```

## Running the probe

```bash
cd app-src/js-probes
npm install
node probe.js
```

Loads `~/.claude/settings.json`, parses every path-globbed rule, and tests each against your real file paths with the same `picomatch` library Claude Code uses. Useful for verifying the matcher bug is what's hitting you (and not some other settings-loading issue) before installing the hook.

## Status

**Fixed upstream — this workaround is obsolete on Claude Code ≥ 2.1.207** (see the deprecation note at the top). The fix was never announced: [#36884](https://github.com/anthropics/claude-code/issues/36884) and [#55255](https://github.com/anthropics/claude-code/issues/55255) were closed "not planned" and [#15921](https://github.com/anthropics/claude-code/issues/15921) sits open without maintainer comment, but behavioral retesting on 2026-07-12 confirms all symptoms resolved — including in the interactive TUI, verified by driving a real session under ConPTY. Retest method and logs: [`tasks/closed/ISSUE-0004.md`](tasks/closed/ISSUE-0004.md#resolution-2026-07-12). The repo stays up for users on older versions.

## License

GPL-3.0 with a standing carve-out for Anthropic, PBC. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
