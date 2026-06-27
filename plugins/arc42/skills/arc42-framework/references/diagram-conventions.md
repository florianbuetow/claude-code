Source: 01-introduction-and-goals/index.md, 02-constraints/index.md, 03-context-and-scope/index.md, 04-solution-strategy/index.md, 05-building-block-view/index.md, 06-runtime-view/index.md, 07-deployment-view/index.md, 08-crosscutting-concepts/index.md, 09-architecture-decisions/index.md, 10-quality/index.md, 11-risks-and-technical-debt/index.md, 12-glossary/index.md, 06-runtime-view/tips/6-7.md, 06-runtime-view/tips/6-11.md, 07-deployment-view/tips/7-6.md

# Diagram Conventions for arc42 Sections

Maps each arc42 section to the recommended Mermaid diagram type (or labeled placeholder) and defines the confidence rubric used to choose between them.

---

## Confidence Rubric

<!-- Origin: plugin-original -->

Three levels govern what the plugin emits:

| Level | Basis for judgment | Output |
|-------|--------------------|--------|
| **High** | Explicit structural signals available — import/dependency graphs, IaC configs, container manifests, route tables, deployment descriptors | Emit Mermaid directly |
| **Medium** | Structure inferred from directory layout, naming conventions, or framework patterns | Emit Mermaid with an inline caveat: *"Derived from conventions — confirm against actual structure"* |
| **Low** | Signal is absent, ambiguous, or the required diagram type has no Mermaid equivalent | Emit a labeled placeholder block instead of a diagram |

---

## Section-to-Diagram Mapping

| Section | Form type (from index) | Mermaid type | Notes |
|---------|------------------------|--------------|-------|
| §1 Introduction and Goals | Tables and short text | — (no diagram) | All three sub-sections use prose or tables |
| §2 Constraints | Constraint tables | — (no diagram) | Tables only; no spatial structure to visualize |
| §3 Business Context | System-as-black-box diagram; optional partner table | `flowchart LR` | System node at center; external actors/systems as surrounding nodes; data flows as labeled edges |
| §3 Technical Context | Channel/protocol diagram; I/O mapping table | `flowchart LR` | Channels modeled as edges; node labels carry protocol or medium name |
| §4 Solution Strategy | Decision list or table linking quality goals to solutions | — (no diagram) | Prose or table; no diagram expected |
| §5 Building Block View | Hierarchical whitebox/blackbox diagrams across levels | `flowchart TD` + `subgraph` | Each whitebox level wraps its contained blocks in a `subgraph`; dependencies become directed edges |
| §6 Runtime — sequence scenarios | Sequence diagrams (tip 6-11) | `sequenceDiagram` | First choice for request/response and message-passing scenarios; lifelines map to building blocks |
| §6 Runtime — swimlane scenarios | Activity diagrams with swimlanes (tip 6-7) | **Placeholder only** | No Mermaid equivalent for partitioned activity flows; see Placeholder-Only Cases below |
| §7 Deployment View | UML deployment diagrams with stereotyped nodes/artifacts (tip 7-6) | `flowchart LR` + `subgraph` **approximation** — or **Placeholder** | When stereotype fidelity is not required, use nested `subgraph` blocks for environments and nodes; when `<<device>>` / `<<artifact>>` semantics matter, emit placeholder instead |
| §8 Crosscutting Concepts | Free-form — concept papers, code excerpts, model fragments | Depends on sub-concept | Route to `sequenceDiagram` for interaction concepts, `flowchart` for structural ones; default to prose |
| §9 Architecture Decisions | ADR structured text; list or table | — (no diagram) | Decision records are prose; no spatial representation |
| §10 Quality | Table or mindmap; quality attribute tree (Q42 model) | `mindmap` | Root node = "Quality"; branches follow ISO 25010 or Q42 categories; leaves are concrete requirements |
| §11 Risks and Technical Debt | Prioritized list or table | — (no diagram) | Tabular; risk entries include description, priority, and mitigation |
| §12 Glossary | Two-column term/definition table | — (no diagram) | No diagram; optionally multi-column for translations |

---

## Placeholder-Only Cases

Two arc42-required diagram types have no faithful Mermaid representation and **must always** produce a labeled placeholder rather than a misleading approximation:

### 1. UML Deployment Diagrams with Stereotypes (§7)

UML deployment notation relies on stereotypes (`<<device>>`, `<<execution environment>>`, `<<artifact>>`, `<<component>>`) that carry well-defined semantic contracts. A `flowchart` can approximate node topology but drops that semantic layer entirely.

When stereotype fidelity is needed, emit:

```
<!-- arc42 §7 Deployment View: UML deployment diagram with stereotypes
     Placeholder — Mermaid cannot express UML deployment stereotypes.
     Use a dedicated UML tool (e.g., PlantUML, draw.io) to render this diagram. -->
```

### 2. Activity Diagrams with Swimlanes (§6, tip 6-7)

Partitioned activity flows group actions by actor or thread using horizontal or vertical swimlanes. PlantUML supports vertical swimlanes; Mermaid does not support swimlanes at all.

When a swimlane-partitioned flow is required, emit:

```
<!-- arc42 §6 Runtime View: Activity diagram with swimlanes
     Placeholder — Mermaid has no swimlane construct.
     Use PlantUML or a dedicated activity-diagram tool to render this. -->
```
