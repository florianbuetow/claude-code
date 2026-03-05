# Hub-Like Dependency

## Definition

A component has excessive fan-in (many other components depend on it) or fan-out
(it depends on many other components). The component becomes a central hub in the
dependency graph, creating a structural bottleneck.

## Variations

**Hub (excessive fan-in):** A popular component that many others depend on. Changes
to this component have an outsized blast radius — every dependent must be retested
and potentially modified.

**Bottleneck (excessive fan-out):** A component that depends on many others. It is
fragile because a change in any of its many dependencies may break it. It also
often indicates a component with too many responsibilities.

## Why It Matters

Hub components concentrate risk. A single change to a hub can cascade across the
entire system. They also indicate potential god components or feature concentration,
and they create bottlenecks in parallel development — multiple teams may need to
coordinate changes to the same hub.

## Detection Heuristics

**Fan-in / fan-out counting:**
- Count afferent coupling (Ca) for fan-in and efferent coupling (Ce) for fan-out
  for each component.
- Components with significantly higher Ca or Ce than the median are candidates.

**Indicative thresholds:**

| Metric | Normal | Monitor | Refactoring Candidate |
|--------|--------|---------|----------------------|
| Fan-in (Ca) | 1–10 | 11–20 | 21+ |
| Fan-out (Ce) | 1–8 | 9–15 | 16+ |

These thresholds are context-dependent. A utility library naturally has high fan-in.
The question is whether the fan-in is intentional and the component is appropriately
abstract, or whether it indicates a god component.

**DSM indicators:**
- Hub with high fan-in: a column with many filled cells (many components depend
  on this row's component).
- Bottleneck with high fan-out: a row with many filled cells (this component
  depends on many others).

**Practical indicators:**
- Single component change affects numerous other components.
- High coupling between component and rest of system.
- Component appears in most import chains.
- Merge conflicts concentrate on a small number of files.
- Build times dominated by a single component and its dependents.

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Coupling count | Far above median | Slightly above median |
| Component type | Application logic hub | Utility/infrastructure library |
| Abstractness | Concrete with many dependents | Abstract interface with many dependents |
| Change frequency | Hub changes often | Hub is stable |
| Team impact | Multiple teams blocked by hub | Single team owns hub |

## Mitigation Strategies

### For Excessive Fan-In (Too Popular)

**1. Split into multiple specialized components:**
If the hub serves different purposes for different clients, decompose it by
responsibility. Each client group depends on a smaller, focused component.

**2. Apply Interface Segregation Principle:**
Define narrow interfaces for different client groups. Clients depend on only
the interface they need, reducing effective coupling even if the implementation
remains unified.

**3. Extract utility components:**
If the hub is popular because it contains shared utility functions, extract
those into dedicated utility components organized by concern.

### For Excessive Fan-Out (Too Many Dependencies)

**1. Apply Facade pattern:**
If the component orchestrates many others, introduce a facade that simplifies
the interface to a subset of dependencies. The component depends on the facade
rather than all individual components.

**2. Question responsibilities:**
A component with many dependencies likely has too many responsibilities.
Decompose it by applying Single Responsibility Principle at the component level.

**3. Abstract dependencies:**
Replace concrete dependencies with abstractions where possible. This doesn't
reduce the count but reduces the coupling strength and allows substitution.

## False Positives

- **Intentional infrastructure hubs**: Logging frameworks, dependency injection
  containers, and configuration providers are designed to have high fan-in. Flag
  only if they also contain business logic or are concrete rather than abstract.
- **Entry point components**: Application entry points, API routers, and
  composition roots naturally have high fan-out. This is their job — they wire
  things together. Flag only if they also contain business logic.
- **Small codebases**: In a 5-component system, having 4 dependents isn't
  remarkable. Scale thresholds to project size.
