# spec-dd Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create the `spec-dd` plugin — a specification-driven development workflow skill for the florianbuetow/claude-code marketplace.

**Architecture:** Single plugin with one skill and four reference files. The SKILL.md contains the phase router and workflow logic. Reference files provide detailed guidance for each phase. Follows the same conventions as existing plugins (solid-principles, spec-writer, etc.).

**Tech Stack:** Markdown (SKILL.md, reference files), JSON (plugin.json, marketplace.json)

**Design doc:** `docs/plans/2026-03-02-spec-dd-design.md`

---

### Task 1: Create plugin manifest

**Files:**
- Create: `plugins/spec-dd/.claude-plugin/plugin.json`

**Step 1: Create directory structure**

Run: `mkdir -p plugins/spec-dd/.claude-plugin`

**Step 2: Write plugin.json**

Create `plugins/spec-dd/.claude-plugin/plugin.json` with:

```json
{
  "name": "spec-dd",
  "version": "1.0.0",
  "description": "Specification-driven development workflow skill. Orchestrates a spec-first discipline: write behavioral specifications, derive test scenarios, plan implementation, and verify alignment across all artifacts and code. Acts as a workflow navigator with advisory quality gates between phases.",
  "author": {
    "name": "Florian Buetow",
    "email": "2320560+florianbuetow@users.noreply.github.com"
  },
  "license": "MIT",
  "keywords": ["specification", "spec-driven", "behavioral-testing", "test-specification", "implementation-specification", "quality-gates", "workflow", "sdd", "bdd", "tdd"]
}
```

**Step 3: Commit**

```bash
git add plugins/spec-dd/.claude-plugin/plugin.json
git commit -m "Add spec-dd plugin manifest"
```

---

### Task 2: Register plugin in marketplace

**Files:**
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Add spec-dd entry to the plugins array**

Add the following entry to the `plugins` array in `.claude-plugin/marketplace.json`, after the `spec-writer` entry and before the `explain-system-tradeoffs` entry (logical grouping: spec-writer then spec-dd):

```json
{
  "name": "spec-dd",
  "description": "Specification-driven development workflow skill. Orchestrates a spec-first discipline with advisory quality gates: behavioral specification, test specification, implementation specification, and alignment review.",
  "version": "1.0.0",
  "author": {
    "name": "Florian Buetow",
    "email": "2320560+florianbuetow@users.noreply.github.com"
  },
  "source": "./plugins/spec-dd",
  "category": "development"
}
```

Also update the top-level `description` field to include spec-dd in the collection description.

**Step 2: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "Register spec-dd in marketplace"
```

---

### Task 3: Write SKILL.md — the main skill definition

**Files:**
- Create: `plugins/spec-dd/skills/spec-dd/SKILL.md`

**Step 1: Create directory**

Run: `mkdir -p plugins/spec-dd/skills/spec-dd/references`

**Step 2: Write SKILL.md**

Create `plugins/spec-dd/skills/spec-dd/SKILL.md`. This is the largest and most important file. Follow the design doc exactly. The file must contain:

**Frontmatter:**
```yaml
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
```

**Content structure — follow this outline exactly:**

1. **H1 title:** `# Specification-Driven Development`

2. **Introduction:** 2-3 sentences. This skill orchestrates a spec-first development workflow. It guides writing behavioral specifications, deriving test scenarios, planning implementation, and verifying alignment. Acts as a workflow navigator with advisory quality gates.

3. **Commands table:**

| Command | Phase | Reference |
|---------|-------|-----------|
| `/spec-dd` | Auto-detect phase, assess state, recommend next step | All references |
| `/spec-dd:spec` | Write/review behavioral specification | `references/specification.md` |
| `/spec-dd:test` | Write/review test specification | `references/test-specification.md` |
| `/spec-dd:impl` | Write/review implementation specification | `references/implementation-specification.md` |
| `/spec-dd:review` | Run alignment review, produce report | `references/review.md` |

4. **Artifacts section:** Describe the 4 markdown files in `docs/specs/`, naming convention `<feature>-specification.md` etc.

5. **First steps (when any command is invoked):**
   - Read the relevant reference file from `references/` BEFORE doing anything
   - Auto-detect project language by scanning for manifest files (package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, pom.xml, build.gradle, etc.)
   - If `/spec-dd` (router): scan `docs/specs/` for existing features, select feature (argument or ask user), assess phase status, report state, recommend next action
   - If `/spec-dd:<phase>`: check for existing artifacts from prior phases, flag gaps advisory, proceed with the requested phase

