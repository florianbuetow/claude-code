---
name: spec-dd
description: >
  This skill should be used when the user asks to "write specifications",
  "create test specifications", "specification-driven development", "spec-first",
  "behavioral specs", "derive test scenarios", "implementation specification",
  "check specification alignment", "review specs", or "spec-dd". Also triggers
  when the user mentions "SDD", "spec-driven", "behavioral testing workflow",
  "test-first design", or asks about writing specifications before code,
  deriving tests from specs, or verifying implementation against specifications.
  Supports a full workflow walkthrough or focusing on individual phases.
---

# Specification-Driven Development

Orchestrate a spec-first development workflow: behavioral specification, test
scenario derivation, implementation planning, and cross-artifact alignment
review. The skill guides writing behavioral specifications, derives test
scenarios, plans implementation approaches, and verifies alignment across all
artifacts and code. Quality gates between phases are advisory — the skill flags
issues and recommends addressing them, but the user can override and proceed.

## Commands

| Command | Phase | Reference |
|---------|-------|-----------|
| `/spec-dd` | Auto-detect phase, assess state, recommend next step | All references |
| `/spec-dd:spec` | Behavioral Specification | `references/specification.md` |
| `/spec-dd:test` | Test Specification | `references/test-specification.md` |
| `/spec-dd:impl` | Implementation Specification | `references/implementation-specification.md` |
| `/spec-dd:review` | Alignment Review | `references/review.md` |

All commands accept an optional feature name argument (e.g., `/spec-dd:spec user-auth`).
If no feature name is provided and multiple features exist, list available features and
ask the user to choose.

## Artifacts

All artifacts live in `docs/specs/` with one set of files per feature:

| Artifact | Filename |
|----------|----------|
| Behavioral Specification | `docs/specs/<feature>-specification.md` |
| Test Specification | `docs/specs/<feature>-test-specification.md` |
| Implementation Specification | `docs/specs/<feature>-implementation-specification.md` |
| Implementation Review | `docs/specs/<feature>-implementation-review.md` |

## First Steps

When any command is invoked:

1. **Read the relevant reference file** from `references/` BEFORE doing anything else.
   - `/spec-dd:spec` -> read `references/specification.md`
   - `/spec-dd:test` -> read `references/test-specification.md`
   - `/spec-dd:impl` -> read `references/implementation-specification.md`
   - `/spec-dd:review` -> read `references/review.md`
   - `/spec-dd` -> read whichever reference applies to the recommended phase

2. **Auto-detect project language** by scanning for manifest files:
   - `package.json` (JavaScript/TypeScript)
   - `requirements.txt`, `pyproject.toml` (Python)
   - `go.mod` (Go)
   - `Cargo.toml` (Rust)
   - `pom.xml`, `build.gradle` (Java/Kotlin)
   - Use the detected language/ecosystem to inform testing frameworks, patterns,
     idioms, and handoff prompts throughout the workflow.

3. **For `/spec-dd` (router):** Follow the auto-detect router logic below.

4. **For `/spec-dd:<phase>`:** Check whether prior-phase artifacts exist. If gaps
   are found, advise the user which earlier phase to complete first, but do not
   block — proceed if the user chooses to continue.

## Phase 1: Behavioral Specification (`/spec-dd:spec`)

**Reference:** Read `references/specification.md` before starting.

**Purpose:** Define what the system does — behavioral contracts, not implementation
details.

**Workflow:**

1. Guide the user through creating or reviewing the behavioral specification for
   the selected feature.
2. Use selectable options plus a free-text escape for every question. Ask 1-3
   questions per turn, grouped thematically. Summarize captured answers before
   moving on.
3. Review for ambiguity:
   - Vague language ("fast", "secure", "easy", "simple", "efficient")
   - Missing edge cases and boundary conditions
   - Undefined terms and implicit assumptions
   - Unmeasurable acceptance criteria
