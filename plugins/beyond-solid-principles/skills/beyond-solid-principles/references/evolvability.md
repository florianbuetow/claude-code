# Build for Change (Evolvability)

> "Prefer evolvable over predictable — optimize for responding to unknown challenges rather than perfectly solving known ones." — Ford, Parsons & Kua, Building Evolutionary Architectures (2017)

## Core Idea

Neal Ford, Rebecca Parsons, and Patrick Kua coined "evolutionary architecture": architecture that supports guided, incremental change across multiple dimensions. Requirements, data, and constraints will shift — the question is whether the architecture absorbs that change gracefully or resists it catastrophically. Foundational modularity work by David Parnas argues that the effectiveness of modularization depends on the criteria used to divide the system, tying it directly to flexibility and comprehensibility. Evolvability is a first-class architectural quality attribute, not an afterthought. Martin Fowler wrote the foreword to the evolutionary architecture book, calling continuous delivery "a crucial enabling factor."

## Violation Patterns

### 1. Big-Bang Rewrite Dependency

**Heuristic:** The system has accumulated so much coupling and rigidity that any significant change requires a massive coordinated effort or complete rewrite.

**Look for:**
- Feature lead time growing rapidly as the system evolves
- Small changes have unexpectedly large blast radius
- "We can't change X without rewriting Y" is common
- eBay's multi-year migrations from Perl to C++ to Java illustrate the extreme cost

**Refactoring/Remedy:** Apply the Strangler Fig pattern (Fowler, 2004): identify thin slices, introduce a routing facade, coexist with legacy, eliminate old functionality incrementally. Never attempt big-bang rewrites.

### 2. Breaking API Changes Without Versioning

**Heuristic:** API changes deployed without versioning cause cascading client failures.

**Look for:**
- No version histories on APIs
- Field removals or renames without deprecation paths
- Clients that must update synchronously
- No backward-compatibility tests
- Azure's versioning policy: "an API version completely defines behaviour — behaviour change requires a version change"

**Refactoring/Remedy:** Adopt API versioning (URI path, header, or query parameter). Enforce backward compatibility as the default — additive changes should never require a version bump. Use expand-and-contract for schema migrations.

### 3. Tight Infrastructure/Persistence Coupling

**Heuristic:** Business logic entangled with specific database technology, ORM frameworks, or cloud SDKs, so migrating storage requires rewriting domain logic.

**Look for:**
- Domain types depending directly on persistence or transport types (ORM entities, API DTOs)
- Domain objects requiring framework initialization to instantiate
- Direct database SDK imports in business logic
- Technology lock-in visible in the core domain layer

**Refactoring/Remedy:** Clean/onion architecture: domain model is persistence-ignorant. Create adapter/mapper layers. The domain defines what it needs; infrastructure adapts to it. Prefer libraries over frameworks (frameworks are harder to replace).

### 4. Absence of Architectural Fitness Functions

**Heuristic:** No automated mechanisms to detect when architectural qualities (coupling, performance, security) silently degrade over time.

**Look for:**
- Architecture rules exist only in documentation/wikis
- No automated dependency checks in CI
- Coupling metrics not tracked
- Silent boundary erosion over months
- Ford et al. define fitness functions as "objective integrity assessments of architectural characteristics"

**Refactoring/Remedy:** Implement fitness functions: automated tests running in CI/CD that enforce architectural constraints. Track DORA metrics (deployment frequency, lead time, change failure rate, MTTR). Use ArchUnit/NetArchTest to enforce dependency rules.

### 5. No Incremental Delivery Capability

**Heuristic:** All changes deployed "big bang" without feature flags, gradual rollout, or rollback capability. Deployment equals release.

**Look for:**
- No feature flag infrastructure
- No canary or blue-green deployment capability
- Changes cannot be rolled back without redeployment
- Feature branches living longer than one week (indicating inability to do trunk-based development)

**Refactoring/Remedy:** Feature flags decouple deployment from release, enabling instant rollback. Expand-and-contract database migrations prevent destructive schema changes. Invest in CI/CD, automated testing, and trunk-based development.

## System-Scale Notes

- Fitness functions can be categorized: triggered vs. continual, atomic vs. holistic, static vs. dynamic, automated vs. manual.
- The four DORA metrics directly measure an architecture's capacity for change.
- Build anticorruption layers to shield your domain from external system changes.
- Fowler's MonolithFirst: start with a modular monolith, split when proven domain boundaries, operational maturity, and team size justify it.
- ADRs (Architecture Decision Records) force discipline by requiring teams to articulate why a complex pattern is needed now.
- Key distinction: YAGNI applies to speculative features, NOT to practices that make software easier to modify. Refactoring, self-testing code, CI/CD, and clean architecture are enabling practices, never YAGNI violations.

## False Positives to Avoid

- Choosing a specific technology (e.g., PostgreSQL) is not an evolvability violation as long as the domain code doesn't depend directly on it. Technology choices are fine; tight coupling to them is the problem.
- A system without API versioning in internal-only APIs where a single team owns all consumers may be fine — versioning is most critical at organizational or external boundaries.
- Not every piece of code needs to be behind a feature flag. Feature flags add complexity and are most valuable for high-risk or high-impact changes.
- A well-designed monolith can be more evolvable than poorly-designed microservices.
