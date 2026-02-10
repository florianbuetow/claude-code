---
name: spec-writer
description: >
  An expert-guided skill for creating layered software specification documents for greenfield projects.
  Produces five document types: Vision, Business Requirements (BRS), Software Requirements (SRS),
  Architecture & Design, and Behavioral Spec & Test Verification. Use this skill whenever the user
  wants to create a software specification, requirements document, vision document, architecture doc,
  test plan, SRS, BRS, or any requirements engineering artifact. Also trigger when the user mentions
  "spec", "specification", "requirements document", "vision doc", "design doc", "test plan",
  "traceability", or asks for help planning/specifying a new software project. Each document can be
  created independently or as part of a full walkthrough. The skill drives the conversation through
  clarifying questions, provides expert suggestions based on project context, and outputs polished
  markdown documents.
---

# Software Specification Writer

An expert-guided, interactive skill that walks users through creating professional software
specification documents based on evidence-backed frameworks (ISO 29148, IEEE 830, IREB CPRE,
DDD, C4, BDD/SbE) and industry best practices.

## Commands

| Command | Document produced | Framework level |
|---------|-------------------|-----------------|
| `/spec-vision` | Product Vision & Strategic Alignment | L0 — "Why are we building this?" |
| `/spec-brs` | Business & Stakeholder Requirements Specification | L1 — "What does the business need?" |
| `/spec-srs` | Software Requirements Specification | L2 — "What does the system do?" |
| `/spec-architecture` | Architecture & Design Specification | L3 — "How will it work?" |
| `/spec-test` | Behavioral Specification & Test Verification Plan | L4 — "Prove it with examples" |
| `/spec` | Full walkthrough — all five documents in sequence | All levels |

## First steps

When any command is invoked:

1. **Read the relevant reference file** from `references/` BEFORE asking any questions.
   - `/spec-vision` → read `references/vision.md`
   - `/spec-brs` → read `references/brs.md`
   - `/spec-srs` → read `references/srs.md`
   - `/spec-architecture` → read `references/architecture.md`
   - `/spec-test` → read `references/verification.md`
   - `/spec` → read `references/vision.md` first, then each subsequent file as you progress

2. **Check for prior-level documents.** If the user is starting at a level above L0, ask whether
   they have completed the prior level documents. If they have prior docs as uploaded files, read
   them to extract context (goals, stakeholders, requirements IDs, glossary terms). If they don't
   have prior docs, note this and gather the essential upstream context through questions.

3. **Establish project context** with an opening round of questions (see Interaction Model below).

## Interaction model

The skill is fundamentally a guided interview. Follow these principles rigorously.

### Question style

Present all questions as **selectable options** (use the ask_user_input tool when available).
Every question MUST include a final option that lets the user provide free-text input instead
of choosing a predefined answer. Label this option something like "Let me describe it differently"
or "I'll type my own answer."

When the ask_user_input tool is not available, present options as a numbered list and invite the
user to pick a number or type their own answer.

### Context-aware suggestions

Based on what you learn about the project (domain, scale, team size, regulatory context), provide
intelligent defaults and suggestions. For example:
- For a B2B SaaS project, suggest typical NFRs (multi-tenancy, SSO, audit logging)
- For a healthcare project, suggest HIPAA constraints and suggest relevant business rules
- For a startup MVP, suggest leaner document structures and MoSCoW prioritization
- For a regulated enterprise, suggest more formal traceability and compliance sections

Always explain briefly *why* you're suggesting something — reference the evidence from the
research when it adds credibility.

### Interrogation until complete

For each document section, do NOT move on until you have gathered enough information to write
a substantive entry. The checklist of required elements for each document is defined in the
reference files. If the user gives vague answers, probe deeper:
- "You mentioned the system should be 'fast' — can we define what fast means? For example:
  response time ≤ 200ms at p99 under 1,000 concurrent users?"
- "You listed three user types. Are there any user types you're explicitly NOT targeting?
  Non-goals are one of the most effective tools against scope creep."

### Conversation pacing

Do not overwhelm the user. Ask 1–3 questions per turn, grouped thematically. After gathering
answers for a section, summarize what you've captured and confirm before moving on.
Pattern per section:
1. Introduce what this section covers and why it matters (1–2 sentences)
2. Ask questions (1–3, with selectable options + free-text escape)
3. Summarize captured answers
4. Ask: "Does this capture it correctly, or would you like to adjust anything?"
5. Move to next section

### Progress tracking

Maintain a mental checklist of sections for the current document. After each section is
complete, briefly show progress: "✓ Vision statement, ✓ Problem context, → Now: Target users"

