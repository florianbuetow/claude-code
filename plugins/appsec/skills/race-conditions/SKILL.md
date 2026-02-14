---
name: race-conditions
description: >
  This skill should be used when the user asks to "check for race conditions",
  "find TOCTOU bugs", "analyze concurrency issues", "detect double-spend
  vulnerabilities", "check for check-then-act patterns", "find shared state
  bugs", or mentions "race condition", "TOCTOU", "double-spend", "concurrency",
  "atomicity", or "thread safety" in a security context.
---

# Race Conditions (RACE)

Analyze source code for race condition vulnerabilities including time-of-check
to time-of-use (TOCTOU), double-spend, check-then-act without locking, file
system race conditions, shared state across async boundaries, and non-atomic
counter operations. Race conditions are among the hardest bugs to detect through
testing because they depend on timing, making static analysis essential.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks for common race patterns
- `--depth deep` traces shared state across call graphs and async boundaries
- `--severity` filters output (race conditions are often `high` or `critical`)

## Framework Context

Key CWEs in scope:
- CWE-362: Concurrent Execution Using Shared Resource with Improper Synchronization
- CWE-367: Time-of-Check Time-of-Use (TOCTOU) Race Condition
- CWE-820: Missing Synchronization
- CWE-821: Incorrect Synchronization
- CWE-829: Inclusion of Functionality from Untrusted Control Sphere

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain race-prone logic:

- Database transaction handlers (`**/services/**`, `**/handlers/**`, `**/models/**`)
- Payment and financial logic (`**/payments/**`, `**/billing/**`, `**/wallet/**`)
- File system operations (`**/storage/**`, `**/upload/**`, `**/fs/**`)
- Async/concurrent code (`**/workers/**`, `**/tasks/**`, `**/jobs/**`)
- Counter and state management (`**/counters/**`, `**/state/**`, `**/cache/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for concurrency patterns
2. `go vet` -- Go-specific race detection heuristics
3. `bandit` -- Python threading and synchronization issues

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting concurrency:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching race condition, TOCTOU, and concurrency
patterns. Normalize output to the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **Check-then-act audit**: Find patterns where a condition is checked and then
   acted on without atomic guarantees (e.g., check balance then debit).
2. **File TOCTOU**: Find file existence checks followed by file operations
   without locking or atomic alternatives.
3. **Shared state across await**: Identify mutable state read before an await
   point and used after it without re-validation.
4. **Non-atomic counters**: Find counter increments (read-modify-write) without
   locking or atomic operations.
5. **Database transactions**: Verify financial and state-changing operations
   use proper isolation levels and row-level locking.
6. **Async/parallel iteration**: Find shared mutable state accessed in parallel
   loops, goroutines, or thread pools.

When `--depth deep`, additionally trace:
- Full data flow of shared variables across async boundaries
- Database isolation level configuration
- Lock acquisition ordering (deadlock potential)

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `RACE` prefix
(e.g., `RACE-001`, `RACE-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- The race window (what happens between check and act)
- Exploit scenario describing how timing can be abused
- Concrete fix with diff when possible
- CWE references

## What to Look For

These are the high-signal patterns specific to race conditions. Each maps
to a detection pattern in `references/detection-patterns.md`.

1. **TOCTOU in file operations** -- Checking file existence or permissions
   then operating on the file in a separate call.

2. **Double-spend / check-then-debit** -- Reading a balance, comparing it,
   then debiting in separate non-atomic steps.

3. **Check-then-act without lock** -- Any pattern where a condition is checked
   and the result is assumed to hold when the action executes.

4. **Shared state across await** -- Reading mutable state, yielding execution
   (await/yield), then using the stale value.

5. **Non-atomic read-modify-write** -- Counter increments, sequence generators,
   or flag toggles without synchronization.

6. **Missing database transaction isolation** -- Financial operations using
   default (READ COMMITTED) isolation when SERIALIZABLE is needed.

7. **Parallel iteration over shared collection** -- Modifying a shared list,
   map, or set from concurrent goroutines, threads, or async tasks.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | TOCTOU file ops, non-atomic patterns | `semgrep scan --config auto --json --quiet <target>` |
| go vet | Go race condition heuristics | `go vet -race ./...` |
| bandit | Python threading issues | `bandit -r <target> -f json -q` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find check-then-act patterns, file stat calls, counter operations, and
async state access. Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `RACE` (e.g., `RACE-001`)
- **metadata.tool**: `race-conditions`
- **metadata.framework**: `specialized`
- **metadata.category**: `RACE`
- **references.cwe**: `CWE-362`, `CWE-367`
- **references.stride**: `T` (Tampering) or `E` (Elevation of Privilege)

Severity guidance for this category:
- **critical**: Double-spend in financial operations, authentication bypass via race
- **high**: TOCTOU in security-sensitive file operations, check-then-act on authorization
- **medium**: Non-atomic counters affecting business logic, shared state across await
- **low**: Theoretical races with no clear exploit path, cosmetic counter inaccuracies
