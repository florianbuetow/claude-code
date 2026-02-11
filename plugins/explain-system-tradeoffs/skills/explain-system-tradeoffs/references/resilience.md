# Resilience & Failure Isolation

> "Everything fails, all the time." — Werner Vogels

## Core Idea

Resilience patterns are often the clearest "reverse signal" of a system's priorities
because they encode what the system fears most: cascading failures, retry storms,
overload, and partial failures. The investment level — from basic timeouts to
sophisticated chaos engineering with steady-state hypotheses — reveals how much
operational complexity the team accepts for reliability.

Resilience is not binary. It spans a spectrum from "hope nothing fails" through
"handle individual failures gracefully" to "continuously verify resilience under
realistic conditions." The artifacts at each level are distinct and measurable.

## Tradeoff Indicators

### 1. Circuit Breakers and Failure Detection

**What to look for:**
- Circuit breaker state machines (Closed → Open → Half-Open): Resilience4j,
  Polly, Hystrix (deprecated but still widely deployed)
- Circuit breaker configuration: failure rate thresholds, wait duration in open state,
  permitted calls in half-open state
- Fallback behaviour when circuit opens: cached data, defaults, reduced functionality,
  or hard failure
- Per-dependency circuit breaker instances vs a single global circuit breaker
- Istio/Envoy `outlierDetection`: consecutive errors, interval, base ejection time,
  max ejection percentage

**What it reveals:**
- Per-dependency circuit breakers = the system isolates failure domains independently
- Global circuit breaker = simpler but less precise failure isolation
- Fallback to cached data/defaults = graceful degradation (availability over freshness)
- Hard failure when circuit opens = fail-fast philosophy (correctness over availability)
- Envoy outlier detection = infrastructure-level failure isolation without app code changes
- `maxEjectionPercent < 100` = the system won't eject all endpoints (preserves minimum
  capacity even during widespread failures)

**Common false positives:**
- Hystrix on the classpath but not configured or wrapped around any calls
- Circuit breaker with very high thresholds (e.g., 95% failure rate) that would never
  trip in practice
- A system calling only a single, highly reliable dependency may not need a circuit
  breaker — timeout + retry with backoff may suffice

### 2. Retry Policies and Storm Prevention

**What to look for:**
- Retry logic: bounded vs unbounded attempts, exponential backoff, jitter
- Multi-layer retry multiplication: client → gateway → service → database each
  retrying independently (attempts multiply as a product at each layer)
- Retry budgets: server-wide or per-client limits on aggregate retry load
- Idempotency enforcement on retried operations
- Distinction between transient fault retries and persistent fault handling
- `while(true)` retry loops = dangerous unbounded retry pattern

**What it reveals:**
- Bounded retries with backoff + jitter = mature retry engineering
- Retry budgets = the system has experienced or anticipated retry storms
- Multi-layer retries without coordination = potential for retry amplification
  (3 retries × 3 retries × 3 retries = 27 total attempts for one user request)
- Idempotency keys on retried operations = correctness under retry conditions
- Unbounded retries = the system has not experienced a retry storm yet

**Common false positives:**
- Retry logic that retries non-idempotent operations (may cause duplicate side effects)
- Exponential backoff without jitter (all retriers back off in sync, creating
  synchronized bursts)
- Retry configuration that respects circuit-breaker state vs retry that ignores it

### 3. Bulkhead Isolation

**What to look for:**
- Per-dependency thread pools or connection pools
- Per-tenant resource partitioning
- Separate queues or processing pipelines for different workload classes
- Kubernetes resource limits and requests per container
- Envoy connection pool limits per upstream cluster
- Load shedding under pressure (reject low-priority work to preserve high-priority)

**What it reveals:**
- Per-dependency pools = failure of one dependency cannot starve others (isolation
  at the cost of lower peak utilization)
- Per-tenant isolation = noisy-neighbour prevention (multi-tenant fairness)
- Shared pools across all dependencies = one slow dependency can exhaust shared
  resources and cascade to everything
