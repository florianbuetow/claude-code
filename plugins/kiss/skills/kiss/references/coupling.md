# Coupling & Dependencies — Simplification Opportunities

> "Coupling is the enemy of change, because it links together things that must
> change independently."
> — Kent Beck

## Core Idea

Coupling becomes a simplification opportunity when components are more intertwined than
the problem requires. Tight coupling means a change in one place forces changes in many
others — the "shotgun surgery" pattern. The simplification is to reduce the dependency
surface so that components can change independently.

Two key metrics from the research:

- **Afferent coupling (Ca):** How many modules depend on this one. High Ca means the
  module is heavily depended upon — changes are risky and far-reaching. This isn't
  inherently bad (core utilities should have high Ca), but it means the interface must
  be stable and minimal.
- **Efferent coupling (Ce):** How many modules this one depends on. High Ce means the
  module is fragile — it breaks when any of its many dependencies change. This is
  almost always simplifiable.

The ratio **instability = Ce / (Ca + Ce)** indicates whether a module is stable
(depended upon, hard to change) or unstable (depends on many, should be easy to
change). Problems arise when unstable modules are depended upon by stable ones.

**Circular dependencies** are a special case: A depends on B which depends on A. These
create tight coupling by definition and prevent independent understanding, testing, or
deployment of either module.

## Simplification Patterns

### 1. Excessive Efferent Coupling
**Detection heuristic:** A module/class importing from many other modules, especially
across different domains or layers.

**Metric thresholds:**
- Imports from > 10 distinct modules: likely simplifiable
- Imports crossing 3+ domain boundaries: likely simplifiable
- A single file depending on > 15 other files: almost certainly simplifiable

**Look for:**
- Classes with import lists spanning 20+ lines.
- Modules that import from unrelated domains (e.g., a payment module importing UI
  utilities).
- "God classes" that orchestrate everything and therefore depend on everything.
- Utility functions that pull in heavy dependencies for one small operation.

**Simplification approach:** Split the module along responsibility lines so each piece
has fewer dependencies. Inject dependencies rather than importing them directly. Extract
shared concerns into focused modules. If a function only needs one method from a large
dependency, consider whether the dependency is the right abstraction.

### 2. Circular Dependencies
**Detection heuristic:** Module A imports from Module B, and Module B (directly or
transitively) imports from Module A.

**Metric thresholds:**
- Any circular dependency between modules: simplifiable
- Circular dependency chains of length 3+: high-priority simplification
- Circular dependencies crossing package/directory boundaries: critical

**Look for:**
- Import cycles (many languages/tools detect these: Python's `importlib` errors,
  ESLint's `import/no-cycle`, Go's compiler errors).
- Two classes that reference each other's types.
- Event emitter/handler pairs that are tightly coupled through shared types.
- Layering violations where a lower layer imports from a higher layer.

**Simplification approach:** Extract the shared concept into a third module that both
depend on (dependency inversion). Use interfaces/protocols at the boundary so neither
module needs to know the other's concrete type. If the cycle exists because two
concepts are genuinely inseparable, merge them into one module — forced separation of
inseparable things is itself accidental complexity.

### 3. Deep Dependency Chains
**Detection heuristic:** Long chains of transitive dependencies where understanding or
changing one module requires understanding many others in sequence.

**Metric thresholds:**
- Dependency chain depth > 5 for a single operation: likely simplifiable
- "Change amplification" — modifying one module requires changes in 3+ others:
  simplifiable
- Transitive dependency count > 30 for a leaf module: worth examining

**Look for:**
- A function call that traverses 5+ modules before reaching the actual work.
- Changes to a data model requiring updates in many layers (serialization,
  validation, display, persistence).
- "Shotgun surgery" — a single business logic change touching many files.
- Long chains of `.get()` or accessor calls: `a.getB().getC().getD().getValue()`.

