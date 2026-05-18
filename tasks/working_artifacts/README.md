# Working Artifacts

This directory stores files related to specific tasks that cannot live inside a single markdown file — SQL scripts, design mockups, meeting notes, data files, spreadsheets, etc.

## Convention

Each task gets its own subdirectory named after its task ID:

```
tasks/working_artifacts/
  FEAT-0001/
    design-mockup.png
    db-schema-notes.sql
    meeting-notes-2026-03-24.md
  BUG-0012/
    repro-script.sql
    screenshot.png
```

## Rules

- Subdirectory name **must match** the task ID exactly (e.g., `FEAT-0001/`, not `feat-1/`)
- Commit artifacts alongside your task work — they are part of the task record
- For files > 10MB, consider Git LFS rather than committing directly
- When the task closes, the artifacts stay — they are the audit trail

## Orchestrator awareness

When the orchestrator spawns an agent for a task, it automatically lists any files present in `tasks/working_artifacts/{task-id}/` in the agent's instructions so the agent knows what context is already available.
