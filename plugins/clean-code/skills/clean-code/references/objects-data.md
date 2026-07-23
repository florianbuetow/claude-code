# Objects and Data Structures — Chapter 6

> Objects hide their data and expose behavior. Data structures expose their data
> and have no meaningful behavior. Trouble starts when a type tries to be both.

## Core idea

The anti-symmetry is the whole chapter: making something an object lets you add
new *types* easily but new *operations* painfully; making it a data structure
inverts that. Neither is better — but a type that has not chosen is worse than
either, because it gets the drawbacks of both.

The practical consequence for a reviewer: look for data that is public but has
an invariant to protect, and for behavior that lives away from the data it
operates on.

**Owns this dimension:** findings whose fix changes *the data representation, or
what a type exposes versus hides*. If the fix is renaming a field it is
`naming`; if it is splitting a method it is `functions`.

## Violation patterns

### 1. Public mutable state with an invariant
**Look for:** a public field callers assign directly, where some rule should
hold — a balance that must not go negative, a status with a legal transition
set, a collection that must stay sorted.

**Why it costs:** there is nowhere to enforce the rule, nowhere to audit the
change, and nowhere to change the representation later. Every caller is coupled
to the field itself.

**Fix:** make the field private; expose the operations that maintain the
invariant — `withdraw()`, `deposit()`, `balance()` — with the check inside.

**Reference:** `Ch.6: Data Abstraction`.
**Severity:** HIGH when a real invariant is unprotected, MEDIUM otherwise.

### 2. Validation living outside the data
**Look for:** the same guard repeated at every assignment site; a rule enforced
in a controller that the model does not know about.

**Fix:** move the check behind the setter or constructor so the invariant
travels with the data and cannot be bypassed.

**Reference:** `Ch.6: Data Abstraction`, or `G17: Misplaced Responsibility`.
**Severity:** MEDIUM, HIGH if any path already bypasses the check.

### 3. Train wrecks and transitive navigation
**Look for:** `a.getB().getC().doSomething()`; chains reaching through two or
more objects; code that must know the shape of a graph it does not own.

**Fix:** ask the immediate collaborator for what you actually need — add a
method that hides the traversal. Note the exception: fluent builders and
query DSLs are chains *by design* and are not train wrecks.

**Reference:** `G36: Avoid Transitive Navigation`, or `Ch.6: The Law of
Demeter`.
**Severity:** MEDIUM.

### 4. Feature envy
**Look for:** a method that reads several fields of another object and barely
touches its own; calculations over another type's data performed outside it.

**Fix:** move the method to the type whose data it uses.

**Reference:** `G14: Feature Envy`.
**Severity:** MEDIUM.

### 5. Hybrids
**Look for:** a type with public fields *and* significant behavior; a "model"
that is half bag-of-data and half business logic; getters and setters for every
field plus meaningful methods.

**Why it costs:** hard to add types *and* hard to add operations.

**Fix:** decide. Either it is a data carrier and behavior moves out, or it is an
object and the fields go private.

**Reference:** `Ch.6: Hybrids`.
**Severity:** MEDIUM.

### 6. Accessor-only classes with logic elsewhere
**Look for:** a class that is nothing but getters and setters, with every rule
about its data implemented in services around it.

**Fix:** pull the behavior in — but check scope first. If the finding is really
"this class has no reason to exist" or "responsibilities are spread across the
wrong classes", that is `solid-principles` (SRP) territory; defer it.

**Reference:** `Ch.6: Data/Object Anti-Symmetry`.
**Severity:** LOW to MEDIUM.

## Do not flag

- **Genuine DTOs.** Wire formats, API request/response types, database rows,
  protobuf and serde structs are *supposed* to be public data with no behavior.
  This is `Ch.6: Data Transfer Objects`, working as intended.
- **Records, dataclasses, structs, and value types** used as values.
- **Fluent interfaces and builders.** `query.where().orderBy().limit()` is a
  designed chain, not a train wreck.
- **Chains through collections and standard library types.**
  `list.stream().filter().map()` is not transitive navigation.
- **Immutable data exposed publicly.** With no mutation there is no invariant to
  protect; a public `final` field is fine.
- **Language idiom.** Python properties, Kotlin data classes, Go's exported
  struct fields, and C# auto-properties are all normal.
- **Class-responsibility problems.** "This class does too much" is
  `solid-principles`. Defer, do not analyse.
