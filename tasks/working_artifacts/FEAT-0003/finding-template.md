# Finding Template

Copy-paste skeleton for documenting a security finding. Same rigor as [INVESTIGATION.md](../ISSUE-0001/INVESTIGATION.md) — citation-backed, version-pinned, empirical.

**Storage:** pre-disclosure findings live in the maintainer's private storage location (see [PLAN §7](PLAN.md#7-pre-disclosure-storage)). After Anthropic's disclosure window completes, the finding may be promoted to a public WRITEUP.md under `tasks/working_artifacts/FEAT-0003/findings/<YYYY-MM-DD>-<slug>/`.

---

## Template

```markdown
# <Finding Title>

**Discovered:** YYYY-MM-DD
**Status:** discovered | drafted | submitted | acknowledged | triaged | fixed | disclosed
**Severity:** Critical / High / Medium / Low (with CVSS v3.1 base vector)
**Affected versions:** <claude.exe version range>
**Reporter:** <maintainer-handle>
**Tracking:** internal-ID (e.g., FEAT-0003-F001); HackerOne report ID once submitted

---

## Summary

<One paragraph. What's the bug, what's the impact, who can trigger it?>

## CVSS

`CVSS:3.1/AV:?/AC:?/PR:?/UI:?/S:?/C:?/I:?/A:?`

Base score: X.X

Rationale per metric:
- AV (attack vector): Local (L) — requires local file write to settings.json / hook script / etc.
- AC (attack complexity): Low (L) — well-understood, deterministic
- PR (privileges required): None / Low / High
- UI (user interaction): Required / None
- S (scope): Unchanged / Changed
- C / I / A (confidentiality / integrity / availability impact)

## Prerequisites

What needs to be true before the bug can be triggered:

- e.g., Claude Code running in <mode>
- e.g., settings.json contains <pattern>
- e.g., user has installed a hook at <path>

## Reproduction steps

Reproducible, deterministic. Includes claude.exe version, commands, expected vs actual.

1. Step 1
2. Step 2
3. Step 3

Expected behavior: <what should happen>
Actual behavior: <what happens>

## Evidence

What you observed:

- Binary offsets (`grep -aob`): ...
- Disassembly snippets (`dd | tr`): ...
- Debug log excerpts (`claude --debug "permission,tool"`): ...
- Screenshots: ...
- POC code: link to file in this folder

## Impact assessment

In concrete user-facing terms:

- What can an attacker (per the threat-model actor from charter.md) achieve?
- What's the worst-case scenario?
- How many users are likely affected?
- Is this exploitable in practice or only theoretically?

## Suggested mitigation

What we propose Anthropic do (Anthropic may pick a different approach — this is informational):

- Code change: <specific function / line>
- Config change: <field>
- Documentation change: <doc / section>
- Workaround for users until fix: <if applicable>

## References

- Internal RC mapping: see [../../FEAT-0001/root-causes.md](../../FEAT-0001/root-causes.md) (`RC-...`).
- Related upstream issues: #NNNN, #NNNN
- Anthropic SECURITY.md: https://github.com/anthropics/claude-code/blob/main/SECURITY.md
- Anthropic responsible-disclosure policy: https://www.anthropic.com/responsible-disclosure-policy

## Conflict-of-interest disclosure

Disclosure: I maintain [permission-probe](https://github.com/twbarnes1972/permission-probe), a public GPL-3.0 workaround tool for related Claude Code permission bugs. The repo's [NOTICE.md](https://github.com/twbarnes1972/permission-probe/blob/main/NOTICE.md) grants Anthropic, PBC a standing, irrevocable license to use any of that code under any terms of their choosing, specifically for Claude Code inclusion. This grant is non-financial. I have no other commercial relationship with Anthropic.

## Timeline

| Date | Event |
|---|---|
| YYYY-MM-DD | Discovered |
| YYYY-MM-DD | First repro verified |
| YYYY-MM-DD | Finding drafted |
| YYYY-MM-DD | Submitted to HackerOne (report #NNNN) |
| YYYY-MM-DD | Anthropic acknowledgment |
| YYYY-MM-DD | Anthropic triage / questions |
| YYYY-MM-DD | Fix shipped in claude.exe <version> |
| YYYY-MM-DD | Coordinated disclosure window expires / agreed publication date |
| YYYY-MM-DD | Public writeup posted |

## Post-disclosure publication checklist

Before promoting this finding to a public WRITEUP.md:

- [ ] Anthropic's coordinated disclosure window has expired OR Anthropic has confirmed publication is OK.
- [ ] Fix has been verified via probe suite against the fixed claude.exe version.
- [ ] Writeup contains no Anthropic employee names without permission.
- [ ] Writeup contains no quotes from internal Anthropic correspondence.
- [ ] POC code in the public writeup is minimal — demonstrates the bug, not weaponized.
- [ ] CVE assigned if applicable (Anthropic may handle this).
- [ ] Cross-references added to [root-causes.md](../FEAT-0001/root-causes.md) and [registry.md](../FEAT-0001/registry.md) if relevant.
- [ ] FEAT-0001 Template D (fix-confirmation comment) drafted for the relevant upstream issue thread(s).
```

---

## Pre-disclosure storage rule

Pre-disclosure findings **do not live in this public repo**. They live in the maintainer's private storage per [PLAN §7](PLAN.md#7-pre-disclosure-storage).

`tasks/working_artifacts/FEAT-0003/findings/` in this public repo is reserved for *post-disclosure* writeups. The folder will appear here once the first finding completes its disclosure window.

<!-- version: v2026.05.18.01 -->
