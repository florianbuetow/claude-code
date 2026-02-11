# Consistency & Availability

> "You can't have your CAP and eat it too." — adapted from Eric Brewer

## Core Idea

In the presence of network partitions, a system cannot guarantee both availability and
strong consistency (CAP theorem). Practical systems choose which to sacrifice during
partitions, and many also trade consistency for lower latency even without partitions
(PACELC framing: if Partition → choose Availability or Consistency; Else → choose
Latency or Consistency).

The goal is not to label a system "CP" or "AP" — most real systems sit on a spectrum
and make different choices for different operations. The goal is to read the evidence
and identify *where* on the spectrum each operation sits and whether the position is
deliberate.

## Tradeoff Indicators

### 1. Consensus and Replication Configuration

**What to look for:**
- Leader election, terms/epochs, replicated logs, quorum acknowledgements, membership
  changes, and "commit index" concepts (Raft, Paxos, Zab)
- Replication factor settings and quorum sizes (e.g., `replication_factor: 3`,
  `read_consistency: QUORUM`, `write_consistency: QUORUM`)
- Synchronous vs asynchronous replication settings
- `acks=all` vs `acks=1` in Kafka producer configuration
- ZooKeeper/etcd/Consul usage — and whether used for metadata coordination only or
  for application data

**What it reveals:**
- Consensus artifacts with quorum acks = consistency-first (CP leaning)
- Async replication with conflict resolution = availability-first (AP leaning)
- Consensus used only for metadata while app data is eventually consistent = hybrid
  (common pattern, but frequently misread as fully CP)

**How to confirm:**
- During dependency loss or partition simulation, does the system *reject* or *block*
  writes/reads to preserve invariants? That confirms CP behaviour
- Does the write acknowledgement point wait for a majority/quorum before returning
  success? That is a direct encoding of the consistency choice
- Can the system still accept writes under replica unavailability if it satisfies a
  weaker consistency level? That confirms AP behaviour

**Common false positives:**
- The mere presence of a consensus library does not prove strong end-to-end semantics;
  some systems use consensus only for coordination metadata (membership, locks) while
  app data is eventually consistent
- Confirm by locating the *ack point* for user writes and the *freshness rule* for reads

### 2. Consistency Level Configuration

**What to look for:**
- Per-request consistency levels (e.g., Cassandra's ONE/QUORUM/ALL/LOCAL_QUORUM)
- "Linearizable read" modes with an option to downgrade to local/stale reads
- Read-your-writes guarantees (session consistency)
- `read_concern` and `write_concern` in MongoDB
- PostgreSQL's `synchronous_commit` setting (on/off/remote_apply/remote_write)
- MySQL's `innodb_flush_log_at_trx_commit` (1 = fully durable, 2 = flush per second,
  0 = fully async)

**What it reveals:**
- Tunable consistency levels per request = the system intentionally sits at different
  points depending on the endpoint or workload
- Default strong + option to downgrade = consistency-first with performance escape hatches
- Default weak + option to upgrade = availability-first with correctness escape hatches
- `synchronous_commit = off` = deliberate trade of durability for latency — dangerous
  but intentional
- Different consistency levels for different operations = mature, per-endpoint tuning

**How to confirm:**
- Find which endpoints actually use stricter or weaker settings — this reveals the
  real operational priority
- Check if reads sometimes return older values unless stricter settings are requested
- A system that is AP in normal operation but blocks on "critical invariants" (payments,
  inventory) using stricter levels is making deliberate per-operation choices

**Common false positives:**
- Default consistency levels that were never explicitly chosen
- Framework-provided "consistency" that only applies to a single node (not distributed)

### 3. Cache Freshness Contracts

**What to look for:**
- Cache TTL values and their variation across different data types
- Cache-aside vs write-through vs read-through patterns
- Invalidation mechanisms: pub/sub invalidation, version-based keys, TTL-only
- Multi-layer caching (L1 local + L2 distributed) with different TTLs per layer
- Spring's `@Cacheable`, Caffeine builders, Redis GET/SETEX sequences

