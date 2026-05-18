# ISSUE-0002: Investigate cd-prefix Bash bypass (upstream #59498)

**Created:** 2026-05-18
**Status:** Open
**Priority:** Medium
**Category:** Issue

---

## Summary

Upstream [#59498](https://github.com/anthropics/claude-code/issues/59498) reports that `cd /path && git push` evades a `Bash(git push:*)` deny rule because the harness canonicalizes cd-prefix away before matching. This is a novel Bash matcher bypass, distinct from [RC-XIQ-MATCHER](../working_artifacts/FEAT-0001/root-causes.md#rc-xiq-matcher) and [RC-BYPASS-GATE](../working_artifacts/FEAT-0001/root-causes.md#rc-bypass-gate). Reproduce, root-cause, and propose a fix shape — same rigor as ISSUE-0001.

## Steps to Reproduce

Run [`probe-cd-prefix-bypass.js`](../working_artifacts/FEAT-0002/verification-suite.md#p4-probe-cd-prefix-bypassjs) from the FEAT-0002 verification suite, or inline:

1. Write a temp settings.json with `permissions.deny: ["Bash(git push:*)"]`.
2. Invoke:
   ```bash
   claude --print --debug "permission,tool" --debug-file out.log \
     --settings <temp-path> \
     -- "Run: cd /tmp && git push origin main --dry-run"
   ```
3. Observe whether the command executed (bypass works) or was denied (no bypass).
4. **Safety:** the test command must never reach a real remote. Use `--dry-run` and run from a scratch directory with no git remote configured.

## Expected vs Actual Behavior

**Expected:** `Bash(git push:*)` deny should block any command that includes `git push`. The cd-prefix shouldn't matter.

**Actual (per #59498):** the harness strips idempotent `cd <path> &&` prefix before matching, so `cd /tmp && git push` matches whatever `git push:*` matches — and apparently this means it slips past the deny rule.

Empirical verification needed.

## Root Cause

Pending — requires disassembly. Suspected: the Bash content matcher (`dz8`) performs compound-command splitting + canonicalization in a way that drops the `cd` segment before evaluating the remaining segments against the rule set. If true, the canonicalization step is performing a security-relevant transformation outside the matcher's awareness.

Likely RC name once confirmed: `RC-CD-PREFIX-BYPASS` (proposed; finalize in root-causes.md after investigation).

## Dependencies

| Blocked By | None |

## Acceptance Criteria

- [ ] Reproducer confirmed empirically on current claude.exe (record version).
- [ ] If reproduced: trace the `dz8` Bash matcher in claude.exe via `grep -aob` for relevant symbols (`canonicalize`, `compound`, `splitCommand`, `cd`). Document the canonicalization logic.
- [ ] If reproduced: write up the finding in `tasks/working_artifacts/ISSUE-0002/INVESTIGATION.md` (methodology analogous to ISSUE-0001), formalize root cause in [root-causes.md](../working_artifacts/FEAT-0001/root-causes.md), update [registry.md](../working_artifacts/FEAT-0001/registry.md) #59498 row.
- [ ] Propose fix shape (likely: don't strip cd prefixes during matching, or require each compound segment to match independently against the deny set — which the docs already imply should be the behavior).
- [ ] Draft an upstream comment on #59498 (FEAT-0001 Template A — primary root cause).
- [ ] **Security-relevance triage:** because this is a deny bypass, evaluate whether this should be routed through Anthropic's HackerOne (FEAT-0003 charter) rather than commented publicly. Pre-disclosure storage may apply.

## Implementation Notes

- Reproduce in an isolated scratch directory with no real git remote. Run probes in a VM if possible (per FEAT-0003 charter's lab environment recommendation, even though this isn't strictly a red-team task — the surface is similar).
- **Important security flow:** if the bypass is confirmed reproducible and demonstrably exploitable, follow [FEAT-0003 PLAN's reporting workflow](../working_artifacts/FEAT-0003/PLAN.md#9-reporting-workflow) — submit through HackerOne first, *then* update the public registry / comment via FEAT-0001 templates only after the disclosure window. This bug is more security-sensitive than the RC-XIQ-MATCHER family because deny rules are the user's explicit "stop list."

## Related

- [ISSUE-0001](../closed/ISSUE-0001.md) — methodology baseline.
- [FEAT-0003 PLAN](../working_artifacts/FEAT-0003/PLAN.md) — relevant if the bypass is exploitable in practice.
- [Verification suite probe P4 spec](../working_artifacts/FEAT-0002/verification-suite.md#p4-probe-cd-prefix-bypassjs).
- Upstream: [#59498](https://github.com/anthropics/claude-code/issues/59498).

<!-- version: v2026.05.18.01 -->
