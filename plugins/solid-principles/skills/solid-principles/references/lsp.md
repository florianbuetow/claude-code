# Liskov Substitution Principle (LSP)

> "Objects of a supertype shall be replaceable with objects of a subtype without
> altering the correctness of the program."
> — Barbara Liskov

## Core Idea

If class `B` extends class `A`, you should be able to use `B` anywhere `A` is
expected without surprises. Subtypes must honor the behavioral contract of their
parent — not just the type signature, but the semantic expectations: preconditions,
postconditions, invariants, and side effects.

LSP is the formal foundation of polymorphism. When it's violated, inheritance
becomes a liability rather than a tool.

## Violation Patterns

### 1. Refusing Inherited Behavior
**Heuristic**: A subclass overrides a method to throw `NotImplementedError`,
return `None`, or do nothing — effectively saying "I don't support this."

**Look for**:
- `raise NotImplementedError` in an override.
- Override that returns a hardcoded empty/null value.
- Override with `pass` as the body.
- Comments like "not applicable for this subtype."

**Refactoring**: The inheritance hierarchy is wrong. Either extract the
unsupported method into a separate interface/mixin, or restructure the hierarchy
so the subclass isn't forced to inherit behavior it can't fulfill.

### 2. Strengthened Preconditions
**Heuristic**: A subclass method requires MORE from its inputs than the parent's
contract promises.

**Look for**:
- Added `if` guards at the start of an override that reject inputs the parent
  would accept (e.g., parent accepts any int, subclass rejects negatives).
- Type narrowing in overrides (e.g., parent accepts `Animal`, subclass demands `Dog`).
- Additional validation not present in the parent.

**Refactoring**: Subtypes should accept at least everything the parent accepts.
Widen preconditions or rethink the hierarchy.

### 3. Weakened Postconditions
**Heuristic**: A subclass method provides LESS in its return value than the
parent guarantees.

**Look for**:
- Parent returns a fully populated object; subclass returns a partial/null result.
- Parent guarantees sorted output; subclass doesn't maintain the order.
- Parent guarantees non-null; subclass may return null.

**Refactoring**: Subtypes must deliver at least what the parent promises.
Strengthen the subclass implementation or adjust the contract.

### 4. Violated Invariants
**Heuristic**: A subclass breaks a property that the parent always maintains.

**Look for**:
- Parent maintains `balance >= 0`; subclass allows negative balance.
- Parent ensures a collection is always sorted; subclass inserts without sorting.
- State machine invariants broken (e.g., skipping required transitions).

**Refactoring**: Either enforce the invariant in the subclass or don't inherit.

### 5. The Classic Rectangle-Square Problem
**Heuristic**: A subclass constrains independent properties of the parent, creating
contradictory behavior under mutation.

**Look for**:
- Subclass overrides setters to enforce constraints that break parent behavior
  (e.g., `Square.set_width()` also sets height).
- Tests that pass for the parent but fail for the subclass.

**Refactoring**: Use composition or a common interface instead of inheritance.
Make `Square` and `Rectangle` siblings, not parent-child.

### 6. Exception Surprises
**Heuristic**: A subclass throws exceptions that callers of the parent type
wouldn't expect.

**Look for**:
- Override that throws new checked/unchecked exception types not in the parent's
  contract.
- Override that can fail in scenarios where the parent is documented as safe.

**Refactoring**: Subtypes should only throw exceptions that are subtypes of
the parent's declared exceptions, or handle errors internally.

## Language-Specific Notes

- **Python**: Duck typing makes LSP violations subtle — they manifest at runtime
  as `AttributeError` or unexpected `None`. Watch for Protocol/ABC mismatches.
- **Java/C#**: The compiler enforces type signatures but NOT behavioral contracts.
  Look for `@Override` methods that change semantics.
- **TypeScript**: Structural typing means you can create implicit subtypes that
  violate LSP. Watch for interface implementations that throw on "unsupported"
  methods.
- **Go**: No inheritance, but interface satisfaction can be violated if a concrete
  type's method has different semantics than the interface implies.

## False Positives to Avoid

- **Template Method pattern**: Abstract methods that are *designed* to be overridden
  with different behavior are not LSP violations — the parent's contract explicitly
  delegates to subclasses.
- **Intentional restriction**: If a subclass is documented as a restricted variant
  and callers are aware, this may be acceptable (though it suggests composition
  over inheritance).
- **Different behavior, same contract**: A `LinkedList` and `ArrayList` behave
  differently in performance characteristics but both honor the `List` contract.
  That's fine.
