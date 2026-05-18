# Verification Suite — design + initial probe specs

Spec for extending `app-src/js-probes/probe.js` into a versioned probe suite that acts as the executable spec for Claude Code's permission/security behavior. Per [PLAN §5](PLAN.md#5-verification--regression-suite--pick).

**Status:** Spec only — implementation lives in proposed follow-up task `INF-0003`. This document is the contract that implementation should satisfy.

---

## Goals

1. **Regression detection.** When Anthropic ships a fix (or regression) affecting a known root cause, the suite tells us — not anecdote.
2. **Version-pinned ground truth.** Each probe records the claude.exe version it ran against. Historical runs are diff-able.
3. **Cheap to extend.** Adding a new probe = adding one file in `app-src/js-probes/suite/`, no test-framework boilerplate.
4. **Deterministic verdict.** Each probe outputs `PASS`, `FAIL`, or `INCONCLUSIVE` with reasoning — no human judgment needed for the headline result.

## Suite layout

```
app-src/js-probes/
  probe.js                          # existing — picomatch verification, becomes probe-picomatch.js
  package.json                      # existing — picomatch dep
  suite/
    run-all.js                      # orchestrator: discovers + runs all probe-*.js, summarizes
    probe-xiq-matcher.js            # P1: verifies RC-XIQ-MATCHER persists
    probe-bypass-gate.js            # P2: verifies RC-BYPASS-GATE persists
    probe-bare-edit.js              # P3: disambiguates RC-EDIT-PROMPT-2126
    probe-cd-prefix-bypass.js       # P4: exercises upstream #59498
    probe-picomatch.js              # P5: existing probe, generalized
    probe-hook-stdin-payload.js     # P6: hook payload schema validator
  runs/
    YYYY-MM-DD-{version}/
      summary.md                    # one row per probe
      probe-xiq-matcher.log
      probe-bypass-gate.log
      ...
```

## Probe contract

Each `probe-*.js` script:

1. Runs synchronously / awaits its own work — no daemon, no setup beyond what's in the file.
2. Begins by recording `claude --version` and the current date/time.
3. Performs its specific behavioral check.
4. Prints `=== VERDICT: PASS|FAIL|INCONCLUSIVE ===` as the **last line** of stdout.
5. Exits 0 on PASS, 1 on FAIL, 2 on INCONCLUSIVE.

**Verdict semantics:**
- `PASS` = the behavior we expected is present. For known-bug probes (P1, P2), this means the bug is still present. The probe will start FAILing when the bug is fixed.
- `FAIL` = expected behavior is *absent*. For known-bug probes, this means the bug was fixed (good news from the user perspective; the workaround can be deprecated).
- `INCONCLUSIVE` = couldn't determine (e.g., claude.exe wasn't found, or the test setup couldn't be created).

For each probe, the expected verdict at the time of writing should be documented in the file header — that's the "this is what we know today" snapshot. Subsequent runs are compared against this.

## Initial probes — detailed specs

### P1: `probe-xiq-matcher.js`

