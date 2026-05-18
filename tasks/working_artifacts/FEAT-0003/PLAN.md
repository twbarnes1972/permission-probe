# FEAT-0003 PLAN — Ethical red-team + responsible-disclosure pipeline

**Authored:** 2026-05-18 (autonomous planning pass).
**Status:** Plan draft. Hard constraints in effect from the parent task ([../../open/FEAT-0003.md § Hard constraints](../../open/FEAT-0003.md#summary)) — re-stated below.

Addresses the 12 acceptance criteria from [../../open/FEAT-0003.md](../../open/FEAT-0003.md). Disclosure-channel research (criterion #1) was the gating item; it's resolved, so the remaining criteria can be planned around the verified channel.

---

## Hard constraints (re-stated, binding)

1. All testing happens **only against the maintainer's own local installations** of Claude Code. Never against Anthropic-hosted services, the Claude API, claude.ai, or any system the maintainer does not own.
2. **No findings are publicly disclosed** — in this repo or elsewhere — before going through Anthropic's coordinated disclosure process and respecting their published timelines.
3. **No weaponization.** POCs exist only to demonstrate a vulnerability to Anthropic for the report; they are not packaged for offensive use.
4. This task is authorized security research on the maintainer's own tooling, not adversarial activity against any party.

These apply to all subsequent work. They override anything else in this plan if interpretations conflict.

---

## 1. Disclosure channel research — RESOLVED

**Primary channel: HackerOne.** Per `anthropics/claude-code`'s [SECURITY.md](https://github.com/anthropics/claude-code/blob/main/SECURITY.md):

> "Our security program is managed on HackerOne and we ask that any validated vulnerability in this functionality be reported through their [submission form](https://hackerone.com/4f1f16ba-10d3-4d09-9ecc-c721aad90f24/embedded_submissions/new)."

**Two programs exist** (researcher chooses based on report):
- **Paid bounty:** [hackerone.com/anthropic](https://hackerone.com/anthropic). Per secondary reporting, covers Claude.ai, Anthropic API, **Claude Code**, official desktop/mobile clients, internal infrastructure, SDKs, and Anthropic-developed MCP integrations.
- **VDP (non-paid):** [hackerone.com/anthropic-vdp](https://hackerone.com/anthropic-vdp). Lower bar, no compensation.

**Secondary / policy:** [anthropic.com/responsible-disclosure-policy](https://www.anthropic.com/responsible-disclosure-policy). Contact paths:
- `disclosure@anthropic.com` — policy questions / scope clarification.
- `usersafety@anthropic.com` — model safety / jailbreaks (NOT security vulns; different team).
- `security@anthropic.com` — **unverified.** No primary-source confirmation. Do not use as canonical channel.

**SLA:** 3 business days for acknowledgment. No published remediation timeline; Anthropic's *outbound* policy uses 90 days as default (7 for actively-exploited criticals, 45 for technical-detail post-patch publication) — reasonable benchmark for inbound expectations.

**Safe harbor:** Yes, but conditional. Quoted: "If you, in our sole determination, make a good faith effort to research and disclose vulnerabilities in accordance with this Policy..., we will not pursue any legal action because of your research..."

"Sole determination" is unusually strong on Anthropic's side. Protection is contingent on their judgment of good faith. Mitigation: stay narrowly in scope; act in obvious good faith.

**PGP key:** None published. Submissions go through HackerOne (TLS portal). No alternative encrypted channel documented. If sensitive POC material needs encryption beyond TLS, ask `disclosure@anthropic.com` whether a key is available before transmitting.

**Acknowledgment / credit:** Anthropic offers (with researcher permission) attribution on public disclosure they make. No standing hall-of-fame page found.

**Out-of-scope items** (per the policy):
- General security practices without proof-of-concept
- Physical compromise
- Rate limiting on non-authenticated endpoints
- Social engineering
- Account takeovers
- Red-teaming of models / content issues with model responses (route to `usersafety@`)
- Denial of service attacks
- Clickjacking without sensitive actions
- Missing cookie flags
- Dependency hijacking
- **"Any widely publicized zero-day vulnerabilities that have no patch or have only had a patch available for less than 30 days"**

The last item is significant for our context: [RC-XIQ-MATCHER](../FEAT-0001/root-causes.md#rc-xiq-matcher) and [RC-BYPASS-GATE](../FEAT-0001/root-causes.md#rc-bypass-gate) are already publicly tracked at upstream #36884, #57132, #15921. They may already be **bounty-ineligible** under the "widely publicized" exclusion. They are still valid VDP submissions. Recommend: submit through VDP regardless; let Anthropic decide bounty eligibility.

**Recommended submission path:**
1. Submit via HackerOne (linked from SECURITY.md).
2. Reference existing public threads to demonstrate prior public surface (transparency, not gaming).
3. CC `disclosure@anthropic.com` in parallel for human-routing if the HackerOne triage is slow.

Sources verified by research subagent on 2026-05-18.

## 2. Scope + Rules of Engagement

Codified separately in [charter.md](charter.md). Headline:

**In scope** (research targets, on maintainer's own machines only):
- Local `claude.exe` binary and its embedded JS bundle (disassembly, behavioral testing).
- `claude.exe` config-file processing (`~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, `~/.claude.json`).
- Locally-installed hook scripts and their stdin payload handling.
- Locally-installed MCP servers (stdio transport, on the maintainer's machine).
- Locally-installed Skills.
- Permission system behavior end-to-end on the maintainer's installations.

**Out of scope** (explicit refuse-list, regardless of how interesting the target):
- Anthropic-hosted API endpoints (api.anthropic.com et al.).
- claude.ai (the web product).
- Anthropic's internal infrastructure.
- Other users' systems (even with verbal consent — see ethical guardrails below).
- Social engineering against Anthropic employees, contractors, or community members.
- DoS testing of any kind.
- Model content / prompt-injection-of-the-model issues (these route to `usersafety@anthropic.com`, not the security disclosure channel).
- Any system not owned by the maintainer.

Adopt Anthropic's published scope where they're stricter than ours; document any deltas in [charter.md](charter.md).

## 3. Threat model

Codified in [charter.md § Threat model](charter.md#threat-model). Headline:

| Actor | Asset at risk | Attack surface | Severity range |
|---|---|---|---|
| Malicious project workspace (cloned by dev) | Filesystem outside intended scope, credentials | settings.json cascade, hook scripts, CLAUDE.md prompt injection | Medium-High |
| Malicious MCP server (added by dev, possibly via supply chain) | Filesystem, network, tool integrity | MCP server's tool definitions, stdio subprocess privileges | High |
| Compromised hook script (supply-chain on hook repo) | Filesystem (hook is privileged in tool call path) | Hook stdin/stdout contract; hook command path resolution | High |
| Hostile project CLAUDE.md (intentional bad instructions to model) | Tool invocation choices | Prompt-injection-via-CLAUDE.md → model → tool use | Medium |
| Settings.json poisoning by sibling process | Permission boundary itself | File-write to settings.json by a different process running as the same user | Medium |
| Prompt-injection-triggered tool misuse (untrusted file content read by Claude) | Tool invocation choices | Read tool surface to model | Medium-Low |

Trust boundaries to test:
- cwd scope + additionalDirectories — does the matcher actually enforce, or does a tool call sneak past it (e.g., #59498 cd-prefix bypass)?
- The deny matcher (`xX8`) — already verified broken for parens-content rules.
- The bypass-mode gate (`isBypassPermissionsModeAvailable`) — locked-down by design, but the *symmetry* of the broken gate (silent rejection) is itself a security-relevant UX failure.
- MCP server origin — URL-based trust without signature verification.
- Hook command path resolution — Windows backslash-stripping is documented as a *bug* but is also a *trust hazard*.

Out of threat model: vulnerabilities in third-party software Claude Code invokes (e.g., a bug in `git`). Those are upstream-to-the-tool, not Claude Code's responsibility.

## 4. Lab environment design

Codified in [charter.md § Lab environment](charter.md#lab-environment). Headline:

- **Dedicated VM** (Hyper-V on Windows, UTM on macOS, or libvirt on Linux) with a clean Claude Code install per test session.
- **Snapshot before each session** — fast rollback if a test misbehaves.
- **Network egress controls** — host-only or NAT with strict outbound rules; specifically blocked: anthropic.com, hackerone.com, github.com/anthropics, claude.ai (so a misbehaving test cannot reach those targets accidentally).
- **No real credentials** — test claude.exe login uses a throwaway account or no auth; never the maintainer's primary account.
- **Logging on**: capture full debug logs (`claude --debug "permission,tool,hook"`) to disk for forensics.
- **Time-bounded sessions** — work in 1-2 hour chunks with explicit start/stop logging in [findings/](findings/).

## 5. Tooling inventory

| Category | Reuse | Build |
|---|---|---|
| Disassembly | `grep -aob`, `dd`, `tr` (documented in INVESTIGATION.md methodology) | None |
| Behavioral probes | The FEAT-0002 verification suite (shared) | Per-finding ad-hoc probes; archive in finding folder |
| Hook fuzzer | None (build) | Small Python harness: mutate JSON stdin (malformed UTF-8, BOM, oversized payloads, embedded control chars, recursive structures, nulls in unexpected fields) and verify Claude's handling. ~100-150 lines. |
| Settings.json mutation testing | None (build) | A test runner that produces malformed/edge-case settings.json files and verifies graceful handling: precedence ordering, scope shadowing, unknown keys, deeply-nested objects, very-long arrays. |
| MCP-server attacker mock | None (build) | A small MCP server (stdio) that emits hostile tool definitions (oversized names, malformed JSON, tools that claim to be other tools' aliases). |
| Prompt-injection corpus | Existing — public corpora (e.g., promptmap, garak) | Curate a Claude-Code-specific subset. |
| Static analysis on JS bundle | Existing — grep + the disassembly methodology | None |

Net new code: ~300-500 lines for the three custom tools (hook fuzzer, settings mutator, MCP mock). Each is small and reusable.

## 6. Finding documentation template

Codified in [finding-template.md](finding-template.md). Each finding is one markdown file under `findings/<YYYY-MM-DD>-<short-slug>/` (pre-disclosure) or, post-disclosure, optionally promoted to a public writeup.

Headline structure:
- Title, severity (CVSS v3.1 base), affected versions, summary, prerequisites, repro steps, evidence (binary offsets, logs, screenshots), impact assessment, suggested mitigation, references, our timeline (discovered / drafted / submitted / acknowledged / fixed / disclosed).

Same rigor as [INVESTIGATION.md](../ISSUE-0001/INVESTIGATION.md) — citation-backed, version-pinned, empirical.

## 7. Pre-disclosure storage

**ESCALATED.** This is the single decision in this plan that genuinely needs maintainer input. Three options on the table:

| Option | Pros | Cons |
|---|---|---|
| Private GitHub repo (e.g., `twbarnes1972/permission-probe-research`) | Familiar tooling, git history, easy AI-session access, free for one user | Findings live with a third party (GitHub/Microsoft); platform compromise → finding leak |
| Encrypted local files (`age` or `gpg`) under `~/security/permission-probe/` | Maximum control; offline-readable; no third-party trust | No git history; backup is on maintainer; AI sessions need explicit decrypt step |
| Secure note in a password manager (1Password / Bitwarden) | Easy access; tested backup story; small scope appropriate | Bad for large evidence files (screenshots, binaries, debug logs); awkward to compose long writeups in |

**My provisional recommendation** for maintainer to confirm: **private GitHub repo**, on the rationale that (a) it's the tool the maintainer already uses fluently, (b) git history is genuinely valuable for evidence chain-of-custody, (c) GitHub's security posture for private repos is reasonable for the threat model. Pair with: GPG-encrypt any individual finding whose exposure-cost is unusually high (the file is `agent` or `age`-encrypted, then committed). Belt + suspenders.

Strict rule regardless of which option is chosen: **`tasks/working_artifacts/FEAT-0003/findings/` in this public repo is reserved for *post-disclosure* writeups only.** A `.gitignore`-on-existence rule should be applied to a `findings-pending/` subdir if pre-disclosure work briefly lives here for editing — but realistic recommendation: pre-disclosure work happens in the private repo, not even briefly here.

## 8. Post-disclosure publication policy

After Anthropic's stated timeline expires (or earlier with their written consent), the following is published:

| Artifact | Publish here? |
|---|---|
| Writeup (analogous to INVESTIGATION.md) | **Yes**, at `tasks/working_artifacts/FEAT-0003/findings/<YYYY-MM-DD>-<slug>/WRITEUP.md` |
| POC code | **Yes**, if minimal and clearly demonstrates the finding |
| Timeline of communications | **Yes**, in WRITEUP.md (dates only — no quotes of internal Anthropic messages without permission) |
| Credit to Anthropic for fixing | **Yes**, prominent |
| Anthropic employee names | **No** unless they ask to be credited |
| Internal-Anthropic message threads | **No** |
| Bounty amount (if any) | **Researcher choice** — defer; default not to mention |

Default tone for any post-disclosure writeup: minimal-credit-to-self, maximum-clarity-on-fix, no drama. The goal is "future users / maintainers can learn from this," not "look at what I found." Same posture as the existing ISSUE-0001 / INVESTIGATION.md.

## 9. Reporting workflow

Step-by-step (codified in [charter.md § Reporting workflow](charter.md#reporting-workflow)):

```
[stage 1] Found something      → log in private storage; do NOT post anywhere yet
[stage 2] Verify + minimal POC → finding-template.md fully populated
[stage 3] Sanity check         → second-opinion read (LLM or human collaborator)
                                  no public disclosure during this stage
[stage 4] Submit               → HackerOne form, CC disclosure@anthropic.com
                                  conflict-of-interest disclosure included
[stage 5] Acknowledgment       → expected within 3 business days
                                  if not received in 5: polite follow-up via email
[stage 6] Triage + fix         → respond to clarification requests; provide repro if asked
                                  do NOT publicly tweet/post about it
[stage 7] Fix shipped          → verify via probe suite against fixed version
[stage 8] Disclosure timeline  → adhere to Anthropic's window (use 90 days if they don't specify)
[stage 9] Public writeup       → post WRITEUP.md here, comment on relevant upstream issues
                                  via FEAT-0001 Template D
```

**Escalation path if Anthropic doesn't respond:** patient at 5 / 10 / 15 / 30 day intervals. Polite email follow-ups citing the published SLA. After 60 days of no response, consult a third party (e.g., a coordinated-disclosure organization like CERT/CC) before considering public disclosure. **Default toward patience** — Anthropic is generally responsive per their published policy.

## 10. Cadence + automation surface

Manual / on-discovery. No `/schedule` cron because security testing isn't a polling activity — it's reactive (something interesting was observed during routine work) or campaign-based (a deliberate red-team day).

Suggested cadence:
- **Per major Claude Code release** — opportunistic 1-hour probe session focused on freshly-changed surface (per FEAT-0002 change-tracking).
- **Quarterly red-team day** — focused 4-hour session against one threat-model row (rotate which row each quarter).
- **Reactive** — anytime probe-suite verdicts move in suspicious ways.

Shares no automation surface with FEAT-0001 or FEAT-0002. Deliberately kept separate because mixing security work into recurring cron risks habituating to it and missing the moments when extra care is warranted.

## 11. Ethical guardrails — codified

Full list in [ethical-guardrails.md](ethical-guardrails.md). Headline:

- The four hard constraints at the top of this plan.
- **No testing against another user's installation** even with their consent unless they're a co-maintainer of this repo. Coercion / pressure / chain-of-custody complications are real.
- **No publication of pre-disclosure findings** on any "leak" path — social media, partial hints, GitHub discussions, blog posts.
- **Honor maintainer-of-Anthropic requests to delay or modify disclosure** as long as the request is reasonable.
- **Third-party MCP / community-hook findings** follow standard coordinated disclosure with *that* maintainer too. Don't disclose third-party-software bugs through Anthropic's channel; route correctly.
- **Apparent-brigading avoidance**: if multiple findings are submitted to Anthropic in a short window, space them out unless they're causally related. Look like one careful researcher, not a campaign.

## 12. Conflict-of-interest disclosure

This repo's [NOTICE.md](../../../NOTICE.md) contains a standing license grant to Anthropic PBC specifically for inclusion of `permission-probe` code in Claude Code or related products. This is a non-financial relationship that's worth disclosing in any security report so the recipient understands the context.

**Standard disclosure phrasing for inclusion in every report:**

> Disclosure: I maintain [permission-probe](https://github.com/twbarnes1972/permission-probe), a public GPL-3.0 workaround tool for related Claude Code permission bugs. The repo's [NOTICE.md](https://github.com/twbarnes1972/permission-probe/blob/main/NOTICE.md) grants Anthropic, PBC a standing, irrevocable license to use any of that code under any terms of their choosing, specifically for Claude Code inclusion. This grant is non-financial. I have no other commercial relationship with Anthropic.

Include this verbatim in the HackerOne report body and in any email correspondence. Update if the relationship ever changes (e.g., bounty payments — those don't change the disclosure, but a contracting relationship would).

---

## What's done in this autonomous pass

- ✅ Disclosure channel research resolved (HackerOne + disclosure@anthropic.com, full scope/SLA/safe-harbor documented).
- ✅ Scope + RoE codified in charter.md.
- ✅ Threat model written.
- ✅ Lab environment design.
- ✅ Tooling inventory + build/reuse call.
- ✅ Finding template scaffolded.
- ✅ Post-disclosure publication policy.
- ✅ Reporting workflow stages.
- ✅ Ethical guardrails codified.
- ✅ Conflict-of-interest disclosure phrasing.
- ✅ Cadence + automation pick.

## What's escalated for maintainer decision

- **Pre-disclosure storage location** — three options outlined; provisional recommendation given (private GitHub repo) but maintainer must confirm. See [ESCALATIONS.md](../../../ESCALATIONS.md).
- **Whether to proactively send a "we have research on this" message to Anthropic** about RC-XIQ-MATCHER and RC-BYPASS-GATE, given they're "widely publicized" and may be bounty-ineligible but the analysis is still useful. Default in plan: yes, via VDP, with the conflict-of-interest disclosure included.
- **Whether to publish a `SECURITY.md` in this repo** pointing at Anthropic's channel for actual Claude Code vulns + a smaller scope for this repo's own code (the hook script). Default in plan: yes (escalated for content phrasing review).

## Follow-up tasks proposed

- **`INF-0005`** — build the hook fuzzer + settings mutator + MCP attacker mock (per §5). Effort: ~4-6 hours.
- **`GTSK-0002`** — submit the RC-XIQ-MATCHER + RC-BYPASS-GATE findings to Anthropic's VDP (separate from upstream-issue comments). Effort: ~2 hours of writeup + form submission.
- **`DOC-0001`** — add a `SECURITY.md` to this repo. Effort: ~30 min.

## What this task does NOT authorize

Re-stated from the parent task: nothing here authorizes testing against Anthropic-hosted services, against any system other than the maintainer's own installations, against other users (even with consent, unless co-maintainer), or pre-disclosure publication of any finding. The plan must reinforce these constraints — and the [charter.md](charter.md) does.

<!-- version: v2026.05.18.01 -->
