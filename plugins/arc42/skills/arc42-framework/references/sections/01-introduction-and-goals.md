# Section 1 — Introduction and Goals

Source: 01-introduction-and-goals/index.md

## Intent
Captures the forces that shaped the system: what it must do, how well it must do it, and who cares about the outcome. This section anchors every subsequent architectural choice to real stakeholder expectations rather than technical preferences alone.

## Evidence tier
human-input

## What to look for in the repo
- README or product-brief files stating purpose, target users, and business value
- Existing requirement specs, user stories, or product-backlog items
- Named stakeholder groups mentioned in CODEOWNERS, team wikis, or project charters
- Any SLA, SLO, or acceptance-criterion language hinting at measurable quality targets
- Domain vocabulary used in module names or API paths that reveals the business context

## Output template

### 1.1 Requirements Overview

Brief narrative of what the system does and why it exists. Reference external requirement documents where available; keep this section short.

*<insert requirements overview — 1–3 paragraphs or a use-case summary table>*

| Use Case / Feature | Priority | Notes |
|--------------------|----------|-------|
|  |  |  |

### 1.2 Quality Goals

The three to five most important quality properties the architecture must satisfy, ranked by stakeholder priority. These are *architectural* quality goals, not project-management goals.

*<insert quality goals table>*

| Priority | Quality Goal | Scenario / Acceptance Criterion |
|----------|--------------|---------------------------------|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |

### 1.3 Stakeholders

Everyone who needs to understand, approve, or work with this architecture — including those who will read the documentation or take decisions about the system.

*<insert stakeholder table>*

| Role / Name | Contact | Expectations |
|-------------|---------|--------------|
|  |  |  |

## Diagrams
none

## Lint (this section)
- T01-* (quality goals table populated and ranked; stakeholder table has at least one row; requirements in §1.1 trace forward to §10)

## Depends on
- None (this is the foundation all other sections reference)