6. **Phase workflows — one subsection per phase:**

   **Phase 1: Behavioral Specification (`/spec-dd:spec`)**
   - Read `references/specification.md`
   - If `<feature>-specification.md` exists, review it for quality; if not, guide creation
   - Interaction model: ask clarifying questions (selectable options + free-text), one topic at a time
   - Review for ambiguity: vague language, missing edge cases, undefined terms, implicit assumptions
   - Mark unresolved items with `[NEEDS CLARIFICATION]`
   - Check completeness: all user stories have measurable acceptance criteria
   - Advisory gate: no unresolved `[NEEDS CLARIFICATION]` markers
   - Output: `docs/specs/<feature>-specification.md` using the template from the design doc

   **Phase 2: Test Specification (`/spec-dd:test`)**
   - Read `references/test-specification.md`
   - Check that `<feature>-specification.md` exists; if not, advise completing Phase 1 first
   - Read the behavioral specification to extract all acceptance criteria
   - Derive Given/When/Then scenarios: one behavior per scenario, one action per step
   - Build coverage matrix: every acceptance criterion maps to at least one test scenario
   - Language-aware: adapt scenarios to the project's testing ecosystem
   - Advisory gate: full traceability between spec requirements and test scenarios
   - Output: `docs/specs/<feature>-test-specification.md` using the template from the design doc

   **Phase 3: Test Code (Handoff)**
   - No reference file needed
   - Check that `<feature>-test-specification.md` exists and passes quality gate
   - Announce: "The test specification is ready for implementation."
   - Offer to propose a prompt for the coding agent that:
     - References `docs/specs/<feature>-test-specification.md`
     - Instructs the agent to use the project's detected test framework and conventions
     - Instructs the agent to write tests following the Given/When/Then scenarios exactly
   - Do NOT write test code

   **Phase 4: Implementation Specification (`/spec-dd:impl`)**
   - Read `references/implementation-specification.md`
   - Check that `<feature>-test-specification.md` exists; advise completing Phase 2 first if not
   - Check that actual test files exist in the project; advise completing Phase 3 (handoff) first if not
   - Read the test specification to extract all test scenarios
   - Guide writing the technical approach for satisfying each test scenario
   - Language-aware: use appropriate patterns, idioms, architecture for the detected stack
   - Verify: every test scenario has a corresponding implementation approach
   - Verify: the approach does not require modifying existing tests
   - Advisory gate: implementation spec addresses all test scenarios
   - Output: `docs/specs/<feature>-implementation-specification.md` using the template from the design doc

   **Phase 5: Implementation Code (Handoff)**
   - No reference file needed
   - Check that `<feature>-implementation-specification.md` exists and passes quality gate
   - Announce: "The implementation specification is ready for implementation."
   - Offer to propose a prompt for the coding agent that:
     - References `docs/specs/<feature>-implementation-specification.md`
     - Instructs the agent to implement code that passes all tests without modifying them
     - References the test specification for context on what tests expect
   - Do NOT write implementation code

   **Phase 6: Review (`/spec-dd:review`)**
   - Read `references/review.md`
   - Read all three spec documents for the feature
   - Scan actual test files and implementation code in the project
   - Check document alignment: specification <-> test specification <-> implementation specification
   - Check code alignment: actual tests vs test spec, actual implementation vs impl spec
   - Identify: coverage gaps, misalignments, unresolved ambiguities, undocumented behavior
   - Produce report: `docs/specs/<feature>-implementation-review.md` using the template from the design doc
   - If issues found, recommend which phase to revisit

7. **Auto-detect router logic:** (as described in the design doc, section "Auto-Detect Router")

8. **Quality gates table:** (as described in the design doc)

9. **Iterative workflow support:** Explain that the skill supports non-linear progression. The router can recommend going back. Any phase can be re-entered via explicit sub-commands. Artifacts are updated in place. Starting rough and iterating is supported.

10. **Pragmatism guidelines:**
    - Scale to project size: a small utility doesn't need the same rigor as a large system
    - Gates are advisory: the user's judgment takes precedence
    - The skill guides and reviews — it doesn't enforce or block
    - When the user overrides a gate, acknowledge the decision and proceed

