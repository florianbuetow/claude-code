# WTG2 DSL Reference (wardleyToGo)

This is the complete syntax and semantics for the **WTG2** Wardley-mapping DSL. Output must be a
valid `.wtg2` file that `wtg2svg` can parse and render to SVG. Read this before writing a map.

---

## What is a Wardley Map?

A Wardley Map visualizes a **value chain** (vertical axis) against the **evolution** of each
component (horizontal axis).

- **Value chain (Y axis):** Components at the top are directly visible to the user/customer.
  Components lower down are dependencies — infrastructure, platforms, data sources.
- **Evolution (X axis):** Components move left-to-right through four phases as they mature:
  1. **Genesis** (I) — Novel, poorly understood, high uncertainty
  2. **Custom-built** (II) — Understood but bespoke, requires expertise
  3. **Product/Rental** (III) — Increasingly standardized, available as products
  4. **Commodity/Utility** (IV) — Highly standardized, pay-per-use, invisible

Key principles:
- **Anchors** represent users or actors — they sit at the top of the value chain, rendered with a
  person icon. They have a position on the evolution axis to control horizontal placement.
- **Components** are connected by dependency edges forming the value chain:
  `User -> Application -> Database -> Compute`.
- Position a component on the evolution axis based on its maturity, not where you *want* it to be.
- Common infrastructure (cloud, networking, power) belongs in phase IV. Novel R&D belongs in phase I.

---

## Document Structure

A WTG2 document follows this canonical order (all sections optional; comments anywhere):

```
1. Metadata        (title, date, author, scope, question, doctrine)
2. Configuration   (stages, legend)
3. Nodes           (anchors, components, submaps, pipelines)
4. Value chain     (edges / dependencies)
5. Groups          (visual organization)
6. Annotations     (notes, warnings, signals, gameplays, focus)
```

---

## Syntax Reference

### Comments

```
// Single-line comment
/* Block comment */
```

### Metadata

```
title: My Wardley Map
date: 2026-01-15
author: Strategy Team
scope: B2C mobile platform, European market
question: "Where should we invest to differentiate?"
doctrine: context
```

All metadata fields are optional. The `question` value should be quoted. The `doctrine` field
indicates organizational maturity phase: `hygiene`, `context`, `excellence`, or `evolution`.

### Stage Labels

Override the default evolution axis labels (default `I`, `II`, `III`, `IV`). Exactly four labels:

```
stages: Genesis, Custom, Product, Commodity
```

### Legend

Standalone keyword; renders an auto-generated legend panel to the right of the map:

```
legend
```

### Nodes

Three node kinds:

| Keyword     | Purpose |
|-------------|---------|
| `anchor`    | User or actor — person icon, always at the top. Has an evolution position for horizontal placement. |
| `component` | Regular component (keyword is optional) |
| `submap`    | Encapsulated sub-map shown as a component |

**Shorthand (single line):** `[kind] <name> : <evolution> [(<type>)] [@<visibility>]`

The `component` keyword is optional — a bare name with a position is a component.

```
anchor User
anchor User : III.5
anchor User : II.3 >> III.5
Application : III.5
Database : III.8 (buy)
Infrastructure : IV.3 (buy) @0.2
submap Payment System : III.6
```

**Block (multi-line):**

```
Route Calculation Engine : II.7 {
  type: build
  asset: tech
  color: #3498DB
  cost: "1.2M/year, 12 FTEs"
  note: "Our key differentiator"
}
```

Block config fields: `type` (`build`/`buy`/`outsource`), `asset`
(`tech`/`financial`/`human`/`relational`/`social`), `evolution` (e.g. `II.7 !! >> III.5`), `color`
(`#RRGGBB`/`#RGB`), `visibility` (`0.0` bottom → `1.0` top), `cost` (free text), `note` (quoted).

### Evolution Positioning

Horizontal position uses **roman numerals** with an optional decimal subdivision: `<roman>.<digit>`
where `<roman>` is `I`–`IV` and `<digit>` is `0`–`9`. Each phase spans 25% of the axis; the decimal
subdivides within the phase (0 = start, 9 = end). Without a decimal, the phase center is used.

