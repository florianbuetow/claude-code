# Latency & Throughput

> "The universality of tail latency is a consequence of scale." — Jeff Dean & Luiz André Barroso

## Core Idea

Latency and throughput are not simply inverse — they are distinct axes that systems
optimize independently through different mechanisms. Throughput-optimized systems batch,
queue, and pipeline work, accepting higher per-request latency. Latency-optimized systems
enforce deadlines, hedge requests, and fail fast, accepting lower peak throughput.

Tail latency dominates user experience in large fanout systems. A single slow sub-request
can dominate end-to-end latency, making p95/p99 optimization more important than average
latency. The artifacts left by these optimizations are unusually strong fingerprints
because they modify control flow shape.

## Tradeoff Indicators

### 1. GC and Memory Management Configuration

**What to look for:**
- JVM garbage collector selection:
  - `-XX:+UseParallelGC` = throughput optimization for batch workloads
  - `-XX:+UseG1GC` with `-XX:MaxGCPauseMillis` = balanced operation; a lowered target
    like `MaxGCPauseMillis=10` confirms latency-critical service
  - `-XX:+UseZGC` or `-XX:+ZGenerational` (JDK 21+) = sub-millisecond pause requirements
- Equal `-Xms` and `-Xmx` values = deliberate avoidance of heap resize overhead
- `-XX:+AlwaysPreTouch` = latency sensitivity (pre-faults all memory pages at startup)
- Intentionally small heaps with reliance on OS page cache (Kafka pattern: `-Xms6G -Xmx6G`
  with `-XX:MaxGCPauseMillis=20`)
- Off-heap memory: Netty's `PooledByteBufAllocator`, Java `DirectByteBuffer`,
  `-XX:MaxDirectMemorySize`
- `ByteBuf.release()` reference counting = deterministic deallocation bypassing GC
- Rust's `#[global_allocator]` with `jemalloc` or `mimalloc` = explicit allocator selection
- Go's `GOGC` environment variable or `debug.SetGCPercent()` = GC pressure tuning

**What it reveals:**
- ParallelGC = throughput over latency (longer pauses, higher overall throughput)
- ZGC/Shenandoah = latency over throughput (sub-ms pauses, some throughput cost)
- G1GC with tuned MaxGCPauseMillis = balanced with explicit latency target
- Off-heap usage = data moved outside GC-managed heap to eliminate pause impact
- Equal Xms/Xmx + AlwaysPreTouch = team has profiled the live set and optimized startup
- Rust adoption for latency-critical paths = GC elimination (Discord migrated from Go
  to Rust specifically to eliminate 10-40ms GC spikes)

**Common false positives:**
- Copied JVM flags from Netflix or LinkedIn configs without matching the workload profile
- Java 8 tuning flags on Java 21+ runtimes that conflict with modern GC heuristics
- `jemalloc` in Rust without profiling allocation patterns (cargo-culting)
- Large heap with default GC may simply be untuned, not a throughput choice

### 2. Thread Pools and Concurrency Primitives

**What to look for:**
- `ThreadPoolExecutor` core/max pool size ratio (equal = steady-state; large max = bursty)
- Queue type: `LinkedBlockingQueue` (buffered), `SynchronousQueue` (direct handoff),
  `ArrayBlockingQueue` (bounded)
- Rejection policy: `CallerRunsPolicy` (backpressure to caller) vs `AbortPolicy` (fail fast)
- Java virtual threads (`Executors.newVirtualThreadPerTaskExecutor()`,
  `spring.threads.virtual.enabled=true`) = I/O-bound workload optimization
- LMAX Disruptor (`com.lmax:disruptor`) with WaitStrategy:
  - `BusySpinWaitStrategy` = burns CPU for lowest latency (~52ns mean)
  - `BlockingWaitStrategy` = conserves CPU at higher latency
  - `YieldingWaitStrategy` = middle ground
- Akka `throughput` parameter (messages per actor before yielding)
- Go channel buffer sizes: `make(chan Work, 100)` (async) vs `make(chan Work)` (sync handoff)
- `uber-go/automaxprocs` = container-aware GOMAXPROCS (necessary because Go's default
  reads host CPU count, not cgroup limits)
- Separate dispatchers/pools for CPU-bound vs I/O-bound work = workload-aware design

