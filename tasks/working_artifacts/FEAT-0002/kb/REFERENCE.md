# Claude Code Permissions + Security — Reference

Single source of truth for documented + observed behavior. Cited and version-pinned. Maintenance per [README §How to update](README.md#how-to-update).

---

## Permission matcher

**Doc URL:** [code.claude.com/docs/en/permissions.md](https://code.claude.com/docs/en/permissions.md)
**Coverage:** Deep
**Last verified:** 2026-05-18 / claude.exe 2.1.143.a06 (Windows)

### Documented behavior

`permissions.allow` / `permissions.deny` / `permissions.ask` arrays in settings.json contain rules; rules are evaluated in order: **deny → ask → allow**, first match wins. Deny rules from any scope prevent allow rules from any other scope. Rules can be bare tool names (`Edit`) or include content in parens (`Edit(/path/**)`, `Bash(git status:*)`).

### Observed / undocumented behavior

`claude.exe`'s matcher dispatches allow / deny / ask checks through three sibling functions (`v$_`, `xX8`, `JIq`) that all forward to a single predicate `XIq(tool, rule, opts)`. **`XIq`'s first line unconditionally rejects any rule with non-empty ruleContent:**

```js
if (rule.ruleValue.ruleContent !== void 0) return false;
```

Consequence: every `Edit(...)`, `Read(...)`, `Write(...)`, `Glob(...)`, `Skill(...)`, `mcp__server__tool(arg)` rule is silently no-op. Only bare tool names match.

Bash and PowerShell with content **do** work — they have their own per-tool content matcher (`dz8`) inside their tool.checkPermissions, which picomatches the command string directly without going through `XIq`.

Per-tool `checkPermissions` for the affected tools (`Read`, `Edit`, `Write`, `Glob`, `NotebookRead`, `NotebookEdit`) does only a working-directory scope check — no consultation of `ruleContent`.

### Known gaps

- We have not verified the matcher on claude.exe versions other than 2.1.143.a06. The `XIq` reject line may have changed in 2.1.126 (per upstream #55255) or in later versions.
- Behavior of `permissions.ask` with `ruleContent` is presumed broken by the same mechanism but not specifically tested.
- We have not traced the VSCode extension's permission decision path — upstream #59171 (IPC race) and similar suggest that surface has additional logic.

### Cross-references

- [INVESTIGATION.md §Finding #1](../../ISSUE-0001/INVESTIGATION.md#finding-1--the-xiq-matcher-bug)
- [root-causes.md / RC-XIQ-MATCHER](../../FEAT-0001/root-causes.md#rc-xiq-matcher)
- Upstream: #36884, #57132, #15921, #27040, #30519 (meta-tracker).

---

## Hook system

**Doc URL:** [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide)
**Coverage:** Moderate
**Last verified:** 2026-05-18 / docs only + empirical work on PreToolUse (via this repo's `file-deny-guard.py`)

### Documented behavior

Hooks fire at named lifecycle points; each is a stdin-JSON / stdout-JSON program (or HTTP endpoint, or MCP tool, or prompt, or agent type).

**Lifecycle events:**

| Event | When | Common use |
|---|---|---|
| `SessionStart` | Session begins | Setup, log, refresh context |
| `SessionEnd` | Session ends | Cleanup |
| `UserPromptSubmit` | User submits a turn | Pre-process / log prompts |
| `PreToolUse` | Before any tool invocation | **Permission decisions** — gate file edits, Bash commands |
| `PostToolUse` | After tool returns | Audit / log results |
| `PostToolUseFailure` | After tool errors | Error-handling hook |
| `Stop` | Turn ends successfully | Log / verify |
| `StopFailure` | Turn ends with failure | Cleanup |
| `Notification` | Claude shows notification | Custom alerting |
| `SubagentStop` | Subagent returns | Aggregate subagent results |
| `PermissionRequest` | Tool requests permission | Custom permission UX |
| `PreCompact` | Before context compaction | Snapshot transcript |

**Common stdin payload (all events):**

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/dir",
  "permission_mode": "default|plan|auto|dontAsk|acceptEdits|bypassPermissions",
  "hook_event_name": "PreToolUse",
  "effort": { "level": "medium" }
}
```

**PreToolUse stdin** adds `tool_name` and `tool_input` fields.

**PreToolUse stdout** for permission decisions:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask|defer",
    "permissionDecisionReason": "<explanation>"
  }
}
```

**Other events** support a different shape:

```json
{
  "decision": "block|allow",
  "reason": "<explanation>",
  "hookSpecificOutput": {
    "hookEventName": "<EventName>",
    "additionalContext": "<context for Claude>"
  }
}
```

**Exit codes:** `0` = success (stdout JSON processed); `2` = blocking error (stderr → Claude); other = non-blocking (continue).

**Hook types:** `command` (most common — stdin/stdout), `http` (POST), `mcp_tool`, `prompt` (yes/no), `agent` (spawn subagent).

**Matchers:** alphanumeric + `|` = exact string/list; other regex chars = JavaScript regex. MCP tools use `mcp__<server>__.*` patterns.

### Observed / undocumented behavior

- Hook stdin payload is read fresh on each invocation. settings.json hook entries are re-read on each tool call, not cached at session start (verified empirically when we re-pointed the hook path mid-session and it took effect immediately — earlier hypothesis that this required a restart was wrong; the README's "restart" caveat applies to *adding/removing* a hook entry, not to changing the path within an existing entry).
- Hook timeout for `Stop` / `StopFailure` is 30s (research-subagent claim; needs primary-source verification — the docs say 60s for the default and the agent reported 30, so one of those is stale).
- The `defer` value for `permissionDecision` is documented but its precise semantics are sparse (does it fall through to allow / ask / deny depending on other rules? Untested.)
- The Windows shell-parsing quirk on the hook `command` string (strips backslashes) is documented in this repo's README but **not** in the upstream docs. It's a known operational hazard.

### Known gaps

- Exact payload shape for `SessionStart`, `PreCompact`, `PermissionRequest` empirically uncaptured (only PreToolUse is widely deployed in our tooling).
- Behavior on hook `command` failure (non-zero exit AND no JSON on stdout): does the harness fall through to allow, fall through to deny, or surface the error? Tested partially in this repo's session — appeared to block Edit when the script path was missing, but the exact contract isn't pinned.
- Multi-hook ordering (when multiple `PreToolUse` hooks fire): does the harness short-circuit on first deny, or run all and aggregate?

### Cross-references

- This repo's [app-src/py-helpers/file-deny-guard.py](../../../app-src/py-helpers/file-deny-guard.py) — empirical PreToolUse implementation.
- This repo's [CLAUDE.md §The hook contract](../../../CLAUDE.md#the-hook-contract--dont-break-it) — operationally-pinned contract notes.

---

## settings.json schema + cascade

**Doc URL:** [code.claude.com/docs/en/settings.md](https://code.claude.com/docs/en/settings.md) + [json.schemastore.org/claude-code-settings.json](https://json.schemastore.org/claude-code-settings.json)
**Coverage:** Moderate
**Last verified:** 2026-05-18 / docs only

### Documented behavior

Five scopes, highest precedence to lowest:

1. **Managed** — system / MDM policy, unconfigurable by user.
2. **Command-line arguments** — `--permission-mode`, `--allowedTools`, etc.; temp overrides.
3. **Local** — `.claude/settings.local.json` (per-user, per-project; gitignored).
4. **Project** — `.claude/settings.json` (shared in git).
5. **User** — `~/.claude/settings.json` (all projects).

Plus the OAuth / MCP / cache file at `~/.claude.json` (different format, different purpose).

**Merge behavior:** Arrays concatenate across scopes; objects deep-merge.

### Observed / undocumented behavior

- The user's `~/.claude/settings.json` is read fresh on tool calls (see Hook section above — the harness re-reads on each invocation, not just at session start).
- Empirical: a UTF-8 BOM at the start of settings.json is tolerated by Claude Code (and ignored), but breaks `probe.js`'s `JSON.parse`. Source: this session's PowerShell BOM regression incident.
- The harness silently tolerates trailing commas? Not yet tested.
- The `.claude/settings.local.json` file is auto-created by Claude Code on first use for allow-rules added via the `/permissions` UI prompts — observed in this repo today.

### Known gaps

- Not all schema keys are documented at the schema level. Empirically-known undocumented keys include `skillListingBudgetFraction`, `maxSkillDescriptionChars`, `worktree.baseRef`, `worktree.sparsePaths`.
- Precedence of conflicting `permissions.allow` entries across scopes: docs say arrays "concatenate" but if both user-scope and project-scope contain `Edit` (bare) vs `Edit(/path/**)`, which wins on evaluation? (See evaluation order in matcher section.)
- Whether `settings.local.json` is read on the same fresh-per-call schedule, or cached, or only at session start.

### Cross-references

- This repo's `~/.claude/settings.json` example wiring lives in [README §Quick start](../../../README.md#quick-start).

---

## Permission rule syntax

**Doc URL:** [code.claude.com/docs/en/permissions.md](https://code.claude.com/docs/en/permissions.md)
**Coverage:** Moderate
**Last verified:** 2026-05-18

### Documented behavior

**Grammar:**
- `Tool` or `Tool(*)` — applies to all uses of the tool.
- `Tool(specifier)` — applies to specific uses; specifier syntax varies by tool.

**Tool-specific specifier formats:**

| Tool | Specifier syntax | Example | Honored? |
|---|---|---|---|
| `Bash` | command pattern with picomatch globs | `Bash(git status:*)` | **Yes** (via `dz8`) |
| `PowerShell` | command pattern, cmdlet aliases canonicalized | `PowerShell(Get-ChildItem*)` | **Yes** |
| `Read` / `Edit` / `Write` | gitignore-style path patterns | `Edit(/path/**)` | **NO** (XIq reject) |
| `Glob` / `NotebookRead` / `NotebookEdit` | path patterns | `Glob(**/*.py)` | **NO** (XIq reject) |
| `WebFetch` | domain | `WebFetch(domain:example.com)` | Unverified |
| `mcp__servername` | bare server name or `__tool` suffix | `mcp__server__tool` | Bare: yes. With parens: **NO** |
| `Agent` | agent name | `Agent(general-purpose)` | Unverified |
| `Skill` | skill name | `Skill(my-skill)` | Bare unverified; with parens: **NO** (XIq reject) |

Evaluation order: deny → ask → allow.

### Observed / undocumented behavior

The asymmetry above is the heart of [RC-XIQ-MATCHER](../../FEAT-0001/root-causes.md#rc-xiq-matcher). Tools whose own `checkPermissions` includes a content matcher (Bash, PowerShell) work with parens-content rules. Tools that fall through to `XIq` don't.

Path patterns in `Read` / `Edit` / `Write` documented to support `/path` = project-relative, `//path` = absolute, `~/path` = home, `./path` = cwd-relative, `**` = recursive. **None of these forms work** in practice for the affected tools.

### Known gaps

- `WebFetch(domain:X)` and `Agent(X)` rule honor not tested.
- Whether `permissions.ask` with parens-content is similarly broken (presumed yes from the shared `XIq` path).

---

## Permission modes

**Doc URL:** [code.claude.com/docs/en/permission-modes.md](https://code.claude.com/docs/en/permission-modes.md)
**Coverage:** Moderate
**Last verified:** 2026-05-18 / docs only

### Documented behavior

| Mode | Prompts for | Best for | Availability |
|---|---|---|---|
| `default` | All edits, all Bash | Starting, sensitive | Always |
| `acceptEdits` | Bash only (not common FS commands) | Code iteration | Always |
| `plan` | Same as default + plan-mode UX | Pre-edit analysis | Always |
| `auto` | Classifier-filtered actions | Long tasks | Max/Team/Enterprise + model qualifications |
| `dontAsk` | Non-interactive CI | Locked-down scripts | Always |
| `bypassPermissions` | Nothing (circuit breakers: `rm -rf /`, `rm -rf ~`) | Containers / VMs only | Opt-in via launch-time flag |

**Set via:** `--permission-mode <mode>` CLI flag, `Shift+Tab` to cycle, `permissions.defaultMode` in settings.json. Disable specific modes via managed `permissions.disableBypassPermissionsMode: "disable"` or `disableAutoMode: "disable"`.

**Auto mode requires:** Sonnet 4.6+, Max/Team/Enterprise plan, Anthropic API only (not Bedrock/Vertex/Foundry), admin opt-in on Team/Enterprise.

### Observed / undocumented behavior

- `bypassPermissions` mode set via `defaultMode` in settings.json is silently rejected at startup unless the session was launched with `--dangerously-skip-permissions` or `--permission-mode bypassPermissions`. See bypassPermissions gate section below.
- Mode transitions via hook return value: upstream #37420 reports hook returning `permissionDecision:"ask"` resets bypassPermissions mode mid-session — a related mode-state bug, not yet root-caused.
- Mode-state persistence across `Plan Approved` UI: upstream #59843 reports the button drops sessions into `default` mode regardless of prior mode.

### Known gaps

- Auto mode classifier rules — what counts as "automatically allowed" vs requiring prompt — not documented.
- Whether `dontAsk` differs from `bypassPermissions` for hooks that would otherwise prompt for confirmation.

### Cross-references

- [bypassPermissions gate section](#dangerously-skip-permissions--isbypasspermissionsmodeavailable-gate) below.
- [root-causes.md / RC-BYPASS-GATE](../../FEAT-0001/root-causes.md#rc-bypass-gate).

---

## additionalDirectories + cwd scope

**Doc URL:** [code.claude.com/docs/en/permissions.md#working-directories](https://code.claude.com/docs/en/permissions.md#working-directories)
**Coverage:** Shallow
**Last verified:** 2026-05-18 / docs only

### Documented behavior

Each entry in `permissions.additionalDirectories` (array of absolute paths) extends the read/edit scope as if cwd were that directory too. CLI flag `--add-dir <path>` is the per-session equivalent.

**Does NOT** load `.claude/` configuration from added dirs. Exceptions:
- Skills in `.claude/skills/` (live-reloaded).
- Plugin settings `enabledPlugins`, `extraKnownMarketplaces`.
- CLAUDE.md / `.claude/rules/` / CLAUDE.local.md only if `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` env var set.

**Cwd semantics:** by default, Claude can read anywhere, edit within cwd + additionalDirectories. Permission rules (and sandbox if enabled) further restrict.

### Observed / undocumented behavior

- Upstream #51286: glob-form `additionalDirectories` doesn't propagate to concurrent subagent dispatch (sequential is fine). Not yet root-caused.
- Empirically observed in this repo's settings.json: `additionalDirectories: ["C:/Data"]` is recognized as a prefix grant in the probe's output, confirming the documented prefix-match behavior.

### Known gaps

- Subagent propagation (#51286).
- Whether ACL denies override the addl-dir grant (likely yes — OS wins — but undocumented).
- Whether the `**` glob in addl-dir entries is supported or treated as a literal path (not yet tested).

---

## MCP server install/trust model

**Doc URL:** [code.claude.com/docs/en/mcp.md](https://code.claude.com/docs/en/mcp.md)
**Coverage:** Shallow
**Last verified:** 2026-05-18 / docs only

### Documented behavior

**Install:**
- HTTP: `claude mcp add --transport http <name> <url> [--header "Auth: ..."]`
- SSE (deprecated): `claude mcp add --transport sse <name> <url>`
- Stdio: `claude mcp add --transport stdio [--env KEY=VAL] <name> -- <command> [args]`

**Scopes:** `local` (default, project-only), `project` (shared, `.mcp.json`), `user` (all projects, `~/.claude.json`).

**Trust model:**
- User runs `claude mcp add` explicitly; no auto-discovery.
- HTTP/SSE servers: trust is at URL validation. No per-tool sandbox beyond `mcp__server__tool` permission rules.
- Stdio servers: launched as subprocess with `CLAUDE_PROJECT_DIR` in environment. No sandboxing; runs with the user's permissions.
- Plugin-bundled MCP: auto-starts when plugin enabled.

### Observed / undocumented behavior

- (None recorded yet — this is a shallow topic.)

### Known gaps

- No signing/verification mechanism documented. HTTP servers trusted by URL only.
- What happens when an MCP server returns malformed tool definitions? Not tested.
- Whether MCP-tool permission rules with content (`mcp__server__tool(arg)`) suffer the same XIq reject — yes by inference, but no specific probe yet.
- Threat model for malicious MCP servers — feed into [FEAT-0003 PLAN](../../FEAT-0003/PLAN.md).

---

## Skill permissions

**Doc URL:** [code.claude.com/docs/en/skills.md](https://code.claude.com/docs/en/skills.md)
**Coverage:** Shallow
**Last verified:** 2026-05-18 / docs only

### Documented behavior

**Rule syntax:** `Skill(name)` or `Skill(name *)`. (Parens-content form will be subject to `XIq` reject — see matcher section.)

**Loading:**
- Descriptions always loaded; full content loads on invocation (lazy).
- Discovery from `.claude/skills/`, `~/.claude/skills/`, parent directories (monorepo-aware).
- Live reload within session if `.claude/skills/` modified.
- Can preload into subagents.

**Skill-scoped tool grants** via `allowed-tools` frontmatter field. Pre-approves listed tools during skill execution without per-use prompt. Does not *restrict*; permission rules still govern.

**Invocation control:**
- `disable-model-invocation: true` — only user-invokable.
- `user-invocable: false` — only Claude-invokable (background knowledge).

### Known gaps

- `Skill(name *)` rule honor not empirically tested; XIq is suspected to reject the parens-content form.
- Whether `allowed-tools` frontmatter can grant a tool that's been deny'd in settings.json (presumed not).
- Skill discovery precedence when same-named skill exists in multiple discovery locations.

---

## `--dangerously-skip-permissions` + `isBypassPermissionsModeAvailable` gate

**Doc URL:** [code.claude.com/docs/en/permission-modes.md#skip-all-checks-with-bypasspermissions-mode](https://code.claude.com/docs/en/permission-modes.md#skip-all-checks-with-bypasspermissions-mode)
**Coverage:** Deep
**Last verified:** 2026-05-18 / claude.exe 2.1.143.a06

### Documented behavior

`--dangerously-skip-permissions` is equivalent to `--permission-mode bypassPermissions`. Disables all permission prompts and hooks. Circuit breakers: `rm -rf /`, `rm -rf ~` still prompt (crash prevention).

**Where available:**
- Always on the CLI when launched with the flag.
- In VS Code / Desktop after enabling "Allow dangerously skip permissions" setting.
- **NOT** in web/mobile sessions or Remote Control.
- Blocked when running as root/sudo; auto-skipped if in a recognized sandbox.

**Disable via managed settings:** `permissions.disableBypassPermissionsMode: "disable"`.

### Observed / undocumented behavior

The default permission context factory `h0()` initializes:

```js
isBypassPermissionsModeAvailable: !1
```

The flag only flips `true` at session launch with the flag. When `defaultMode: "bypassPermissions"` is in settings.json:

1. Claude reads the setting, calls `setMode("bypassPermissions")`.
2. setMode gate checks `isBypassPermissionsModeAvailable === false`, rejects.
3. Rejection logs at debug level only: `"Ignoring permission update: setMode 'bypassPermissions' rejected — mode is not available..."` (offset ~111875000 in claude.exe).
4. Session silently stays in `default`. **No UI warning.**

Same gate pattern: `dontAsk` mode, the policy flags `disableBypassPermissionsMode`, `disableAutoMode`.

Upstream #49525 reports the same gate rejects hook return value `setMode:"bypassPermissions"` in v2.1.110+ — the hook code path goes through the same setMode gate.

### Known gaps

- Has the `h0()` factory or the setMode gate changed in versions after 2.1.143.a06? Not verified.
- The exact logic computing `isBypassPermissionsModeAvailable` at session start is not in the public surface — likely: plan tier check + platform check + no-root check.

### Cross-references

- [INVESTIGATION.md §Finding #2](../../ISSUE-0001/INVESTIGATION.md#finding-2--the-bypasspermissions-mode-gate).
- [root-causes.md / RC-BYPASS-GATE](../../FEAT-0001/root-causes.md#rc-bypass-gate).

---

## Bash and PowerShell content matchers

**Doc URL:** [code.claude.com/docs/en/permissions.md#bash](https://code.claude.com/docs/en/permissions.md#bash), [...#powershell](https://code.claude.com/docs/en/permissions.md#powershell)
**Coverage:** Moderate
**Last verified:** 2026-05-18 / docs only + ISSUE-0001 confirmation that Bash content rules work

### Documented behavior

**Bash:**
- Pattern uses picomatch-style globs with word-boundary-aware `*` (if preceded by space).
- `Bash(ls *)` matches `ls -la` but not `lsof`; `Bash(ls*)` matches both.
- `:*` suffix = "trailing space + *" — matches any trailing args.
- Process wrappers recognized: `timeout`, `time`, `nice`, `nohup`, `stdbuf`, bare `xargs`.
- Built-in read-only commands always allowed: `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, read-only `git` subcommands.
- Compound-command splitting: `&&`, `||`, `;`, `|`, `|&`, `&`, newlines. Each subcommand must match independently.

**PowerShell:**
- Same glob semantics.
- Cmdlet names canonicalized through aliases.
- Case-insensitive.
- Compound parsing via AST.

### Observed / undocumented behavior

- Bash with content rules **do** work — the `dz8` per-tool matcher inside Bash's `checkPermissions` picomatches the command directly without going through `XIq` (which is what defeats Edit/Read/Write rules).
- Upstream #59498 reports the harness strips idempotent `cd /path && ` prefix from compound commands before matching — so `cd /path && git push` matches `Bash(git push:*)`, BUT also matches `Bash(git status:*)` if `git status` is in the allow list, even though the user typed `git push`. Effectively a bypass via cd-prefix. **Novel bug not yet root-caused** — candidate for `RC-CD-PREFIX-BYPASS`.

### Known gaps

- Exact picomatch version / configuration in use is not disclosed.
- The built-in read-only command list isn't user-configurable.
- Network and filesystem state changes triggered by built-ins (`cd` changes cwd, `ls` is fine, `cat /etc/passwd` is reading sensitive content but is in the built-in list…) — the security implications of the always-allowed list aren't documented.

### Cross-references

- Upstream #59498 (cd-prefix bypass) → registry seed → proposed `ISSUE-0002`.
- Upstream #18160 (Bash matcher `ls *` allow not matching) — closed-but-relevant in registry.

---

## Filesystem ACL interaction

**Doc URL:** *No documentation found.*
**Coverage:** None (explicit gap)
**Last verified:** n/a

### Documented behavior

(None.)

### Observed / undocumented behavior

Claude Code's tools call OS file APIs that respect filesystem ACLs. An ACL-denied read returns an OS-level error to the tool, which surfaces as a tool error to the model — but how the permission system interacts with this is not documented.

### Known gaps

- Does a deny rule + an OS-allowed ACL combine to: prompt the user? Block via permission system? Block via OS?
- Does an allow rule + an OS-denied ACL silently block, or surface the error to the user?
- Are there platform differences (Windows ACLs vs POSIX permissions vs macOS-specific extended attributes)?
- Does the sandbox layer (on Linux/macOS, when enabled) modify the OS-level access check?

### Investigation needed

This is a top-3 priority gap (see [PLAN §7 Learning roadmap](../PLAN.md#7-learning-roadmap--current-gap-assessment)). Suggested approach:

1. Create a file with restrictive ACL (`chmod 000` on Linux/macOS or `icacls /deny` on Windows).
2. Attempt to read it via Claude's Read tool with the path in permissions.allow.
3. Observe behavior — error code, UI prompt, silent fail, etc.

---

## Sandbox mode

**Doc URL:** [code.claude.com/docs/en/sandboxing.md](https://code.claude.com/docs/en/sandboxing.md)
**Coverage:** Moderate
**Last verified:** 2026-05-18 / docs only

### Documented behavior

**Scope:** Bash subprocesses only. Read/Edit/Write tools use the permission system, NOT the sandbox.

**Enforcement mechanisms:**
- macOS: Seatbelt (`sandbox-exec`).
- Linux / WSL2: bubblewrap + socat (for limited network).
- WSL1: not supported.

**Modes:**
- **Auto-allow:** sandboxed commands execute without prompts; explicit deny rules still respected; circuit-breaker prompts (`rm -rf /`, `~`) still fire.
- **Regular permissions:** sandboxed commands still go through normal permission flow.

**Config (settings.json):**
- `sandbox.enabled`, `sandbox.failIfUnavailable`.
- `sandbox.filesystem.allowWrite`, `denyWrite`, `denyRead`, `allowRead` (arrays merge across scopes).
- `sandbox.network.allowedDomains`, `deniedDomains`.
- `sandbox.excludedCommands` (run outside the sandbox).
- `autoAllowBashIfSandboxed` (default `true`).

**Escape hatch:** `dangerouslyDisableSandbox` parameter on individual tool calls; disable via `allowUnsandboxedCommands: false`.

### Observed / undocumented behavior

- (None recorded — we've only used Windows; sandbox doesn't apply.)

### Known gaps

- Network filtering is hostname-based, not TLS-SNI-inspected. Domain fronting is possible if broad domains are allowed (e.g., `*.amazonaws.com` covers many services). Documented as a known limitation in the sandboxing page but worth flagging in threat modeling.
- Unix-socket allowlist (`allowUnixSockets`) can grant access to system services running on the host (e.g., the X server, the docker socket) — privilege escalation surface.
- Behavior on macOS pre-Catalina (Seatbelt deprecation) not documented.
- Behavior with rootless containers (Podman) vs Docker not documented.

### Investigation needed

A FEAT-0003 sandbox-escape probe could exercise these gaps if the threat-model section calls for it.

---

## Sources used in this reference (canonical URLs)

Listed in [README.md § Sources catalog](README.md#sources-catalog).

<!-- version: v2026.05.18.01 -->
