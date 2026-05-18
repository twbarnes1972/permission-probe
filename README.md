# permission-probe

A `PreToolUse` hook and diagnostic for a Claude Code permission-matcher bug where path-globbed `Edit(...)`, `Read(...)`, `Write(...)` allow/deny rules in `~/.claude/settings.json` are silently ignored. If you've been hit by Claude Code prompting for files you've explicitly allowed in settings, this is why.

Full story: [`docs/INVESTIGATION.md`](docs/INVESTIGATION.md). Upstream tracking: [#36884](https://github.com/anthropics/claude-code/issues/36884) · [#57132](https://github.com/anthropics/claude-code/issues/57132) · [#15921](https://github.com/anthropics/claude-code/issues/15921).

## Quick start

In `~/.claude/settings.json`:

```jsonc
{
  "permissions": {
    "allow": ["Read", "Edit", "Write", "..."]    // bare — path-globbed forms are no-ops
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "Read|Edit|Write|NotebookEdit|MultiEdit",
      "hooks": [{
        "type": "command",
        "command": "python /absolute/path/to/app-src/py-helpers/file-deny-guard.py"
      }]
    }]
  }
}
```

Customize the `DENY_PATTERNS` list at the top of `app-src/py-helpers/file-deny-guard.py` for paths you want blocked. Windows / macOS / Linux examples are included as commented-out entries. Restart Claude Code once to register the hook; after that, pattern edits are live (no restart).

**Windows:** use forward slashes in the hook command path — `python C:/path/to/app-src/py-helpers/file-deny-guard.py`, not backslashes. The hook runner's shell parsing strips `\\` and you get fail-closed errors on every Read/Edit. Python on Windows accepts forward slashes.

## Also useful as a reference

Beyond the specific bug, this repo doubles as a worked example for two recurring needs:

- **Debugging Claude Code permission issues.** [`docs/INVESTIGATION.md`](docs/INVESTIGATION.md#methodology) walks through the diagnostic methodology: `claude --print --debug "permission,tool" --debug-file out.log` to capture matcher decisions without UI prompts, plus offset-and-`dd` binary disassembly when the docs disagree with reality. Reusable for any Claude Code permission question, not just this one.
- **Writing a `PreToolUse` hook.** [`app-src/py-helpers/file-deny-guard.py`](app-src/py-helpers/file-deny-guard.py) is a minimal-but-complete hook (~90 lines) with the right error handling (fail-open on parse error, never brick a session), the canonical `hookSpecificOutput` response format, and live editability (script re-read on each invocation, so config changes don't need a Claude restart). Usable as a starting template for `PostToolUse`, `Notification`, and the other hook types — they all follow the same stdin-JSON / stdout-JSON / exit-zero shape. The contract is documented in [`CLAUDE.md`](CLAUDE.md#the-hook-contract--dont-break-it).

## Repository layout

```
app-src/
  py-helpers/
    file-deny-guard.py    # the PreToolUse hook — ~90 lines, customize DENY_PATTERNS
  js-probes/
    probe.js              # Node diagnostic, proves picomatch isn't the bug
    package.json          # picomatch dep for probe.js
docs/
  INVESTIGATION.md        # full disassembly walkthrough — read for the "why"
  upstream-comments/      # drafts of the three comments posted to anthropics/claude-code
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

Open upstream — when [#36884](https://github.com/anthropics/claude-code/issues/36884) and friends ship a fix, this workaround becomes obsolete. [`docs/INVESTIGATION.md`](docs/INVESTIGATION.md#verifying-the-bug-is-still-present-in-a-future-release) has the recipe for verifying when the fix lands.

## License

GPL-3.0 with a standing carve-out for Anthropic, PBC. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
