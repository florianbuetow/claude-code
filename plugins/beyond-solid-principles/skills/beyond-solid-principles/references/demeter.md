# Principle of Least Knowledge / Law of Demeter

> "Only talk to your immediate friends." — Ian Holland, Northeastern University, 1987

## Core Idea

The Law of Demeter states that a method may only invoke methods on itself, its parameters, objects it creates, and its instance variables — never on objects returned by other method calls. At architecture scale, LoD constrains communication patterns: a component should only interact with its immediate collaborators and never reach through them to access distant internal details. Robert C. Martin devotes several pages of Clean Code Chapter 6 to "Train Wrecks," "Hybrids," and "Hiding Structure." Martin Fowler pragmatically calls it the "Occasionally Useful Suggestion of Demeter." The key insight: LoD is a coupling-control rule that limits what components need to know about each other's internal structure.

## Violation Patterns

### 1. Train Wreck / Deep Object Navigation

**Heuristic:** Chained method/property calls that traverse multiple objects, exposing deep structural knowledge.

**Look for:**
- `ctxt.getOptions().getScratchDir().getAbsolutePath()`
- `order.getCustomer().getAddress().getCity()`
- Chains longer than two dots on objects (not data structures)
- Disguising chains with intermediate variables doesn't fix it — the caller still knows the internal structure

**Refactoring/Remedy:** Apply "Tell, Don't Ask" — instead of querying an object's internals, tell the object what you need done. `account.withdraw(amount)` replaces interrogating the balance externally. Create intention-revealing methods that hide the navigation.

### 2. Service Reach-Through / Transitive Dependencies

**Heuristic:** Service A calls Service B, which calls Service C, giving A implicit knowledge of the B→C relationship. If C changes its API, both B and A may break.

**Look for:**
- Distributed traces showing call chains longer than one hop from a given service's perspective
- A client service calling a downstream service then reaching through its DTOs to call another service
- Multi-hop synchronous flows that tightly couple components

**Refactoring/Remedy:** Use facade patterns and API gateways that aggregate calls so clients don't chain through services. Enforce that each layer calls only the layer directly below it.

### 3. Schema Reach-Through in Service Architectures

**Heuristic:** A service reads another service's internal tables, internal event payloads, or database entities directly — coupling itself to the other service's internal representation.

**Look for:**
- Services reading each other's database tables
- Integration tests that manipulate internal tables or queues of a service instead of using its public interface
- Azure explicitly calls "using database entities as events" an antipattern because it exposes internal details

**Refactoring/Remedy:** Enforce "database per service." Services communicate only through public APIs or published events. Event payloads should represent domain concepts, not internal database entities.

### 4. Client-Side Business Logic / Orchestrator Overreach

**Heuristic:** UI clients, API gateways, or orchestrator services replicate domain rules that should live behind service boundaries, effectively knowing too much about the internal logic of services.

**Look for:**
- Gateway/orchestrator code that queries multiple contexts and recomputes internal state
- Calling code that depends on deep internal fields of complex DTOs that should be encapsulated
- Clients assembling a domain operation by pulling many internal fields because no coherent "tell" operation exists

**Refactoring/Remedy:** Expose narrow, intention-revealing APIs (PlaceOrder, ReserveInventory) instead of leaking raw data for callers to manipulate. Push domain logic into the service that owns the bounded context.

### 5. Layer Skipping

**Heuristic:** Presentation layer directly calls data access, bypassing business logic. Lower layers reach up to higher layers.

**Look for:**
- UI code directly executing SQL or calling repository methods
- Infrastructure modules importing from service/domain modules
- Circular imports or lazy imports used to work around circular dependencies

**Refactoring/Remedy:** Enforce strict layer dependency direction. Higher layers call lower layers only through defined interfaces. Use dependency inversion to break circular dependencies.

## System-Scale Notes

- Robert C. Martin draws an important distinction: data structures (DTOs, records) expose data with no behavior — navigating through them is acceptable. Objects expose behavior and hide data — chaining through objects violates LoD.
- Builder patterns and fluent APIs that return the same type at each step are explicitly not violations.
- The Response For a Class (RFC) metric — methods potentially invoked in response to a method call — correlates with bug probability. Following LoD reduces RFC.
- Coupling Between Objects (CBO) measures how many external types a class references.
- At architecture level, visualize service-to-service call chains: any path longer than one hop suggests a potential violation.
- The Demeter paper notes that LoD tends to force narrow method-level dependencies but can lead to wide class-level interfaces because you introduce auxiliary methods rather than digging into structures. This trade-off requires system-level judgment.
- JetBrains IntelliJ includes a built-in "Law of Demeter" inspection.

## False Positives to Avoid

- Navigating through data structures (DTOs, records, configuration objects) is acceptable — LoD applies to objects with behavior, not plain data.
- Fluent APIs and builder patterns that return `this` or the same builder type are not violations — the chain stays on one object.
- A facade that deliberately aggregates multiple calls behind a single interface is not a violation — it's the recommended fix.
- Standard library traversals (e.g., `path.parent.name` in pathlib, or stream operations) are generally not violations.
