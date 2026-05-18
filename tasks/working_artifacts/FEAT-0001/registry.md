# Upstream Issue Registry — anthropics/claude-code

Tracks open upstream issues in scope (per [PLAN §1](PLAN.md#1-scope-definition)) with their root-cause mapping and our triage state.

**Last sweep:** 2026-05-18 (initial seed from autonomous research pass).
**Sweep mechanism:** TBD — manual until `scripts/triage-sweep.sh` lands (see INF-0001 follow-up).
**Cursor (last-poll timestamp):** 2026-05-18T00:00:00Z

---

## Schema

| Field | Notes |
|---|---|
| `gh#` | GitHub issue number (link in row body) |
| `title` | Short title (truncated to 60 chars in table) |
| `opened` | YYYY-MM-DD |
| `last_seen` | Last sweep date |
| `state` | open / closed / locked |
| `mapped_rc` | Foreign key to [root-causes.md](root-causes.md), or `needs-triage`, or `novel` |
| `our_action` | none / commented / opened-internal / escalated / skip |
| `our_task` | If applicable |
| `last_comment` | When we last commented (— = never) |
| `conf` | Confidence in RC mapping: L / M / H |

---

## Tracked issues

| gh# | title | opened | last_seen | state | mapped_rc | our_action | our_task | last_comment | conf |
|---|---|---|---|---|---|---|---|---|---|
| [27040](https://github.com/anthropics/claude-code/issues/27040) | Deny permissions in settings.json ignored | 2026-02-20 | 2026-05-18 | open | RC-XIQ-MATCHER | none | — | — | H |
| [30519](https://github.com/anthropics/claude-code/issues/30519) | META: Permissions matching is fundamentally broken | 2026-03-03 | 2026-05-18 | open | RC-XIQ-MATCHER (umbrella) | none | — | — | H |
| [39523](https://github.com/anthropics/claude-code/issues/39523) | META: Bypass permissions mode is fundamentally broken | 2026-03-26 | 2026-05-18 | open | RC-BYPASS-GATE (umbrella) | none | — | — | H |
| [37420](https://github.com/anthropics/claude-code/issues/37420) | Bypass mode resets after PreToolUse hook returns "ask" | 2026-03 | 2026-05-18 | open | needs-triage (likely RC-BYPASS-GATE adjacent) | none | — | — | M |
| [49525](https://github.com/anthropics/claude-code/issues/49525) | Hook setMode:'bypassPermissions' silently dropped 2.1.110+ | 2026-04-16 | 2026-05-18 | open | RC-BYPASS-GATE (same gate, hook code path) | none | — | — | H |
| [51286](https://github.com/anthropics/claude-code/issues/51286) | additionalDirectories glob doesn't propagate to subagents | 2026-04-20 | 2026-05-18 | open | needs-triage (likely novel — subagent context propagation) | none | — | — | M |
| [55255](https://github.com/anthropics/claude-code/issues/55255) | Permission allowlist + mode toggles not suppressing prompts | 2026-05-01 | 2026-05-18 | open | RC-EDIT-PROMPT-2126 (provisional) | escalated | proposed ISSUE-0003 | — | L |
| [59171](https://github.com/anthropics/claude-code/issues/59171) | VSCode/Cursor extension permission-IPC race | 2026-05-14 | 2026-05-18 | open | needs-triage (transport/IPC, not matcher) | skip | — | — | M |
| [59498](https://github.com/anthropics/claude-code/issues/59498) | cd-prefixed compound commands bypass permission system | 2026-05-15 | 2026-05-18 | open | novel | escalated | proposed ISSUE-0002 | — | H |
| [59738](https://github.com/anthropics/claude-code/issues/59738) | PostToolUse hook `if: Bash(<head> *)` matcher false-positives | 2026-05-16 | 2026-05-18 | open | novel (hook-level matcher) | none | — | — | M |
| [59843](https://github.com/anthropics/claude-code/issues/59843) | Plan Approved button drops session into default mode | 2026-05-16 | 2026-05-18 | open | needs-triage (mode-state regression) | none | — | — | L |
| [60112](https://github.com/anthropics/claude-code/issues/60112) | SessionStart hook crashes Agent View background sessions | 2026-05-18 | 2026-05-18 | open | novel (hook lifecycle / Agent View) | none | — | — | M |
| [36884](https://github.com/anthropics/claude-code/issues/36884) | VS Code extension permission rules not respected | 2026-03 | 2026-05-18 | open | RC-XIQ-MATCHER | commented | ISSUE-0001 | (draft posted) | H |
| [57132](https://github.com/anthropics/claude-code/issues/57132) | Allow rules under ~/.claude/ show as loaded but don't match | 2026-05 | 2026-05-18 | open | RC-XIQ-MATCHER | commented | ISSUE-0001 | (draft posted) | H |
| [15921](https://github.com/anthropics/claude-code/issues/15921) | .claude/settings.local.json permissions not respected | 2026-01 | 2026-05-18 | open | RC-XIQ-MATCHER + RC-BYPASS-GATE | commented | ISSUE-0001 | (draft posted) | H |

---

## Notes

- The three issues at the bottom (#36884, #57132, #15921) are the ones [ISSUE-0001](../../closed/ISSUE-0001.md) was filed against. They appear here because they're the original tracked threads with our analysis already drafted (drafts live at [../ISSUE-0001/upstream-comments/](../ISSUE-0001/upstream-comments/)).
- `last_comment` = "(draft posted)" means the comment draft is committed to this repo but **not necessarily posted to GitHub yet**. Verify before re-commenting.
- Issues #18160 (Bash matcher), #31925 (managed remote-settings deny), #49122 (.claude/settings.json deny bypass), #52822 (hook permissionDecision:"allow"), #47810 (background-task bypass loss) are *closed* — referenced in research but not seeded here.

## Closed-but-relevant (historical context, do not re-comment)

If reopened, these warrant evaluation:
- **#49122** — closed as duplicate; deny rule on `.claude/settings.json` itself bypassed.
- **#52822** — closed; hook returning `permissionDecision:"allow"` didn't suppress prompt in 2.1.119.
- **#21155** — closed `not planned`.

---

## How to update

Manual sweep until `INF-0001` lands:

```bash
# Approximate manual procedure
gh api -X GET "/repos/anthropics/claude-code/issues" \
  -f state=open -f since=2026-05-18T00:00:00Z -f per_page=100 \
  --paginate \
  --jq '.[] | select(.title + .body | test("permission|settings\\.json|hook|allow rule|deny rule|matcher|picomatch|additionalDirectories|bypassPermissions|dangerously-skip-permissions"; "i")) | {number, title, created_at, updated_at, state, user: .user.login, url: .html_url}' \
  > inbox/$(date +%Y-%m-%d).json
```

Then diff against this table, classify each new issue (RC mapping with citation, or `needs-triage`, or `novel`), and append rows. Update the `Last sweep` date and `Cursor` at the top.

<!-- version: v2026.05.18.01 -->
