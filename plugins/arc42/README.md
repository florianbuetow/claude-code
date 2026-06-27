# arc42

Generate [arc42](https://arc42.org) architecture documentation from a codebase.

`12 sections` · `Mermaid diagrams where structure is code-verifiable` · `GAP flags where human input is needed` · `Evidence-grounded (never fabricated)`

Software architecture decisions accumulate in code, configuration, and deployment artifacts — not in stale Word documents. This plugin reads your repository into a structured evidence base, then authors all 12 arc42 sections from that evidence. Where the code gives high-confidence structure (module decomposition, component boundaries, deployment topology), it generates Mermaid diagrams. Where human context is needed (goals, constraints, quality requirements), it emits explicit `<!-- GAP -->` flags rather than fabricating content.

| Command | What it does |
|---------|-------------|
| `/arc42:generate` | Full run: scan repo → evidence base → author all 12 sections → `docs/arc42/` |
| `/arc42:fill-gaps` | Guided walkthrough of all open `<!-- GAP -->` flags — prompts for missing context and fills in each section |
| `/arc42:gap-check` | *(coming in phase 2)* Report all open GAPs across the output without filling them |
| `/arc42:drift-check` | *(coming in phase 2)* Detect drift between the evidence base and output sections (re-scans repo, flags stale sections) |

### How It Works

1. **Evidence sweep** — `evidence-scout` agent reads source files, configs, manifests, and infrastructure code into a structured `_evidence.md` base.
2. **Section authoring** — `section-author` agent writes each of the 12 arc42 sections from evidence only. Claims anchor to source files via `<!-- arc42-meta: T<nn>-<n> -->` comment tags. Content without a source anchor is flagged as `<!-- GAP -->`.
3. **Consistency check** — `consistency-checker` agent verifies cross-section coherence (component names, interfaces, data flows) and reports mismatches.

Output lives in `docs/arc42/`: one file per section (`01-introduction-and-goals.md` through `12-glossary.md`), an index, and an `_evidence.md` base.

### Diagrams

Mermaid diagrams are generated only where the code provides enough structure to be confident — typically the building block view (§5), runtime view (§6), and deployment view (§7). The diagram-conventions reference controls which diagram types are used and when confidence thresholds are met. Sections where structure cannot be inferred from code alone are left as prose with GAP flags.

### arc42 Sections

| § | Section |
|---|---------|
| 1 | Introduction and Goals |
| 2 | Architecture Constraints |
| 3 | System Scope and Context |
| 4 | Solution Strategy |
| 5 | Building Block View |
| 6 | Runtime View |
| 7 | Deployment View |
| 8 | Cross-cutting Concepts |
| 9 | Architecture Decisions |
| 10 | Quality Requirements |
| 11 | Risks and Technical Debt |
| 12 | Glossary |

**Trigger** — Ask Claude to "generate arc42 docs", "document the architecture", "run arc42", or "fill in the arc42 gaps".

---

## License

This plugin is licensed under **CC BY-SA 4.0**. The knowledge base (section templates, expected-topics reference, keyword taxonomy, diagram conventions) is adapted from the [arc42 architecture documentation framework](https://arc42.org) by Peter Hruschka and Gernot Starke, which is also CC BY-SA 4.0.

All other plugins in this marketplace are MIT. See `NOTICE` for the full attribution and the scope of the CC BY-SA 4.0 material.
