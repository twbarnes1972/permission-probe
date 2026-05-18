# Task Management

**Related:**
- [Task Formatting](./task_formatting.md) -- Standard format and category-specific sections
- [Instruction Handling](./instruction_handling.md) -- How tasks are created from INSTRUCTIONS.md
- [Complexity Criteria](./complexity_criteria.md) -- 5-dimension scoring rubric for task complexity

## Task ID Prefixes

| Prefix | Category | Example Use |
|--------|----------|-------------|
| FEAT | Feature | Software Engineering, Feature Requests, Features |
| ISSUE | Issue | Debugging, Error Resolution, Code Fixes |
| INF | Infrastructure | Docker, databases, messaging |
| SVC | Services | Backend APIs and applications |
| WRK | Workers | Background processing workers |
| MON | Monitoring | Prometheus, Grafana, observability |
| FE | Front-End | User interface components |
| TST | Testing | Test framework and integration tests |
| DOC | Documentation | Documentation tasks |
| INIT | Initialization | Project setup tasks |
| GTSK | General Task | All other tasks |

## Dependencies

Every task file must include a `## Dependencies` section with a `| Blocked By |` table row. This is parsed by the dependency analyzer and orchestrator to determine execution order.

```
| Blocked By | SVC-0001, INF-0002 |
```

Use `| Blocked By | None |` when there are no blockers. When creating a new task, review existing open tasks in `tasks/open/` to identify any that must complete first.

## Task Lifecycle

```
tasks/open/[TASK-ID].md  ->  Work in Progress  ->  tasks/closed/[TASK-ID].md
```

## Key Task Files

| File | Purpose |
|------|---------|
| `tasks/task_list.md` | Master index of all tasks (open and closed) |

## Key Task Directories
| Directory| Purpose |
|------|---------|
| `tasks/open/` | Individual open task files |
| `tasks/closed/` | Completed task archive |
