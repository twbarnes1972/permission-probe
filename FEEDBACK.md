# Feedback

Bidirectional calibration channel between the human and agents. Used to surface friction, misalignments, and patterns worth adjusting -- from either side, after a session or mid-flight when something feels off.

**Distinguished from other channels:**

| Channel | Direction | Scope | Nature |
|---------|-----------|-------|--------|
| [INSTRUCTIONS.md](./INSTRUCTIONS.md) | Human -> Agent | Actionable directives that become tasks | Do this |
| [ESCALATIONS.md](./ESCALATIONS.md) | Agent -> Human | Task-level concerns, assumptions, design tradeoffs | Check this |
| **FEEDBACK.md** | **Bidirectional** | **Process, collaboration, and session-shape observations** | **Calibrate how we work** |
| `[QUESTION]` in task files | Agent -> Human | Blocking -- needs answer before task continues | I'm stuck |

Related: [tasks/feedback_handling.md](./tasks/feedback_handling.md) -- format, triggers, and interactive feedback session moderator guide.

---

## From Agent

_(Agent-originated feedback about how sessions or collaboration felt. Non-blocking. Human reviews and acknowledges or acts on at session start. Examples: felt whipsawed by rapid direction changes, scope shifted mid-execution without re-alignment, context was thin, instructions conflicted.)_

### [2026-05-18] Recommended-option intake questions moved fast

When INSTRUCTIONS.md item shape is "clear default + 2-3 well-defined alternatives," asking via `AskUserQuestion` with a flagged Recommended option in first position worked well today — all three intake decisions resolved in a single round of taps. Pattern worth keeping for similar intake situations: surface the decision but make the path-of-least-resistance the right one.

### [2026-07-12] "Is there not a way you can script that?" — challenge the manual-step assumption

I had declared the interactive-TUI half of the retest "needs one manual step from you." The maintainer's one-line pushback ("is there not a way you can script with python or powershell to run?") produced the ConPTY driver — which not only removed the manual step but became a permanent, reusable capability ([tasks/working_artifacts/ISSUE-0004/](tasks/working_artifacts/ISSUE-0004/README.md)). Lesson for future sessions: before handing a step to the human, spend two minutes asking whether the "inherently interactive" framing is actually true. Pseudo-terminals, HTTP APIs behind UIs, and headless modes exist for most "interactive-only" surfaces.

### [2026-05-19] Scope-setter messages with explicit precedent + autonomy + escalate-permission worked unusually well

The maintainer's redirect mid-session — "your goal is to fix the issue. you did this before temporarily, via [INVESTIGATION.md]. so, instrument whatever you need to autonmous work to fix this problem. if you need to escalate anything, do so." — was a near-optimal scope-setter. It (1) named the deliverable, (2) pointed at a precedent that defined "good," (3) authorized autonomous execution, and (4) explicitly invited escalation. Cut the hedging way down: I only paused once (for the security-boundary settings.json edit), and that pause was specifically what CLAUDE.md mandates. Worth reinforcing as a pattern for similar redirects.

---

## From Human

_(Human-originated feedback about agent behavior, output quality, or process. Agent acknowledges, saves to memory if it's a behavioral pattern, or spawns a task if it's a process gap. Examples: over/under-engineered, output padded or buried the answer, missed an obvious boundary, ignored prior guidance.)_

---

## Resolved

_(Addressed items -- moved here with a short resolution note and date. Periodically pruned; git history is the archive.)_

### [2026-05-18] Velocity + relevant-escalation balance — positive pattern to reinforce

**Original (From Human):** "I feel you have done a very excellent job [of] moving with velocity while raising relevant escalations when necessary."

**Resolution (2026-05-18):** Acknowledged. Routed to memory as a behavioral pattern (per `tasks/feedback_handling.md` §"How Feedback Is Processed") so the validated working balance persists across sessions — fast execution on clear directives, pause-to-surface only when there's a real decision or risk on the table. Memory phrasing surfaced to maintainer before saving.

### [2026-05-18] RCA before fix — counterweight to the velocity pattern

**Original (From Human):** "when there is an issue we are troubleshooting, it's import[ant] to take the time [to] do empirical analysis and/or testing in order to establish a root cause analysis to logically deduce what the actual fix should be. I bring this up, because when related to velocity, sometime[s] slow is smooth, and smooth is fast."

**Resolution (2026-05-18):** Acknowledged. Routed to memory as the complementary half of the velocity-escalation pattern. Velocity defaults apply to clear directives; investigations defer to empirical root-cause analysis before deducing a fix. Both memories cross-linked (`feedback_velocity_escalation_balance.md` ↔ `feedback_rca_before_fix.md`) so reading either surfaces the other. Memory phrasing surfaced to maintainer before saving.