4. Mark any unresolved items with `[NEEDS CLARIFICATION]`.
5. Produce or update `docs/specs/<feature>-specification.md`.

**Advisory gate:** No unresolved `[NEEDS CLARIFICATION]` markers before proceeding
to Phase 2.

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

## Phase 2: Test Specification (`/spec-dd:test`)

**Reference:** Read `references/test-specification.md` before starting.

**Purpose:** Derive test scenarios from the behavioral spec only — no implementation
knowledge.

**Pre-check:** Verify that `<feature>-specification.md` exists. If it does not,
advise the user to complete Phase 1 first. If the user chooses to proceed anyway,
note the risk and continue.

**Workflow:**

1. Derive Given/When/Then scenarios from each acceptance criterion in the
   behavioral specification.
2. Enforce one behavior per scenario, one action per step.
3. Build a coverage matrix mapping every spec requirement to test scenarios.
4. Language-aware review: ensure scenarios are realistic and testable for the
   project's detected testing ecosystem.
5. Check traceability: every acceptance criterion must have at least one test
   scenario.
6. Produce or update `docs/specs/<feature>-test-specification.md`.

**Advisory gate:** Full traceability between spec requirements and test scenarios
before proceeding to Phase 3.

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

## Phase 3: Test Code (Handoff)

**Purpose:** Actual test code is written by a coding agent following the test
specification. This skill does NOT write test code.

**Workflow:**

1. Announce readiness for test implementation.
2. Summarize what the test specification contains and where it lives
   (`docs/specs/<feature>-test-specification.md`).
3. Offer to propose a prompt for the coding agent. The prompt should:
   - Reference the test specification document
   - Instruct the agent to use the project's test framework and conventions
   - Specify the detected language and ecosystem
4. Wait for test code to be written before proceeding.

## Phase 4: Implementation Specification (`/spec-dd:impl`)

**Reference:** Read `references/implementation-specification.md` before starting.

**Purpose:** Describe the technical approach for satisfying each test scenario.

**Pre-check:** Verify that `<feature>-test-specification.md` exists and that
actual test files exist in the project. If either is missing, advise the user
which prior phase to complete first. Proceed if the user overrides.

**Workflow:**

1. Guide the user through describing the implementation approach for the
   selected feature.
2. Use language-aware patterns, idioms, and architecture appropriate for the
   detected stack.
3. Map every test scenario from the test specification to a corresponding
   implementation approach.
4. Verify that the approach does not require modifying existing tests — tests
   are a firewall between specification and implementation.
5. Produce or update `docs/specs/<feature>-implementation-specification.md`.

**Advisory gate:** Implementation spec addresses all test scenarios without
requiring test modifications before proceeding to Phase 5.

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

## Phase 5: Implementation Code (Handoff)

**Purpose:** Actual implementation code is written by a coding agent following the
implementation specification. This skill does NOT write implementation code.

**Workflow:**

1. Announce readiness for implementation.
2. Summarize what the implementation specification contains and where it lives
   (`docs/specs/<feature>-implementation-specification.md`).
3. Offer to propose a prompt for the coding agent. The prompt should:
   - Reference the implementation specification document
   - Instruct the agent to implement code that passes all tests without modifying them
   - Specify the detected language and ecosystem
4. Wait for implementation code to be written before proceeding.

## Phase 6: Review (`/spec-dd:review`)

**Reference:** Read `references/review.md` before starting.

**Purpose:** Verify alignment across all artifacts and actual code.

**Pre-check:** Check that all three specification documents exist for the feature:
`<feature>-specification.md`, `<feature>-test-specification.md`, and
`<feature>-implementation-specification.md`. Flag any that are missing but proceed
with what is available.

**Workflow:**

1. **Document alignment:** Cross-check the three specification documents against
   each other. Identify inconsistencies, coverage gaps, and unresolved ambiguities.
