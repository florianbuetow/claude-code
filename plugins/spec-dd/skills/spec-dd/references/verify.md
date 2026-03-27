# Implementation Verification — Reference Guide

> "Did we build what the spec says?" is a different question from "are our
> documents consistent?" Verification answers the first.

## Core Principles

Implementation verification checks whether actual code satisfies a specification.
It operates at the **requirement satisfaction layer** — not the artifact alignment
layer (that is the review phase's job). The distinction matters:

| Review (Phase 6) | Verify |
|-------------------|--------|
| Checks spec-dd artifacts against each other | Checks code against a single source-of-truth spec |
| Requires the full artifact chain (spec → test spec → test impl spec) | Works with any spec file, including informal ones |
| Runs the full test suite | Prefers reading files; runs tests only when needed |
| Produces a severity-classified review report | Produces a requirement-level PASS/FAIL checklist |

Verification is complementary to review, not a replacement. Use verify when:

- The spec is an informal document (not created through spec-dd Phase 1)
- You want a fast, requirement-level check before a full review
- Re-running tests is slow, non-deterministic, or insufficient
- The spec predates the spec-dd workflow and was never formalized

## Requirement Extraction

The first step is extracting every testable requirement from the spec file.
Not all specs follow the same format. Use these heuristics to identify
requirements regardless of document structure:

### Numbered Items

Any numbered or lettered list where items describe expected behavior:

```
1. The sidebar displays all available corpora
2. Messages stream via Server-Sent Events
3. Users can export chat history as markdown
```

Each item becomes a requirement (R01, R02, R03...).

### Acceptance Criteria

Sections titled "Acceptance Criteria", "Requirements", "Must Have", or
"Definition of Done". Items within these sections are requirements by
definition.

### RFC-Style Keywords

Statements containing MUST, SHALL, SHOULD, MUST NOT, SHALL NOT
(per RFC 2119). Each statement is a requirement.

```
The API MUST return HTTP 429 when the rate limit is exceeded.
```

### Behavioral Descriptions

Prose that describes what the system does in specific situations. Look for
action verbs with concrete outcomes:

```
When a user uploads a file larger than 10MB, the system rejects it
with an error message showing the maximum allowed size.
```

### Implicit Requirements

Some requirements are implied by constraints or non-functional sections.
Extract them explicitly:

- "Performance: < 200ms response time" → R: API responds within 200ms at p95
- "Security: all endpoints require authentication" → R: Unauthenticated
  requests receive 401

### What Is NOT a Requirement

Skip items that cannot be verified by reading or testing code:

- Project management notes ("Phase 2 delivery target: March")
- Aspirational statements ("The UX should feel modern")
- Implementation suggestions ("Consider using Redis for caching")

## Verification Strategy: Read First, Run Second

The default verification approach prioritizes **reading code** over running
tests. This is deliberate:

1. Reading is fast, deterministic, and works in any environment
2. Running tests can be slow, flaky, or require infrastructure
3. Many requirements are verifiable by inspecting the code path
4. Non-deterministic tests (LLM-dependent, network-dependent) produce
   unreliable pass/fail signals

### When to Read

For most requirements, find the implementation file(s) and verify the logic
matches the spec's behavioral description:

- **API endpoints**: Check route definitions, handler logic, response formats
- **Data validation**: Check input validation rules, error messages
- **Business logic**: Trace the code path that implements the rule
- **Configuration**: Check that config values match spec constraints
- **UI behavior**: Check component rendering logic, event handlers

Use `Grep` and `Read` to locate relevant code. Cite specific file paths and
line numbers as evidence.

### When to Run

Execute tests only when:

- The requirement describes **runtime behavior** that cannot be verified by
  reading (timing, concurrency, integration with external systems)
- The user **explicitly asks** for test execution
- A read-based check is **inconclusive** and a test run would resolve it

### When NOT to Run

Do not re-run tests when:

- Tests are known to be **non-deterministic** (LLM calls, network calls)
- The test suite is **slow** and the user has not asked for execution
- Tests **already passed** in a recent run and the code has not changed

If a test is non-deterministic, verify that the test **exists and exercises
the correct code path** rather than asserting it passes.

## Verification Statuses

Each requirement receives one of three statuses:

### PASS

The code fully satisfies the requirement. Evidence shows the implementation
matches the spec's behavioral description.

**Evidence format**: File path and line number, with a one-line description
of what the code does.

```
R01 | PASS | `routes_corpora.py:45` — GET /v1/corpora returns corpus list
```

### FAIL

The requirement is not satisfied. Either the code is missing entirely, or the
implementation contradicts the spec.

**Evidence format**: What was expected (from the spec) and what was found (or
not found) in the code.

```
R03 | FAIL | No export endpoint or UI button found. Spec requires markdown export.
```

### PARTIAL

The code addresses the requirement but with gaps — missing edge cases,
incomplete UI, hardcoded values where config is expected, or partial
implementation.

**Evidence format**: What works and what is missing, with file references.

```
R04 | PARTIAL | Citation numbers rendered (`chat.js:340`) but footnote
     |         | mapping is incomplete — links do not resolve to source panel
```

## Handling Non-Deterministic Tests

When a requirement is tested by a non-deterministic test (depends on an LLM,
external API, or timing):

1. **Do not assert the test passes.** Non-deterministic tests can fail on any
   given run without indicating a real problem.
2. **Verify the test exists** and references the correct code path.
3. **Mark the requirement as PASS** if the code logic is correct by reading,
   even if the test is flaky. Note the non-determinism.
4. **Add a note** to the evidence: `(non-deterministic test — verified by
   code reading)`.

## Verification Report Format

The verification report is saved to `docs/specs/<feature>-verification.md`.
If no feature name is provided, use `docs/specs/verify-<spec-filename>-<date>.md`.

```markdown
# Verification: <spec-file>

| Field | Value |
|-------|-------|
| Spec file | `<path to spec>` |
| Feature | <feature name or "N/A"> |
| Date | <today's date> |

## Requirements

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| R01 | <extracted requirement> | PASS | `file:line` — description |
| R02 | <extracted requirement> | FAIL | Expected X, found nothing |
| R03 | <extracted requirement> | PARTIAL | `file:line` — works but missing Y |

## Summary

**Result: X/Y PASS, Z FAIL, W PARTIAL**

## Gaps Requiring Action

| # | Requirement | Issue | Suggested Fix |
|---|-------------|-------|---------------|
| R02 | <requirement> | Not implemented | Add endpoint at `routes/export.py` |
| R03 | <requirement> | Incomplete | Complete footnote mapping in `chat.js` |

## Notes

- <Any observations about non-deterministic tests, environment issues, or
  spec ambiguities discovered during verification>
```

## Verification Checklist

- [ ] Read the spec file and extract all testable requirements
- [ ] Assign each requirement an ID (R01, R02, ...)
- [ ] For each requirement, search the codebase for implementing code
- [ ] Verify code logic matches the spec's behavioral description
- [ ] Mark each requirement as PASS, FAIL, or PARTIAL with evidence
- [ ] For non-deterministic tests, verify test exists and code logic is correct
- [ ] Run targeted tests only when reading is insufficient
- [ ] Produce the verification report
- [ ] List gaps and suggested fixes for FAIL and PARTIAL items
