# FEAT-0002 PLAN — Deep expertise in Claude permissions + security (KB + change-tracking + verification suite)

**Authored:** 2026-05-18 (autonomous planning pass).
**Status:** Plan draft. Initial KB seeded (see [kb/](kb/)); change-tracking + verification suite scoped here for follow-up implementation.

Addresses the 12 acceptance criteria from [../../open/FEAT-0002.md](../../open/FEAT-0002.md).

---

## 1. Topic scope

**In scope** (the 11 topics now seeded in [kb/REFERENCE.md](kb/REFERENCE.md)):

1. Permission matcher internals (`XIq` predicate, `v$_` / `xX8` / `JIq` dispatchers, per-tool `checkPermissions`).
2. Hook system lifecycle (PreToolUse, PostToolUse, Notification, SubagentStop, SessionStart/End, UserPromptSubmit, Stop, StopFailure, PreCompact, PermissionRequest).
3. `settings.json` schema and cascade (managed → cli → local → project → user).
4. Permission rule syntax (allow/deny/ask grammar, `ruleContent` semantics, per-tool variants).
5. Permission modes (default / acceptEdits / plan / auto / dontAsk / bypassPermissions).
6. `additionalDirectories` + cwd scope check.
7. MCP server install/trust model.
8. Skill permissions and matching.
9. `--dangerously-skip-permissions` + `isBypassPermissionsModeAvailable` gate.
10. Bash and PowerShell content matchers (`dz8`).
11. Filesystem ACL interaction (explicitly **undocumented** — flagged in KB as a gap).
12. Sandbox mode (Seatbelt / bubblewrap; Bash-only).