**Step 3: Commit**

```bash
git add plugins/spec-dd/skills/spec-dd/SKILL.md
git commit -m "Add spec-dd SKILL.md with phase router and workflow logic"
```

---

### Task 4: Write references/specification.md

**Files:**
- Create: `plugins/spec-dd/skills/spec-dd/references/specification.md`

**Step 1: Write the reference file**

This file guides how to write and review behavioral specifications. Target length: 150-250 lines.

**Required content:**

1. **H1:** `# Behavioral Specification — Reference Guide`

2. **Core principles:**
   - Specifications describe WHAT the system does, not HOW
   - Every requirement must be unambiguous, measurable, and testable
   - Non-goals are as important as goals — they prevent scope creep
   - Edge cases and error states are first-class requirements

3. **Ambiguity detection checklist** (cite [Bender RBT](https://benderrbt.com/Ambiguityprocess.pdf) and [academic research](https://www.researchgate.net/publication/326730868)):
   - **Lexical ambiguity:** Words with multiple meanings (e.g., "process", "handle", "manage")
   - **Syntactic ambiguity:** Sentence structure allows multiple interpretations (e.g., "Users can view reports and dashboards" — can they view both, or view reports and separately manage dashboards?)
   - **Semantic ambiguity:** Vague or unmeasurable terms ("fast", "secure", "user-friendly", "easy", "reliable", "scalable", "efficient")
   - **Pragmatic ambiguity:** Context-dependent meaning, implicit assumptions not stated
   - **Referential ambiguity:** Pronouns or references that could point to multiple things ("it", "they", "the system")

4. **The `[NEEDS CLARIFICATION]` convention:**
   - When an ambiguous or incomplete requirement is identified, mark it with `[NEEDS CLARIFICATION]`
   - Format: `[NEEDS CLARIFICATION: brief description of what's unclear]`
   - These markers serve as quality gate checkpoints — the skill checks for unresolved markers before proceeding

5. **Required specification sections** with guidance for each:
   - **Objective:** What this feature does and why. One paragraph. Must answer "what problem does this solve?"
   - **User Stories & Acceptance Criteria:** Numbered. Each story follows "As a [role], I want [action], so that [benefit]". Each has measurable acceptance criteria. Use concrete values, not vague adjectives.
   - **Constraints:** Technical (platform, performance), business (budget, timeline), regulatory (compliance, data handling)
   - **Edge Cases:** Boundary conditions, error states, unusual inputs, concurrent access, empty/null states
   - **Non-Goals:** What this feature explicitly does NOT do. Critical for scope management.
   - **Open Questions:** All `[NEEDS CLARIFICATION]` items collected here for visibility

6. **Good vs bad specification examples:**

   Bad: "The system should respond quickly to user requests."
   Good: "The API responds to authenticated GET requests within 200ms at p95 under 500 concurrent users."

   Bad: "Users should be able to manage their accounts."
   Good: "Authenticated users can update their display name (1-50 characters, Unicode) and email address (validated format). Changes take effect immediately. Email changes require verification via a confirmation link sent to the new address."

   Bad: "The system should handle errors gracefully."
   Good: "When a downstream service returns HTTP 5xx, the system retries up to 3 times with exponential backoff (1s, 2s, 4s). If all retries fail, it returns HTTP 503 with body `{\"error\": \"service_unavailable\", \"retry_after\": 30}`."

7. **Quality criteria** (cite IEEE 830 / ISO 29148):
   - **Complete:** All sections populated, unknowns in Open Questions, not silently omitted
   - **Unambiguous:** No vague adjectives, no undefined terms, no implicit assumptions
   - **Testable:** Every acceptance criterion can be verified with a concrete test
   - **Consistent:** No contradictions between sections
   - **Traceable:** Numbered IDs on all requirements for downstream linking

**Step 2: Commit**

```bash
git add plugins/spec-dd/skills/spec-dd/references/specification.md
git commit -m "Add behavioral specification reference guide"
```

---

### Task 5: Write references/test-specification.md

**Files:**
- Create: `plugins/spec-dd/skills/spec-dd/references/test-specification.md`

**Step 1: Write the reference file**

This file guides how to derive and review test scenarios from behavioral specs. Target length: 150-250 lines.

**Required content:**

1. **H1:** `# Test Specification — Reference Guide`

2. **Core principles:**
   - Test scenarios are derived from the behavioral specification ONLY — no implementation knowledge
   - Tests describe expected behavior, not implementation details
   - One behavior per scenario, one action per step
   - Tests are immutable during implementation — if code can't pass, the implementation is wrong
   - Cite [Martin Fowler - Given When Then](https://martinfowler.com/bliki/GivenWhenThen.html)

3. **Given/When/Then format rules** (cite [BDD best practices](https://testomat.io/blog/writing-bdd-test-cases-in-agile-software-development-examples-best-practices-test-case-templates/) and [Cucumber](https://cucumber.io/blog/bdd/bdd-vs-tdd)):
   - **Given:** The precondition / state of the world before the behavior. One Given per scenario (use And for additional preconditions). Describes setup, not actions.
   - **When:** The single action or event being tested. Exactly one When per scenario.
   - **Then:** The expected outcome. Observable result, not implementation detail. Use And for additional assertions.
   - Keep steps declarative, not imperative: "Given a logged-in user" not "Given the user enters username and password and clicks login"
   - Use domain language from the specification, not technical jargon

4. **Deriving test scenarios from specifications:**
   - For each acceptance criterion in the spec, write at least one happy-path scenario
   - For each edge case in the spec, write a scenario
   - For each constraint, consider what happens when the constraint is violated
   - For each non-goal, consider writing a negative scenario ("the system does NOT do X")
   - Decision tables: when a requirement has multiple conditions, enumerate the combinations

5. **Coverage matrix:**
   - A table mapping each acceptance criterion ID to its test scenario IDs
   - Format: `| Spec Requirement | Test Scenario(s) |`
   - Every row in the spec requirements column must have at least one entry in test scenarios
   - Uncovered requirements are flagged as gaps

6. **Language-aware review guidance:**
   - After detecting the project language/framework, consider:
     - Are the scenarios realistic for this testing ecosystem?
     - Do the scenarios map to the kinds of tests the framework supports?
     - Are there framework-specific patterns that should be reflected? (e.g., async behavior in Node.js, database transactions in backend apps)
   - This does NOT mean writing framework-specific test code — it means ensuring scenarios are *implementable* in the detected stack

7. **Anti-patterns to flag:**
   - Testing implementation details ("Given the database has a row with id=1") instead of behavior ("Given a user exists")
   - Combining multiple behaviors in one scenario
   - Imperative steps that describe HOW instead of WHAT
   - Missing error/edge case scenarios
   - Scenarios that are untestable or unmeasurable

8. **Example test scenario:**

   From spec: "Authenticated users can update their display name (1-50 characters, Unicode)."

   ```
   Scenario: Update display name with valid input
     Given an authenticated user with display name "Alice"
     When the user updates their display name to "Bob"
     Then the display name is "Bob"

   Scenario: Reject display name exceeding maximum length
     Given an authenticated user
     When the user updates their display name to a 51-character string
     Then the update is rejected with error "display name must be 1-50 characters"

   Scenario: Accept Unicode characters in display name
     Given an authenticated user
     When the user updates their display name to "日本語テスト"
     Then the display name is "日本語テスト"
   ```

**Step 2: Commit**

```bash
git add plugins/spec-dd/skills/spec-dd/references/test-specification.md
git commit -m "Add test specification reference guide"
```

---

### Task 6: Write references/implementation-specification.md

**Files:**
- Create: `plugins/spec-dd/skills/spec-dd/references/implementation-specification.md`

**Step 1: Write the reference file**

This file guides how to write and review implementation specifications. Target length: 150-250 lines.

**Required content:**

1. **H1:** `# Implementation Specification — Reference Guide`

2. **Core principles:**
   - The implementation spec describes HOW each test scenario will be satisfied
   - Every test scenario from the test specification must have a corresponding implementation approach
   - The implementation must not require modifying existing tests — tests are immutable
   - Language-aware: use patterns and idioms appropriate for the detected stack
   - Cite [GitHub spec-kit](https://github.com/github/spec-kit) and [Thoughtworks SDD](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)

3. **Required sections guidance:**

   - **Technical Approach:** High-level design decisions and rationale. Which architectural pattern? Which components? Why?
   - **Component Design:** Language-aware. For a Python project, describe modules/classes. For a Go project, describe packages/interfaces. For TypeScript, describe modules/types. Use the idioms of the detected stack.
   - **Test Scenario Mapping:** A table or list mapping each test scenario ID to the component/function that will satisfy it. This is the critical alignment artifact.
   - **Dependencies & Constraints:** External libraries, services, performance requirements, integration points
   - **Alignment Check:** Explicit confirmation that the approach satisfies all test scenarios. Flag any test that seems impossible to satisfy — this indicates a spec or test spec issue, NOT a reason to modify tests.

4. **Alignment verification process:**
   - Walk through each test scenario from the test specification
   - For each scenario, identify which component/function in the implementation spec handles it
   - If a test scenario has no corresponding implementation approach, flag it as a gap
   - If an implementation approach would require changing a test, flag it as a misalignment — the implementation approach must change, not the test
   - If the implementation introduces behavior not covered by any test scenario, flag it as undocumented behavior

5. **Language-aware patterns:**
   - The skill auto-detects the project stack from manifest files
   - Use this context to suggest appropriate:
     - Architecture patterns (MVC, hexagonal, layered, etc.)
     - Error handling patterns (exceptions vs result types vs error codes)
     - Testing patterns (mocking strategies, fixture patterns, test isolation)
     - Dependency management approaches
   - Do NOT prescribe a specific framework or library unless the project already uses one

6. **Handoff prompt generation:**
   - When the implementation spec is complete, the skill offers to generate a prompt for the coding agent
   - The prompt should:
     - Reference the implementation specification file path
     - Reference the test specification file path
     - State the constraint: "implement code that passes all tests without modifying them"
     - Mention the detected stack and conventions
     - Be self-contained enough for a coding agent with no prior context

7. **Anti-patterns to flag:**
   - Implementation approaches that require test modifications
   - Over-engineering beyond what the test scenarios require (YAGNI)
   - Missing error handling for edge cases specified in the behavioral spec
   - Inconsistency between the implementation approach and the project's existing patterns

**Step 2: Commit**

```bash
git add plugins/spec-dd/skills/spec-dd/references/implementation-specification.md
git commit -m "Add implementation specification reference guide"
```

---

### Task 7: Write references/review.md

**Files:**
- Create: `plugins/spec-dd/skills/spec-dd/references/review.md`

**Step 1: Write the reference file**

This file guides how to perform alignment reviews and produce reports. Target length: 150-250 lines.

**Required content:**

1. **H1:** `# Alignment Review — Reference Guide`

2. **Core principles:**
   - The review verifies alignment across ALL artifacts AND actual code
   - Three layers of alignment: spec <-> test spec, test spec <-> impl spec, specs <-> actual code
   - Identify gaps in both directions: missing coverage AND undocumented behavior
   - Cite [InfoQ - conformance testing](https://www.infoq.com/articles/spec-driven-development/) and [Addy Osmani](https://addyosmani.com/blog/good-spec/)

3. **Document alignment checks:**

   **Specification <-> Test Specification:**
   - Every acceptance criterion in the spec has at least one test scenario
   - Every test scenario traces back to a spec requirement (no orphan tests)
   - Edge cases from the spec are covered by test scenarios
   - Non-goals from the spec are NOT tested (unless as explicit negative tests)

   **Test Specification <-> Implementation Specification:**
   - Every test scenario has a corresponding implementation approach
   - The implementation approach does not require modifying any test
   - No implementation behavior exists without a corresponding test scenario

   **Specification <-> Implementation Specification:**
   - The implementation approach is consistent with the constraints in the spec
   - Non-goals from the spec are respected (not implemented)

4. **Code alignment checks:**

   **Actual test code vs Test Specification:**
   - Scan the project for test files related to the feature
   - Check that test scenarios from the test spec have corresponding test functions/methods
   - Flag test code that doesn't correspond to any test scenario (undocumented tests)
   - Flag test scenarios with no corresponding test code (unimplemented tests)

   **Actual implementation code vs Implementation Specification:**
   - Scan the project for source files related to the feature
   - Check that components described in the impl spec exist in the code
   - Flag code that doesn't correspond to any impl spec section (undocumented implementation)
   - Flag impl spec sections with no corresponding code (unimplemented components)

   **Actual implementation code vs Test Specification:**
   - Check that all tests pass (or note that this requires running the test suite)
   - Flag implementation behavior not covered by any test

5. **Review report format:**

   ```markdown
   # <Feature> - Implementation Review

   | Field | Value |
   |-------|-------|
   | Feature | <feature name> |
   | Date | <today> |
   | Status | <PASS / ISSUES FOUND> |

   ## Specification Alignment
   | Check | Status | Details |
   |-------|--------|---------|
   | Spec -> Test Spec coverage | PASS/FAIL | ... |
   | Test Spec -> Spec traceability | PASS/FAIL | ... |
   | Test Spec -> Impl Spec coverage | PASS/FAIL | ... |
   | Spec constraints respected | PASS/FAIL | ... |

   ## Code Alignment
   | Check | Status | Details |
   |-------|--------|---------|
   | Test code vs Test Spec | PASS/FAIL | ... |
   | Implementation vs Impl Spec | PASS/FAIL | ... |
   | Undocumented behavior | PASS/FAIL | ... |

   ## Coverage Report
   - Gaps: ...
   - Misalignments: ...
   - Unresolved items: ...

   ## Recommendations
   - ...
   ```

6. **Severity classification for findings:**
   - **CRITICAL:** Missing test coverage for a spec requirement, or implementation contradicts spec
   - **WARNING:** Undocumented behavior, orphan tests, minor misalignments
   - **INFO:** Suggestions for improvement, stylistic observations

7. **When to recommend going back:**
   - CRITICAL findings in spec alignment → revisit Phase 1 (specification) or Phase 2 (test spec)
   - CRITICAL findings in code alignment → revisit Phase 4 (impl spec) or Phase 5 (handoff)
   - WARNING-only findings → note them but don't block completion

**Step 2: Commit**

```bash
git add plugins/spec-dd/skills/spec-dd/references/review.md
git commit -m "Add alignment review reference guide"
```

---

### Task 8: Add LICENSE file

**Files:**
- Create: `plugins/spec-dd/LICENSE`

**Step 1: Copy LICENSE from an existing plugin**

Run: `cp plugins/solid-principles/LICENSE plugins/spec-dd/LICENSE`

**Step 2: Commit**

```bash
git add plugins/spec-dd/LICENSE
git commit -m "Add LICENSE to spec-dd plugin"
```

---

### Task 9: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Add spec-dd section**

Add a new section for `spec-dd` in `README.md` after the `spec-writer` section and before the `explain-system-tradeoffs` section. Follow the same format as existing plugin sections.

Update the header counts: `6 plugins` and update the skill count. Add spec-dd to the Skills table in the introduction.

The spec-dd section should include:
- Plugin name and description
- The 6-phase workflow (spec, test spec, test code handoff, impl spec, impl code handoff, review)
- Commands table (`/spec-dd`, `/spec-dd:spec`, `/spec-dd:test`, `/spec-dd:impl`, `/spec-dd:review`)
- Artifacts description (`docs/specs/` with the 4 markdown files)
- Mention: advisory quality gates, language-aware reviews, coding agent handoff prompts
- Languages & stacks: Any — auto-detects from project manifest files

**Step 2: Commit**

```bash
git add README.md
git commit -m "Add spec-dd to README"
```

---

### Task 10: Verify and final commit

**Step 1: Verify file structure**

Run: `find plugins/spec-dd -type f | sort`

Expected output:
```
plugins/spec-dd/.claude-plugin/plugin.json
plugins/spec-dd/LICENSE
plugins/spec-dd/skills/spec-dd/SKILL.md
plugins/spec-dd/skills/spec-dd/references/implementation-specification.md
plugins/spec-dd/skills/spec-dd/references/review.md
plugins/spec-dd/skills/spec-dd/references/specification.md
plugins/spec-dd/skills/spec-dd/references/test-specification.md
```

**Step 2: Verify marketplace.json is valid JSON**

Run: `python3 -c "import json; json.load(open('.claude-plugin/marketplace.json')); print('Valid JSON')"`

**Step 3: Verify all files are committed**

Run: `git status`

Expected: clean working tree.

**Step 4: Final verification**

Run: `git log --oneline -10`

Expected: 8-9 commits for this feature (manifest, marketplace, SKILL.md, 4 references, LICENSE, README).
