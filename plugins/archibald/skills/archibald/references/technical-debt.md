# Technical Debt Assessment

## Definition

Technical debt is the implied cost of future rework caused by choosing an expedient
solution now instead of a better approach that would take longer. At the
architectural level, technical debt manifests as structural problems — smells,
antipatterns, metric violations — that increase the cost of every future change.

## Technical Debt Index (TDI)

The TDI quantifies debt severity by considering three factors for each detected
architectural smell:

```
TDI = Σ (centrality × order × trend)
```

Where:
- **Centrality** = the smell's position in the dependency graph, measured by
  PageRank or similar centrality metric. A smell in a central, highly-connected
  component has more impact than one in a peripheral component.
- **Order** = the smell's severity/impact. Maps to the severity ratings from
  smell detection (CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1).
- **Trend** = the smell's growth trajectory. Is it getting worse (+1), stable (0),
  or improving (-1)? This requires historical data; when unavailable, default
  to stable (0) and note the limitation.

Higher TDI indicates more severe, more central, and growing debt that demands
attention.

## Prioritization Framework

Not all debt warrants immediate action. Prioritize using the impact × change
frequency matrix:

| Smell Impact | Change Frequency | Priority |
|-------------|-----------------|----------|
| High | High | **Critical — Immediate** |
| High | Low | **Important — Near term** |
| Low | High | **Important — Near term** |
| Low | Low | **Beneficial — Opportunistic** |

**Rationale**: A severe smell in frequently-changed code is the worst combination —
developers hit it constantly and it slows them down every time. A severe smell in
stable code is important but less urgent. A minor smell in frequently-changed code
matters because developers encounter it often, creating cumulative friction.

## Debt Categories

### Deliberate vs. Inadvertent

**Deliberate debt**: Conscious decisions to take shortcuts with awareness of the
consequences. "We know this isn't ideal, but we need to ship by Friday." This
debt is manageable because it's known, scoped, and can be tracked.

**Inadvertent debt**: Debt created unknowingly due to insufficient design skills,
understanding, or foresight. "We didn't realize this would become a problem."
This debt is more dangerous because it's invisible until it causes pain.

### Architecture-Level Debt Types

1. **Structural debt**: Poor component boundaries, inappropriate dependency
   directions, missing or violated layering. Detected through smells and DSM.
2. **Decision debt**: Architectural decisions that are no longer appropriate for
   current requirements but haven't been revisited. Detected through risk analysis.
3. **Evolution debt**: Failure to evolve the architecture as requirements changed.
   The architecture was right for v1 but not for v3. Detected through scenario
   analysis.
4. **Knowledge debt**: Architecture decisions that aren't documented. The system
   works, but no one fully understands why certain choices were made. Detected
   through missing ADRs, tribal knowledge dependencies.

## Management Strategies

### 1. Repayment through Refactoring

Active debt reduction through planned refactoring work.

**Tactical approaches:**
- Dedicated refactoring sprints focused on specific debt items.
- Allocate 10–15% of sprint capacity to technical debt reduction.
- Track refactoring as first-class work items (not hidden in feature work).
- Measure debt reduction over time to demonstrate progress.

**Strategic approaches:**
- Strangler Fig pattern for incremental migration away from problematic
  architecture.
- Façade pattern for isolating legacy components while refactoring behind
  the interface.
- Branch by abstraction for replacing implementations without disrupting
  consumers.

### 2. Prevention through Quality Practices

Prevent new debt from accumulating.

**Practices:**
- Architecture reviews for major changes (PRs that add new components,
  dependencies, or communication patterns).
- Automated smell detection in CI/CD pipeline (fail or warn on new smells).
- Code review focus on architectural principles (not just code style).
- Architecture Decision Records (ADRs) documenting rationale for decisions.
- Quality gates based on metric thresholds (no merge if CBO > threshold).

### 3. Continuous Monitoring

Track debt levels over time to detect trends.

**Monitoring approaches:**
- Regular metric collection and trend analysis (weekly or per-sprint).
- Smell detection on each commit or PR.
- Quality gates with defined thresholds that alert before problems become severe.
- Architecture health dashboard for visibility across the team/organization.
- Track the ratio of feature work to debt work to maintain balance.

### 4. Balancing Prevention and Remediation

Research suggests a 60/40 to 70/30 split:

**Prevention (60–70% of effort):**
- Write clean code following design principles (SOLID, DRY, YAGNI).
- Design with modularity and low coupling from the start.
- Review architectural impact of changes.
- Maintain architectural documentation.

**Remediation (30–40% of effort):**
- Dedicated refactoring time in each sprint.
- Address high-priority smells and risks.
- Continuous incremental improvement.
- Strategic architectural refactoring initiatives for systemic issues.

## Refactoring Strategies for Architectural Debt

### Substitute Architectural Decision

Replace fundamental architectural choices (database technology, messaging system,
UI framework).

**Approaches:**
- **Leap**: Immediate switch (only for small, low-risk changes).
- **Parallel Change**: Run old and new simultaneously during transition.
- **Stepping Stone**: Create intermediate platform enabling target design.
- **Simplification**: Implement subset now, add complexity incrementally.

### Refactor Architectural Structure

Change component boundaries, dependencies, and organization.

**Techniques:**
- Extract or introduce new component/module.
- Remove or invert dependencies between components.
- Introduce layering or clean up layering violations.
- Address specific architectural smells (cyclic dependencies, god components,
  hub-like dependencies).
- Apply Strangler Fig pattern to gradually replace components.

### Refactor Architectural Style

Widespread changes to architectural patterns and conventions.

**Scenarios:**
- Upgrading major library version with breaking API changes.
- Migrating between similar frameworks.
- Changing or unifying coding conventions.
- Consistently applying cross-cutting concerns (logging, security).
- Adding internationalization support.

**Approach**: Automation through scripts, codemods, or refactoring tools. Even
80% automation provides significant value.

## Façade Pattern for Incremental Refactoring

**Use case**: Tightly coupled legacy components requiring significant restructuring.

**Process:**
1. **Introduce Façade** — Create intermediary interface between callers and legacy
   components.
2. **Redirect Calls** — Update all callers to use Façade instead of direct access.
3. **Refactor Behind Façade** — Incrementally improve legacy components while
   Façade maintains stable interface.
4. **Remove Façade** — Once refactoring is complete, eliminate intermediary and
   update callers to use new components directly.

**Caution**: The Façade is temporary scaffolding. It must be removed after
refactoring to avoid introducing a permanent God Object.

## Strangler Fig Pattern

**Concept**: Incrementally migrate from legacy system to new architecture by
gradually replacing functionality.

**Process:**
1. Identify functionality to migrate.
2. Build new implementation alongside legacy.
3. Route requests to new implementation.
4. Repeat until legacy is completely replaced.
5. Remove legacy code.

**Advantages**: Low risk, incremental value delivery, ability to pause/adjust
during migration.

## Reporting Debt Assessment

When reporting technical debt findings, provide:

1. **Debt inventory**: List of identified debt items with category, severity,
   location, and estimated remediation effort.
2. **TDI score**: Aggregate severity weighted by centrality and trend (if
   historical data available).
3. **Prioritized backlog**: Debt items ordered by the impact × frequency matrix.
4. **Remediation roadmap**: Recommended sequence of refactoring work with
   approach (strangler fig, façade, direct refactoring) for each item.
5. **Prevention recommendations**: Practices and quality gates to prevent
   new debt accumulation.