| Position | Coord | Meaning | Position | Coord | Meaning |
|----------|-------|---------|----------|-------|---------|
| `I.0`  | 0  | Start of Genesis  | `III.0` | 50 | Start of Product   |
| `I.5`  | 12 | Middle of Genesis | `III.5` | 62 | Middle of Product  |
| `I.9`  | 22 | End of Genesis    | `III.9` | 72 | End of Product     |
| `II.0` | 25 | Start of Custom   | `IV.0`  | 75 | Start of Commodity |
| `II.5` | 37 | Middle of Custom  | `IV.5`  | 87 | Middle of Commodity|
| `II.9` | 47 | End of Custom     | `IV.9`  | 97 | End of Commodity   |

### Evolution Movement

```
Component : II.7 >> III.5
```

Renders an arrow from II.7 to III.5.

### Inertia

Mark resistance with `!` (1–3 levels), optionally qualified by kind. Inertia goes between the
current position and the `>>` movement operator:

```
Component : II.7 ! >> III.5               // moderate inertia
Component : II.7 !! >> III.5              // strong inertia
Component : II.7 !!! >> III.5             // blocking inertia
Component : II.7 !!(tech,human) >> III.5  // qualified: tech + human
Component : II.7 !(financial) >> III.5    // qualified: financial
```

Inertia kinds: `tech`, `financial`, `human`, `relational`, `social`.

### Visibility Override

Vertical position is computed from the dependency graph by default; override with `@` (`0.0` bottom
→ `1.0` top):

```
Component : III.5 @0.9
```

### Edges (Value Chain)

```
A -> B                  // A depends on B
A <-> B                 // bidirectional
A -[label text]-> B     // annotated dependency
A <-[label text]-> B    // annotated bidirectional
```

Edges chain: `User -> App -> API -> Database -> Cloud` creates four edges. Target a pipeline member
with `Component -> Pipeline:Member`.

### Pipelines

Multiple implementations of a component at different evolution stages:

```
pipeline Route Calculation Engine {
  Classic Dijkstra : III.5
  Predictive AI : II.3
  Quantum Algo : I.2
}
```

The pipeline name must match an already-declared component. Members are positioned on the evolution
axis only; vertical position derives from the parent. Pipelines cannot be nested.

### Groups

Purely visual grouping (no scoping). Members must reference existing components:

```
group R&D Team {
  team: explorer
  color: #E74C3C
  Quantum Algo
  Experimental Cache
}
```

Group directives: `color:` (`#RRGGBB`/`#RGB`), `team:`
(`explorer`/`settler`/`town-planner`/`pioneer`/`villager`).

### Annotations, Signals, Gameplays, Focus

```
note "Description text" on Component Name
warning "Risk description" on Component Name

signal accelerating on Component Name      // also: stagnating, declining,
signal co-evolution on Component Name      // co-evolution, red-queen,
signal commoditization on Component Name   // commoditization, network-effects,
                                           // economies-of-scale

gameplay ILC on Platform API
gameplay open-source "Commoditize to capture adjacent value" on Database Engine

focus Recommendation Engine
```

Gameplay types: `ILC`, `open-source`, `land-grab`, `embrace-extend`, `tower-moat`, `FUD`,
`strangler-fig`, `signal-distortion`, `due-diligence`, `two-sided-market`. `focus` highlights a
component and its descendants; everything else dims.

---

## Identifier Rules

Identifiers (component/group names): start with a letter or digit; may contain letters, digits,
`.`, `-`, `'`, `_`, and spaces; cannot be a reserved keyword used alone.

