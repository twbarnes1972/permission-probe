# Artifacts Convention

Tasks sometimes require supporting files that cannot live inside a single markdown file — SQL scripts, data files, design mockups, meeting notes, spreadsheets, migration scripts, etc. These are stored in companion folders under `tasks/working_artifacts/`.

## Naming convention

The subfolder name **must exactly match** the task ID — same case, same format:

```
tasks/working_artifacts/
  FEAT-0001/          ← correct
  feat-0001/          ← wrong
  FEAT-1/             ← wrong
  FEAT-0001-stuff/    ← wrong
```

## Creating a companion folder

When you need a companion folder for a task, create it with:

```bash
mkdir -p tasks/working_artifacts/FEAT-0001
```

Replace `FEAT-0001` with the exact task ID. That's all — no registration needed.

## What belongs here

| Put here | Keep in task markdown |
|---|---|
| SQL scripts | Decisions and rationale |
| Data files / CSVs | Acceptance criteria |
| Design mockups / images | Links to artifacts |
| Meeting notes | Architecture notes |
| Migration scripts | Dependencies |
| Reference spreadsheets | Summary and context |

## Orchestrator awareness

When the orchestrator spawns an agent for a task, it automatically scans `tasks/working_artifacts/{task-id}/` and lists any files found in the agent's instructions. Agents see what context is available before they start work — no manual wiring needed.

## Git

Commit artifacts alongside task work — they are part of the task record. For files larger than 10MB, use Git LFS rather than committing directly.
