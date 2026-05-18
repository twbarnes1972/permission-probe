# Instruction Handling Workflow

How to process items listed in [INSTRUCTIONS.md](./INSTRUCTIONS.md).

---

## 1. Read INSTRUCTIONS.md

Review the Items section. For each item, follow step 2.

## 2. Process Each Item

### a. Trivial Task (no questions, can be done immediately)
1. Perform the work.
2. Create a task file in `tasks/closed/` per [task_management.md](./task_management.md).
3. Add entry to `tasks/task_list.md`.
4. Update the Processing table in INSTRUCTIONS.md with the task ID and status `closed`.

### b. Standard Task
1. Assign a task ID using the appropriate prefix from [task_management.md](./task_management.md).
2. Create a task file in `tasks/open/` with:
   - Summary, background, acceptance criteria
   - A **Questions and Answers** section for any Q&A (ask the user, record answers in the task file)
   - Any directives from the item (e.g., "use planning mode") are instructions **for executing the task**, not for the intake step -- include them in the task file as implementation notes
3. Add entry to `tasks/task_list.md`.
4. Update the Processing table in INSTRUCTIONS.md with the task ID and status `created`.

> **Important:** The intake step is only about creating task files. Directives like "use planning mode" or "requires research" are captured in the task file for the session that picks up the task for implementation.

### c. Unclear Item
Prompt the user for clarification with a numbered list:
- First option: your suggested interpretation/action
- Other options as appropriate
- Last option: "type something else"

Then proceed with (a) or (b) based on the answer.

## 3. Track Progress

Update the **Processing** table in INSTRUCTIONS.md after each item is handled. This table serves as a resume point if the session is interrupted. Columns:

| # | Item | Task ID | Status |
|---|------|---------|--------|
| 1 | Short description | FEAT-0001 | created / closed / skipped |

## 4. Finalize

Once all items are processed:
1. Clear the Items section.
2. Move a summary of the batch to the **Completed** section (date + what was processed).
3. Clear the Processing table.
4. Update CLAUDE.md if needed.
5. Commit.
