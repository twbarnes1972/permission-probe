# Investigation — how the permission-matcher bug was found

A single-document walkthrough of the full investigation. The README explains how to *use* the workaround; this file explains how the bug was actually found, what code in `claude.exe` causes it, and how to verify the bug is still present in a future release.

If you're skimming: jump to [Finding #1](#finding-1--the-xiq-matcher-bug) and [Finding #2](#finding-2--the-bypasspermissions-mode-gate) for the two root causes. The rest is methodology, evidence, and implications.

---

## The setup

Symptom: in a Claude Code session with `cwd` set to a project directory, attempting to `Edit` a file in a sibling repo under the user's broader workspace (e.g. cwd = `/home/me/project-a`, file = `/home/me/project-b/notes.md`) **always prompted for permission**, despite `~/.claude/settings.json` containing:

```json
"permissions": {
  "allow": [
    "Read(/home/me/**)",
    "Edit(/home/me/**)",
    "Write(/home/me/**)"
  ]
}
```

Two prior diagnostic sessions over two days landed on confident-but-wrong theories:

- **Theory 1 (the "backslash glob escape" hypothesis):** glob libraries treat `\` as an escape character, so on Windows `Edit(C:\Data\**)` after JSON decode collapses to an effective pattern that matches nothing. Tested by switching all path-globs to forward slashes — no improvement.
- **Theory 2 (the "working-directory scope guardrail" hypothesis):** Claude Code might have a second guardrail (`permissions.additionalDirectories`) that runs before the matcher and restricts file access to cwd by default. Tested by adding `"additionalDirectories": ["/home/me"]` to settings — also no improvement.

Both theories failed the empirical test: even with `--add-dir "/home/me/project-b"` passed on the CLI (which puts the file's parent directly into the working-directories list with the highest-precedence `cliArg` source), the Edit *still* prompted. Something else had to be going on.

## Methodology

`claude.exe` (Windows native CLI, 2.1.143.a06, ~218MB) is a **Bun-compiled native binary** with the JavaScript bundle embedded. Three techniques to extract the relevant code:

1. **Find offsets via `grep -aob`** for distinctive identifiers:

   ```bash
   grep -aob "additionalDirectories" /path/to/claude.exe | head -20
   grep -aob "alwaysAllowRules\|alwaysDenyRules" /path/to/claude.exe
   grep -aob "checkPermissions\|matchPath\|ruleValue" /path/to/claude.exe
   ```

2. **Extract printable context with `dd`** around each offset (filter binary noise with `tr`):

   ```bash
   dd if=/path/to/claude.exe bs=1 skip=$((OFFSET-500)) count=2000 status=none \
     | tr -c '[:print:][:space:]' '.'
   ```

3. **Verify findings with `--print --debug` probe runs** against the live harness:

   ```bash
   claude --print --debug "permission,tool" --debug-file out.log \
     --permission-mode default \
     -- "Edit /path/outside/cwd/somefile.md ..."
   ```

   The debug log emits `Permission suggestions for <tool>: [...]` immediately followed by `<tool> tool permission denied` (in `--print` mode the harness auto-rejects rather than prompt). The contents of the suggestions array tells you which rules the matcher *could* see as relevant. Generic `setMode:acceptEdits` as the only suggestion means it found no rule-based path to allow.

This combination — disassembly to read the code, `--debug` runs to verify behavior, `app-src/js-probes/probe.js` (in this repo) to confirm the matcher's downstream library (`picomatch`) is working correctly — is enough to ground-truth what the matcher actually does.

---

## Finding #1 — the `XIq` matcher bug

### The decision flow

In `claude.exe`, the master per-tool permission decision happens in `RzA()`. Extracted approximately verbatim (variable names are the minified ones from the Bun bundle):

```js
async function RzA(tool, input, ctx) {
  if (ctx.abortController.signal.aborted) throw new Xf;

  // 1. Check deny rules first
  let K = xX8(ctx.getToolPermissionContext(), tool);
  if (K) return {
    behavior: "deny",
    decisionReason: {type: "rule", rule: K},
    message: `Permission to use ${tool.name} has been denied.`
  };

  // 2. Check ask rules
  let _ = JIq(ctx.getToolPermissionContext(), tool);
  if (_) {
    if (!(tool.name === I$ && cq.isSandboxingEnabled() && ...))
      return {behavior: "ask", decisionReason: {type: "rule", rule: _}, ...};
  }

  // 3. Run the tool's own checkPermissions
  let A = {behavior: "passthrough", message: SA(tool.name)};
  try {
    let parsedInput = tool.inputSchema.parse(input);
    A = await tool.checkPermissions(parsedInput, ctx);
  } catch (...) {...}

  if (A?.behavior === "deny") return A;
  // ... mode-handling: bypassPermissions, etc.

  // 4. Check allow rules — THIS IS WHERE THE BUG MATTERS
  let M = v$_(ctx.getToolPermissionContext(), tool);
  if (M) return {behavior: "allow", updatedInput: ..., decisionReason: {type: "rule", rule: M}};

  // 5. No rule matched — coerce passthrough to ask
  let O = A.behavior === "passthrough"
    ? {...A, behavior: "ask", message: SA(tool.name, A.decisionReason)}
    : A;
  if (O.behavior === "ask" && O.suggestions)
    N(`Permission suggestions for ${tool.name}: ${SH(O.suggestions, null, 2)}`);
  return O;
}
```

Three matchers — `v$_` (allow), `xX8` (deny), `JIq` (ask) — all dispatch through `XIq()`:

```js
function v$_(ctx, tool) {
  return FNH(ctx).find(rule => XIq(tool, rule)) || null;
}
function xX8(ctx, tool) {
  return s4H(ctx).find(rule => XIq(tool, rule, {proxyExpansion: ..., toolAliases: ctx.toolAliases})) || null;
}
function JIq(ctx, tool) {
  return gNH(ctx).find(rule => XIq(tool, rule, {proxyExpansion: ..., toolAliases: ctx.toolAliases})) || null;
}
```

### The bug

`XIq()`'s first line:

```js
function XIq(tool, rule, opts) {
  if (rule.ruleValue.ruleContent !== void 0) return false;  // ← THE BUG
  let toolName = Om6(tool);
  if (rule.ruleValue.toolName === toolName) return true;
  if (opts && AK8(rule.ruleValue.toolName, opts.toolAliases).includes(toolName)) return true;
  let A = Ny(rule.ruleValue.toolName), f = Ny(toolName);
  return A !== null && f !== null
    && (A.toolName === void 0 || A.toolName === "*")
    && A.serverName === f.serverName;
}
```

**Any rule with `ruleContent !== undefined` is unconditionally rejected.** A settings.json entry like `Edit(/path/**)` is parsed into `{toolName: "Edit", ruleContent: "/path/**"}` — the moment `XIq` sees the `ruleContent`, it returns `false`. Only bare tool-name rules (no parens) ever match.

### Why Bash and PowerShell work despite this

The Bash tool has its **own** content matcher (`dz8` in the binary) that runs as part of its `tool.checkPermissions` call. `dz8` picomatches the bash command string against each `Bash(...)` rule's `ruleContent` directly, bypassing `XIq`'s reject. That's why `Bash(git status:*)` works correctly while `Edit(/path/**)` doesn't.

The file-pattern tools (`Read`, `Edit`, `Write`, `Glob`, `NotebookRead`, `NotebookEdit`) have **no equivalent** in their `checkPermissions`. Their content check is only a working-directory scope check — "is this file inside cwd or `additionalWorkingDirectories`?" — with no consultation of the rules' `ruleContent`. So they fall through to the `XIq`-based matchers, which reject any path-globbed rule.

You can find this asymmetry in the binary by searching for `sI8` (the registry):

```js
sI8 = {
  filePatternTools: ["Read", "Write", "Edit", "Glob", "NotebookRead", "NotebookEdit"],
  bashPrefixTools: ["Bash"],
  customValidation: {WebSearch: ..., WebFetch: ...}
}
```

The `filePatternTools` are *supposed* to be checked against `ruleContent`-as-glob — that's literally what the registry is for. But the matcher implementation never does it.

### Empirical confirmation — the four-row reproducer

Setup: `~/.claude/settings.json` `permissions.allow` contains `Edit(/home/me/**)` (or platform-equivalent absolute path glob). `cwd` is `/home/me/project-a`. Target: edit `/home/me/project-b/notes.md`.

| Configuration                                              | Edit result                                       |
|------------------------------------------------------------|---------------------------------------------------|
| `Edit(/home/me/**)` only                                   | **blocked**; suggestions = `setMode:acceptEdits` only |
| `Edit(/home/me/**)` + `--add-dir "/home/me/project-b"`     | **blocked** (additional-dir doesn't grant Edit)   |
| `--permission-mode acceptEdits`                            | allowed (mode bypass, `permissionDecisionMs=1`)   |
| `--allowedTools "Read" "Edit" "Write"` (bare, no parens)   | **allowed**, `permissionDecisionMs=1`             |

Each row's behavior captured directly via:

```bash
claude --print --debug "permission,tool" --debug-file out.log \
  --permission-mode default \
  -- "<the edit prompt>"
```

The blocked rows' debug logs show `Permission suggestions for Edit: [{"type":"setMode","mode":"acceptEdits","destination":"session"}]` — a *generic* suggestion, not a rule-based one. The matcher couldn't find any rule that would grant the path, even though `Edit(/home/me/**)` is sitting right there in the allow list and the file is unambiguously under that prefix.

### Negative test — denies are equally broken

`--disallowedTools "Edit(/exact/path/to/file.txt)"` does **not** block an Edit to that exact path. Same `XIq` filter rejects the rule. This is the more alarming half of the bug: any path-globbed deny rule someone has been relying on for security (e.g. `Edit(/home/me/secrets/**)`) is silently no-op.

### What's actually working in your settings.json

Going through the typical user's allow/deny lists:

| Rule form                                | Tool        | Honored? |
|------------------------------------------|-------------|----------|
| `Edit` (bare)                            | Edit        | yes      |
| `Edit(/path/**)`                         | Edit        | **NO**   |
| `Read(/path/**)`                         | Read        | **NO**   |
| `Write(/path/**)`                        | Write       | **NO**   |
| `Glob(/path/**)`                         | Glob        | **NO**   |
| `Bash` (bare)                            | Bash        | yes      |
| `Bash(git status:*)`                     | Bash        | yes      |
| `PowerShell(git config *)`               | PowerShell  | yes      |
| `Skill(some-skill)`                      | Skill       | **NO** (same XIq filter) |
| `mcp__server__tool` (bare, no parens)    | MCP         | yes (sdk-cli) / **NO** (TUI) † |
| `mcp__*` (catch-all wildcard)            | MCP         | yes (sdk-cli) / **NO** (TUI) † |
| `mcp__server__tool(arg)` (with parens)   | MCP         | **NO**   |

The pattern: any rule with `ruleContent` works only if the corresponding tool has its own content matcher (Bash, PowerShell). Otherwise it's a no-op.

**RESOLVED upstream (added 2026-07-12):** every **NO** in this table (and the † TUI divergence below) was retested on claude.exe **2.1.207** and now works: path-globbed `Edit(...)` allow rules match, path-globbed deny rules override bare allows (verified in both `--print` and ConPTY-driven interactive TUI), `"defaultMode": "bypassPermissions"` activates from settings.json, and bare MCP allow rules are honored in the TUI (`permissionDecisionMs=0`, `entrypoint=cli`). Notably the `XIq` reject filter (`ruleContent!==void 0 → return false`, now minified as `pto`) is *still present* in the 2.1.207 binary — upstream fixed the behavior by adding a separate content-matching path rather than removing the filter. The table above is preserved as the record for ≤2.1.144. Full retest method and logs: [ISSUE-0004 § Resolution](../../closed/ISSUE-0004.md#resolution-2026-07-12).

**† Entrypoint-dependent (added 2026-05-19, see [ISSUE-0004](../../closed/ISSUE-0004.md)):** the "yes" verdict on bare MCP rules above is `--print`/sdk-cli only. The interactive TUI path silently drops bare MCP allow rules, surfacing a prompt the matcher should have auto-approved. Verified on claude.exe 2.1.144. Workaround: `app-src/py-helpers/mcp-allow-guard.py` re-applies MCP allow rules in TUI mode via a `PreToolUse` hook. The original 2026-05-16 testing for this table was done entirely in `--print` mode, which is why this divergence wasn't caught in the initial run; bare `Edit`/`Read`/`Write`/`Bash` rules were observed working in both modes during the 2026-05-19 follow-up, so the entrypoint fork appears MCP-specific or at least narrower than tool-class-wide. See [ISSUE-0004](../../closed/ISSUE-0004.md) for the full reproducer.

---

## Finding #2 — the `bypassPermissions` mode gate

A second, independent bug found during the same disassembly pass.

### The symptom

Users put `"defaultMode": "bypassPermissions"` in their `settings.json` expecting it to suppress all permission prompts. It silently does nothing — prompts continue to fire as if the setting wasn't there. There's no UI warning explaining why.

### The cause

`claude.exe` contains this exact log string at offset ~111875000:

> `Ignoring permission update: setMode 'bypassPermissions' rejected — mode is not available (disableBypassPermissionsMode set, or session not launched in bypassPermissions mode)`

The default permission context is initialized by the factory `h0()`:

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

The flag `isBypassPermissionsModeAvailable` is **false by default**. It only flips to `true` when the session is *launched* with `--dangerously-skip-permissions` or `--permission-mode bypassPermissions` on the CLI.

When Claude reads `"defaultMode": "bypassPermissions"` from settings.json on startup and attempts to call `setMode("bypassPermissions")`:

1. The setMode gate checks `isBypassPermissionsModeAvailable`.
2. Sees `false`, rejects the change.
3. Logs the rejection at debug level only — no UI surface.
4. Session silently stays in `default` mode.
5. Prompts keep firing.

### The fix shape

Either let `defaultMode: bypassPermissions` in settings flip `isBypassPermissionsModeAvailable = true` automatically (the user explicitly opted into it; their settings are managed by them), or surface the rejection at warn level so the user sees why their setting didn't take effect. The current behavior — silent rejection of a setting the user explicitly wrote — is the worst of both worlds.

### Workaround

Launch with `--dangerously-skip-permissions` on the CLI. The same opt-in-per-session gate exists for `dontAsk` mode, and policy flags `disableBypassPermissionsMode` and `disableAutoMode` follow the same pattern.

---

## Implications

### What this means for your existing settings

Most users have written settings that *look* secure but aren't:

- `"Edit(/home/me/secrets/**)"` in deny → no-op; secrets aren't protected from Claude's Edit tool
- `"defaultMode": "bypassPermissions"` → no-op; mode never activates
- `"Skill(some-untrusted-skill)"` in deny → no-op; skill can still run
- `"Edit"` (bare) in allow → works; Edit is auto-allowed for *all* paths

The functional security boundary for file operations has effectively been:

1. Whether Claude's cwd allows the path (working-directory scope check)
2. Filesystem ACLs
3. Bare allow rules
4. The harness asking the user interactively when scope didn't grant it

Path-globbed allows and denies have been window dressing.

### What this means for fixing it

Two fixes, both small and isolated, can ship independently:

1. **Matcher fix:** when a `filePatternTool` is checked and the rule has `ruleContent`, picomatch the content against the resolved `file_path` (or `pattern` for Glob). The `sI8.filePatternTools` lookup table already enumerates the affected tools. Symmetric fix needed for the deny matcher `xX8`, otherwise users are worse off (bare `Edit` allows work but path-specific denies still don't, so the safety carve-outs people wrote remain unenforced).

2. **bypassPermissions gate fix:** either auto-flip `isBypassPermissionsModeAvailable` when `defaultMode: bypassPermissions` appears in settings, or surface the rejection at warn level. Optionally both.

### Workaround in this repo

Bare `Read` / `Edit` / `Write` in `permissions.allow` (the only form the matcher honors), plus the `PreToolUse` hook (`app-src/py-helpers/file-deny-guard.py`) to re-implement path-based denies. The hook lives below the broken `XIq` filter in the decision flow, so it actually fires. See the README for install instructions.

---

## Upstream issues

Bug reported and root-cause-analyzed in these upstream threads (drafts of the comments are in `upstream-comments/`):

- [anthropics/claude-code#36884](https://github.com/anthropics/claude-code/issues/36884) — Windows + macOS + native CLI reports; full root cause comment
- [anthropics/claude-code#57132](https://github.com/anthropics/claude-code/issues/57132) — Linux variant of the same bug
- [anthropics/claude-code#15921](https://github.com/anthropics/claude-code/issues/15921) — long-running multi-bug thread; both Finding #1 and Finding #2 documented there

When upstream lands a fix, this investigation becomes historical record and the README should be updated to point at the fixed version.

## Verifying the bug is still present in a future release

If you want to check whether a newer `claude.exe` has fixed the matcher, the methodology is:

```bash
# 1. Find the offset of XIq's distinctive first-line behavior
grep -aob "ruleContent" /path/to/new/claude.exe | head

# 2. Extract context around an interesting offset
dd if=/path/to/new/claude.exe bs=1 skip=$((OFFSET-500)) count=2000 status=none \
  | tr -c '[:print:][:space:]' '.'

# 3. Look for the "if (rule.ruleValue.ruleContent !== void 0) return false" pattern
#    in the v$_ / xX8 / XIq area. If it's gone, the matcher fix likely landed.
```

Or much faster — just run the four-row reproducer matrix at the top of [Finding #1](#finding-1--the-xiq-matcher-bug). If row 1 (`Edit(/path/**)` only) is *no longer blocked*, the fix is in. Confirm with a positive deny test too — set `--disallowedTools "Edit(<exact path>)"` and verify it actually blocks now. Both halves need to work before the workaround in this repo becomes obsolete.
