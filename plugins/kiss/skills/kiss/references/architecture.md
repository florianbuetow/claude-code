# Architecture Complexity — Simplification Opportunities

> "Fancy algorithms are slow when n is small, and n is usually small."
> — Rob Pike

## Core Idea

Architecture becomes a simplification opportunity when system-level decisions introduce
disproportionate operational and cognitive overhead relative to the problem being solved.
Kelly Johnson's KISS principle: design systems so they can be maintained by an average
person under pressure. Fred Brooks's distinction between essential complexity (inherent
to the problem) and accidental complexity (introduced by our tools and choices) is the
framework.

The practical measure: when a team spends more time on infrastructure than features,
when onboarding takes weeks for a simple domain, when a one-character fix requires a
full deployment pipeline — the architecture has become the problem it was supposed to
solve.

This dimension also covers **testing complexity** and **configuration complexity** as
architecture-level simplification opportunities, since both are system-level decisions
that can accumulate accidental overhead.

## Simplification Patterns

### 1. Premature Distribution
**Detection heuristic:** Splitting a small product into many services without
demonstrated need for independent scaling or deployment.

**Metric thresholds:**
- More services than engineers: almost certainly simplifiable
- Network calls where function calls would suffice: simplifiable
- Distributed transactions (sagas) for what could be a single DB transaction: simplifiable
- Deployment pipeline takes > 30 minutes for a one-line change: worth examining

**Look for:**
- Teams spending more time on infrastructure than features.
- High ratio of infrastructure PRs to feature PRs.
- Network calls where function calls would suffice.
- Distributed transactions (sagas) for what could be a single database transaction.
- Service mesh complexity for < 5 services.

**Simplification approach:** Fowler's MonolithFirst — start with a modular monolith.
Split only when proven domain boundaries, operational maturity, and team size justify
it. Merge services that always change and deploy together — forced separation of
inseparable things is accidental complexity.

### 2. Architecture Astronautics
**Detection heuristic:** Excessive architectural patterns stacked on patterns,
generalized frameworks that few people understand.

**Metric thresholds:**
- Implementing a simple feature takes days instead of hours: simplifiable
- New team members need weeks to understand the architecture: simplifiable
- Architecture diagram is more complex than the business domain: simplifiable
- "Architecture documents" longer than the codebase: likely over-engineered

**Look for:**
- CQRS + Event Sourcing + DDD + microservices for a CRUD app.
- 10+ architectural layers.
- In-house "frameworks" no one can explain.
- Architectural patterns adopted because they solve problems at a scale the team
  hasn't reached and may never reach.

**Simplification approach:** Kent Beck's four rules of Simple Design — passes all
tests, reveals intention, has no duplication, has fewest elements. Remove layers that
don't deliver proportional value. Ask: "What would this look like if it were simple?"

### 3. Resume-Driven Technology Choices
**Detection heuristic:** Technology choices driven by what looks impressive rather than
what solves the problem. Capabilities far exceed actual usage.

**Look for:**
- Kafka when REST/webhooks suffice.
- Kubernetes for a single-team application.
- GraphQL for a single consumer.
- NoSQL when data is relational.
- Polyglot persistence without clear justification.
- Significant learning curves for marginal benefit.
- Event-driven architecture when request-response is the natural pattern.

**Simplification approach:** Bezos's "one-way door vs. two-way door" — reserve heavy
analysis for irreversible decisions. Pick boring technology where possible. Right-size
technology to the problem. A Postgres database covers an enormous range of use cases
before you need anything fancier.

### 4. Speculative Infrastructure
**Detection heuristic:** Plugin architectures with one plugin, extension points never
extended, infrastructure built for hypothetical scale. Disproportionate complexity for
actual requirements.

**Metric thresholds:**
- Interfaces with 1 implementation across the entire codebase: simplifiable
- Event systems with 1 publisher and 1 subscriber: simplifiable
- Auto-scaling configured but traffic is constant: simplifiable

