# permission-probe

Diagnostic tools and a workaround hook for a bug in [Claude Code](https://github.com/anthropics/claude-code) where path-globbed `Edit(...)`, `Read(...)`, `Write(...)` (and friends) allow / deny rules in `~/.claude/settings.json` are **silently ignored** by the permission matcher. Only bare tool-name rules — `Edit`, `Read`, `Write` — actually take effect.

If you've been frustrated by Claude Code prompting for files you've explicitly allowed in your settings, this is probably why.

This repo has two artifacts:

- **`file-deny-guard.py`** — a `PreToolUse` hook that re-implements path-based denies for the affected tools (`Read`, `Edit`, `Write`, `NotebookEdit`, `MultiEdit`). Drop-in workaround until the upstream bug is fixed.
- **`probe.js`** — a diagnostic that loads your `~/.claude/settings.json`, parses every `Edit/Read/Write(...)` rule, and tests each one with the real `picomatch` library against a matrix of path forms and option variants. Useful for proving the bug is *not* in picomatch — it's a layer above.

The full disassembly notes and upstream comment drafts are in [`docs/upstream-comments/`](docs/upstream-comments/).

## The bug in one paragraph

In `claude.exe`'s permission matcher, both the **allow** matcher `v$_(ctx, tool)` and the **deny** matcher `xX8(ctx, tool)` dispatch through `XIq()`. The first line of `XIq` is:

```js
function XIq(tool, rule, opts) {
  if (rule.ruleValue.ruleContent !== void 0) return false;  // <— THE BUG
  let toolName = Om6(tool);
  if (rule.ruleValue.toolName === toolName) return true;
  // proxy-expansion check...
}
```

Any rule with parens content is unconditionally rejected. `Bash(git status:*)` works because Bash's own per-tool checker (`dz8`) matches `ruleContent` directly against the command string. But the file-pattern tools (`Read`, `Edit`, `Write`, `Glob`, `NotebookRead`, `NotebookEdit`) don't have an equivalent — they fall through to `XIq` and get rejected, so path-globbed rules never apply to them.

| Rule in `permissions.allow` | Effect for Edit tool |
|---|---|
| `Edit` (bare) | works — auto-allows any Edit |
| `Edit(/home/me/proj/**)` | **NO-OP** — silently ignored |
| `Edit(C:/Users/me/code/**)` | **NO-OP** — silently ignored |

Same for `deny` rules. So `Edit(/path/to/secrets/**)` in your deny list is *not* protecting that path. You need a hook.

## Reproducer

Run with debug logging to see the matcher's decision directly, no UI prompt required:

```bash
claude --print --debug "permission,tool" --debug-file out.log \
  --permission-mode default \
  -- "Edit /path/outside/cwd/somefile.md replacing X with Y, then revert"
```

Four configurations, four results:

| Config | Result |
|---|---|
| `Edit(/path/**)` in settings.json | **blocked**; debug log shows generic `setMode:acceptEdits` suggestion (no rule-based suggestion) |
| Add `--add-dir /path` (extends working dir scope) | **still blocked** |
| `--permission-mode acceptEdits` | allowed (mode bypass, `permissionDecisionMs=1`) |
| `--allowedTools Read Edit Write` (bare) | allowed (`permissionDecisionMs=1`) |

The first two failures prove neither rule-matching nor additional-directory scope grants Edit on path-globbed rules. The last row is the only thing that works.

A negative test for denies: setting `--disallowedTools "Edit(/exact/path/file.txt)"` does **not** block an Edit to that exact path. The denies are no-ops too.

## Using the hook

1. Clone or copy `file-deny-guard.py` to a stable absolute path on your machine.
2. Edit the `DENY_PATTERNS` list near the top of the file. Examples for Windows / macOS / Linux are included as comments — uncomment what you want, customize the username placeholder.
3. Add a top-level `hooks` block to `~/.claude/settings.json`:

   ```json
   {
     "permissions": { ... },
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
   }
   ```

   **Windows users:** use forward slashes in the command path. `python C:/Users/.../file-deny-guard.py` works; `python C:\\Users\\...\\file-deny-guard.py` does **not** — the shell parsing strips the backslashes and you get fail-closed errors on every Read/Edit. Python on Windows accepts forward-slash paths.

4. Restart Claude Code so the hook gets registered. After that, pattern changes inside the script are live without restart (the script is re-read on every invocation).

5. To verify the hook fires, pipe a test payload to it directly:

   ```bash
   echo '{"tool_name":"Edit","tool_input":{"file_path":"/etc/passwd"}}' | python file-deny-guard.py
   ```

   With `/etc/**` in `DENY_PATTERNS`, expected output is JSON with `"permissionDecision":"deny"`.

You'll also want to make sure your `permissions.allow` list has bare `Read`, `Edit`, `Write` (not the path-globbed forms) — otherwise you'll continue to get prompts for files outside your cwd despite the hook being installed.

## Using the probe

```bash
npm install        # picomatch dep
node probe.js
```

Outputs, per test path, every `(pattern variant × picomatch option)` combination that matches. The probe demonstrates that picomatch correctly matches path-globbed patterns against absolute Windows / POSIX paths under every option variant — proving the bug is upstream of picomatch.

If you're investigating a *different* permission issue and want to add your own test paths or rules, edit the `TEST_PATHS` constant near the top of `probe.js`.

## Status

Bug reported in upstream issues:

- [anthropics/claude-code#36884](https://github.com/anthropics/claude-code/issues/36884) — Windows + macOS + native CLI report; full root-cause comment with the `XIq` disassembly
- [anthropics/claude-code#57132](https://github.com/anthropics/claude-code/issues/57132) — Linux variant of the same bug
- [anthropics/claude-code#15921](https://github.com/anthropics/claude-code/issues/15921) — long-running multi-bug thread; root cause for two of the three reported symptoms

When upstream lands a fix, this repo becomes obsolete — you can revert to using `Edit(/path/**)` rules directly and remove the hook.

## Affected versions

Verified on `claude.exe` 2.1.143.a06 on Windows. The same matcher code is in the shared JS bundle, so Linux and macOS hit the same bug — confirmed by independent reproducers in the upstream issues across all three platforms.

## License

GPL-3.0 — see [LICENSE](LICENSE). Strong copyleft: if you distribute derivative works, they must also be released under GPL-3.0.

In addition, the copyright holder grants Anthropic, PBC a standing, irrevocable license to use this code under any terms of their choosing for inclusion in Claude Code or related Anthropic products — see [NOTICE.md](NOTICE.md) for the full grant. This carve-out exists specifically because the tool is a workaround for a Claude Code bug, and the author wants Anthropic to be able to incorporate it (or the underlying ideas) without friction. It does not extend to other third parties.
