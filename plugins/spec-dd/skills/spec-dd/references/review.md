# Alignment Review — Reference Guide

> "A specification that is never verified against the implementation is just
> documentation — and documentation lies."
> — Addy Osmani, [Writing Good Specs](https://addyosmani.com/blog/good-spec/)

## Core Principles

The alignment review is the final quality check in specification-driven
development. It verifies that all artifacts — behavioral specification, test
specification, test implementation specification — are consistent with each
other AND with the actual code in the project (both test code and feature code).

Alignment operates across three layers:

1. **Spec <-> Test Spec** — Do the test scenarios fully cover the behavioral
   requirements?
2. **Test Spec <-> Test Impl Spec** — Does the test implementation plan address
   every test scenario?
3. **Specs <-> Actual Code** — Does the test code and feature code match what
   the specifications describe?

Gaps can exist in both directions. Missing coverage (a spec requirement with no
test) is as important as undocumented behavior (code that no spec describes).
Conformance testing treats specifications as the source of truth — deviations
in the code are bugs, not features
([InfoQ — Spec-Driven Development](https://www.infoq.com/articles/spec-driven-development/)).

## Document Alignment Checks

### Specification <-> Test Specification

| Check | What to verify |
|-------|---------------|
| **Coverage** | Every acceptance criterion in the spec has at least one test scenario |
| **Traceability** | Every test scenario traces back to a numbered spec requirement — no orphan tests |
| **Edge cases** | Edge cases listed in the spec are covered by dedicated test scenarios |
| **Non-goals** | Non-goals from the spec are NOT tested, unless as explicit negative tests ("the system does NOT do X") |

Walk the coverage matrix in the test specification. Every spec requirement ID
should appear. Requirements with no corresponding test scenario are gaps.
Test scenarios that reference no spec requirement are orphans.

### Test Specification <-> Test Implementation Specification

| Check | What to verify |
|-------|---------------|
| **Scenario coverage** | Every test scenario has a corresponding test implementation approach |
| **Test isolation** | Each test can run independently without depending on other tests |
| **No orphan tests** | No test implementation exists without a corresponding test scenario |

Walk the test scenario mapping table in the test implementation specification.
Every test scenario ID from the test spec should appear. Test implementations
that reference no spec scenario are orphans.

### Specification <-> Test Implementation Specification

| Check | What to verify |
|-------|---------------|
| **Constraints respected** | The test approach is consistent with constraints in the behavioral spec (performance, platform, regulatory) |
| **Non-goals respected** | Non-goals from the spec are not tested, unless as explicit negative tests |

## Code Alignment Checks

Code alignment verifies that the actual project source matches the
specifications. This requires scanning the project for test files and
implementation files related to the feature.

### Actual Test Code vs Test Specification

- Scan the project for test files related to the feature (by name, imports,
  or directory structure).
- Check that each test scenario from the test spec has a corresponding test
  function or method in the code.
- **Flag undocumented tests:** test functions that do not correspond to any
  test scenario. These may be valid additions, but they should be documented
  in the test specification.
- **Flag unimplemented tests:** test scenarios from the test spec with no
  corresponding test code. These are coverage gaps.

### Actual Test Code vs Test Implementation Specification

- Scan the project for test files related to the feature.
- Check that test functions described in the test impl spec exist in the code.
- **Flag undocumented tests:** test functions that do not correspond to any
  entry in the test impl spec. These may be valid additions but should be
  documented.
- **Flag unimplemented test specs:** test impl spec entries with no
  corresponding test code. These are coverage gaps.

### Actual Feature Code vs Behavioral Specification

- Verify that all tests pass (requires running the test suite — see below).
- Flag implementation behavior not covered by any test.

## Test Execution

Detect the test runner by scanning for known configuration files:

| Indicator | Runner command |
|-----------|---------------|
| `Makefile` with test target | `make test` |
| `justfile` with test recipe | `just test` |
| `package.json` with `test` script | `npm test` or `yarn test` |
| `pytest.ini`, `pyproject.toml` (pytest), `conftest.py` | `pytest` |
| `go.mod` | `go test ./...` |
| `Cargo.toml` | `cargo test` |
| `pom.xml` | `mvn test` |
| `build.gradle` or `build.gradle.kts` | `gradle test` |

**Steps:** Detect the runner. Run the full suite (or feature subset). Record
total/passed/failed/skipped. For failures, capture the test name, assertion
message, and stack trace. If the suite cannot be run (missing dependencies,
environment issues), note this and proceed with document-level checks only.

## Severity Classification

Every finding in the review is classified by severity:

### CRITICAL

Findings that indicate a fundamental alignment failure. The specifications or
code must be revised before the feature can be considered complete.

- A spec requirement has no test coverage at all
- Implementation contradicts a spec constraint
- Tests fail and the failure traces to a spec-code mismatch
- A non-goal from the spec is implemented in the code

### WARNING

Findings that indicate a minor misalignment or documentation gap. These should
be addressed but do not block completion.

- Undocumented behavior in the code (code exists but is not in any spec)
- Orphan tests that do not trace to any spec requirement
- Minor inconsistencies in naming or structure between specs and code
- Test scenarios that are overly broad or combine multiple behaviors

### INFO

Suggestions for improvement that do not represent alignment failures.

- Opportunities to improve test scenario clarity
- Stylistic inconsistencies across specification documents
- Suggestions for additional edge case coverage beyond the current spec

## When to Recommend Going Back

The review may recommend revisiting an earlier phase based on findings:

| Finding severity | Affected layer | Recommendation |
|-----------------|----------------|----------------|
| CRITICAL | Spec <-> Test Spec | Revisit Phase 1 (specification) or Phase 2 (test specification) |
| CRITICAL | Test Spec <-> Test Impl Spec | Revisit Phase 3 (test implementation specification) |
| CRITICAL | Test code alignment | Revisit Phase 4 (test implementation handoff) — the test code needs rework |
| CRITICAL | Feature code alignment | Revisit Phase 5 (feature implementation handoff) — the feature code needs rework |
| WARNING only | Any layer | Note findings in the report but do not block completion |

CRITICAL findings mean the feature is not ready. The review report should
clearly state which phase to revisit and what specific issue must be resolved.

WARNING-only results mean the feature is substantially complete. The warnings
should be documented for future iteration but do not require immediate action.

## Review Report Format

The review produces a markdown report at `docs/specs/<feature>-implementation-review.md`.
Use this template:

```markdown
# <Feature> — Implementation Review

| Field | Value |
|-------|-------|
| Feature | <feature name> |
| Date | <today's date> |
| Status | PASS / ISSUES FOUND |

## Specification Alignment

| Check | Status | Details |
|-------|--------|---------|
| Spec -> Test Spec coverage | PASS/FAIL | <summary of gaps or "Full coverage"> |
| Test Spec -> Spec traceability | PASS/FAIL | <orphan tests or "All traced"> |
| Test Spec -> Test Impl Spec coverage | PASS/FAIL | <unmapped scenarios or "All mapped"> |
| Test Impl Spec -> Test Spec (no orphans) | PASS/FAIL | <orphan test impl or "No orphans"> |
| Spec constraints respected | PASS/FAIL | <violated constraints or "All respected"> |
| Non-goals respected | PASS/FAIL | <scope creep or "No scope creep"> |

## Code Alignment

| Check | Status | Details |
|-------|--------|---------|
| Test code vs Test Impl Spec | PASS/FAIL | <unimplemented or undocumented tests> |
| Feature code vs Behavioral Spec | PASS/FAIL | <unimplemented or undocumented code> |
| Undocumented behavior | PASS/FAIL | <untested code paths or "None found"> |

## Test Execution

| Metric | Value |
|--------|-------|
| Total tests | <count> |
| Passed | <count> |
| Failed | <count> |
| Skipped | <count> |
| Runner | <detected runner command> |

### Failures (if any)

- **<test name>**: <assertion message / reason>

## Coverage Report

### Gaps (spec requirements without test or implementation)
- <list gaps or "None">

### Misalignments (contradictions between artifacts)
- <list misalignments or "None">

### Unresolved Items
- <list [NEEDS CLARIFICATION] markers still present or "None">

## Findings

| # | Severity | Layer | Description |
|---|----------|-------|-------------|
| 1 | CRITICAL/WARNING/INFO | <which alignment layer> | <description> |

## Recommendations

- <actionable recommendation with phase reference>
```

## Review Checklist

- [ ] Read all three specification documents for the feature
- [ ] Build coverage matrix: spec requirements -> test scenarios -> test impl approaches
- [ ] Check for orphan tests and orphan test implementations
- [ ] Verify non-goals are not implemented
- [ ] Scan project for actual test and source files; verify against specs
- [ ] Run the test suite and record results
- [ ] Classify all findings by severity
- [ ] Produce the review report
- [ ] If CRITICAL findings exist, recommend which phase to revisit
