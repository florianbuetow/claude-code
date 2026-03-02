# Test Implementation Specification -- Reference Guide

> "The act of writing a test is more an act of design than of verification."
> -- Robert C. Martin, *Clean Code*

## Purpose

This reference guides the creation and review of test implementation
specifications. A test implementation specification describes HOW each test
scenario from the test specification will be implemented as actual test code. It
bridges the gap between Given/When/Then scenarios (human-readable behavior
descriptions) and executable test functions, providing a technical blueprint for
test structure, frameworks, fixtures, and assertion strategies.

## Core Principles

### 1. Test Scenarios Drive the Structure

Every test scenario from the test specification must have a corresponding test
implementation approach. The test specification defines WHAT to verify; the test
implementation specification defines HOW to verify it. No test scenario may be
left unaddressed.

> GitHub's [spec-kit](https://github.com/github/spec-kit) project demonstrates
> how formal specifications serve as the source of truth for test design
> decisions, ensuring tests stay aligned with documented behavior.

### 2. Tests Must Initially Fail

The test implementation specification is written BEFORE the feature code exists.
All tests derived from this specification must fail when first implemented,
confirming they actually test the intended behavior. A test that passes before
the feature is implemented is not testing anything useful.

### 3. Language-Aware, Not Language-Prescriptive

Use test frameworks, patterns, and idioms appropriate for the project's detected
stack. Do not prescribe specific test libraries unless the project already uses
them. The detected stack informs suggestions; it does not constrain choices.

> Thoughtworks identifies this balance in their analysis of
> [spec-driven development](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices):
> specifications should constrain behavior, not technology choices.

### 4. Test Behavior, Not Implementation

Tests describe expected behavior from the outside. They should not depend on
internal implementation details, private methods, or specific data structures.
A well-written test remains valid regardless of how the feature is implemented,
as long as the behavior matches the specification.

## Required Sections

A test implementation specification must contain these sections. Each section
has a specific purpose in ensuring traceability and completeness.

### Test Framework & Conventions

Identify the test framework and conventions for the detected stack:

- **Python**: pytest, unittest, or nose2. Fixtures via conftest.py or setUp/
  tearDown. Assertion style (assert statements vs self.assert methods).
- **TypeScript/JavaScript**: Jest, Vitest, Mocha, or Playwright. Describe/it
  nesting, beforeEach/afterEach, assertion library (expect, chai, assert).
- **Go**: Standard testing package, testify, or gomega. Table-driven test
  patterns, test helper functions, t.Run subtests.
- **Java/Kotlin**: JUnit 5, TestNG, or Kotest. Annotations, lifecycle methods,
  assertion libraries (AssertJ, Hamcrest).
- **Rust**: Built-in test module, or external crates (rstest, proptest).
  #[test] attributes, Result-based test functions, assertion macros.

State which framework the project already uses. If no tests exist yet,
recommend the most common framework for the stack.

### Test Structure

Describe how test files and test functions are organized:

- **File organization**: Where test files live (co-located, separate test
  directory, mirrored source structure). Follow existing project conventions.
- **Test grouping**: How tests are grouped (by user story, by functional area,
  by test scenario category). Map to the test specification's grouping.
- **Naming conventions**: Test function/method naming pattern. Names should
  reflect the behavior being tested, not implementation details.
  - Good: `test_rejects_duplicate_email`, `it("returns 404 for unknown user")`
  - Bad: `test_validate_method`, `it("calls the database")`

### Test Scenario Mapping

This is the critical alignment artifact. Map every test scenario from the test
specification to a specific test function, class, or module.

Format:

```
| Test Scenario ID | Scenario Title              | Test Function/Method                    |
|------------------|-----------------------------|-----------------------------------------|
| TS-001           | Create user with valid input | test_create_user_with_valid_input()     |
| TS-002           | Reject duplicate email       | test_rejects_duplicate_email()          |
| TS-003           | Validate email format        | test_rejects_invalid_email_format()     |
| EC-001           | Empty name rejected          | test_rejects_empty_display_name()       |
```

For each mapping, describe:
- **Setup (Given)**: How preconditions are established -- fixtures, factories,
  mocks, database seeding, or API stubs.
- **Action (When)**: How the action under test is triggered -- function call,
  HTTP request, event dispatch, or CLI invocation.
- **Assertion (Then)**: What is checked and how -- return values, side effects,
  error types, status codes, database state, or event emissions.

Rules for this mapping:
- Every test scenario ID from the test specification must appear exactly once
- A test function may cover only one test scenario (one behavior per test)
- If a test scenario cannot be mapped, flag it as a gap
- If a test scenario requires testing internal implementation details, flag it
  as a design concern and recommend testing the behavior instead

### Fixtures & Test Data

Describe shared test infrastructure:

