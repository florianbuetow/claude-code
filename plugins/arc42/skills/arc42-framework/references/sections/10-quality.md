# Section 10 — Quality Requirements

Source: 10-quality/index.md

## Intent
Expands the brief quality goals from §1.2 into a complete, measurable set of requirements. Structured scenarios make each requirement verifiable in practice. Lower-priority quality properties that do not warrant a place in §1.2 are also captured here.

## Evidence tier
human-input

## What to look for in the repo
- SLA/SLO definitions in runbooks or infrastructure configurations encoding latency and availability targets
- Performance test scripts or load-test threshold configs that embed measurable acceptance criteria
- Security policy documents specifying authentication, authorization, or data-protection requirements
- Accessibility or compliance checklists in `docs/`
- Existing quality attribute utility trees or Q42 label annotations in any architecture documents

## Output template

### 10.1 Quality Requirements Overview

A summary of all quality requirements grouped by category. Use ISO 25010:2023 categories or Q42 labels (`#reliable`, `#secure`, `#efficient`, `#usable`, `#operable`, `#testable`, `#safe`, `#flexible`) as organizing headings. If these summaries are already specific and measurable, §10.2 may be omitted.

*<table or category summary>*

| Category / Label | Quality Requirement | Priority |
|------------------|--------------------|-|
|  |  |  |

### 10.2 Quality Scenarios

Concrete scenarios that translate each quality requirement into a testable acceptance criterion.

**Short form (Q42 — preferred for most scenarios):**

| Scenario ID | Context | Stimulus | Metric / Acceptance Criterion |
|-------------|---------|----------|-------------------------------|
|  |  |  |  |

**Extended form (SEI / Bass et al. — use for the highest-priority scenarios):**

| Field | Value |
|-------|-------|
| Scenario ID |  |
| Scenario Name |  |
| Source |  |
| Stimulus |  |
| Environment |  |
| Artifact |  |
| Response |  |
| Response Measure |  |

## Diagrams
none — tables are the standard form; a quality attribute utility tree may be rendered as `graph TD` if it aids navigation

## Lint (this section)
- T10-* (§10.1 covers all goals from §1.2; every scenario has a numeric or otherwise verifiable acceptance criterion; scenarios are specific, not generic)

## Depends on
- §1.2 (top quality goals are the primary input; §10 expands them without replacing them)
- §4 (solution choices must demonstrably address the scenarios captured here)
