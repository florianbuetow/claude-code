# Data Distribution

> "There are only two hard things in distributed systems: guaranteed order of messages,
> exactly-once delivery, and data partitioning." — paraphrased from many engineers

## Core Idea

Data distribution encompasses three interrelated decisions: how data is partitioned
(sharding), how it is replicated (redundancy and locality), and whether reads or writes
are prioritized. These choices are among the most consequential and irreversible in a
system's architecture — they determine what queries are efficient, where hotspots emerge,
how painful resharding will be, and what failure modes the system can tolerate.

The replication–sharding balance, plus read- vs write-optimisation, is usually visible
directly in topology diagrams and in the partitioning logic in code.

## Tradeoff Indicators

### 1. Shard Key and Partition Strategy

**What to look for:**
- MongoDB: `sh.shardCollection("mydb.users", { user_id: "hashed" })` — hash-based vs
  `{ created_at: 1 }` — range-based vs compound keys `{ customer_id: 1, order_id: 1 }`
- Vitess VSchema files (`vschema.json`): `hash`/`xxhash` vindex = uniform distribution;
  `consistent_lookup_unique` = cross-shard queries at write amplification cost;
  `region_json` = geo-aware sharding
- Cassandra `PRIMARY KEY ((partition_key), clustering_columns)` — the double parentheses
  define node placement; composite partition key groups data for locality
- Consistent hashing libraries (Go `ketama`, Guava `consistentHash()`, Python `uhashring`)
  = application-level routing; virtual node count reveals uniformity-vs-memory tradeoff
- ID-embedded shard routing: Pinterest embeds shard_id in UUIDs
  `[shard_id (16 bits)][type_id (10 bits)][local_id (36 bits)]`; Instagram uses
  `shard_id = user_id % 2000` with PostgreSQL schemas as logical shards

**What it reveals:**

| Artifact | Tradeoff axis |
|----------|---------------|
| Hashed shard key | Write distribution ↔ Range query support |
| Range shard key | Query locality ↔ Hotspot risk |
| Lookup vindexes (Vitess) | Cross-shard queries ↔ Write amplification |
| High virtual node count | Load uniformity ↔ Memory overhead |
| ID-embedded shard routing | Resharding flexibility ↔ Indirection complexity |

**How to confirm:**
- Check for scatter-gather queries in explain plans (`mongos` explain showing `Scatter`,
  Vitess `vexplain`) — these reveal when the partition key doesn't align with query patterns
- Resharding operations in operational history indicate the original key was suboptimal

**Common false positives:**
- Consistent hashing libraries imported only for cache routing (not database sharding)
- Compound keys where the second field adds no cardinality
- Multiple database connections that look like sharding but are actually read replicas
- Default `_id` as shard key in MongoDB may be accidental, not deliberate

### 2. Replication Topology and Locality

**What to look for:**
- Multi-zone/multi-region deployment with automatic failover
- Cassandra `NetworkTopologyStrategy` with per-datacenter replica counts (e.g.,
  `us-east: 3, eu-west: 2`)
- Snitch configuration: `GossipingPropertyFileSnitch` (production rack-awareness),
  `Ec2MultiRegionSnitch` (AWS cross-region), `SimpleSnitch` (development)
- `cassandra-rackdc.properties` with `prefer_local=true` = deliberate internal-IP routing
- Kafka `broker.rack` + `RackAwareReplicaSelector` = consumers read from closest replica
  (cross-AZ bandwidth cost optimization on AWS)
- Replica selection logic: "pick nearest", "prefer local region/AZ", health-based routing
- Active/active vs active/passive patterns
- Explicit replication factors and "local quorum" concepts

**What it reveals:**
- Asymmetric replica counts across regions = primary-region design with secondary
  read capacity
- Rack-aware placement + consumption = deliberate cross-AZ cost optimization
- Active/active = availability and locality prioritized over consistency simplicity
- `broker.rack` without `replica.selector.class` = only half the benefit captured
  (rack-aware placement but not rack-aware consumption)
- `prefer_local=true` = latency/cost optimization within datacenter boundaries

**Common false positives:**
- Rack awareness configured but all nodes in the same rack (`dc1:rack1`) provides no
  actual fault tolerance
- Multi-region deployment may be for user proximity, not availability
- Kafka `broker.rack` configured without matching consumer-side rack-aware selector

### 3. Read-Optimized vs Write-Optimized Design

**What to look for:**
- **Write-optimized fingerprints:** Commit logs, memtables, background compaction
  (LSM-tree style); Cassandra's storage engine writing to in-memory memtable + append-only
  commit log; RocksDB with size-tiered or universal compaction
- **Read-optimized fingerprints:** Denormalized read models, materialized views,
  cache-heavy frontends; CQRS (Command Query Responsibility Segregation) splitting
  read and write models
