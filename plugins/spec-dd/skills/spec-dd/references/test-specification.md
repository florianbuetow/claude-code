# Test Specification — Reference Guide

> "The purpose of a test is to document expected behavior, not to verify implementation."
> — Martin Fowler, [Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)

## Core Principles

Test scenarios are the bridge between a behavioral specification and working code.
They must be derived from the specification alone — never from implementation
knowledge. A well-written test specification captures what the system should do in
concrete, verifiable scenarios without prescribing how the system does it.

**1. Derive from the spec only.** Every test scenario must trace back to a requirement,
acceptance criterion, edge case, or constraint in the behavioral specification. If you
cannot point to the spec section a scenario covers, the scenario is either orphaned
or the spec is incomplete.

**2. Describe behavior, not implementation.** Tests assert observable outcomes — state
changes, return values, error messages, side effects visible to the user. They never
assert internal data structures, private method calls, or database row layouts.

**3. One behavior per scenario.** Each scenario exercises exactly one behavior or
decision path. When a scenario fails, the failure message should tell you precisely
which behavior is broken. Combining behaviors obscures this signal.

**4. One action per step.** The "When" step contains a single triggering action. If
you need multiple actions, you are testing a workflow, not a behavior — split it into
separate scenarios or extract shared state into the "Given" block.

**5. Tests are immutable during implementation.** Once the test specification is
approved, it becomes a contract. If the implementation cannot satisfy a scenario, the
implementation is wrong — not the test. Changing tests to fit code inverts the
spec-driven workflow and defeats its purpose.

## Given/When/Then Format

