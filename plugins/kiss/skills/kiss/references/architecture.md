# Architecture Complexity

> "Fancy algorithms are slow when n is small, and n is usually small."
> — Rob Pike

## Core Idea

Architecture complexity refers to system-level decisions that introduce disproportionate
operational and cognitive overhead relative to the problem being solved. Kelly Johnson,
lead engineer at Lockheed Skunk Works, coined the KISS principle: design systems so they
can be maintained by an average person under pressure. Fred Brooks's 1986 distinction
between essential complexity (inherent to the problem) and accidental complexity
(introduced by our tools and choices) provides the intellectual framework.

The practical measure of architecture violations is disproportionate complexity relative
to requirements. When a team spends more time on infrastructure than features, when
onboarding takes weeks for what should be a simple domain, when a one-character fix takes
a full deployment pipeline to ship — the architecture has become the problem it was
supposed to solve.

## Violation Patterns

### 1. Premature Microservices / Over-Distribution
**Heuristic:** Splitting a small product into many services without demonstrated need
for independent scaling or deployment. More services than engineers, heavy
Kubernetes/service mesh for a simple CRUD app.

**Look for:**
- Teams spending more time on infrastructure than features.
- High ratio of infrastructure PRs to feature PRs.
- Network calls where function calls would suffice.
- Distributed transactions (sagas) for what could be a single database transaction.

**Refactoring:** Fowler's MonolithFirst — start with a modular monolith. Split only
when proven domain boundaries, operational maturity, and team size justify it.

### 2. Architecture Astronautics
**Heuristic:** Excessive architectural layers, patterns stacked on patterns, generalized
frameworks that few people understand. CQRS + Event Sourcing + DDD + microservices for
a CRUD app, 10+ architectural layers, in-house "frameworks" no one can explain.

**Look for:**
- Implementing a simple feature takes days instead of hours due to all the layers.
- New team members need weeks to understand the architecture.
- The architecture diagram is more complex than the business domain.
- "Architecture documents" that are longer than the codebase.

**Refactoring:** Kent Beck's four rules of Simple Design — passes all tests, reveals
intention, has no duplication, has fewest elements. Remove layers that don't deliver
proportional value.

### 3. Resume-Driven Development
**Heuristic:** Technology choices driven by what looks good on resumes rather than what
solves the problem. Technologies whose capabilities far exceed actual usage.

**Look for:**
- Kafka when REST/webhooks suffice.
- Kubernetes for a single-team application.
- GraphQL for a single consumer.
- NoSQL when data is relational.
- Polyglot persistence without clear justification.
- Significant learning curves for marginal benefit.

**Refactoring:** Bezos's "one-way door vs. two-way door" — reserve heavy analysis for
irreversible decisions. Pick boring technology where possible. Right-size technology to
the problem.

### 4. Speculative Generality
**Heuristic:** Plugin architectures with one plugin, extension points never extended,
infrastructure built for hypothetical scale. Disproportionate complexity for actual
requirements, unused capabilities.

**Look for:**
- Interfaces with one implementation across the entire codebase.
- Event systems with one publisher and one subscriber.
- Message queues with one producer and one consumer.
- Auto-scaling configured but traffic is constant.
- Multi-region deployment for a single-market product.

**Refactoring:** Remove unused abstractions and infrastructure. Apply YAGNI rigorously.
Add generality when the second use case arrives. Design for 10x current scale, not 1000x.

### 5. Excessive Middle Tiers
**Heuristic:** Intermediate layers that add latency and complexity without delivering
meaningful value — the middle tier that performs only basic CRUD passthrough. Charity
Majors's test: "How long to ship a one-character fix?"

**Look for:**
- Proxy services that add no logic, transformation, or validation.
- API gateways that only forward requests.
- BFF (Backend for Frontend) layers that mirror the backend API 1:1.
- Message brokers used as synchronous RPC.
- Caching layers for data that's never read twice.

**Refactoring:** Remove passthrough layers. If a layer doesn't transform, validate,
aggregate, or make decisions, it's accidental complexity. Measure deployment time for
trivial changes as a complexity gauge.

## System-Scale Notes

- A declining deployment frequency often signals that architecture has become too
  complex to change safely.
- A high ratio of infrastructure code to business logic suggests accidental complexity
  dominates.
- If onboarding a new engineer takes weeks for what should be a simple domain, the
  system is over-engineered.
- Fowler: "Don't even consider microservices unless you have a system that's too complex
  to manage as a monolith."
- Standardize cross-cutting concerns (logging, monitoring, deployment) to avoid a
  "complexity tax" multiplying across components.
- Prefer simpler architecture styles when they meet requirements — treat distribution as
  an operational trade-off, not a default.

## False Positives to Avoid

- A system that has grown legitimately complex because the domain is complex — KISS
  targets accidental complexity, not essential complexity.
- Well-established patterns (MVC, repository pattern, DI) that are idiomatic to the
  tech stack — conventions reduce cognitive load.
- A large system with many modules is not inherently complex if each module is simple
  and boundaries are clear.
- Investment in CI/CD, automated testing, and observability is enabling infrastructure,
  not over-engineering.
- Microservices that genuinely serve independent teams with different deployment cadences
  and scaling requirements.
