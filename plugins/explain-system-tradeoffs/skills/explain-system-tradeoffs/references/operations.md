# Observability, Security & Cost

> "Observability is about being able to ask arbitrary questions of your system
> without having to predict those questions in advance." — Charity Majors

## Core Idea

Observability, security, and cost form a triangle of operational tradeoffs. More
observability means more overhead and storage cost. Stronger security means more
latency and operational complexity. Higher reliability means more redundancy and spend.
These choices are visible in tracing configuration, security infrastructure, audit
patterns, compliance-driven retention, and SLO/error-budget frameworks.

Unlike the other axes which manifest primarily in application code and data layer
configuration, this axis surfaces in operational infrastructure, deployment topology,
and compliance artifacts.

## Tradeoff Indicators

### 1. Distributed Tracing and Context Propagation

**What to look for:**
- Trace context propagation: W3C Trace Context headers (`traceparent`, `tracestate`),
  OpenTelemetry default propagators, or proprietary trace headers
- Sampling configuration: fixed rate sampling, adaptive/dynamic sampling, per-service
  sampling rates
- Tracing SDK integration: OpenTelemetry SDK, Jaeger client, Zipkin instrumentation
- Span creation patterns: manual vs auto-instrumented, span attributes and events
- Sampling rate tuning: high rates (>10%) for low-traffic services vs low rates (<1%)
  for high-traffic services
- Head-based vs tail-based sampling: head-based decides at trace start (simpler,
  may miss interesting traces); tail-based decides after completion (captures errors
  and slow traces, requires buffering)

**What it reveals:**
- End-to-end trace propagation = cross-service debuggability is prioritized
- Adjustable per-service sampling = the team balances observability value against
  overhead/cost per workload
- High sampling rates = debuggability prioritized over overhead (or low traffic)
- Low sampling rates = overhead/cost concerns dominate (or high traffic)
- Tail-based sampling = the team wants to capture interesting traces without the
  cost of sampling everything (sophisticated)
- No tracing = debuggability is not a priority (or the system is simple enough to
  debug without it)

**Common false positives:**
- OpenTelemetry SDK on the classpath but no exporters configured
- Trace headers propagated but no spans created (pass-through without instrumentation)
- Jaeger/Zipkin deployed but sampling at 0% in production

### 2. Structured Logging and Log Management

**What to look for:**
- Structured logging: `LogstashEncoder` (logback), `JsonTemplateLayout` (Log4j2),
  `structlog` (Python) with MDC enrichment (user ID, trace ID, correlation ID)
- Per-package log level overrides (e.g., `logger name="org.hibernate.SQL" level="DEBUG"`)
  = active investigation areas
- Log aggregation pipeline: application → Fluentd/Filebeat → Elasticsearch/Loki → Kibana/Grafana
- Log retention policies: different retention for different log categories
- Request/response logging with PII redaction
- Correlation IDs linking logs to traces to metrics

**What it reveals:**
- Structured logging with trace/correlation IDs = deliberate observability investment
  connecting logs to traces
- Per-package log level overrides = the team actively tunes observability per component
  (the performance-observability tradeoff at package granularity)
- JSON-formatted logs without aggregation pipeline = "structured logging theater"
  (the effort of structuring without the benefit of searching)
- PII redaction = compliance-aware logging (GDPR, HIPAA)
- No correlation IDs = logs are isolated per service (debugging cross-service issues
  requires manual correlation)

**Common false positives:**
- JSON-formatted logs without an aggregation pipeline (no Elasticsearch/Loki/Splunk)
- Log levels set to DEBUG in production (may be leftover from debugging, not deliberate)
- Correlation ID in logs but not propagated to downstream services

### 3. SLOs, Error Budgets, and Reliability Management

**What to look for:**
- Explicit SLO definitions: SLI metrics, SLO targets, error budget calculations
- Error budget policies: what happens when the budget is exhausted (freeze releases,
  focus on reliability)
- SLO-based alerting: alerts on burn rate rather than threshold (faster detection
  of sustained degradation)
