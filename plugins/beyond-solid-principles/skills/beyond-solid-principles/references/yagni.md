# YAGNI — "You Aren't Gonna Need It" at Architecture Level

> "The most expensive features are the ones you never needed." — Martin Fowler

## Core Idea

Fowler identifies four costs of building presumptive features: the cost of build (wasted effort), the cost of delay (revenue-generating features deferred), the cost of carry (added complexity slowing all subsequent development), and the cost of repair (the feature is often built wrong because understanding evolves).

Research by Kohavi et al. at Stanford and Microsoft found that only one-third of carefully analyzed features actually improved the metrics they were designed to improve — meaning two-thirds of speculative features are wrong. At architecture scale, YAGNI targets premature adoption of complex patterns: full microservices, event sourcing, multi-region active-active, elaborate plugin architectures — when current requirements do not demand them.

The Last Responsible Moment principle from Lean Software Development instructs: delay irreversible decisions until failing to decide would eliminate an important alternative. This is not procrastination — it's disciplined decision-making with the best available information.

## Violation Patterns

### 1. Premature Microservices Decomposition

**Heuristic:** A system decomposed into many microservices without demonstrated need, creating operational overhead that far exceeds business value.

**Look for:**
- More services than engineers (Segment's canonical case: 140+ microservices for 3 engineers)
- Consolidation attempts producing massive gains (Segment saw 46 shared library improvements in one year vs. 32 during the entire microservices era)
- Amazon Prime Video scaling failures (distributed serverless microservices hit 5% of expected throughput, consolidated into one ECS process for 90% cost reduction)
- Teams spending more time debugging cross-service issues than building features

**Refactoring/Remedy:** Adopt Fowler's MonolithFirst approach. Start with a well-modularized monolith with clear module boundaries. Split only when proven domain boundaries, operational maturity, and team size justify it. "Almost all successful microservice stories have started with a monolith that got too big."

### 2. Speculative Generality / Unused Extension Points

**Heuristic:** Interfaces with single implementations, strategy patterns with one strategy, plugin architectures with one plugin, abstract classes never extended.

**Look for:**
- Disproportionate ratio of infrastructure PRs to feature PRs
- Engineers spending more time on infrastructure maintenance than feature development
- Significant complexity for features not on the near-term roadmap
- The answer to "What current requirement does this serve?" begins with "What if someday..." rather than "Currently we need..."

**Refactoring/Remedy:** Remove unused abstractions ruthlessly. Apply the Rule of Three — don't abstract until you see three instances. Add generality only when the second or third use case arrives and you understand the axis of variation. Make concrete before making generic.

### 3. Over-Provisioned Infrastructure

**Heuristic:** Many environments, regions, replicas, and complex orchestration for a system that doesn't yet need that scale or availability.

**Look for:**
- Kubernetes for single-team applications
- Kafka event systems when REST suffices
- Multi-region active-active for an internal tool used by 50 people
- Many environments and replicas sitting unused
- Complex infrastructure that exists "in case we need to scale"

**Refactoring/Remedy:** Right-size technology to the problem. Use metrics and production data to justify scaling decisions, not speculation. Jeff Bezos calls these "two-way door" decisions — make them quickly and cheaply with simple solutions. Add capacity when data proves necessity, not when fear suggests possibility.

### 4. Premature Pattern Application

**Heuristic:** Advanced architectural patterns (CQRS, Event Sourcing, Saga orchestration, hexagonal architecture) applied everywhere including trivial modules.

**Look for:**
- CQRS + Event Sourcing for simple CRUD operations
- Full DDD tactical patterns (Aggregates, Value Objects, Domain Events) in a module with 3 entities
- Distributed transaction infrastructure with only one database
- Pattern proliferation that makes simple changes complex
- Team velocity declining as infrastructure complexity grows

**Refactoring/Remedy:** Apply advanced patterns selectively where justified by complexity or scale. Kent Beck's four rules of Simple Design counter the impulse to add flexibility for speculative needs. Design for replaceability (encapsulate behind interfaces) rather than speculative generality. Add patterns when the pain appears, not before.

### 5. Over-General Domain Models

**Heuristic:** Extremely generic domain models or "frameworks" designed to handle hypothetical future use cases, making concrete features harder to implement.

**Look for:**
- Domain entities with dozens of optional/nullable fields for "future use"
- Overly abstract inheritance hierarchies requiring interpretation
- Configuration-driven behavior harder to understand than code
- The phrase "we built a platform" when a simple application was needed
- Configuration complexity exceeding the complexity of the domain itself

**Refactoring/Remedy:** Build specific solutions for known requirements. Harvest patterns after they emerge rather than predicting them. Fowler's Harvested Platform: build well-factored applications, notice duplication between them, then extract shared code. Make the happy path obvious and easy.

## System-Scale Notes

- **CRITICAL DISTINCTION:** YAGNI applies to speculative features, NOT to practices that make software easier to modify. Refactoring, self-testing code, CI/CD, and clean architecture are enabling practices — they are never YAGNI violations
- The Last Responsible Moment: delay irreversible decisions until failing to decide would eliminate an important alternative. This is not procrastination — it's making decisions with the best available information
- Architecture Decision Records (ADRs) force discipline by requiring teams to articulate why a complex pattern is needed now
- Feature flags and toggles help keep partial work from forcing big-bang releases — these are tools for YAGNI compliance
- Treat "future needs" as hypotheses and validate with production data before paying the full complexity cost
- Segment's consolidation story: "Instead of enabling us to move faster, the small team found themselves mired in exploding complexity"

## False Positives to Avoid

- Investing in CI/CD, automated testing, observability, and clean code practices is NOT a YAGNI violation — these enable future change and are always justified
- A well-chosen abstraction boundary that makes testing easier is not speculative generality — testability is a current requirement
- Security and compliance requirements are not speculative — if regulations require audit logging, encryption, or access controls, implementing them now is not YAGNI
- Designing for replaceability (e.g., putting a database behind a repository interface) is not YAGNI — it's good architectural hygiene that costs almost nothing upfront
- Building monitoring, logging, and alerting infrastructure is not speculative — these are operational necessities from day one
