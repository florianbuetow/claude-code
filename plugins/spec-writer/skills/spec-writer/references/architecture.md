# Architecture & Design Specification -- Reference Guide

## Table of Contents

- [1. Where Level 3 sits in the stack](#1-where-level-3-sits-in-the-stack)
- [2. Comparative analysis of architecture/design document formats](#2-comparative-analysis-of-architecturedesign-document-formats)
- [3. Architecture Decision Records (ADRs) in depth](#3-architecture-decision-records-adrs-in-depth)
- [4. Visual architecture documentation](#4-visual-architecture-documentation)
- [5. API and interface contracts (design‑first)](#5-api-and-interface-contracts-designfirst)
- [6. SRS (Level 2) ↔ Architecture spec (Level 3): ASRs and ADD](#6-srs-level-2-architecture-spec-level-3-asrs-and-add)
- [7. Documenting trade-offs and alternatives](#7-documenting-trade-offs-and-alternatives)
- [8. Architecture specs in agile/evolutionary contexts](#8-architecture-specs-in-agileevolutionary-contexts)
- [9. Failure modes: absent vs excessive architecture documentation](#9-failure-modes-absent-vs-excessive-architecture-documentation)
- [10. Concrete recommendations per deliverable](#10-concrete-recommendations-per-deliverable)
- [Additional Research & Evidence](#additional-research-evidence)
- [The "level 3" specification boundary and the minimum viable document set](#the-level-3-specification-boundary-and-the-minimum-viable-document-set)
- [Comparative analysis of document formats and when to use each](#comparative-analysis-of-document-formats-and-when-to-use-each)
- [Architecture Decision Records in depth: templates, lifecycle, and empirical impact](#architecture-decision-records-in-depth-templates-lifecycle-and-empirical-impact)
- [Context](#context)
- [Decision](#decision)
- [Alternatives considered](#alternatives-considered)
- [Consequences](#consequences)
- [Visual architecture documentation: C4, UML, 4+1, and diagrams-as-code](#visual-architecture-documentation-c4-uml-41-and-diagrams-as-code)
- [Specifying API and interface contracts: OpenAPI, AsyncAPI, GraphQL SDL, and Protobuf/gRPC](#specifying-api-and-interface-contracts-openapi-asyncapi-graphql-sdl-and-protobufgrpc)
- [Traceability from SRS to architecture spec: ASRs, ADD, and IEEE architecture description](#traceability-from-srs-to-architecture-spec-asrs-add-and-ieee-architecture-description)
- [Deciding what is "just enough": agile evolution, trade-offs, and failure modes](#deciding-what-is-just-enough-agile-evolution-trade-offs-and-failure-modes)

---

Below is a synthesis oriented toward "how to actually do this" on a greenfield system, with pointers to the underlying evidence and standards.

***

## 1. Where Level 3 sits in the stack

Think in terms of three adjacent layers:

- **Requirements (Level 2: SRS)**  
  System requirements (functional, non‑functional, constraints) per IEEE 29148:2018. [standards.ieee](https://standards.ieee.org/ieee/29148/6937/)

- **Architecture/Design (Level 3)** – your target in this report  
  - Primary design/architecture document (or RFC / 6‑pager).
  - Architecture Decision Records (ADRs).
  - Visual models (C4, selected UML, deployment views).
  - Machine‑readable API / interface contracts (OpenAPI, AsyncAPI, GraphQL SDL, Protobuf IDL).

- **Implementation (Level 4)**  
  Code, infra-as-code, tests, operational runbooks.

IEEE 42010 defines an *architecture description* as a collection of artifacts (views, models, decisions, rationale) that address stakeholder concerns and explicitly calls for documenting architecture decisions and their rationale. Level 3 is essentially "the architecture description for this system." [quality.arc42](https://quality.arc42.org/standards/iso-42010)

A practical artifact stack for a greenfield system:

- One **primary design document** for the system (10–20 pages for major systems; 1–5 for minor). [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/)
- A **log of ADRs** under `docs/adr/` in the main repo. [faq.arc42](https://faq.arc42.org/questions/C-9-3/)
- A **C4 model** (C1–C2 for almost all systems; C3 selectively; C4 only when necessary). [en.wikipedia](https://en.wikipedia.org/wiki/C4_model)
- **API specs**: OpenAPI for REST, AsyncAPI for events, Protobuf/gRPC IDL, GraphQL SDL as needed. [swagger](https://swagger.io/blog/code-first-vs-design-first-api/)
- A small number of **UML sequence / deployment diagrams** for critical flows/infrastructure. [guides.visual-paradigm](https://guides.visual-paradigm.com/component-diagram-vs-deployment-diagram-in-uml/)

Everything should be *close to code* (same repo, versioned, reviewed via PR).

***

## 2. Comparative analysis of architecture/design document formats

### 2.1 Google-style Design Doc

**Structure.** An influential pattern (described in "Design Docs at Google" and summarized by others) is: [linkedin](https://www.linkedin.com/pulse/design-docs-google-gonzalo-zarazaga-x7aef)

1. **Context and Scope** – objective background, problem, constraints (but not a full requirements doc).
2. **Goals and Non‑Goals** – explicit goals and, equally important, things that are out of scope.
3. **The Actual Design** – overview then drill‑down; main structures, data flows, APIs, storage, algorithms.
4. **Alternatives Considered** – competing designs and trade‑offs.
5. **Cross‑cutting Concerns** – security, privacy, observability, reliability, compliance, etc.
6. Optional: roll‑out plan, open questions, testing strategy.

**Intended audience.** Engineers, tech leads, SREs, plus PMs for high‑level understanding.

**Typical length.** Guidance from Google‑derived sources puts the "sweet spot" for significant projects at **10–20 pages**, shorter (1–3 pages) for small changes. [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/)

**When to write one.** Internal guidance emphasizes writing design docs when the solution is non‑obvious (high ambiguity, multiple viable solutions, or high risk) and skipping them when changes are trivial or fully constrained. [developers.google](https://developers.google.com/tech-writing/one/documents)

**Evidence / effectiveness.**

- Google credits design docs with catching design issues early, scaling knowledge across teams, and forcing explicit trade‑off discussion. [linkedin](https://www.linkedin.com/pulse/design-docs-google-gonzalo-zarazaga-x7aef)
- Empirical work on architecture documentation format (narrative vs structured) suggests that the *presence* of documentation matters more than the precise structure; format had no significant impact on newcomers' understanding, while familiarity with code had the largest effect. This supports choosing a familiar, disciplined structure (like Google's) but not obsessing over the exact template. [arxiv](https://arxiv.org/abs/2305.17286)

**When to use.**  
Excellent default for:

- Medium–large projects (multi‑month, multi‑team).
- Greenfield services that will become shared platforms.
- Any change where several alternatives exist and non‑functional trade‑offs are non‑trivial.

***

### 2.2 Uber RFC / Engineering Review Docs

**Origins and structure.**

- Started as **DUCK docs** ("rubber ducking" a proposal), then evolved into Request for Comment (RFC) documents as Uber scaled beyond 50 engineers and hundreds of microservices. [newsletter.pragmaticengineer](https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs)
- Typical RFC structure (from internal templates and external write‑ups): [data.eklablog](https://data.eklablog.com/1/27/94/10/20250213/ob_9224a6_49012284639.pdf)
  - Summary / abstract  
  - Background & motivation  
  - Proposed architecture / changes  
  - Service SLAs  
  - Dependencies  
  - Load & performance expectations, capacity planning  
  - Security & privacy considerations  
  - Multi‑DC / HA considerations  
  - Operational aspects: logging, metrics, on‑call impact, support  
  - Alternatives / drawbacks  
  - Roll‑out and migration strategy  
  - Approvers and reviewers

**Process.**

- RFC emailed or submitted to domain‑specific lists (backend, mobile, etc.) for async review. [newsletter.pragmaticengineer](https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs)
- For larger orgs, Uber built internal tooling to index documents, track approvers, and link to Phabricator/JIRA. [newsletter.pragmaticengineer](https://newsletter.pragmaticengineer.com/p/rfcs-and-design-docs)
- RFCs required for **new services** and large refactors, to avoid duplicate work and surface dependencies early. [uber](https://www.uber.com/blog/building-tincup-microservice-implementation/)

**Intended audience.** Engineers across domains, SREs, architects, product/PMs for larger RFCs.

**Typical length.** 3–10 pages for most; large initiatives can be longer but remain concise (appendix for details).

**Effectiveness.**

- Uber credits RFCs with:
  - Catching duplicated efforts and dependency issues "before starting to code." [uber](https://www.uber.com/blog/building-tincup-microservice-implementation/)
  - Enabling design review at scale as the org grew to thousands of engineers. [blog.pragmaticengineer](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)
- Pragmatic Engineer's cross‑company survey notes many orgs adopting similar RFC processes to scale architectural decision‑making. [blog.pragmaticengineer](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)

**When to use.**  
Best for orgs with:

- Many services and teams where cross‑team impact is common.
- Need for *async*, organization‑wide feedback and explicit approvals.
- Desire to unify product PRDs and technical design documents into a single pipeline.

***

### 2.3 Amazon Six-page Narrative

**Format and rules.**

- Max **6 pages of prose** (no bullet‑point slide decks), written in complete sentences, read silently at the start of a meeting. [reddit](https://www.reddit.com/r/aws/comments/14df2il/how_to_write_aws_style_technical_narratives/)
- Appendices may contain diagrams, data tables, or deep technical detail; the main narrative must stand alone. [softwareseni](https://www.softwareseni.com/the-amazon-memo-culture-and-its-effect-on-system-design-how-six-page-narratives-shape-architecture/)
- Typical sections (varies by team, but common patterns in public reconstructions): [devpath](https://www.devpath.com/blog/one-pager-six-pager)
  - Background / problem statement ("why this matters").
  - Customer experience & use cases.
  - Proposed solution (architecture, data flows, APIs) explained narratively.
  - Tenets (guiding principles).
  - Trade‑offs, risks, and mitigations.
  - Success metrics & experiment plan.

**Intended audience.** Executives and senior ICs jointly; forces alignment between business and technical perspectives.

**Typical length.** Hard limit of **6 pages** for the main doc; 1–2 page "one‑pager" often used earlier for idea validation. [reddit](https://www.reddit.com/r/aws/comments/14df2il/how_to_write_aws_style_technical_narratives/)

**Effectiveness.**

- Bezos instituted six‑pagers specifically to improve depth and rigor of thinking for technical and product decisions; narrative writing exposes logical gaps and prevents slide-driven hand‑waving. [softwareseni](https://www.softwareseni.com/the-amazon-memo-culture-and-its-effect-on-system-design-how-six-page-narratives-shape-architecture/)
- External analyses argue that six‑pagers create durable records of system design choices, mitigating "nobody remembers why we did this" failure modes similar to those ADRs target. [softwareseni](https://www.softwareseni.com/the-amazon-memo-culture-and-its-effect-on-system-design-how-six-page-narratives-shape-architecture/)

**When to use.**

- Major cross‑organizational platform or product architecture decisions.
- Contexts where you must thoroughly persuade non‑engineers (e.g., capex-heavy infra, cross‑org bets).
- Complementary to, but not a replacement for, lower-level docs (ADRs, C4, API specs).

***

### 2.4 Architecture Decision Records (as a "micro-format")

Covered deeply in §3, but at the format level:

- Proposed by **Michael Nygard (2011)** as short, atomic documents with sections: **Title, Context, Decision, Status, Consequences**. [docs.publishing.service.gov](https://docs.publishing.service.gov.uk/repos/govuk-docker/adr/0001-record-architecture-decisions.html)
- Intended length: usually **<1 page** per decision.
- Audience: primarily engineers and architects; occasionally PMs and ops.

They are best thought of as the *decision log* that supports your primary design docs, not a replacement.

***

### 2.5 arc42 Template (Gernot Starke)

**Purpose.**  
arc42 is an open, vendor‑neutral architecture documentation template used widely in Europe. It is explicitly designed for "effective, practical and pragmatic" documentation. [github](https://github.com/arc42/arc42-template)

**Structure (abbreviated).** [arc42](https://arc42.org/overview)

1. Introduction & Goals (including quality goals and stakeholders)
2. Constraints
3. Context & Scope
4. **Solution Strategy** (key architectural decisions and approaches) [arc42](https://arc42.org/overview)
5. Building Block View (static decomposition; akin to C4 C2/C3) [arc42](https://arc42.org/overview)
6. Runtime View (key scenarios / sequences)
7. Deployment View
8. Cross-cutting Concepts (security, persistence, error handling, etc.)
9. Architecture Decisions (often links to ADRs)
10. Quality Requirements (NFRs, scenarios)
11. Risks & Technical Debt
12. Glossary

**Intended audience.** Broad: developers, ops, management, sometimes auditors and external partners.

**Typical length.** Highly variable; for typical product systems, 20–50 pages including diagrams, but arc42 authors stress "fill only what's useful" and that not all sections need equal depth.

**Effectiveness.**

- SE Radio interview with Starke emphasizes that arc42 forces documentation of **reasons**, not just structures, especially in white‑box templates that ask "why these components and not others." [youtube](https://www.youtube.com/watch?v=xchTKbEhchc)
- arc42 aligns well with ISO 42010's emphasis on views, viewpoints, and rationale. [standards.ieee](https://standards.ieee.org/ieee/42010/5334/)

**When to use.**

- Systems that need *long-lived, multi-audience* documentation: regulated, safety‑critical, enterprise platforms, government projects.
- Good umbrella under which to plug in C4 diagrams, ADRs, and API specs.

***

### 2.6 4+1 View Model (Kruchten)

The 4+1 model is a conceptual framework organizing architecture descriptions into five views: [software-architecture-guild](https://software-architecture-guild.com/guide/competencies/modeling/frameworks/4-plus-1/)

- **Logical view** – key abstractions and responsibilities (classes, domain concepts).
- **Process view** – concurrency, processes, runtime behavior.
- **Development view** – code/module organization.
- **Physical view** – deployment to hardware / nodes.
- **Scenarios (+1)** – representative use cases tying views together.

Not a concrete template by itself, but a useful checklist to ensure your C4 diagrams, sequence diagrams, and deployment views collectively cover stakeholder concerns.

***

### 2.7 Choosing a format by project type and team size

**Small product / startup (1–2 teams).**

- Primary artifact: **Google-style design doc** (3–10 pages) or lightweight RFC.
- ADR log in repo.
- C4 C1/C2 diagrams; a couple of sequence diagrams.
- arc42 not necessary in full; you can borrow sections as needed.

**Medium product (3–6 squads; internal platform or B2B product).**

- Primary artifact: **Google-style design doc or Uber-style RFC**, depending on org culture.
- ADR log in repo.
- One or more **C4 workspaces** (C1–C3) plus deployment view.
- **Partial arc42** structure or 4+1 mapping: especially Solution Strategy, Building Block View, Deployment, Quality Requirements.

**Large, regulated, safety‑critical, or cross‑enterprise systems.**

- **arc42 template** or equivalent, completed at least at a high level.
- ADRs as decision log.
- C4 + 4+1 aligned diagrams.
- For major decisions, **Amazon‑style six‑page narratives** (or equivalent) for executive review.

Empirical evidence suggests that the *existence* and *integration* of architecture documentation, plus its linkage to code and decisions, is more important than the specific template. [research.rug](https://research.rug.nl/en/publications/enriching-software-architecture-documentation)

***

## 3. Architecture Decision Records (ADRs) in depth

### 3.1 Origins and core template

Michael Nygard's original ADR pattern (2011): [faq.arc42](https://faq.arc42.org/questions/C-9-3/)

- **Title** – with an ID, e.g., "ADR 9: LDAP for multitenant integration".
- **Context** – forces at play (technical, organizational, political, constraints).
- **Decision** – what choice was made to resolve the forces.
- **Status** – proposed, accepted, deprecated, superseded, etc.
- **Consequences** – all consequences, positive and negative.

This has been widely adopted (e.g., UK Government Digital Service, GOV.UK, many OSS projects). [gds-way.digital.cabinet-office.gov](https://gds-way.digital.cabinet-office.gov.uk/standards/architecture-decisions.html)

### 3.2 MADR and evolutions (Y‑statements, extended metadata)

The **MADR (Markdown Architectural Decision Record)** template extends Nygard with a bit more structure: [ozimmer](https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html)

- Context and Problem Statement
- Decision Drivers (key ASRs, business goals, constraints)
- Considered Options
- Pros and Cons for each option
- Decision Outcome (chosen option and rationale)
- Status, Date
- Consequences
- References, links

MADR is partially derived from the **Y‑statement format** ("In the context of X, facing Y, we decided for Z and against W to achieve V"), which comes from research on *sustainable architectural decisions*. [ceur-ws](https://ceur-ws.org/Vol-2072/paper9.pdf)

### 3.3 Where ADRs live and how they form a timeline

Best practices from GDS, various government and OSS projects: [wiki.simpler.grants](https://wiki.simpler.grants.gov/decisions/adr/2023-06-26-recording-architecture-decisions)

- Store ADRs **in the same version control repo as the code**, typically under `docs/adr/` or `doc/adrs/`.
- Use text formats (Markdown/AsciiDoc) so they diff well and are easy to review. [openpracticelibrary](https://openpracticelibrary.com/practice/architectural-decision-records-adr/)
- Name files sequentially or by date, e.g., `0001-record-architecture-decisions.md`. [docs.publishing.service.gov](https://docs.publishing.service.gov.uk/repos/govuk-docker/adr/0001-record-architecture-decisions.html)
- Treat the collection as an **append-only decision log**:
  - Old ADRs are never deleted; instead, mark as **superseded** with a link to the new ADR.
  - This forms an explicit **history of architectural evolution** over time. [keeling](https://keeling.dev/essays/psychology-of-architecture-decision-records/)

### 3.4 Lifecycle and usage

A practical lifecycle:

1. **Raise** an ADR when:
   - A decision affects architecture significantly (ASR),  
   - Has cross-team impact,  
   - Or will be hard/expensive to change later.
2. **Proposed** – drafted and circulated (often linked from an RFC or design doc).
3. **Accepted / Rejected** – once reviewed.
4. Later: **Deprecated / Superseded** – when replaced, with pointers.

Joel Parker Henderson's "decision-record" repo generalizes this to **Decision Records (DRs)** beyond architecture and provides templates and governance advice. [github](https://github.com/joelparkerhenderson/decision-record)

Tooling like **Nat Pryce's `adr-tools`** and various MADR helpers support creating, listing, and linking ADRs. [ceur-ws](https://ceur-ws.org/Vol-2072/paper9.pdf)

### 3.5 Evidence ADRs help

Several lines of evidence:

- **ThoughtWorks Technology Radar** moved ADRs into "Adopt", reflecting observed success across many client projects (referenced in Red Hat's write‑up). [redhat](https://www.redhat.com/en/blog/architecture-decision-records)
- Keeling's **"Psychology of Architecture Decision Records"** (IEEE Software, 2022) reports from extensive field use that ADRs: [keeling](https://keeling.dev/essays/psychology-of-architecture-decision-records/)
  - Encourage developers to think architecturally.
  - Provide an accessible history of why architecture changed.
  - Help teams understand and revisit trade‑offs explicitly.
- Endjin's case study emphasizes that ADRs stored alongside code let documentation "reflect a specific state of the system," supporting change over time and avoiding analysis paralysis by allowing decisions at the last responsible moment with recorded context. [endjin](https://endjin.com/blog/2023/07/architecture-decision-records)
- Design rationale literature (Dutoit, Paech, Burge & Brown, etc.) has long shown rationale is valuable for maintenance, verification, and evaluation but often fails in practice due to overhead and tooling complexity. ADRs can be seen as a lightweight, pragmatic embodiment of rationale management principles. [cambridge](https://www.cambridge.org/core/journals/ai-edam/article/special-issue-design-rationale/BC91F6968115F74046BD4A7DD1E89445)

### 3.6 Recommended ADR template

For a greenfield project, a **slightly streamlined MADR** works well:

- **Title**: "ADR-0007: Choose Kafka for Event Backbone"
- **Status**: Proposed | Accepted | Rejected | Superseded by ADR-00XX
- **Date**
- **Context and Problem Statement**
- **Decision Drivers**
  - Referencing ASR IDs from the SRS (e.g., NFR-001 latency, NFR-004 durability).
- **Considered Options**
  - Option A – …
  - Option B – …
- **Decision Outcome**
  - Chosen option and key reasons.
- **Consequences**
  - Positive, negative, neutral.
- **Links**
  - To design doc sections, C4 views, tickets.

That explicit linkage to ASRs and design doc sections is key for traceability (see §6).

***

## 4. Visual architecture documentation

### 4.1 The C4 model

**Concept.**  
The C4 model is a lean graphical notation for software architecture based on hierarchical structural decomposition: [simonscholz](https://simonscholz.dev/tutorials/c4-software-architecture-diagrams/)

- **C1 – System Context**: System and its external actors/systems.
- **C2 – Container**: Major deployable/runtime units (services, UIs, databases, queues).
- **C3 – Component**: Logical components within a container.
- **C4 – Code**: Classes, modules, methods (often auto‑generated UML/ER).

C4 focuses on a small set of elements (Person, Software System, Container, Component, Relationship) and leaves visual style flexible. [en.wikipedia](https://en.wikipedia.org/wiki/C4_model)

**Why it works.**

- It closely follows 4+1/ISO 42010 notions of views and stakeholder concerns. [quality.arc42](https://quality.arc42.org/standards/iso-42010)
- It allows zooming from business‑level context to developer‑level structure in a consistent way. [icepanel](https://icepanel.io/blog/2022-10-03-c4-model-for-system-architecture-design)
- Many teams find **C1 and C2** deliver most of the value; C3 is used for complex subsystems, C4 rarely or generated from code. [revision](https://revision.app/blog/practical-c4-modeling-tips)

**Evidence of effectiveness.**

- Case studies and vendor write‑ups report improved cross‑team communication, especially across technical/non‑technical stakeholders. [valueblue](https://www.valueblue.com/blog/c4-model-in-enterprise-architecture)
- Empirical studies of using C4 for architecture visualization (case‑study based) indicate that it is easy for industry devs to pick up and that its lightweight nature helps teams otherwise unfamiliar with structured modeling methods. [ceur-ws](https://ceur-ws.org/Vol-4034/paper95short.pdf)

**Practical C4 workflow for a greenfield project.**

1. **C1 – System Context**
   - One diagram per system: users, external systems, high‑level purpose.
   - Use in SRS review and initial stakeholder alignment.

2. **C2 – Container**
   - Show all services, UIs, data stores, message brokers, external dependencies.
   - Annotate containers with key responsibilities and relevant ASRs (e.g. "handles P95 < 100 ms for search"). [en.wikipedia](https://en.wikipedia.org/wiki/Attribute-driven_design)

3. **C3 – Component**
   - Only for complex containers (e.g. central API gateway, orchestration service).
   - Focus on architecturally significant components, not every class.

4. **C4 – Code**
   - Generate as needed from IDE/UML tools; don't hand‑maintain.

**Tools.**

- **Structurizr** (DSL + SaaS/self‑hosted) – defines a single model, generates multiple C4 views; supports export to PlantUML, Mermaid, etc. [dev](https://dev.to/simonbrown/diagrams-as-code-2-0-82k)
- **C4-PlantUML**, **Mermaid** – diagrams as code; good for embedding in repos and docs. [gotopia](https://gotopia.tech/episodes/298/creating-software-with-modern-diagramming-techniques-build-better-software-with-mermaid)
- Traditional tools (draw.io, Gliffy, IcePanel) can be used as front‑ends, but for long‑lived docs, diagrams‑as‑code integrations are usually better. [revision](https://revision.app/blog/diagram-as-code)

***

### 4.2 UML: what's still useful

UML as a whole is heavyweight, but specific diagram types remain valuable: [visual-paradigm](https://www.visual-paradigm.com/guide/uml-unified-modeling-language/what-is-uml/)

- **Sequence diagrams** – excellent for documenting critical flows (auth, payment, failure handling, external integrations). Many practitioners in domains like PCI-compliant systems still rely heavily on them. [reddit](https://www.reddit.com/r/softwarearchitecture/comments/1ly9tv7/are_uml_diagrams_really_useful_in_realworld/)
- **Component diagrams** – higher-level module and interface structure, particularly useful for aligning logical decomposition with C4 C3. [guides.visual-paradigm](https://guides.visual-paradigm.com/component-diagram-vs-deployment-diagram-in-uml/)
- **Deployment diagrams** – mapping software artifacts to nodes, capturing topology, redundancy, and key infrastructure decisions; especially useful for operations, capacity planning, and compliance. [geeksforgeeks](https://www.geeksforgeeks.org/system-design/deployment-diagram-unified-modeling-languageuml/)

Empirical work and experiments suggest that *graphical design descriptions* improve active discussion and recall of design details compared to purely textual descriptions. That supports including at least a handful of UML/C4 diagrams for key areas. [arxiv](http://arxiv.org/pdf/2305.17286.pdf)

***

### 4.3 Diagrams as code

"Diagrams as code 2.0" (Simon Brown) argues for defining a **single model** and generating multiple diagrams (views) from it, to avoid DRY violations across separate diagram source files. Structurizr implements this idea. [dev](https://dev.to/simonbrown/diagrams-as-code-2-0-82k)

Benefits: [gotopia](https://gotopia.tech/episodes/298/creating-software-with-modern-diagramming-techniques-build-better-software-with-mermaid)

- Version-controlled diagrams, reviewed in PRs.
- Easier refactoring and automated regeneration.
- Better consistency across C1–C3, deployment, and dynamic views.

Trade‑offs:

- DSL syntax overhead (Mermaid, PlantUML, Structurizr).
- Less accessible to non‑developers unless paired with rendered diagrams in wikis.

For a greenfield system with a dev-heavy audience, C4 via Structurizr DSL or PlantUML/Mermaid is usually an excellent default.

***

### 4.4 Mapping C4 to 4+1 and arc42

- **Logical view (4+1)** ⇔ C4 C2/C3 plus domain models.
- **Process view** ⇔ sequence diagrams and C4 dynamic views (if used).
- **Development view** ⇔ module/package view; can be expressed via C3 or UML component diagrams.
- **Physical view** ⇔ deployment diagrams and infra‑as‑code representations.
- **Scenarios** ⇔ runtime view (arc42 §6) + sequence diagrams + narrative scenarios. [themightyprogrammer](https://themightyprogrammer.dev/article/kruchten-software-view-model)

arc42 explicitly allocates space for **Building Block View** (C2/C3), **Runtime View**, and **Deployment View**, making it straightforward to plug C4 and UML diagrams into the template. [arc42](https://arc42.org)

***

## 5. API and interface contracts (design‑first)

### 5.1 Design-first vs code-first

**Code-first**:

- Write implementation code first, generate OpenAPI from annotations or reflection afterward. [apidog](https://apidog.com/blog/code-first-vs-design-first-api-doc-workflows/)
- Pros: lower startup overhead, good for small, rapidly evolving prototypes.
- Cons: API shape emerges implicitly from code; hard to coordinate with non‑backend stakeholders; higher risk of later breaking changes and ad‑hoc inconsistencies.

**Design-first (API-first)**:

- Design and agree on an API specification (OpenAPI, AsyncAPI, GraphQL SDL, Protobuf) *before* implementation. [learn.openapis](https://learn.openapis.org/best-practices.html)
- Spec becomes a **contract** between producers and consumers; code generated/as scaffolded from the spec.

Benefits documented across multiple sources: [codecentric](https://www.codecentric.de/en/knowledge-hub/blog/charge-your-apis-volume-26-choosing-the-right-api-development-strategy-a-guide-to-api-design-first-vs-code-first-approaches)

- **Collaboration & alignment** – product, frontend, backend, QA, and external integrators can agree on the contract upfront.
- **Parallel workstreams** – frontends and testers can develop against **mock servers** generated from the spec while backend is still implementing. [api7](https://api7.ai/es/learning-center/api-101/api-first-development)
- **Quality & consistency** – linting and style guides for specs; central governance for naming, error models, auth.
- **Reduced integration issues** – API-first adopters report substantially fewer integration problems; one experience report cites up to **50% fewer integration issues** and **20–30% faster development cycles** due to parallelism and early validation. [api7](https://api7.ai/es/learning-center/api-101/api-first-development)
- **Better documentation & DX** – interactive docs (Swagger UI, Redoc), codegen for SDKs.

The OpenAPI Initiative itself describes design‑first as writing the API description first, then following with code, with obvious advantages around generating boilerplate and skeletons. Swagger's own comparison argues that while code-first may be faster for simple cases, design-first improves long‑term consistency and allows non‑developers to participate effectively. [swagger](https://swagger.io/blog/code-first-vs-design-first-api/)

### 5.2 How machine-readable specs complement the prose design doc

A good Level 3 stack uses **both**:

- The **design doc**:
  - Explains rationale and broader context (why this API exists, key use cases, performance and reliability goals, security model).
  - Summarizes major resources/operations and error handling patterns.
  - Links to the canonical OpenAPI/AsyncAPI/SDL/IDL files in the repo.

- The **spec** (OpenAPI, AsyncAPI, etc.):
  - Provides the precise, machine‑readable contract.
  - Drives codegen, mocks, contract tests, documentation, and client SDKs.

Recommended pattern:

- For each major service, create an API spec at `/apis/` (e.g., `/apis/payments/openapi.yaml`).
- The design doc has a section like **"Public API"** which:
  - Shows a C4 C2 diagram for the service.
  - Lists key operations in human language.
  - Links to the spec files.
- For event-driven systems, pair REST OpenAPI with **AsyncAPI** describing topics, message schemas, and consumer responsibilities.

***

## 6. SRS (Level 2) ↔ Architecture spec (Level 3): ASRs and ADD

### 6.1 Architecturally Significant Requirements (ASRs)

ASRs are those requirements that have a **measurable effect on architecture** — a subset of all requirements that significantly shape structure, technology choices, and quality attributes. [en.wikipedia](https://en.wikipedia.org/wiki/Architecturally_significant_requirements)

Characteristics and indicators: [ida.liu](https://www.ida.liu.se/~TDDC88/openup/core.tech.common.extend_supp/guidances/concepts/arch_significant_requirements_1EE5D757.html)

- Often non‑functional (performance, reliability, security, scalability, etc.), but can also be functional.
- Hard to satisfy, strict or non‑negotiable, high business value or technical risk.
- Affect multiple components; changing them implies significant rework.
- Examples:
  - "System must handle 10K concurrent users with P95 latency < 100 ms from EU."
  - "Regulatory requirement: all PII must be stored within the EU, encrypted at rest, & auditable."
  - "System must support offline operation with eventual synchronization."

ASRs typically come from the **SRS** (IEEE 29148) where NFRs, constraints, and key functional requirements are specified. Non‑functional requirements are often architecturally significant and are sometimes called **architectural characteristics**. [cwnp](https://www.cwnp.com/req-eng/)

### 6.2 Attribute-Driven Design (ADD)

SEI's **Attribute-Driven Design (ADD)** method is explicitly based on ASRs: [sei.cmu](https://www.sei.cmu.edu/library/attribute-driven-design-create-software-architectures-using-architecturally-significant-requirements/)

- Inputs: functional requirements, quality attribute requirements, constraints (collectively, ASRs).
- Iterative steps:
  1. Choose a system element to design (initially the whole system).
  2. Identify **ASRs** relevant to that element.
  3. Design (or refine) the architecture for that element using patterns/tactics to satisfy ASRs.
  4. Produce architectural views (sketches) and validate against ASRs.
  5. Repeat for sub‑elements.

ADD thus gives you a **systematic trace** from requirements → architectural structures.

### 6.3 IEEE 42010 vs IEEE 29148

- **IEEE/ISO/IEC 29148:2018** – requirements engineering standard defining SRS, characteristics of good requirements, and related processes. [cdn.standards.iteh](https://cdn.standards.iteh.ai/samples/72089/62bb2ea1ef8b4f33a80d984f826267c1/ISO-IEC-IEEE-29148-2018.pdf)
- **IEEE/ISO/IEC 42010:2022** – architecture description standard defining architecture description, stakeholders, concerns, views, viewpoints, and explicitly requiring documentation of architecture decisions and rationale tied to concerns and requirements. [iso-architecture](http://www.iso-architecture.org/ieee-1471/ads/)

Relationship:

- Requirements (29148) identify **stakeholder needs and constraints**.
- Architecture description (42010) structures how the system will satisfy those concerns, via views and explicit decisions and rationale.
- A well‑constructed Level 3 architecture spec therefore:
  - Identifies **stakeholders and concerns**.
  - States **ASRs** clearly.
  - Provides views (C4, runtime, deployment) that **address** these ASRs.
  - Records **decisions and rationale** (via ADRs and design docs) that trace back to ASRs. [standards.ieee](https://standards.ieee.org/ieee/42010/5334/)

### 6.4 Practical traceability model

For a greenfield project, use IDs consistently:

1. In the **SRS**:
   - Tag ASRs as `ASR-xxx` or `NFR-xxx` (e.g., `ASR-001: Availability 99.95% in region EU-West`, `ASR-004: P95 latency < 100 ms`).

2. In the **design doc**:
   - In **Goals** / **Quality Requirements**, list relevant ASR IDs.
   - In each major design section, annotate which ASRs it addresses.

3. In **ADRs**:
   - Under "Decision Drivers", list the ASRs that motivate this decision, e.g., `Decision Drivers: ASR-001, ASR-004, ASR-010`. [ozimmer](https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html)

4. In **C4 and other diagrams**:
   - Use tags or notes to annotate containers/components that primarily address specific ASRs (e.g., "edge-caching-proxy – ASR-004 (latency), ASR-011 (cost)").

5. In **tests and SLAs**:
   - Map performance tests, chaos experiments, and SLOs to ASR IDs, closing the loop.

This gives you end‑to‑end traceability without heavyweight tooling: SRS → ASRs → design/ADRs → architecture views → tests/SLAs.

***

## 7. Documenting trade-offs and alternatives

### 7.1 Why "Alternatives Considered" rots fastest

Google-style design docs explicitly call "Alternatives Considered" one of the most important sections because it explains *why* the chosen design is better than other plausible options and answers "why not X?" questions upfront. If this isn't written, institutional memory relies on hallway conversations and chat logs that decay rapidly. [industrialempathy](https://www.industrialempathy.com/posts/design-docs-at-google/)

Design rationale research since the 1970s (IBIS, QOC, etc.) has consistently argued that: [web.cs.wpi](https://web.cs.wpi.edu/~dcb/Papers/DCC-paper-04.pdf)

- Alternatives, arguments, and trade‑offs:
  - Help detect design errors earlier (during analysis and design, not during coding). [ftp.cs.wpi](https://ftp.cs.wpi.edu/pub/techreports/pdf/99-27.pdf)
  - Improve design verification and evaluation (checking intent vs. implementation).
  - Aid maintenance and evolution by explaining why constraints exist.
- However, heavy rationale systems often fail in practice due to capture overhead and lack of tool integration. [se.ifi.uni-heidelberg](http://se.ifi.uni-heidelberg.de/fileadmin/pdf/publications/RMiSE.pdf)

### 7.2 Lightweight rationale via ADRs and design docs

Using **"Alternatives Considered"** in design docs and **options/pros/cons** sections in ADRs (as in MADR) gives you most of the benefits with minimal ceremony: [openpracticelibrary](https://openpracticelibrary.com/practice/architectural-decision-records-adr/)

- For each significant decision:
  - Enumerate 2–4 realistic options.
  - For each, list 3–7 pros/cons, explicitly relating to ASRs.
  - Record why the chosen option best balances those ASRs *given current constraints*.

Empirical and field experience suggests that such lightweight rationale helps teams: [endjin](https://endjin.com/blog/2023/07/architecture-decision-records)

- Avoid revisiting the same debates.
- Onboard newcomers faster ("why do we use X instead of Y?").
- Reevaluate past decisions more rationally when context changes.

***

## 8. Architecture specs in agile/evolutionary contexts

### 8.1 Just Enough Architecture Up Front (JEAUF) and Last Responsible Moment

Mary and Tom Poppendieck's "last responsible moment" principle: *defer commitment until the moment at which failing to decide eliminates an important alternative*. In other words: [linkedin](https://www.linkedin.com/pulse/technical-decisions-series-decision-reversibility-papadimitriou)

- Deciding **too early** risks over‑engineering for imagined futures.
- Deciding **too late** forces suboptimal defaults and expensive rework.

Practically, this implies:

- Identify **irreversible or expensive‑to‑change decisions** (e.g., core data model, tenancy model, deployment model, major tech stack choices) – these warrant early ADRs.
- For **reversible** or low‑impact decisions (e.g., small library choices, internal naming), decide later or let teams self‑organize.

Articles caution that "last responsible moment" must not become procrastination; leaving many decisions open increases cognitive load and can stall progress. [ben-morris](https://www.ben-morris.com/lean-developments-last-responsible-moment-should-address-uncertainty-not-justify-procrastination/)

### 8.2 Evolutionary Architecture and fitness functions

Neal Ford, Rebecca Parsons et al. define **evolutionary architecture** as one that supports *guided, incremental change across multiple dimensions*. [youtube](https://www.youtube.com/watch?v=Uce-sRp2IGw)

Key ideas:

- Use **fitness functions** (automated checks) to continuously validate architectural characteristics (performance, coupling, modularity, etc.).
- Design **architecture quanta** – units of architecture that can change independently, limiting the blast radius and supporting structural evolution. [youtube](https://www.youtube.com/watch?v=m2ZlX1je3as)
- Fast feedback (CI/CD, monitoring) plus loosely coupled boundaries enables architecture changes without big-bang redesigns. [youtube](https://www.youtube.com/watch?v=Uce-sRp2IGw)

This meshes well with ADRs and C4:

- ADRs document decisions and changes over time.
- C4 views show structure and coupling.
- Fitness functions enforce ASRs continuously.

### 8.3 Architectural runway (SAFe)

In SAFe, **architectural runway** is the existing technical foundation (code, infrastructure, frameworks) that enables quick implementation of upcoming features without excessive redesign. [valueglide](https://www.valueglide.com/what-does-architectural-runway-mean-in-safe/)

- Built via **Enabler Epics/Features** that fund architecture and infra work explicitly.
- Managed as a first‑class concern in PI planning (runway budget). [agileseekers](https://agileseekers.com/blog/mapping-enablers-to-architectural-runway-in-safe-portfolios)
- Aims to avoid hitting architectural "walls" mid‑feature development.

For a greenfield system, architectural runway usually includes:

- Base platform (service mesh, CI/CD, logging/metrics, auth).
- Shared data platform decisions.
- Reusable API and messaging patterns.

### 8.4 How much architecture before coding?

Combine these ideas into a **heuristic framework** based on three axes: *scale*, *criticality*, *uncertainty*.

**Small scale, low/medium criticality, high uncertainty (e.g., new product in a startup).**

- Up‑front:
  - 3–7 clear ASRs and constraints.
  - 3–10 page design doc.
  - C4 C1/C2.
  - 2–5 initial ADRs for truly hard‑to‑change choices (data store, deployment model, major third‑party dependencies).
  - Design-first API specs for any externally consumed APIs.
- Then:
  - Start coding early; rely on ADRs + C4 to evolve architecture as you learn.
  - Use fitness functions where feasible (e.g., basic latency SLOs).

**Medium scale (several squads), medium/high criticality.**

- Up‑front:
  - Clear SRS with ASRs prioritized.
  - 10–20 page design doc or RFC, reviewed cross‑team.
  - C4 C1/C2 plus C3 for key platform containers.
  - Architecture runway defined for 1–2 PIs (platform/infrastructure capabilities).
  - ADRs for major cross‑team decisions (integration patterns, data domains, auth model).
- Then:
  - Continue capturing decisions in ADRs and updating C4 as you build.
  - Define fitness functions for main quality attributes over time.

**High scale or safety/mission‑critical.**

- Up‑front:
  - More systematic **ADD** iterations to design for ASRs before heavy implementation. [sei.cmu](https://www.sei.cmu.edu/documents/2545/2018_010_001_513930.pdf)
  - arc42 or similar template fully instantiated at high level.
  - Hazard analysis, formal modeling where mandated.
- Still:
  - Embrace evolutionary principles and ADRs; architecture must evolve safely, not be frozen.

The empirical doc study by Ernst & Robillard suggests that, for smaller systems, the specific format of architecture documents doesn't significantly affect understanding; what matters is that documentation exists, is reasonably structured, and is complemented by code exploration. This supports "just enough, but actually maintained" over gold‑plated architecture tomes. [arxiv](https://arxiv.org/abs/2305.17286)

***

## 9. Failure modes: absent vs excessive architecture documentation

### 9.1 Absent or weak documentation → accidental architecture

Grady Booch notes that every interesting software‑intensive system has an architecture; many are **accidental**, emerging from uncoordinated local decisions rather than intentional design. Consequences observed in industry case studies: [objectcomputing](https://objectcomputing.com/how-we-share/articles/2024/06/06/business-leaders-how-do-you-know-if-your-enterprise-has-acci)

- Fragile systems with implicit coupling and "architecture by accident."
- Knowledge trapped in a "walking architecture" (one or two senior devs) rather than shared artifacts. [arxiv](https://arxiv.org/pdf/2503.08628.pdf)
- Large outages or degraded performance traceable to historical, undocumented decisions.

Agile misapplied as "no design, just code" accelerates this drift; over years, systems become unstable and very expensive to change. [genehughson.wordpress](https://genehughson.wordpress.com/2014/07/18/accidental-architecture/)

### 9.2 Excessive or over‑abstract documentation → architecture astronautics

Joel Spolsky's "architecture astronaut" critique still applies: architects who spend their time on grand, abstract architectures disconnected from actual needs and constraints. Contemporary commentary highlights: [swiderski](https://swiderski.tech/2024-05-14-architecture-astronautics/)

- Over‑engineering for Facebook/Netflix scale when building a small product.
- Technology/tool obsession ("we have Kafka, therefore everything is an event").
- Multi‑layer abstractions and frameworks that few can understand, slowing delivery and deterring changes.

### 9.3 Empirical perspective: documentation vs outcomes

- **Format vs usefulness.**  
  Ernst & Robillard's controlled study found that for newcomers working with ~1,000 words of architecture documentation, **document format (narrative vs structured) had little effect** on task performance; familiarity with the code and the specific information sought was more important. Structured docs were perceived as somewhat easier to navigate, but not significantly. [arxiv](https://arxiv.org/abs/2305.17286)
- **Graphical vs textual.**  
  Experiments with students showed that graphical design descriptions improved active discussion and recall of design details compared to pure text. [research.tue](https://research.tue.nl/files/354706907/2503.08628v1.pdf)
- **Architectural knowledge & project outcomes.**  
  Work on *architectural knowledge* (AK) highlights shortcomings of traditional docs and argues for enriching them with explicit decisions and rationale to improve reuse and evolution. More general project‑level research shows that explicit project artefacts and shared understanding ("knowledge alignment") are positively associated with business value realization in IT projects. [studeersnel](https://www.studeersnel.nl/nl/document/radboud-universiteit-nijmegen/knowledge-in-organizations/material-for-th1-knowledge-management-and-project-performance-analysis/152453573)
- **Design rationale.**  
  Design rationale research concludes that rationale helps detect errors earlier, supports maintenance and change, and improves design quality, but must be integrated lightly into the development process to be adopted broadly. [books.google](https://books.google.com/books/about/Rationale_Management_in_Software_Enginee.html?id=QKlQAAAAMAAJ)

Combined, this suggests:

- You want **intentional, light‑weight but complete** architecture documentation (design docs + ADRs + diagrams), close to code.
- Avoid both extremes: no docs (accidental architecture) and huge detached architecture frameworks (astronautics).

***

## 10. Concrete recommendations per deliverable

### 10.1 Comparative analysis & recommendations

**Short version:**

- Default for most greenfield projects:
  - **Google-style design doc** (or Uber-style RFC if your org is already RFC‑driven).
  - ADR log in repo.
  - C4 diagrams (C1/C2, plus C3 where necessary).
  - API specs (design‑first).
- For larger or regulated systems:
  - Wrap above inside **arc42** or a 4+1‑aligned structure to cover multi‑stakeholder concerns.
  - Use Amazon‑style narratives for major cross‑org decisions.

Use project scale, criticality, and uncertainty to tune depth as described in §8.4.

***

### 10.2 ADR template and lifecycle (with example)

**Template (MADR‑style, minimal):**

- Title, Status, Date
- Context and Problem Statement
- Decision Drivers (ASR/NFR IDs)
- Considered Options
- Decision Outcome
- Consequences
- Links (design doc sections, C4 views, tickets)

**Lifecycle:**

- Created as "Proposed" when a significant decision arises.
- Reviewed via normal code review/RFC process; moved to "Accepted" or "Rejected."
- Later decisions "Supersede" older ADRs, but never delete them.
- All ADRs live under `docs/adr/` or similar in the main repo, version‑controlled.

**Example (sketch):**

> ADR-0005: Choose Postgres for primary OLTP store  
> Status: Accepted  
> Context: Need a transactional store for core account data; ASR-001 (99.95% availability), ASR-004 (P95 < 100 ms), ASR-010 (EU data residency)…  
> Decision Drivers: ASR-001, ASR-004, ASR-010, constraint C-03 (team skillset)  
> Options: Managed Postgres, Managed MySQL, NoSQL (DynamoDB) …  
> Decision Outcome: Choose managed Postgres in region eu-west‑1 with multi‑AZ…  
> Consequences: + Strong consistency, familiar query model; – Vertical scaling limits, future sharding complexity…

***

### 10.3 Practical guide to C4 modelling for greenfield projects

1. **Start from ASRs and bounded contexts.**
   - Identify main domain areas and quality drivers.
2. **Draw C1 (System Context).**
   - One diagram; keep it business‑friendly.
3. **Draw C2 (Container).**
   - List all services, UIs, data stores, event busses.
   - Annotate each container with responsibility and relevant ASRs.
4. **Selectively draw C3.**
   - Only for containers where internal structure matters architecturally (e.g., orchestration vs. choreography).
5. **Derive deployment and runtime views.**
   - Use C2 as basis for deployment diagrams and runtime/sequence views for key scenarios.
6. **Integrate with tools.**
   - Choose **Structurizr DSL** if you want a single model → multiple views. [docs.structurizr](https://docs.structurizr.com/export/mermaid)
   - Or **C4-PlantUML/Mermaid** if you prefer simple text DSLs embedded in Markdown. [revision](https://revision.app/blog/diagram-as-code)
7. **Maintain with code.**
   - Keep diagram source in repo.
   - Update C2/C3 when ADRs change major structure.

***

### 10.4 API-first design specification (with examples)

Suggested workflow:

1. **Identify API consumers and use cases.**
   - Frontends, other services, external partners.
2. **Draft OpenAPI / AsyncAPI / SDL / IDL.**
   - Use design‑first tools (e.g., Stoplight, SwaggerHub, Insomnia) or plain YAML.
3. **Review API contracts.**
   - With product, frontend, backend, QA; treat spec as a contract.
   - Validate against ASRs (e.g., payload sizes, pagination, rate limits).
4. **Generate mocks & client/server stubs.**
   - Frontends and testers start against mocks.
5. **Implement backend to spec.**
   - Use contract tests to ensure implementation adheres to spec.
6. **Link in design doc and ADRs.**
   - Design doc's API section points to spec file.
   - ADRs record major API style decisions (REST vs gRPC, resource structure, versioning).

Example mapping:

- `apis/payments/openapi.yaml` – REST API for payments.
- `apis/payments-events/asyncapi.yaml` – event topics for payment status changes.
- Design doc section "3.2 Payments API" describes business semantics and refers to both specs.

***

### 10.5 Framework for "just enough" documentation

Use this decision matrix:

- Document a **design doc section + ADR** when a decision:
  - Impacts **multiple teams**.
  - Is **difficult or expensive to change** later.
  - Relates to a **primary ASR** (availability, latency, compliance, data model, integration).
- Use **only ADR (no large section)** when:
  - Decision is local but still architecturally significant (e.g., choose library X that shapes internal architecture).
- Use **code + short comment** when:
  - Decision is reversible, small in scope, low risk.

Limit diagrams to:

- 1× C1 per system.
- 1–2× C2 per system variant (e.g., normal vs DR topologies).
- C3 only for tricky containers.
- 2–5 sequence diagrams for key flows.
- 1 deployment diagram for main environment (or rely on IaC + textual explanation).

Review docs regularly (e.g., once per quarter or PI) for **alignment with reality**, not for prose polish.

***

### 10.6 Traceability model (decisions ↔ NFRs/constraints)

Implement traceability with **lightweight IDs**:

- SRS: `ASR-###`, `FR-###`, `CON-###`.
- Design doc: references ASRs explicitly in goals & per-section notes.
- ADRs: "Decision Drivers: ASR-001, ASR-004, CON-003."
- C4: tags or notes referencing ASRs on critical containers/components.
- Tests/SLOs: references ASR IDs for key non‑functional tests.

This yields a simple but powerful graph:  
Requirements → ASRs → Design & ADRs → Architecture Views → Validation.  
It aligns directly with IEEE 29148 + 42010 and ADD's ASR‑centric process. [en.wikipedia](https://en.wikipedia.org/wiki/Attribute-driven_design)

***

If you want, a next step could be to turn this into a concrete *"Architecture & Design Documentation Playbook"* for your org: a short internal standard (e.g., 8–12 pages) that fixes templates (design doc, ADR, C4 conventions, API workflow) and gives your teams a repeatable, low‑friction way to hit this Level 3 consistently.

---

## Additional Research & Evidence

*Supplementary research and evidence from a second research pass.*

# Creating architecture and design specification documents for a greenfield software project

## The "level 3" specification boundary and the minimum viable document set

In a greenfield project, the architecture/design specification layer is where the work crosses from *what the system must do* into *how the system will be structured to do it*: major decomposition choices, technology selection, interface contracts, deployment topology, critical data flows, and the rationale and trade-offs behind these decisions. This layer is most effective when treated as a **set of complementary, versionable artefacts**, not one monolithic document: a primary design document for a coherent proposal and review, a decision log for irreversible or high-cost calls, and a small set of diagrams and interface schemas that let others implement and operate the system without needing the original authors in the room. turn21view0

A pragmatic "minimum viable" set for most service-centric greenfield systems is:

- **Primary Design Document (human-readable)**: problem framing, constraints, core structure, key flows, risks, and alternatives. Google's published documentation culture guidance strongly emphasises keeping a small set of fresh docs and updating docs with code; it explicitly frames design docs as a place to collect feedback and then serve as an archive of decisions, rather than being kept as a perpetually-correct reference manual. turn22view0  
- **Architecture Decision Records (ADRs) (human-readable, small)**: one decision per record; immutable timeline; stored beside code. turn15view2  
- **Visual architecture model(s)**: typically one System Context and one Container diagram (C4 level 1–2) plus a small number of dynamic/sequence diagrams for critical flows. C4 explicitly defines this as a hierarchical set of diagrams and encourages supporting dynamic and deployment diagrams when needed. turn1search1  
- **Machine-readable interface specifications** (when the system is API-/service-centric): OpenAPI for HTTP APIs; AsyncAPI for event-driven contracts; GraphQL SDL for GraphQL; `.proto` for gRPC/Protobuf. These are explicitly described as "contracts" by the relevant standards and documentation. turn18search6turn18search1  

The rest of this report compares the most common formats and proposes an evidence-based, "just enough" workflow for greenfield projects.

## Comparative analysis of document formats and when to use each

The formats below are not mutually exclusive; in practice, teams often combine (a) a "proposal" doc (design doc/RFC/six-pager), (b) an architecture description template (arc42/4+1-inspired), and (c) ADRs for durable rationale. C4 diagrams and interface schemas then act as the "shared language" between these artefacts. turn15view6

| Approach | Structure (high-level) | Intended audience | Typical length | Evidence and effectiveness signals |
|---|---|---|---|---|
| "Google-style" design doc (widely adopted outside Google) | Context/scope, goals & non-goals, proposed design, alternatives considered, cross-cutting concerns (e.g., security/privacy/observability), lifecycle/review notes | Engineers + reviewers across teams; also future maintainers | A commonly cited sweet spot is ~10–20 pages for "larger" work, and 1–3 pages for a mini design doc; the decision to write one hinges on ambiguity and meaningful trade-offs | A widely circulated ex-Google account highlights "Alternatives considered" and cross-cutting concerns as central value, and provides the (10–20 / 1–3) size guidance.  Separately, Google's published documentation guidance cautions that design docs should become archives of decisions once code exists, not half-correct live docs. turn22view0 |
| Uber-style RFC process (engineering RFCs) | Short summary → motivation/problem → proposal → drawbacks/risks → detailed design/implementation; reviewed asynchronously; may include explicit approvers and tiering | Engineers across teams; stakeholders impacted by interfaces/platform constraints | Highly variable; typically "proportionate to complexity" rather than fixed | A detailed practitioner account notes that using RFCs early helped scale knowledge and reduce silos as the organisation grew, but also created noise at scale, leading to segmentation and tiering. turn3search0 Increment's description of RFC templates aligns with this: summary, motivation, drawbacks, and design/implementation details.  |
| Amazon six-page narrative ("six-pager") | Dense narrative, read in-meeting; strict page limit with appendices; optimised for shared understanding and decision quality | Decision-makers + cross-functional participants; can be adapted for system/architecture proposals | Max six pages + appendices | AWS's published guidance states a narrative is limited to six pages (appendices allowed), explicitly to force clarity.  Reporting on Amazon's "reading culture" describes the six-page memo as a standard internal decision artefact (context varies), reinforcing the organisational mechanism (read together, then discuss).  |
| arc42 template | 12 sections spanning goals, constraints, context, solution strategy, building block view, runtime view, deployment view, cross-cutting concepts, decisions, quality requirements, risks, glossary | Broad: architects, engineers, ops, security, plus external stakeholders; supports systematic coverage | Scales from "thin" to comprehensive; sections are selectively filled | The official arc42 overview makes explicit that it covers both structural views and quality requirements and includes a dedicated "architectural decisions" section. turn1search13 |
| ADRs (decision log) | One decision per record; minimally: title, context, decision, status, consequences; sometimes added sections for options/links/tags | Primarily engineers and future maintainers; also reviewers who need rationale and history | Usually 1–2 pages equivalent; intentionally small | Primary ADR articulation: one record per significant decision; consequences become context for later decisions.  A practical guideline emphasises storing ADRs in the repository, keeping them short, and superseding via a new ADR rather than rewriting history.  Empirical action research reports improved cooperation and that storage location strongly affects perceived usefulness; ADRs helped with culture/knowledge transfer challenges, while distributed-system documentation challenges remained harder. turn11view2 |

### Recommendations by project type and team size (synthesis grounded in the evidence above)

For **1–5 engineers, single service or small product**: adopt a mini design doc (1–3 pages) plus a small ADR log for irreversible choices; keep diagrams at C4 level 1–2; put OpenAPI/AsyncAPI/SDL/`.proto` in-repo if interfaces exist. This aligns with the "mini doc" guidance and the idea that the value of a design doc is in ambiguity/trade-offs, not as an implementation manual. turn21view0

For **6–20 engineers, multiple services, meaningful cross-cutting concerns**: use a fuller design doc (often nearer the 10–20 page range) for major initiatives, and institutionalise ADRs as the durable decision history. Add C4 dynamic and deployment diagrams as soon as runtime behaviour and deployment constraints become architecturally significant. turn15view6turn15view0

For **20+ engineers or multi-team platforms**: adopt an RFC process (explicit approvers, tiering, discoverable storage) to manage organisational scale, and consider arc42 as the long-lived architecture description "spine" with ADRs as the decision ledger and C4 as the diagramming standard. This recommendation matches documented scaling patterns (noise → segmentation/tiering) and arc42's explicit coverage of views and quality scenarios. turn15view5turn15view7

A key research caveat is that rigorous evidence suggests **document format alone may not drive comprehension outcomes**: a controlled study with 65 participants found no significant association between narrative vs structured architecture documentation format and performance on architecture understanding tasks; prior exposure to source code was the dominant factor. Format still matters for process and governance, but teams should prioritise *appropriate content, discoverability, and integration with code workflows* over template purity. turn13view1

## Architecture Decision Records in depth: templates, lifecycle, and empirical impact

### What ADRs are and why teams use them

An ADR is a compact record of **one significant decision** for a specific project, capturing what was decided and why, with explicit consequences; later ADRs often treat earlier consequences as context, forming a readable chain of rationale over time. turn15view1

ADRs are widely promoted as a remedy to the recurring organisational problem, "Why did we do this?", especially when teams change and memory decays. Google's documentation literature explicitly calls out "Why were these design decisions made?" as a key question that good documentation should answer, and ADRs are designed precisely for that durability. turn15view0

### Canonical structure and evolved variants

The minimal ADR structure is commonly expressed as:

- **Context** (drivers and constraints)  
- **Decision** (what you chose)  
- **Status** (proposed/accepted/deprecated/superseded)  
- **Consequences** (positive/negative/neutral effects, follow-on work)  

This structure is consistent across Nygard's influential formulation and later "keep it in repo" practitioner guidance. turn15view2

Major evolutions relevant to practice:

- **MADR (Markdown Architectural Decision Records)**: positioned as a streamlined template for recording architecturally significant decisions in a structured way, grounded in the ADR/AKM terminology.   
- **Y-statements**: a compressed "In the context of…, facing…, we decided…, to achieve…, accepting…" form; the associated academic work explains how Y-statements and ADRs align with lean/agile documentation goals and describes the rationale for keeping decisions near developer tooling. turn10view2  
- **"Alexandrian pattern" style**: often used to emphasise forces and trade-offs; commonly catalogued in practitioner collections (useful when decisions resemble repeatable patterns).   

### Where ADRs should live and how they become an "immutable timeline"

Two consistent recommendations appear across practitioner and tooling ecosystems:

1. **Store ADRs in the version-controlled repository**, near the code, so they are discoverable during development and maintenance. turn22view0  
2. **Do not rewrite old decisions** when a decision changes. Mark the old ADR as deprecated/superseded and add a new ADR that links back. This preserves a time-ordered decision history. turn15view0  

A common convention is `docs/adr/` (or similar) with sequential numbering and a short slug. While conventions vary by tool, the "keep decisions within repositories" guidance and tool ecosystems strongly support this workflow. turn15view3

### Empirical evidence on ADR impact and limitations

Empirical evidence is still emerging, but one action research study in a microservices context reports that introducing ADRs helped address challenges related to documentation culture and knowledge transfer; it also reports improved cooperation among teams after ADR introduction and highlights that where documentation is stored has a "massive influence" on perceived usefulness. It simultaneously concludes that some challenges in distributed development require more than ADRs alone. turn11view2

This aligns with a broader finding in design rationale research: rationale documentation can improve effectiveness and efficiency (including for change impact reasoning), but "full" rationale capture is typically too costly for systematic industrial use; the practical path is to capture the *minimum rationale needed to support future change and review*. turn16view9

### Recommended ADR template and lifecycle management approach

Below is a practical template that stays close to the canonical form while explicitly supporting "Alternatives considered" (a recurrent need in both design-doc and ADR practice). It is intentionally compatible with MADR-like Markdown workflows. turn15view4turn16view3

```md
# ADR 0007: <decision title>

Date: YYYY-MM-DD
Status: proposed | accepted | deprecated | superseded
Deciders: <names/roles>
Context links: SRS-ASR-003, SRS-CONSTR-002, DesignDoc §4.2, Incident-2026-01-17 (optional)

## Context
What problem are we solving? What constraints and quality attributes matter?
What options are viable given the current system boundary?

## Decision
We will <chosen option>. This decision is binding for <scope>.

## Alternatives considered
A) <option> — why rejected
B) <option> — why rejected
(Only list credible alternatives someone might reasonably ask about later.)

## Consequences
Positive:
- ...
Negative / trade-offs:
- ...
Follow-up work:
- ...
```

Lifecycle rules (lightweight governance):

- **Create ADRs at the point of commitment**, not at the start of exploration: use the design doc/RFC to explore, then publish an ADR once the team converges. This matches the separation between "proposal" artefacts and "decision log" artefacts found in common practice. turn15view0  
- **Link ADRs to the drivers they satisfy** (quality attribute scenarios, constraints, key requirements). This is consistent with the definition that architectural decisions address significant requirements and with SEI's ASR-driven approach. turn16view9  
- **Supersede, don't edit**: new ADR references the superseded one; old ADR status becomes "superseded by ADR-00xx". turn15view0  

## Visual architecture documentation: C4, UML, 4+1, and diagrams-as-code

### C4 model essentials and how it pairs with prose and ADRs

The C4 model defines a set of **hierarchical abstractions and diagrams**: software system → containers → components → code, plus supporting diagrams such as dynamic and deployment. It is explicitly tooling- and notation-independent. turn1search1

In greenfield projects, the most common "just enough" C4 progression is:

- **System Context (Level 1)**: establishes boundary, users, and external systems; reduces early ambiguity about what is "in scope". turn15view5  
- **Container (Level 2)**: defines runtime units (services, web apps, databases, queues) and the main communication paths; often the single most valuable diagram for onboarding and risk review. turn1search1  
- **Component (Level 3)** (selectively): used for complex containers (e.g., a rules engine, stream processor, auth service) where internal structure is non-obvious. turn1search1  
- **Code (Level 4)**: often optional; C4 expects you to rely on code, IDE views, or more detailed notations where necessary. turn1search1  

C4 works best when each diagram is paired with short prose answering: what is shown, what is deliberately not shown, and what key risks/assumptions the diagram encodes. ADRs then capture why particular structural choices were made (e.g., why synchronous HTTP was chosen over events for a specific boundary; why a given datastore was selected). turn15view6


### UML's role today: useful subsets, and evidence on how practitioners actually use it

UML remains useful when used selectively for specific questions (runtime interactions, deployments, component dependencies). Industry evidence suggests UML is frequently not used in a full formal way: in interviews with 50 professional software engineers across 50 companies, five patterns were identified, including "No UML" (35/50) and "Selective" informal usage (11/50), with UML often treated as a short-lived "thought tool" or discussion aid rather than a maintained blueprint. turn16view1turn16view1

For greenfield architecture specs, the UML diagram types that tend to provide the highest signal-to-effort ratio are:

- **Sequence diagrams** for critical request flows, sagas, and failure handling (timeouts, retries, compensations). turn13view2  
- **Component diagrams** for package/service/module dependencies when a C4 component diagram is too informal or when explicit provided/required interfaces add clarity. turn12search8  
- **Deployment diagrams** for multi-environment topology and network boundaries (especially when NFRs like latency, data residency, or reliability drive design). turn5search12  

Empirical research also supports the idea that *how* diagrams are presented affects comprehension: studies on UML comprehension investigate factors like level of detail and layout, reflecting that diagram readability and appropriate abstraction are not optional if diagrams are meant to communicate effectively. turn1search31

### 4+1 view model as a "coverage checklist" for stakeholder concerns

The 4+1 model describes architecture through multiple concurrent views (logical, development, process, physical) plus scenarios, explicitly addressing different stakeholder concerns. It remains valuable as a mental model for ensuring your C4 set (structure) is complemented with runtime and deployment views and validated by scenarios. turn1search18

### Diagrams-as-code and models-as-code: tool recommendations

For long-lived documentation, "diagrams as code" reduces diagram drift by placing diagram sources under version control and enabling review alongside code changes.

- **Structurizr** is explicitly designed for the C4 model and supports a "models as code" approach (DSL renders multiple diagrams). turn12search9  
- **Mermaid** renders Markdown-like text definitions into diagrams and is integrated into platforms like GitHub, making it effective for lightweight, in-repo diagrams. turn12search10  
- **PlantUML** supports many UML diagram types via textual definitions; it is a common choice where teams want UML-like precision in a code-reviewable form. turn12search17  
- The C4 ecosystem itself curates tool categories (text-based modelling, text-based diagramming, visual tools), reinforcing that tool choice should track your expected documentation lifespan and governance needs. turn15view6  

## Specifying API and interface contracts: OpenAPI, AsyncAPI, GraphQL SDL, and Protobuf/gRPC

### Contracts as first-class architecture artefacts

For service-centric systems, machine-readable specs are not "documentation after the fact"; they are themselves **architecture constraints** because they define coupling points. The OpenAPI Specification is explicitly a language-agnostic interface description that enables both humans and tools to understand a service without needing source code. turn9search6  
Similarly, an AsyncAPI document is described as a "communication contract" between senders and receivers in an event-driven system.   
GraphQL explicitly defines an IDL to describe a service's type system, supporting tooling such as code generation or bootstrapping. turn18search3  
gRPC is based on defining a service interface of remotely callable methods, using Protocol Buffers as the default IDL for service and message structure. turn18search1  

### Evidence for design-first (spec-first/contract-first) vs code-first

High-quality empirical evidence specifically comparing design-first vs code-first in modern OpenAPI/AsyncAPI practice is limited, but there are meaningful signals:

- An empirical thesis study comparing API-first vs code-first found participants perceived the API-first specification as more user-friendly and easier to test and navigate, and observed that code-first required more support in testing phases, contributing to confusion and lower precision relative to requirements.   
- Industry experience reports describe measurable benefits from spec-first adoption: for example, Atlassian engineering reports that moving to spec-first API design produced benefits including reduced development time and tighter feedback loops (internal case evidence, not a controlled experiment).   
- Academic work on REST API design and specification practices notes that machine-checkable specifications enable tooling to detect incompatible changes and generate examples/documentation, directly supporting the core claim of contract-first approaches: earlier detection of integration problems and safer evolution.   

A pragmatic interpretation consistent with the evidence is: **design-first helps most when parallel work and compatibility risks dominate**, such as multi-team development, external consumers, mobile/web client splits, or event-driven ecosystems. Where a single team iterates rapidly and the interface is still volatile, design-first may still be valuable, but should be scoped (e.g., design the "spine" endpoints/events first, not every optional field). turn9search8

### How machine-readable specs complement the prose design doc

A robust architecture spec treats the prose design document as the place for: rationale, trade-offs, threat modelling, cross-cutting concerns, and "why this and not that". Google's documentation guidance implicitly supports this separation by positioning design docs as archives of decisions, while method/class docstrings and similar reference docs act as behavioural contracts. Machine-readable API specs operationalise that "contract" idea with tooling support. turn22view0turn18search6

Concrete (illustrative) examples:

**OpenAPI (REST)**
```yaml
openapi: 3.1.0
info: { title: Payments API, version: 1.0.0 }
paths:
  /payments:
    post:
      operationId: createPayment
      responses:
        "201": { description: Created }
```

**AsyncAPI (event contract)**
```yaml
asyncapi: 3.0.0
info: { title: Payments Events, version: 1.0.0 }
channels:
  payments.created:
    address: payments.created
    messages:
      PaymentCreated:
        payload:
          type: object
```

**GraphQL SDL**
```graphql
type Payment { id: ID!, amount: Int! }
type Mutation { createPayment(amount: Int!): Payment! }
```

**Protobuf / gRPC**
```proto
syntax = "proto3";
service Payments { rpc CreatePayment(CreatePaymentRequest) returns (Payment) {} }
message CreatePaymentRequest { int64 amount = 1; }
message Payment { string id = 1; int64 amount = 2; }
```

These snippets are intentionally minimal; in real systems, the architectural value comes from consistent error models, versioning strategy, idempotency, message evolution rules, and security schemes—topics that belong in the design doc and corresponding ADRs, while the schema files become the executable contract surface. turn15view0turn18search6

## Traceability from SRS to architecture spec: ASRs, ADD, and IEEE architecture description

### Why traceability matters most for non-functional requirements and constraints

Architectural decisions are frequently driven less by individual functional requirements than by **quality attributes and constraints** (latency budgets, availability targets, compliance boundaries, cost ceilings, operational constraints). SEI's Attribute-Driven Design (ADD) explicitly frames architecture design as being based on **architecturally significant requirements (ASRs)**, including functional requirements, quality attribute requirements, and constraints, and describes an iterative decomposition process guided by these ASRs. turn16view9

Research on ASRs supports the need to distinguish which requirements truly shape architecture: indicators of architectural significance include wide impact, targeting tradeoffs, strictness, assumption breaking, and technical difficulty; heuristic characteristics include quality attributes, core features, constraints, and application environment. turn20view1

### IEEE/ISO standards perspective: architecture descriptions (42010) and requirements engineering (29148)

ISO/IEC/IEEE 42010 defines architecture description in terms of stakeholders, concerns, and viewpoints, making "concerns" (including quality attributes, constraints, assumptions, and risks) first-class drivers for what an architecture description must cover. turn5search9  
ISO/IEC/IEEE 29148 provides a unified treatment of requirements engineering processes and products across the lifecycle, including guidance for requirements specification. 

Practically, the bridge between these standards in a greenfield project is: **requirements are captured and validated in the SRS (29148-style), then distilled into ASRs and stakeholder concerns, and then architecture views/decisions (42010-style) are produced explicitly to address those concerns**. turn5search12

### A practical traceability model for greenfield projects (actionable synthesis)

A workable traceability model is lightweight if you constrain it to *architecturally significant items*:

```
SRS (FRs, NFRs, constraints)
  └─ ASR catalogue (quality attribute scenarios + hard constraints)
       ├─ Design Doc sections (context, goals, architecture, alternatives, cross-cutting)
       ├─ ADRs (each ADR references ASR IDs it satisfies/trades off)
       ├─ C4 diagrams (views that express the decision's structural impact)
       └─ Interface specs (OpenAPI/AsyncAPI/SDL/Proto) with links back to ADR IDs
```

Implementation detail that makes this real in day-to-day engineering:

- Give each ASR a stable identifier (e.g., `ASR-PERF-001`, `ASR-SEC-003`, `CONSTR-REG-002`).  
- Require every ADR to list the ASR IDs it is primarily addressing (and any it harms).  
- Put ADR IDs into interface specs via comments/links (or in generated documentation sites), so contract changes can be traced to decision rationale.  
- When a decision is reversed, supersede the ADR and reference the new ADR from the old one (preserving the timeline). turn15view0turn20view0  

This model aligns with: (a) ADD's ASR-driven method, (b) ADR practice as an evolving chain of context→decision→consequences, and (c) the viewpoint/concern framing of architecture description. turn15view0

## Deciding what is "just enough": agile evolution, trade-offs, and failure modes

### Agile/iterative reality: architecture evolves, but some decisions are expensive to reverse

Two ideas consistently recur across agile architecture practice:

- **Delay irreversible decisions** to the "last responsible moment", meaning the latest point at which deferring would remove a valuable option; this idea is widely attributed to lean software development thinking and is commonly used to argue against premature commitment. turn6search30  
- **Build an architectural runway**: even frameworks that emphasise emergence argue for balancing emergent design with intentional architecture to avoid waste at scale; the "architectural runway" definition explicitly frames a foundation of code/components/infrastructure needed to deliver near-term features without excessive redesign. turn7search9  

In evolutionary architecture, the key mechanism for keeping "just enough" architecture intact over time is defining measurable constraints ("fitness functions") that act as automated guardrails; this concept is described as providing objective integrity assessment of architectural characteristics and can be operationalised via tests, metrics, monitoring, and pipeline checks. turn7search10

### How to document trade-offs so they don't rot

Trade-offs and rejected alternatives are often the first knowledge to disappear because they are not directly visible in code. A design rationale technical report synthesising evidence and experiments explains that design rationale documentation can support activities such as architectural review and change impact analysis and reports experimental findings indicating improved effectiveness/efficiency when rationale documentation is available under change. turn16view8  
Consistent with that, the Google-style design doc guidance makes "Alternatives considered" one of the most important sections precisely because it answers future readers' "why not X?" questions and forces explicit trade-off reasoning at the time decisions are made. 

A practical rule that follows directly from this evidence: **every major decision must record at least (a) the primary driver(s), (b) 2–3 credible alternatives, and (c) the main downside you are accepting**—either in the design doc's "Alternatives considered" or in the ADR's "Alternatives considered". turn16view5

### Failure modes: absent vs excessive documentation

When documentation is **absent**, teams risk "accidental architecture": the system's structure emerges from local optimisations and short-term fixes without explicit, shared intent, making later reasoning and change harder. While the term is often discussed in practitioner literature, the underlying risk is consistent with empirical findings that lack of architectural knowledge impedes analysis and review, and with action research findings that missing decision documentation creates onboarding and knowledge-transfer burdens. turn16view4

When documentation is **excessive**, teams risk "architecture astronaut" behaviour: elaborate abstraction and speculative design work that is disconnected from immediate product problems. The original essay critique explicitly targets over-abstract, non-problem-solving architecture work as a failure mode. turn6search4  
Design rationale research also cautions that "full" rationale documentation is often too onerous for systematic industrial use, reinforcing that cost matters and over-documentation can fail by non-adoption. turn15view2

### A contextual framework for "just enough" architecture documentation (decision rubric)

Given the evidence that format alone may not improve comprehension and that cost/benefit drives adoption, a "just enough" rubric should be based on *risk, coupling, and reversibility* rather than team preference for templates. turn16view9

Document more (design doc depth + ADR frequency + diagrams + formal contracts) when:

- **Decisions are hard to reverse** (data model choices, external API shapes, event schemas, authn/z model, tenancy boundaries). turn18search6  
- **Multiple teams or external consumers depend on the interface** (contract stability becomes a first-order risk). turn10view3  
- **ASRs are strict or trade-off heavy** (latency/availability/compliance constraints that shape topology and runtime strategies). turn16view9  

Document less (but still record key decisions) when:

- The change is local, low-coupling, and easily reversible, and there is little ambiguity or meaningful alternatives. turn15view2  

Operationally, this means: start a greenfield project with a **thin but complete** set (context + container diagram + initial contracts + 3–10 ADRs for foundational calls), then expand documentation only where ASRs, coupling, or reversibility demands it—keeping everything in the development workflow so updates occur with code changes. turn22view0turn15view2