**Simplification approach:** Reduce chain depth by giving modules direct access to what
they need (Law of Demeter). Flatten unnecessary intermediaries. If many modules must
change together, they may belong in the same module. Co-change analysis (which files
always change together) reveals hidden coupling that the dependency graph doesn't show.

### 4. Tight Data Coupling
**Detection heuristic:** Modules sharing mutable state, passing large data structures
where only a few fields are used, or depending on internal data formats of other
modules.

**Look for:**
- Global mutable state accessed by multiple modules.
- Functions receiving a large object but only reading 1–2 fields.
- Modules that parse or construct another module's internal data format.
- Shared database tables accessed directly by multiple services.
- JSON/protobuf schemas tightly coupled to internal data models.

**Simplification approach:** Narrow data interfaces — pass only what's needed, not
entire objects. Encapsulate data behind accessor functions or APIs. Replace shared
mutable state with message passing or event-driven patterns. Define clear data
contracts at module boundaries.

### 5. Temporal Coupling
**Detection heuristic:** Operations that must happen in a specific order but that
ordering is implicit, not enforced by the code structure.

**Look for:**
- `init()` must be called before `process()` but nothing prevents calling them out of
  order.
- Setup/teardown sequences where forgetting a step causes silent failures.
- Modules that must be imported or registered in a specific order.
- State machine transitions enforced by convention rather than type system or runtime
  checks.

**Simplification approach:** Make the ordering explicit through the type system (builder
pattern for required sequencing, state types that change after each step) or through
runtime enforcement (initialization guards). If two things must happen together, make
them one operation.

### 6. Co-Change Coupling
**Detection heuristic:** Files that always change together in commits but have no
explicit dependency in the code. This is the hidden coupling that static analysis
misses.

**Metric thresholds:**
- Files that co-change in > 70% of commits touching either one: likely coupled
- Co-changing files in different packages/domains: likely simplifiable

**Look for:**
- A config file and a service file that always change together.
- A schema definition and multiple handler files that must be updated in sync.
- Test files that break when unrelated production files change.
- Documentation that must be manually updated when code changes.

**Simplification approach:** If files always change together, consider merging them or
generating one from the other. Automate synchronization (code generation, shared source
of truth). If they must remain separate, add a test that verifies consistency.

## Language-Specific Notes

- **Python:** Circular imports are a common symptom — use `TYPE_CHECKING` imports for
  type hints that create cycles. Prefer function-level imports for breaking cycles over
  architectural workarounds. `__init__.py` barrel files can mask coupling.
- **Java/C#:** Package-level coupling metrics (Ca/Ce) are measurable with tools like
  JDepend, NDepend. Module systems (Java 9 modules, .NET assemblies) provide hard
  boundaries. DI containers can hide coupling — the wiring configuration is the real
  dependency graph.
- **TypeScript:** Barrel files (`index.ts`) can create false coupling — importing one
  thing pulls in everything. Circular dependencies cause runtime issues with module
  initialization order. Path aliases can mask coupling distance.
- **Go:** The compiler enforces no circular imports — cycles must be broken at the
  package level. This constraint is a feature. Internal packages provide encapsulation.
  Interface-at-consumer pattern reduces coupling naturally.
- **Rust:** The module system and ownership model naturally limit coupling. `pub(crate)`
  vs `pub` provides granular visibility. Trait objects at boundaries reduce concrete
  coupling.

## False Positives to Avoid

- Core utility modules (logging, error handling, configuration) naturally have high
  afferent coupling — this is appropriate, not a problem.
- Framework-imposed coupling (e.g., Spring beans wired by the container, Rails
  model-controller conventions) is part of the framework's design.
- Co-change coupling during a refactoring — files change together because the
  refactoring touches them, not because they're permanently coupled.
- Data transfer objects (DTOs) shared across layers — if the DTO genuinely represents
  the same concept at each layer, sharing it is simpler than maintaining copies.
- Stable interfaces with high afferent coupling — being widely depended upon is fine
  if the interface rarely changes.
