# Design for Failure / Resilience

> "Integration points are the number-one killer of systems." — Michael Nygard, Release It!

## Core Idea

Michael Nygard's foundational truth: every integration point — network call, database query, external API — is a potential failure vector. The principle assumes networks, services, and hardware will fail and engineers must design retries, timeouts, circuit breakers, and fallbacks from the start. Modern architecture guidance treats partial failure as normal, especially in cloud and distributed systems.

Netflix's multi-region failover kept them running during the 2017 AWS S3 outage that cost S&P 500 companies $150 million. Knight Capital lost $460 million in 45 minutes because they had no circuit breaker to halt runaway trades, no real-time anomaly detection, and no safe rollback mechanism. Resilience is not optional for any system that integrates with external dependencies.

## Violation Patterns

### 1. Missing Timeouts

**Heuristic:** Network calls block indefinitely or for excessive duration. Downstream services becoming slow causes upstream thread pools to fill and the caller itself to become unresponsive — classic cascading failure.

**Look for:**
- HTTP/DB clients with no explicit timeout configuration
- Default timeouts set to minutes or infinity
- Blocking calls without async alternatives
- Thread pool exhaustion under load
- Azure warns about choosing "a shorter timeout so operations fail fast when likely to fail"

**Refactoring/Remedy:** Configure explicit timeouts on every network call. Non-negotiable. Choose timeouts shorter than the caller's own SLA. Prefer "fail fast" when a required dependency is known to be unavailable.

### 2. Unbounded Retries / Retry Storms

**Heuristic:** Retries without limits or backoff create thundering herd problems. Multiple layers retrying the same request multiply attempts exponentially.

**Look for:**
- Retry loops without max-attempt limits
- Retries without exponential backoff and jitter
- Multiple layers (client → gateway → service → DB) each retrying independently, multiplying load as a product of attempts at each layer
- Non-idempotent operations retried (causing duplicate side effects)
- Azure warns: "non-idempotent operations can cause unintended side effects when retried"

**Refactoring/Remedy:** Bounded retries with exponential backoff and jitter. Per-request retry limits. Retry budgets (server-wide or per-client) to contain aggregate retry load. Ensure retried operations are idempotent. Never retry at multiple layers without coordination.

### 3. No Circuit Breakers

**Heuristic:** Clients keep attempting operations against a failing service, wasting resources and potentially preventing downstream recovery.

**Look for:**
- No circuit breaker pattern (Closed → Open → Half-Open) around external calls
- P95/P99 latency spikes when a downstream service degrades
- No fallback behavior when a dependency is down
- Callers that block and wait rather than fail fast when a service is known to be unavailable

**Refactoring/Remedy:** Implement circuit breakers (Resilience4j, Polly, Hystrix). When the circuit opens, serve cached data, defaults, or reduced functionality (graceful degradation). Azure explicitly differentiates retry (expects eventual success) from circuit breaker (prevents likely-to-fail operations) — combine if retry respects circuit-breaker signals.

### 4. No Bulkhead Isolation

**Heuristic:** One overloaded or slow dependency exhausts shared resources (thread pools, connection pools) and takes down unrelated functions.

**Look for:**
- Shared thread pools or connection pools across unrelated dependencies
- One slow service causing all services to degrade
- No resource partitioning per dependency or per tenant
- No load shedding under pressure

**Refactoring/Remedy:** Bulkhead pattern: partition resources into separate pools per dependency so one failure domain can only exhaust its own allocation. Combine with throttling and queue-based load leveling. Azure recommends combining bulkheads with retry/circuit breaker/throttling.

### 5. Single Points of Failure / SLA Inversion

**Heuristic:** The system's promised availability depends on a less-reliable downstream service without mitigation. Or: a single instance of a critical component with no redundancy.

**Look for:**
- Composite SLA math not done (if A is 99.9% and B is 99.9% and C is 99.9%, composite availability drops to 99.7%)
- One database instance, one message broker, or one service instance with no replicas
- No health checks or readiness probes
- Session state stored on individual nodes making recovery impossible

**Refactoring/Remedy:** Redundancy at every critical layer. Multi-instance services with load balancers. Replicated databases. Multi-zone or multi-region for critical paths. Health checks and liveness/readiness probes. Calculate composite SLAs and mitigate where they don't meet requirements.

### 6. No Observability for Failure Detection

**Heuristic:** Failures are invisible until they cascade into full outages. Knight Capital received 97 automated error emails that went unnoticed.

**Look for:**
- No monitoring of P95/P99 latency per dependency
- No circuit breaker state transition monitoring
- No distributed tracing
- No alerting on error rate spikes
- Incomplete dashboards for latency, error rates, and resource saturation

**Refactoring/Remedy:** Implement observability through metrics, logs, and distributed traces (OpenTelemetry). Monitor circuit breaker state, retry rates, thread pool utilization, and connection pool usage. Alert on anomalies before they become cascading failures.

## System-Scale Notes

- Nygard's stability patterns: Timeouts, Circuit Breakers, Bulkheads, Retry with Backoff, Graceful Degradation, Fail Fast
- Netflix's Simian Army: Chaos Monkey (kills instances), Chaos Gorilla (kills AZs), Chaos Kong (kills regions)
- Cascading failure pattern: latency increases → timeouts → retries → load increases → more latency → collapse. Adding capacity often fails because new instances get saturated immediately
- Feature flags enable instant rollback without redeployment — the lesson Knight Capital teaches most painfully
- Asynchronous communication via message queues absorbs failures better than synchronous call chains
- SRE guidance: define time budgets (deadlines), not just timeouts. Misaligned timeouts can trigger immediate subsequent attempts
- Google's SRE: "overload and resource exhaustion interactions" are the primary drivers of cascading failures

## False Positives to Avoid

- A system that calls only a single, highly reliable internal dependency (e.g., a co-located database) may not need a full circuit breaker — a timeout and retry with backoff may suffice. Calibrate to risk.
- Not every service needs multi-region failover. Reserve heavy resilience for critical paths and services with strict SLA requirements.
- A batch processing system that can tolerate delays may not need circuit breakers — it may be acceptable to retry with longer intervals.
- Chaos engineering is not required for every project. It is most valuable for systems with complex dependency graphs and strict availability requirements.
