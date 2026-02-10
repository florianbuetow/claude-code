# Single Responsibility — System Level

> "A module should be responsible to one, and only one, actor." — Robert C. Martin

## Core Idea

At the architecture scale, Single Responsibility Principle means each module, service, or bounded context owns one coherent business capability and has one primary reason to change. Azure's microservices architecture guidance states: "each service implements a single business capability within a bounded context." When this principle reaches its logical endpoint, you get a microservices architecture where each service is independently deployable and owned by a single team.

Even in a monolith, each module should have a crisp, memorable purpose. If you need multiple paragraphs to describe what a module does, you likely need more than one module. The principle applies at multiple scales: functions should have one job, classes should have one reason to change, modules should own one coherent business capability, and services should implement one business domain.

## Violation Patterns

### 1. God Service / Kitchen-Sink Module

**Heuristic:** A service or module responsible for user management, billing, notifications, and reporting all at once. Its API surface and codebase grow without coherent focus.

**Look for:**
- A single service exposing 10+ unrelated API endpoints spanning multiple business domains
- Multiple teams or squads coordinating changes to the same service
- Service backlog mixing unrelated business initiatives from different stakeholders
- The component is a universal dependency; many unrelated features import from it

**Refactoring/Remedy:**
Identify "mini domains" or business slices inside the overgrown service. Extract along those seams using the Strangler Fig pattern to gradually migrate functionality. Apply Domain-Driven Design strategic design (bounded context mapping, context mapping) to find natural business boundaries.

### 2. Distributed Monolith / Lock-Step Deployment

**Heuristic:** Multiple services that must be deployed together despite being technically separate components.

**Look for:**
- Changes to one service routinely require synchronized changes in others
- Services share databases or database schemas across application boundaries
- Deploying a single user-profile change requires redeploying 10 unrelated backend services
- Lock-step deployment is normal practice rather than an exceptional circumstance

**Refactoring/Remedy:**
Redraw service boundaries so each can be deployed independently. Each service should own its own data store and database schema. Use asynchronous communication (events, queues) to decouple deployments. Validate boundaries by asking: "Can I deploy this service alone without coordinating with others?"

### 3. Bounded Context Drift

**Heuristic:** A context (e.g., "Orders") starts handling inventory, shipping, and payments because it was "convenient", creating unintended coupling across domains.

**Look for:**
- A module that changes for many unrelated reasons (product pricing logic, regulatory updates, UI redesign, logging policies all modify the same module)
- High commit activity in a single module spanning multiple distinct business domains
- Modules with unclear or expansive purpose; descriptions use "and", "or", "also" repeatedly

**Refactoring/Remedy:**
Perform a "reasons to change" analysis for each module. Document what changes would trigger changes to that module. Align boundaries with business capabilities using DDD strategic design. Involve domain experts to validate that boundaries match business reality.

### 4. Gateway/Orchestrator Accumulating Domain Knowledge

**Heuristic:** API gateways or orchestration layers accumulate domain logic that belongs in the services themselves.

**Look for:**
- Gateway code containing business validation, transformation logic, or domain-specific routing beyond simple proxying
- The gateway becomes a coupling bottleneck that must change whenever any downstream service changes
- Business rules encoded in gateway configuration or routing logic rather than in service code

**Refactoring/Remedy:**
Keep domain knowledge out of the gateway. Push domain logic into the services that own the bounded context. The gateway should handle only cross-cutting concerns like authentication, rate-limiting, and protocol translation. Maintain a clean separation between infrastructure orchestration and domain logic.

### 5. Chatty Service Communication

**Heuristic:** Two services require excessive synchronous communication to implement a single user-visible capability.

**Look for:**
- Distributed traces showing 5+ synchronous calls between two services for one user action
- High inter-service call volume for what should be simple operations
- Services that are effectively parts of the same responsibility split too early
- Average latency increases significantly because of sequential inter-service calls

**Refactoring/Remedy:**
If two services are chatty, their functionality may belong in the same service. Azure's guidance: "chatty calls are a symptom that functions might belong in the same service." Prefer starting with coarser-grained services; splitting a service is easier than merging functionality across multiple services. Use asynchronous events or sagas for truly distributed operations.

## System-Scale Notes

- **Monolith:** SRP applies to modules and packages as much as to services. A monolith with no internal boundaries (one massive project with 50 unrelated responsibilities) violates SRP even without any service decomposition.
- **Microservices:** Azure advises starting coarse-grained when uncertain about boundaries. "Splitting one service into two is easier than refactoring functionality across several existing services." Over-splitting early is more expensive than merging later.
- **Conway's Law:** Pair organizational team structures to bounded contexts so organizational boundaries reinforce and clarify architectural ones.
- **Discovery techniques:** Event Storming (Alberto Brandolini) and Context Mapping (Eric Evans) help identify whether boundaries are correctly drawn before problems emerge in production.
- **Validation metrics:** Use "independent deployability" and "no chatty calls" as first-class constraints when validating whether service boundaries are appropriate.

## False Positives to Avoid

- A service that handles multiple operations within a single coherent business domain is fine (e.g., an Order service managing order creation, updates, status transitions, and cancellation — all part of unified order management).
- A monolith module with many classes but a single, clear business focus does not violate SRP. The principle is about coherent responsibility, not code size.
- An orchestrator or saga that coordinates a multi-step business process across multiple services has coordination as its responsibility — that is its single, legitimate purpose and not a violation.
- A utility or infrastructure library that multiple services depend on is not a god service; it has a clear, focused infrastructure responsibility.
