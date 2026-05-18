# FEAT-0001 PLAN — Recurring upstream issue triage + root-cause registry + helpful commenting

**Authored:** 2026-05-18 (autonomous planning pass)
**Status:** Plan draft — open for review. Implementation pieces split into follow-up tasks below.

This plan answers the 12 acceptance criteria in [../../open/FEAT-0001.md](../../open/FEAT-0001.md). Decisions are concrete picks with rationale; alternatives that were rejected are noted. Where a decision genuinely needs user input, see [ESCALATIONS.md](../../../ESCALATIONS.md).

---

## 1. Scope definition

**In-scope** — an upstream issue at `anthropics/claude-code` qualifies when its title or body matches any of:

- `permission` / `permissions`
- `settings.json`
- `hook` / `hooks` (including hook event names: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, `UserPromptSubmit`, etc.)
- `allow rule` / `deny rule` / `allow list` / `deny list`
- `matcher`
- `picomatch`
- `additionalDirectories`
- `bypassPermissions` / `dangerously-skip-permissions`
- `acceptEdits` / `plan mode` / `dontAsk`
- `PermissionRequest`
- `mcp__` (tool-rule format)
- `Skill(` (rule format)

**Out-of-scope** — model behavior, prompt injection of the model itself (different domain), IDE-extension bugs unrelated to permissions, account/billing issues, feature requests unrelated to security.

**Recency window** — open + opened-or-updated within last 365 days. (Older bugs may be stale or already fixed.)

**Why:** This list mirrors the symptom vocabulary observed in the 12-issue seed registry (see [registry.md](registry.md)) and covers the three known/suspected root causes. It will need expansion as new RCs are found.

## 2. Fetch tooling — pick

**Decision: REST `/repos/anthropics/claude-code/issues?since=<lastPoll>&state=open&per_page=100` with client-side regex filter, via `gh api`.**

Rationale (from research): the Search API is rate-limited 30/min vs 5000/hr for core; the `since=` parameter on the issues endpoint gives free incremental polling. `gh api` inherits `gh auth login` token — no separate PAT management. Atom feed (`/issues.atom`) returned HTTP 406, unusable.

**Rejected alternatives:**
- `gh issue list --search` — pleasant CLI but silently switches to the Search API for keyword queries, burning the tighter rate limit.
- Direct REST with PAT — equivalent capability but adds credential surface for no gain over `gh api`.
- Search API for incremental polling — wastes the rate limit; reserve for one-shot backfill / registry rebuild.

**Auth approach:** existing `gh auth login` on the maintainer's workstation. No fine-scoped PAT. Token has issue-read scope by default; no write access needed for the read-only fetch phase. Comment-posting uses the same `gh` auth identity (decision in §6).

## 3. Cadence + automation surface — pick

**Decision: Manual on-demand initially, via a thin script invocable from the repo. Move to `/schedule` weekly only after one month of successful manual runs.**

Implementation:
- Stage 1 (now): a `scripts/triage-sweep.sh` (or `.ps1`) in this repo that calls `gh api` with the `since` cursor stored in a small state file, filters with the regex from §1, writes diffs to `tasks/working_artifacts/FEAT-0001/inbox/`, and prints a summary. Maintainer runs it when convenient.
- Stage 2 (after a month of validation): wrap stage 1 in a `/schedule` cron-mode remote agent that runs weekly and stages the diff for maintainer review.

**Rejected:**
- `/loop` — wrong primitive; that's for active polling within a session, not background.
- Full `/schedule` immediately — escalates the blast radius before we know the script's failure modes (e.g., what happens when `gh auth` token expires).
- External Windmill — adds infra dependency; reuse the available primitives first.

**See ESCALATIONS.md** for the cadence-decision confirmation request.

## 4. Registry schema + storage — pick

**Decision: A markdown table in [registry.md](registry.md) within this artifact folder.** Each row is one tracked upstream issue.

**Fields:**

| Column | Type | Notes |
|---|---|---|
| `gh_issue` | int | GitHub issue number |
| `title` | string | Verbatim from GitHub (truncated to 80 chars in table; full title in row body if longer) |
| `opened` | YYYY-MM-DD | From `created_at` |
| `last_seen` | YYYY-MM-DD | Last time the registry-sweep saw activity (comments, updates) |
| `state` | open / closed / locked | GitHub state at last sweep |
| `mapped_rc` | RC-id or `needs-triage` or `novel` | Foreign key to [root-causes.md](root-causes.md) |
| `our_action` | none / commented / opened-internal / escalated / skip | Our workflow status |
| `our_task_id` | string | If we spawned an internal task (e.g., `ISSUE-0001`) |
| `last_comment` | YYYY-MM-DD | Last date *we* commented |
| `confidence` | low / med / high | Confidence in RC mapping |

