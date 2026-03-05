---
name: archibald
version: 1.0.0
description: >
  This skill should be used when the user asks to "assess architecture quality",
  "check for architectural smells", "analyze dependencies", "evaluate technical debt",
  "review architecture health", "find antipatterns", or "measure coupling/cohesion/complexity".
  Also triggers when the user mentions specific concepts by name (e.g., "cyclic dependency",
  "god component", "hub-like dependency", "dependency structure matrix", "DSM",
  "instability metric", "LCOM", "CBO", "Big Ball of Mud", "cargo cult", "golden hammer").
  Supports a full architecture assessment or focused analysis of individual dimensions.
---

# Archibald — Software Architecture Quality Assessment

Assess the structural health of a software architecture through smell detection,
quantitative metrics, antipattern identification, dependency structure evaluation,
risk/trade-off analysis, and technical debt measurement.

This skill operates at the architecture level — components, modules, packages,
services, layers, and their relationships. It complements class-level SOLID checks
and system-level design principle checks by focusing on **observable structural
quality** rather than adherence to specific design principles.

Key insight: architectural smells are independent from code smells (less than 30%
correlation), making dedicated architecture-level assessment essential.

## Subcommands

Request a full assessment or focus on a single dimension:

| Command | Dimension | References |
|---------|-----------|------------|
| `archibald` / `archibald full` | Full assessment (all dimensions) | All references |
| `archibald smells` | Architectural smell detection | `references/cyclic-dependency.md`, `references/unstable-dependency.md`, `references/hub-like-dependency.md`, `references/god-component.md`, `references/feature-concentration.md`, `references/scattered-functionality.md`, `references/ambiguous-interface.md` |
| `archibald antipatterns` | Antipattern identification | `references/antipatterns.md` |
| `archibald metrics` | Quantitative metrics analysis | `references/metrics.md` |
| `archibald dependencies` | Dependency structure analysis | `references/dependency-structure.md` |
| `archibald risks` | Risk & trade-off analysis | `references/risk-analysis.md` |
| `archibald debt` | Technical debt assessment | `references/technical-debt.md` |

When no subcommand is specified, default to a full assessment.
When a specific concept is mentioned by name (e.g., "cyclic dependency", "CBO",
"DSM"), match it to the appropriate dimension and load the relevant references.

## Workflow

### 1. Identify Target Architecture

Determine what to analyze:
- When files or a directory are provided, use those.
- When a service, module, or component is referenced by name, locate it.
- When ambiguous, ask which files, directories, or services to scan.

Before diving in, establish context that affects severity calibration:
- **Project scale**: small app, medium codebase, large platform, distributed system?
- **Team size**: solo developer, small team, multiple teams?
- **Lifecycle stage**: prototype, active development, mature production, legacy?
- **Architecture style**: monolith, modular monolith, microservices, serverless, etc.?

Use whatever context is available from the codebase itself (directory structure,
build files, deployment configs, README) rather than asking unnecessary questions.

### 2. Load References

Before analyzing, read the reference file(s) for the requested dimension(s).

For smell detection, read the individual smell references needed:
- [`references/cyclic-dependency.md`](references/cyclic-dependency.md)
- [`references/unstable-dependency.md`](references/unstable-dependency.md)
- [`references/hub-like-dependency.md`](references/hub-like-dependency.md)
- [`references/god-component.md`](references/god-component.md)
- [`references/feature-concentration.md`](references/feature-concentration.md)
- [`references/scattered-functionality.md`](references/scattered-functionality.md)
- [`references/ambiguous-interface.md`](references/ambiguous-interface.md)

For other dimensions:
- [`references/antipatterns.md`](references/antipatterns.md)
- [`references/metrics.md`](references/metrics.md)
- [`references/dependency-structure.md`](references/dependency-structure.md)
- [`references/risk-analysis.md`](references/risk-analysis.md)
- [`references/technical-debt.md`](references/technical-debt.md)

For a full assessment (`archibald full`), read all twelve reference files.

### 3. Gather Architectural Artifacts

Before applying assessment patterns, build a picture of the current architecture:

**From the codebase:**
- Component/module/package structure (directory layout, build modules)
- Import/dependency graph (who depends on whom)
- Public API surface of each component (exports, interfaces, endpoints)
- Size indicators (approximate LOC per component, class counts)

**From documentation (if available):**
- Architecture diagrams or design documents
- Architecture Decision Records (ADRs)
- Dependency maps or component catalogs
- Quality attribute requirements

**From version control (if available):**
- Files that change together (logical coupling)
- Change frequency per component (hotspots)
- Growth trends over time

### 4. Analyze

Apply the detection heuristics from the loaded references. Each dimension has
its own analysis approach:

- **Smells**: Match structural patterns against the seven smell definitions.
  Check dependency graphs for cycles, compute fan-in/fan-out, assess component
  sizes, evaluate interface clarity, and identify scattered/concentrated features.
- **Antipatterns**: Look for recurring flawed decision patterns — technology
  choices driving architecture, cargo cult adoption, over/under-engineering.
- **Metrics**: Compute or estimate coupling (CBO, Ca, Ce, instability),
  cohesion (LCOM, cohesion type), and complexity (CC, LOC, nesting depth).
  Compare against established thresholds.
