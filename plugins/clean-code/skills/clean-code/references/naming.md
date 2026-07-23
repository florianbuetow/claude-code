# Naming — Chapter 2

> A name should tell you why it exists, what it does, and how it is used. If a
> name needs a comment, it is not revealing intent.

## Core idea

Names are the highest-leverage thing in a codebase because they are read far
more often than they are written. A wrong name is worse than a vague one: a
vague name slows a reader down, a wrong name sends them somewhere else entirely
and they do not find out until something breaks.

**Owns this dimension:** any finding whose sufficient fix is *a rename*. If
renaming the identifier resolves the problem completely, it belongs here — even
when the thing being renamed is a function, and even when Chapter 3 also
discusses it.

## Violation patterns

### 1. Names that state something false
**Look for:** `accountList` that is a `Map`; `isValid()` that mutates;
`getUser()` that creates one when missing; `count` holding a sum; abbreviations
colliding with a domain term that means something else here.

**Why it costs:** the reader trusts the name and stops reading. This is the one
naming problem that reliably causes defects rather than delay.

**Fix:** rename to what it actually is or does. If the name is right and the
behavior is wrong, that is a `functions` finding instead.

**Reference:** `N4: Unambiguous Names`, or `Ch.2: Avoid Disinformation`.
**Severity:** HIGH — it misleads.

### 2. Function names that do not say what the function does
**Look for:** `addToDate(date, 1)` — adds what? `process()`, `handle()`,
`doWork()`, `manage()`. Call sites that are unreadable without opening the
definition.

**Fix:** name the operation and its object: `addMonthsToDate(date, months)`.

**Reference:** `G20: Function Names Should Say What They Do`.
**Severity:** MEDIUM, HIGH if the call site reads as the wrong operation.

### 3. Scope-inappropriate length
**Look for:** single letters spanning long bodies; `d`, `tmp`, `data`, `obj`,
`l` used across a dozen lines. Conversely, `theCustomerAccountRecordObject` for
a two-line block.

**Rule of thumb:** name length should scale with scope. A loop index in a
three-line loop is fine as `i`. The same identifier across forty lines is not.

**Fix:** rename to the domain term.

**Reference:** `N5: Use Long Names for Long Scopes`.
**Severity:** MEDIUM for long scopes, LOW for short ones.

### 4. Inconsistent vocabulary and convention
**Look for:** `fetchUser` / `getAccount` / `retrieveOrder` for the same
operation; `DAYS_IN_WEEK` beside `daysInMonth`; `eraseDatabase` beside
`restore_database`; `animal` beside `Container` as type names.

**Why it costs:** a reader cannot infer the rule, so every name must be looked
up individually.

**Fix:** pick one verb per concept and one case convention per category, and
apply them.

**Reference:** `G11: Inconsistency`, or `Ch.2: Pick One Word per Concept`.
**Severity:** MEDIUM.

### 5. Gratuitous or redundant context
**Look for:** `Car.carMake`, `Car.carModel`; every class in a module prefixed
with the module name; `UserInfoDataObject`.

**Fix:** drop the prefix. The enclosing type already supplies the context.

**Reference:** `Ch.2: Don't Add Gratuitous Context`.
**Severity:** LOW.

### 6. Encodings and noise
**Look for:** Hungarian notation (`strName`, `iCount`), `m_` member prefixes,
`I` interface prefixes in languages that do not need them, noise words
(`Data`, `Info`, `Manager`, `Processor`) that distinguish nothing —
`ProductInfo` beside `ProductData`.

**Fix:** delete the encoding; make the distinction real or merge the concepts.

**Reference:** `N6: Avoid Encodings`, or `Ch.2: Make Meaningful Distinctions`.
**Severity:** LOW, unless two noise-distinguished types are actively confused.

### 7. Unsearchable and unpronounceable names
**Look for:** bare numeric literals used as identifiers-by-value, `genymdhms`,
single letters as class or module names.

**Fix:** named constants; pronounceable words.

**Reference:** `Ch.2: Use Searchable Names`, `G25: Replace Magic Numbers with
Named Constants`.
**Severity:** LOW to MEDIUM.

## Do not flag

The false-positive risks specific to naming — the most over-flagged dimension:

- **Established short names in their conventional scope.** `i`, `j` for loop
  indices; `e` for a caught exception; `_` for a discard; `id`, `url`, `db`.
- **Domain abbreviations the project uses consistently.** If the codebase and
  its domain say `SKU`, `ISBN`, `FX`, that is the right name.
- **Language and framework conventions.** Python `self`, Go's single-letter
  receivers (`func (s *Server)`), Rust `impl` lifetimes, React `props`.
- **Test fixture names.** `foo`, `bar`, `sut`, `dummy` are conventional in tests
  and communicate "irrelevant" deliberately.
- **Generic names on genuinely generic code.** `combine(a, b)` in a math utility
  does not need domain terms, because there is no domain.
- **Names you merely find inelegant.** If you cannot say what a reader would
  misunderstand, there is no finding.
