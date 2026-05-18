# FEAT-0003 findings — post-disclosure writeups

This folder holds **post-disclosure** security-research writeups. Each writeup lives in its own dated subfolder following the [finding template](../finding-template.md) format.

## Where pre-disclosure findings live (NOT HERE)

Pre-disclosure findings — work in progress, awaiting Anthropic's coordinated disclosure window — live in the **gitignored** `permission-probe-research/` folder at the repo root. That folder is local-only and never committed. See [permission-probe-research/README.md](../../../../permission-probe-research/README.md) for the convention (note: that file is also gitignored, but lives on the maintainer's workstation).

## What ends up here

Once Anthropic's coordinated disclosure window for a finding has expired (or they've explicitly OK'd publication), the writeup is promoted to this folder. The promotion procedure is documented in [permission-probe-research/README.md](../../../../permission-probe-research/README.md#when-a-finding-completes-disclosure).

## Format per writeup

```
findings/
  <YYYY-MM-DD>-<short-slug>/
    WRITEUP.md          # the public writeup (file renamed from pre-disclosure's FINDING.md)
    repro/              # minimal reproducer (POC code, sanitized of weaponization)
    timeline.md         # dates only: discovered → submitted → fixed → disclosed
```

## Currently published

(None yet — this folder will be empty until the first finding completes disclosure.)

## Status

This folder is structurally ready. The pre-disclosure side (`permission-probe-research/`) is the active work location, gitignored. See [FEAT-0003 PLAN](../PLAN.md) for the full process.
