# Dependency Inversion Principle (DIP)

> "High-level modules should not depend on low-level modules. Both should depend
> on abstractions. Abstractions should not depend on details. Details should
> depend on abstractions."
> — Robert C. Martin

## Core Idea

The flow of control and the flow of source code dependency should point in
opposite directions at architectural boundaries. Business logic (high-level
policy) should define the interfaces it needs, and infrastructure (low-level
detail) should implement those interfaces. This makes the core of your
application independent of databases, frameworks, and external services.

DIP is NOT simply "use interfaces everywhere." It specifically addresses the
direction of dependency at boundaries between layers.

## Violation Patterns

### 1. Direct Infrastructure Coupling
**Heuristic**: Business logic classes directly import and instantiate
infrastructure classes (database clients, HTTP libraries, file system APIs).

**Look for**:
- Business logic that imports `psycopg2`, `requests`, `boto3`, `smtplib`, etc.
- Classes that create their own database connections or HTTP clients.
- Domain logic files with imports from infrastructure/framework packages.

**Refactoring**: Define an interface/protocol in the domain layer for the
capability needed (e.g., `UserRepository`, `EmailSender`). Implement it in
the infrastructure layer. Inject the implementation at composition time.

### 2. Concrete Class Injection
**Heuristic**: Dependency injection is used, but concrete classes are injected
instead of interfaces/protocols.

**Look for**:
- Constructor type hints referencing concrete classes rather than abstractions:
  `def __init__(self, db: PostgresDatabase)` instead of `def __init__(self, db: Database)`.
- Factory methods that return concrete types.
- DI container bindings that map concrete to concrete.

**Refactoring**: Introduce an abstraction and depend on it. The concrete class
implements the abstraction and is wired in at the composition root.

### 3. Framework Entanglement
**Heuristic**: Domain/business classes inherit from or directly use framework
base classes, coupling the domain to the framework.

**Look for**:
- Domain entities extending ORM base classes (e.g., `class User(db.Model)`).
- Business logic decorated with framework decorators that can't run without the framework.
- Domain objects that require framework initialization to instantiate.

**Refactoring**: Keep domain objects plain (POJOs/dataclasses/structs). Create
adapter/mapper layers between the domain and the framework. The domain defines
what it needs; the framework adapts to it, not the other way around.

### 4. Upward Dependencies
**Heuristic**: A low-level module imports from a high-level module, creating
a circular or inverted dependency.

**Look for**:
- A utility/infrastructure module importing from a service/domain module.
- Circular import errors or lazy imports used to work around circular dependencies.
- A "shared" module that depends on specific feature modules.

**Refactoring**: Extract the shared contract into an interface module that both
layers can depend on. The dependency arrows should point inward (toward
abstractions), not upward or circularly.

### 5. Service Locator Anti-Pattern
**Heuristic**: Instead of injecting dependencies, code reaches into a global
registry or container to pull them out at runtime.

**Look for**:
- Calls like `Container.get(UserService)` or `ServiceLocator.resolve("db")`
  scattered through business logic.
- Global singleton access patterns in domain code.
- `import settings` / `from config import db` in domain logic.

**Refactoring**: Use constructor injection. Dependencies are declared explicitly
in the constructor signature and wired at the composition root (main/entry point).

### 6. Missing Abstraction Boundary
**Heuristic**: There's no interface at all between layers — high-level code
directly calls low-level code with no seam for substitution.

**Look for**:
- No interfaces/protocols/ABCs in the codebase at architectural boundaries.
- Inability to run business logic tests without a real database/API.
- Integration tests where unit tests should suffice.

**Refactoring**: Introduce interface boundaries at the points where
high-level policy meets low-level detail. You don't need interfaces everywhere —
only at architectural boundaries.

## Language-Specific Notes

- **Python**: Use `Protocol` (structural subtyping) or `ABC` for abstractions.
  Python's duck typing can mask DIP violations — things work until you try to
  test or swap implementations. Type hints with concrete classes are a smell.
- **Java/C#**: Natural territory for DIP with strong interface support and
  mature DI frameworks (Spring, .NET DI). Watch for `new` inside business
  logic as the primary violation signal.
- **TypeScript**: Use interfaces or abstract classes. Watch for direct imports
  of concrete implementations across module boundaries.
- **Go**: Interfaces are implicitly satisfied, which makes DIP natural. Define
  interfaces in the consumer package (where they're needed), not the provider
  package. This is idiomatic Go and inherently supports DIP.
- **Rust**: Traits serve as the abstraction boundary. Watch for concrete type
  dependencies where `dyn Trait` or generic `T: Trait` would be more appropriate
  at module boundaries.

## False Positives to Avoid

- **Leaf nodes**: Code at the edges of the system (entry points, scripts, CLI
  tools) naturally depends on concretes — that's the composition root. Don't
  flag `main()` for instantiating concrete classes.
- **Value objects and DTOs**: These are details, but they're typically stable
  and shared across layers. Depending on a `User` dataclass is fine.
- **Standard library**: Depending on `datetime`, `pathlib`, `collections`, etc.
  is not a DIP violation. These are stable abstractions.
- **Small projects**: A 500-line application probably doesn't need interface
  boundaries. DIP shines in systems with multiple developers, long lifespans,
  and complex infrastructure dependencies.
