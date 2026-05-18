# Feedback Handling Workflow

How both humans and agents write to [FEEDBACK.md](../FEEDBACK.md) -- the bidirectional calibration channel. Mirrors [instruction_handling.md](./instruction_handling.md) and [escalation_handling.md](./escalation_handling.md) in structure.

---

## When to Write Feedback

Feedback is for **process and collaboration** observations -- how we worked, not what we produced. It is non-blocking. Write it when something felt off, or when something went unusually well and is worth reinforcing.

### Agent writes feedback when:

| Situation | Example |
|-----------|---------|
| **Whipsawed** -- rapid direction changes without a clear reason | "Scope shifted three times in Phase 3 without an explicit decision; hard to keep the session file coherent." |
| **Execute-before-align** -- asked to implement before scope was settled | "Told to 'just proceed' on Q2 before I had clarity on the underlying constraint. Defaulted reasonably but flagged the guess." |
| **Thin context** -- had to infer who/why/constraints | "Task referenced a stakeholder I had no file for. Inferred from repo history; confirm." |
| **Conflicting instructions** -- guidance contradicts prior guidance or a memory | "Memory says 'cut to 3 items when board is light' but user asked for 5. Went with 5, worth reconciling." |
| **Framing nit** -- user phrasing hinted I was drifting toward the wrong answer | "User asked 'based on which doc?' -- caught that I'd framed a prescribed choice as a recommendation." |

### Human writes feedback when:

| Situation | Example |
|-----------|---------|
| **Over- or under-engineered** | "Five task files for intra-session work was ceremony; consider a fast-lane." |
| **Padded output** -- answer buried in scaffolding | "Third paragraph had the decision; first two were setup." |
| **Missed boundary** -- agent reached beyond its scope | "You created a task file in another repo from this session. Pointer-issue pattern instead." |
| **Ignored prior guidance** -- drift from a memory or established pattern | "Saved feedback says terse responses; this one had headers and summaries." |
| **Positive pattern** -- reinforce what worked | "Stopping to check the scoping doc before recommending was the right call." |

### Do NOT use FEEDBACK.md for:

| Situation | Use Instead |
|-----------|-------------|
| **Blocking question** -- can't proceed without an answer | `[QUESTION]` in task file |
| **Task-level concern** -- scope or convention issue within a specific task | ESCALATIONS.md |
| **New work request** -- something should get done | INSTRUCTIONS.md |
| **Code bug or doc error** -- fix it or file a task | Fix in-scope or create task in `tasks/open/` |

---

## How to Write an Entry

Append to the appropriate section of FEEDBACK.md (`## From Agent` or `## From Human`):

```markdown
### [YYYY-MM-DD] Short topic
Context and what felt off (or what worked). 2-4 sentences.
Suggest what adjustment would help, if any.
```

**Rules:**
- **Date**: Absolute date (not "today" or "last session")
- **Short topic**: scan-able in a list
- **Specific**: name the behavior or moment, not a vague vibe
- **Short**: 2-4 sentences. Git history preserves detail if needed
- **Non-blocking**: write it and keep working
- **Positive feedback is welcome** -- reinforcing what worked keeps the calibration channel honest, not just a complaint box

---

## How Feedback Is Processed

Feedback routes to one of four outcomes based on what it is:

| Outcome | When | How |
|---------|------|-----|
| **Memory** | Behavioral pattern worth persisting across sessions | Save to `~/.claude/projects/.../memory/` as a feedback memory; index it in `MEMORY.md` |
| **Task** | Process gap that needs a concrete change (doc update, hook, skill edit) | Create a task in `tasks/open/` (usually PROC, DOC, or GTSK); link from the FEEDBACK.md entry |
| **Conversation** | Needs discussion to shape, not a mechanical fix | Raise it at the start of the next session or during a Strategic session |
| **Acknowledged** | One-off friction, no durable pattern | Move the entry to `## Resolved` with a one-line ack |

At session start, review `## From Agent` and `## From Human`. Route each pending item. Move resolved items to `## Resolved` with a date and short resolution.

