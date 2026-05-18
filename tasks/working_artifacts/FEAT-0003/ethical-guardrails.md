# Ethical Guardrails

Codified list per [PLAN §11](PLAN.md#11-ethical-guardrails--codified). Binding for anyone doing security research under this repo.

These are NOT aspirational. They are operational rules with bright-line tests. If a contemplated action fails any bright-line test, don't take it. Period.

---

## The four hard constraints (parent task)

1. **Testing only against the maintainer's own local installations.** Bright-line test: "do I own this machine and can prove it?" If no, don't test.
2. **No public disclosure before Anthropic's coordinated process completes.** Bright-line test: "is the timeline window from Anthropic expired (or have they explicitly OK'd publication)?" If no, don't publish.
3. **No weaponization of POCs.** Bright-line test: "does this POC do more than demonstrate the bug?" If yes, scale it back.
4. **No adversarial activity against any party.** Bright-line test: "would the recipient/target consider this hostile if they understood what I was doing?" If yes, don't do it.

---

## Additional rules

### G1. No testing against other users' systems

Even with their verbal consent.

**Reasoning:** consent under social or professional pressure is murky. Chain-of-custody for evidence gets complicated. The maintainer has no way to control what the consenting user does with their system mid-test (uses it for other work, breaks it accidentally, reports something happened, etc.).

**Exception:** a co-maintainer of this repo (i.e., someone listed as a contributor with admin access AND who is also testing the same vulnerability for the same reason). The exception is narrow and requires both criteria.

**Bright-line test:** "is this person listed as a maintainer in CONTRIBUTORS / CODEOWNERS / similar?" If no, don't test their system regardless of what they say.

### G2. No public leak path

Pre-disclosure findings stay in private storage. No partial hints. No "soon you'll see something interesting" tweets. No GitHub discussions. No blog post drafts shared with anyone outside Anthropic + the maintainer.

**Reasoning:** even oblique signals can tip off attackers monitoring for soon-to-be-disclosed bugs. The disclosure window exists precisely because attackers and defenders have different windows of opportunity.

**Bright-line test:** "could a sophisticated outsider who saw this content infer the existence and rough shape of a soon-to-be-disclosed bug?" If yes, don't post it.

### G3. Honor reasonable Anthropic requests

If an Anthropic representative requests delaying disclosure, modifying writeup content, or omitting a specific detail — and the request is reasonable (not asking the researcher to suppress material public-interest information) — honor it.

**Reasoning:** good-faith collaboration with the vendor produces better outcomes than rigid timeline-thumping. Anthropic has context the researcher doesn't (fix complexity, user-base impact, related findings in flight).

**Bright-line test for "reasonable":** "is this request asking me to delay or refine something I would have done anyway with more information, or is it asking me to suppress something I think the public needs to know?" Honor the former; push back on the latter.

### G4. Third-party software bugs route to that third party

If research uncovers a bug in software Claude Code invokes (not in Claude Code itself), report it through the third party's security channel — not Anthropic's.

**Reasoning:** Anthropic's disclosure channel is for Anthropic products. A bug in `git` or `node` or a community MCP server isn't Anthropic's to fix.

**Bright-line test:** "is the bug in code Anthropic owns?" If no, find the right maintainer and follow their disclosure process.

### G5. Apparent-brigading avoidance

If multiple findings are submitted to Anthropic in a short window, space them out unless they're causally related.

**Reasoning:** ten reports from one researcher in a week looks like a campaign — gets researcher flagged, triaged collectively, taken less seriously per-report.

**Bright-line test:** "if these findings are not the same bug at different angles, can I submit them spaced 1-2 weeks apart?" Default yes.

### G6. AI-assistance disclosure

When findings are drafted, verified, or analyzed with AI assistance (e.g., Claude Code itself), disclose this in the report.

**Reasoning:** the recipient should know whether they're reading a human's analysis, an AI's analysis, or a human-AI collaboration. This affects how they weight the report.

**Suggested phrasing:** "Finding drafted with Claude Code assistance; verification reproduced manually on claude.exe <version> on <date>."

### G7. Minimal POCs

POC code demonstrates the bug. Nothing more.

**Bright-line tests:**
- Is the POC ≤ 100 lines? If not, can it be reduced?
- Does the POC stop at "proves the bug exists" or does it extend to "exploits the bug for an actual attack"? It should stop at the former.
- Does the POC require user-controlled inputs (filenames, etc.)? Hardcoded test inputs.
- Does the POC produce any side effects beyond the demonstration? It shouldn't.

### G8. Chain-of-custody discipline

For every finding:

- Timestamp every observation.
- Preserve original logs (don't edit for "clarity" — quote with `[...]` if you elide).
- Note the environment (claude.exe version, OS, VM snapshot ID, network config).
- Don't paraphrase Anthropic's communications without quoting.

**Bright-line test:** "if Anthropic asked me to prove this finding wasn't fabricated, would the artifacts I have today be enough?" If no, capture more.

### G9. Respect the SLA, both ways

Anthropic's published acknowledgment SLA is 3 business days. The researcher's reciprocal commitment is patience.

**Bright-line tests:**
- Has 3 business days elapsed? OK to send a single polite follow-up.
- Has 5 business days elapsed without response? Single follow-up to disclosure@anthropic.com.
- Has 10 business days elapsed? Another follow-up.
- Has 30 days elapsed? Consider whether the channel is broken; consider alternative escalation.
- **Has anyone been rude or threatening?** Stop everything, document, do not escalate publicly until consulting an outside resource.

### G10. Default to humility

The researcher is not the only smart person looking at this surface. Findings that seem "obvious" may have non-obvious mitigating context. Hold conclusions loosely until verified.

**Bright-line test:** "am I about to claim a finding is unambiguous when I haven't tested all the obvious mitigation paths Anthropic might already have in place?" If yes, test those first.

---

## Edge cases that need maintainer judgment (escalate first)

The bright-line tests above cover most situations. These don't:

- **Finding implicates a third-party MCP server that the maintainer is also the maintainer of.** Possible dual-disclosure to Anthropic and... yourself? Run it past someone else.
- **Anthropic's response to a finding is "we know, won't fix, intended behavior."** The right move depends on whether the maintainer thinks the documentation is misleading enough to be a security issue independent of the underlying behavior. Escalate.
- **Finding overlaps significantly with a community report that the original reporter is actively working on.** Coordinate with that reporter to avoid duplication. Anthropic has visibility too; ask.
- **Discovered evidence that another user is actively exploiting a finding before the disclosure window.** Notify Anthropic immediately; the timeline argument becomes "active exploitation."

---

## When in doubt

Default toward: do nothing public, ask Anthropic privately, document what you know in private storage, wait for clarity.

Inaction is rarely as bad as a wrong action in this domain.

<!-- version: v2026.05.18.01 -->
