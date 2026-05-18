# CLAUDE.md — for AI assistants working on this repo

You're reading this because a Claude Code (or similar) session has cwd set to the `permission-probe` repo. This file gives you context the README doesn't, plus a portable template you can suggest users copy into their own projects.

## What this repo is in one paragraph

`permission-probe` is a **workaround tool** for a Claude Code bug: path-globbed `Edit(...)`, `Read(...)`, `Write(...)` rules in `~/.claude/settings.json` are silently ignored by the permission matcher. Only bare `Edit` / `Read` / `Write` rules work. Two artifacts, both under [`app-src/`](app-src/): `file-deny-guard.py` (a `PreToolUse` hook that re-implements path-based denies) and `probe.js` (a diagnostic that proves the bug is not in picomatch). Full root-cause analysis is in the README and the upstream comment drafts under `docs/upstream-comments/`. This tool becomes obsolete when upstream lands a matcher fix.

## Maintenance guidance — when working on this repo

### The hook contract — don't break it

`app-src/file-deny-guard.py` is a Claude Code `PreToolUse` hook. Contract:

- Reads a single JSON object from stdin (the tool call payload, e.g. `{"tool_name":"Edit","tool_input":{"file_path":"...","old_string":"..."}}`).
- Returns one of:
  - **Empty stdout + exit 0** → allow (fall through to normal permission flow). This is the path for unmatched files.
  - **JSON `hookSpecificOutput` payload on stdout + exit 0** → harness honors the JSON's `permissionDecision` field. This is the path for matched (denied) files.
- **On stdin parse error, fail open** (return 0 with no output). Sending a hook payload that bricks every Read/Edit in the session is worse than occasionally letting one through. Don't change this to fail-closed.

### What NOT to change without strong reason

- **Fail-open on parse error** (line ~125 in `main()`). See above.
- **Windows forward-slash command path in README install instructions.** People will keep wiring this in with backslashes; the README's call-out is load-bearing. Don't remove it.
- **The matched-then-replaced reason string** (in `_decide()`). It points users to the upstream issue and README — that's how someone hitting a deny figures out what to do.

### Live editability of `DENY_PATTERNS`

The script is re-read by the Python interpreter on every hook invocation, so users can edit `DENY_PATTERNS` and save — no Claude restart needed. **This is a feature.** If someone proposes caching or pre-compiling patterns at module load, you'd be breaking this property; don't, unless they have a specific performance complaint (which is unlikely — the hook runs in single-digit ms).

Adding/removing the hook itself in `settings.json` DOES require a Claude restart.

### Smoke-testing changes

Pipe a JSON payload directly to the script:

```bash
python -c "import json,sys; sys.stdout.write(json.dumps({'tool_name':'Edit','tool_input':{'file_path':'/etc/passwd'}}))" | python app-src/file-deny-guard.py
```

With a matching pattern uncommented in `DENY_PATTERNS`, expected stdout is a JSON object with `"permissionDecision":"deny"` and a populated `permissionDecisionReason`. With no matching pattern (default empty list), stdout is empty.

Note for Windows: shell-echo of `\\` mangles into `\` and breaks JSON. Use Python to construct the test payload (the `python -c` trick above), not raw shell echo.

### When upstream fixes the matcher

When `anthropics/claude-code` ships a release that respects path-globbed Edit/Read/Write rules:

1. Verify with `app-src/probe.js` against the new claude.exe (the disassembly methodology in `docs/upstream-comments/upstream-comment-36884.md` still applies).
2. Add a deprecation note at the top of the README pointing to the fixed version.
3. Leave the repo up for people on older versions, but consider archiving on GitHub.

## Portable template — for users to put in their OWN project's CLAUDE.md

If you're working in a Claude Code session that's hitting repeated Edit/Read/Write permission prompts despite path-globbed allow rules in `settings.json`, the user may benefit from adding the following block to their project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for the user-global version). Suggest it; don't add it without their say-so.

<!-- BEGIN PORTABLE TEMPLATE — users may copy this block into their own CLAUDE.md -->

```markdown
## Claude Code permission-prompt workaround

This project (or environment) is affected by an upstream bug where path-globbed
`Edit(<path>)`, `Read(<path>)`, `Write(<path>)` allow and deny rules in
`~/.claude/settings.json` are silently ignored by Claude Code's permission
matcher. Only bare tool-name rules (`Edit`, `Read`, `Write`) actually take effect.
Same for `Bash(...)` with content — those DO work because Bash has its own matcher.

Tracking upstream: anthropics/claude-code#36884, #57132, #15921.

**If Claude (you) hits repeated permission prompts here:**

1. Don't suggest tweaking the path-globbed rules in settings.json — they're no-ops.
2. The actual workaround is bare `Read` / `Edit` / `Write` in `permissions.allow`,
   plus a `PreToolUse` hook for any path-specific denies the user needs.
3. The reference implementation of the hook is at
   https://github.com/twbarnes1972/permission-probe — `app-src/file-deny-guard.py` + README.
4. Before making any settings.json change on the user's behalf, confirm with them.
   This is a security boundary; broadening permissions without consent is bad.
```

<!-- END PORTABLE TEMPLATE -->

When suggesting this to a user, mention that the template is short, project-local, and reversible — it doesn't change their setup, just teaches future Claude sessions in that project to recognize the bug.