- Resource limits without requests = Kubernetes can't make scheduling decisions
  (containers may be placed on overcommitted nodes)

**Common false positives:**
- A single shared pool may be adequate for systems with few, equally reliable dependencies
- Over-partitioned pools (one pool per trivial dependency) waste resources
- Kubernetes resource requests without limits = pods can consume unbounded resources

### 4. Progressive Delivery and Deployment Safety

**What to look for:**
- Argo Rollouts canary configurations: multi-step `setWeight` progression, pause
  durations, indefinite pause (`pause: {}` = manual approval gate)
- AnalysisTemplate with Prometheus queries and `successCondition` = automated
  metric-based promotion
- Flagger: `stepWeight`, `maxWeight`, `threshold` (failures before rollback)
- Feature flag integrations: LaunchDarkly `.variation()`, Unleash `.isEnabled()`,
  Split.io `.getTreatment()` — percentage-based rollouts vs simple on/off toggles
- Kill-switch flags that can instantly disable features = explicit blast radius control
- Istio VirtualService traffic splitting with explicit weight percentages
- Argo Rollouts `dynamicStableScale: true` = resource cost for instant rollback capability

**What it reveals:**
- Multi-step canary with analysis templates = the team invests heavily in deployment
  safety (automated quality gates)
- Indefinite pause = human judgment required before full rollout
- Feature flags with percentage rollouts = decoupling deployment from release
  (progressive exposure)
- Kill switches = the team has experienced incidents requiring instant rollback
- Single-step `setWeight: 100` with no analysis = Rollout CRD that behaves like a
  basic Deployment (no safety benefit)
- `dynamicStableScale: true` = the team values rollback speed over resource cost

**Common false positives:**
- A Rollout CRD with single `setWeight: 100` and no analysis = no actual canary
- Feature flag SDKs imported but used only for static boolean configuration
- ArgoCD Application resources indicate GitOps sync, not progressive delivery
- VirtualService with 100/0 weight is routing, not canary

### 5. Rate Limiting as Resilience

**What to look for:**
- Envoy's `failure_mode_deny` boolean: `true` = fails closed (safety over availability),
  `false` = fails open (availability over safety)
- Adaptive rate limiting: Netflix `concurrency-limits` with VegasLimit (delay-based)
  and AIMDLimit (loss-based)
- Priority partitions: `partition("live", 0.9)` and `partition("batch", 0.1)` =
  traffic class differentiation
- Google SRE adaptive throttling with configurable K multiplier (aggression)
- Backpressure propagation through reactive streams or queue depth signals
- Different rate limits per customer tier = multi-tenant fairness

**What it reveals:**
- `failure_mode_deny: true` = the system chooses safety when the rate limiter itself
  is unavailable (one of the most consequential single config values)
- Adaptive limiting = production feedback loops driving load management
- Priority partitions = live traffic explicitly protected over batch/background work
- K=2 in adaptive throttling = allows more wasted backend work but faster recovery;
  K=1.1 = aggressive backend protection
- No rate limiting = the system hasn't experienced overload or trusts upstream to
  manage load

**Common false positives:**
- Default Nginx `limit_req` may be copy-pasted security config
- API gateway rate limits may be infrastructure defaults
- Rate limiter imported but only used for a single endpoint

### 6. Chaos Engineering and Resilience Verification

**What to look for:**
- Chaos Mesh CRDs: PodChaos, NetworkChaos, StressChaos, IOChaos, HTTPChaos with
  `mode` field (one/all/fixed-percent/random-max-percent) for blast radius control
- Schedule CRDs with CRON syntax = continuous resilience validation (not one-off)
- LitmusChaos experiments with `httpProbe` steady-state hypotheses in `Continuous` mode
  = measuring impact, not just breaking things
- `ChaosResult` resources with `verdict: Pass/Fail` and `probeSuccessPercentage` =
  auditable resilience evidence
