# Behavioral Specification — Reference Guide

> "The hardest single part of building a software system is deciding precisely what to build."
> — Fred Brooks, *The Mythical Man-Month*

## Core Principles

A behavioral specification describes **WHAT** the system does, never HOW it does it.
Implementation details belong in the implementation specification. This separation
ensures that the specification remains stable even when the underlying technology changes.

Every requirement must be:

- **Unambiguous** — only one valid interpretation exists.
- **Measurable** — a concrete value, threshold, or observable outcome is stated.
- **Testable** — a test can verify whether the requirement is met or not.

Non-goals are as important as goals. Without explicit non-goals, scope creeps silently —
stakeholders assume features that were never intended, and developers build behavior that
was never requested.

Edge cases and error states are first-class requirements. A specification that only
describes the happy path is incomplete. Boundary conditions, invalid inputs, concurrent
access, and failure modes must be addressed with the same rigor as primary functionality.

## Ambiguity Detection Checklist

Requirements ambiguity is the leading cause of defects introduced during specification.
Research by Berry et al. (2003) identifies five categories of ambiguity in natural-language
requirements. The Bender RBT ambiguity process (Bender, 2003) provides a systematic
approach for detection.

### 1. Lexical Ambiguity

Words with multiple meanings in context.

**Watch for:** "process", "handle", "manage", "support", "set up", "run"

**Example:** "The system processes the order" — does "process" mean validate, charge
payment, ship, or all three?

### 2. Syntactic Ambiguity

Sentence structure allows multiple valid parse trees.

**Example:** "Users can view reports and dashboards" — can users view both types, or
can they view reports AND separately manage dashboards? Restructure: "Users can view
reports. Users can view dashboards."

### 3. Semantic Ambiguity

Vague or unmeasurable terms with no agreed-upon definition.

**Watch for:** "fast", "secure", "user-friendly", "easy", "reliable", "scalable",
"efficient", "intuitive", "modern", "robust", "seamless"

**Example:** "The page loads quickly" — replace with "The page reaches First Contentful
Paint within 1.5 seconds on a 4G connection."

### 4. Pragmatic Ambiguity

Meaning depends on unstated context or implicit assumptions.

**Example:** "The user is notified" — notified via what channel? Email, push
notification, in-app banner, SMS? What content? When exactly?

### 5. Referential Ambiguity

Pronouns or references that could point to multiple antecedents.

**Watch for:** "it", "they", "the system", "the user", "this", "that"

**Example:** "When the admin deletes a user, they receive a confirmation" — does "they"
refer to the admin or the deleted user?

**References:**
- Berry, D.M., Kamsties, E., & Krieger, M.M. (2003). *From Contract Drafting to Software Specification: Linguistic Sources of Ambiguity.*
- Bender, R.B.T. (2003). [*Ambiguity Detection Process*](https://benderrbt.com/Ambiguityprocess.pdf).

## The `[NEEDS CLARIFICATION]` Convention

When an ambiguous, incomplete, or contradictory requirement is identified during
specification review, mark it inline:

```
[NEEDS CLARIFICATION: What HTTP status code is returned when the rate limit is exceeded?]
```

**Format:** `[NEEDS CLARIFICATION: brief description of what is unclear]`

**Purpose:** These markers make unknowns explicit and visible rather than silently
omitted. They serve as quality gate checkpoints — the skill checks for unresolved
markers before recommending progression to the test specification phase.

**Quality gate role:** A specification with unresolved `[NEEDS CLARIFICATION]` markers
is not ready for test derivation. Each marker must be resolved by:

1. Getting an answer from the stakeholder and replacing the marker with the answer.
2. Making a documented decision and replacing the marker with the decision and rationale.
3. Moving the marker to the Open Questions section if resolution is deferred.

## Required Specification Sections

### Objective

What this feature does and why it exists. One paragraph. Must answer: "What problem
does this solve for which user?" Avoid implementation language — describe the outcome,
not the mechanism.

### User Stories & Acceptance Criteria

Numbered for traceability. Each story follows the format:

```
US-1: As a [role], I want [action], so that [benefit].

Acceptance Criteria:
  AC-1.1: [Concrete, measurable criterion]
  AC-1.2: [Concrete, measurable criterion]
```

Every acceptance criterion must use concrete values, not vague adjectives. The criterion
must be verifiable by a test without human judgment.

### Constraints

Three categories to consider:

- **Technical:** Platform requirements, performance budgets, API compatibility, data formats.
- **Business:** Budget, timeline, regulatory compliance, licensing restrictions.
- **Operational:** Deployment environment, monitoring requirements, data retention policies.

### Edge Cases

Boundary conditions, error states, unusual inputs, concurrent access, empty/null states,
and resource exhaustion scenarios. Each edge case should specify the expected behavior,
not just identify the condition.

### Non-Goals

What this feature explicitly does NOT do. Each non-goal should explain why it is excluded.
Non-goals prevent scope creep and set clear expectations for stakeholders.

### Open Questions

All unresolved `[NEEDS CLARIFICATION]` items collected in one place for visibility.
This section is empty when the specification is complete.

## Good vs Bad Specification Examples

### Example 1: Performance Requirements

**Bad:** "The system should respond quickly to user requests."

**Good:** "The API responds to authenticated GET requests within 200ms at the 95th
percentile under 500 concurrent users. POST requests that trigger background processing
return HTTP 202 within 100ms; the background job completes within 30 seconds."

**Why:** The bad version uses "quickly" — a semantic ambiguity with no measurable
threshold. The good version specifies the request type, percentile, concurrency level,
and distinguishes synchronous from asynchronous processing.

### Example 2: User Actions

**Bad:** "Users should be able to manage their accounts."

**Good:** "Authenticated users can update their display name (1-50 characters, Unicode
letters, numbers, spaces, and hyphens) and email address (RFC 5322 validated format).
Display name changes take effect immediately. Email changes require verification via a
confirmation link sent to the new address; the link expires after 24 hours."

