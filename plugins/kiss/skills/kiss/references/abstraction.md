# Over-Abstraction — Simplification Opportunities

> "All problems in computer science can be solved by another level of indirection...
> except for the problem of too many layers of indirection."
> — Butler Lampson

## Core Idea

Abstraction is a simplification opportunity when the layers, interfaces, and patterns
don't serve a concrete need. Good abstraction simplifies; premature abstraction
obscures. The cost of an abstraction is not just writing it — it's every developer who
must understand it, navigate through it, and maintain it.

An abstraction is justified only when it: (a) eliminates duplication across multiple
concrete uses, (b) encapsulates genuinely variable behavior, or (c) provides a simpler
mental model than the underlying implementation. If none of these conditions holds, the
abstraction is speculative — and speculative abstractions become load-bearing walls that
resist the changes they were supposed to enable.

This dimension also covers **interface complexity** — the surface area that consumers
must understand. Overly broad interfaces, excessive parameter counts, and complex return
types are abstraction problems that can be simplified by narrowing.

## Simplification Patterns

### 1. Premature Generalization
**Detection heuristic:** Interface or abstract class with exactly one implementor and
no tests using mocks or stubs against it.

**Metric thresholds:**
- Interface with 1 implementation: likely simplifiable
- Generic type parameters always instantiated the same way: simplifiable
- Abstract class with 1 concrete subclass: likely simplifiable

**Look for:**
- `IFooService` with only `FooService`.
- Generic type parameters always instantiated identically.
- "Plugin architectures" with one plugin.
- Configuration systems with one configuration.
- Abstract base classes where the "template method" is only overridden once.

**Simplification approach:** Delete the interface, use the concrete class directly. Add
abstraction when a second use case arrives and reveals the actual axis of variation. For
generics, replace with the concrete type until genuine polymorphism is needed.

### 2. Unnecessary Indirection
**Detection heuristic:** A class whose methods all delegate to another object with zero
additional logic, validation, or transformation. The indirection adds a hop without
adding value.

**Metric thresholds:**
- Class where >80% of methods are pure delegation: likely simplifiable
- Call chain depth > 3 for a simple operation: likely simplifiable

**Look for:**
- Service → ServiceImpl with no additional behavior.
- Methods that just call `this.delegate.sameMethod(sameArgs)`.
- "Manager" or "Handler" classes that only forward calls.
- Adapter/wrapper classes that don't adapt — same interface in, same interface out.

**Simplification approach:** Remove the wrapper, depend on the underlying class
directly. If the wrapper exists "for testing," use the real class and test at a higher
level, or introduce the indirection only in the test setup.

### 3. Pattern Overuse
**Detection heuristic:** Pattern implementation where the "framework" code exceeds the
"business" code. The pattern solves a problem that doesn't exist in the codebase.

**Look for:**
- Strategy pattern with one strategy.
- Observer with one listener.
- Factory that always returns the same type.
- Builder for objects with 2–3 fields.
- AbstractFactory for one product family.
- Visitor for one or two node types.
- Command pattern wrapping simple function calls.
- Mediator with two participants.

**Simplification approach:** Replace with the simplest construct that works — a
function, a constructor, a conditional. Patterns are solutions to recurring problems;
without the recurring problem, they're ceremony. When the second strategy or second
listener arrives, introduce the pattern then.

### 4. Excessive Layering
**Detection heuristic:** A request passes through 4+ layers to reach the actual logic,
with most layers adding no meaningful transformation, validation, or decision.

**Metric thresholds:**
- ≥ 4 layers for a simple operation: likely simplifiable
- DTO/entity mapping chains with near-identical objects: simplifiable
- Each layer mirrors the one below in structure: simplifiable

**Look for:**
- Controller → Service → Repository → DAO with each layer mirroring the one below.
- DTO → Entity → Model → ViewModel mapping chains with near-identical objects.
- "Clean architecture" where every layer has its own copy of the same data structure.
- Middleware chains where most middleware passes through unchanged.

**Simplification approach:** Collapse passthrough layers. Allow controllers to use
repositories directly when the service layer adds nothing. Keep layers that genuinely
separate concerns; remove layers that separate nothing. Shared data structures across
layers is acceptable when the layers don't truly need isolation.

### 5. Abstraction Inversion
**Detection heuristic:** Using a complex tool to do something the language provides
natively, then fighting the tool to get simple behavior.

**Look for:**
- String manipulation via regex when `split`/`replace` suffices.
- Using an ORM to run raw SQL by working around the ORM.
- Building a key-value store on top of a relational database.
- Wrapping `fetch` in a custom HTTP client that exposes the same API.
- Using a state management library for state that lives in one component.

**Simplification approach:** Use the simpler, more direct tool. If you're fighting the
abstraction, you've chosen the wrong one. Drop down a level when the abstraction adds
friction without adding value.

### 6. Interface Bloat
**Detection heuristic:** Interfaces or APIs with a large surface area, many parameters,
or complex return types that force consumers to understand more than they need.

**Metric thresholds:**
- Function parameters > 5: likely simplifiable
- Interface with > 10 methods: may violate Interface Segregation, simplifiable
- Return types requiring 3+ levels of unwrapping: simplifiable
- Method signatures longer than one line: worth examining

**Look for:**
- Functions accepting many parameters where most are optional or configuration.
- "God interfaces" that cover many unrelated operations.
- Complex return types (nested optionals, tuples of tuples, deeply generic types).
- APIs where every consumer uses a different subset of methods.
- Configuration objects with 20+ fields where most consumers need 3–4.

**Simplification approach:** Group related parameters into a struct/object. Split
large interfaces into focused ones (Interface Segregation). Simplify return types —
a named struct is clearer than a tuple. Provide sensible defaults so consumers only
specify what they care about.

## Language-Specific Notes

- **Python:** Duck typing means interfaces are often unnecessary — just use the
  object. `Protocol` is useful for structural typing in testing, but don't create
  protocols for every class. `dataclass` replaces builder patterns naturally.
- **Java/C#:** The ecosystem encourages interfaces and DI frameworks, but
  single-implementation interfaces are still overhead. Spring/ASP.NET conventions
  don't mandate unnecessary layers. Records (Java 16+) replace many DTOs.
- **TypeScript:** Type aliases and union types often replace class hierarchies. A
  type literal is simpler than an enum with one value. Discriminated unions replace
  the visitor pattern. `Partial<T>` and `Pick<T>` simplify interface variants.
- **Go:** Implicit interface satisfaction means you should define interfaces at the
  consumer, not the provider. An interface with one method used in one place is
  noise. Accept interfaces, return structs.
- **Rust:** Trait-based polymorphism is idiomatic but trait objects for one type are
  premature. `impl Trait` in argument position avoids unnecessary boxing. Prefer
  concrete types until polymorphism is needed.

## False Positives to Avoid

- Interfaces used for testing with mocks/stubs across multiple test files — that's
  a legitimate second consumer.
- Abstraction layers mandated by well-understood framework conventions (e.g., MVC
  controllers, Rails models) — conventions reduce cognitive load even when they look
  like overhead.
- Separation that enables independent deployment or team ownership, even if the code
  looks like passthrough.
- Type hierarchies that model a real domain taxonomy (not invented for code
  organization).
- Dependency injection containers in large applications where they genuinely manage
  complex object graphs — DI itself is not the problem; DI for 3 classes is.