- Istio fault injection: `fault.delay.fixedDelay`, `fault.abort.httpStatus` with
  `percentage.value` — 10% fault injection in production = real confidence
- k6 load test scripts with `thresholds` (`http_req_duration: ['p(95)<500']`) and
  `abortOnFail: true` = SLOs as code with automated quality gates
- Pact contract tests with Pact Broker and `can-i-deploy` CI checks = systematic
  service boundary testing

**What it reveals:**
- Chaos experiments with steady-state hypotheses and probes = genuine chaos engineering
  (the team measures impact against expected behaviour)
- Scheduled chaos experiments = continuous resilience validation (mature practice)
- Chaos experiments without probes = destruction without measurement (performative)
- Multiple fault types (network, pod, stress, IO) with monitoring = comprehensive
  resilience characterization
- k6 with thresholds in CI = performance regression prevention
- Pact with active Broker verification = contract-driven development

**The key distinguisher between genuine and performative chaos engineering is the
presence of steady-state hypotheses and probes.** A pod-delete experiment without
probes is a tutorial artifact, not resilience engineering.

**Common false positives:**
- Chaos Mesh operators installed but no experiments defined
- k6 scripts in the repository with no CI integration
- Pact files checked in but outdated
- Toxiproxy configs only in test environments
- A single `pod-delete` in a `chaos-test` namespace with no probes

### 7. Service Mesh as Resilience Infrastructure

**What to look for:**
- Istio `DestinationRule` with `outlierDetection`, `connectionPool` limits, custom
  `loadBalancer` policies
- `LEAST_REQUEST` load balancing (vs default `ROUND_ROBIN`) = latency-sensitive optimization
- Per-subset overrides (different settings for v1 vs v2) = deliberate per-version tuning
- `PeerAuthentication` with `mode: STRICT` = zero-trust security posture (mTLS enforced)
- `PERMISSIVE` mode = transitional (allowing both plaintext and mTLS during migration)
- Envoy xDS: static config (simpler, requires restarts) vs dynamic (runtime updates,
  control plane complexity)
- Linkerd vs Istio choice: Linkerd's ultra-lightweight Rust proxy (~10MB vs Envoy ~40-50MB)
  trades feature richness for operational simplicity

**What it reveals:**
- Custom DestinationRules with outlier detection = deliberate traffic management
- Per-subset overrides = the team tunes per version, not blanket defaults
- mTLS STRICT = zero-trust security accepted with operational overhead
- Dynamic xDS = mature operations team managing runtime config
- Linkerd choice = operational simplicity prioritized over feature richness
- Istio ambient mesh (per-node L4 proxy) = newer middle ground reducing resource overhead

**Common false positives:**
- Istio sidecar present but no custom VirtualService or DestinationRule = only defaults
- Envoy bootstrap in Istio deployments is auto-generated; real config is in Istio CRDs
- Service mesh CRDs with Bookinfo sample names = leftover tutorial resources
- `PeerAuthentication PERMISSIVE` = migration state, not final posture

## Cross-Axis Interactions

- **With Latency:** Circuit breakers and timeouts are both resilience and latency
  mechanisms. Hedged requests reduce tail latency but increase total load
- **With Consistency:** Fallback to cached data during circuit-open state trades
  consistency for availability
- **With Transactions:** Compensation handlers in sagas are resilience mechanisms
  for distributed transaction failures
- **With Operations:** Chaos experiments require observability infrastructure to
  measure impact; SLOs define what "resilient enough" means

## False Positives to Avoid

- A batch processing system that can tolerate delays may not need circuit breakers —
  retry with longer intervals may suffice
- Not every service needs multi-region failover — reserve heavy resilience for critical
  paths with strict SLA requirements
- Chaos engineering is not required for every project — it is most valuable for systems
  with complex dependency graphs and strict availability requirements
- A system calling only a single highly reliable dependency needs less isolation than
  one with many unreliable dependencies
- Kubernetes liveness probes are basic health checks, not resilience engineering
