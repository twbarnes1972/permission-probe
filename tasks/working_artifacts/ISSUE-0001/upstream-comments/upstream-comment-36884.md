<!--
Comment draft for: https://github.com/anthropics/claude-code/issues/36884
"VS Code Extension Permission Rules Not Respected"

Post this as a comment (not a new issue). Paste body below "Add a comment".
-->

Reproduced on the native Windows CLI (`claude.exe` 2.1.143.a06), not just the VS Code extension — same root cause, so the fix would close both surfaces. Spent a couple of sessions tracking this down; sharing the disassembly notes in case it saves the team time.

## Root cause

In claude.exe's permission matcher, both the **allow** matcher `v$_(ctx, tool)` and the **deny** matcher `xX8(ctx, tool)` dispatch through `XIq()`. The first line of `XIq` is:

```js
function XIq(tool, rule, opts) {
  if (rule.ruleValue.ruleContent !== void 0) return false;  // <— this
  let toolName = Om6(tool);
  if (rule.ruleValue.toolName === toolName) return true;
  // proxy-expansion check...
}
```

Any rule with parens content (`Edit(...anything...)`) is unconditionally rejected by the matcher. Only bare tool-name rules (`Edit`, `Read`, `Write`) ever return true. The per-tool `checkPermissions` for `filePatternTools` (Read / Edit / Write / Glob / NotebookRead / NotebookEdit) doesn't compensate — it does only a working-directory scope check, not a `ruleContent` check. So path-globbed rules in `permissions.allow` and `permissions.deny` are silently no-ops for those tools.

`Bash(...)` and `PowerShell(...)` rules with content **do** work because the Bash tool has its own content matcher (`dz8` in the binary) that picomatches the command string against `ruleContent` directly. That's why the original reporter saw Bash rules respected while Edit/Write rules were ignored.

This is **not** a Windows path-normalization issue. `picomatch` handles `C:/Data/**` vs `C:\Data\foo` correctly on Windows under every option variant I tested (`windows:true`, `windows:false`, `posix:true`, no opts, nocase, etc.). The bug is at a layer above picomatch — the rule never reaches the matcher in the first place.

## Empirical reproducer (4-row matrix)

Setup: `~/.claude/settings.json` `permissions.allow` contains `Edit(C:/Data/**)`. CWD = `C:\Data\projects\current-repo`. Target: edit a file at `C:\Data\projects\sibling-repo\NOTES.md` (under the allowed prefix, outside CWD).

| Configuration | Edit result |
|---|---|
| `Edit(C:/Data/**)` only | **blocked**; only "suggestion" is `setMode:acceptEdits` |
| `Edit(C:/Data/**)` + `--add-dir "C:\Data\Workspace"` (the file's parent dir) | **blocked** |
| `--permission-mode acceptEdits` | allowed (mode bypass, `permissionDecisionMs=1`) |
| `--allowedTools "Read" "Edit" "Write"` (bare, no parens) | **allowed**, `permissionDecisionMs=1` |

Each row's debug output captured via:

```
claude.exe --print --debug "permission,tool" --debug-file out.log --permission-mode default -- "<edit prompt>"
```

The "blocked" rows' debug log shows `Permission suggestions for Edit: [{"type":"setMode","mode":"acceptEdits","destination":"session"}]` — a generic suggestion, NOT a rule-based one. That tells you the matcher couldn't find any rule that would grant the path, even though `Edit(C:/Data/**)` is in the allow list and the file is under that prefix.

Negative test: `--disallowedTools "Edit(<exact path>)"` does **not** block an Edit to that exact path either. Same `XIq` filter — denies with `ruleContent` are no-ops for Read/Edit/Write/NotebookEdit just like allows are.

**Implication for existing users**: any `Edit(.../sd/**)` or `Read(.../secrets/**)` deny rules people have been relying on for safety have likely been no-ops the whole time, with protection coming only from behavioral conventions in CLAUDE.md and filesystem ACLs.

## Suggested fix

The matcher's `XIq` should not hard-reject `ruleContent !== undefined`. Instead, when a `filePatternTool` is being checked and the rule has `ruleContent`, the rule content should be `picomatch`'d against the resolved `file_path` (or for Glob, the `pattern`/`path`). The lookup table at `sI8.filePatternTools` already enumerates the affected tools (`Read`, `Write`, `Edit`, `Glob`, `NotebookRead`, `NotebookEdit`).

A symmetric fix for the deny matcher `xX8` is required at the same time, otherwise users will land in the worst case: bare `Edit` allows work, but path-specific denies still don't, so the explicit safety carve-outs they wrote remain unenforced.

## Workaround (today)

Two parts:

1. **In `~/.claude/settings.json` `permissions.allow`**: replace any path-globbed `Edit(...)`/`Read(...)`/`Write(...)` rules with bare `Edit`/`Read`/`Write`. The bare form actually works.

2. **For path-specific denies**: enforce via a `PreToolUse` hook, since `Edit(<path>)` denies in settings.json are no-ops. Minimal Python hook:

   ```python
   # file-deny-guard.py
   import json, os, sys, re
   DENY = [r"C:\Windows\**", r"C:\Program Files\**", r"C:\Users\<otheruser>\**"]
   data = json.loads(sys.stdin.read() or "{}")
   fp = (data.get("tool_input") or {}).get("file_path", "")
   if not (fp and os.path.isabs(fp)): sys.exit(0)
   p = os.path.normpath(fp).lower()
   for pat in DENY:
       pat_n = os.path.normpath(pat).lower()
       rx = ".*".join(re.escape(s) for s in pat_n.split("**")) + r"\Z"
       if re.match(rx, p, re.DOTALL):
           print(json.dumps({"hookSpecificOutput":{
               "hookEventName":"PreToolUse",
               "permissionDecision":"deny",
               "permissionDecisionReason": f"deny pattern {pat!r} matched {fp!r}"}}))
           break
   ```

   Wire via `"hooks": {"PreToolUse":[{"matcher":"Read|Edit|Write|NotebookEdit|MultiEdit","hooks":[{"type":"command","command":"python C:/path/to/file-deny-guard.py"}]}]}` in settings.json. **Note**: use forward slashes in the command's script path — the hook runner's shell parsing strips backslashes (separate, smaller issue, easy to work around).

The hook + bare-allows combo gives back the same safety posture that path-globbed rules were supposed to provide, and the hook config can be edited without a Claude restart (the Python script is re-read on each invocation).

## Environment

- Windows 11 Pro 10.0.26200
- claude.exe 2.1.143.a06 (from `cc_version` in the API attribution header)
- Native CLI install at `~/.local/bin/claude.exe` (Bun-compiled, 218MB)
- Node 24.15.0, Python 3.14, picomatch 4.0.4 (used for independent verification)

Happy to share the full disassembly notes, probe scripts, and `--debug` log captures if useful — they're in a public-ish workstation repo and can be pulled out.