**What it reveals:**
- Disruptor with BusySpinWaitStrategy = extreme latency optimization (burns CPU cores)
- Virtual threads replacing reactive frameworks = I/O-bound workload acknowledging
  that threads aren't the bottleneck
- Separate thread pools per dependency = bulkhead pattern for failure isolation
- `CallerRunsPolicy` = backpressure propagation; `AbortPolicy` = fail fast
- Single pool for all work = no isolation, one slow dependency can starve everything

**Common false positives:**
- Over-provisioned thread pools (200 threads on 4 cores)
- Disruptor for simple pub/sub where `ConcurrentLinkedQueue` suffices
- `synchronized` blocks with virtual threads (causes carrier thread pinning; should
  use `ReentrantLock`)
- Pooling virtual threads (`newFixedThreadPool(100, Thread.ofVirtual().factory())`)
  defeats their purpose

### 3. Batching and Queueing Patterns

**What to look for:**
- Micro-batchers, flush intervals, pooling, async sinks
- "Accumulate then send" patterns in producers/writers
- Kafka producer `batch.size`, `linger.ms`, `buffer.memory` settings
- Database batch inserts and bulk operations
- Log-structured storage (LSM trees): memtables + append-only commit logs +
  background compaction
- Write-ahead logs (WAL) with configurable flush intervals

**What it reveals:**
- Batching as first-class = throughput-optimized (accepting per-item latency increase)
- LSM-tree storage = write-throughput optimization (sequential writes, background compaction)
- Flush interval > 0 = throughput over durability within that window
- If disabling batching (batch size = 1, flush interval = 0) collapses throughput,
  the architecture depends on batching

**Common false positives:**
- Framework-default batching that was never tuned
- Batch size of 1 with linger.ms of 0 = effectively unbatched (may be intentional
  for latency or may be an untuned default)

### 4. Deadline Propagation and Timeout Hierarchies

**What to look for:**
- gRPC native deadline propagation via `grpc-timeout` header
- `context.WithTimeout(ctx, ...)` derived from parent context = deadline chain preserved
- **Anti-pattern:** `context.WithTimeout(context.Background(), 5*time.Second)` = breaks
  the propagation chain entirely — this single line distinguishes genuine deadline
  propagation from absence
- Budget allocation patterns: splitting remaining deadline across downstream calls
  (e.g., `allocateTime(ctx, 0.3)`)
- Envoy timeout hierarchy: `idle_timeout` > `request_timeout` > `route.timeout` >
  `retry_policy.per_try_timeout`
- Relationship `per_try_timeout * maxRetries < route.timeout` confirms retry-aware
  budget management
- C#'s `EnableCallContextPropagation()` on gRPC client factories
- Per-dependency timeout budgets in client libraries

**What it reveals:**
- End-to-end deadline propagation = latency is a first-class concern
- Timeout budgets per downstream call = sophisticated latency engineering
- Fixed timeouts on every call regardless of parent context = no propagation
- All timeouts set to the same value = hierarchy wasn't considered
- Very large or absent default timeouts = system accepts tail risk for simplicity
- Per-dependency timeout values calibrated to actual latency distributions = mature tuning

**Common false positives:**
- HTTP server `request_timeout` is a server-side safeguard, not a propagated deadline
- Load balancer health check timeouts are not deadline propagation
- Fixed per-call timeouts without context derivation are isolated, not propagated

### 5. Hedged and Speculative Requests

**What to look for:**
- gRPC's `hedgingPolicy` with `hedgingDelay` and `maxAttempts`
- Concurrent request patterns with `context.WithCancel` for losing-request cancellation
- Speculative execution in storage systems (e.g., Cassandra speculative retry)
- `hedgingDelay` calibrated to observed p95 latency = tuned to actual distributions

**What it reveals:**
- Hedged requests = tail latency reduction investment (Google showed sending a hedge
  after 10ms delay reduced p99.9 from 1,800ms to 74ms with only 2% more requests)
- Cancellation of losing requests = resource-aware hedging
- Fixed `hedgingDelay` without p95 calibration = copied pattern without tuning

**Common false positives:**
- Simple retry with backoff is sequential, not hedging (hedging sends concurrent
  speculative requests)
- Load balancer retries to different backends are retries, not hedges

### 6. Rate Limiting and Backpressure

**What to look for:**
- Static rate limiters: Guava `RateLimiter`, Nginx `limit_req`, Resilience4j
- **Envoy's `failure_mode_deny` boolean:** `true` = fails closed (safety over availability),
  `false` = fails open (availability over safety) — one of the most consequential
  single configuration values
