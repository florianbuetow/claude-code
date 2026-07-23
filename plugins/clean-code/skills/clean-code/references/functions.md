# Functions — Chapter 3

> A function should do one thing, do it well, and do only it. You know it does
> one thing when you cannot extract another function from it with a name that is
> not merely a restatement of its body.

## Core idea

Functions are where reading happens. A long function forces the reader to hold
the whole thing in working memory; a well-decomposed one lets them stop at the
level of detail they need. The test for "one thing" is not line count — it is
whether every statement sits at the same level of abstraction.

**Owns this dimension:** findings whose fix changes *decomposition, signature,
control flow, side effects, or body*. If a rename alone would fix it, it is a
`naming` finding instead.

## Violation patterns

### 1. Doing more than one thing
**Look for:** a function that filters *and* transforms *and* dispatches; blank
lines separating a body into labelled stages; a name containing "and";
extractable blocks with meaningful names.

**Detection:** try to name the sections. If you can name them, they are separate
functions.

**Fix:** extract each section into a named function. State the names.

**Reference:** `G30: Functions Should Do One Thing`.
**Severity:** MEDIUM, HIGH if the function is also long and widely called.

### 2. Mixed levels of abstraction
**Look for:** a high-level policy call sitting beside byte manipulation or
string formatting; `calculateTotal()` next to `buffer.append(',')`.

**Why it costs:** the reader cannot skim. Every line must be read at full
attention because the altitude keeps changing.

**Fix:** push the low-level detail into its own function so the caller reads as
a sequence of intentions.

**Reference:** `G34: Functions Should Descend Only One Level of Abstraction`, or
`G6: Code at Wrong Level of Abstraction`.
**Severity:** MEDIUM.

### 3. Too many arguments
**Guideline:** zero is ideal, one or two fine, three needs a reason, four or
more almost always indicates a missing type.

**Look for:** long parameter lists; several parameters that always travel
together (a data clump); parameters only forwarded to one call.

**Fix:** introduce a parameter object for the clump, or split the function.

**Reference:** `F1: Too Many Arguments`.
**Severity:** MEDIUM. LOW when the language has named arguments and call sites
stay readable.

### 4. Flag and selector arguments
**Look for:** `render(user, true)`; `process(order, isUrgent)`; any boolean
parameter that selects a branch inside the callee.

**Why it costs:** the function does two things by construction, and the call
site is unreadable — `true` tells the reader nothing.

**Fix:** split into two named functions, `renderPreview()` and `renderFinal()`.

**Reference:** `F3: Flag Arguments`, or `G15: Selector Arguments`.
**Severity:** MEDIUM.

### 5. Hidden side effects
**Look for:** `checkPassword()` that also initialises a session; a getter that
mutates or lazily writes; a validator that logs, sends, or persists; output
arguments mutated in place.

**Why it costs:** callers cannot reason about ordering, and the function cannot
be called twice safely.

**Fix:** separate the query from the command, or rename to declare the effect
(`N7`) — note that if a *rename alone* makes it honest, route it to `naming`.

**Reference:** `Ch.3: Have No Side Effects`, `Ch.3: Command Query Separation`,
`F2: Output Arguments`.
**Severity:** HIGH — hidden effects cause defects.

### 6. Type-code dispatch that wants polymorphism
**Look for:** `switch` or if/else chains on a type field, repeated in more than
one place; parallel chains that must be edited together whenever a case is
added.

**Fix:** replace with polymorphic dispatch. If the switch appears exactly once
and creates objects, it may be a legitimate factory — say so and move on.

**Reference:** `G23: Prefer Polymorphism to If/Else or Switch/Case`.
**Severity:** MEDIUM when repeated, LOW for a single occurrence.

### 7. Obscured intent and unexplained conditions
**Look for:** dense boolean expressions; magic numbers in comparisons; negative
conditionals (`if (!isNotReady)`); deeply nested guards.

**Fix:** extract the condition into a named predicate or explanatory variable —
`if (isEligibleForDiscount(customer))`.

**Reference:** `G28: Encapsulate Conditionals`, `G19: Use Explanatory
Variables`, `G29: Avoid Negative Conditionals`, `G25: Replace Magic Numbers`.
**Severity:** MEDIUM.

### 8. Dead and unreachable functions
**Look for:** zero call sites outside tests; code behind a permanently-settled
feature flag; overloads nothing calls.

**Fix:** delete it. Version control is the backup.

**Reference:** `F4: Dead Function`, or `G9: Dead Code`.
**Severity:** LOW to MEDIUM.

## Do not flag

- **Length alone.** A 40-line function at one consistent abstraction level,
  doing one thing, is fine. Report structure, not line count.
- **Long but flat dispatch tables**, parsers, and generated code — these are
  data expressed as code.
- **Idiomatic error handling.** Go's repeated `if err != nil` is the language,
  not a smell.
- **Framework-mandated signatures.** Lifecycle hooks, handlers, and middleware
  take the arguments the framework passes.
- **Test functions** doing arrange/act/assert — that is three phases of one
  concept, not three things.
- **A single factory switch** creating instances. That is the one switch the
  polymorphism advice permits.
