# ISSUE-0003: Disambiguate RC-EDIT-PROMPT-2126 — does bare `Edit` allow still suppress prompts in current claude.exe?

**Created:** 2026-05-18
**Status:** Open
**Priority:** High
**Category:** Issue

---

## Summary

Upstream [#55255](https://github.com/anthropics/claude-code/issues/55255) reports that bare `Edit` in `permissions.allow` no longer suppresses Edit prompts in Claude Code 2.1.126+. This contradicts the finding in [ISSUE-0001](../closed/ISSUE-0001.md) (verified on 2.1.143.a06) where bare names were the working workaround. Either the reporter mis-stated, the behavior changed in a version range, or the README's recommended workaround is no longer valid for current users. **Disambiguation is the only correct response.**

## Steps to Reproduce

Run [`probe-bare-edit.js`](../working_artifacts/FEAT-0002/verification-suite.md#p3-probe-bare-editjs) from the FEAT-0002 verification suite (spec only — needs implementation as part of this task or in INF-0003). Minimum viable repro without the full suite:

1. Capture current `claude --version`.
2. Write a temp settings.json with `permissions.allow: ["Edit"]` (bare, no parens).
3. Create a file at a path under cwd.
4. Invoke:
   ```bash
   claude --print --debug "permission,tool" --debug-file out.log \
     --permission-mode default --settings <temp-path> \
     -- "Edit <file> replacing X with Y, then revert"
   ```
5. Inspect `out.log` for the permission decision and `permissionDecisionMs`.

## Expected vs Actual Behavior

**Expected (per ISSUE-0001 finding on 2.1.143.a06):** allow-via-rule, `permissionDecisionMs=1`, no prompt.

**Actual (per upstream #55255 on 2.1.126+):** ask / deny / prompt-shown despite the bare allow.

The point of this task is to determine which is currently correct.

## Root Cause

Pending — depends on the empirical result.

Possibilities (per [RC-EDIT-PROMPT-2126 in root-causes.md](../working_artifacts/FEAT-0001/root-causes.md#rc-edit-prompt-2126)):

1. Regression introduced between 2.1.126 and 2.1.143 (i.e., bare allow was broken in a range, then fixed) — unlikely.
2. Regression introduced AFTER 2.1.143 (after our investigation) — needs re-test on current claude.exe.
3. Reporter misread their own setup — also possible.
4. Different code path — bare `Edit` allow works in some session configurations and not others.

## Dependencies

| Blocked By | None |

Adjacent: [FEAT-0002](FEAT-0002.md) — the verification suite spec under [verification-suite.md](../working_artifacts/FEAT-0002/verification-suite.md) includes `probe-bare-edit.js`, which this task either implements directly or uses if INF-0003 lands first.

## Acceptance Criteria

- [ ] Current claude.exe version is recorded in the writeup.
- [ ] Bare `Edit` allow rule tested empirically with the exact reproducer above on current claude.exe.
- [ ] If the reporter is correct (bare allow doesn't work): run the disassembly methodology to find the new gate, document the new RC fully in [root-causes.md](../working_artifacts/FEAT-0001/root-causes.md), and add a README deprecation note (the existing "bare rules workaround" recommendation needs updating).
- [ ] If the reporter is incorrect / out of date (bare allow still works): mark `RC-EDIT-PROMPT-2126` as `closed-not-reproduced` in root-causes.md and add a brief note explaining what configuration the reporter likely had.
- [ ] Either way: update [FEAT-0001 registry.md](../working_artifacts/FEAT-0001/registry.md) row for #55255 with the verdict and our confidence level.
- [ ] If outcome warrants, draft a comment for #55255 using FEAT-0001 Template A (root-cause found) or Template C (hypothesis-only triage).

## Implementation Notes

- Use the methodology from [INVESTIGATION.md](../working_artifacts/ISSUE-0001/INVESTIGATION.md) — same `grep -aob` + `dd` + `--print --debug` approach.
- If the probe suite is built first (INF-0003), use `probe-bare-edit.js` directly. Otherwise this task implements the minimum viable test inline.
- Output: a writeup in `tasks/working_artifacts/ISSUE-0003/INVESTIGATION.md` analogous to ISSUE-0001's, scoped to this question only.

## Status Notes

- **2026-07-12 — largely answered by the ISSUE-0004 resolution retest.** On claude.exe **2.1.207**, sandboxed (`CLAUDE_CONFIG_DIR`, no hooks): bare `Read`/`Edit` allow rules auto-approved without prompts in both `--print` and ConPTY-driven interactive TUI (Read: `permissionDecisionMs=8`, dispatched `outcome=ok`; Edit auto-dispatched and blocked only where a deny rule matched). So bare allows work *now* — and hypothesis #4's "different code path" pattern was real but is also fixed (see [ISSUE-0004 § Resolution](../closed/ISSUE-0004.md#resolution-2026-07-12)). Upstream #55255 was **closed as "not planned" / stale** with no maintainer comment, weakening the case for further investment. Remaining before closing: decide whether the registry/root-causes bookkeeping (RC-EDIT-PROMPT-2126 → `closed-not-reproduced` on current builds) is enough, or whether the version range 2.1.126–2.1.143 deserves a look for a transient regression. Recommendation: close as not-reproduced-on-current; the fix wave that resolved ISSUE-0001/0004 makes historical bisection low-value.

## Related

- [ISSUE-0001](../closed/ISSUE-0001.md) — methodology + RC-XIQ-MATCHER + RC-BYPASS-GATE.
- [Root cause stub: RC-EDIT-PROMPT-2126](../working_artifacts/FEAT-0001/root-causes.md#rc-edit-prompt-2126).
- [Verification suite probe P3 spec](../working_artifacts/FEAT-0002/verification-suite.md#p3-probe-bare-editjs).
- Upstream: [#55255](https://github.com/anthropics/claude-code/issues/55255).

<!-- version: v2026.05.18.01 -->