**Reserved keywords:** `anchor`, `component`, `submap`, `pipeline`, `group`, `note`, `warning`,
`signal`, `gameplay`, `legend`, `focus`, `title`, `date`, `author`, `scope`, `question`, `stages`,
`doctrine`, `evolution`, `type`, `asset`, `color`, `visibility`, `cost`, `team`, `build`, `buy`,
`outsource`, `accelerating`, `stagnating`, `declining`, `co-evolution`, `red-queen`,
`commoditization`, `network-effects`, `economies-of-scale`, `ILC`, `open-source`, `land-grab`,
`embrace-extend`, `tower-moat`, `FUD`, `strangler-fig`, `signal-distortion`, `due-diligence`,
`two-sided-market`, `explorer`, `settler`, `town-planner`, `pioneer`, `villager`, `tech`,
`financial`, `human`, `relational`, `social`, `on`, `hygiene`, `context`, `excellence`.

---

## Semantic Rules

1. Every node referenced in an edge, annotation, signal, or pipeline must be declared with a
   position somewhere in the document.
2. Pipeline names must match a declared component.
3. Pipelines cannot be nested.
4. Groups do not create namespaces — components remain global.
5. Anchors do not need an evolution position (placed at top automatically).
6. The dependency graph must be acyclic (no circular dependencies).

---

## Strategic Concepts (for richer maps)

**Climat / Doctrine / Manoeuvre.** Climate = external forces you read but can't control (expressed
as `signal`). Doctrine = universal principles you choose to follow (the `doctrine:` field).
Manoeuvre = deliberate actions to change your position (expressed as `gameplay`). A *manoeuvre*
repositions you on the map; a *tactique* optimizes execution within the current context — only
manoeuvres belong as `gameplay`.

**Gameplays (strategic manoeuvres):**

| Gameplay | Description | Typical context |
|----------|-------------|-----------------|
| `ILC` | Innovate-Leverage-Commoditize: provide base infra, externalize innovation risk to the ecosystem, sense weak success signals, absorb validated innovations. | Platform with ecosystem |
| `open-source` | Commoditize a layer to capture value in an adjacent layer (attack / defense / standardization). | Competitor with proprietary rent |
| `land-grab` | Sacrifice profit for rapid market share to become the de facto standard. | New market, strong network effects |
| `embrace-extend` | Embrace an open standard, extend with proprietary lock-in, extinguish the standard. | Standard you want to control |
| `tower-moat` | Erect barriers (patents, lock-in). Temporary in an evolutionary climate — a harvesting tactic. | Protecting an existing rent |
| `FUD` | Spread fear/uncertainty/doubt to slow a competitor's adoption. Double-edged. | Competitor gaining traction |
| `strangler-fig` | Progressively replace a legacy system component by component (vs Big Bang rewrite). | Legacy system blocking evolution |
| `signal-distortion` | Mislead competitors about strategic intent (e.g. techdrop). | Competitive misdirection |
| `due-diligence` | Map an M&A target's value chain to detect anomalies and real vs paper synergies. | Merger / acquisition |
| `two-sided-market` | Create an obligatory passage point via cross-sided network effects. | Platform connecting producers + consumers |

**Five capitals (`asset`):** `tech` (code, infra, patents), `financial` (revenue models, pricing
power), `human` (expertise, tacit knowledge), `relational` (partnerships, brand, contracts),
`social` (community, regulatory). `build` creates CAPEX (high inertia); `buy`/`outsource` shift to
OPEX (lower inertia).

**Inertia kinds:** `tech` (lock-in, infra debt), `financial` (sunk costs), `human` (skills gap,
identity threat), `relational` (contracts, partner deps), `social` (cultural/regulatory resistance).
Inertia is proportional to past success (mass = past investment × dependencies × identities).

**Climatic signals:** `co-evolution` (tech + practice evolve together), `red-queen` (must evolve to
hold position), `commoditization` (pull toward utility), `network-effects` (value grows with
adoption), `economies-of-scale` (cost advantage from volume).

**EVT/PST team alignment (`team:` in groups):** `explorer`/`pioneer` own Genesis (I);
`settler`/`villager` own Custom–Product (II–III); `town-planner` owns Commodity (IV). A mismatch
between team type and component phase is a strategic signal worth flagging.

**Doctrine violations to flag with `warning`:** NIH (`build` in phase III–IV where market
alternatives exist); no differentiation (everything in III–IV, nothing in I–II); dispersion (many
phase-I bets, no critical mass); strategy theatre (no `question:`, no `gameplay`, no movement).

