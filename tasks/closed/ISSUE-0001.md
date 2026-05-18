# ISSUE-0001: Path-globbed Edit/Read/Write rules and `bypassPermissions` setting silently ignored by Claude Code matcher

**Created:** 2026-05-16
**Status:** Closed
**Closed:** 2026-05-18
**Priority:** High
**Category:** Issue

---

## Summary

Investigate why path-globbed permission rules (e.g. `Edit(/home/me/**)`) in `~/.claude/settings.json` were silently failing to match at runtime in Claude Code, despite appearing loaded by `/permissions`. Two prior diagnostic sessions had landed on confident-but-wrong theories (glob-escape behavior on Windows, working-directory-scope guardrail). This task re-opened the investigation, took a binary-disassembly approach against `claude.exe` 2.1.143.a06, identified the actual root cause(s), produced a workaround hook, and prepared upstream comment drafts so Anthropic can ship a fix.

## Steps to Reproduce

Setup: `~/.claude/settings.json` `permissions.allow` contains `Edit(/home/me/**)` (or platform-equivalent absolute path glob). `cwd` is `/home/me/project-a`. Target file: `/home/me/project-b/notes.md` (under the allow prefix, outside cwd).

Capture matcher behavior directly (no UI prompt) with:

```bash
claude --print --debug "permission,tool" --debug-file out.log \
  --permission-mode default \
  -- "Edit /home/me/project-b/notes.md replacing X with Y, then revert"
```

Four-row reproducer matrix:

| Configuration | Edit result |
|---|---|
| `Edit(/home/me/**)` only | **blocked**; suggestions = `setMode:acceptEdits` only |
| `Edit(/home/me/**)` + `--add-dir "/home/me/project-b"` | **blocked** |
| `--permission-mode acceptEdits` | allowed (mode bypass) |
| `--allowedTools "Read" "Edit" "Write"` (bare, no parens) | **allowed**, `permissionDecisionMs=1` |

Negative test for denies: `--disallowedTools "Edit(/exact/path/to/file.txt)"` does **not** block an Edit to that exact path — the same matcher rejects the deny rule too.

Second symptom: `"defaultMode": "bypassPermissions"` in settings.json silently does nothing; prompts continue to fire as if the setting wasn't there, with no UI surface for the rejection.

## Expected vs Actual Behavior

**Expected:**
- `Edit(/path/**)` in `permissions.allow` auto-allows Edit operations on files matching the glob.
- `Edit(/path/**)` in `permissions.deny` blocks Edit operations on files matching the glob.
- `"defaultMode": "bypassPermissions"` in settings.json puts the session in bypass mode on startup.

**Actual:**
- Path-globbed allow rules are silently no-ops for `Read`, `Edit`, `Write`, `Glob`, `NotebookRead`, `NotebookEdit`, `Skill`, and `mcp__server__tool(arg)`. Only bare tool-name rules ever match.
- Path-globbed deny rules are equally no-op — including any `Edit(/.../secrets/**)` carve-outs users have been writing for safety.
- `"defaultMode": "bypassPermissions"` is silently rejected by a launch-time-only gate; setting it via settings.json never activates the mode.
- `Bash(...)` and `PowerShell(...)` rules with content **do** work, because those tools have their own per-tool content matchers (`dz8` in the binary) that picomatch the command string directly, bypassing the broken filter.

## Root Cause

Two independent bugs in `claude.exe` 2.1.143.a06, both verified by disassembling the Bun-compiled native binary.

**Finding #1 — the `XIq` matcher filter.** The allow matcher `v$_`, deny matcher `xX8`, and ask matcher `JIq` all dispatch through `XIq(tool, rule, opts)`, whose first line is:

```js
if (rule.ruleValue.ruleContent !== void 0) return false;
```

Any rule with parens content (`Edit(/path/**)` → `{toolName: "Edit", ruleContent: "/path/**"}`) is unconditionally rejected. The per-tool `checkPermissions` for `filePatternTools` (`Read`/`Edit`/`Write`/`Glob`/`NotebookRead`/`NotebookEdit`) does only a working-directory scope check — it does not consult `ruleContent`. Bash works because it has its own `dz8` content matcher. File-pattern tools have no equivalent.

**Finding #2 — the `bypassPermissions` launch-time gate.** The default permission context factory `h0()` initializes `isBypassPermissionsModeAvailable: false`. The flag only flips to `true` when the session is *launched* with `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` on the CLI. When Claude reads `"defaultMode": "bypassPermissions"` from settings and calls `setMode("bypassPermissions")`, the setMode gate checks the flag, sees `false`, rejects the change, and logs the rejection at debug level only — no UI warning.

Independent verification that the bug is upstream of picomatch: `probe.js` in this repo loads the user's settings.json, parses each `Edit/Read/Write(...)` rule, and tests every (pattern variant × picomatch option) combination against absolute paths. picomatch correctly matches `C:/Data/**` against Windows absolute paths under every option variant. The matcher never reaches picomatch for these rules — the rule is rejected at `XIq` first.

