# Interface Segregation Principle (ISP)

> "Clients should not be forced to depend on interfaces they do not use."
> — Robert C. Martin

## Core Idea

Keep interfaces small and focused. When a class is forced to implement methods
it doesn't need, those empty/stub methods are dead weight that couples the class
to concerns it shouldn't know about. ISP says: split large interfaces into
smaller, role-specific ones so that implementing classes only depend on the
methods they actually use.

ISP works hand-in-hand with SRP at the interface level — where SRP is about
implementation cohesion, ISP is about contract cohesion.

## Violation Patterns

### 1. Fat Interface
**Heuristic**: An interface/abstract class with 7+ methods where most
implementations only meaningfully use a subset.

**Look for**:
- Implementations with multiple `pass` / `return None` / `throw NotImplementedError`
  stub methods.
- An interface that mixes read and write operations when some consumers are read-only.
- A "God interface" that defines operations for multiple unrelated capabilities.

**Refactoring**: Split into role-based interfaces. For example,
`IRepository` → `IReader` + `IWriter`. Implementing classes can implement
one or both.

### 2. Marker Methods / Stub Implementations
**Heuristic**: A class implements an interface but leaves some methods as
no-ops or throws exceptions.

**Look for**:
- Methods with body `pass`, `return null`, `throw new UnsupportedOperationException()`.
- Comments like "// not needed for this implementation".
- Methods that always return a default/empty value because the class doesn't
  actually support that operation.

**Refactoring**: The class shouldn't be forced to implement those methods.
Extract the unsupported methods into a separate interface.

### 3. Parameter Interfaces / Bag-of-Methods
**Heuristic**: A function or constructor accepts a large interface but only
calls 1-2 methods on it.

**Look for**:
- A function that takes `IUserService` but only calls `getUserById()`.
- Constructor injection of a broad service where only a narrow slice is used.
- Test mocks that must implement 10 methods but the test only exercises 2.

**Refactoring**: Depend on a smaller interface that exposes only what's needed.
This also makes testing dramatically easier.

### 4. Leaking Infrastructure into Domain Interfaces
**Heuristic**: A domain-level interface includes infrastructure concerns like
serialization, caching, or transport.

**Look for**:
- Domain interfaces with methods like `toJson()`, `serialize()`, `cache()`.
- An interface mixing business operations (`calculateTotal()`) with
  infrastructure (`save()`, `publish()`).

**Refactoring**: Separate domain interfaces from infrastructure interfaces.
A class can implement both, but consumers depend only on the interface relevant
to their layer.

### 5. Callback / Event Listener Bloat
**Heuristic**: An event listener or callback interface requires implementing
many event handlers when most consumers care about only one or two.

**Look for**:
- Adapter base classes that exist solely to provide empty default implementations
  of a fat listener interface (e.g., Java's `MouseAdapter`).
- Event handlers with mostly empty method bodies.

**Refactoring**: Use single-method interfaces (functional interfaces) per
event type, or an event bus pattern where consumers subscribe to specific events.

## Language-Specific Notes

- **Python**: Python uses Protocols and ABCs. ISP violations show up as Protocol
  classes with too many required methods. Also applies to function signatures —
  if a function accepts a complex object but only reads `.name`, consider accepting
  just the string.
- **Java/C#**: Classic ISP territory. Watch for interfaces with `default` methods
  (Java 8+) used to paper over the fact that the interface is too broad.
- **TypeScript**: `Pick<T, K>` and mapped types allow narrowing interfaces at the
  call site, but the underlying interface might still be too broad. Also check for
  `Partial<T>` used to avoid implementing all properties.
- **Go**: Interfaces are implicitly satisfied and typically small (often 1-2 methods),
  which naturally encourages ISP. Violations happen when someone defines a large
  explicit interface mimicking Java-style patterns.
- **Rust**: Traits can become fat. Look for traits with many methods where
  implementors use `todo!()` or `unimplemented!()` for some.

## False Positives to Avoid

- **Genuinely cohesive interfaces**: A `Stream` interface with `read()`, `write()`,
  `seek()`, `close()` is cohesive if all stream types support all operations.
  Only flag it if some streams meaningfully can't support some operations.
- **Standard library interfaces**: Don't flag language-standard interfaces
  (e.g., Java's `Iterable`, Python's `Sequence`) as too broad — they're
  established contracts.
- **Small total interface count**: If an interface has 3-4 methods and all
  implementors use all of them, it's fine. ISP isn't about making every
  interface have exactly one method.
