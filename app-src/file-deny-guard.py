#!/usr/bin/env python
"""
PreToolUse hook that enforces path-based denies for Read/Edit/Write/NotebookEdit/
MultiEdit, working around a Claude Code bug where path-globbed allow and deny
rules in settings.json (e.g. `Edit(/home/me/secrets/**)`) are silently ignored
by the allow/deny matchers for file-pattern tools.

How the bug works (verified by disassembling claude.exe and running --print
probe sessions with --debug logging):

  - In the permission matcher, the allow matcher `v$_(ctx, tool)` and the
    deny matcher `xX8(ctx, tool)` both dispatch through `XIq()`.
  - `XIq()`'s first line is:  if (rule.ruleValue.ruleContent !== void 0) return false;
  - That means any rule WITH parens content (e.g. `Edit(/path/**)`) is
    skipped. Only bare tool-name rules (e.g. `Edit`) ever match.
  - The Edit/Read/Write tools themselves do NOT consult ruleContent for
    allow/deny — they only do a working-directory-scope check.
  - Net result: every `Edit(<path>)` / `Read(<path>)` / `Write(<path>)` allow
    or deny rule in settings.json is a no-op for those tools. (Bash and
    PowerShell rules with content DO still work — those tools have their
    own content matcher.)

Upstream issues this hook works around:
  - https://github.com/anthropics/claude-code/issues/36884
  - https://github.com/anthropics/claude-code/issues/57132
  - https://github.com/anthropics/claude-code/issues/15921

This hook fills the gap by inspecting `tool_input.file_path` (or
`notebook_path`) for the affected tools and emitting a deny decision when the
path matches a configured pattern. Patterns live in `DENY_PATTERNS` below;
edit and save to change them — the script is re-read on each invocation, so
no Claude restart is needed for pattern changes (a restart IS needed to
register the hook itself the first time).

Wiring (top-level `hooks` block in ~/.claude/settings.json):

    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Read|Edit|Write|NotebookEdit|MultiEdit",
          "hooks": [
            {
              "type": "command",
              "command": "python /absolute/path/to/file-deny-guard.py"
            }
          ]
        }
      ]
    }

IMPORTANT on Windows: the hook runner's shell parsing strips backslashes from
the command string. Use forward slashes in the script path:

    "command": "python C:/path/to/file-deny-guard.py"

NOT `python C:\\path\\to\\file-deny-guard.py` — that gets mangled to
`C:pathtofile-deny-guard.py` and every Read/Edit fails-closed with a
confusing "can't open file" error. Python on Windows accepts forward slashes.

Matching semantics:
  - Patterns are glob-like with `**` (multi-segment, matches across path
    separators), `*` (single-segment wildcard), `?` (single char), case-
    insensitive on Windows. Both pattern and tested path are normalized via
    os.path.normpath() before matching.
  - Only absolute paths are checked. Relative paths fall through (they
    can't escape working-directory guards anyway).
  - On JSON-parse failure of the stdin payload, the hook FAILS OPEN (lets
    the tool through). Better to occasionally allow than to brick every
    Read/Edit if some upstream system mangles the payload.
"""

import fnmatch
import json
import os
import re
import sys


# ============================================================================
# Customize this list for your environment. Each entry is a glob-like path
# pattern (** for multi-segment, * for single-segment wildcard). The hook is
# case-insensitive on Windows. Use raw strings (r"...") to avoid escape issues.
#
# Leave the list empty to make the hook a no-op (lets everything through).
# Uncomment / add entries to enforce specific denies.
# ============================================================================
DENY_PATTERNS = [
    # --- Windows examples ---
    # r"C:\Windows\**",
    # r"C:\Program Files\**",
    # r"C:\Program Files (x86)\**",
    # r"C:\Users\<your-username>\.ssh\**",
    # r"C:\Users\<your-username>\.claude\.credentials.json",
    # r"C:\Users\<your-username>\AppData\Roaming\Microsoft\Crypto\**",

    # --- macOS examples ---
    # r"/System/**",
    # r"/Library/**",
    # r"/usr/**",
    # r"/Users/<your-username>/.ssh/**",
    # r"/Users/<your-username>/.claude/.credentials.json",

    # --- Linux examples ---
    # r"/etc/**",
    # r"/usr/**",
    # r"/var/**",
    # r"/root/**",
    # r"/home/<your-username>/.ssh/**",
    # r"/home/<your-username>/.claude/.credentials.json",
]


def _expand_separators(pattern: str) -> str:
    """Normalize separators to the OS native form so matching is consistent."""
    return pattern.replace("/", os.sep)


def _matches(path: str, pattern: str) -> bool:
    """Case-insensitive ** match. Both inputs use OS sep."""
    p = os.path.normpath(path).lower()
    pat = os.path.normpath(_expand_separators(pattern)).lower()
    if "**" in pat:
        # Treat `**` as "any sequence including separators". Split, regex-escape
        # each literal segment, join with `.*`, anchor end with \Z, DOTALL so
        # `.` crosses path separators.
        parts = [re.escape(seg) for seg in pat.split("**")]
        rx = ".*".join(parts)
        return re.match(rx + r"\Z", p, re.DOTALL) is not None
    return fnmatch.fnmatchcase(p, pat)


def _decide(tool_name: str, tool_input: dict) -> dict | None:
    """Return a deny decision dict, or None if no match."""
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not file_path:
        return None
    if not os.path.isabs(file_path):
        return None  # Relative paths can't escape cwd guards; let them through.
    for pat in DENY_PATTERNS:
        if _matches(file_path, pat):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"file-deny-guard.py: path {file_path!r} matches deny pattern {pat!r}. "
                        f"Path-globbed Edit/Read/Write rules in Claude Code's settings.json "
                        f"are silently ignored by the matcher (see anthropics/claude-code #36884); "
                        f"this hook enforces them instead."
                    ),
                }
            }
    return None


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        # Fail open — don't break the session if upstream sends mangled JSON.
        return 0
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    decision = _decide(tool_name, tool_input)
    if decision is not None:
        sys.stdout.write(json.dumps(decision))
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
