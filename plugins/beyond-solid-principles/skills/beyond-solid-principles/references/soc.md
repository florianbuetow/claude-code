# Separation of Concerns (SoC)

> "Separation of concerns is the only available technique for effective ordering of one's thoughts." — Edsger Dijkstra, 1974

## Core Idea

Separation of Concerns splits a system into distinct sections — UI, business logic, persistence, infrastructure — so modifying one area does not force changes in others. At the architecture level, it means enforcing clear boundaries between presentation, domain/business rules, persistence/infrastructure, and cross-cutting concerns. Each layer or module should have a well-defined scope and minimal coupling to others.

Microsoft's architecture guidance is direct: "business rules and logic should reside in a separate project, which should not depend on other projects in the application." This enforces the dependency rule from Clean Architecture: source code dependencies point only inward toward higher-level policies. When concerns are properly separated, changing a database technology, UI framework, or messaging system becomes a localized task rather than a system-wide refactor.

## Violation Patterns

### 1. Big Ball of Mud / Boundary Erosion

**Heuristic:** No clear separation between presentation, application, domain, and infrastructure layers. Controllers talk directly to databases and external APIs while containing domain logic.

**Look for:**
- JSP/Razor pages with embedded SQL queries alongside HTML rendering
- Active Record objects coupling domain logic tightly to persistence mechanisms
- UI components that reference specific database tables or message queue names
- Domain services that inspect HTTP headers or depend on serialization formats

**Refactoring/Remedy:**
Use layered or hexagonal/clean architecture. Establish explicit project/package structure separating presentation, application, domain, and infrastructure. Enforce dependencies pointing strictly inward. Use architecture test tools (ArchUnit, NetArchTest) to validate that higher layers never reference lower ones.

### 2. Persistence-Driven Design

**Heuristic:** Database schema or ORM model becomes the de facto architecture; business logic lives in stored procedures or is tightly coupled to table structure.

**Look for:**
- Domain objects requiring specific ORM base classes, parameterless constructors, or persistence-specific attributes
- Direct database access from multiple unrelated components scattered through the codebase
- Database schema treated as the integration contract between services
- Business logic encoded in database views or stored procedures rather than application code

**Refactoring/Remedy:**
Keep domain models persistence-ignorant. Use repository abstractions and mappers to decouple domain objects from database representation. Prefer programmatic service interfaces over shared persistence as integration points. Treat the database as an infrastructure detail, not an architectural centerpiece.

### 3. UI-Driven Domain Logic

**Heuristic:** Domain logic is duplicated across UI channels (web, mobile, batch) rather than being centralized in a domain or application layer.

**Look for:**
- Business validation rules implemented separately in frontend code for each delivery channel
- Presentation layers directly querying data tiers, bypassing application services
- Documented layer boundaries that exist "on paper" but are routinely bypassed in actual code
- Different business rule implementations across web and mobile frontends

**Refactoring/Remedy:**
Centralize domain logic in application or domain services. Enforce that all UI channels call only application-layer services. Treat the UI as a thin presentation layer that orchestrates domain operations, never as a container for business rules.

### 4. Cross-Cutting Concern Leakage

**Heuristic:** Logging, caching, authorization, and retry logic are spread arbitrarily through all layers rather than being centralized or coordinated.

**Look for:**
- Copy-pasted logging, retry, and security check code across multiple modules
- No middleware, filter, decorator, or AOP patterns despite multiple places needing the same cross-cutting logic
- Each module independently implementing its own version of authentication, rate-limiting, or monitoring

**Refactoring/Remedy:**
Use middleware, filters, decorators, or Aspect-Oriented Programming for cross-cutting concerns. Encapsulate shared infrastructure logic in reusable components. This centralizes concern management and makes policy changes easier.

### 5. Technical-Layer Decomposition in Distributed Systems

**Heuristic:** Microservices are organized by technical concern ("Controller Service", "Repository Service", "Notification Service") rather than business capability.

**Look for:**
- Services that slice horizontally by technical function instead of vertical business domains
- Feature changes that require coordinated edits across many services and their databases
- Architecture discussions framed in technology terms rather than business capability terms
- Services that are tightly coupled because they share infrastructure responsibility

**Refactoring/Remedy:**
Organize services around business capabilities and bounded contexts. Each service should own its domain slice end-to-end, including presentation, application logic, and persistence for that capability.

## System-Scale Notes

- **Monolith:** Enforce SoC via project/assembly/package structure. Use architecture test tools (ArchUnit, NetArchTest) to assert rules like "no UI class references infrastructure directly."
- **Microservices:** Services should be designed around business capabilities, not horizontal layers. Avoid shared databases as integration contracts; each service owns its data.
- **Detection:** Use Robert C. Martin's coupling metrics (Ca, Ce, instability index). Adam Tornhill's change-coupling analysis reveals hidden violations: files that always change together but reside in different modules signal boundary erosion.
- **Contract-first design:** Define explicit interfaces between layers and bounded contexts to prevent leaking internal structures.

## False Positives to Avoid

- A facade or orchestration layer that coordinates multiple concerns is not a violation — coordination across concerns is its single, legitimate responsibility.
- Cross-cutting middleware that touches multiple layers (e.g., request-scoped correlation ID injection) is not a violation; it is infrastructure that serves all layers uniformly.
- A monolith with modules in the same deployment unit is fine as long as dependency direction is enforced; physical separation into services is not required for SoC.
- A service that handles multiple related operations within a coherent domain (e.g., an Order service managing creation, updates, and fulfillment) respects SoC because the domain is unified.