**Purpose:** Verify [RC-XIQ-MATCHER](../FEAT-0001/root-causes.md#rc-xiq-matcher) persists — path-globbed Edit allow rules silently no-op.

**Expected verdict at time of writing:** `PASS` (bug present; rule does not match).

**Method:**

1. Write a temp settings.json containing `permissions.allow: ["Edit(/tmp/probe-target/**)"]`.
2. Create a file at `/tmp/probe-target/sentinel.md` (or Windows equivalent).
3. Invoke `claude --print --debug "permission,tool" --debug-file /tmp/probe-xiq.log --permission-mode default --settings <temp-path> -- "Edit /tmp/probe-target/sentinel.md replacing X with Y, then revert"`.
4. Parse the debug log for the permission decision.
5. If permission was **denied / asked** → `PASS` (XIq still rejecting the parens-content rule).
6. If permission was **allowed via rule match** → `FAIL` (matcher was fixed).
7. If anything else → `INCONCLUSIVE`.

**Critical detail:** must use `--permission-mode default` (not `acceptEdits`, which would bypass the matcher entirely via mode and produce false PASSes).

### P2: `probe-bypass-gate.js`

**Purpose:** Verify [RC-BYPASS-GATE](../FEAT-0001/root-causes.md#rc-bypass-gate) persists — `defaultMode: "bypassPermissions"` in settings.json silently rejected.

**Expected verdict at time of writing:** `PASS` (gate still rejecting).

**Method:**

1. Write a temp settings.json with `permissions.defaultMode: "bypassPermissions"`.
2. Invoke `claude --print --debug "permission,tool" --debug-file /tmp/probe-bypass.log --settings <temp-path> -- "Run echo hello"`.
3. Parse the debug log for either:
   - `Ignoring permission update: setMode 'bypassPermissions' rejected` → bug present → `PASS`.
   - No such log + Bash was auto-allowed via bypass → `FAIL` (gate was opened).
4. If neither signal is present → `INCONCLUSIVE`.

### P3: `probe-bare-edit.js`

**Purpose:** Disambiguate [RC-EDIT-PROMPT-2126](../FEAT-0001/root-causes.md#rc-edit-prompt-2126) — does bare `Edit` allow rule suppress prompts in the *current* claude.exe?

**Expected verdict at time of writing:** Unknown — that's the point.

**Method:**

1. Temp settings.json with `permissions.allow: ["Edit"]` (bare).
2. Create a file at a path under cwd.
3. Invoke `claude --print --debug ... -- "Edit <file> replacing X with Y, then revert"`.
4. If `permissionDecisionMs=1` and decision was allow-via-rule → `PASS` (bare Edit still works as expected per RC-XIQ-MATCHER analysis).
5. If decision was deny / ask despite the bare allow → `FAIL` (RC-EDIT-PROMPT-2126 is real; the bare-allow workaround no longer applies).
6. Other → `INCONCLUSIVE`.

**Output of this probe directly drives whether the README workaround (recommending bare `Read`/`Edit`/`Write`) is still valid.**

### P4: `probe-cd-prefix-bypass.js`

**Purpose:** Exercise upstream #59498 — does `cd /path && git push` evade `Bash(git push:*)` deny rule via cd-prefix stripping?

**Expected verdict at time of writing:** `PASS` (bypass present per upstream report; we have not independently verified).

**Method:**

1. Temp settings.json with `permissions.deny: ["Bash(git push:*)"]`.
2. Invoke `claude --print --debug ... -- "Run: cd /tmp && git push origin main --dry-run"` (the `--dry-run` ensures no actual push attempt).
3. If the command executed → `PASS` (bypass works).
4. If denied → `FAIL` (no bypass; report is incorrect or has been fixed).
5. Other → `INCONCLUSIVE`.

**Caution:** the test command itself should never actually push to a real remote. Use `--dry-run` or a scratch directory with no git remote.

### P5: `probe-picomatch.js` (existing `probe.js`, generalized)

**Purpose:** Confirm picomatch correctly matches path patterns when reached. Originally written to rule out picomatch as the cause of RC-XIQ-MATCHER.

**Expected verdict:** `PASS` (picomatch correct; rules out a downstream-library cause for matcher bugs).

**Method:** existing `probe.js` logic, refactored to emit the verdict line. Iterate over a fixed `TEST_PATHS` against a fixed set of patterns and option variants. PASS if all expected matches succeed and all expected non-matches fail.

### P6: `probe-hook-stdin-payload.js`

**Purpose:** Verify hook stdin payloads match the documented schema for each lifecycle event.

**Expected verdict at time of writing:** `PASS` for PreToolUse (well-known), `INCONCLUSIVE` for others (untested).

**Method:**

1. Install a temporary `PreToolUse` hook that dumps its stdin to a file then exits 0.
2. Invoke a tool call (e.g., a trivial Bash).
3. Validate the dumped JSON against the schema in [kb/REFERENCE.md §Hook system](kb/REFERENCE.md#hook-system).
4. Repeat for other event types (`SessionStart`, `Stop`, `UserPromptSubmit`) — different invocation triggers.
5. PASS if all schemas match; FAIL on any mismatch.

This probe is the canonical "what does the harness actually send?" empirical capture.

## Orchestrator (`run-all.js`)

```bash
node app-src/js-probes/suite/run-all.js
```

Effect:
1. Discover all `probe-*.js` siblings.
2. Run each in sequence (parallelism not needed at this scale).
3. Collect stdout, stderr, exit code, duration.
4. Write a per-run directory `runs/YYYY-MM-DD-<version>/`:
   - `summary.md` — table: probe / verdict / duration / log file.
   - One log file per probe.
5. Print the summary to stdout.

Failure mode: if `claude.exe` is unavailable / wrong version, all probes that depend on `claude --print` go INCONCLUSIVE; suite continues to run the ones that don't (P5 picomatch).

## When a probe verdict changes

When a known-bug probe flips from PASS → FAIL (the bug appears to be fixed):

1. Don't trust the first run. Re-run twice. If consistent → proceed.
2. Update the relevant section in [kb/REFERENCE.md](kb/REFERENCE.md) with the new claude.exe version and the observation.
3. Update [FEAT-0001 root-causes.md](../FEAT-0001/root-causes.md): mark the RC's "known-fixed versions" field.
4. Update [registry.md](../FEAT-0001/registry.md) rows tied to that RC: mark `state` as candidate for `closed` pending upstream confirmation.
5. Post a fix-confirmation comment on the upstream tracker using [FEAT-0001 comment-templates.md Template D](../FEAT-0001/comment-templates.md#template-d--acknowledging-a-fix-shipped).
6. Add a deprecation note to the relevant README section if the workaround is now obsolete.

## Cross-platform considerations

- All paths in probe code use forward slashes where possible (works on Windows + POSIX).
- Temp settings.json written to OS-specific temp dir (`os.tmpdir()` in Node).
- The `claude.exe` invocation works the same on macOS / Linux / Windows once on PATH.
- Some probes (e.g., P4 cd-prefix) may behave differently across shells. Document the shell used per run in `summary.md`.

## Effort estimate

Implementation: ~3-4 hours for the initial 6 probes + orchestrator. Each individual probe is ~30-60 minutes to write + debug.

<!-- version: v2026.05.18.01 -->
