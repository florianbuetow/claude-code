# Over-Abstraction

> "All problems in computer science can be solved by another level of indirection...
> except for the problem of too many layers of indirection."
> — Butler Lampson

## Core Idea

Over-abstraction introduces accidental complexity by adding layers, interfaces, and
patterns that don't yet serve a concrete need. Good abstraction simplifies; premature
abstraction obscures. The cost of an abstraction is not just writing it — it's every
developer who must understand it, navigate through it, and maintain it forever.

An abstraction is justified only when it eliminates duplication across multiple concrete
uses or encapsulates genuinely variable behavior. If neither condition holds, the
abstraction is speculative — and speculative abstractions become load-bearing walls
that resist the changes they were supposed to enable.

## Violation Patterns

### 1. Premature Generalization
**Heuristic:** Interface or abstract class with exactly one implementor and no tests
using mocks or stubs against it.

**Look for:**
- `IFooService` with only `FooService`.
- Generic type parameters that are always instantiated the same way.
- "Plugin architectures" with one plugin.
- Configuration systems with one configuration.

**Refactoring:** Delete the interface, use the concrete class directly. Add abstraction
when a second use case arrives and reveals the actual axis of variation.

### 2. Unnecessary Indirection
**Heuristic:** A class whose methods all delegate to another object with zero
additional logic, validation, or transformation.

**Look for:**
- Service -> ServiceImpl with no additional behavior.
- Methods that just call `this.delegate.sameMethod(sameArgs)`.
- "Manager" or "Handler" classes that only forward calls.

**Refactoring:** Remove the wrapper, depend on the underlying class directly. If the
wrapper exists "for testing," use the real class and test at a higher level.

### 3. Pattern Overuse
**Heuristic:** Pattern implementation where the "framework" code exceeds the
"business" code.

**Look for:**
- Strategy pattern with one strategy.
- Observer with one listener.
- Factory that always returns the same type.
- Builder for objects with 2-3 fields.
- AbstractFactory for one product family.

**Refactoring:** Replace with the simplest construct that works — a function, a
constructor, a conditional. Patterns are solutions to recurring problems; without
the recurring problem, they're just ceremony.

### 4. Excessive Layering
**Heuristic:** A request passes through 4+ layers to reach the actual logic, with
most layers adding no meaningful transformation.

**Look for:**
- Controller -> Service -> Repository -> DAO with each layer mirroring the one below.
- DTO -> Entity -> Model -> ViewModel mapping chains where the objects are nearly
  identical.
- "Clean architecture" where every layer has its own copy of the same data structure.

**Refactoring:** Collapse passthrough layers, allow controllers to use repositories
directly when the service layer adds nothing. Keep layers that genuinely separate
concerns; remove layers that separate nothing.

### 5. Abstraction Inversion
**Heuristic:** Using a complex tool to do something the language provides natively.

**Look for:**
- Implementing string manipulation using regex when `split`/`replace` suffices.
- Using an ORM to run raw SQL by working around the ORM.
- Building a simple key-value store on top of a relational database.
- Wrapping `fetch` in a custom HTTP client that exposes the same API.

**Refactoring:** Use the simpler, more direct tool. If you're fighting the
abstraction, you've chosen the wrong one.

## Language-Specific Notes

- **Python:** Duck typing means interfaces are often unnecessary — just use the
  object. `Protocol` is useful when you need structural typing for testing, but
  don't create protocols for every class.
- **Java/C#:** The ecosystem encourages interfaces and DI frameworks, but
  single-implementation interfaces are still overhead. Spring/ASP.NET conventions
  don't mandate unnecessary layers.
- **TypeScript:** Type aliases and union types often replace the need for class
  hierarchies. A type literal is simpler than an enum with one value.
- **Go:** Implicit interface satisfaction means you should define interfaces at the
  consumer, not the provider. An interface with one method used in one place is
  just noise.

## False Positives to Avoid

- Interfaces used for testing with mocks/stubs across multiple test files — that's
  a legitimate second consumer.
- Abstraction layers mandated by framework conventions that are widely understood
  (e.g., MVC controllers, Rails models).
- Separation that enables independent deployment or team ownership, even if the code
  looks like passthrough.
- Type hierarchies that model a real domain taxonomy (not invented for code
  organization).
