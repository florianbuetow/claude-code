# Section 11 — Risks and Technical Debt

Source: 11-risks-and-technical-debt/index.md

## Intent
Catalogs known risks and accumulated technical debt in priority order, giving management and the team a shared view of what could go wrong and what costs have been deferred. The goal is deliberate, informed decision-making about mitigation and refactoring investments rather than surprises late in the project.

## Evidence tier
human-input

## What to look for in the repo
- TODO / FIXME / HACK comments that flag shortcuts taken under time pressure
- Dependency declarations with known CVEs or end-of-life warnings in lockfiles or audit reports
- Deprecated API usage flagged by linters or static analysis tools
- GitHub issues or backlog items tagged as technical debt, cleanup, or architectural risk
- Test-coverage gaps in complex or business-critical modules
- Incomplete or missing error handling in high-traffic code paths

## Output template

*<Order by priority — highest risk or most impactful debt first>*

**Combined view (use when the list is short):**

| Priority | Risk / Debt Item | Impact | Probability | Suggested Mitigation |
|----------|-----------------|--------|-------------|----------------------|
| 1 |  |  |  |  |
| 2 |  |  |  |  |

**Separate tables (use when either list is long):**

**Known Risks**

| Priority | Risk | Impact | Probability | Mitigation |
|----------|------|--------|-------------|------------|
|  |  |  |  |  |

**Technical Debt**

| Priority | Item | Affected Components | Remediation Effort |
|----------|------|--------------------|--------------------|
|  |  |  |  |

## Diagrams
none

## Lint (this section)
- T11-* (items are prioritized; each entry includes impact and at least a direction for mitigation; technical debt items reference the affected components from §5)

## Depends on
- §1 (stakeholder expectations determine what counts as high risk)
- §4 (solution strategy choices may introduce or knowingly accept specific risks)
- §8 (crosscutting concepts that are incompletely implemented generate debt)
- §9 (decisions with acknowledged downsides should appear here as tracked risks)