**Out of scope:**
- Model behavior / prompt-injection of the model.
- IDE-extension UI/UX issues unrelated to permission decisions.
- Account/billing/licensing.
- Anthropic-hosted API security (different threat model; routed to FEAT-0003's disclosure channel research).

## 2. KB structure + storage — pick

**Decision: Start with a single dense `kb/REFERENCE.md` plus a `kb/README.md` index. Split into per-topic files only when any single topic section exceeds ~500 lines.**

Rationale:
- Topic-per-file at this scale (11 topics, mostly small) produces 11 files most of which contain a one-paragraph stub — friction without benefit.
- A single REFERENCE.md is grep-friendly, easy to scan, single-source-of-truth.
- Migration from one file to many is cheap (cut sections into siblings).
- Git diffs over REFERENCE.md are perfect for "what did our understanding of topic X change this week."

**Per-topic page template** (each section in REFERENCE.md):

```markdown
## <Topic name>

**Doc URL:** <canonical official doc URL>
**Coverage:** deep / moderate / shallow / none
**Last verified:** <YYYY-MM-DD> against claude.exe <version>

### Documented behavior
<2-4 sentences citing docs>

### Observed / undocumented behavior
<what we've verified empirically + the version>

### Known gaps
<what we don't know>

### Cross-references
<links to INVESTIGATION.md sections, registry.md issues, root-causes.md entries>
```

**Storage location:** `tasks/working_artifacts/FEAT-0002/kb/` per the artifacts convention. Sibling location to FEAT-0001's registry — a natural place to cross-reference.

**Rejected:**
- Per-topic files now: premature splitting (see above).
- External (Notion / Obsidian): not portable; the next AI session can't read it.
- Cross-session memory only: memory is for *this user's facts*; the KB is *Claude Code facts that should be citation-backed and version-pinned*. Different shape.
- Separate repo: this repo already exists as the natural home for the work.

## 3. Authoritative sources catalog — see [kb/REFERENCE.md](kb/REFERENCE.md)

The "Sources" section at the end of REFERENCE.md lists canonical URLs per topic. Primary (Anthropic-controlled) sources are distinguished from secondary (community / third-party).

Primary catalog (from FEAT-0002 research subagent):
- [code.claude.com/docs/en/settings.md](https://code.claude.com/docs/en/settings.md) — settings schema + cascade.
- [code.claude.com/docs/en/permissions.md](https://code.claude.com/docs/en/permissions.md) — rule syntax + tool-specific matchers.
- [code.claude.com/docs/en/permission-modes.md](https://code.claude.com/docs/en/permission-modes.md) — modes.
- [code.claude.com/docs/en/hooks-guide](https://code.claude.com/docs/en/hooks-guide) — hook lifecycle + payloads.
- [code.claude.com/docs/en/mcp.md](https://code.claude.com/docs/en/mcp.md) — MCP install + trust.
- [code.claude.com/docs/en/skills.md](https://code.claude.com/docs/en/skills.md) — Skill permission rule + frontmatter.
- [code.claude.com/docs/en/sandboxing.md](https://code.claude.com/docs/en/sandboxing.md) — sandbox.
- [json.schemastore.org/claude-code-settings.json](https://json.schemastore.org/claude-code-settings.json) — settings JSON Schema.

Primary disassembly sources (this repo):
- [tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md](../ISSUE-0001/INVESTIGATION.md) — `XIq` + `bypassPermissions` gate disassembly.
- [app-src/js-probes/probe.js](../../../app-src/js-probes/probe.js) — picomatch verification probe.

Secondary (community):
- The 15-issue seed registry in [../FEAT-0001/registry.md](../FEAT-0001/registry.md) — symptom reports + community workarounds.

## 4. Change-tracking workflow — pick

**Decision: Three-signal change detect, primary + fallbacks.** Captured fully in [change-tracking.md](change-tracking.md). Headline:

| Signal | Trigger | Frequency | Implementation |
|---|---|---|---|
| **Primary: claude.exe binary version diff** | New release detected in installed CLI (or via `gh release list anthropics/claude-code`) | Per release | Run probe-suite + symbol-search for `XIq`, `h0`, `sI8` regions |
| **Secondary: GitHub releases watcher** | New tag at anthropics/claude-code | Weekly | `gh release list` + parse release notes for permission/hook/settings keywords |
| **Tertiary: docs schema diff** | Periodic | Monthly | `curl` the doc URLs from §3 + diff against a baseline snapshot stored at `kb/baselines/<YYYY-MM>-docs/` |

Re-investigation trigger: any of the above flagging a permission-relevant change. Probe-suite run is mandatory; INVESTIGATION.md update is recommended.

**Rejected:**
- Polling claude.exe bytes more often than per-release: wasteful.
- Atom feeds: GitHub returns 406 (per FEAT-0001 research).
- Webhook-based push: more infra than needed.

## 5. Verification + regression suite — pick

**Decision: Extend `app-src/js-probes/probe.js` into a versioned probe-suite under `app-src/js-probes/suite/`.** Spec in [verification-suite.md](verification-suite.md).

Each probe is a small Node script that:
1. Records claude.exe version (via `claude --version`) at the top of its output.
2. Exercises one specific permission-system behavior.
3. Produces a deterministic pass/fail/inconclusive verdict against an expected outcome encoded in the probe.

Initial suite (priority order, from highest-payoff to lowest):

1. **`probe-xiq-matcher.js`** — verifies `Edit(/path/**)` allow rule fails to match (RC-XIQ-MATCHER persists).
2. **`probe-bypass-gate.js`** — verifies `defaultMode:"bypassPermissions"` in settings.json is silently rejected (RC-BYPASS-GATE persists).
3. **`probe-bare-edit.js`** — disambiguates RC-EDIT-PROMPT-2126 (does bare `Edit` allow still work?).
4. **`probe-cd-prefix-bypass.js`** — exercises upstream #59498 (cd-prefixed Bash commands bypassing matcher).
5. **`probe-picomatch.js`** — the existing probe.js, generalized as one of the suite members.
6. **`probe-hook-stdin-payload.js`** — verifies hook payload shape matches documented schema for each event type.

When the suite shifts from all-known-bugs-still-present to one-or-more-now-pass, that's the signal to update INVESTIGATION.md, deprecate workarounds, and post fix-confirmation comments via FEAT-0001's Template D.

**Rejected:**
- A single mega-script: too tightly coupled; can't run individual probes against historical claude.exe binaries easily.
- Test-framework wrapper (jest/mocha): overkill for ~10 probes that are mostly shell-orchestration around `claude --print --debug`.

## 6. Cadence + automation surface — pick

Shares with FEAT-0001:

- Stage 1 (now): manual, on-demand. Run the change-detect script + probe suite when a new claude.exe ships or "feels stale."
- Stage 2 (later): `/schedule` weekly cron that runs the probe suite and posts a summary to a `kb/probe-runs/<YYYY-MM-DD>.md`.

Cross-reference [FEAT-0001 PLAN §3](../FEAT-0001/PLAN.md#3-cadence--automation-surface--pick) — same primitives, same maturity gate.

## 7. Learning roadmap — current gap assessment

| Topic | Current depth | Next 1-3 actions to lift |
|---|---|---|
| Permission matcher (XIq) | **Deep** | Re-verify on current claude.exe; check for ruleContent-path-aware code added since 2.1.143. |
| Hook system | **Moderate** | Trace full payload shape for SessionStart, PreCompact, PermissionRequest (less explored than PreToolUse). Run hooks with `--debug "hook"` and capture stdin. |
| `settings.json` cascade | **Moderate** | Verify merge behavior with conflicting `permissions.allow` arrays across scopes (do they concat or replace?). Test edge cases: malformed JSON, BOM, large arrays. |
| Permission rule syntax | **Moderate** | Map each documented rule variant to whether `XIq` rejects it. Build the truth table empirically (the "What's actually working" table in INVESTIGATION.md is a starting point). |
| Permission modes | **Moderate** | Test mode transitions via hook return value (per upstream #37420). |
| `additionalDirectories` | **Shallow** | Verify subagent propagation (upstream #51286 reports it doesn't propagate). Understand whether it's a "trust to read" or "trust to edit" grant or both. |
| MCP trust model | **Shallow** | Document the threat model for malicious MCP servers (FEAT-0003 input). |
| Skill permissions | **Shallow** | Test `Skill(<name>)` allow/deny with `disable-model-invocation` and `user-invocable:false` skills. |
| bypassPermissions gate | **Deep** | Already root-caused. Verify if 2.1.126+ changed the gate (RC-EDIT-PROMPT-2126 is adjacent — same neighborhood). |
| Bash/PowerShell matchers | **Moderate** | Exercise the cd-prefix bypass (#59498). Understand compound-command splitting precisely. |
| Filesystem ACL interaction | **None** (undocumented upstream) | Test what Claude does when OS ACL denies access vs when permission rule denies. Document the difference. |
| Sandbox mode | **Shallow** | Test the documented behavior (Seatbelt/bubblewrap) on Linux + macOS; we've only used Windows. |

Top 3 priorities for the next investigation pass:
1. **RC-EDIT-PROMPT-2126 disambiguation** — most actionable since it might mean our workaround docs are wrong.
2. **Hook payload schema empirical capture** — feeds FEAT-0003 threat modeling (hooks are the local trust boundary).
3. **MCP trust model** — also feeds FEAT-0003 + has the largest gap-to-importance ratio.

## 8. Memory integration — pick

**Decision: Memory entries cover (a) the maintainer's own setup specifics and (b) procedural lessons. KB covers Claude-Code facts that are version-pinned and citation-backed.**

Examples:
- **Memory:** "the maintainer's settings.json has a live PreToolUse hook running `app-src/py-helpers/file-deny-guard.py`; never rename without re-pointing settings.json first" — already saved as `project_live_hook_dependency.md` last session.
- **Memory:** "PowerShell 5.1's `Set-Content -Encoding utf8` adds a BOM that Node JSON.parse rejects" — already saved as `feedback_powershell_utf8_bom.md`.
- **KB:** "the `XIq` predicate's first line `if (rule.ruleValue.ruleContent !== void 0) return false` was present in claude.exe 2.1.143.a06 at offset ~X" — facts about Claude Code, version-pinned.

Cross-link convention: KB pages link to memory entries by `[[memory-slug]]` when relevant; memory entries link to KB sections via repo-relative path (`tasks/working_artifacts/FEAT-0002/kb/REFERENCE.md#<section>`).

## 9. Outward-facing artifacts — pick

**Decision: README enhancements are encouraged. Blog posts / external writeups are opportunistic — yes when a natural opportunity appears, with hard constraints. Upstream doc PRs are encouraged if narrowly scoped and obviously correct.**

Specific policy:
- **README updates** as understanding deepens: add a "Status" subsection when an RC is confirmed fixed, add a deprecation banner when the workaround becomes obsolete, link new RC entries.
- **Upstream contributions:** if our research reveals a clearly missing piece in the docs (e.g., filesystem ACL behavior — currently undocumented), open a PR against `anthropics/claude-code` docs proposing the addition. Bias toward small, single-topic PRs that maintainers can accept quickly.
- **Blog / external writeups (resolved 2026-05-18 — "yes, opportunistic"):** take the opportunity when a natural one appears (Show HN moment after a meaningful release, security-blog invitation, conference CFP, podcast). Per-piece quality bar: must add value beyond what's already in the repo's INVESTIGATION.md, must be honest and citation-backed, must include the conflict-of-interest disclosure (the Anthropic carve-out in NOTICE.md). **Hard constraint from [FEAT-0003 ethical-guardrails G2](../FEAT-0003/ethical-guardrails.md#g2-no-public-leak-path):** any external writeup that touches a finding before Anthropic's coordinated disclosure window completes is forbidden. The "opportunistic yes" applies only to *post-disclosure* writeups or to work already public in this repo.
- **Disclosure stance on any comment / PR / blog post:** "Maintainer of [permission-probe](https://github.com/twbarnes1972/permission-probe); GPL-3.0 with a standing license grant to Anthropic for Claude Code inclusion." Standard footer, same as FEAT-0001 §10 and FEAT-0003 §12.

## 10. Tooling inventory

| Tool | Use case |
|---|---|
| `claude-api` skill | Building any Anthropic-SDK code (e.g., a comment-drafter that uses Claude with prompt caching). |
| `claude-code-guide` subagent | Quick "is X documented?" lookups during KB maintenance. Used for the FEAT-0002 research pass. |
| `WebFetch` / `WebSearch` tools | Pulling release notes, doc-page diffs, secondary writeups. |
| `gh` CLI | Issue tracker access (shared with FEAT-0001). |
| `app-src/js-probes/probe.js` | Existing probe; basis for the suite extension. |
| `app-src/py-helpers/file-deny-guard.py` | Reference hook implementation; documents the hook contract empirically. |
| Disassembly tooling: `grep -aob` + `dd` + `tr` | Already documented in INVESTIGATION.md §Methodology. The probe suite codifies the most useful invocations. |

## 11. Reuse vs build

| Need | Reuse | Build |
|---|---|---|
| KB storage | Markdown + git | None |
| Doc fetch | `WebFetch` | None |
| Release-list fetch | `gh release list` | None |
| Probe suite runner | Node + `claude --print --debug` | ~5-10 small probe scripts (one per known/suspected RC) + a thin orchestrator |
| Baseline doc snapshots | `curl` + `diff` | A `kb/baselines/` snapshot script |
| Symbol-search in claude.exe | `grep -aob` | None (already validated) |
| Cross-session memory | Existing memory system | Targeted entries per new RC discovery |

Net new code: probably ~200 lines of shell + Node probe scripts. Everything else is markdown + git + existing tooling.

## 12. Honest uncertainties (escalated where applicable)

- **Will Anthropic ship a matcher fix soon?** Unknown. If yes (months), the KB rapidly becomes historical record. If no, ongoing maintenance is valuable. Either way the work is worth doing — even the historical-record outcome documents the workaround era.
- **Is RC-EDIT-PROMPT-2126 real or reporter error?** Unknown until we run probe-bare-edit against the current claude.exe. **High priority.**
- **Should the probe suite be public?** Yes by default — same posture as probe.js today. Hides nothing from Anthropic, helps community verification. But if any individual probe demonstrates an unfixed security-sensitive bug, that probe belongs in FEAT-0003's pre-disclosure private storage instead.
- **External blog / writeup policy** — escalated.

---

## What's done in this autonomous pass

- ✅ Topic scope defined (12 items).
- ✅ KB structure picked + initial REFERENCE.md seeded with all 11 topics (depth varies — see [kb/README.md](kb/README.md) for status per topic).
- ✅ Authoritative sources catalog committed inline in REFERENCE.md.
- ✅ Change-tracking workflow specified in [change-tracking.md](change-tracking.md).
- ✅ Verification suite design in [verification-suite.md](verification-suite.md).
- ✅ Learning roadmap with concrete gap assessment + top-3 priorities.
- ✅ Memory ↔ KB split rule.
- ✅ Tooling inventory + reuse/build call.
- ✅ Uncertainties surfaced.

## What needs maintainer decision

- Blog/external-writeup policy (escalated).
- Whether to proactively send a "we have research on this" message to the Anthropic dev team via `disclosure@anthropic.com` or directly via #36884 PR. Either is reasonable.
- Whether RC-EDIT-PROMPT-2126 investigation is high enough priority to be the next session's focus, or whether FEAT-0003 setup (the security-research framework) should go first.

## Follow-up tasks proposed

- **`INF-0003`** — implement the probe suite (scripts under `app-src/js-probes/suite/`). Effort: ~3-4 hours.
- **`INF-0004`** — implement the change-detect script + baseline snapshot workflow. Effort: ~2 hours.
- **`ISSUE-0003`** — RC-EDIT-PROMPT-2126 disambiguation (shared with FEAT-0001 follow-ups). Effort: ~1-2 hours.
- **`GTSK-0001`** — first-pass KB content fill for the "Shallow" / "None" topics (MCP trust, Skill permissions, filesystem ACL, sandbox cross-platform). Effort: ~4-6 hours.

<!-- version: v2026.05.18.01 -->
