# Section 8 — Crosscutting Concepts

Source: 08-crosscutting-concepts/index.md

## Intent
Documents solution patterns and design principles that span multiple components rather than belonging to a single building block. Covering them once here prevents duplication and promotes consistent implementation across the system, contributing to the architecture's conceptual integrity.

## Evidence tier
code-derivable

## What to look for in the repo
- Shared infrastructure libraries (logging, tracing, auth, caching, error handling) imported by multiple modules
- Base classes, mixins, or interfaces that enforce a common pattern across components
- Domain-model files defining entities referenced system-wide
- Middleware, interceptors, or aspect-oriented configurations (e.g., logging filters, auth guards, validation pipelines)
- Security policy files, rate-limiting configurations, or standardized error-response schemas
- Common serialization formats or API versioning conventions applied everywhere

## Output template

*<Create one numbered subsection for each concept that genuinely crosses multiple building blocks. Select only the topics relevant to this system — do not attempt to cover every possible concept category.>*

#### 8.1 `<Concept Name>` (e.g., Logging)

*<What this concept covers; which components it applies to; the chosen approach>*

*<Implementation example or configuration snippet where it aids comprehension>*

#### 8.2 `<Concept Name>` (e.g., Authentication)

*<Description>*

*<Implementation example>*

#### 8.n `<Concept Name>`

*<Description>*

## Diagrams
- Mermaid `classDiagram` for shared domain models or base-class hierarchies
- Mermaid `sequenceDiagram` for cross-cutting flows (e.g., token validation, distributed tracing)
- Code blocks or configuration excerpts for implementation-pattern examples

## Lint (this section)
- T08-* (only genuinely cross-cutting topics included; each concept names the building blocks it affects; implementation examples present where the approach is non-obvious)

## Depends on
- §5 (identifies the building blocks that concepts cut across)
- §4 (solution strategy decisions that mandate certain cross-cutting patterns)