```markdown
## Resolved

### [YYYY-MM-DD] Short topic
**Resolution (YYYY-MM-DD):** One-line note on how it was handled. Link to task ID or memory filename if applicable.
```

Periodically prune `## Resolved` when it grows long -- git history is the permanent archive.

---

## Interactive Feedback Session

A **Feedback Session** is a short, structured retrospective -- separate from standard execution sessions. Run one when feedback has been accumulating, when something recent felt significantly off, or as a periodic calibration (quarterly-ish). Designed to take 15-30 minutes.

### Triggers

- Three or more pending items in `## From Agent` or `## From Human`
- A recent session that felt bad to either side (even if not written up)
- Before or after a major project pivot -- calibrate the operating model
- Scheduled cadence (e.g., end-of-month, end-of-milestone)

### Agent Moderator Guide

The agent moderates. The human is the primary speaker; the agent is the scribe and prompter.

**Phase 1 -- Frame (2 min)**
- State the purpose: "This is a feedback session, not an execution session. Output is calibration."
- Confirm mode: full retrospective, or focused on one specific theme?
- Agree on timebox (15/30 min).

**Phase 2 -- Read Pending Feedback (5 min)**
- Read out `## From Agent` and `## From Human` entries one at a time.
- For each, ask: *"Still relevant? Resolution clear, or does this need discussion?"*
- Move obviously-settled items to `## Resolved` immediately.

**Phase 3 -- Open Floor (Bulk of session)**
- Prompt the human first: *"Anything about how we've been working that you'd change? Anything that's working that I should keep doing?"*
- Agent adds any fresh items that emerged since last written (don't pre-stage -- surface in the moment so it's genuine, not rehearsed).
- **Scribe discipline:** capture each distinct observation as its own entry in FEEDBACK.md as the conversation happens, not after. Read back for accuracy before moving on.

**Phase 4 -- Route (5 min)**
- For each new or unresolved entry, choose outcome: memory, task, conversation, acknowledged (per the table above).
- Create tasks immediately if agreed; note task IDs in the FEEDBACK.md entry.
- Write memories immediately if agreed; note the memory filename.

**Phase 5 -- Close (2 min)**
- Summarize: what changes (concrete), what's staying the same, what's deferred.
- Commit FEEDBACK.md, any new task files, `MEMORY.md` index updates.
- Note the session in SESSION.md or the active session file: "Feedback session held YYYY-MM-DD, N items routed."

### Moderation Rules

- **Don't defend.** When the human raises something about agent behavior, acknowledge before explaining. Curiosity beats justification.
- **Don't soften.** Write what the human actually said, not a polite paraphrase. The entry is a tool, not a diplomatic gesture.
- **Don't batch-update memory silently.** Saving a feedback memory is a decision, not a reflex -- surface it: *"Saving this to memory so I apply it in future sessions. Phrased as: [text]. OK?"*
- **End on balance.** Close with at least one thing that's working, not just a list of changes. The channel needs to stay honest in both directions.

---

## Relationship to Other Channels

```
INSTRUCTIONS.md    Human -> Agent     "Do this"           (intake, becomes tasks)
ESCALATIONS.md     Agent -> Human     "Check this"        (task-level, non-blocking)
FEEDBACK.md        Both ways          "Calibrate us"      (process-level, non-blocking)
SESSION.md         Shared context     "Where we are"      (session notes)
[QUESTION]         Agent -> Human     "I'm stuck"         (blocks the task)
```

Three non-blocking channels (ESCALATIONS, FEEDBACK, SESSION) and two blocking ones (INSTRUCTIONS, `[QUESTION]`). The key distinctions:

- **INSTRUCTIONS.md vs. FEEDBACK.md:** an INSTRUCTION is "do a thing" (becomes a task). Feedback may *lead* to an instruction, but it starts as an observation.
- **ESCALATIONS.md vs. FEEDBACK.md:** an ESCALATION is task-scoped (about a specific piece of work). Feedback is session- or collaboration-scoped (about how we work).
- **SESSION.md vs. FEEDBACK.md:** SESSION is descriptive (what happened). Feedback is prescriptive (what should change).

When in doubt, write it somewhere and reroute later. An entry in the wrong channel is easier to move than an observation that never got written down.
