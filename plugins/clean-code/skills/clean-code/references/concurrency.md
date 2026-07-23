# Concurrency — Chapter 13

> Concurrency is a decoupling strategy, and it is hard. Bugs here are rare
> enough to be dismissed as one-offs and non-reproducible enough to survive
> every attempt to find them.

## Core idea

Concurrency defects do not fail the way other defects do. They pass a thousand
test runs, then corrupt data in production under load, then refuse to reproduce.
That asymmetry is why the review bar differs from other dimensions: a *possible*
race is worth reporting even without a reproduction, because the cost of being
right is high and the cost of a look is low.

The chapter's core advice: keep shared data to a minimum, keep synchronized
sections small, and know what your library actually guarantees.

**Owns this dimension:** findings whose fix changes *shared-state access,
coordination, scheduling, or synchronization*. Callback nesting that is merely
hard to read, with no concurrency hazard, is a `functions` finding.

## Violation patterns

### 1. Unsynchronized shared mutable state
**Look for:** a field written by one thread and read by another with no lock,
atomic, or volatile marker; a shared collection mutated from a handler; a
counter incremented from multiple threads; lazy initialisation without
protection.

**Why it costs:** torn reads, lost updates, and stale values that appear only
under load.

**Fix:** confine the data to one thread, make it immutable, or guard every
access with the same lock. Name which.

**Reference:** `Ch.13: Limit the Scope of Data`, `Ch.13: Use Copies of Data`.
**Severity:** HIGH.

### 2. Check-then-act races
**Look for:** `if (!map.containsKey(k)) map.put(k, v)`; check-then-create;
read-modify-write on a shared field; `if (instance == null) instance = new ...`.

**Why it costs:** each operation may be individually thread-safe while the
sequence is not — a very common false sense of safety.

**Fix:** use the atomic compound operation the library provides —
`putIfAbsent`, `computeIfAbsent`, compare-and-swap — or hold a lock across the
whole sequence.

**Reference:** `Ch.13: Beware Dependencies Between Synchronized Methods`.
**Severity:** HIGH.

### 3. Oversized synchronized sections
**Look for:** a lock held across I/O, a network call, or a callback into
unknown code; whole methods marked synchronized when two lines need it.

**Why it costs:** throughput collapses, and calling foreign code under a lock is
a classic deadlock source.

**Fix:** shrink the critical section to the smallest correct region; never call
out to unknown code while holding a lock.

**Reference:** `Ch.13: Keep Synchronized Sections Small`.
**Severity:** MEDIUM, HIGH if foreign code is called under the lock.

### 4. Lock-ordering and deadlock risk
**Look for:** two locks acquired in different orders on different paths; nested
synchronized blocks; a lock held while awaiting a future that needs the same
lock.

**Fix:** impose a global lock order and document it, or restructure to hold one
lock at a time.

**Reference:** `Ch.13: Beware Dependencies Between Synchronized Methods`.
**Severity:** HIGH.

### 5. Assuming thread safety a library does not promise
**Look for:** a non-thread-safe type used as a shared field —
`SimpleDateFormat`, a plain `HashMap`, a mutable builder; a connection or
session object shared across requests; a framework object used outside the
thread that owns it.

**Fix:** use the concurrent variant, or make it thread-local. State which.

**Reference:** `Ch.13: Know Your Library`.
**Severity:** HIGH.

### 6. Concurrency tangled into business logic
**Look for:** threading, locking, and domain rules in the same method; a class
that both computes and manages its own workers.

**Fix:** separate the concurrency mechanism from the logic so each can be
reasoned about and tested alone.

**Reference:** `Ch.13: Threads Should Be as Independent as Possible`.
**Severity:** MEDIUM.

### 7. Ignored shutdown and completion
**Look for:** threads or executors never shut down; fire-and-forget tasks whose
failures vanish; unawaited promises; no handling of interruption or
cancellation; producer/consumer with no termination signal.

**Why it costs:** hangs on exit, silent task failures, and leaked resources.

**Fix:** add explicit shutdown with a timeout; await and handle results.

**Reference:** `Ch.13: Writing Correct Shut-Down Code Is Hard`.
**Severity:** MEDIUM.

### 8. Untestable threaded code
**Look for:** `sleep()` used to sequence a test; no way to inject the executor;
races only reachable through real timing.

**Fix:** inject the executor or scheduler so tests can run deterministically;
treat spurious failures as real defects rather than reruns.

**Reference:** `Ch.13: Testing Threaded Code`.
**Severity:** MEDIUM.

## Do not flag

- **Single-threaded code.** Most application code is. Do not report hypothetical
  races in a CLI script or a request handler touching only locals.
- **JavaScript and Python asyncio single-threaded event loops.** `await` points
  are not data races. Unless `SharedArrayBuffer`, worker threads, or
  multiprocessing are in play, there is no shared-memory hazard.
- **Promise chains and `async`/`await` style.** A `.then()` chain is not a
  concurrency defect. Preferring `async`/`await` is a readability opinion — if
  you report it at all, it is `functions`, and usually it is nothing.
- **Callback nesting.** Deep callbacks are a readability problem. Route to
  `functions` unless there is an actual coordination hazard.
- **Immutable shared data.** No mutation, no race.
- **Framework-managed concurrency.** Actor mailboxes, Go channels used
  idiomatically, request-scoped instances, and `structuredConcurrency` scopes
  are the mechanism working.
- **Thread-confined state.** Locals, thread-locals, and per-request objects are
  not shared.
