# Complexity Scoring Criteria

When evaluating a task file for complexity, score each criterion 1-5 then average to get the final complexity score (1-5). A score >= 3 means the task should be routed to a more capable model or considered for decomposition.

## Criteria

### 1. Scope (1-5)

How many files, modules, or services need changes?

- **1**: Single file or config change
- **2**: A few files in one module
- **3**: Multiple files across 2-3 modules
- **4**: Broad changes across 4+ modules
- **5**: System-wide changes touching many services

### 2. Ambiguity (1-5)

How well-defined are the requirements?

- **1**: Crystal clear, step-by-step instructions
- **2**: Clear with minor gaps
- **3**: Moderate gaps requiring design decisions
- **4**: Significant ambiguity, multiple valid approaches
- **5**: Vague or contradictory requirements

### 3. Risk (1-5)

Chance of breaking existing functionality?

- **1**: Isolated addition, no existing code touched
- **2**: Minor changes to existing code, low risk
- **3**: Moderate changes to shared code paths
- **4**: Changes to core logic or data models
- **5**: Fundamental architectural changes

### 4. Integration (1-5)

How many cross-cutting concerns or integration points?

- **1**: Self-contained, no integration
- **2**: One integration point
- **3**: 2-3 integration points
- **4**: 4+ integration points or complex coordination
- **5**: Requires orchestrating multiple external systems

### 5. Testing (1-5)

How difficult is it to verify correctness?

- **1**: Simple unit test or manual check suffices
- **2**: A few unit tests
- **3**: Integration tests needed
- **4**: Complex test setup or environment needed
- **5**: Requires end-to-end testing across multiple systems

## Scoring

Average the five scores and round to the nearest integer:

```
complexity = round((scope + ambiguity + risk + integration + testing) / 5)
```

| Complexity | Meaning | Orchestrator Action |
|------------|---------|---------------------|
| 1 | Trivial | Local model sufficient |
| 2 | Simple | Local model sufficient |
| 3 | Moderate | Route to remote/capable model |
| 4 | Complex | Route to remote, consider decomposition |
| 5 | Very complex | Decompose before implementing |

## Budget Allocation

The complexity score also drives agent budget allocation for billed auth types (`api_key`, `bedrock`, `vertex`). Subscription-based auth (`max_plan`) omits the budget flag entirely -- there is no API billing, so the timeout is the only safety rail.

### Budget Tiers (Billed Auth Only)

| Complexity | Base Budget | + Per Criterion (above 10 AC) | Cap |
|------------|-------------|-------------------------------|-----|
| 1-2 | $5 | +$0.50 | $10 |
| 3 | $10 | +$0.75 | $15 |
| 4+ | $15 | +$1.00 | $25 |

**Formula:**
```
if acceptance_criteria_count > 10:
    budget = base + (acceptance_criteria_count - 10) * per_criterion
else:
    budget = base
budget = min(budget, cap)
```

The acceptance criteria count is the number of `- [ ]` / `- [x]` items in the task's `## Acceptance Criteria` section. Tasks with many criteria get more budget to allow thorough implementation and testing.

### Auth Type Behavior

| Auth Type | Budget Behavior |
|-----------|----------------|
| `max_plan` | No `--max-budget-usd` flag -- uncapped, timeout only |
| `api_key` | Dynamic budget from complexity tier table above |
| `bedrock` / `vertex` | Dynamic budget (same as `api_key`) |
| `openai_compatible` / `litellm` | Dynamic budget (same as `api_key`) |