**Why:** The bad version uses "manage" — a lexical ambiguity covering an undefined set
of actions. The good version enumerates the specific operations, input constraints,
validation rules, and temporal behavior.

### Example 3: Error Handling

**Bad:** "The system should handle errors gracefully."

**Good:** "When a downstream service returns HTTP 5xx, the system retries up to 3 times
with exponential backoff (initial delay 1s, multiplier 2x, maximum delay 4s). If all
retries fail, the system returns HTTP 503 with body
`{\"error\": \"service_unavailable\", \"retry_after\": 30}` and emits a structured log
event at ERROR level with the downstream service name and response code."

**Why:** The bad version uses "gracefully" — a semantic ambiguity. The good version
specifies the retry policy, backoff parameters, failure response format, and
observability behavior.

### Example 4: Authorization

**Bad:** "Only authorized users can access sensitive data."

**Good:** "Users with the `admin` role can read and write all patient records. Users
with the `doctor` role can read and write records of patients assigned to them. Users
with the `nurse` role can read records of patients in their assigned ward but cannot
write. All other authenticated users receive HTTP 403. Unauthenticated requests
receive HTTP 401."

**Why:** The bad version has referential ambiguity ("authorized"), semantic ambiguity
("sensitive data"), and pragmatic ambiguity (what does "access" mean — read, write,
delete?). The good version defines each role's permissions with specific operations
and error responses.

## Quality Criteria

These criteria are drawn from IEEE 830-1998 (*Recommended Practice for Software
Requirements Specifications*) and ISO/IEC/IEEE 29148:2018 (*Systems and Software
Engineering — Life Cycle Processes — Requirements Engineering*).

### Complete

Every section of the specification is populated. Unknown items appear in Open Questions
with `[NEEDS CLARIFICATION]` markers — they are never silently omitted. A requirement
that says nothing about error handling is incomplete, not "implicitly fine."

### Unambiguous

No vague adjectives, no undefined terms, no implicit assumptions. Each requirement has
exactly one valid interpretation. Apply the five-category ambiguity checklist above.

### Testable

Every acceptance criterion can be verified by a concrete test with a deterministic
pass/fail outcome. If a requirement cannot be tested, it must be rewritten until it can.
"The UI is intuitive" is not testable. "A new user completes the checkout flow in under
3 minutes without external help" is testable.

### Consistent

No contradictions between sections. Constraints do not conflict with acceptance criteria.
Edge case behavior does not contradict happy-path behavior. Non-goals do not overlap
with stated features.

### Traceable

Every requirement has a numbered ID (e.g., US-1, AC-1.1) that downstream artifacts —
test scenarios, implementation components, review findings — can reference. Traceability
enables impact analysis when requirements change.

**References:**
- IEEE 830-1998. *IEEE Recommended Practice for Software Requirements Specifications.*
- ISO/IEC/IEEE 29148:2018. *Systems and Software Engineering — Life Cycle Processes — Requirements Engineering.*
