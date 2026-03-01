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
        implementation-specification.md       # How to write/review impl specs
        review.md                             # How to verify alignment + produce report
```

## Invocation

| Command | Purpose |
|---------|---------|
| `/spec-dd` | Auto-detect phase, assess current state, recommend next step |
| `/spec-dd:spec` | Work on the behavioral specification |
| `/spec-dd:test` | Work on the test specification |
| `/spec-dd:impl` | Work on the implementation specification |
| `/spec-dd:review` | Run alignment review and produce report |

All commands accept an optional feature name argument (e.g., `/spec-dd:spec user-auth`). If no feature name is provided and multiple features exist, the skill lists available features and asks the user to choose.

## Artifacts

All artifacts live in `docs/specs/` per feature:

```
docs/specs/
  <feature>-specification.md
  <feature>-test-specification.md
  <feature>-implementation-specification.md
  <feature>-implementation-review.md
```

## Workflow Phases

The skill manages 6 logical phases. It actively guides phases 1, 2, 4, and 6. For phases 3 and 5 (actual code writing), it acts as a handoff point — proposing prompts and later verifying results.

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

### Phase 3: Test Code (Handoff)

**Purpose:** Actual test code is written following the test specification.

**The skill:**
- Announces readiness for test implementation
- Offers to propose a prompt for the coding agent that references `docs/specs/<feature>-test-specification.md`
- The prompt instructs the agent to use the project's test framework and conventions
- Does not write test code itself

### Phase 4: Implementation Specification (`/spec-dd:impl`)

**Purpose:** Technical approach for satisfying each test scenario.

**The skill:**
- Guides the user through describing the implementation approach
- Language-aware: uses appropriate patterns, idioms, and architecture for the detected stack (auto-detected from project manifest files like package.json, requirements.txt, go.mod, Cargo.toml, etc.)
- Verifies every test scenario has a corresponding implementation approach
- Checks that the approach does not require modifying existing tests

**Advisory gate:** Implementation spec addresses all test scenarios without requiring test modifications.

**Artifact template:**
```markdown
# <Feature> - Implementation Specification

## Technical Approach
High-level design decisions and rationale.

## Component Design
Language-aware patterns and idioms for the detected stack.

## Test Scenario Mapping
How each test scenario from the test specification will be satisfied.

## Dependencies & Constraints
External dependencies, performance constraints, integration points.

## Alignment Check
Confirmation that no test modifications are needed.
```

### Phase 5: Implementation Code (Handoff)

**Purpose:** Actual implementation code is written following the implementation specification.

**The skill:**
- Announces readiness for implementation
- Offers to propose a prompt for the coding agent that references `docs/specs/<feature>-implementation-specification.md`
- The prompt instructs the agent to implement code that passes all tests without modifying them
- Does not write implementation code itself

### Phase 6: Review (`/spec-dd:review`)

**Purpose:** Verify alignment across all artifacts and actual code.

**The skill:**
- Checks document alignment: specification <-> test specification <-> implementation specification
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
Actual test code vs test specification. Actual implementation vs implementation specification.

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
   - Does `<feature>-implementation-specification.md` exist? Does it address all test scenarios?
   - Does actual implementation code exist? Does it align with the impl spec?
   - Does `<feature>-implementation-review.md` exist? Is it current?
4. **Report current state** — which phases are done, which have gaps
5. **Recommend next action** — either fix gaps in an earlier phase or proceed to the next one
6. **If at a handoff phase** — offer to propose a prompt for the coding agent

## Quality Gates

All gates are **advisory** — the skill flags issues and recommends addressing them, but the user can override and proceed.

| Transition | Gate Check |
|------------|-----------|
| Spec -> Test Spec | No unresolved `[NEEDS CLARIFICATION]` markers |
| Test Spec -> Test Code | Full traceability: every acceptance criterion mapped to test scenarios |
| Test Code -> Impl Spec | Test files exist and align with test specification |
| Impl Spec -> Impl Code | Every test scenario has a corresponding implementation approach; no test modifications required |
| Impl Code -> Review | Implementation code exists |
| Review -> Done | All checks pass in the review report |

## Language Awareness

The skill auto-detects the project's language and ecosystem by scanning for manifest files (package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, pom.xml, build.gradle, etc.).

This context is used when:
- **Reviewing test specifications** — ensuring scenarios are realistic for the test framework
- **Reviewing implementation specifications** — using appropriate patterns and idioms
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

### `references/implementation-specification.md`
- How to describe a technical approach that satisfies test scenarios
- Alignment verification: every test scenario maps to an implementation approach
- Language-aware patterns and idioms guidance
- Constraint enforcement: implementation must not require modifying tests
- Handoff prompt generation: how to instruct a coding agent

### `references/review.md`
- Cross-artifact alignment checks (spec <-> test spec <-> impl spec)
- Code scanning: verifying actual test and implementation files against specs
- Report format and status conventions
- Conformance testing principles
- Identifying undocumented behavior (code not covered by specs)
