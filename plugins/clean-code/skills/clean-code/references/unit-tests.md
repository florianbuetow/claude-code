# Unit Tests — Chapter 9

> Test code is not second-class. It is held to the same standard as production
> code, because a suite nobody can read is a suite nobody maintains, and a suite
> nobody maintains stops being trusted.

## Core idea

Tests are what make everything else safe to change. That only holds while they
stay readable and fast — a slow, tangled suite gets skipped, then ignored, then
deleted, and the codebase loses the property that let it be refactored at all.

**F.I.R.S.T.** — Fast, Independent, Repeatable, Self-validating, Timely.

**Owns this dimension:** findings whose fix changes *test structure, naming,
setup, assertions, independence, or speed*. Production-code problems found while
reading tests route to their own dimension.

## Violation patterns

### 1. More than one concept per test
**Look for:** a test asserting several unrelated rules; blank-line-separated
blocks each with their own arrange and assert; a name so general it cannot
describe the failure — `testEverything`, `handlesDateBoundaries`.

**Why it costs:** the first failing assert hides the rest, so a run reports one
broken thing when three may be broken, and the name cannot say which rule went.

**Fix:** split into one test per rule, each named for the rule —
`handles30DayMonths`, `handlesLeapYear`, `handlesNonLeapYear`.

**Reference:** `Ch.9: One Concept per Test`. (Note: the Chapter 17 catalog has
no code for this — do not stretch `T1`.)
**Severity:** MEDIUM.

### 2. Tests that depend on each other
**Look for:** shared mutable state between tests; a test that only passes after
another has run; ordering assumptions; a class-level fixture mutated in place.

**Why it costs:** breaks parallel execution and makes failures depend on run
order, which is how a suite becomes flaky and then distrusted.

**Fix:** give each test its own fixture; move setup into per-test construction.

**Reference:** `Ch.9: F.I.R.S.T.` (Independent).
**Severity:** HIGH — flakiness destroys trust in the whole suite.

### 3. Non-repeatable tests
**Look for:** dependence on wall-clock time, `now()`, timezone, random values
without a fixed seed, network calls, real filesystem paths, or leftover state
from a previous run.

**Fix:** inject the clock and the seed; stub the network; use a temp directory.

**Reference:** `Ch.9: F.I.R.S.T.` (Repeatable).
**Severity:** HIGH when it can fail spuriously.

### 4. Tests that do not self-validate
**Look for:** tests that print instead of assert; assertions on output a human
must eyeball; a test that cannot fail — asserting a mock was configured, or
`assertTrue(true)`; a test whose assertion restates the stub.

**Why it costs:** a green test that cannot go red is worse than no test, because
it advertises coverage that does not exist.

**Fix:** assert the actual observable behavior. If the test cannot fail, it is
testing nothing — say so plainly.

**Reference:** `Ch.9: F.I.R.S.T.` (Self-validating).
**Severity:** HIGH.

### 5. Slow tests in the unit suite
**Look for:** sleeps, real timeouts, container startup, large fixture files,
network or database access in tests labelled unit.

**Fix:** move to an integration suite or replace the dependency.

**Reference:** `T9: Tests Should Be Fast`.
**Severity:** MEDIUM.

### 6. Unreadable tests
**Look for:** twenty lines of setup obscuring one assertion; magic literals with
no meaning; duplicated arrange blocks across a file; no visible
arrange/act/assert shape.

**Fix:** extract a builder or a named factory; name the fixture values.

**Reference:** `Ch.9: Clean Tests`.
**Severity:** MEDIUM.

### 7. Missing and skipped tests
**Look for:** untested boundary conditions — empty, null, zero, negative,
off-by-one, maximum; disabled tests with no explanation; a bug fix with no
regression test.

**Fix:** add the boundary cases; either fix or delete an ignored test, and if it
marks a real ambiguity, record the question.

**Reference:** `T5: Test Boundary Conditions`, `T1: Insufficient Tests`,
`T4: An Ignored Test Is a Question about an Ambiguity`, `T6: Exhaustively Test
Near Bugs`.
**Severity:** MEDIUM.

## Do not flag

- **Multiple asserts in one test.** The rule is one *concept*, not one assert.
  Three assertions checking three fields of one returned object is one concept.
- **Arrange/act/assert structure** — three phases of one concept, not three
  things.
- **Conventional fixture names.** `foo`, `bar`, `sut`, `dummy`, `sut` are
  deliberate signals that a value is irrelevant.
- **Integration and e2e tests being slow.** They are supposed to be. Judge speed
  only against the suite the test claims to belong to.
- **Table-driven tests** with many cases in one function. That is one concept,
  parameterised — idiomatic in Go and Rust especially.
- **Deliberate duplication in tests.** Tests favour explicitness over DRY;
  aggressive extraction that hides what a test does is a step backwards.
- **Snapshot tests** used for genuinely large output.
- **Absence of tests for trivial code** — but note that `T3: Don't Skip Trivial
  Tests` cuts the other way; use judgement about which applies.
