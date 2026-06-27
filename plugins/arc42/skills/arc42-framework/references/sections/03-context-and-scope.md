# Section 3 — Context and Scope

Source: 03-context-and-scope/index.md

## Intent
Draws the boundary of the system under description: what is inside, what lies outside, and what crosses that boundary in either direction. Distinguishes the business-level view of those exchanges (what data means) from the technical-channel view (how it travels). The external interfaces defined here are among the most critical aspects of the architecture.

## Evidence tier
code-derivable

## What to look for in the repo
- API definitions (OpenAPI specs, protobuf files, GraphQL schemas) naming external callers and downstream systems
- Integration test fixtures or mock configurations that reveal which neighboring systems exist
- Environment variables or config files referencing external service URLs, message queues, or third-party databases
- Event-bus topic lists or message-queue configurations that expose publish/subscribe boundaries
- Network or infrastructure diagrams in `docs/` or `architecture/` folders

## Output template

### 3.1 Business Context

All communication partners at the domain level — which actors and external systems exchange information with this system, and what that information means in business terms. Transport details are excluded here.

*<insert context diagram or partner table>*

| Partner | Information Flowing In | Information Flowing Out |
|---------|------------------------|-------------------------|
|  |  |  |

*<optional: narrative explaining domain-specific interface semantics>*

### 3.2 Technical Context

The channels, protocols, and infrastructure links that carry the business flows identified in §3.1, plus a mapping that connects each business exchange to its technical channel.

*<insert deployment or network diagram>*

| Channel / Protocol | Direction | Business Flow Carried |
|--------------------|-----------|----------------------|
|  |  |  |

*<optional: explain interface details that are not obvious from the table>*

## Diagrams
- C4 Context diagram (`graph LR` or `C4Context` Mermaid block) for §3.1
- UML deployment-style diagram or `graph TB` for §3.2

## Lint (this section)
- T03-* (all external actors named; business and technical sub-sections both present; no internal component decomposition introduced here)

## Depends on
- §1 (stakeholders identified there are the communication partners here)
- §2 (constraints may restrict which interfaces or protocols are permitted)
