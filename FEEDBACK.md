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

---

## From Human

_(Human-originated feedback about agent behavior, output quality, or process. Agent acknowledges, saves to memory if it's a behavioral pattern, or spawns a task if it's a process gap. Examples: over/under-engineered, output padded or buried the answer, missed an obvious boundary, ignored prior guidance.)_

---

## Resolved

_(Addressed items -- moved here with a short resolution note and date. Periodically pruned; git history is the archive.)_

### [2026-05-18] Velocity + relevant-escalation balance — positive pattern to reinforce

**Original (From Human):** "I feel you have done a very excellent job [of] moving with velocity while raising relevant escalations when necessary."

**Resolution (2026-05-18):** Acknowledged. Routed to memory as a behavioral pattern (per `tasks/feedback_handling.md` §"How Feedback Is Processed") so the validated working balance persists across sessions — fast execution on clear directives, pause-to-surface only when there's a real decision or risk on the table. Memory phrasing surfaced to maintainer before saving.
