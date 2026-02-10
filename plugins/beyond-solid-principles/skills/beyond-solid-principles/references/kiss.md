# KISS — Keep It Simple, Stupid

> "Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it." — Brian Kernighan

## Core Idea

Kelly Johnson, lead engineer at Lockheed Skunk Works, coined the principle: design systems so they can be maintained by an average person under pressure. In software, Fred Brooks's 1986 distinction between essential complexity (inherent to the problem) and accidental complexity (introduced by our tools and choices) provides the intellectual framework.

KISS is not "make everything trivial" — it's a bias toward the simplest architecture that satisfies requirements while remaining maintainable and testable. Joel Spolsky coined the "Architecture Astronaut" in 2001: smart thinkers who "go too far up, abstraction-wise" and create "absurd, all-encompassing, high-level pictures of the universe that don't actually mean anything at all." An ICSE 2021 study found that 82% of software professionals believed using trending technologies makes them more attractive to employers — resume-driven development systematically biases teams toward over-engineered solutions.

## Violation Patterns

### 1. Premature Microservices / Over-Distribution

**Heuristic:** Splitting a small product into dozens of services without demonstrated need for independent scaling or deployment. Heavy Kubernetes, service mesh, and complex orchestration for a simple CRUD app.

**Look for:**
- More services than engineers (Segment's 140 services for 3 engineers)
- Teams spending more time on infrastructure than features
- High ratio of infrastructure PRs to feature PRs
- Azure warns: "microservices require a fundamental shift in mindset" and "overly granular services increase complexity"

**Refactoring/Remedy:** Fowler's MonolithFirst: "Almost all the successful microservice stories have started with a monolith that got too big and was broken up." Start with a modular monolith. Split only when proven domain boundaries, operational maturity, and team size justify it.

### 2. Architecture Astronautics / Over-Abstraction

**Heuristic:** Excessive architectural layers, patterns stacked on patterns, generalized frameworks that few people understand.

**Look for:**
- 10+ architectural layers
- CQRS + Event Sourcing + DDD + microservices for a CRUD app
- A real project where implementing a simple "copy user" feature took two full days instead of hours because of all the layers
- Generic in-house "frameworks" that no one can explain

**Refactoring/Remedy:** Kent Beck's four rules of Simple Design: passes all tests, reveals intention, has no duplication, has fewest elements. Remove layers that don't deliver proportional value. Treat complexity as a finite budget.

### 3. Resume-Driven Development

**Heuristic:** Technology choices driven by what looks good on resumes rather than what solves the problem. Kafka when REST suffices. Kubernetes for single-team applications.

**Look for:**
- Technologies whose capabilities far exceed actual usage
- Significant learning curves imposed on the team for marginal benefit
- "We chose this because it's popular" rather than "we chose this because we need X"
- Polyglot persistence without a clear reason

**Refactoring/Remedy:** Jeff Bezos's "one-way door vs. two-way door" framework: reserve heavy analysis for irreversible decisions, use simple reversible solutions elsewhere. Right-size technology to the problem. Pick boring technology where possible.

### 4. Speculative Generality

**Heuristic:** Interfaces with only one implementation, abstract classes never extended, design patterns used "in case we need it later," plugin architectures with one plugin.

**Look for:**
- Disproportionate complexity for the actual requirements
- Unused extension points
- Under-utilized infrastructure capabilities
- Significant portions of system complexity corresponding to features not used or not on the near-term roadmap

**Refactoring/Remedy:** Remove unused abstractions. Apply YAGNI rigorously. If there's only one implementation, you don't need the interface yet. Add abstraction when the second use case arrives and you understand the axis of variation.

### 5. Excessive Middle Tiers and Indirection

**Heuristic:** Intermediate layers that add latency and complexity without delivering meaningful value — the middle tier that performs only basic CRUD passthrough.

**Look for:**
- Azure flags "the middle tier that performs only basic CRUD as adding latency/complexity without value"
- Proxy services that add no logic
- "Onion architecture" where every layer is a 1:1 passthrough to the next
- Charity Majors's test: "How long to ship a one-character fix?"

**Refactoring/Remedy:** Remove passthrough layers. If a layer doesn't transform, validate, or make decisions, it's accidental complexity. Measure deployment time for trivial changes as a complexity gauge.

## System-Scale Notes

- The practical measure of KISS violations: disproportionate complexity relative to requirements
- A declining deployment frequency often signals that architecture has become too complex to change safely
- A high ratio of infrastructure code to business logic suggests accidental complexity is dominating
- If onboarding a new engineer takes weeks for what should be a simple domain, the system is over-engineered
- Fowler: "Don't even consider microservices unless you have a system that's too complex to manage as a monolith"
- Standardize cross-cutting concerns (logging, monitoring, deployment) to avoid a "complexity tax" multiplying across components
- Prefer simpler architecture styles when they meet requirements. Treat distribution as an operational trade-off, not a default

## False Positives to Avoid

- A system that has grown legitimately complex because the domain is complex is not violating KISS — KISS targets accidental complexity, not essential complexity
- Well-established patterns (e.g., MVC, repository pattern, dependency injection) that are idiomatic to the tech stack are not over-engineering — they are conventions that reduce cognitive load
- A large system with many modules is not inherently complex if each module is simple and boundaries are clear
- Investment in CI/CD, automated testing, and observability is not over-engineering — these are enabling infrastructure that makes simplicity sustainable
