# Unstable Dependency

## Definition

A component depends on other components that are less stable than itself. Stability
here is a structural property defined by the ratio of incoming to outgoing
dependencies — not a subjective judgment about code quality.

## The Stability Metric

**Instability (I)** measures how susceptible a component is to change:

```
I = Ce / (Ca + Ce)
```

Where:
- **Ce (efferent coupling)** = number of outgoing dependencies (components this
  one depends on)
- **Ca (afferent coupling)** = number of incoming dependencies (components that
  depend on this one)

**Range**: 0 to 1
- **I = 0**: Maximally stable. Only incoming dependencies, no outgoing. Changing
  this component would break many dependents, so it resists change.
- **I = 1**: Maximally unstable. Only outgoing dependencies, no dependents.
  Nothing breaks if this component changes, so it can change freely.

## Why It Matters

The **Stable Dependencies Principle (SDP)** states: dependencies should flow in
the direction of stability. A component with many dependents (low I, hard to change)
should not depend on a component with few dependents (high I, easy to change).

When a stable component depends on an unstable one, changes in the volatile
unstable component force changes in the stable component — which in turn forces
changes in everything that depends on the stable component. This creates a ripple
effect that undermines the entire dependency hierarchy.

## Detection Heuristics

**Compute instability for each component:**
1. For each component, count Ca (incoming) and Ce (outgoing) dependencies.
2. Calculate I = Ce / (Ca + Ce).
3. For each dependency edge A → B, check if I(A) < I(B).
   If so, A (more stable) depends on B (less stable) — a violation.

**Practical indicators:**
- A widely-used utility/core module imports from a feature-specific module.
- A shared library depends on application-specific code.
- An infrastructure layer depends on a presentation layer.
- Changing a leaf module triggers cascading changes in foundational modules.

**Scale thresholds (indicative):**

| Instability | Character | Should Contain |
|-------------|-----------|----------------|
| I ≈ 0 | Maximally stable | Abstract interfaces, core contracts |
| I ≈ 0.3 | Mostly stable | Shared services, domain logic |
| I ≈ 0.5 | Balanced | Application services |
| I ≈ 0.7 | Mostly unstable | Feature implementations |
| I ≈ 1 | Maximally unstable | Concrete implementations, adapters |

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Stability gap | Large I difference (stable → very unstable) | Small I difference |
| Dependent count | Stable component has many dependents | Few dependents |
| Change rate | Unstable dependency changes frequently | Rarely changes |
| Abstractness | Stable component is concrete | Stable component is abstract |

## Related: Stable Abstractions Principle (SAP)

Stability and abstractness should be correlated:
- **Stable packages (I ≈ 0)** should be abstract (contain interfaces, abstract classes).
  This makes them stable without being rigid.
- **Unstable packages (I ≈ 1)** should be concrete (contain implementations).
  Their instability allows them to change easily.

A stable, concrete component is the worst combination: hard to change (many
dependents) yet full of implementation details that will need to change.

## Mitigation Strategies

### 1. Increase Stability of the Dependency
Make the frequently-depended-upon component more stable by reducing its own
outgoing dependencies. Move volatile implementation details out of it.

### 2. Introduce an Interface
Have the stable component depend on an abstraction (interface/protocol/trait)
rather than the concrete unstable component. The unstable component implements
the interface. The dependency now points toward an abstraction that is itself
stable.

### 3. Move Dependency Downward
Restructure so the unstable component depends on the stable one, not vice versa.
This may require extracting shared functionality into a lower-level stable
component.

## False Positives

- **Framework dependencies**: Depending on a third-party framework that is
  technically "unstable" (high Ce) but practically stable (mature, well-maintained)
  is usually fine. Evaluate actual change risk, not just the metric.
- **Small projects**: In very small codebases, every component has few dependencies
  and the instability metric becomes noisy. Focus on the dependency direction
  principle rather than exact numeric thresholds.