**Storage rationale:** Markdown gives the best git-diffability for review (each sweep produces a reviewable diff in the PR/commit), greppability, and zero infrastructure. A SQLite or Supabase backend would be overkill for an expected steady-state of ~50–100 tracked issues. Migration to a richer store is straightforward later (the table is the model).

**Rejected:**
- SQLite — premature; would need a sync layer for diff review.
- Supabase MCP — fine if cross-session memory is wanted, but the markdown table is the canonical record; Supabase would be a downstream cache, not the source of truth.
- JSON / YAML — less human-scannable than a markdown table.

## 5. Root-cause mapping model — pick

**Decision: Each root cause gets a stable ID and a stub in [root-causes.md](root-causes.md). One issue can map to 0, 1, or N root causes; mapping is many-to-many but recorded by storing the comma-separated RC list in the `mapped_rc` column.**

Initial root-cause IDs (formalized from research):

- **`RC-XIQ-MATCHER`** — `XIq()`'s `if (rule.ruleValue.ruleContent !== void 0) return false` rejects every path-globbed `Edit(...)`/`Read(...)`/`Write(...)`/`Glob(...)`/`Skill(...)`/`mcp__(...)` rule. Documented in [INVESTIGATION.md §Finding #1](../ISSUE-0001/INVESTIGATION.md#finding-1--the-xiq-matcher-bug). Verified on claude.exe 2.1.143.a06.
- **`RC-BYPASS-GATE`** — `isBypassPermissionsModeAvailable` defaults `false` and only flips on launch-time CLI flag; settings.json `defaultMode:"bypassPermissions"` silently rejected. Documented in [INVESTIGATION.md §Finding #2](../ISSUE-0001/INVESTIGATION.md#finding-2--the-bypasspermissions-mode-gate). Verified on 2.1.143.a06.
- **`RC-EDIT-PROMPT-2126`** — *Provisional, needs verification.* Per upstream #55255, bare `Edit` in `permissions.allow` no longer suppresses prompts in 2.1.126+. This contradicts the RC-XIQ-MATCHER finding from 2.1.143.a06 where bare names worked. Either a regression we missed, or the reporter mis-stated. **A follow-up task should re-run probe.js methodology against 2.1.126 to disambiguate.**

Each RC entry in root-causes.md has: summary, evidence pointer (binary offset / INVESTIGATION.md section / disassembly snippet), verified-on version(s), known-affected versions, known-fixed versions (none yet), workaround pointer (e.g., this repo's hook), upstream tracker(s) we've reported in.

## 6. Per-cycle workflow draft — pick

**Decision: 4-stage workflow per sweep. Maintainer-in-the-loop on every comment.**

```
[Stage 1: Fetch]    gh api ... since=<lastPoll>  -->  raw issues JSON
[Stage 2: Filter]   regex over title+body         -->  in-scope subset
[Stage 3: Diff]     compare against registry.md  -->  new / updated / closed
[Stage 4: Triage]   for each delta:
                      - new issue:
                          map to RC (if confident) → draft comment in tasks/working_artifacts/FEAT-0001/drafts/<gh#>.md
                          if novel → propose opening an internal task (don't auto-create)
                      - updated existing:
                          refresh last_seen, mapped_rc if new evidence, our_action if dev team responded
                      - closed:
                          mark state=closed; if mapped to known RC and we have a related task, note "upstream-closed" hint
```

**Maintainer gate:** Every drafted comment lands in `drafts/<gh#>.md` for review. No auto-posting. Maintainer reads, edits, posts via `gh issue comment <gh#> --body-file drafts/<gh#>.md`, then moves the file to `posted/<date>-<gh#>.md` so we don't double-comment.

**Internal task spawning:** When a novel RC is suspected, the sweep produces a *proposal* (a draft task file at `tasks/open/proposed-ISSUE-NNNN.md` with the symptom + upstream link). Maintainer reviews and either renames to `ISSUE-NNNN.md` (committing to investigate) or deletes. Same pattern as comments — never auto-act, always review-first.

## 7. Comment style guide — see [comment-templates.md](comment-templates.md)

The style guide and three template skeletons are in the companion file. Headline rules:

- **Tone:** factual, helpful, never preachy. Acknowledge the dev team's constraints (this is a big surface, our investigation took two days, we're sharing notes to make their triage cheaper).
- **Required components of any substantive comment:**
  1. Cross-link to the root-cause documentation (`tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md` or the relevant RC entry).
  2. The relevant binary-disassembly snippet or the empirical reproducer (so maintainers can verify without re-deriving).
  3. Workaround pointer (link to this repo's hook).
  4. Acknowledgment of what we don't know (e.g., "haven't traced the IPC layer for VSCode extension symptoms").
- **Never include:**
  - Speculation framed as fact.
  - Marketing this repo. (The hook is mentioned because it's relevant, not as promotion.)
  - Snark about Anthropic, the dev team, or other reporters.
  - Anything that reads as brigading multiple threads with the same message (write each fresh).
  - "This is a security issue!!!" alarmism — see FEAT-0003 for the right channel.

## 8. Internal task spawning + naming

**Decision:** Novel-upstream-issues that we choose to investigate get the `ISSUE-NNNN` prefix (sequential, continuing from ISSUE-0001). The link from upstream → internal task lives in the `our_task_id` column of registry.md. The link from internal task → upstream lives in the internal task's `Related` section.

**Initial registry seed (next sequential numbers):** ISSUE-0002, ISSUE-0003 reserved for the two most pressing novel issues identified in research:
- `ISSUE-0002` placeholder for **#59498** (cd-prefixed Bash bypass) — needs investigation.
- `ISSUE-0003` placeholder for **#55255** / `RC-EDIT-PROMPT-2126` (bare Edit allow not suppressing prompts in 2.1.126+) — disambiguation needed.

**Not auto-created in this autonomous run** — opened as escalations for maintainer to commission.

## 9. Rate + politeness limits

**Decision:**

- **Maximum 3 substantive comments per week across all tracked issues.** Bias toward depth, not coverage.
- **Cooldown:** at least 14 days between *our* comments on the same thread, unless the dev team or OP @-mentions us.
- **Opt-out signal:** if a maintainer (any user with write access to anthropics/claude-code) replies with "we know," "duplicate," "stop," or similar dismissive language, flip the row's `our_action` to `skip` and never comment on that thread again. Don't argue.
- **Drafting cadence:** can draft comments freely; gate is at posting, not drafting.

## 10. Ethical + reputational guardrails

- **Disclose AI assistance in comments** when the comment was substantially drafted by an AI. Suggested footer: `_Comment drafted with Claude Code assistance; reviewed and posted by @<maintainer-handle>._` Be transparent.
- **Avoid brigading appearance:** don't comment on three duplicates in the same hour. Stagger by days. If multiple threads share a root cause, post ONCE in the canonical thread and link from the duplicates without repeating the analysis.
- **Disagreement handling:** if a maintainer triages a bug differently from our analysis (e.g., closes "not a bug"), respect it. Update the registry. If the discrepancy is technical and substantive, the right move is a small follow-up comment offering verification steps — not arguing.
- **Conflict of interest:** this repo's NOTICE.md has a standing license grant to Anthropic. Disclose this in any comment that includes our analysis — phrasing: `_Disclosure: maintainer of [permission-probe](https://github.com/twbarnes1972/permission-probe), GPL-3.0 with a standing license grant to Anthropic specifically for Claude Code inclusion._`

## 11. Effort + cost estimate

- **Per-sweep effort (maintainer):** ~20–30 min weekly = ~1.5 hr/month. Most of that is reading new comments and approving/editing drafts.
- **Per-sweep API cost:** the fetch script makes 1–3 `gh api` calls per sweep. Effectively free.
- **AI tokens:** drafting a substantive comment with all required components is ~$0.05–$0.20 of Claude tokens per draft. At 3 comments/week, ~$1–$3/month.
- **One-shot cost:** registry backfill + initial RC mapping = a few hours of focused work (mostly done already in the seeded research).

## 12. Reuse vs build

| Need | Reuse | Build |
|---|---|---|
| Issue fetch | `gh api` | Thin wrapper script (~30 lines) |
| Issue diff | `jq` + shell | None |
| Registry storage | Markdown | None |
| Comment drafting | Claude Code (interactive) | None |
| Posting comments | `gh issue comment` | None |
| Cadence (stage 2) | `/schedule` remote agent | Wrapper around stage-1 script |
| Cross-session memory | Existing claude.ai memory system | Sibling memory entries linking to RCs |
| Task spawning | task-manager from stackagentic-library (already in this repo) | None |

**Net new code:** ~50–100 lines of shell. Everything else is conventions + markdown + existing tooling.

---

## Follow-up tasks proposed

Once this plan is approved, the autonomous run has created the substrate. The remaining implementation work splits cleanly:

- **`INF-0001`** — write `scripts/triage-sweep.sh` (the fetch + diff script). Effort: ~2 hours.
- **`INF-0002`** — set up `/schedule` weekly cron for stage 2 (deferred until 1 month of manual stage-1 runs validate the script).
- **`ISSUE-0002`** — investigate upstream #59498 (cd-prefixed Bash bypass).
- **`ISSUE-0003`** — investigate upstream #55255 + verify `RC-EDIT-PROMPT-2126` against current claude.exe version.

## What's deferred

Everything in this PLAN that isn't a clean call (cadence escalation, AI-disclosure phrasing exact wording, bot-vs-personal-account if you ever want a bot) lives in [ESCALATIONS.md](../../../ESCALATIONS.md) for maintainer decision.

<!-- version: v2026.05.18.01 -->
