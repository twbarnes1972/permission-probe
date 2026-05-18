# Task Categories

This project uses the following task ID prefixes:

| Prefix | Meaning |
|--------|---------|
| FEAT | Feature or enhancement |
| BUG | Bug fix |
| INF | Infrastructure |
| GTSK | General maintenance task |
| TST | Test or validation |
| INIT | Initialization and onboarding |
| ISSUE | Issue tracking |
| SES | Session planning |

To add project-specific categories, add a `categories` key to your project config:

```json
{
  "tools": {
    "task-manager": {
      "categories": {
        "DB": "Database schema change or migration",
        "ASP": "ASP Classic refactor or legacy code change"
      }
    }
  }
}
```

Project-level categories merge with (and can override) the defaults above.
