# Cyclic Dependency

## Definition

Two or more architectural components depend on each other directly or indirectly,
forming dependency cycles. Component A depends on B, B depends on C, and C depends
back on A — creating a cycle where none can be understood, tested, or deployed in
isolation.

## Why It Matters

Cyclic dependencies are among the most damaging architectural smells because they
destroy the fundamental benefit of modular decomposition: independent reasoning
about components. When a cycle exists, every component in the cycle is effectively
one monolithic unit — changing any part risks breaking all parts.

## Detection Heuristics

**Import/dependency graph analysis:**
- Build a directed graph of component dependencies (from imports, build files,
  or package manifests).
- Run a cycle detection algorithm (e.g., Tarjan's strongly connected components).
- Any strongly connected component with more than one node is a cycle.

**Dependency Structure Matrix (DSM):**
- In a properly ordered DSM, all dependencies should be below the diagonal
  (forward dependencies). Entries above the diagonal indicate backward
  dependencies — potential cycles.
- Symmetric entries at positions (i,j) and (j,i) confirm a direct cycle.

**Build system signals:**
- Circular dependency warnings or errors from the compiler/linker.
- Inability to build or test a single module in isolation.
- Build order that requires multiple passes.

**Practical indicators:**
- Circular references between packages or modules.
- Cannot reuse a single component without pulling in unrelated components.
- Changes propagate through the entire cycle (modify A, must also modify B and C).
- Difficult to understand module responsibilities in isolation.

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Cycle size | Many components involved | Two tightly related components |
| Cycle depth | Transitive (A→B→C→A) | Direct (A↔B only) |
| Component importance | Core/shared components in cycle | Peripheral components |
| Change frequency | Frequently modified components | Stable, rarely changed code |
| Team boundaries | Cycle spans team ownership | Single team owns all components |

## Violated Principles

- **Acyclic Dependencies Principle (ADP)**: The dependency graph of components
  must be a directed acyclic graph (DAG).
- **Dependency Inversion Principle (DIP)**: High-level modules should not depend
  on low-level modules — both should depend on abstractions.

## Mitigation Strategies

### 1. Extract Shared Dependencies
Create a new lower-level component containing the shared code that both sides
of the cycle need. Both original components depend on the new one, but not on
each other.

**When to use**: The cycle exists because two components share common logic that
was arbitrarily placed in one of them.

### 2. Introduce Abstraction Layer
Define an interface in one component and implement it in the other. The
dependency now points toward the abstraction rather than the concrete
implementation.

**When to use**: One component needs to call back into the other. The callback
can be expressed as an interface/protocol/trait.

### 3. Invert Dependency
Use dependency injection to reverse the relationship. Instead of A calling B
directly, A defines what it needs (an interface) and B is injected at runtime.

**When to use**: The cycle exists because of a runtime callback or notification
pattern that creates a compile-time dependency in the wrong direction.

### 4. Merge Components
If the cycle is tight and justified — the two components are genuinely one
cohesive unit that was artificially split — merge them into a single component.

**When to use**: The components have high cohesion with each other and low
cohesion internally. The split was premature or arbitrary.

## False Positives

- **Test dependencies**: Test code depending on the module under test and vice
  versa (test utilities) is normal and not a true architectural cycle.
- **Interface + implementation in separate packages**: Some languages split
  interfaces and implementations into separate packages that naturally
  reference each other. Check whether the runtime dependency is actually cyclic.
- **Build tool artifacts**: Some build systems report false cycles due to how
  they resolve transitive dependencies.