2. **Code alignment:** Scan actual test files and implementation source code in the
   project. Compare against the specification documents. Identify:
   - Test scenarios in the spec without corresponding test code
   - Implementation approaches in the spec without corresponding source code
   - Undocumented behavior (code not covered by any specification)
3. **Test execution:** Detect the project's test runner and execute all available
   tests locally:
   - Check for: Makefile targets, justfile recipes, package.json scripts (test,
     test:unit, test:integration), pytest, go test, cargo test, mvn test, gradle
     test, and similar
   - Run the detected test command
   - Report pass/fail results with failure details
4. **Produce review report** at `docs/specs/<feature>-implementation-review.md`.
5. If issues are found, recommend which phase to revisit and why.

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

When `/spec-dd` is invoked (without a specific phase subcommand):

1. **Scan `docs/specs/`** for `*-specification.md` files to discover features. If
   the directory does not exist or is empty, ask the user for a feature name and
   start at Phase 1.
2. **Select feature:** Use the argument if provided. Otherwise, list discovered
   features and ask the user to choose, or let them name a new feature.
3. **Assess phase status** for the selected feature:
   - Does `<feature>-specification.md` exist? Any `[NEEDS CLARIFICATION]` markers?
   - Does `<feature>-test-specification.md` exist? Does it cover all acceptance
     criteria from the behavioral spec?
   - Do actual test files exist in the project? Do they align with the test spec?
   - Does `<feature>-implementation-specification.md` exist? Does it address all
     test scenarios?
   - Does actual implementation code exist? Does it align with the impl spec?
   - Does `<feature>-implementation-review.md` exist? Is it current?
4. **Report current state:** Which phases are complete, which have gaps, which
   have not been started.
5. **Recommend next action:** Either fix gaps in an earlier phase or proceed to the
   next incomplete phase.
6. **If at a handoff phase** (Phase 3 or Phase 5): Offer to propose a prompt for
   the coding agent.

## Quality Gates

All gates are **advisory** — the skill flags issues and recommends addressing them,
but the user can override and proceed.

| Transition | Gate Check |
|------------|-----------|
| Spec -> Test Spec | No unresolved `[NEEDS CLARIFICATION]` markers |
| Test Spec -> Test Code | Full traceability: every acceptance criterion mapped to test scenarios |
| Test Code -> Impl Spec | Test files exist and align with test specification |
| Impl Spec -> Impl Code | Every test scenario has a corresponding implementation approach; no test modifications required |
| Impl Code -> Review | Implementation code exists |
| Review -> Done | All checks pass in the review report, including test execution |

## Iterative Workflow Support

The workflow supports non-linear progression:

- The auto-detect router can recommend going back to an earlier phase when it finds
  gaps or inconsistencies.
- Any phase can be re-entered at any time via explicit subcommands
  (`/spec-dd:spec`, `/spec-dd:test`, etc.).
- Artifacts are updated in place — the skill works with whatever state exists.
- Starting rough and iterating is explicitly supported: write a quick behavioral
  spec, rough out test scenarios, refine both, then proceed.
- Review findings may reveal issues that require revisiting specification,
  test specification, or implementation specification phases.

## Pragmatism Guidelines

These are guidelines, not laws. Apply judgment:

- **Scale to project size.** A small utility feature needs a lighter touch than a
  complex distributed system feature. Do not demand exhaustive specs for a 20-line
  function.
- **Gates are advisory.** Flag issues and recommend addressing them. If the user
  acknowledges a gap and wants to proceed, respect the override.
- **Guide, do not block.** The skill's role is to surface gaps, ambiguities, and
  misalignments. It is not a gatekeeper — it is a navigator.
- **Acknowledge trade-offs.** When the user makes a conscious decision to skip or
  simplify a phase, note it and move on. Do not repeatedly insist.
- **Language idioms matter.** Adapt patterns, terminology, and recommendations to
  the project's detected language and ecosystem. A Go project and a Python project
  have different testing conventions, architectural patterns, and file structures.
