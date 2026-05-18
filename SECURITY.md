# Security Policy

This repo (`permission-probe`) is a small open-source workaround tool for Claude Code permission bugs. It contains roughly two things: a PreToolUse hook (`app-src/py-helpers/file-deny-guard.py`) and a diagnostic probe (`app-src/js-probes/probe.js`). This file explains where to send security reports.

## Reporting a vulnerability in **Claude Code itself**

If your finding is a vulnerability in Claude Code (`claude.exe`, the `@anthropic-ai/claude-code` npm package, Anthropic's permission system, hooks, MCP, settings.json processing, etc.) — **report it directly to Anthropic, not here.** This repo's maintainer is not on Anthropic's security team and cannot triage Claude Code vulnerabilities.

Anthropic's published channel:

- **HackerOne (primary):** [https://github.com/anthropics/claude-code/blob/main/SECURITY.md](https://github.com/anthropics/claude-code/blob/main/SECURITY.md) — the SECURITY.md in `anthropics/claude-code` links to the submission form.
- **Programs:** [hackerone.com/anthropic](https://hackerone.com/anthropic) (paid bounty), [hackerone.com/anthropic-vdp](https://hackerone.com/anthropic-vdp) (vulnerability disclosure, non-paid).
- **Policy questions / scope clarification:** `disclosure@anthropic.com`.
- **Model safety / jailbreaks (different team):** `usersafety@anthropic.com`.
- **Full policy:** [anthropic.com/responsible-disclosure-policy](https://www.anthropic.com/responsible-disclosure-policy).
- **Acknowledgment SLA:** 3 business days per Anthropic's policy.

## Reporting a vulnerability in **this repo's own code**

If your finding is in this repo's own code — the hook script, the probe, or the build/install instructions in the README — **a regular GitHub issue or pull request is fine.** The attack surface here is small:

- `app-src/py-helpers/file-deny-guard.py` runs as a PreToolUse hook on the maintainer's machine. Findings could include: deny-pattern bypasses, ReDoS in the regex pattern compilation, JSON parsing edge cases that fail-closed in destructive ways, etc.
- `app-src/js-probes/probe.js` reads the user's `~/.claude/settings.json` as a diagnostic. Findings could include: path-traversal in pattern parsing, settings-file disclosure, etc.
- The README's installation instructions — if there's a way to follow them and end up with an insecure setup that isn't obvious, please flag it.

**How to report:**

1. **Default channel:** open a GitHub issue at [twbarnes1972/permission-probe/issues](https://github.com/twbarnes1972/permission-probe/issues). Label it `security` if you have permission to label.
2. **For findings that need pre-disclosure handling:** open a GitHub security advisory at [twbarnes1972/permission-probe/security/advisories](https://github.com/twbarnes1972/permission-probe/security/advisories/new) — this is private to repo collaborators until published.
3. **For anything that can't go through GitHub:** the maintainer's GitHub handle is `twbarnes1972`; reach out via the GitHub profile.

I will acknowledge within ~7 days (no SLA — this is a hobbyist repo, not a vendor). If the issue is in *this* repo and reasonable, I'll fix it. If it's in Claude Code itself, I'll redirect you to Anthropic's channel above.

## Scope clarification — what is *not* covered

- **Vulnerabilities in Claude Code** — see Anthropic's channel above.
- **Vulnerabilities in `picomatch`** (this repo's only runtime dependency) — report directly to [micromatch/picomatch](https://github.com/micromatch/picomatch).
- **Theoretical exploits against the maintainer's personal infrastructure** — not in scope here.
- **DoS / availability** of this repo (it's just files on GitHub; not a service).

## Research conducted under this repo

This repo's maintainer also conducts security research on the locally-installed Claude Code under the [FEAT-0003 charter](tasks/working_artifacts/FEAT-0003/charter.md), which is bound by hard ethical constraints:

1. Testing happens only against the maintainer's own local installations.
2. No public disclosure of Claude Code findings before Anthropic's coordinated disclosure window completes.
3. No weaponization of POCs.
4. No adversarial activity against any party.

If you'd like to collaborate on Claude Code security research using the methodology in [INVESTIGATION.md](tasks/working_artifacts/ISSUE-0001/INVESTIGATION.md), please open a GitHub issue first to discuss scope — independent collaboration must follow the same rules of engagement.

## Standing license context

This repo's [NOTICE.md](NOTICE.md) grants Anthropic, PBC a standing, irrevocable license to use the code under any terms specifically for Claude Code inclusion. This grant is non-financial. The repo is GPL-3.0 for everyone else. This context is included in every report the maintainer submits to Anthropic per [FEAT-0003 charter §Conflict-of-interest disclosure](tasks/working_artifacts/FEAT-0003/charter.md#conflict-of-interest-disclosure-mandatory).