**What it reveals:**
- Short TTLs (seconds) = freshness-critical data, accepts higher origin load
- Medium TTLs (minutes) = acceptable staleness for user-facing data
- Long TTLs (hours/days) = static or rarely-changing reference data
- Different TTLs for different cache keys = deliberate freshness tuning
- Write-through caching = consistency prioritized (synchronous cache + DB writes)
- TTL-only invalidation = simplest but only bounded staleness
- Pub/sub invalidation = strong consistency investment at the cost of complexity
- `expireAfterWrite` vs `expireAfterAccess` = whether infrequently-accessed items
  should persist or age out regardless of popularity

**How to confirm:**
- Are cache stampede protections present? (Go's `singleflight`, XFetch algorithm,
  `@Cacheable(sync = true)`) — their presence confirms production-hardened caching
- Is there invalidation logic in write paths? A lone `@Cacheable` without
  invalidation suggests "add caching for speed" without freshness consideration

**Common false positives:**
- Redis client presence alone doesn't distinguish caching patterns
- HTTP `Cache-Control` headers indicate CDN/browser caching, not application-level
  consistency decisions
- A lone `@Cacheable` without invalidation logic in write paths

### 4. Conflict Resolution Mechanisms

**What to look for:**
- Vector clocks or multi-version payloads returned to clients
- Last-write-wins (LWW) conflict resolution
- CRDT (Conflict-free Replicated Data Type) usage
- Hinted handoff, read repair, anti-entropy with Merkle trees
- "May return stale data" or "eventual consistency" in API documentation
- Explicit reconciliation or merge functions in application code

**What it reveals:**
- Version divergence support (vector clocks, multi-version returns) = the system
  accepts conflicting writes and defers resolution
- Repair machinery (hinted handoff, read repair, Merkle trees) = "serve now,
  repair later" availability bias
- CRDTs = availability-first with mathematically guaranteed convergence
- LWW = simplest conflict resolution, accepts potential data loss from concurrent
  writes

**How to confirm:**
- Under replica unavailability, can the system still accept writes? Hinted handoff
  (storing writes for later delivery to unavailable replicas) is an explicit AP signal
- Do reads sometimes return older values unless stricter settings are requested?

**Common false positives:**
- Event sourcing with append-only logs is not the same as conflict resolution —
  it may still require linearizable writes to the event store
- Optimistic locking (version columns in SQL) is a single-node concurrency control,
  not a distributed consistency mechanism

### 5. Schema Compatibility as Consistency Signal

**What to look for:**
- Avro Schema Registry compatibility modes: BACKWARD, FORWARD, FULL, FULL_TRANSITIVE
- Protocol buffer `reserved` field numbers and the `FOO_UNSPECIFIED = 0` enum convention
- Proto3's all-optional-fields design
- Database migration patterns: simple sequential vs expand-contract

**What it reveals:**
- Schema Registry set to FORWARD or FULL_TRANSITIVE = deliberate override of the
  BACKWARD default, indicating conscious coordination decisions
- Expand-contract migrations = zero-downtime deployment requirements and willingness
  to accept complexity for availability
- Proto3 all-optional = evolution freedom prioritized over type safety
- Simple sequential migrations = maintenance-window tolerance (consistency over
  availability during deployment)

**Common false positives:**
- Schema Registry at the BACKWARD default may simply be unconfigured
- Liquibase rollback blocks that exist as template boilerplate never tested

## Cross-Axis Interactions

- **With Latency:** PACELC "EL" systems reduce consistency even without partitions
  for lower latency via local reads or async cross-region replication. Look for
  local/near-replica reads and cross-region async replication with stated RPO/RTO
- **With Data Distribution:** Replication topology directly affects consistency
  guarantees — asymmetric replica counts across regions signal primary-region design
- **With Transactions:** A system that is AP for reads but CP for writes to certain
  entities is making deliberate per-operation tradeoffs
- **With Operations:** SLO/error-budget language reveals whether consistency failures
  are measured and budgeted or merely hoped away

## False Positives to Avoid

- A system using consensus only for metadata (leader election, locks) while application
  data is eventually consistent — don't label the whole system as CP
- Default consistency levels that were never explicitly chosen — flag as "untuned"
  rather than "deliberate"
- Event sourcing is not inherently AP or CP — it depends on the event store's
  guarantees and how projections are built
- A "consistent" cache may just mean "not corrupted", not "linearizable"
- Multi-region deployment does not automatically mean AP — some systems do synchronous
  cross-region writes for strong consistency at latency cost
