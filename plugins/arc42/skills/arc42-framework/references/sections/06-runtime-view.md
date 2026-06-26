# Section 6 — Runtime View

Source: 06-runtime-view/index.md

## Intent
Illustrates how the static components from §5 collaborate at runtime: which scenarios they execute together, how they handle errors, and how the system starts or shuts down. Focus is on architecturally significant flows rather than exhaustive coverage — a representative selection beats a comprehensive catalogue.

## Evidence tier
code-derivable

## What to look for in the repo
- Integration and end-to-end test files that trace flows across multiple components
- Message queue consumers/producers revealing publish-subscribe choreography
- Middleware chains, filter pipelines, or interceptor stacks that define request lifecycle
- Application entry points and graceful-termination handlers (startup / shutdown hooks)
- Error-handling middleware, retry logic, or circuit-breaker configurations

## Output template

*<Add one numbered subsection per architecturally relevant runtime scenario. Criteria for inclusion: critical external interface, important use case, error path, or operational lifecycle event.>*

#### 6.1 `<Scenario Name>`

*<sequence diagram or numbered step-by-step description of the component interaction>*

*<explanation of the notable architectural points — why this flow is worth documenting>*

#### 6.2 `<Scenario Name>`

*<diagram or description>*

*<explanation>*

#### 6.n `<Scenario Name>`

*<diagram or description>*

*<explanation>*

## Diagrams
- Mermaid `sequenceDiagram` for request/response flows between components
- Mermaid `stateDiagram-v2` for lifecycle and state-machine scenarios
- Activity diagrams or numbered step lists for batch or workflow scenarios

## Lint (this section)
- T06-* (at least one scenario per critical external interface from §3; error or exception paths represented; participant names match §5 component names)

## Depends on
- §5 (every component named in a scenario must appear in the building block view)
- §3 (external actors from the business context appear as participants in runtime scenarios)