- Operational runbooks for compaction/repair (write-optimized maintenance) or for
  rebuilding read projections (read-optimized maintenance)
- Per-table compaction strategy variation: STCS on write-heavy tables, LCS on
  read-heavy tables within the same cluster

**What it reveals:**
- LSM-tree storage = write throughput prioritized (sequential writes, deferred reads)
- CQRS with separate read models = read performance prioritized at the cost of
  eventual consistency and complexity
- Per-table compaction variation = the team understands per-workload tuning
- Cassandra's hinted handoff/read repair = ongoing operational cost accepted for
  AP-leaning design

**Common false positives:**
- WiredTiger in MongoDB is the only option since 4.2, so its presence isn't a choice signal
- CQRS adopted but the read model is just a cache in front of the same database
- Materialized views that are rarely queried (the read optimization serves no purpose)

### 4. Data Placement and Sovereignty

**What to look for:**
- CockroachDB multi-region SQL:
  - `REGIONAL BY TABLE IN "us-east1"` = table pinned to region
  - `REGIONAL BY ROW` with hidden `crdb_region` column = row-level homing
  - `GLOBAL` tables with non-blocking transactions = low-latency reads everywhere
  - `ALTER DATABASE PLACEMENT RESTRICTED` + `SUPER REGION` = direct GDPR data
    domiciling signal — replicas physically cannot leave designated regions
- Kubernetes topology spread constraints:
  - `topologyKey: topology.kubernetes.io/zone` with `DoNotSchedule` (hard) vs
    `ScheduleAnyway` (soft)
  - `podAffinity` co-locating services = latency over blast radius
  - `podAntiAffinity` spreading database pods = fault isolation over scheduling flexibility
- Terraform multi-region provider aliases with compliance tags
  (`Compliance = "GDPR"`, `DataRegion = "EU"`)
- AWS S3 bucket regions, DynamoDB global tables, Aurora Global Database configurations

**What it reveals:**
- PLACEMENT RESTRICTED + SUPER REGION = regulatory data domiciling (GDPR, data sovereignty)
- REGIONAL BY ROW = per-row latency optimization (rows served from their home region)
- GLOBAL tables = read latency prioritized globally (accepts eventual consistency on writes)
- Hard topology constraints (DoNotSchedule) = availability is non-negotiable
- Soft topology constraints (ScheduleAnyway) = best-effort, may be violated under
  resource pressure
- Co-location affinity = latency over failure isolation
- Anti-affinity spreading = failure isolation over scheduling efficiency

**Common false positives:**
- CockroachDB locality flags on nodes without multi-region SQL = configured but not leveraged
- Topology spread with `ScheduleAnyway` may be routinely violated
- Terraform resources in EU may be simple user proximity, not GDPR compliance
- S3 bucket region may be default account region, not a deliberate placement choice

### 5. Cross-Shard Complexity Management

**What to look for:**
- "No cross-partition transactions", "no joins across shards" policies
- Aggregation pushed into asynchronous pipelines or read models
- Scatter-gather query patterns in middleware/proxy layers
- CQRS separation of read and write models to avoid cross-shard reads
- Shared proto repositories with `shared/common.proto` — the size of shared types
  measures coupling surface area

**What it reveals:**
- Cross-shard avoidance = scale and availability prioritized over simple global invariants
- Scatter-gather queries = the system accepts the latency cost of fan-out reads
- CQRS for cross-shard reads = complexity investment to avoid fan-out at read time
- Large shared proto surface = high coupling between services (potential bottleneck
  for independent evolution)

**Common false positives:**
- An API gateway routing requests doesn't prevent backend services from directly
  accessing each other's databases
- "Microservices" sharing a database are not truly independently sharded
- A monorepo does not equal a monolith (Google's monorepo has strong module boundaries)

## Cross-Axis Interactions

- **With Consistency:** Partition key choice directly affects consistency guarantees —
  operations within a partition can be strongly consistent while cross-partition
  operations require weaker guarantees or coordination
- **With Latency:** Read vs write optimization directly affects latency profiles;
  rack-aware consumption reduces cross-AZ latency
- **With Transactions:** Database-per-service with saga patterns is a direct consequence
  of choosing shard-first distribution
- **With Operations:** Data sovereignty constraints add operational complexity
  (compliance auditing, restricted placement)

## False Positives to Avoid

- A hashed shard key on time-series data is a deliberate sacrifice (accepting poor
  range queries for write distribution); default `_id` as shard key may be accidental
- Having multiple database connections doesn't mean the system is sharded — they may
  be read replicas
- Consistent hashing for cache keys is routing, not database sharding
- Multi-region deployment alone doesn't indicate a sharding strategy
- A monolithic database with large tables may need sharding but hasn't gotten it yet —
  that's a finding about missing data distribution strategy, not a tradeoff choice
