# Don't Repeat Yourself (DRY)

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." — Andy Hunt & Dave Thomas, The Pragmatic Programmer (1999)

## Core Idea

DRY is about knowledge, not code. Two identical-looking code blocks representing different domain concepts are incidental duplication — merging them creates harmful coupling. Two different-looking blocks encoding the same business rule are the real violation. At architecture scale, the most dangerous violation is either (a) the same business rule implemented independently in multiple services leading to divergence, or (b) shared domain-object libraries that create distributed monoliths. Sam Newman: "The evils of too much coupling between services are far worse than the problems caused by code duplication." DRY has two distinct failure modes: under-DRY (true duplication of the same knowledge across components) and overzealous-DRY (premature centralization that creates coupling).

## Violation Patterns

### 1. Divergent Business Rules Across Services

**Heuristic:** The same business rule (pricing, validation, eligibility, authorization) is independently encoded in multiple services without a shared authoritative source.

**Look for:**
- Password validation enforced as 8 chars in web, 10 in mobile, 6 on backend
- Discount logic repeated in web app, mobile API, and reporting ETL
- A single business rule change requiring modifications in multiple services (shotgun surgery)

**Refactoring/Remedy:** Identify the authoritative owner of each business rule. Centralize within the owning bounded context. Other consumers call the owner's API or subscribe to its events rather than re-implementing the rule.

### 2. Schema and Contract Divergence

**Heuristic:** Multiple services expose subtly different representations of the same concept because each defined it ad-hoc.

**Look for:**
- "Customer" looks different across services and databases without a clear reason
- JSON fields with same meaning but different names (userId vs customer_id)
- Multiple, slightly different API definitions for the same entity creating integration friction

**Refactoring/Remedy:** Use contract-first design (OpenAPI, Protobuf, AsyncAPI) to generate clients and servers from a single source of truth. Establish canonical models for cross-cutting concepts and version them carefully.

### 3. Shared Library Coupling (Overzealous DRY)

**Heuristic:** A shared domain-object library forces all consuming services to update simultaneously whenever a field changes.

**Look for:**
- Many services cannot upgrade independently because a shared library or shared schema change forces widespread rebuild/redeploy
- Shared entity libraries that grow to include domain logic specific to individual services
- Azure warns "sharing common libraries" is a coupling antipattern

**Refactoring/Remedy:** Share stable contracts (published interfaces), not implementations. Prefer duplication of domain-specific models across bounded contexts over shared libraries. Sam Newman: lean toward duplication when unsure.

### 4. Shared Database as Integration Point

**Heuristic:** Multiple services reading and writing the same database schema, using the database as an implicit integration contract.

**Look for:**
- Multiple services with direct access to the same tables
- Schema changes requiring coordination across teams
- The database schema is treated as shared mutable state

**Refactoring/Remedy:** Each service owns its data store. Integrate through APIs or events, not shared databases. Use materialized views or local copies for read-heavy cross-service data needs.

### 5. Infrastructure Pattern Duplication

**Heuristic:** Each service independently implements its own logging format, retry logic, idempotency strategy, health checks, and configuration management.

**Look for:**
- Copy-pasted HTTP client setup, message deserialization, logging and correlation logic across services
- Different copies of connection strings and feature flags hardcoded in multiple services
- Bug fixes that must be applied in many places

**Refactoring/Remedy:** Extract genuinely cross-cutting infrastructure into shared libraries or sidecars. Use centralized config services (Consul, Vault, Azure App Configuration). Standardize via service mesh for network-level concerns.

## System-Scale Notes

- **The Rule of Three:** Don't abstract until you see three instances of the same knowledge — by the third you understand the commonality well enough. Sandi Metz: "It is better to have some duplication than a bad abstraction."
- **Strategic approach:** Apply DRY aggressively within bounded contexts but accept duplication across them.
- Share stable, cross-cutting types (like a PostalCode value object) but duplicate domain-specific models (like Address, which will diverge between Billing and Delivery).
- **Fowler's Harvested Platform pattern:** don't build shared infrastructure upfront. Build well-factored applications, notice duplication, and extract shared code only after patterns stabilize.
- Static analysis tools (SonarQube, CPD) detect syntactic duplication but cannot identify knowledge duplication. Treat their findings as investigation triggers, not mandates. The key question: "Is this knowledge duplication or syntactic similarity?"

## False Positives to Avoid

- Having a Customer class in both Checkout and OrderManagement microservices is proper bounded-context separation, not a DRY violation — each representation will diverge to serve its context.
- Two code blocks that look identical but represent different domain concepts (e.g., tax calculation for two jurisdictions that happen to currently have the same rate) are incidental duplication — merging them would create harmful coupling.
- Boilerplate required by a framework (e.g., controller setup, DI wiring) is not a DRY violation — it's structural scaffolding.
- Configuration that differs per environment (dev/staging/prod) is not duplication — it's intentional variation.