- **Fixtures**: Shared setup that multiple tests use (database connections, API
  clients, authenticated sessions, mock servers). State lifecycle (per-test,
  per-module, per-session).
- **Test data factories**: How test data is created (factory functions, builder
  patterns, fixture files, or inline construction). Prefer factories over
  hardcoded values.
- **Mocks and stubs**: What external dependencies are mocked and how. State the
  mocking strategy (dependency injection, monkey patching, test doubles,
  interface-based mocking). Mock boundaries should align with the behavioral
  specification's scope.
- **Setup/teardown**: What happens before and after each test or test group.
  Ensure tests are isolated -- no test should depend on another test's state.

### Alignment Check

An explicit statement confirming the test implementation approach addresses all
test scenarios. This section has three possible outcomes:

1. **Full alignment**: Every test scenario is mapped to a test function with
   setup, action, and assertion defined. Proceed to test implementation.
2. **Gaps identified**: Some test scenarios lack a test implementation approach.
   List them. These must be resolved before proceeding.
3. **Design concerns**: Some test scenarios may be difficult to test without
   coupling to implementation details. List them with recommended alternatives
   that test behavior instead.

## Alignment Verification Process

Follow this process to verify the test implementation specification is complete
and consistent:

**Step 1 -- Walk the test scenarios.** Read each test scenario from the test
specification sequentially. For each one, locate its entry in the Test Scenario
Mapping table.

**Step 2 -- Verify test isolation.** For each mapped test, confirm it can run
independently. No test should depend on the execution order or side effects of
another test.

**Step 3 -- Flag gaps.** Any test scenario without a mapping entry is a
coverage gap. Record it in the Alignment Check section.

**Step 4 -- Flag implementation coupling.** Any test that requires knowledge of
internal implementation details (private methods, specific data structures,
internal state) is coupled to implementation. Recommend testing the observable
behavior instead.

**Step 5 -- Verify initial failure.** Confirm that the test implementation
approach will produce failing tests when no feature code exists. If a test would
pass without any feature code (e.g., testing a default value that already
exists), flag it for review.

## Language-Aware Test Patterns

The skill auto-detects the project stack by scanning for manifest files
(`package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
`pom.xml`, `build.gradle`, `*.csproj`). Use the detected stack to inform --
but not dictate -- the following:

**Test framework**: Use the project's existing test framework. If none exists,
recommend the ecosystem default (pytest for Python, Jest/Vitest for JS/TS,
testing package for Go, JUnit 5 for Java, built-in test for Rust).

**Assertion style**: Match the project's assertion conventions. Do not mix
assertion libraries within a project.

**Mocking strategy**: Match the project's existing approach. If the project
uses dependency injection, describe test doubles. If it uses monkey patching,
describe patches. Do not introduce a different mocking paradigm.

**Test organization**: Follow the project's existing test directory structure
and naming patterns. Do not reorganize existing tests.

## Handoff Prompt Generation

When the test implementation specification is complete and passes its advisory
quality gate, offer to generate a handoff prompt for the coding agent. The
prompt must be self-contained -- a coding agent with no prior context should be
able to execute it.

Template:

```
Implement the tests for the <feature> feature according to the test
implementation specification.

References:
- Test specification: docs/specs/<feature>-test-specification.md
- Test implementation specification: docs/specs/<feature>-test-implementation-specification.md

Constraint: All tests MUST FAIL when first run, because the feature code does
not exist yet. A passing test before feature implementation indicates the test
is not testing the intended behavior. After implementing all tests, run them
and confirm they all fail.

Stack: <detected language/framework>
Test framework: <detected test framework>
Conventions: <project test patterns observed, e.g., "pytest with conftest.py
fixtures", "Jest with describe/it blocks", "table-driven tests in Go">

Start by reading both specification files, then implement each test function
described in the test implementation specification.
```

## Anti-Patterns

### Testing Implementation Details

Tests should verify observable behavior, not internal mechanics. Testing that
a specific private method was called, or that data is stored in a specific
internal structure, creates brittle tests that break during refactoring even
when behavior is preserved.

### Shared Mutable State Between Tests

Tests that share mutable state (global variables, class-level state, database
rows from other tests) create order-dependent failures. Each test must set up
its own preconditions and clean up after itself.

### Over-Mocking

Mocking every dependency creates tests that verify mock behavior rather than
real behavior. Mock at system boundaries (external APIs, databases, file
systems) but let internal components interact naturally when possible.

### Tests That Cannot Fail

A test that passes regardless of the implementation is not testing anything. The
"verify initial failure" step catches this: if a test passes before the feature
is implemented, the test needs rework.

### One Test Per Scenario Violation

Combining multiple test scenarios into a single test function makes failures
ambiguous. When a combined test fails, it is unclear which behavior is broken.
Each test scenario from the test specification maps to exactly one test function.
