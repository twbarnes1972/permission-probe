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
        "command": "python /absolute/path/to/file-deny-guard.py"
      }]
    }]
  }
}
```

Customize the `DENY_PATTERNS` list at the top of `file-deny-guard.py` for paths you want blocked. Windows / macOS / Linux examples are included as commented-out entries. Restart Claude Code once to register the hook; after that, pattern edits are live (no restart).

**Windows:** use forward slashes in the hook command path — `python C:/path/to/file-deny-guard.py`, not backslashes. The hook runner's shell parsing strips `\\` and you get fail-closed errors on every Read/Edit. Python on Windows accepts forward slashes.

## Repository layout

```
file-deny-guard.py        # the PreToolUse hook — ~90 lines, customize DENY_PATTERNS
probe.js                  # Node diagnostic, proves picomatch isn't the bug
docs/
  INVESTIGATION.md        # full disassembly walkthrough — read for the "why"
  upstream-comments/      # drafts of the three comments posted to anthropics/claude-code
CLAUDE.md                 # guidance for AI assistants (maintenance + portable template)
LICENSE                   # GPL-3.0
NOTICE.md                 # standing Anthropic carve-out on top of the GPL
```

## Running the probe

```bash
npm install
node probe.js
```

Loads `~/.claude/settings.json`, parses every path-globbed rule, and tests each against your real file paths with the same `picomatch` library Claude Code uses. Useful for verifying the matcher bug is what's hitting you (and not some other settings-loading issue) before installing the hook.

## Status

Open upstream — when [#36884](https://github.com/anthropics/claude-code/issues/36884) and friends ship a fix, this workaround becomes obsolete. [`docs/INVESTIGATION.md`](docs/INVESTIGATION.md#verifying-the-bug-is-still-present-in-a-future-release) has the recipe for verifying when the fix lands.

## License

GPL-3.0 with a standing carve-out for Anthropic, PBC. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
