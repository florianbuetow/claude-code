# Dependency Structure Analysis

## Dependency Structure Matrix (DSM)

A DSM provides a compact, visual representation of dependencies in matrix form.
It scales better than dependency graphs for large systems and highlights
architectural patterns at a glance.

### Structure

- Rows and columns represent components (packages, modules, classes).
- Cell (i,j) contains the number of dependencies from row i to column j.
- The diagonal represents a component's relationship with itself (ignored).
- **Lower triangle** = forward dependencies (expected in well-layered systems).
- **Upper triangle** = backward dependencies (feedback, often problematic).

### Reading a DSM

**Ordering matters**: Components should be ordered so that dependencies flow
downward (lower triangle). A well-ordered DSM has most entries below the
diagonal.

**Row = what this component depends on**: A filled row means this component has
many outgoing dependencies (high fan-out).

**Column = what depends on this component**: A filled column means many components
depend on this one (high fan-in).

### Pattern Detection

**Layering**: Dependencies concentrated below the diagonal indicate clear
architectural layering. Higher-layer components depend on lower-layer ones,
not vice versa. The cleaner the lower triangle, the better the layering.

**Cycles**: Symmetric dependencies at positions (i,j) and (j,i) — entries both
above and below the diagonal between the same components — indicate cycles.
Any entry above the diagonal in a properly ordered DSM is a backward dependency
that potentially participates in a cycle.

**High cohesion clusters**: Square clusters of filled cells along the diagonal
indicate groups of tightly related components. These clusters may represent
well-defined subsystems or bounded contexts.

**Hub components**: A row with many filled cells indicates a component with high
fan-out (depends on many others). A column with many filled cells indicates
high fan-in (many depend on it). See `hub-like-dependency.md`.

### Constructing a DSM

**From source code:**
1. Identify architectural components (packages, modules, services).
2. For each component pair, count the number of dependencies (imports, calls,
   type references, inheritance relationships).
3. Populate the matrix.
4. Order components to minimize above-diagonal entries (various algorithms exist).

**From build systems:**
- Maven/Gradle module dependencies.
- npm/yarn workspace dependencies.
- Go module dependencies.
- Python package import analysis.

**Granularity choices:**
- **Package level**: Best for architectural overview. Each cell = dependencies
  between packages.
- **Class level**: Best for detailed analysis of a single component. Can be
  very large for big components.
- **Service level**: Best for microservice architectures. Each cell = API calls
  or message passing between services.

## Partitioning Algorithms

Partitioning algorithms reorder the DSM to reveal architectural structure.

### Component Algorithm
Identifies strongly connected components (cycles) in the dependency graph.
Groups cyclically dependent components together. Use this to find and
visualize dependency cycles.

### Reachability Algorithm
Groups components by transitive dependencies. Components that can reach
each other through dependency chains are grouped together. Reveals which
components are truly independent.

### Layering Algorithm
Organizes components into hierarchical layers. Components with no incoming
dependencies form the top layer. Components depending only on the top layer
form the second layer. And so on. Reveals the natural layering of the system.

**Application**: After layering, any remaining above-diagonal entries are
true layering violations — backward dependencies that break the architectural
hierarchy.

## Dependency Analysis Beyond DSM

### Dependency Direction Assessment

For each dependency edge, assess whether it flows in the correct direction:
- **Toward stability**: Dependencies should point from unstable components
  toward stable ones (see `unstable-dependency.md`).
- **Toward abstraction**: Concrete components should depend on abstract ones.
- **Downward in layers**: Higher architectural layers depend on lower ones.

### Transitive Dependency Analysis

Direct dependencies are visible. Transitive dependencies are hidden but equally
impactful. Component A depends on B depends on C — A is transitively coupled to
C. Changes in C can break A even though they have no direct relationship.

**Detection**: Compute the transitive closure of the dependency graph. Identify
unexpectedly long dependency chains and components with high transitive
dependency counts.

**Risk**: Long transitive chains amplify change impact. A change in a deep
dependency can cascade through many layers.

### Dependency Categorization

Not all dependencies are equal. Categorize them:
- **Compile-time vs. runtime**: Compile-time dependencies are visible in source.
  Runtime dependencies (DI, reflection, dynamic loading) are invisible.
- **Strong vs. weak**: Inheritance and direct method calls create strong coupling.
  Event-based communication and interface-only dependencies create weaker coupling.
- **Structural vs. logical**: Structural dependencies are in the code. Logical
  dependencies are in the change patterns (files that change together).

## Tools

- **Lattix Architect**: Enterprise-grade DSM analysis with multiple partitioning
  algorithms.
- **NDepend**: .NET dependency analysis with DSM visualization.
- **Structure101**: Multi-language architectural analysis with DSM.
- **IntelliJ IDEA**: Built-in DSM analysis for Java/Kotlin projects.
- **Eclipse DSM plugins**: DSM visualization for Eclipse-based projects.
- **Madge / dependency-cruiser**: JavaScript/TypeScript dependency analysis.
- **pydeps / import-linter**: Python dependency analysis.
