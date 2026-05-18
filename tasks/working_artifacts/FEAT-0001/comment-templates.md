# Comment Templates + Style Guide

Per [PLAN §7](PLAN.md#7-comment-style-guide--see-comment-templatesmd). Skeletons for the common comment shapes we'll post on upstream issues. Each template includes the required components (cross-link to root cause + reproducer + workaround + acknowledgment of gaps + AI-assistance disclosure + conflict-of-interest disclosure).

Replace `<placeholders>` with specifics per issue. **Always edit before posting** — generic comments read as brigading.

---

## Template A — Known root cause, primary thread

Use when: the issue maps cleanly to RC-XIQ-MATCHER or RC-BYPASS-GATE and we're commenting on the *primary* tracker (not a duplicate).

```markdown
Reproduced and root-caused this — sharing notes in case it saves the team time.

## Root cause

<one-paragraph summary of the relevant RC — pull from tasks/working_artifacts/FEAT-0001/root-causes.md>

The disassembly + four-row reproducer is in [permission-probe / INVESTIGATION.md §<section-name>](https://github.com/twbarnes1972/permission-probe/blob/main/tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md#<anchor>).

## Empirical reproducer

<2-3 line CLI invocation that reproduces deterministically via `claude --print --debug "permission,tool" --debug-file out.log --permission-mode default -- "<prompt>"`>

## Workaround (today)

<bare-rules trick OR PreToolUse hook — link to permission-probe / app-src/py-helpers/file-deny-guard.py if the hook is relevant>

## What this comment does NOT explain

<honest note about what we haven't traced — e.g., "VSCode extension's settings-load path is different and I haven't investigated that">

---

_Disclosure: maintainer of [permission-probe](https://github.com/twbarnes1972/permission-probe) (GPL-3.0 with a standing license grant to Anthropic for Claude Code inclusion). Comment drafted with Claude Code assistance; reviewed and posted by @<maintainer-handle>._
```

---

## Template B — Cross-link to existing root-cause comment (duplicate / related thread)

Use when: an issue's symptom maps to a root cause we've already analyzed in detail elsewhere. Goal: link, don't re-paste the analysis.

```markdown
Same root cause as <link to primary tracker comment, e.g., https://github.com/anthropics/claude-code/issues/36884#issuecomment-XXXX>: <one-sentence summary of the RC mechanism>.

Full disassembly + reproducer matrix in [that comment / the linked permission-probe writeup](https://github.com/twbarnes1972/permission-probe/blob/main/tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md). Marking these as duplicates seems right.

_Disclosure: maintainer of [permission-probe](https://github.com/twbarnes1972/permission-probe). Comment drafted with Claude Code assistance; reviewed and posted by @<maintainer-handle>._
```

---

## Template C — Helpful triage on a novel symptom we haven't fully root-caused

Use when: an issue's symptom is plausible-but-unverified, we have a partial hypothesis, and we want to offer the maintainer a starting point without overclaiming.

```markdown
Tentatively hypothesis: <one paragraph proposing what might be going on, framed as a hypothesis, NOT a finding>.

Suggested verification steps:

1. <step 1 — usually a `--print --debug "permission,tool"` invocation>
2. <step 2 — a comparison run with a different settings.json snippet>
3. <step 3 — what to look for in the debug output>

Happy to investigate further if helpful — I've been disassembling `claude.exe` for related permission bugs ([context](https://github.com/twbarnes1972/permission-probe)), and this one is adjacent.

_Disclosure: maintainer of permission-probe. Comment drafted with Claude Code assistance; reviewed and posted by @<maintainer-handle>._
```

---

## Template D — Acknowledging a fix shipped

Use when: a release lands that addresses one of our tracked root causes. Goal: confirm the fix from our side, thank the team, mark the workaround obsolete.

```markdown
Confirming this is fixed in <release version> on <platform>. Re-ran the four-row reproducer matrix from [our earlier comment](<link>); all rows that were previously blocked now pass.

The `permission-probe` workaround can be deprecated for users on <release version> or later — a deprecation note has been added to that repo's README.

Thanks for the fix.
```

---

## Style guide (binding rules)

| Rule | Applies to |
|---|---|
| **Cross-link the canonical RC analysis** — don't re-paste it. | A, B, D |
| **Include the reproducer.** Either inline or as a link to the same. | A, C |
| **Acknowledge gaps** — what we haven't traced. | A |
| **AI-assistance disclosure** footer on any comment substantially AI-drafted. | A, B, C |
| **Conflict-of-interest disclosure** (the standing Anthropic grant) on any comment that includes our analysis. | A, B, C |
| **Never speculate framed as fact.** Hypothesis-framing for unverified claims. | C |
| **Never market this repo.** Mention it only when relevant. | All |
| **Never snark.** About Anthropic, the dev team, other reporters. | All |
| **Cooldown ≥14 days** between comments on the same thread. | All |
| **Max 3 substantive comments/week** total across tracked issues. | All |

## What never to post

- "This is a security issue!!1" alarmism. If you genuinely think it's a security issue, follow [FEAT-0003's process](../FEAT-0003/PLAN.md) — HackerOne, not a public issue thread.
- POC code for an unfixed vulnerability.
- Internal task IDs (`ISSUE-0001`, `FEAT-0001`) — those are our private referents; the public version is the GitHub issue number.
- Speculation about Anthropic's internal triage decisions or development priorities.
- Anything that would embarrass either party 6 months from now.

## Posting procedure

Once a draft is approved by the maintainer:

```bash
gh issue comment <gh#> --body-file tasks/working_artifacts/FEAT-0001/drafts/<gh#>.md
```

Then move the draft to `posted/<YYYY-MM-DD>-<gh#>.md` to record what was actually posted and prevent double-commenting. Update [registry.md](registry.md) `last_comment` field.

<!-- version: v2026.05.18.01 -->
