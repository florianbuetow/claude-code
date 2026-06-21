---
name: diagrams:wardley
description: Produce a Wardley map in the WTG2 DSL (wardleyToGo) as a .wtg2 file that renders to SVG via wtg2svg — anchors (user needs), components positioned by value chain (visibility) and evolution (roman numerals I–IV), dependencies, movement, inertia, build/buy/outsource, signals, gameplays, and groups. Use when the user asks for a Wardley map, strategic map, or value-chain map.
disable-model-invocation: false
---

# Diagrams: Wardley Maps (WTG2)

Generate a strategic Wardley map in the **WTG2** domain-specific language (wardleyToGo). Output is a
valid `.wtg2` file that `wtg2svg` parses and renders to SVG.

## ⛔ Read these first (bundled, self-contained)

Before writing any map, read both — they are bundled with this skill, no network needed:

1. **[`references/how-wardley-maps-work.md`](references/how-wardley-maps-work.md)** — the concepts:
   the two axes, the value chain, evolution phases, and how the map drives build/buy/outsource
   decisions. Producing valid DSL without understanding these yields a syntactically correct but
   strategically useless map.
2. **[`references/wtg2-dsl-reference.md`](references/wtg2-dsl-reference.md)** — the complete WTG2
   syntax and semantics: nodes, evolution positioning (`I`–`IV`), movement (`>>`), inertia (`!`),
   edges, pipelines, groups, annotations, signals, gameplays, reserved keywords, and a full example.

Do not skip them.

## Output rules

- Emit the map inside a fenced ` ```wtg2 ` code block (or as a standalone `.wtg2` file when writing
  to disk).
- Follow the canonical section order: metadata → stages/legend → nodes → edges → groups →
  annotations.
- Positions use roman numerals with a decimal: `Component : III.5`. Genesis = `I`, Custom = `II`,
  Product = `III`, Commodity = `IV`.
- Dependencies use `->`. Comments use `//` (or `/* ... */`).
- Every node referenced in an edge/annotation/signal/pipeline must be declared with a position.
- The dependency graph must be acyclic.

## Workflow

1. **Anchor first.** Identify the user/actor(s) and declare them with `anchor`.
2. **Value chain top-down.** "What does the user need?" → for each component, "what does *this*
   need?" — down to infrastructure. Wire with `->`.
3. **Position evolution realistically** (I = novel/research, II = custom/bespoke, III = product, IV
   = commodity/utility). Position on actual maturity, not where you wish it were.
4. **Sourcing:** tag `(buy)`/`(outsource)` for consumed components; `(build)` or untyped for in-house.
5. **Movement & inertia:** add `>>` only for components actively transitioning; add `!`/`!!`/`!!!`
   (optionally qualified, e.g. `!!(tech,human)`) where resistance slows the move.
6. **Annotate sparingly:** `warning` for risks (SPOF, lock-in), `note` for observations, `signal`
   for market dynamics, `gameplay` for deliberate strategic manoeuvres.
7. **Group** by team/domain; align `team:` types to evolution phases.

## Quality check before returning

- Anchor(s) present and at the top; every anchor reaches infrastructure through a dependency chain.
- A `question:` is set (a map without one is strategy theatre) and at least one component moves
  (`>>`) if the map is meant to be strategic.
- `build` in phase III–IV is justified (else it's an NIH violation worth a `warning`).
- All referenced nodes are declared; no cycles; identifiers are readable natural-language names.

## Rendering note

In a Hugo/blog context, a `.wtg2` source file is rendered to an `.svg` of the same basename by
`wtg2svg`, and both files are committed together; the article references the SVG with standard
Markdown image syntax. The skill's job is to produce the valid `.wtg2` source.