Full narrative including the methodology, code excerpts, and decision-flow walkthrough is in [`docs/INVESTIGATION.md`](../../docs/INVESTIGATION.md).

## Work Completed

- **Disassembly + analysis.** Located the permission decision flow (`RzA`), the three matcher functions (`v$_`/`xX8`/`JIq`), and the `XIq` predicate inside `claude.exe` using `grep -aob` + `dd` extraction. Identified the `ruleContent !== void 0` reject line. Separately, located the `bypassPermissions` setMode rejection log string and the `h0()` default factory that initializes `isBypassPermissionsModeAvailable: false`.
- **Empirical verification.** Ran the four-row `--print --debug` reproducer matrix against the live harness to confirm path-globbed allow rules, additional-directory grants, and exact-path deny rules all fail; only bare tool-name rules and mode bypass succeed. Negative-tested the deny path too.
- **Eliminated downstream theories.** Built `probe.js` to demonstrate picomatch correctly matches path-globbed patterns against Windows/POSIX absolute paths under every option variant — proving the bug is not in picomatch.
- **Built workaround hook.** `file-deny-guard.py` — a `PreToolUse` hook that lives below the broken `XIq` filter in the decision flow, so it actually fires. Inspects `tool_input.file_path` / `notebook_path` against a user-editable `DENY_PATTERNS` list and emits a `permissionDecision: deny` for matches. Fail-open on JSON parse error (deliberate — bricking a session is worse than the rare passthrough). Patterns are live-editable; only the hook registration needs a Claude restart.
- **Documented Windows install gotcha.** Hook runner's shell parsing strips backslashes from the hook command string; forward slashes in the script path are required (`python C:/path/to/file-deny-guard.py`). Surfaced this in both the README and `INVESTIGATION.md` because it makes every Read/Edit fail-closed in a confusing way if missed.
- **Drafted upstream comments.** Three threads: [#36884](https://github.com/anthropics/claude-code/issues/36884) (primary root-cause report with the disassembly), [#57132](https://github.com/anthropics/claude-code/issues/57132) (Linux variant, cross-link), [#15921](https://github.com/anthropics/claude-code/issues/15921) (multi-bug umbrella thread; covers both Finding #1 and Finding #2, explicit about which symptom is *not* explained). Drafts live in `docs/upstream-comments/`.
- **Published publicly.** Repo licensed GPL-3.0 with a standing Anthropic grant in `NOTICE.md` so the matcher fix or hook ideas can be incorporated upstream without friction. CLAUDE.md added with maintenance contract for future AI sessions plus a portable template users can drop into their own projects' `CLAUDE.md`. Pre-publication scrub pass removed workstation-specific sibling-project names from `probe.js` test paths and the upstream-comment draft. Pushed to `https://github.com/twbarnes1972/permission-probe`.

## Dependencies

| Blocked By | None |

## Acceptance Criteria

- [x] Root cause of path-globbed-rule failure identified at the code level in `claude.exe`, not inferred from symptoms.
- [x] Bug confirmed to be in the matcher layer, not in picomatch (independent verification via `probe.js`).
- [x] Symmetric verification that both allow and deny rules are affected.
- [x] Reproducer is deterministic and runs in `--print --debug` mode without manual UI interaction.
- [x] Second finding (`bypassPermissions` silent rejection) root-caused independently.
- [x] Workaround hook implemented, smoke-tested, and documented with a known-bad install gotcha called out.
- [x] Upstream issues identified and root-cause comments drafted (not just symptom reports).
- [x] Repo published with license + standing Anthropic grant so the workaround can be upstreamed friction-free.

## Related

- [`docs/INVESTIGATION.md`](../../docs/INVESTIGATION.md) — full investigation narrative, methodology, code excerpts, both findings.
- [`docs/upstream-comments/upstream-comment-36884.md`](../../docs/upstream-comments/upstream-comment-36884.md) — primary root-cause comment draft.
- [`docs/upstream-comments/upstream-comment-57132.md`](../../docs/upstream-comments/upstream-comment-57132.md) — Linux cross-link.
- [`docs/upstream-comments/upstream-comment-15921.md`](../../docs/upstream-comments/upstream-comment-15921.md) — multi-bug thread; both findings.
- [`app-src/py-helpers/file-deny-guard.py`](../../app-src/py-helpers/file-deny-guard.py) — workaround hook.
- [`app-src/js-probes/probe.js`](../../app-src/js-probes/probe.js) — picomatch verification probe.
- Commit `5867746` — initial commit (hook + probe).
- Commit `d4b4270` — INVESTIGATION.md added.
- Commit `1839836` — pre-publication scrub.
- Upstream: anthropics/claude-code#36884, #57132, #15921.

<!-- version: v2026.05.18.01 -->
