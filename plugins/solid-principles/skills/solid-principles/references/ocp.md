# Open/Closed Principle (OCP)

> "Software entities should be open for extension, but closed for modification."
> — Bertrand Meyer (popularized by Robert C. Martin)

## Core Idea

You should be able to add new behavior to a system without modifying existing,
working code. This is achieved through abstractions: interfaces, abstract classes,
strategy patterns, plugins, or higher-order functions. When new requirements arrive,
you extend (add new implementations) rather than edit existing classes.

OCP doesn't mean "never touch existing code" — it means design so that the *common*
axis of change can be handled by extension rather than modification.

## Violation Patterns

### 1. Type-Switching / Conditional Dispatch
**Heuristic**: `if/elif/else` or `switch/case` chains that branch on a type,
status, enum, or string tag to decide behavior.

**Look for**:
- `if isinstance(x, Foo)` / `if type == "bar"` chains.
- The same switch structure repeated across multiple methods/locations.
- Adding a new type requires editing every switch statement.

**Refactoring**: Replace conditionals with polymorphism. Define an interface,
implement per type, and dispatch via method calls instead of branches.

### 2. Hardcoded Strategies
**Heuristic**: An algorithm or behavior is baked directly into a class with no
way to swap it out without modifying the class itself.

**Look for**:
- A class that internally instantiates its collaborators (e.g., `self.sorter = QuickSort()`).
- Formatting/encoding logic written inline rather than delegated.
- Configuration that requires code changes (magic strings, hardcoded URLs).

**Refactoring**: Extract the strategy into an interface/protocol and inject it.
The class becomes open to new strategies without modification.

### 3. Modification Magnets
**Heuristic**: A single file or class that must be edited for every new feature,
even when the features are independent.

**Look for**:
- A router/registry where every new handler requires adding a line.
- A factory with a growing `if/elif` chain.
- A config file that's really just a list of hardcoded mappings.

**Refactoring**: Use registration patterns (decorators, plugin discovery,
convention-based loading) so new features register themselves.

### 4. Rigid Data Pipelines
**Heuristic**: A processing pipeline where adding a new step requires modifying
the pipeline class rather than plugging in a new processor.

**Look for**:
- Sequential method calls in a `process()` method with no way to add/remove steps.
- ETL code where each new transformation is added by editing the main function.

**Refactoring**: Use a pipeline/chain pattern where processors implement a common
interface and can be composed dynamically.

## Language-Specific Notes

- **Python**: Protocols and ABCs enable OCP. Decorators and first-class functions
  are natural extension points. `functools.singledispatch` is an idiomatic
  alternative to type-switching.
- **Java/C#**: Interfaces and abstract classes are the primary mechanism. Look
  for `switch` on enums as a common violation.
- **TypeScript**: Union types with exhaustive switches are sometimes intentional
  (discriminated unions). This is a valid pattern when the set of types is truly
  closed. Flag it only when the set is expected to grow.
- **Go**: Interface satisfaction is implicit, which makes OCP natural. Watch for
  type-switch statements (`switch v := x.(type)`) as potential violations.

## False Positives to Avoid

- **Discriminated unions in functional-style code**: TypeScript `type Shape = Circle | Square`
  with exhaustive pattern matching is a deliberate design choice, not a violation —
  the compiler enforces handling all cases.
- **Simple mappings**: A dictionary/map from string to handler is often fine and
  doesn't need a full plugin system.
- **Early-stage code**: Adding abstractions before you know the axis of change
  is premature. OCP is most valuable when applied to known extension points.
- **Configuration**: Not every hardcoded value is an OCP violation. Constants
  that genuinely don't change are fine.