- Prometheus recording rules and alerting rules for SLI/SLO calculation
- SLO as code: Sloth, OpenSLO, or custom SLO frameworks
- Composite SLA math: if A=99.9%, B=99.9%, C=99.9%, composite = 99.7%

**What it reveals:**
- Explicit SLOs with error budgets = reliability is a first-class product constraint
  (the team manages reliability proactively, not reactively)
- Burn-rate alerting = sophisticated reliability management (detecting problems before
  the budget is exhausted)
- SLO as code = reliability targets are version-controlled and reviewed
- No SLOs = reliability is aspirational, not measured (common in early-stage systems)
- Composite SLA math done = the team understands how dependency chains affect
  end-to-end reliability
- Error budget freeze policies = the team explicitly trades velocity for reliability
  when needed

**Common false positives:**
- SLO targets defined but never measured or alerted on
- "Five nines" claims without corresponding infrastructure investment
- SLA documents that are contractual (legal) rather than operational (engineering)

### 4. Security Infrastructure

**What to look for:**
- mTLS configuration: `PeerAuthentication mode: STRICT` (zero-trust), PERMISSIVE
  (transitional), or absent
- Certificate management: short-lived certs with automatic rotation (SPIRE, cert-manager)
  vs long-lived static certs
- Workload identity: SPIFFE/SPIRE runtime attestation vs static secrets/API keys
- TLS version requirements: TLS 1.2 minimum, TLS 1.3 preferred
- Network policies: Kubernetes NetworkPolicy, Calico/Cilium policies restricting
  pod-to-pod communication
- Secret management: HashiCorp Vault, AWS Secrets Manager, sealed secrets vs
  environment variables or config files
- RBAC and authorization: OPA/Gatekeeper policies, service-level authorization

**What it reveals:**
- mTLS STRICT with short-lived certs = zero-trust security posture (reduced blast
  radius, stronger authN, operational complexity)
- SPIFFE/SPIRE workload identity = runtime attestation replacing static secrets
  (security over simplicity)
- Static long-lived secrets = operational convenience over security
- Perimeter trust only = the system trusts internal traffic (simpler but larger blast
  radius on compromise)
- Kubernetes NetworkPolicy = micro-segmentation (lateral movement prevention)
- No network policies = flat network (simpler but no blast radius containment)
- Vault for secrets = centralized secret management with audit trails

**Common false positives:**
- mTLS PERMISSIVE is transitional, not the final security posture
- TLS configured at load balancer but plaintext internally = partial encryption
- Secrets in environment variables may be injected from a secret manager (not necessarily
  hardcoded)
- RBAC that grants admin to all services = authorization theater

### 5. Audit Trails and Compliance

**What to look for:**
- Event sourcing: EventStoreDB streams, Axon `@Aggregate`/`@EventSourcingHandler`,
  Marten `StartStream` — events as source of truth with full change history
- Append-only event store tables with `stream_id`, `event_type`, `event_data`, `version`,
  `timestamp`
- Debezium CDC connectors capturing changes from database transaction logs with
  `table.include.list` specifying audited tables and `snapshot.mode: initial`
- Transactional outbox tables alongside Debezium EventRouter SMT
- Compliance-driven retention: 7 years (SOX), 6 years (HIPAA), 12 months (PCI-DSS 4.0,
  3 months immediately available)
- WORM storage (S3 Object Lock, write-once media) = tamper-proof regulatory requirements
- Kafka topic `retention.ms = -1` (infinite) on audit topics vs `604800000` (7 days)
  on operational topics = differentiated retention

**What it reveals:**
- Event sourcing = maximum audit fidelity (every state change captured) at highest
  complexity and storage cost
- CDC capture = audit coverage that includes direct database modifications bypassing
  application code (more complete than app-level logging)
- Differentiated retention (infinite audit, 7-day operational) = deliberate compliance-
  driven data management
- WORM storage = regulatory tamper-proof requirements (SOX, HIPAA, financial services)
- `created_at`/`updated_at` columns alone = ORM defaults, not audit trails (true audit
  requires `operation_type`, `old_values`, `changed_by`)