**Look for:**
- Interfaces with one implementation across the entire codebase.
- Event systems with one publisher and one subscriber.
- Message queues with one producer and one consumer.
- Auto-scaling configured but traffic is constant.
- Multi-region deployment for a single-market product.
- Caching layers for data that's never read twice.

**Simplification approach:** Remove unused abstractions and infrastructure. Apply YAGNI
rigorously. Add generality when the second use case arrives. Design for 10x current
scale, not 1000x.

### 5. Excessive Middle Tiers
**Detection heuristic:** Intermediate layers that add latency and complexity without
delivering meaningful transformation. Charity Majors's test: "How long to ship a
one-character fix?"

**Look for:**
- Proxy services that add no logic, transformation, or validation.
- API gateways that only forward requests.
- BFF (Backend for Frontend) layers that mirror the backend API 1:1.
- Message brokers used as synchronous RPC.
- Caching layers for data that changes frequently and is rarely re-read.

**Simplification approach:** Remove passthrough layers. If a layer doesn't transform,
validate, aggregate, or make decisions, it's accidental complexity. Measure deployment
time for trivial changes as a complexity gauge.

### 6. Testing Overhead
**Detection heuristic:** Test infrastructure that is harder to understand and maintain
than the code it tests. Tests that are brittle, slow, or require extensive setup that
obscures the test's intent.

**Metric thresholds:**
- Test setup > 50% of test function: likely simplifiable
- Mock depth > 3 (mocking a mock's dependency): simplifiable
- Test-to-code ratio > 5:1 for non-critical code: worth examining
- Test suite takes > 10 minutes for a small project: architecture smell

**Look for:**
- Mock setups that mirror the entire dependency graph.
- Test fixtures that are hundreds of lines long.
- Integration tests that require spinning up 5+ services.
- Test helpers that are themselves complex enough to need tests.
- Snapshot tests for rapidly changing UIs (constant false-positive churn).
- E2E tests testing implementation details rather than behavior.

**Simplification approach:** Test at the right level — unit tests for logic,
integration tests for boundaries, E2E tests for critical paths only. If testing
requires extensive mocking, the code under test may have too many dependencies
(coupling problem). Prefer testing through public interfaces over internal details.
Simplify the production code and the tests simplify with it.

### 7. Configuration Sprawl
**Detection heuristic:** Configuration that has grown to cover every possible option,
spread across multiple formats and locations, with defaults that no one remembers and
overrides that no one understands.

**Look for:**
- Configuration files longer than the code they configure.
- Environment matrices (dev × staging × prod × region) with mostly identical values.
- Multiple configuration formats for the same system (YAML + JSON + env vars + CLI
  flags + database settings).
- Feature flags numbering in the hundreds with no cleanup process.
- Configuration values that have never been changed from their initial setting.

**Simplification approach:** Reduce the configuration surface area — many settings
should be code, not config. Use convention over configuration. Consolidate formats.
Clean up stale feature flags. If a value never changes, it's a constant, not a
configuration option.

## System-Scale Signals

These system-level observations suggest architecture simplification opportunities:

- **Declining deployment frequency** often signals architecture too complex to change
  safely.
- **High infrastructure-to-business-logic ratio** suggests accidental complexity
  dominates.
- **Long onboarding time** for what should be a simple domain indicates
  over-engineering.
- **Change amplification** — small feature changes requiring updates across many
  services — indicates poorly drawn boundaries.
- **Standardization gaps** — every service doing logging, monitoring, and deployment
  differently — multiply the "complexity tax" across components.

## False Positives to Avoid

- A system that has grown legitimately complex because the domain is complex — KISS
  targets accidental complexity, not essential complexity.
- Well-established patterns (MVC, repository, DI) that are idiomatic to the tech
  stack — conventions reduce cognitive load.
- A large system with many modules is not inherently complex if each module is simple
  and boundaries are clear.
- Investment in CI/CD, automated testing, and observability is enabling infrastructure,
  not over-engineering.
- Microservices that genuinely serve independent teams with different deployment
  cadences and scaling requirements.
- Configuration for genuinely variable deployments (multi-tenant, multi-region with
  regulatory differences) — the configuration reflects essential, not accidental,
  complexity.
