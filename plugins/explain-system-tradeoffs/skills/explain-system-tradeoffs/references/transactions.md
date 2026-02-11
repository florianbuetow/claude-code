# Transaction Boundaries & Coordination

> "Microservices buy you options. They also buy you lots of new failure modes."
> — Sam Newman, Building Microservices

## Core Idea

Where a system draws its atomicity boundary — and how much coordination it tolerates
across those boundaries — encodes the fundamental tension between simplicity, scalability,
and correctness. A monolith with a single database gets strong transactions for free
but couples everything into one failure domain. Microservices with per-service databases
gain independent scaling and deployment but must explicitly manage distributed consistency
through sagas, outbox patterns, or eventual convergence.

The artifacts of these choices are visible in deployment topology, database connection
strings, schema evolution strategy, API contract design, and the presence (or absence)
of compensation logic.

## Tradeoff Indicators

### 1. Monolith vs Microservices Topology

**What to look for:**
- Single deployable with one database and pervasive local transactions = monolith
  prioritizing simplicity and strong invariants within one failure domain
- Service boundaries with decentralised data ownership and distributed failure handling
  = microservices choosing independent scaling/deployment over simplicity
- Modular monolith patterns: internal module boundaries enforced by visibility rules
  (Bazel `visibility`, Shopify's Packwerk) but single deployment unit
- Service mesh presence (Istio, Linkerd, Envoy sidecars) confirming inter-service
  network communication

**What it reveals:**
- Monolith with local transactions = simplicity and correctness over independent scaling
- Microservices with per-service databases = independent evolution over transactional
  simplicity
- Modular monolith = "increased modularity without increasing deployment units"
  (Shopify's explicit framing) — a middle ground that preserves local transactions
  while gaining boundary enforcement
- Microservices sharing a database = hybrid that preserves some transactional guarantees
  but undermines independent deployment (often a migration waypoint)

**How to confirm:**
- Trace one business command end-to-end: if it returns success before all downstream
  services observe the change, and correctness relies on later convergence or
  compensation, that is distributed consistency
- Check database connection strings: separate hostnames or database names per service
  confirms per-service data ownership

**Common false positives:**
- "Microservices" sharing a database are not truly independent despite separate deployment
- A monorepo does not equal a monolith
- An API gateway routing requests doesn't prevent backend services from directly
  accessing each other's databases

### 2. Distributed Transaction Avoidance: Sagas and Outbox

**What to look for:**
- Saga frameworks: Eventuate, Axon, MassTransit saga state machines, custom
  orchestrators with compensation handlers
- Compensation handlers/actions (undo logic for each step in a multi-service operation)
- Transactional outbox: an "outbox" table (`id`, `aggregate_type`, `aggregate_id`,
  `type`, `payload`, `timestamp`) written in the same local transaction as business state
- CDC relay (Debezium) publishing outbox events to a message broker
- "No dual writes" patterns — writing to exactly one system (database) atomically
  and relaying changes asynchronously
- Choreography-based sagas: services react to domain events without central orchestration
  vs orchestration-based: a saga orchestrator directs the sequence

**What it reveals:**
- Saga with compensation handlers = the system substitutes global atomicity with
  eventual consistency plus compensations; it accepts that intermediate states are
  visible and rollback is best-effort
- Transactional outbox + CDC = reliable messaging without distributed transactions;
  the system accepts eventual consistency for reliable cross-boundary communication
- Choreography = loose coupling between services (each service decides independently)
  at the cost of harder-to-understand overall flow
- Orchestration = clearer overall flow at the cost of a central coordination point

**How to confirm:**
- Does a business command return success before all downstream services observe the
  change? If so, the system relies on eventual convergence
- Are there compensation handlers that undo steps on failure? Their presence confirms
  saga-based design
- Is there an outbox table that's written in the same transaction as the business
  entity? That confirms the transactional outbox pattern

**Common false positives:**
- Event sourcing is not the same as a saga — event sourcing stores events as the
  source of truth, while sagas coordinate multi-service operations
- A message queue between services doesn't automatically mean saga — it may just be
  async communication without compensation logic
- An outbox table without a CDC relay may be abandoned infrastructure

### 3. Coordination Mechanisms

**What to look for:**
- Strict failure isolation: majority quorum requirements (ZooKeeper's Zab, etcd's Raft),
  leader election, split-brain prevention
- Looser coordination: gossip-based membership (SWIM protocol), weakly-consistent
  dissemination, eventual membership convergence
- Distributed locks: ZooKeeper recipes, etcd leases, Redis Redlock
- Idempotency keys in APIs: if APIs accept idempotency keys and store the first result
  for replay on retries, the system acknowledges retries happen and prevents duplicate
  side effects (Stripe's approach)

**What it reveals:**
- Majority quorum requirements = willing to sacrifice availability to avoid inconsistency
- Gossip-based membership = scalable, weakly-consistent control plane (AP/scale signal)
- Distributed locks = coordination overhead accepted for correctness on specific operations
- Idempotency keys = the system is built for "at-least-once" delivery with explicit
  deduplication — availability (retry) prioritized while preventing duplicate side effects

**Common false positives:**
- ZooKeeper/etcd used only for leader election doesn't mean the whole system uses
  consensus for data
- Distributed locks that are rarely used may be precautionary rather than architecturally
  significant
- Redis Redlock is controversial (the Kleppmann-Antirez debate) — its presence may
  indicate a correctness gap

### 4. Schema Evolution and Deployment Coupling

**What to look for:**
- Avro Schema Registry compatibility modes: BACKWARD (default — upgrade consumers
  first), FORWARD (upgrade producers first), FULL_TRANSITIVE (all versions mutually
  compatible)
- Protocol buffer evolution: `reserved` fields, field numbering gaps, proto3 all-optional
  design, `FOO_UNSPECIFIED = 0` enum convention
- Database migration patterns: simple sequential migrations (maintenance-window tolerance)
  vs expand-contract (zero-downtime deployment)
- Dual-write code paths writing to both old and new columns during migration
- Feature flags controlling which column/field is read during transitions
- API versioning: Stripe date-based versioning with per-account pinning (massive
  backward compatibility investment) vs simple `/v1/` prefix

**What it reveals:**
- Schema Registry set to FORWARD or FULL_TRANSITIVE = deliberate override, conscious
  coordination decision about producer/consumer independence
- Expand-contract migrations = zero-downtime requirement accepted with complexity
- Proto3 all-optional = evolution freedom over type safety
- Sequential migrations = maintenance windows are acceptable (simpler but less available)
- Stripe-style date-based versioning = maximum backward compatibility investment
- `/v1/` prefix without a `/v2/` = speculative versioning (the version boundary was
  never actually needed)

**Common false positives:**
- Schema Registry at BACKWARD default may simply be unconfigured
- Field number gaps in .proto files without `reserved` annotations — may be lazy deletion
  rather than principled evolution
- Liquibase rollback blocks that exist as template boilerplate never tested
- `.avsc` files with default values on all fields as a template convention

### 5. API Contract Design

**What to look for:**
- Pagination strategy:
  - Offset-based (`?page=2&per_page=50`) = simple, supports random access but breaks
    under concurrent mutations
  - Cursor-based (opaque `next_page_token`, Google AIP-158) = consistent iteration
    at the cost of random access and total count
  - Keyset (`?since_id=12345&limit=100`) = database-efficient deep pagination
- Field masks (`google.protobuf.FieldMask`, `?fields=` query parameters) = safe partial
  updates preventing accidental field clearing
- Technology choice: `.proto` with `rpc` (strong typing, performance) vs `.graphql`
  (flexible queries, complexity risks) vs REST with OpenAPI (interoperability)
- GraphQL with persisted queries + query complexity limits = production-hardened;
  GraphQL without complexity limits = vulnerability waiting to happen

**What it reveals:**
- Cursor pagination = correctness for large-scale iteration prioritized over convenience
- Field masks = the system has been bitten by unintentional data loss from naive PATCH
- gRPC = internal service communication optimized for performance and type safety
- GraphQL with complexity limits = client power with server protection
- REST with OpenAPI = interoperability-first, universal accessibility
- Different rate limits per endpoint or customer tier = mature API management

**Common false positives:**
- `/v1/` URL prefix without `/v2/` is speculative versioning
- OpenAPI specs that are auto-generated and outdated don't reflect actual contracts
- `page` and `per_page` parameters that are Django/Rails framework defaults
- GraphQL adopted for an internal API where REST would have been simpler

### 6. Dependency Boundary Enforcement

**What to look for:**
- Vendored dependencies (`vendor/` in Go, `third_party/` in monorepos) = supply chain
  security and build reproducibility over dependency freshness
- Bazel BUILD `visibility` rules: `//visibility:private` (compile-time module boundaries)
  vs `//visibility:public` (absent enforcement)
- Go `go.sum` hash verification, Bazel hash-pinned external dependencies
- Shopify Packwerk for Ruby on Rails = static analysis enforcing component boundaries
  in a modular monolith
- Database-per-service visible in connection strings: separate hostnames/database names
  per service vs shared database
- Per-service Flyway/Alembic migration directories confirming data ownership boundaries
- Shared proto repositories with clear package structures and the size of `shared/`
  common types

**What it reveals:**
- Vendored + hash-verified dependencies = supply chain security prioritized
- Compile-time visibility rules = strong boundary enforcement accepted with build
  system complexity
- Database-per-service + per-service migrations = full data ownership decoupling
- Large shared proto surface = high coupling despite service boundaries
- Google's One-Version Rule = dependency consistency prioritized over per-team autonomy
- Packwerk in Rails = modular monolith investment — "modularity without deployment units"

**Common false positives:**
- Vendored dependencies that haven't been updated in years = neglect, not security strategy
- `//visibility:public` everywhere = the build system supports boundaries but they aren't enforced
- Shared proto repository without clear ownership = accidental coupling
- Per-service databases that are actually different schemas in the same PostgreSQL instance

## Cross-Axis Interactions

- **With Consistency:** Sagas explicitly accept eventual consistency; systems that
  avoid distributed transactions must choose what consistency level each operation gets
- **With Data Distribution:** Database-per-service with saga patterns is a direct
  consequence of shard-first data distribution
- **With Resilience:** Compensation handlers are a resilience mechanism — they define
  what happens when part of a distributed operation fails
- **With Operations:** Schema evolution strategy directly affects deployment safety
  and rollback capability

## False Positives to Avoid

- A monolith is not automatically a problem — for many systems, it's the right choice
  at the current scale. Flag as "simple and effective" rather than "needs to be broken apart"
- Microservices sharing a database are not fully decoupled despite separate deployments
- Event sourcing frameworks in dependencies used only as message buses
- An outbox table without CDC relay may be abandoned infrastructure
- gRPC used only between two services doesn't indicate a system-wide contract strategy
- Saga frameworks imported but only used for simple request-response patterns
