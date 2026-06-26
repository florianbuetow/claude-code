---
name: arc42-framework
description: Generate arc42 architecture documentation from a codebase. Read the repository into a structured evidence base, then author the 12 arc42 sections — emitting Mermaid diagrams where the code gives high-confidence structure, and explicit typed GAP flags where human input is needed, never fabricating. Use when asked to create, scaffold, or update arc42 docs, an architecture document, or per-section architecture views (building block view, runtime view, deployment view, etc.) for a project.
---

Origin: plugin-original

# arc42-framework

This skill is the knowledge base behind the arc42 plugin. It turns a target codebase into arc42
architecture documentation by (1) reading the repo into a fact base and (2) authoring the twelve
arc42 sections from that evidence. It does **not** copy arc42's prose; it routes each generated
claim to recorded evidence, an explicit inference, or a typed GAP flag.

The bundled references under `references/` are the plugin's working knowledge; the generated
output format is fixed by `references/output-conventions.md`.

---

## Recipe overview

1. **Build the evidence base.** Parse manifests, import/dependency graphs, configs, IaC, route
   tables, and naming conventions into fact records (`F-NNN`) with a precise `source` and an
   `extraction_method`. This is the only place facts enter the system.
2. **Author sections in dependency order** (see Waves). Each sub-section pulls from the fact base,
   cites fact ids per claim, and chooses a diagram per `references/diagram-conventions.md`.
3. **Flag, never fabricate.** Where the code cannot answer, emit `GAP:human-input`; where evidence
   should exist but was not found, emit `GAP:no-evidence`. All gaps aggregate into `_gaps.md`.
4. **Lint and check consistency.** Apply `references/lint-checklist.md` (per-section rules) and
   `references/consistency-rules.md` (cross-section invariants) before delivery.

The exact output layout, YAML front-matter, fact-record schema, per-sub-section `arc42-meta`
blocks, per-claim anchors, and typed GAP flags are specified in `references/output-conventions.md`.

---

## Evidence-tier table

Each section is classed by how far the code alone can carry it. The tier sets the default
provenance and confidence, and decides whether a missing answer becomes a Mermaid diagram, a
caveated diagram, or a `GAP:human-input`.

| Tier | Meaning | Default output when evidence is thin | Sections |
|------|---------|--------------------------------------|----------|
| **code-derivable** | Structure is read directly from manifests, import graphs, configs, or route tables (high confidence) | Emit Mermaid directly; `GAP:no-evidence` only if the artifact is genuinely absent | §3 Context, §5 Building Block, §6 Runtime, §7 Deployment, §8 Crosscutting, §12 Glossary |
| **code-inferable** | Reasoned from conventions, naming, or framework patterns (medium confidence) | Emit with an inline "derived from conventions — confirm" caveat | §2 Constraints, §4 Solution Strategy, §9 Architecture Decisions |
| **human-input** | Business, quality, or intent decisions the code cannot reveal | Emit `GAP:human-input` with a specific question | §1 Introduction & Goals, §10 Quality, §11 Risks & Technical Debt |

These tiers are recorded per section in `references/sections/NN-*.md` under `## Evidence tier`.

---

## Generation waves (code-derivable first)

Sections are generated in three waves by the `generate` command. The wave order is
**code-derivable structural sections first → dependent sections → synthesis**, not a strict
topological sort of the `Depends on` edges declared in `references/sections/NN-*.md`.

Cross-section consistency is enforced **post-hoc** by the consistency-checker (Phase C) —
particularly the §3↔§5 interface symmetry (`interfaces-match`). Other `Depends on` edges are
**best-effort cross-references**: a section may be authored before all of its declared upstream
sections exist, and that is expected. Do not assume that all inputs pre-exist when a section
is dispatched.

- **Wave 0 — Evidence base.** Extract fact records from the repo. Precedes all sections.
- **Wave 1 — §3 Context and Scope, §5 Building Block View, §7 Deployment View, §12 Glossary.**
  These four sections are code-derivable (structure readable directly from manifests, import
  graphs, IaC, and route tables). They run first with no prior wave output, in parallel.
- **Wave 2 — §6 Runtime View, §8 Crosscutting Concepts, §4 Solution Strategy,
  §9 Architecture Decisions, §2 Constraints.**
  These five sections receive Wave 1 output as upstream context where available. Because §1 is not
  yet generated, upstream deps that reference §1 are absent and treated as best-effort. All five
  run in parallel.
- **Wave 3 — §1 Introduction and Goals, §10 Quality, §11 Risks and Technical Debt.**
  These synthesis sections are authored last, after the structural and dependent sections are
  complete. §10 and §11 receive Wave 2 output. All three run in parallel.

---

## Why the knowledge base is *derived*, not copied

The `references/` corpus is rewritten from the arc42 material rather than bundled verbatim, for
four reasons:

- **Licensing.** arc42 material is CC BY-SA 4.0. Derived, reworded, attributed references keep the
  plugin's obligations clean and auditable instead of shipping large verbatim excerpts.
- **Portability.** The plugin ships self-contained reference files with no runtime dependency on
  the upstream arc42 site or its asset tree; generation works fully offline.
- **Fitness for agents.** The corpus is restructured into machine-actionable artifacts — a lint
  checklist, cross-section consistency rules, a keyword taxonomy, a diagram-convention map, and an
  expected-topics catalog — which an agent can apply directly, unlike narrative documentation.
- **Augmentation.** Each section spec adds plugin-original evidence-routing (what to look for in a
  repo, which extraction method, which Mermaid type, which GAP to emit) that arc42 itself does not
  provide, because arc42 documents the *template*, not how to derive it from code.

### Corpus Derivation Contract (the bar for future editors)

Every arc42-derived reference file MUST keep sourcing from the crawled corpus snapshot
(`.../crawl-arc42-doc/data/output`), MUST carry a `Source:` line citing the corpus-relative paths
it derives from, MUST be reworded (no verbatim runs from the source), and MUST be accounted for in
`references/COVERAGE.md` (every corpus file maps to a destination or a justified `dropped:`
reason). Plugin-original files (this `SKILL.md`, `output-conventions.md`, `COVERAGE.md`) are marked
`Origin: plugin-original` and need no `Source:`. The gate is
`plugins/arc42/tests/check_corpus_contract.py`; keep it green and keep its `--corpus` pointed at
the corpus root.

---

arc42 is the work of Dr. Gernot Starke and Dr. Peter Hruschka; this knowledge base is derived from
the arc42 framework material, used under CC BY-SA 4.0.
