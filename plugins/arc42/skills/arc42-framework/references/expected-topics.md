Source: index.md, 01-introduction-and-goals/index.md, 02-constraints/index.md, 03-context-and-scope/index.md, 04-solution-strategy/index.md, 05-building-block-view/index.md, 06-runtime-view/index.md, 07-deployment-view/index.md, 08-crosscutting-concepts/index.md, 09-architecture-decisions/index.md, 10-quality/index.md, 11-risks-and-technical-debt/index.md, 12-glossary/index.md

# Expected Topics — arc42 Section Catalog

Canonical subsections and content items per arc42 section, derived from the official template indexes. The phase-2 gap-check diffs discovered content against this catalog.

---

> **Root-index standout keywords** (from index.md): The arc42 tips are tagged with 56 keywords; three are called out explicitly:
> - **lean** — reduce documentation effort pragmatically without losing essential content; suited to agile contexts
> - **thorough** — full rigor required; for large or safety-critical systems subject to audit
> - **essential** — content that should always be present regardless of lean/thorough stance (e.g., quality goals)

---

## §1 Introduction and Goals

| Sub-section | Content to expect |
|-------------|-------------------|
| **1.1 Requirements Overview** | Summary of functional requirements and driving forces; links to external requirements documents; use-case table or short prose |
| **1.2 Quality Goals** | Top three to five quality goals for the architecture (not project goals); priority-ordered table with concrete scenarios; cross-reference to §10 |
| **1.3 Stakeholders** | Roster of all parties who need to know, influence, or work with the architecture; table of role/name, contact, and expectations |

---

## §2 Architecture Constraints

| Topic | Content to expect |
|-------|-------------------|
| **Technical constraints** | Technology or platform choices imposed from outside the team |
| **Organizational / political constraints** | Process rules, governance mandates, third-party dependencies |
| **Conventions** | Coding standards, versioning rules, documentation or naming conventions |

All items in a constraint table with explanations. Negotiability of each constraint may be noted.

---

## §3 Context and Scope

| Sub-section | Content to expect |
|-------------|-------------------|
| **3.1 Business Context** | All external communication partners (users, neighboring systems); domain-specific inputs and outputs; optional table of partner / input / output per channel |
| **3.2 Technical Context** | Technical channels and transmission media linking the system to its surroundings; mapping of domain I/O to those channels; optional protocol details |

Both sub-sections may include diagrams (see `diagram-conventions.md`) and/or partner tables.

---

## §4 Solution Strategy

| Topic | Content to expect |
|-------|-------------------|
| **Technology decisions** | Chosen tech stack and rationale |
| **Top-level decomposition** | Architectural or design patterns selected (e.g., layered, hexagonal, event-driven) |
| **Quality-achievement decisions** | How key quality goals are addressed by the strategy |
| **Organizational decisions** | Build-vs-buy, outsourcing, team structure choices |

Short entries; each links to the section (§5, §8) where detail lives.

---

## §5 Building Block View

| Sub-section | Content to expect |
|-------------|-------------------|
| **5.1 Whitebox Overall System (Level 1)** | Overview diagram of the whole system; decomposition rationale; black-box descriptions of top-level building blocks; important interfaces |
| **5.2 Level 2** | Whitebox templates for selected Level-1 blocks that warrant detail; inner structure diagram per block; black-box descriptions of their sub-blocks |
| **5.3 Level 3** | Further zoom into selected Level-2 blocks; same whitebox template pattern; repeated as needed for additional levels |

Each whitebox template includes: overview diagram, decomposition motivation, contained black-box descriptions, and optionally: interface specs and open issues.

---

## §6 Runtime View

| Topic | Content to expect |
|-------|-------------------|
| **Named runtime scenarios (6.1 … 6.n)** | One subsection per architecturally relevant scenario: important use-case flows, critical external-interface interactions, startup/shutdown sequences, error/exception paths |

Each scenario entry: a diagram or numbered step list plus a narrative of notable interaction aspects. Notation choices include sequence diagrams, activity/swimlane diagrams, flow charts, state machines, and BPMN/EPC flows.

---

## §7 Deployment View

| Sub-section | Content to expect |
|-------------|-------------------|
| **7.1 Infrastructure Level 1** | Topology diagram of the full deployment environment; distribution across locations/environments; motivation for the topology; quality/performance characteristics of the infrastructure; mapping of software building blocks to infrastructure elements |
| **7.2 Infrastructure Level 2 (7.2.1 … 7.2.n)** | Internal structure of selected infrastructure elements from Level 1; one entry per element needing detail |

Multiple deployment environments (dev, test, prod) each get their own Level 1 copy.

---

## §8 Crosscutting Concepts

| Topic | Content to expect |
|-------|-------------------|
| **Author-chosen subsections (8.1 … 8.n)** | Only the concepts that actually apply to the system; typical candidates include: domain model, persistence approach, UI patterns, session/state handling, transaction management, error handling, logging, authentication/authorization, security, safety, communication patterns, distribution/scaling, testability |

No fixed list — pick the subset relevant to the system. Each concept entry: prose, code examples, or model excerpts sufficient for consistent implementation across building blocks.

---

## §9 Architecture Decisions

| Topic | Content to expect |
|-------|-------------------|
| **ADR entries (one per decision)** | Each record includes: title, context (forces and tensions), decision taken, current status (proposed/accepted/deprecated/superseded), consequences (positive, negative, neutral) |

May also appear as a flat list or table ordered by importance. Avoids duplicating decisions already in §4; cross-references §4 instead.

---

## §10 Quality Requirements

| Sub-section | Content to expect |
|-------------|-------------------|
| **10.1 Quality Requirements Overview** | High-level summary of quality categories or topics; table or mindmap structure; may reference ISO 25010 / Q42 labels; if entries are specific and measurable, §10.2 may be skipped |
| **10.2 Quality Scenarios** | Concrete, measurable scenarios; short form: context/background, source/stimulus, metric/acceptance criteria; long form (SEI): scenario ID, name, source, stimulus, environment, artifact, response, response measure |

Cross-reference: top-three quality goals are in §1.2; §10 captures the full set including lower-priority requirements.

---

## §11 Risks and Technical Debt

| Topic | Content to expect |
|-------|-------------------|
| **Prioritized risk and debt list** | Each entry: description of the risk or debt item, priority, and proposed mitigation or reduction measure |

Ordered from highest to lowest priority. Serves management and project-stakeholder audiences.

---

## §12 Glossary

| Topic | Content to expect |
|-------|-------------------|
| **Term / definition table** | One row per domain or technical term; columns: Term, Definition; optionally additional columns for translations in multi-language contexts |

Focus on terms where stakeholders might otherwise disagree on meaning or use synonyms/homonyms.
