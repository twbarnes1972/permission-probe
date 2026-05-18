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

---

## From Human

_(Human-originated feedback about agent behavior, output quality, or process. Agent acknowledges, saves to memory if it's a behavioral pattern, or spawns a task if it's a process gap. Examples: over/under-engineered, output padded or buried the answer, missed an obvious boundary, ignored prior guidance.)_

---

## Resolved

_(Addressed items -- moved here with a short resolution note and date. Periodically pruned; git history is the archive.)_