The Given/When/Then structure — popularized by BDD practitioners and formalized by
[Cucumber](https://cucumber.io/blog/bdd/bdd-vs-tdd) and
[Testomat](https://testomat.io/blog/writing-bdd-test-cases-in-agile-software-development-examples-best-practices-test-case-templates/) —
provides a consistent, readable format for expressing test scenarios.

### Given — Preconditions

The state of the world before the behavior occurs. Describes context, not actions.

- Use one Given per scenario. Chain additional preconditions with "And".
- Keep it declarative: "Given an authenticated user" — not "Given the user enters
  credentials and clicks login".
- Use domain language from the specification. "Given a published article" is
  clearer than "Given a row in the articles table with status=1".

### When — The Action

The single event or action under test.

- Exactly one When per scenario. If you have two, you have two scenarios.
- Express intent, not mechanics: "When the user updates their display name" — not
  "When a PUT request is sent to /api/users/123/name".

### Then — Expected Outcome

The observable result that proves the behavior works.

- Assert outcomes the user or caller can observe: response values, state changes,
  error messages, published events.
- Chain additional assertions with "And".
- Avoid asserting internals: "Then the cache is invalidated" is an implementation
  detail. "Then subsequent requests return the updated value" is observable behavior.

### Language Conventions

- Use domain vocabulary from the specification consistently.
- Write in present tense: "Then the display name is updated" — not "should have been".
- Avoid technical jargon unless the specification itself uses it.

## Deriving Test Scenarios

Systematically extract scenarios from each section of the behavioral specification.

### Happy Path Scenarios

For every acceptance criterion in the specification, write at least one scenario that
exercises the intended behavior with valid inputs and preconditions. This is the
baseline — the system works as designed when everything goes right.

### Edge Case Scenarios

The specification's "Edge Cases" section is a direct source of test scenarios. Each
edge case should produce at least one scenario. Common categories: boundary values,
empty/null states, concurrent access, and timing conditions.

### Constraint Violation Scenarios

For each constraint — technical, business, or regulatory — consider what happens
when it is violated. These scenarios verify that the system enforces its boundaries:
input exceeding limits, unauthorized access, rate limit breaches, malformed data.

### Negative Scenarios from Non-Goals

The specification's "Non-Goals" section defines what the system does NOT do. Write
negative scenarios to guard the boundary and prevent scope creep during
implementation.

### Decision Tables

When a requirement involves multiple independent conditions, enumerate the
combinations in a decision table and derive one scenario per combination:

| Condition A | Condition B | Expected Outcome |
|-------------|-------------|------------------|
| True        | True        | Result X         |
| True        | False       | Result Y         |
| False       | True        | Result Z         |
| False       | False       | Result W         |

Each row becomes a scenario. This ensures combinatorial coverage without
guesswork.

## Coverage Matrix

The coverage matrix is the traceability artifact that proves every specification
requirement is tested. Build it as a table:

| Spec Requirement         | Test Scenario(s)                       |
|--------------------------|----------------------------------------|
| AC-1: Valid display name | TS-1: Update with valid input          |
| AC-2: Name length limit  | TS-2: Reject exceeding max, TS-3: Reject empty |
| EC-1: Unicode support    | TS-4: Accept Unicode characters        |
| C-1: Auth required       | TS-5: Reject unauthenticated request   |

**Rules:**

- Every row in the left column must have at least one entry in the right column.
- If a requirement has no scenarios, flag it as a **coverage gap**.
- If a scenario has no corresponding requirement, flag it as an **orphan test** —
  either the spec is missing a requirement or the scenario is unnecessary.
- Review the matrix with the specification author when possible.

## Language-Aware Review Guidance

After detecting the project language and framework (from manifest files such as
`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, etc.), review the test
scenarios through the lens of that ecosystem.

**Realistic scenarios.** Ensure the scenarios describe behaviors that the testing
ecosystem can verify. For example, testing "the page renders a success banner" is
natural in a frontend framework with component testing but awkward in a CLI tool.

**Framework-compatible patterns.** Consider how scenarios translate to actual tests:

- **Async behavior (Node.js, Python asyncio):** Be explicit about ordering and timing.
- **Database transactions (backend apps):** State isolation expectations in Given.
- **HTTP APIs:** Describe request/response at the boundary the framework tests.
- **Frontend components:** Describe user-visible behavior, not DOM structure.

**This is NOT about writing code.** Language-aware review ensures scenarios are
*implementable* in the detected stack. Actual test code is written during handoff.

## Anti-Patterns to Flag

During review, watch for these common problems:

### Testing Implementation Details

Bad: "Given the database has a row with id=1 and name='Alice'"
Good: "Given a user named 'Alice' exists"

The test should survive a migration from PostgreSQL to MongoDB without changing.

### Combining Multiple Behaviors

Bad: "When the user updates their name and email, then both are changed"
Good: Two separate scenarios — one for name update, one for email update.

Each scenario tests one thing. Combined scenarios produce ambiguous failures.

### Imperative Steps

Bad: "Given the user navigates to /settings, clicks the edit button, types 'Bob'
in the name field, and clicks save"
Good: "Given an authenticated user / When the user updates their display name to
'Bob' / Then the display name is 'Bob'"

Declarative steps survive UI redesigns. Imperative steps break with every layout
change.

### Missing Edge Case Scenarios

If the specification lists edge cases but the test specification has only happy-path
scenarios, flag the gap. Edge cases are where bugs hide.

### Untestable Scenarios

If a scenario's "Then" clause cannot be objectively verified — "Then the user has a
good experience" — it is untestable. Every assertion must be measurable. Rewrite
using concrete, observable outcomes.

## Example: Deriving Scenarios from a Spec Requirement

**Specification excerpt:**

> Authenticated users can update their display name (1-50 characters, Unicode).
> Changes take effect immediately.

**Derived scenarios:**

```
Scenario: Update display name with valid input
  Given an authenticated user with display name "Alice"
  When the user updates their display name to "Bob"
  Then the display name is "Bob"
  And the change is reflected immediately

Scenario: Reject display name exceeding maximum length
  Given an authenticated user
  When the user updates their display name to a 51-character string
  Then the update is rejected with error "display name must be 1-50 characters"
  And the display name remains unchanged

Scenario: Reject empty display name
  Given an authenticated user
  When the user updates their display name to an empty string
  Then the update is rejected with error "display name must be 1-50 characters"
  And the display name remains unchanged

Scenario: Accept Unicode characters in display name
  Given an authenticated user
  When the user updates their display name to "日本語テスト"
  Then the display name is "日本語テスト"

Scenario: Reject unauthenticated display name update
  Given an unauthenticated user
  When the user attempts to update a display name
  Then the request is rejected as unauthorized
```

**Coverage matrix for this requirement:**

| Spec Requirement               | Test Scenario(s)              |
|--------------------------------|-------------------------------|
| AC: Update display name        | Update with valid input       |
| C: 1-50 character limit        | Reject exceeding max, Reject empty |
| C: Unicode support             | Accept Unicode characters     |
| C: Authentication required     | Reject unauthenticated update |
| AC: Immediate effect           | Verified in valid input scenario (And clause) |
