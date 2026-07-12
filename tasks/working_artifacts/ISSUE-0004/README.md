# ISSUE-0004 working artifacts — TUI permission-testing harness

Artifacts from the 2026-07-12 resolution retest (see [ISSUE-0004 § Resolution](../../closed/ISSUE-0004.md#resolution-2026-07-12)) that verified both permission bugs fixed on claude.exe 2.1.207. Kept because they're reusable: this is the missing half of the `--print --debug` methodology — a way to test the **interactive TUI** permission path programmatically, which `--print` by definition cannot exercise.

## Files

- [`tui-driver.py`](tui-driver.py) — spawns claude.exe under a Windows ConPTY (`pywinpty`) so it runs the real TUI entrypoint (`entrypoint=cli` in the debug log, not `sdk-cli`), types one prompt, and watches the screen for a success marker vs a permission dialog. Auto-answers only the workspace-trust dialog, never a permission prompt (the prompt appearing is the measurement). Config via env vars — see the module docstring.
- [`mini-mcp.py`](mini-mcp.py) — dependency-free stub MCP stdio server with one tool (`ping` → `pong`). Lets you test MCP permission rules without registering a real server (no credentials, no network). Register in the sandbox `.claude.json` as `{"type":"stdio","command":"python","args":["<path>/mini-mcp.py"]}`.

## The sandbox recipe

Tests run under an isolated config dir so live settings/hooks can't mask results:

1. Create a sandbox dir; point `CLAUDE_CONFIG_DIR` at it.
2. Copy `.credentials.json` from the real `~/.claude/` into it (auth only — no other state).
3. Seed `.claude.json` with `{"hasCompletedOnboarding": true, "projects": {"<test-cwd>": {"hasTrustDialogAccepted": true}}}` (plus `bypassPermissionsModeAccepted: true` if testing bypass mode, and `mcpServers` if testing MCP).
4. Write the `settings.json` under test — only the rules being probed, **no hooks**.
5. Always pair a positive run with a negative control (same setup minus the rule under test) before concluding the rule is what caused the behavior.

FEAT-0002's verification suite is the natural long-term home for these; promote them there if that work resumes.
