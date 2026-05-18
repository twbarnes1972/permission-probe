<!--
Comment draft for: https://github.com/anthropics/claude-code/issues/15921
"[BUG] VSCode Extension: .claude/settings.local.json permissions not respected for Bash/Write/Edit operations"

This thread has accumulated three distinct bugs under one umbrella. Our root cause
explains ONE of them — the Edit/Write/CLI portion. Comment is scoped to that piece
and is explicit about what we are NOT explaining.
-->

This thread has accumulated multiple distinct failure modes under one umbrella. I can root-cause **two of them** from a disassembly of `claude.exe` 2.1.143.a06: the Edit/Write path-globbed-rules-ignored half (per @losjoe Feb 9 and @Kieldro Apr 15) and the `bypassPermissions`-mode-silently-rejected half (per several commenters). The third — Bash rules being ignored specifically in the VSCode extension while working on the CLI (OP's primary symptom) — is a different layer that I haven't traced.

## Root cause for the Edit/Write/CLI half

I disassembled `claude.exe` 2.1.143.a06 (Bun-compiled native binary) to chase a closely-related Windows reproducer. In the permission matcher, both the **allow** matcher `v$_(ctx, tool)` and the **deny** matcher `xX8(ctx, tool)` dispatch through `XIq()`, whose first line is:

```js
function XIq(tool, rule, opts) {
  if (rule.ruleValue.ruleContent !== void 0) return false;  // <— this
  let toolName = Om6(tool);
  if (rule.ruleValue.toolName === toolName) return true;
  // proxy-expansion check...
}
```

Any rule with parens content (`Edit(...)`, `Write(...)`, `Read(...)`, `Glob(...)`, `Skill(...)`, `mcp__name(...)`) is unconditionally rejected by the matcher. Only bare tool-name rules (`Edit`, `Write`, `Read`) ever match. The per-tool `checkPermissions` for `filePatternTools` (Read / Edit / Write / Glob / NotebookRead / NotebookEdit) doesn't compensate — it does only a working-directory scope check.

`Bash(...)` and `PowerShell(...)` rules with content **do** work because Bash has its own content matcher (`dz8`) that picomatches the command string against `ruleContent` directly. That's why patterns like `Bash(dir:*)` work on the CLI but `Edit(C:/Data/**)` doesn't.

Cross-platform: same matcher code in the shared JS bundle, so Linux/macOS/Windows all hit it identically. See [#36884](https://github.com/anthropics/claude-code/issues/36884#issuecomment-4474702923) for the full disassembly notes, four-row reproducer matrix, and `--print --debug` recipe.

## Root cause for the `bypassPermissions`-mode-silently-rejected half

Same methodology, different code path. The binary contains this exact log string:

> `Ignoring permission update: setMode 'bypassPermissions' rejected — mode is not available (disableBypassPermissionsMode set, or session not launched in bypassPermissions mode)`

The mode is gated by an `isBypassPermissionsModeAvailable` flag on the permission context. The default factory `h0()` initializes that flag to `false`:

```js
var h0 = () => ({
  mode: "default",
  additionalWorkingDirectories: new Map,
  alwaysAllowRules: {},
  alwaysDenyRules: {},
  alwaysAskRules: {},
  isBypassPermissionsModeAvailable: !1
});
```

The flag only flips to `true` when the session is **launched** with `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` on the CLI. So when someone puts `"defaultMode": "bypassPermissions"` in `settings.json` and starts a session the normal way:

1. Claude reads the setting on startup and attempts `setMode("bypassPermissions")`.
2. The setMode gate sees `isBypassPermissionsModeAvailable === false` and rejects the change.
3. The rejection logs at debug level only — no UI surface, no warning.
4. The session silently stays in `default` mode and continues to prompt.

**Workaround for this one:** launch with `--dangerously-skip-permissions` on the CLI; `defaultMode` in settings.json can't bootstrap into bypass mode by design. The same opt-in-per-session gate also exists for `dontAsk` mode and the `disableBypassPermissionsMode`/`disableAutoMode` policy flags follow the same pattern.

This is independent of the `XIq` matcher bug above — it's a separate "opt-in-only gate that fails silently" issue. The fix is small in both cases but different: either let `defaultMode: bypassPermissions` in settings flip `isBypassPermissionsModeAvailable = true` automatically, or surface the rejection at warn level so users see why their setting didn't apply.

## Note on the OP's Read/Glob/Grep observation

@elliottgaryusa noted Read/Glob/Grep worked while Edit/Write didn't. Worth being precise: Read/Glob/Grep on files **inside the current working directory** don't need a permission rule at all — the working-directory scope check grants them. The `Read(**)` rule isn't what's allowing those; it's the scope. Try a Read of a file **outside** cwd (e.g., from `~/something-else/file.md` when cwd is a different project) and Read fails too, for the same `XIq` reason.

## Workaround — same one @nikhilsitaram and @RoboLagoon already arrived at

A `PreToolUse` hook that inspects `tool_input.file_path` (or `tool_input.command` for Bash if you need the same for that bug) and emits a deny decision when patterns match. Independently confirms what others in this thread built — the hook layer is below the broken `XIq` filter, so it actually fires. The minimal Python reference is inline in the [#36884 comment](https://github.com/anthropics/claude-code/issues/36884#issuecomment-4474702923).

Gotcha worth flagging for Windows users: the hook command string in `settings.json` needs **forward slashes** in the script path (`python C:/path/to/guard.py` not `python C:\\path\\to\\guard.py`) — backslashes get stripped by the hook runner's shell parsing, which makes every Read/Edit/Write fail-closed with a confusing `can't open file 'mangledpath'` error.

## What this comment does NOT explain

- **Bash rules being ignored in the VSCode extension specifically** (OP's primary symptom). Bash's own `dz8` content matcher works on the CLI (verified — `Bash(dir:*)` honored, `Bash(rm -rf:*)` denies fire), so this is a different layer — likely the VSCode extension loading settings from a different scope or handling permissions in a separate IPC path. Possibly related to [#43787](https://github.com/anthropics/claude-code/issues/43787) (project-level settings ignored by VSCode extension). I haven't traced the extension's code paths.

Worth maintainers splitting this thread into separate issues for distinct triage. The two bugs I've root-caused (`XIq` matcher reject and `bypassPermissions` opt-in gate) are both small, isolated fixes touching different functions; they can ship independently.
