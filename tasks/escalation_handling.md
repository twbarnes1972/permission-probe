# Escalation Handling Workflow

How agents write to [ESCALATIONS.md](./ESCALATIONS.md) -- the agent-to-human feedback channel.

Mirrors [instruction_handling.md](./instruction_handling.md) (human -> agent). This workflow is agent -> human.

---

## When to Escalate

Write an escalation when you encounter something that **doesn't block your work** but **needs human awareness or alignment**. Continue working after writing the escalation.

### Escalate

| Situation | Example |
|-----------|---------|
| **Ambiguous spec** -- you made a reasonable assumption | "Spec says 'handle edge case' but doesn't specify behavior. Defaulted to fail-safe." |
| **Design tradeoff** -- you chose one approach over another | "Used keyword routing instead of embedding similarity for matching. Faster but less flexible." |
| **Codebase concern** -- you noticed something that seems wrong or inconsistent | "The config module silently ignores unknown env vars due to permissive parsing." |
| **Spec conflict** -- the task spec contradicts project conventions or existing code | "Task says to add a migration, but the project uses auto-create tables at startup." |
| **Scope creep risk** -- the task touches more than expected | "Implementing this task requires changes to a shared pipeline used by other workers." |
| **Quality feedback** -- the task spec could be improved for future tasks | "Acceptance criteria mix implementation details with behavioral requirements -- harder to verify." |

### Do NOT Escalate (use other mechanisms instead)

| Situation | Use Instead |
|-----------|-------------|
| **Blocked -- need an answer to continue** | `[QUESTION]` protocol in the task spec (pauses the task) |
| **Bug found in existing code** | Fix it if in scope, or create a task in `tasks/open/` |
| **Task is done** | Standard completion workflow and commit |
| **Need to communicate with another agent** | Not supported -- work independently |

---

## How to Write an Escalation

Append an entry to the `## Pending` section of `ESCALATIONS.md`:

```markdown
### [YYYY-MM-DD] TASK-ID: Short description
Context and what you decided or observed. Keep it to 2-4 sentences.
Include what action the human should take: confirm, adjust, review, etc.
```

**Rules:**
- **Date**: Use the current date (absolute, not relative)
- **Task ID**: The task you're working on
- **Be specific**: State what you did, why, and what you need from the human
- **Keep it short**: 2-4 sentences. The human can read the code/task for details
- **Don't block**: Write the escalation and keep working. This is informational, not a gate.

---

## How the Human Processes Escalations

At session start, the human reviews `ESCALATIONS.md`:

1. **Read each pending item**
2. **Act on it**: update task spec, adjust project conventions, create a follow-up task, or acknowledge
3. **Move resolved items** from `## Pending` to `## Resolved` with a date and one-line resolution:

```markdown
## Resolved

### [2026-03-21] FEAT-0053: Scope keyword overlap
**Resolution (2026-03-22):** Confirmed -- keep separate, review after first run.
```

4. **Periodically clear** the `## Resolved` section when it grows long. Git history (`git log -p ESCALATIONS.md`) is the permanent archive.
5. **If a resolution establishes a pattern**, capture it in project conventions or the relevant task spec -- not just in the resolved entry.

---

## Relationship to Other Channels

```
INSTRUCTIONS.md    Human -> Agent     "Do this"           (intake, becomes tasks)
ESCALATIONS.md     Agent -> Human     "Check this"        (feedback, non-blocking)
SESSION.md         Shared context    "Here's where we are" (planning, history)
[QUESTION]         Agent -> Human     "I'm stuck"         (blocks the task)
```

The key distinction: `[QUESTION]` blocks the task and waits for an answer. `ESCALATIONS.md` is fire-and-forget -- the agent continues working. Use `[QUESTION]` only when you genuinely cannot proceed without human input.