---

## Complete Example

```wtg2
// Wardley Map — GPS Navigation Platform

title: Navigation Platform — 2026 Strategy
date: 2026-01-15
author: Product Strategy Cell
scope: B2C mobile app, European market
question: "Where to invest to differentiate against incumbents?"
doctrine: context

stages: Genesis, Custom, Product, Commodity
legend

// Anchors
anchor Driver
anchor Local Authority

// Visible layer
Application : III.5
Displayed Route : III.2
Real-Time Traffic Alerts : II.3

// Core engine with qualified inertia and asset/cost
Route Calculation Engine : II.7 !!(tech,human) >> III.5 {
  type: build
  asset: tech
  color: #3498DB
  cost: "1.2M/year, 12 FTEs"
  note: "Key differentiator"
}

// Pipeline: the engine exists in multiple forms
pipeline Route Calculation Engine {
  Classic Dijkstra : III.5
  Predictive AI : II.3
  Quantum Algo : I.2
}

Cartographic Data Model : III.1 (buy)
OSM Data : III.8 (buy)
Cloud Infrastructure : IV.3 (buy) {
  cost: "500k/year, rising 30%"
}
Mobile Network : IV.7 (outsource)

// Value chain
Driver -> Application -> Displayed Route -> Route Calculation Engine
Application -> Real-Time Traffic Alerts
Route Calculation Engine -> Cartographic Data Model -> OSM Data
Route Calculation Engine -> Cloud Infrastructure
Cloud Infrastructure -> Mobile Network
Local Authority -> Real-Time Traffic Alerts

// Groups with team types
group Core Navigation Team {
  team: settler
  Route Calculation Engine
  Cartographic Data Model
}

group Platform Team {
  team: town-planner
  Cloud Infrastructure
}

// Annotations
warning "SPOF — no fallback if unavailable" on Route Calculation Engine
warning "Vendor lock-in, cost rising 30%/year" on Cloud Infrastructure
note "Candidate for outsourcing Q4 2026" on Mobile Network

// Market signals
signal accelerating on Predictive AI
signal commoditization on Cloud Infrastructure
signal red-queen on Application

// Gameplays
gameplay strangler-fig "Replace Classic Dijkstra with Predictive AI" on Route Calculation Engine

// Focus
focus Route Calculation Engine
```

---

## Generation Guidelines

1. **Start with the user need.** Identify the anchor(s) — who is the user/customer?
2. **Build the value chain top-down.** "What does the user need?" then for each component "What does
   *this* need?" until you reach infrastructure.
3. **Position evolution realistically:** I = research/novel; II = built in-house, bespoke; III =
   available as products; IV = utilities (cloud, electricity, internet).
4. **Use `(buy)`/`(outsource)`** for consumed components; leave untyped or `(build)` for in-house.
5. **Mark movement (`>>`)** only for components actively transitioning; add inertia (`!`/`!!`/`!!!`)
   when resistance slows the transition.
6. **Use pipelines** when a component exists in multiple forms at different stages.
7. **Annotate sparingly:** `warning` for risks, `note` for observations, `signal` for market dynamics.
8. **Group by team or domain;** align `team:` types to evolution phases.
9. **Readable identifiers:** natural-language names with spaces, not camelCase.
10. **Follow the canonical section order.**

## Completeness Checklist

- Every anchor has at least one dependency chain to infrastructure.
- Components in Genesis (I) have movement (`>>`) or a signal.
- Inertia is qualified by kind when the nature of resistance is known.
- Groups carrying team types align with component evolution phases.
- At least one `gameplay` if the map is strategic.
- `warning`s exist for SPOF, vendor lock-in, single-supplier risks.
- `cost:` annotations exist for high-budget components.
- The `question:` metadata is defined — a map without a question is strategy theatre.
- At least one component has movement (`>>`) — a static map is not strategic.
- Components marked `build` in phase III–IV are justified (otherwise NIH violation).
