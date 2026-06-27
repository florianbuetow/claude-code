# Section 5 — Building Block View

Source: 05-building-block-view/index.md

## Intent
Shows the static structure of the system as a hierarchy of components — modules, packages, services, classes, or other named units — together with their dependencies. Each level of the hierarchy expands selected black boxes from the level above, trading breadth for detail. This section is mandatory and serves as the architectural floor plan.

## Evidence tier
code-derivable

## What to look for in the repo
- Top-level source directory layout (services, modules, packages, layers)
- Module manifests, build files, or workspace configs that enumerate components
- Import graphs or package-level dependency declarations
- Public interfaces: exported symbols, REST controllers, gRPC service definitions, event producers/consumers
- Per-module README files describing a component's responsibility

## Output template

### 5.1 Whitebox Overall System

Overview of how the entire system is decomposed into top-level components and the rationale for that decomposition.

*<insert Level 1 overview diagram>*

*<brief rationale explaining why the system is structured this way>*

**Component summary (compact form):**

| Component | Responsibility |
|-----------|---------------|
|  |  |

**Component summary (extended form — use when interfaces and locations matter):**

| Component | Responsibility | Key Interfaces | Source Location |
|-----------|---------------|----------------|-----------------|
|  |  |  |  |

**Black box description per component (repeat block for each):**

##### `<ComponentName>`

- Purpose / Responsibility:
- Interfaces:
- Quality characteristics (if notable):
- Source location:
- Fulfilled requirements (optional):
- Open issues (optional):

### 5.2 Level 2

Internal structure of the most architecturally significant Level 1 components. Document only components where the internal breakdown is surprising, risky, complex, or likely to change — skip straightforward ones.

#### 5.2.1 Whitebox `<Component 1>`

*<internal decomposition diagram>*

| Sub-component | Responsibility |
|---------------|---------------|
|  |  |

#### 5.2.2 Whitebox `<Component 2>`

*<internal decomposition diagram>*

### 5.3 Level 3

Further expansion of selected Level 2 sub-components when the added granularity justifies the documentation cost.

#### 5.3.1 Whitebox `<Sub-component x.1>`

*<internal structure diagram and description>*

#### 5.3.2 Whitebox `<Sub-component x.2>`

*<internal structure diagram and description>*

## Diagrams
- Mermaid `graph TD` (component / package hierarchy) for each whitebox level
- C4 Container diagram for Level 1 where a C4 context exists

## Lint (this section)
- T05-* (Level 1 is complete; every component has a stated responsibility; interfaces documented; at least one diagram per level described; components align with §3 boundary)

## Depends on
- §3 (system boundary establishes what is inside; context actors become external boxes at Level 1)
- §4 (strategy decisions drive the decomposition pattern chosen)
