# Implementation Specification -- Reference Guide

> "The best code is the code that satisfies the tests you already have."
> -- Specification-Driven Development principle

## Purpose

This reference guides the creation and review of implementation specifications.
An implementation specification describes HOW each test scenario will be
satisfied. It bridges the gap between behavioral test scenarios and the code
that makes them pass, providing a technical blueprint that is traceable,
language-aware, and constrained by the immutability of existing tests.

## Core Principles

### 1. Test Scenarios Drive the Design

Every test scenario from the test specification must have a corresponding
implementation approach. The test specification is the contract; the
implementation specification is the plan for fulfilling that contract. No test
scenario may be left unaddressed.

> GitHub's [spec-kit](https://github.com/github/spec-kit) project demonstrates
> how formal specifications serve as the source of truth for implementation
> decisions, ensuring code stays aligned with documented behavior.

### 2. Tests Are Immutable

The implementation must not require modifying existing tests. If a test scenario
appears impossible to satisfy, the problem lies in either the behavioral
specification or the test specification -- not in the tests themselves. Flag
such cases as misalignments and escalate to the appropriate phase for
resolution.

### 3. Language-Aware, Not Language-Prescriptive

Use patterns, idioms, and architecture appropriate for the project's detected
stack. Do not prescribe specific frameworks or libraries unless the project
already uses them. The detected stack informs suggestions; it does not constrain
creative problem-solving.

> Thoughtworks identifies this balance in their analysis of
> [spec-driven development](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices):
> specifications should constrain behavior, not technology choices.

### 4. Minimal Sufficiency

Implement exactly what the test scenarios require. Avoid over-engineering,
speculative generalization, and premature abstraction. If no test scenario
exercises a capability, that capability does not belong in this specification.

## Required Sections

An implementation specification must contain these sections. Each section has a
specific purpose in ensuring traceability and completeness.

### Technical Approach

High-level design decisions and their rationale. Answer these questions:

- **What architectural pattern will be used?** (layered, hexagonal, MVC, pipes
  and filters, event-driven, etc.)
- **Why this pattern?** Link the choice to project context: existing codebase
  patterns, team conventions, or specific requirements from the behavioral spec.
- **What are the key design trade-offs?** Acknowledge what is gained and what is
  sacrificed by the chosen approach.

Keep this section concise. The goal is orientation, not exhaustive architecture
documentation.

### Component Design

Describe the modules, classes, interfaces, or functions that will be created or
modified. This section is language-aware:

- **Python**: Describe modules, classes, protocols, and key functions. Reference
  standard patterns like dataclasses, context managers, or generator-based flows.
- **TypeScript/JavaScript**: Describe modules, types/interfaces, and exported
  functions. Reference async patterns, error boundaries, or middleware chains.
- **Go**: Describe packages, interfaces, and exported functions. Reference
  idiomatic patterns like table-driven tests, interface consumers, or error
  wrapping.
- **Java/C#**: Describe classes, interfaces, and key methods. Reference DI
  patterns, service layers, or repository abstractions.
- **Rust**: Describe crates, modules, traits, and key functions. Reference
  ownership patterns, Result-based error handling, or trait-based polymorphism.

For each component, state its responsibility, its public interface (inputs,
outputs, error conditions), and its relationship to other components.

### Test Scenario Mapping

This is the critical alignment artifact. Map every test scenario from the test
specification to the component or function that satisfies it.

Format:

```
| Test Scenario ID | Scenario Title              | Component/Function           |
|------------------|-----------------------------|------------------------------|
| TS-001           | Create user with valid input | UserService.create()         |
| TS-002           | Reject duplicate email       | UserService.create() -> err  |
| TS-003           | Validate email format        | Validator.validateEmail()    |
```

Rules for this mapping:
- Every test scenario ID from the test specification must appear exactly once
- A component may satisfy multiple test scenarios
- If a test scenario cannot be mapped, flag it as a gap
- If a mapping would require changing the test, flag it as a misalignment

### Dependencies and Constraints

Document external dependencies and technical constraints:

- **External libraries**: Only those needed to satisfy test scenarios. Pin
  version constraints if compatibility matters.
- **External services**: APIs, databases, message queues that the implementation
  must integrate with.
- **Performance constraints**: From the behavioral specification. Link each
  constraint to its source requirement.