- No audit infrastructure = either pre-compliance stage or compliance is handled externally

**Common false positives:**
- `created_at`/`updated_at` columns are ORM defaults (Rails, Hibernate), not audit trails
- `_history` tables that are empty = abandoned audit implementation
- Event sourcing frameworks in dependencies used only as message buses
- JSON-formatted logs without aggregation = "audit theater"

### 6. Cost vs Reliability Topology

**What to look for:**
- Multi-AZ deployment: services spread across availability zones with automatic failover
- Multi-region deployment: active/active or active/passive across geographic regions
- Redundancy levels: N+1, N+2, or N+N for critical services
- Auto-scaling configuration: min/max replicas, scaling metrics, cooldown periods
- Spot/preemptible instances for non-critical workloads = cost optimization
- Reserved instances or savings plans for baseline capacity = cost commitment
- Resource requests and limits in Kubernetes = capacity planning

**What it reveals:**
- Multi-AZ = baseline reliability investment (standard for production)
- Multi-region = significant reliability investment (active/active is the most expensive)
- Spot instances for batch/background work = cost optimization accepted with
  interruption risk
- Reserved instances = the team has stable capacity predictions (cost savings with
  commitment)
- No auto-scaling = either fixed-capacity (cost-predictable) or scaling isn't needed
- Over-provisioned resources (large instances with low utilization) = reliability
  margin or waste
- Under-provisioned resources = cost-constrained or early-stage

**Common false positives:**
- Multi-region deployment for user proximity is not the same as multi-region for
  reliability (check whether failover is configured)
- Auto-scaling based on CPU alone may miss memory or queue-depth bottlenecks
- "Multi-AZ" may mean the load balancer is multi-AZ but the database is single-AZ

### 7. Service Discovery and Operational Complexity

**What to look for:**
- Discovery mechanism: Kubernetes DNS (`svc.cluster.local`), Consul
  (`consul.hashicorp.com/connect-inject`), Eureka (`eureka.client.serviceUrl`)
- Client-side vs server-side load balancing: sidecar proxy (fine-grained routing,
  more complexity) vs Kubernetes Service (simpler, less control)
- Health check sophistication: simple TCP checks vs deep health checks with
  dependency verification
- Envoy xDS model: static config (simpler, requires restarts) vs dynamic
  (runtime updates, control plane complexity)

**What it reveals:**
- Kubernetes DNS = tied to K8s ecosystem (simpler within K8s, harder to extend beyond)
- Consul = multi-platform discovery (operational complexity for platform independence)
- Client-side load balancing = fine-grained routing control at operational cost
- Dynamic xDS = mature operations team managing runtime configuration
- Deep health checks = the team understands that "process is running" doesn't mean
  "service is healthy"

**Common false positives:**
- Eureka presence may be legacy Spring Cloud that's being migrated to K8s-native discovery
- Health checks that only verify the process is running (not that dependencies are
  reachable)
- Service mesh sidecar injected but no custom routing rules applied

## Cross-Axis Interactions

- **With Latency:** Observability overhead (tracing, logging) is itself a latency cost;
  sampling rates are the primary control. mTLS adds latency for security
- **With Resilience:** Chaos experiments require observability to measure impact;
  SLOs define what "resilient enough" means; error budgets gate deployment velocity
- **With Consistency:** Audit trails may need strong consistency guarantees for
  regulatory compliance (append-only, WORM storage)
- **With Transactions:** CDC-based audit captures changes at the transaction log level,
  independent of application transaction boundaries

## False Positives to Avoid

- A system with no tracing may be a simple monolith where request logs suffice — don't
  flag as a gap unless the system has cross-service communication
- mTLS PERMISSIVE is a migration state, not the final security posture — check whether
  migration is in progress
- SLO targets without measurement infrastructure are aspirational, not operational
- Multi-region deployment doesn't automatically mean reliability engineering — check for
  failover configuration
- "Structured logging" that outputs JSON but has no aggregation pipeline provides
  no observability benefit over plain text logs
- Event sourcing is an expensive audit mechanism — don't recommend it unless the
  system genuinely needs temporal queries and full change history
