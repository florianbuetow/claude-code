# Section 4 — Solution Strategy

Source: 04-solution-strategy/index.md

## Intent
Summarizes the handful of pivotal decisions that give the architecture its shape: technology picks, structural decomposition approach, and the choices made to satisfy the key quality goals from §1.2. Think of it as the executive summary of the architectural reasoning — motivation included, implementation detail excluded.

## Evidence tier
code-inferable

## What to look for in the repo
- Technology stack files (runtime versions, framework declarations, major library choices) and any README rationale
- Folder structure and module naming that reveals a chosen architectural pattern (layered, hexagonal, event-driven, microservices, etc.)
- Commit messages, PR descriptions, or ADR files explaining why a technology was selected
- Configuration that signals quality-driven decisions (caching layers → performance; circuit breakers → resilience; auth middleware → security)
- Dependency injection configurations or plugin manifests that reveal structural patterns

## Output template

*<Use the table for decisions that directly address a quality goal; use the bulleted list below for technology and structural decisions>*

| Quality Goal | Scenario | Solution Approach | Details |
|--------------|----------|-------------------|---------|
|  |  |  |  |

**Additional key decisions:**

- Technology stack:
- Top-level structural pattern:
- Organizational / process decisions:

## Diagrams
none — narrative and table only; structural diagrams belong in §5 and §7

## Lint (this section)
- T04-* (each table row traces to a quality goal from §1.2; decisions link forward to §5 or §8 for detail; no implementation specifics here)

## Depends on
- §1.2 (quality goals are the primary input to the strategy)
- §2 (constraints limit the available strategy options)
- §3 (context determines which integration points must be designed for)
