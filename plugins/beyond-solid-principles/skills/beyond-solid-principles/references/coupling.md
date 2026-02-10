# Loose Coupling, High Cohesion

> "The goal is to create modules that can be understood, developed, tested, and maintained independently." — Larry Constantine & Ed Yourdon, Structured Design (1979)

## Core Idea

Larry Constantine and Ed Yourdon defined these complementary metrics in Structured Design (1979). Coupling measures how much one component depends on another's details; cohesion measures how related the elements within a single component are. The ideal is low coupling between components and high cohesion within them. Sam Newman calls this the core motivator behind microservices and event-driven architecture. Azure's microservices guidance: "microservices are loosely coupled if you can change one service without requiring other services to be updated at the same time, and cohesive if they have a single, well-defined purpose." At system scale, Martin's package coupling metrics provide quantitative tools: the Stable Dependencies Principle, the Stable Abstractions Principle, and the Distance from Main Sequence metric.

## Violation Patterns

### 1. Distributed Monolith

**Heuristic:** Services that must deploy together despite being technically separate. Gremlin identifies three forms: behavioral coupling (dependency must be available), temporal coupling (requiring low-latency synchronous communication), and implementation coupling (changes to one service force changes in others).

**Look for:**
- Coordinated deployments are normal because changes require multiple services to update together
- Inability to deploy services independently
- Service A becomes unavailable when service B goes down

**Refactoring/Remedy:** Redraw boundaries along business capabilities using DDD. Each service should own its data and be independently deployable. Use asynchronous messaging to eliminate temporal coupling.

### 2. Shared Mutable State / Shared Database

**Heuristic:** Multiple services read and write the same database schema, creating hidden coupling at the data layer.

**Look for:**
- Multiple services with direct access to the same tables
- Schema changes requiring coordination across teams
- "Using database entities as events" (Azure antipattern)
- Modules sharing global caches or static singletons

**Refactoring/Remedy:** Each service owns its data store with no cross-service database access. When Service B needs Service A's data, A publishes events and B maintains a local projection. Use Anti-Corruption Layers to protect boundaries.

### 3. Synchronous Call Chain Entanglement

**Heuristic:** Long synchronous dependency chains (A→B→C→D) where all services must be responsive simultaneously. This creates temporal coupling that cascades both latency and failure.

**Look for:**
- Distributed traces showing deep synchronous call chains
- P95/P99 latencies compounding across hops
- One slow service causing all upstream services to degrade
- Thread pool exhaustion from blocked calls

**Refactoring/Remedy:** Replace synchronous chains with asynchronous messaging (Kafka, RabbitMQ, SQS) where possible. Use event-driven patterns where services react to domain events rather than pulling data through call chains.

### 4. Low Cohesion — Technical-Layer Organization

**Heuristic:** Organizing by technical layer (/entities/, /factories/, /repositories/) rather than business domain produces low cohesion: a single feature change touches files across many folders.

**Look for:**
- Shotgun surgery — a feature change requires editing files in 5+ unrelated directories
- Architecture diagrams that look like spaghetti with no clear dependency direction
- "Common" or "Shared" projects with unrelated functionality mixed together (logging, date helpers, domain rules, UI utilities)

**Refactoring/Remedy:** Organize by business capability and bounded context. Group operations that naturally change together into one cohesive module. Feature slicing: keep all code for one feature vertically aligned.

### 5. Wide Interfaces Leaking Implementation Details

**Heuristic:** Service interfaces become "wide" because other services need internal details, not because domain operations require them.

**Look for:**
- APIs that expose internal data structures rather than domain operations
- Many endpoints/fields that exist for other services rather than domain needs
- Interservice chattiness grows as teams spend effort managing call graphs
- APIs that model internal implementation rather than the domain

**Refactoring/Remedy:** Design APIs to model the domain, not internal implementation. Use intention-revealing operations (PlaceOrder, not SetOrderStatusAndUpdateInventoryAndNotifyShipping). Consumer-driven contract testing (Pact) verifies provider changes don't break consumer expectations.

## System-Scale Notes

- Martin's package coupling metrics: Afferent coupling (Ca) = inbound dependencies, Efferent coupling (Ce) = outbound dependencies. Instability (I = Ce/(Ca+Ce)). Distance from Main Sequence catches modules in the "Zone of Pain" (concrete but heavily depended upon) or "Zone of Uselessness" (abstract but unused).
- Deployment coupling is the most practical smell — can you deploy services independently?
- Git co-change analysis reveals logical coupling invisible in static dependency graphs.
- Chaos engineering (injecting failures) tests whether services are truly independent.
- Track Ca, Ce, and instability per module in CI pipelines as automated fitness functions.
- CodeOpinion emphasizes functional cohesion (grouping by related business operations) over informational cohesion (grouping by shared data).
- Destructive decoupling is the opposite extreme — decoupling so aggressively that interfaces everywhere have no coherent purpose.

## False Positives to Avoid

- Libraries or modules with high afferent coupling (many things depend on them) that are also highly stable and abstract are not violating coupling principles — they are in the ideal "Zone of the Main Sequence."
- A service that makes several calls to another service as part of a single coherent operation is not necessarily too tightly coupled — evaluate whether the calls represent a genuinely distributed workflow.
- Event-driven architecture still has coupling — it's just looser and temporal. Publishing an event doesn't eliminate the dependency; it changes its nature.
- A well-designed monolith with clear module boundaries can have lower coupling than poorly-designed microservices.
