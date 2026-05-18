# Knowledge Base — Claude Code Permissions + Security

A version-pinned, citation-backed knowledge base. The single source of truth for "what does Claude Code actually do" in our area of focus.

**Format:** all topics live in [REFERENCE.md](REFERENCE.md) as a single dense document. When a topic exceeds ~500 lines, it gets split into its own file (see [../PLAN.md §2](../PLAN.md#2-kb-structure--storage--pick)).

**Maintenance:** updates happen on a change-detect trigger (see [../change-tracking.md](../change-tracking.md)) or after a probe-suite run reveals new behavior.

---

## Topic index

| # | Topic | Coverage | Last verified | REFERENCE.md anchor |
|---|---|---|---|---|
| 1 | Permission matcher (`XIq`, `v$_`, `xX8`, `JIq`) | **Deep** | 2026-05-18 / claude.exe 2.1.143.a06 | [#permission-matcher](REFERENCE.md#permission-matcher) |
| 2 | Hook system lifecycle events | **Moderate** | 2026-05-18 / docs only | [#hook-system](REFERENCE.md#hook-system) |
| 3 | settings.json schema + cascade | **Moderate** | 2026-05-18 / docs only | [#settings-json](REFERENCE.md#settings-json-schema--cascade) |
| 4 | Permission rule syntax | **Moderate** | 2026-05-18 | [#rule-syntax](REFERENCE.md#permission-rule-syntax) |
| 5 | Permission modes | **Moderate** | 2026-05-18 / docs only | [#modes](REFERENCE.md#permission-modes) |
| 6 | additionalDirectories + cwd scope | **Shallow** | 2026-05-18 / docs only | [#addl-dirs](REFERENCE.md#additionaldirectories--cwd-scope) |
| 7 | MCP server install/trust | **Shallow** | 2026-05-18 / docs only | [#mcp](REFERENCE.md#mcp-server-installtrust-model) |
| 8 | Skill permissions | **Shallow** | 2026-05-18 / docs only | [#skill](REFERENCE.md#skill-permissions) |
| 9 | bypassPermissions gate | **Deep** | 2026-05-18 / claude.exe 2.1.143.a06 | [#bypass-gate](REFERENCE.md#dangerously-skip-permissions--isbypasspermissionsmodeavailable-gate) |
| 10 | Bash/PowerShell content matchers | **Moderate** | 2026-05-18 / docs only | [#bash-matcher](REFERENCE.md#bash-and-powershell-content-matchers) |
| 11 | Filesystem ACL interaction | **None** (undocumented upstream) | n/a | [#fs-acl](REFERENCE.md#filesystem-acl-interaction) |
| 12 | Sandbox mode (Seatbelt / bubblewrap) | **Moderate** | 2026-05-18 / docs only | [#sandbox](REFERENCE.md#sandbox-mode) |

Coverage legend:
- **Deep** = we've root-caused / disassembled / empirically verified.
- **Moderate** = docs read carefully + cross-referenced; not all behavior empirically tested.
- **Shallow** = primary doc URLs known, basic summary; many edge cases untested.
- **None** = no documentation; behavior unknown.

## Sources catalog

### Primary (Anthropic-controlled)

| URL | Topic |
|---|---|
| [code.claude.com/docs/en/settings.md](https://code.claude.com/docs/en/settings.md) | settings.json schema + cascade |
| [code.claude.com/docs/en/permissions.md](https://code.claude.com/docs/en/permissions.md) | rule syntax + per-tool matchers |
| [code.claude.com/docs/en/permission-modes.md](https://code.claude.com/docs/en/permission-modes.md) | modes (default / acceptEdits / plan / auto / dontAsk / bypassPermissions) |
| [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide) | hook lifecycle events + stdin/stdout payloads |
| [code.claude.com/docs/en/mcp.md](https://code.claude.com/docs/en/mcp.md) | MCP install + trust model |
| [code.claude.com/docs/en/skills.md](https://code.claude.com/docs/en/skills.md) | Skill permission rule + frontmatter |
| [code.claude.com/docs/en/sandboxing.md](https://code.claude.com/docs/en/sandboxing.md) | sandbox (Seatbelt + bubblewrap, Bash-only) |
| [json.schemastore.org/claude-code-settings.json](https://json.schemastore.org/claude-code-settings.json) | settings JSON Schema (community-mirrored) |

### Primary (this repo's disassembly)

| Path | Topic |
|---|---|
| [../../ISSUE-0001/INVESTIGATION.md](../../ISSUE-0001/INVESTIGATION.md) | `XIq` matcher + `bypassPermissions` gate disassembly |
| [../../../app-src/js-probes/probe.js](../../../app-src/js-probes/probe.js) | picomatch verification probe |

### Secondary (community)

| Path | Topic |
|---|---|
| [../../FEAT-0001/registry.md](../../FEAT-0001/registry.md) | 15-issue upstream symptom registry with RC mapping |
| [../../FEAT-0001/root-causes.md](../../FEAT-0001/root-causes.md) | RC-XIQ-MATCHER, RC-BYPASS-GATE, RC-EDIT-PROMPT-2126 |

## How to update

1. Identify what changed (new claude.exe version? doc revision? new bug? new investigation?).
2. Update the relevant section in [REFERENCE.md](REFERENCE.md). Update "Last verified" date + version at the top of the section.
3. If your update reveals a topic now exceeds ~500 lines, split it out: move the section to `kb/<topic-slug>.md`, leave a "see also" pointer at the original location in REFERENCE.md, update this index.
4. If a change affects a known root cause, cross-update [../../FEAT-0001/root-causes.md](../../FEAT-0001/root-causes.md) too.
5. Commit with `KB:` prefix and the topic(s) touched in the subject line. E.g., `KB: refresh permission-matcher + add 2.1.150 verification`.

<!-- version: v2026.05.18.01 -->