- Adaptive rate limiting: Netflix `concurrency-limits` library (VegasLimit, AIMDLimit)
- Partition ratios: `partition("live", 0.9)` and `partition("batch", 0.1)` = priority-based
  load shedding
- Google SRE adaptive throttling: `P(reject) = max(0, (requests - K * accepts) / (requests + 1))`
  — the K multiplier encodes throttling aggression (K=2 allows more waste but faster
  recovery; K=1.1 protects aggressively)
- Reactive backpressure: `Flux.onBackpressureDrop()` vs `.onBackpressureBuffer(100)` vs
  `.onBackpressureLatest()`
- Kafka `max.poll.records` and consumer lag as backpressure indicators
- Resilience4j `timeoutDuration` for permit acquisition (0ms = shed immediately;
  higher = queue and wait)

**What it reveals:**
- Adaptive rate limiting = deliberate load management with production feedback loops
- Priority partitions = the system distinguishes traffic classes
- `failure_mode_deny` = fundamental philosophical choice about overload handling
- Different rate limits per customer tier = multi-tenant fairness engineering
- Backpressure propagation via reactive streams = the system communicates overload
  upstream rather than silently dropping work
- Resilience4j with 0ms timeout = fail-fast philosophy; higher timeouts = throughput
  preference (queue and wait)

**Common false positives:**
- Default Nginx `limit_req` may be copy-pasted security configuration
- API gateway rate limits may be infrastructure defaults, not application design
- Rate limiter imported but only used for a single endpoint

### 7. Storage Engine Tuning

**What to look for:**
- RocksDB `compaction_style`: `kCompactionStyleLevel` (read-optimized, ~10x write
  amplification), `kCompactionStyleUniversal` (write-optimized), `kCompactionStyleFIFO`
  (time-series/TTL data)
- Per-level compression: `compression_per_level=kNoCompression:kNoCompression:kLZ4:kZSTD`
  = hot/cold data tiering
- Bloom filter settings: `filter_policy=bloomfilter:10:false` (~1% false positive at
  10 bits/key), `optimize_filters_for_hits=true` = workload where most lookups find
  existing keys
- Cassandra compaction strategy per table: STCS (write-optimized, default), LCS
  (read-optimized) — different strategies on different tables confirms deliberate tuning
- RocksDB write stall triggers: `level0_slowdown_writes_trigger` and
  `level0_stop_writes_trigger` — wide gaps = tolerance for write slowdowns; tight gaps
  = latency sensitivity
- Connection pool sizing (HikariCP `maximum-pool-size`, `minimum-idle`) — optimal
  formula: `connections ≈ (core_count * 2) + effective_spindle_count`

**What it reveals:**
- Leveled compaction = read latency prioritized over write throughput
- Size-tiered compaction = write throughput prioritized over read latency
- Per-level compression = sophisticated understanding of hot/cold data tiers
- Different compaction strategies per table = deliberate per-workload tuning
- Write stall trigger tuning = the team has experienced and addressed write latency issues
- Separate OLTP and OLAP connection pools = workload-aware database access

**Common false positives:**
- Default STCS in Cassandra may not be deliberate
- `compression=snappy` everywhere may be a framework default
- Large `shared_buffers` in PostgreSQL is often cargo-culted from tuning guides
- Pool of 100+ connections on a 4-core machine is likely over-provisioned

## Cross-Axis Interactions

- **With Consistency:** PACELC — many systems trade consistency for latency even
  without partitions via local reads or async replication
- **With Resilience:** Circuit breakers and timeouts are both latency controls and
  resilience mechanisms. Hedged requests reduce tail latency but increase total load
- **With Data Distribution:** Read-optimized vs write-optimized storage choices
  directly affect latency profiles
- **With Operations:** Observability overhead (tracing, logging) is itself a latency
  cost — sampling rates encode the debuggability-vs-performance tradeoff

## False Positives to Avoid

- A system with no explicit latency tuning may simply be at a scale where defaults
  are adequate — flag as "untuned" not "wrong"
- Copied JVM flags or RocksDB configs from well-known systems without matching the
  workload profile indicate cargo-culting, not deliberate tuning
- Batch processing systems inherently trade latency for throughput — this is expected,
  not a finding
- A single slow endpoint doesn't mean the system is throughput-optimized; it may just
  be a bug
