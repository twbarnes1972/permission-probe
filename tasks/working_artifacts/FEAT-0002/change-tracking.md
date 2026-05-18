# Change-Tracking Workflow

Spec for detecting when Claude Code's permission/security surface changes. Per [PLAN §4](PLAN.md#4-change-tracking-workflow--pick).

**Status:** Spec only — implementation in proposed follow-up `INF-0004`.

---

## Three-signal change detection

| Signal | Frequency | Trigger | Implementation |
|---|---|---|---|
| **Primary: claude.exe binary diff** | Per release | New version detected | Run probe suite + grep symbol regions |
| **Secondary: GitHub releases watcher** | Weekly | New tag at anthropics/claude-code | Parse release notes for permission/hook/settings keywords |
| **Tertiary: docs schema diff** | Monthly | Periodic | `curl` each canonical doc URL + diff against baseline |

The signals are layered for redundancy. The primary catches *all* changes that affect runtime behavior; the secondary catches changes Anthropic communicates intentionally; the tertiary catches doc-only revisions (re-reads of existing behavior, new examples, etc.) that may not change the binary but do change what's "documented."

## Primary signal — claude.exe binary diff

When a new claude.exe is installed (detected via `claude --version` differing from a stored last-seen value):

1. **Run the full probe suite** (`node app-src/js-probes/suite/run-all.js`). Any verdict change is a flag.
2. **Symbol-region greps:**
   ```bash
   # Save offsets for known-relevant functions
   grep -aob "ruleContent" /path/to/claude.exe | head -20 > /tmp/ruleContent-offsets.txt
   grep -aob "isBypassPermissionsModeAvailable" /path/to/claude.exe | head -5 > /tmp/bypass-offsets.txt
   grep -aob "filePatternTools" /path/to/claude.exe | head -5 > /tmp/filepatterntools-offsets.txt
   
   # Diff against the last-known offsets in kb/baselines/
   diff /tmp/ruleContent-offsets.txt kb/baselines/<prev>-ruleContent-offsets.txt
   ```
3. **Disassembly context extraction** for any region that moved significantly (offsets ±10KB+):
   ```bash
   dd if=/path/to/claude.exe bs=1 skip=$((OFFSET-500)) count=2000 status=none \
     | tr -c '[:print:][:space:]' '.' \
     > kb/baselines/<version>-XIq-context.txt
   ```
4. **Compare disassembly** against the stored baseline. Material change → re-run INVESTIGATION.md methodology.

**Storage:** baselines live at `kb/baselines/<version>-<symbol>.txt`. Committed to the repo — they're small, and the diffs are the value.

## Secondary signal — GitHub releases watcher

Weekly:

```bash
gh release list --repo anthropics/claude-code --limit 10 \
  --json tagName,publishedAt,name \
  > /tmp/releases.json
```

Diff against `kb/baselines/last-known-releases.json`. New entries → fetch their release notes:

```bash
gh release view <tag> --repo anthropics/claude-code --json body --jq .body \
  > /tmp/release-notes.md
```

Grep release notes for permission/hook/settings keywords:

```bash
grep -iE 'permission|hook|settings\.json|matcher|allow rule|deny rule|bypassPermissions|additionalDirectories|sandbox|MCP|skill' /tmp/release-notes.md
```

Any match → flag for manual review + update `kb/REFERENCE.md` Last-verified dates after running probe suite.

## Tertiary signal — docs schema diff

Monthly, for each canonical doc URL in [kb/README.md § Sources catalog](kb/README.md#sources-catalog):

```bash
# Pseudo — each URL gets its own snapshot
curl -s 'https://code.claude.com/docs/en/permissions.md' \
  > kb/baselines/$(date +%Y-%m)-docs-permissions.md
```

Diff against last month's snapshot:

```bash
diff kb/baselines/2026-04-docs-permissions.md kb/baselines/2026-05-docs-permissions.md
```

Material changes → update REFERENCE.md "Documented behavior" sections + Last-verified date.

## Baselines directory layout

```
kb/baselines/
  2026-05-claude-version.txt                  # output of `claude --version`
  2026-05-ruleContent-offsets.txt
  2026-05-bypass-offsets.txt
  2026-05-filePatternTools-offsets.txt
  2026-05-XIq-context.txt
  2026-05-h0-context.txt
  2026-05-docs-permissions.md
  2026-05-docs-hooks.md
  2026-05-docs-settings.md
  ...
  2026-05-releases.json
```

Each baseline file is small (KB range). All committed — git is the version log.

## When to run

**Today (Stage 1):** all manual. Maintainer runs the three signals on convenient cadence — probably aligned to noticing claude.exe got updated.

**Future (Stage 2):** `/schedule` weekly cron runs secondary + tertiary; primary fires on-demand when a new claude.exe is observed.

Cross-reference [FEAT-0001 PLAN §3 cadence](../FEAT-0001/PLAN.md#3-cadence--automation-surface--pick) — shares the same automation surface.

## What changes when a signal fires

Decision tree:

```
Primary fires (probe verdict changed):
  - Known bug now fixed (PASS → FAIL on a known-bug probe):
      → update kb/REFERENCE.md (last verified, observed behavior section)
      → update root-causes.md (known-fixed versions field)
      → post fix-confirmation comment via FEAT-0001 Template D
      → README deprecation note if workaround obsolete
  - New unexpected behavior (new FAIL or INCONCLUSIVE):
      → open ISSUE-NNNN to investigate
      → freeze probe-suite cadence on this version pending investigation
      → consider FEAT-0003 disclosure if security-sensitive

Secondary fires (release notes mention permissions):
  → manual read of release notes
  → run primary signal (probe suite) immediately
  → update REFERENCE.md if behavior described differs from current understanding

Tertiary fires (docs changed):
  → diff and read the change
  → update REFERENCE.md "Documented behavior" section
  → if docs now describe undocumented-but-observed behavior we'd noted: remove from "Known gaps"
  → if docs contradict observed behavior: flag for investigation
```

## Open question — escalated

Some change-tracking decisions need maintainer input:
- Whether baselines should be committed publicly. They're small binary-derived snippets (offsets + disassembly context) — useful but they're also evidence of "we're disassembling the binary." Defensible either way; default committed (consistent with this repo's existing posture of INVESTIGATION.md being public).
- Whether to set up the `/schedule` cron immediately or wait for the FEAT-0001 cadence decision. Shares automation surface.

<!-- version: v2026.05.18.01 -->
