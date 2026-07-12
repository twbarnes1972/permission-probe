#!/usr/bin/env python
"""
PreToolUse hook that re-implements allow-rule honoring for MCP tools
(`mcp__<server>__<tool>`) in interactive (TUI) Claude Code sessions, working
around a bug where bare MCP allow rules in ~/.claude/settings.json
`permissions.allow` are honored by the `--print`/sdk-cli path but NOT by the
interactive TUI path.

How the bug manifests (verified 2026-05-19, claude.exe 2.1.144):

  - With ~/.claude/settings.json `permissions.allow` containing entries like
    `"mcp__stackagentic-gateway__list_projects"` (bare, no parens) AND the
    wildcard `"mcp__*"`, a fresh `claude --print` subprocess auto-allows the
    call: debug log shows `permissionDecisionMs=0` and the tool runs.
  - The same settings.json in an interactive TUI session does NOT auto-allow.
    The call surfaces a permission prompt (sometimes hard to see / dismiss),
    and any user input that isn't an explicit approval results in a silent
    rejection -- the harness records `user_rejected` and Claude sees
    "tool use was rejected" with no indication that a prompt fired.
  - Entrypoint divergence: `cc_entrypoint=sdk-cli` (the --print path) auto-
    approves; `cc_entrypoint=cli` (interactive TUI) does not. Both run the
    same matcher rules per settings.json's debug-log dump on startup.

This hook fills the gap. It runs BEFORE the broken TUI gate and emits an
explicit `permissionDecision: "allow"` for MCP tool calls whose tool name
matches an entry in `~/.claude/settings.json` `permissions.allow`. The
hook honors both bare-exact rules (e.g. `mcp__server__tool`) and prefix
wildcards (`mcp__*`, `mcp__server__*`).

Wiring (add a SECOND PreToolUse entry alongside any existing file-deny
hook; don't merge matchers):

    "hooks": {
      "PreToolUse": [
        { "matcher": "Read|Edit|Write|NotebookEdit|MultiEdit",
          "hooks": [{"type": "command", "command": "python /path/to/file-deny-guard.py"}] },
        { "matcher": "mcp__.*",
          "hooks": [{"type": "command", "command": "python /path/to/mcp-allow-guard.py"}] }
      ]
    }

IMPORTANT on Windows: use forward slashes in the command path (the hook
runner mangles backslashes). See file-deny-guard.py header for the
detailed rationale.

Behavior:
  - Hook reads ~/.claude/settings.json on every invocation. No caching.
    Edit `permissions.allow` and save -- the next MCP call picks up the
    new rule without restarting Claude. (Adding the hook itself in
    settings.json DOES require a restart.)
  - On JSON-parse failure of the stdin payload OR settings.json, the hook
    FAILS OPEN (lets the call fall through to normal permission flow).
    Better to occasionally prompt than to brick MCP calls.
  - Deny rules in `permissions.deny` for MCP tools are also honored
    (symmetric to allow). Deny takes precedence over allow.
"""

import json
import os
import sys


def _settings_path() -> str:
    home = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    return os.path.join(home, ".claude", "settings.json")


def _load_allow_deny() -> tuple[list[str], list[str]]:
    """Return (allow, deny) lists from settings.json. Empty lists on failure."""
    try:
        with open(_settings_path(), "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return [], []
    perms = data.get("permissions") or {}
    allow = perms.get("allow") or []
    deny = perms.get("deny") or []
    return [r for r in allow if isinstance(r, str)], [r for r in deny if isinstance(r, str)]


def _matches_mcp_rule(tool_name: str, rule: str) -> bool:
    """True if `rule` is an MCP rule that would match `tool_name`.

    Honored forms (bare, no parens content -- ruleContent forms are not
    supported here because Claude's own matcher rejects them via the XIq
    filter regardless):

      - `mcp__server__tool` exact match
      - `mcp__server__*`   prefix-with-wildcard (any tool of one server)
      - `mcp__*`           catch-all for any MCP tool
    """
    if "(" in rule:
        # Has parens content -- the XIq matcher rejects these anyway;
        # we don't try to re-implement that. Could be added later if
        # an MCP server needs per-input gating.
        return False
    if not rule.startswith("mcp__"):
        return False
    if rule == "mcp__*":
        return True
    if rule.endswith("__*"):
        return tool_name.startswith(rule[:-1])  # strip trailing '*'
    return rule == tool_name


def _decide(tool_name: str) -> dict | None:
    if not tool_name.startswith("mcp__"):
        return None  # Hook matcher already filters, but be defensive.
    allow, deny = _load_allow_deny()
    for rule in deny:
        if _matches_mcp_rule(tool_name, rule):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"mcp-allow-guard.py: MCP tool {tool_name!r} matches deny rule {rule!r} "
                        f"in ~/.claude/settings.json permissions.deny."
                    ),
                }
            }
    for rule in allow:
        if _matches_mcp_rule(tool_name, rule):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": (
                        f"mcp-allow-guard.py: MCP tool {tool_name!r} matches allow rule {rule!r}. "
                        f"Interactive TUI sessions silently drop bare MCP allow rules that the "
                        f"--print/sdk-cli path honors (see permission-probe README); this hook "
                        f"reapplies them."
                    ),
                }
            }
    return None  # No rule matched -- fall through to normal permission flow.


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return 0  # Fail open.
    tool_name = payload.get("tool_name", "")
    decision = _decide(tool_name)
    if decision is not None:
        sys.stdout.write(json.dumps(decision))
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