- **Dependencies**: Construct a mental or actual DSM. Identify layering patterns,
  cycles, hub components, and problematic backward dependencies.
- **Risks**: Identify architectural decisions with potentially undesirable
  consequences, sensitivity points where small changes have outsized impact,
  and trade-off points where quality attributes conflict.
- **Debt**: Assess accumulated structural problems using the severity/centrality/
  trend framework. Map smells to the prioritization matrix.

Think carefully about each finding. Not every heuristic match is a true problem.
Consider context, scale, team maturity, and conscious trade-offs.

### 5. Report Findings

Present findings using this structure:

#### Per Finding

```
**[DIMENSION] Finding — Severity: CRITICAL | HIGH | MEDIUM | LOW**
Location: `component/module/service`, files or paths involved
Finding: Clear description of the structural issue and why it matters.
Evidence: What observable patterns led to this finding.
Impact: How this affects maintainability, evolvability, reliability, or velocity.
Recommendation: Concrete remediation approach with effort estimate if possible.
```

Severity guidelines:
- **CRITICAL**: Immediate structural risk — cascading failures, complete inability
  to evolve a component independently, or blocking parallel development.
- **HIGH**: Active maintenance pain, significant coupling drag, or measurable
  impact on development velocity.
- **MEDIUM**: Architecture smell that will compound as the system grows or as
  more teams contribute.
- **LOW**: Minor structural impurity, worth noting but fine to defer.

#### Assessment Summary

After all findings, provide:

1. **Findings table**: `| Dimension | CRITICAL | HIGH | MEDIUM | LOW |`

2. **Architecture health score**: Rate each dimension on a simple scale:
   - Smells: HEALTHY / CONCERNING / DEGRADED
   - Metrics: WITHIN THRESHOLDS / APPROACHING LIMITS / EXCEEDING THRESHOLDS
   - Dependencies: CLEAN / TANGLED / CYCLIC
   - Antipatterns: NONE DETECTED / MINOR / SYSTEMIC
   - Risk posture: LOW / MODERATE / HIGH
   - Technical debt: MANAGEABLE / ACCUMULATING / CRITICAL

3. **Top 3 priorities**: Which findings to address first and why, considering
   both impact and effort.

4. **Improvement roadmap**: Categorize all recommendations as:
   - **Critical** — Immediate action required (high-severity risks)
   - **Important** — Address in near term (quality attribute deficiencies)
   - **Beneficial** — Opportunistic improvements (debt reduction)

5. **Overall assessment**: One paragraph synthesizing the architecture's
   structural health, key strengths, and primary risks.

### 6. Remediation Mode (Optional)

When a fix or refactoring is requested, produce concrete remediation proposals:
- For smells: specific refactoring steps following the mitigation strategies
  in the smell references.
- For antipatterns: architectural change proposals with migration approach.
- For metric violations: targeted interventions to bring metrics within thresholds.
- For dependency issues: restructuring proposals with before/after dependency maps.
- For debt: a prioritized backlog of remediation work items.

Use incremental approaches (Strangler Fig, Façade pattern) for large-scale changes
rather than proposing big-bang rewrites.

## Pragmatism Guidelines

These are diagnostic findings, not mandates. Apply judgment:

- **Scale calibration**: A weekend project doesn't need the same structural rigor
  as a platform serving millions. Adjust severity to match the context.
- **Conscious trade-offs**: Some structural impurities are deliberate. When
  rationale exists (in ADRs, comments, or documentation), acknowledge it.
- **Competing concerns**: Architectural quality attributes have productive
  tensions — loose coupling vs. DRY across service boundaries, simplicity vs.
  resilience patterns, YAGNI vs. evolvability. Flag the tension and offer
  judgment, not dogma.
- **Trend matters more than snapshot**: A codebase with moderate smells but
  improving trends is healthier than one with few smells but deteriorating.
- **Actionable over exhaustive**: Five findings with clear remediation paths
  beat twenty observations without actionable next steps.
- **No architecture is perfect**: The goal is continuous improvement, not
  theoretical purity. Prioritize findings that deliver the most maintainability
  benefit per unit of remediation effort.

## Example Interactions

**User**: `archibald smells` (with a codebase directory)

**Claude**:
1. Reads all seven smell reference files
2. Maps the component/module structure from the directory
3. Analyzes dependency graphs for cycles, fan-in/fan-out, stability
4. Assesses component sizes, interface clarity, feature distribution
5. Reports findings with locations, severity, evidence, and recommendations
6. Provides summary with health scores and priorities

**User**: `archibald metrics` (with specific files)

**Claude**:
1. Reads `references/metrics.md`
2. Computes or estimates CBO, Ca/Ce, instability, LCOM, CC for target code
3. Compares against established thresholds
4. Reports outliers and threshold violations with severity
5. Provides summary with metric dashboard and refactoring candidates

**User**: `archibald` (full assessment of a project)

**Claude**:
1. Reads all twelve reference files
2. Gathers architectural artifacts from codebase
3. Runs all six dimensions of analysis
4. Reports findings organized by dimension
5. Provides comprehensive summary with health scores, priorities, and roadmap