- **Integration points**: Where this feature touches existing code. Describe the
  boundaries and contracts at each integration point.

### Alignment Check

An explicit statement confirming the implementation approach addresses all test
scenarios. This section has three possible outcomes:

1. **Full alignment**: Every test scenario is mapped and satisfiable. Proceed
   to implementation.
2. **Gaps identified**: Some test scenarios lack an implementation approach.
   List them. These must be resolved before proceeding.
3. **Misalignments identified**: Some implementation approaches conflict with
   test expectations. List them with recommended resolution. The resolution
   must change the implementation approach, never the tests.

## Alignment Verification Process

Follow this process to verify the implementation specification is complete and
consistent:

**Step 1 -- Walk the test scenarios.** Read each test scenario from the test
specification sequentially. For each one, locate its entry in the Test Scenario
Mapping table.

**Step 2 -- Trace to components.** For each mapped test scenario, verify the
referenced component exists in the Component Design section. Confirm the
component's described interface can produce the expected outcome.

**Step 3 -- Flag gaps.** Any test scenario without a mapping entry is a
coverage gap. Record it in the Alignment Check section.

**Step 4 -- Flag misalignments.** Any implementation approach that would require
modifying a test is a misalignment. The test defines expected behavior; the
implementation must conform to it. Record misalignments with a recommended
alternative approach.

**Step 5 -- Flag undocumented behavior.** Any component or function described in
the implementation specification that is not referenced by any test scenario
introduces undocumented behavior. This may indicate over-engineering or a
missing test scenario. Record it for review.

## Language-Aware Patterns

The skill auto-detects the project stack by scanning for manifest files
(`package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
`pom.xml`, `build.gradle`, `*.csproj`). Use the detected stack to inform --
but not dictate -- the following:

**Architecture patterns**: Suggest patterns the project already uses. If the
codebase follows layered architecture, the implementation spec should follow
suit. If the project uses hexagonal architecture, describe ports and adapters.

**Error handling**: Match the project's conventions. Use exceptions in Python,
`Result<T, E>` in Rust, error returns in Go, `Either` in functional Scala.

**Testing patterns**: Match the project's mocking strategy (dependency
injection, monkey patching, test doubles, interface-based mocking). The
implementation must be structured so existing tests can exercise it.

**Dependency management**: Use the project's dependency tool and conventions.
Do not introduce a conflicting package manager.

## Handoff Prompt Generation

When the implementation specification is complete and passes its advisory quality
gate, offer to generate a handoff prompt for the coding agent. The prompt must
be self-contained -- a coding agent with no prior context should be able to
execute it.

Template:

```
Implement the <feature> feature according to the implementation specification.

References:
- Implementation specification: docs/specs/<feature>-implementation-specification.md
- Test specification: docs/specs/<feature>-test-specification.md

Constraint: Implement code that passes ALL existing tests without modifying
any test files. The tests in <test-file-paths> define the expected behavior.
If a test cannot pass, report the conflict rather than changing the test.

Stack: <detected language/framework>
Conventions: <project patterns observed, e.g., "layered architecture",
"dependency injection via constructors", "error handling via Result types">

Start by reading both specification files, then implement each component
described in the implementation specification.
```

## Anti-Patterns

### Requiring Test Modifications

Any implementation approach that assumes tests will be adjusted is a
specification failure, not a testing failure. If the implementation cannot
satisfy a test as written, revisit the behavioral specification or the test
specification.

### Over-Engineering (YAGNI)

Do not design components, abstractions, or extension points that no test
scenario exercises. Every element in the implementation specification must trace
back to a test scenario or a documented constraint. Speculative features
increase complexity without verified value.

### Missing Error Handling

The behavioral specification defines edge cases and error states. The test
specification encodes them as test scenarios. If the implementation
specification does not address how errors are handled for each error-path test
scenario, it is incomplete. Error handling is not optional detail -- it is
specified behavior.

### Inconsistency with Existing Project Patterns

When the project has established patterns (naming conventions, directory
structure, architectural layers, error handling strategies), the implementation
specification must follow them. Introducing a novel pattern without cause
creates friction for both the coding agent and future maintainers.

### Premature Technology Decisions

Do not specify new libraries, frameworks, or tools unless the test scenarios
specifically require capabilities the project does not currently have. Prefer
using what the project already depends on.
