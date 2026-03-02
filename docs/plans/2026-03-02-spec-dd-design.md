# spec-dd: Specification-Driven Development Skill

## Overview

`spec-dd` is a Claude Code plugin skill that orchestrates a specification-driven development workflow. It acts as a workflow navigator and quality assessor — guiding users through writing behavioral specifications, deriving test scenarios, planning implementation, and verifying alignment across all artifacts and code.

The skill does not generate production code or test code itself. It produces specification documents, assesses quality, surfaces gaps, and offers handoff prompts for coding agents when it's time to write actual code.

## Motivation

Specification-Driven Development (SDD) extends the "spec first" principle from TDD to create formal behavioral contracts before implementation. While TDD operates at the unit level with tight second-by-second cycles, SDD operates at the feature level — defining what the system does, deriving how to verify it, then implementing to satisfy those verifications.

The core discipline: **tests are a firewall between specification and implementation.** You never modify tests during implementation — if the code can't pass the tests, the implementation approach is wrong, not the tests.

Key references:
- [Addy Osmani - How to write a good spec for AI agents](https://addyosmani.com/blog/good-spec/)
- [GitHub spec-kit](https://github.com/github/spec-kit)
- [Thoughtworks - Spec-driven development](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)
- [InfoQ - Spec Driven Development: When Architecture Becomes Executable](https://www.infoq.com/articles/spec-driven-development/)
- [Martin Fowler - Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)

## Plugin Structure

```
plugins/spec-dd/
  .claude-plugin/
    plugin.json
  skills/
    spec-dd/
      SKILL.md                                # Main workflow logic + phase router
      references/
        specification.md                      # How to write/review behavioral specs
        test-specification.md                 # How to derive/review test scenarios
        test-implementation-specification.md  # How to map test scenarios to test code
        review.md                             # How to verify alignment + produce report
```

## Invocation

| Command | Purpose |
|---------|---------|
| `/spec-dd` | Auto-detect phase, assess current state, recommend next step |
| `/spec-dd:spec` | Work on the behavioral specification |
| `/spec-dd:test` | Work on the test specification |
| `/spec-dd:test-impl` | Work on the test implementation specification |
| `/spec-dd:review` | Run alignment review and produce report |

All commands accept an optional feature name argument (e.g., `/spec-dd:spec user-auth`). If no feature name is provided and multiple features exist, the skill lists available features and asks the user to choose.

## Artifacts

All artifacts live in `docs/specs/` per feature:

```
docs/specs/
  <feature>-specification.md
  <feature>-test-specification.md
  <feature>-test-implementation-specification.md
  <feature>-implementation-review.md
```

## Workflow Phases

The skill manages 6 logical phases. It actively guides phases 1, 2, 3, and 6. For phases 4 and 5 (actual code writing), it acts as a handoff point — proposing prompts and later verifying results.

### Phase 1: Behavioral Specification (`/spec-dd:spec`)

**Purpose:** Define what the system does — behavioral contracts, not implementation details.

**The skill:**
- Guides the user through writing the specification
- Reviews for ambiguity: vague language ("fast", "secure", "easy"), missing edge cases, undefined terms, implicit assumptions
- Marks unresolved items with `[NEEDS CLARIFICATION]`
- Checks completeness: are all user stories covered? Are acceptance criteria measurable?

**Advisory gate:** No unresolved `[NEEDS CLARIFICATION]` markers before proceeding.

**Artifact template:**
```markdown
# <Feature> - Behavioral Specification

## Objective
What this feature does and why it exists.

## User Stories & Acceptance Criteria
Numbered user stories, each with measurable acceptance criteria.

## Constraints
Technical, business, or regulatory constraints.

## Edge Cases
Boundary conditions, error states, unusual inputs.

## Non-Goals
What this feature explicitly does NOT do.

## Open Questions
Items marked [NEEDS CLARIFICATION] that must be resolved.
```

### Phase 2: Test Specification (`/spec-dd:test`)

**Purpose:** Derive test scenarios from the behavioral spec only — no implementation knowledge.

**The skill:**
- Derives Given/When/Then scenarios from each acceptance criterion
- Enforces one behavior per scenario, one action per step
- Builds a coverage matrix mapping every spec requirement to test scenarios
- Language-aware: understands the project's testing ecosystem to ensure scenarios are realistic and testable
- Checks traceability: every acceptance criterion has at least one test scenario

**Advisory gate:** Full traceability between spec requirements and test scenarios.

**Artifact template:**
```markdown
# <Feature> - Test Specification

## Coverage Matrix
Table mapping each acceptance criterion to its test scenarios.

## Test Scenarios
Given/When/Then format. Grouped by user story or functional area.

## Edge Case Scenarios
Boundary conditions derived from the specification's edge cases section.

## Traceability
Summary confirming every acceptance criterion is covered.
```

### Phase 3: Test Implementation Specification (`/spec-dd:test-impl`)

**Purpose:** Map every test scenario to a technical approach for test implementation.

**The skill:**
- Guides the user through describing the technical approach for implementing each test scenario as actual test code
- Language-aware: test framework selection, fixture strategies, mock/stub approaches, test file organization for the detected stack
- Maps every test scenario to specific test functions, classes, or modules
- Describes shared fixtures, test data factories, and setup/teardown strategies
- Verifies completeness: every Given/When/Then scenario has a test implementation approach

**Advisory gate:** Every test scenario mapped to a test implementation approach.

**Artifact template:**
```markdown
# <Feature> - Test Implementation Specification

## Test Framework & Conventions
Detected stack, test framework, test runner, conventions.

## Test Structure
How tests are organized: files, classes/modules, naming conventions.

## Test Scenario Mapping
Map each test scenario to a test function/method with setup and assertion strategy.

## Fixtures & Test Data
Shared fixtures, factories, test data approach, setup/teardown.

## Alignment Check
Confirmation that every test scenario has a test implementation approach.
```

### Phase 4: Test Implementation (Handoff)

**Purpose:** Actual test code is written by a coding agent. Tests must initially FAIL because the feature code does not exist yet.

**The skill:**
- Announces readiness for test implementation
- Offers to propose a prompt for the coding agent that references both `docs/specs/<feature>-test-specification.md` and `docs/specs/<feature>-test-implementation-specification.md`
- The prompt instructs the agent to implement tests and verify they all FAIL (since feature code doesn't exist yet)
- Does not write test code itself

### Phase 5: Feature Implementation (Handoff)

**Purpose:** Production code is written to make all tests pass.

**The skill:**
- Announces readiness for feature implementation
- Offers to propose a prompt for the coding agent that references the behavioral specification and the test files
- The prompt instructs the agent to write code that makes all tests pass without modifying any test files
- Does not write implementation code itself

### Phase 6: Review (`/spec-dd:review`)

**Purpose:** Verify alignment across all artifacts and actual code.

**The skill:**
- Checks document alignment: specification <-> test specification <-> test implementation specification
- Checks code alignment: actual test files and source code against the spec documents
- **Runs tests:** Detects the project's test runner (Makefile, justfile, package.json scripts, pytest, go test, cargo test, etc.) and executes all available tests locally. Reports pass/fail results.
- Identifies: coverage gaps, misalignments, unresolved ambiguities, undocumented behavior
- Produces a review report

**Artifact template:**
```markdown
# <Feature> - Implementation Review

## Specification Alignment
Cross-check between the three spec documents.

## Code Alignment
Actual test code vs test implementation specification. Actual feature code vs behavioral specification.

## Test Execution
Test runner detected, command used, pass/fail results, failure details if any.

## Coverage Report
Gaps, misalignments, unresolved items.

## Status
Pass/fail summary per check.

## Recommendations
Next steps if issues are found.
```

## Auto-Detect Router (`/spec-dd`)

When invoked without a specific phase:

1. **Scan `docs/specs/`** for `*-specification.md` files to discover features
2. **Select feature** — use argument if provided, otherwise list features and ask
3. **Assess phase status** for the selected feature:
   - Does `<feature>-specification.md` exist? Any `[NEEDS CLARIFICATION]` markers? Ambiguity issues?
   - Does `<feature>-test-specification.md` exist? Does it cover all acceptance criteria from Phase 1?
   - Do actual test files exist in the project? Do they align with the test spec?
   - Does `<feature>-test-implementation-specification.md` exist? Does it address all test scenarios?
   - Do actual test files exist? Do they fail (feature not yet implemented)?
   - Does actual implementation code exist? Do the tests pass?
   - Does `<feature>-implementation-review.md` exist? Is it current?
4. **Report current state** — which phases are done, which have gaps
5. **Recommend next action** — either fix gaps in an earlier phase or proceed to the next one
6. **If at a handoff phase** — offer to propose a prompt for the coding agent

## Quality Gates

All gates are **advisory** — the skill flags issues and recommends addressing them, but the user can override and proceed.

| Transition | Gate Check |
|------------|-----------|
| Spec -> Test Spec | No unresolved `[NEEDS CLARIFICATION]` markers |
| Test Spec -> Test Impl Spec | Full traceability: every acceptance criterion mapped to test scenarios |
| Test Impl Spec -> Test Impl | Every test scenario mapped to a test implementation approach |
| Test Impl -> Feature Impl | Test files exist and all tests FAIL (feature not yet implemented) |
| Feature Impl -> Review | Implementation code exists and tests pass |
| Review -> Done | All checks pass in the review report |

## Language Awareness

The skill auto-detects the project's language and ecosystem by scanning for manifest files (package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, pom.xml, build.gradle, etc.).

This context is used when:
- **Reviewing test specifications** — ensuring scenarios are realistic for the test framework
- **Reviewing test implementation specifications** — using appropriate test patterns and idioms
- **Checking code alignment** — understanding file conventions and test structures
- **Proposing handoff prompts** — referencing the correct framework and conventions

## Iterative Workflow Support

The skill supports non-linear progression:
- The auto-detect router can recommend going back to an earlier phase when it finds gaps
- Any phase can be re-entered at any time via explicit sub-commands
- Artifacts are updated in place — the skill works with whatever state exists
- Starting rough and iterating is explicitly supported: write a quick spec, rough test scenarios, then refine both before proceeding

## Reference Files

Each reference file in `references/` guides the skill on how to perform a specific phase:

### `references/specification.md`
- How to write unambiguous behavioral requirements
- Ambiguity detection checklist: lexical, syntactic, semantic, pragmatic types
- Required sections and their purpose
- `[NEEDS CLARIFICATION]` convention
- Examples of good vs bad specification language
- Quality criteria: completeness, clarity, measurability, testability

### `references/test-specification.md`
- How to derive test scenarios from behavioral specs without implementation knowledge
- Given/When/Then format rules and best practices
- One behavior per scenario, one action per step
- Coverage traceability techniques
- Language-aware review: what to check per ecosystem
- Anti-patterns: testing implementation details, combining multiple behaviors

### `references/test-implementation-specification.md`
- How to map test scenarios to a technical approach for test implementation
- Test framework selection and fixture strategies per ecosystem
- Test scenario mapping: every scenario maps to a test function/method
- Language-aware test patterns and mocking strategies
- Handoff prompt generation: how to instruct a coding agent to write tests

### `references/review.md`
- Cross-artifact alignment checks (spec <-> test spec <-> test impl spec)
- Code scanning: verifying actual test and implementation files against specs
- Report format and status conventions
- Conformance testing principles
- Identifying undocumented behavior (code not covered by specs)