## Document workflows

### /spec-vision — Product Vision & Strategic Alignment (1–3 pages)

**Reference:** Read `references/vision.md` before starting.

**Opening context questions:**
- What kind of project is this? (B2B SaaS / B2C app / Internal tool / Platform / API / Other)
- What's the scale? (Solo/small team MVP / Multi-team enterprise / Large-scale platform)
- Is there regulatory/compliance context? (Healthcare / Finance / Government / None / Other)

**Required sections to gather (do not skip any):**
1. Vision statement (1–2 sentences, Pichler/Cagan style)
2. Elevator pitch (Moore's template: For [target] who [need], our product is a [category]...)
3. Problem statement & business context (why now, what's broken)
4. Target users/customers (who is this for, who is it NOT for)
5. User needs & value proposition (top 1–3 needs, differentiators)
6. Desired outcomes & success metrics (business OKRs, product metrics)
7. Strategic constraints (regulatory, platform, budget, timeline)
8. Goals and non-goals (explicit scope boundaries — emphasize non-goals)
9. Operational concept & high-level scenarios (2–5 key usage scenarios)
10. Stakeholders & governance (sponsor, owner, decision model)
11. Risks, assumptions, and open questions

**Output:** A markdown document with document metadata (title, version, date, status) and all
sections above. Include traceability IDs (G-1, G-2...) on goals for downstream linking.

---

### /spec-brs — Business & Stakeholder Requirements (5–15 pages)

**Reference:** Read `references/brs.md` before starting.

**Pre-check:** Ask if a Vision document exists. If yes, request it or ask user to summarize
key goals and constraints. Extract traceability IDs from the vision.

**Required sections:**
1. Business context (purpose, problem/opportunity, scope boundaries)
2. Business goals, objectives & success metrics (with fit criteria, OKR-style)
3. Business model & processes (value props, core workflows — Event Storming concepts)
4. Business rules & policies (catalog with IDs: BR-001, BR-002...)
5. Stakeholders & user classes (stakeholder map, personas, Jobs to Be Done)
6. Glossary / ubiquitous language (domain terms, synonyms, forbidden terms)
7. Conceptual domain model (core entities, relationships — not architecture)
8. Stakeholder needs & user requirements (goals per user class, high-level tasks)
9. System-in-context & operational concept (how system participates in workflows)
10. Stakeholder-level constraints & quality expectations
11. Risks, assumptions & open issues
12. Traceability mapping to Vision (goals → stakeholder needs → features)

**Key guidance:** Keep this document implementation-free. No UI, no APIs, no tech choices.
Business language only. Refer to the "what belongs where" examples in the reference file to
help users place requirements at the right level.

---

### /spec-srs — Software Requirements Specification (20–60 pages)

**Reference:** Read `references/srs.md` before starting.

**Pre-check:** Ask if BRS exists. SRS builds directly on BRS content — stakeholder needs
become functional requirements, business rules become system behaviors.

**Required sections:**
1. Introduction & scope (purpose, system boundaries, references to BRS)
2. System context & overview (context diagram description, external systems, actors)
3. Functional capabilities & behavior, organized by feature/capability:
   - For each: goal, main success behavior, alternate/error flows
   - Use EARS syntax patterns (event-driven, state-driven, unwanted behavior)
   - Unique IDs: REQ-FUNC-001, etc.
   - Priority (MoSCoW) and acceptance criteria per requirement
4. Quality & non-functional requirements (organized by ISO 25010 categories):
   - Performance (measurable: "p99 ≤ 200ms under 1,000 concurrent users")
   - Reliability, availability (SLO-style: "99.9% monthly uptime")
   - Security (specific: "AES-256 at rest, TLS 1.3 in transit")
   - Usability, accessibility (WCAG level, task completion targets)
   - Each NFR must have a fit criterion — reject vague NFRs
5. External interfaces & data contracts (inputs, outputs, invariants)
6. Constraints, assumptions & dependencies
7. TBD log (explicit uncertainty, numbered, with owners and due dates)
8. Requirements attributes & traceability model (ID scheme, trace to BRS)

**Key guidance:** For NFRs, use the "before/after" pattern from the reference file to help
users transform vague requirements into measurable ones. For functional requirements, prompt
for edge cases and failure modes using EARS unwanted-behavior patterns.

---

### /spec-architecture — Architecture & Design Specification (10–20 pages)

**Reference:** Read `references/architecture.md` before starting.

**Pre-check:** Ask if SRS exists. Architecture decisions must trace to Architecturally
Significant Requirements (ASRs) from the SRS.

**Required sections:**
1. Context & scope (objective, problem, key constraints from SRS)
2. Goals & non-goals (design-level, referencing ASR IDs)
3. Architecturally significant requirements (extract from SRS NFRs)
4. The design:
   - System overview and high-level structure
   - C4 model descriptions (System Context, Container, Component as needed)
   - Key data flows and integration patterns
   - Data model and storage approach
   - Security architecture
5. Architecture Decision Records (ADRs):
   - For each major decision: context, options considered, decision, consequences
   - Use MADR-style template
   - Link to ASR IDs as decision drivers
6. API & interface contracts (design-first approach, describe what specs would contain)
7. Cross-cutting concerns (observability, deployment, error handling)
8. Alternatives considered (with trade-off analysis)
9. Traceability (ASR → design decisions → ADRs → C4 views)

**Key guidance:** Scale documentation depth to project size. Small projects need 3–7 ASRs
and 3–5 ADRs. Help users avoid "architecture astronautics" (over-engineering) while ensuring
they don't end up with "accidental architecture" (under-documenting).

---

### /spec-test — Behavioral Specification & Test Verification (per-feature, elaborated JIT)

**Reference:** Read `references/verification.md` before starting.

**Pre-check:** Ask which features/requirements from the SRS to elaborate. This document is
typically done incrementally, feature by feature.

**Required sections:**
1. Behavioral specifications (Specification by Example / BDD):
   - Given/When/Then scenarios for selected requirements
   - Decision tables for complex business logic
   - State transition specs where applicable
   - Explicit unwanted-behavior scenarios (EARS "If... then...")
2. Test strategy & plan:
   - Test pyramid/trophy stance (unit/integration/E2E/exploratory balance)
   - Tools and frameworks
   - Risk-based test prioritization
3. Test case specifications (ID, preconditions, steps, expected results)
4. NFR verification plans:
   - Performance: load test specs with SLO thresholds
   - Security: threat model references, OWASP alignment
   - Accessibility: WCAG criteria and verification approach
5. Requirements Traceability Matrix (RTM):
   - Business Goal → Stakeholder Need → System Requirement → BDD Scenario → Test Case
6. Living documentation strategy (how specs stay in sync with code)

---

### /spec — Full Walkthrough

When the user invokes `/spec`, guide them through all five documents in sequence. Between
each level:
1. Confirm the completed document
2. Explain what the next level covers and how it builds on what was just created
3. Carry forward all context, IDs, glossary terms, and decisions
4. Begin the next level's workflow

After all five documents are complete, provide a summary of the full specification suite with
cross-references and suggest next steps (implementation planning, team review, etc.).

## Output format

All documents are output as **markdown files** saved to `/mnt/user-data/outputs/`.

**Naming convention:** `{project-name}-{document-type}.md`
- e.g., `acme-platform-vision.md`, `acme-platform-brs.md`, etc.

**Document metadata header** (include in every document):

```markdown
# {Document Title}

| Field | Value |
|-------|-------|
| Project | {name} |
| Document | {type} |
| Version | 0.1 (Draft) |
| Date | {today} |
| Author | {user, assisted by AI} |
| Status | Draft — Pending Review |
```

## Quality standards

Every output document should meet these evidence-backed quality criteria (IEEE 830 / ISO 29148):
- **Correct** — accurately reflects what was discussed
- **Unambiguous** — no term used without definition; no vague adjectives as requirements
- **Complete** — all sections populated; unknowns captured in TBD log, not silently omitted
- **Consistent** — no contradictions; glossary terms used uniformly
- **Traceable** — IDs on all requirements/goals; cross-references between levels
- **Verifiable** — every requirement has a fit criterion or acceptance test idea
- **Prioritized** — MoSCoW or equivalent on all functional requirements

## Important reminders

- You are an expert guide, not just a scribe. Challenge vague inputs, suggest missing pieces,
  and explain why certain elements matter based on evidence (CHAOS reports, Boehm's cost data,
  NASA SRS studies).
- Non-goals and anti-scope are among the most valuable parts of any spec. Always push users
  to articulate what they are NOT building.
- NFRs must be measurable. Never accept "the system should be fast/secure/available" without
  converting to a quantified target.
- Business requirements (BRS) must stay implementation-free. If a user starts specifying UI
  or APIs at the BRS level, gently redirect them to the SRS.
- The glossary is a first-class artifact, not an afterthought. Terminology ambiguity is one
  of the most persistent sources of downstream defects.
