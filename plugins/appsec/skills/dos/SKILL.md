---
name: dos
description: >
  This skill should be used when the user asks to "check for denial of service",
  "analyze availability risks", "find DoS vulnerabilities", or mentions
  "denial of service" or "DoS" in a security context. Maps to STRIDE category D.
---

# Denial of Service Analysis

Analyze source code for denial of service threats where attackers can disrupt or degrade service availability. Maps to **STRIDE D** -- violations of the **Availability** security property.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full flag specification. This skill supports all cross-cutting flags including `--scope`, `--depth`, `--severity`, `--format`, `--fix`, `--quiet`, and `--explain`.

## Framework Context

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md), specifically the **D - Denial of Service** section, for the threat model backing this analysis. Key concerns: resource exhaustion (CPU, memory, disk, network), algorithmic complexity attacks, application crashes, zip bombs.

## Workflow

### 1. Determine Scope

Parse flags and resolve the target file list per the flags spec. Filter to files handling external input processing:

- API endpoints and route handlers (especially public/unauthenticated ones)
- File upload and processing handlers
- Search and query endpoints
- WebSocket handlers and long-lived connections
- Message queue consumers and event processors
- Cron jobs and batch processors
- Middleware configuration (body parsers, rate limiters)
- Regular expressions applied to user input
- Image/video/document processing pipelines

### 2. Analyze for Denial of Service Threats

For each in-scope file, apply the Analysis Checklist below. At `--depth standard`, examine resource consumption patterns in each file. At `--depth deep`, trace input from entry points through processing chains to identify amplification points, unbounded operations, and cascading failure paths.

### 3. Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) using the `DOS` ID prefix (e.g., `DOS-001`). Set `references.stride` to `"D"` on every finding.

## Analysis Checklist

Work through these questions against the scoped code. Each "yes" may produce a finding.

1. **Missing rate limiting** -- Are public-facing endpoints (login, search, signup, API) exposed without rate limiting or throttling middleware? Check route definitions for absence of `rateLimit`, `throttle`, `@rate_limit`, or API gateway quotas. Auth endpoints are especially critical -- brute force attacks are both a spoofing and DoS vector.
2. **Unbounded input size** -- Are request body, file upload, or query parameter sizes unconstrained? Look for missing `bodyParser.json({ limit: })`, absent `MAX_CONTENT_LENGTH`, file upload handlers without size caps, or missing `Content-Length` checks. Multipart form handlers that buffer entire uploads into memory are high risk.
3. **ReDoS patterns** -- Do regular expressions use nested quantifiers or overlapping alternations on user input? Search for regex patterns like `(a+)+`, `(a|a)*`, `(\w+\s*)+`, `(.*a){x}`, or `([a-zA-Z]+)*` applied to request data. These cause exponential backtracking. Test suspicious patterns with a ReDoS analyzer.
4. **Algorithmic complexity** -- Are user inputs fed into operations with super-linear worst-case complexity? Look for nested loops over user-controlled collections, quadratic string building (repeated concatenation in loops), unbounded recursion on user data, or hash collision-prone data structures.
5. **Uncontrolled resource allocation** -- Can user input control how much memory, disk, or CPU is allocated? Look for array/buffer creation sized by request parameters, unbounded `SELECT` without `LIMIT`, pagination without maximum page size, or `new Array(req.query.size)`.
6. **Zip/decompression bombs** -- Are compressed files (zip, gzip, brotli, tar) decompressed without checking the expanded size or compression ratio? Look for `unzip`, `gunzip`, `decompress`, `inflate`, `extractall` calls without size monitoring, ratio limits, or file count caps.
7. **Missing timeouts** -- Are external HTTP calls, database queries, or subprocess executions missing timeout configuration? Look for `requests.get` without `timeout=`, `fetch` without `AbortController`, database connections without `statement_timeout`, `subprocess.run` without `timeout`.
8. **Single point of failure** -- Does the application crash entirely on unhandled exceptions? Check for missing global error handlers, uncaught promise rejections crashing the Node.js process (`unhandledRejection`), or `process.exit` / `os._exit` in error paths that kill the entire service.
9. **Synchronous blocking in async paths** -- Are CPU-intensive or I/O-blocking operations running on the main event loop (Node.js, Python asyncio)? Look for `fs.readFileSync`, `crypto.pbkdf2Sync`, large `JSON.parse`, image processing, or PDF generation on the event loop without worker offloading.
10. **Unbounded fan-out** -- Can a single request trigger an unbounded number of downstream operations (API calls, database queries, notifications, emails)? Look for loops over user-provided arrays that make external calls per element without cardinality limits or batch caps.
11. **GraphQL complexity** -- Do GraphQL endpoints allow deeply nested queries or queries requesting unlimited data? Check for absence of query depth limiting, complexity analysis, or field count restrictions. A single deeply nested query can generate millions of database operations.
12. **Connection/resource exhaustion** -- Can an attacker exhaust connection pools, file descriptors, or thread pools? Look for long-lived connections without idle timeouts, connection pool configuration without max limits, or leaked connections in error paths (missing `finally` blocks that release resources).

## Pragmatism Notes

- Internal-only services behind a VPN or service mesh have lower DoS risk from external attackers. Rate findings lower when the endpoint is not publicly accessible, but note that internal attackers and compromised services can still exploit them.
- Rate limiting at the API gateway level may cover endpoints that lack application-level rate limiting. Check infrastructure configuration before flagging individual routes.
- Synchronous file reads in startup/initialization code (not request handlers) are generally acceptable. Focus `Sync` findings on code paths that execute per-request.
- Missing timeouts on internal service calls within the same datacenter are lower risk than missing timeouts on calls to external third-party APIs. Prioritize external call timeouts.
- ReDoS severity depends on whether the regex runs on user input. A complex regex on server-side constants is not a DoS vector.

## What to Look For

Concrete code patterns and grep heuristics to surface DoS risks:

- **Missing rate limiters**: Public routes without `express-rate-limit`, `@throttle`, `RateLimiter`, `slowapi`, or API gateway throttling config. Grep: route definitions without adjacent rate limiting middleware.
- **Dangerous regex**: Patterns with nested quantifiers: `(.*)+`, `(\w+)+`, `(a|aa)+`, `([a-z]+)*`, `(.+)+$`. Search for `new RegExp(`, `re.compile(`, `/pattern/` applied to user input. Grep: `(RegExp|re\.compile|re\.match|re\.search)\s*\(`.
- **Unbounded queries**: `SELECT * FROM` without `LIMIT`, `.find({})` without `.limit()`, `findAll` without pagination, aggregation pipelines without `$limit`. Grep: `SELECT \*|\.find\(\s*\{|findAll\(\s*\)|aggregate\(`.
- **Missing body limits**: Express without `{ limit: '1mb' }` in bodyParser, Django without `DATA_UPLOAD_MAX_MEMORY_SIZE`, Flask without `MAX_CONTENT_LENGTH`, Spring without `spring.servlet.multipart.max-file-size`. Grep: `bodyParser|json\(\s*\)|urlencoded\(\s*\)` and check for limit configuration.
- **No timeouts**: `requests.get(url)` without `timeout`, `fetch(url)` without `signal: AbortSignal.timeout()`, `pg.query` without `statement_timeout`, `http.get` without timeout. Grep: `(requests\.(get|post)|fetch|axios\.(get|post))\s*\(` without adjacent timeout.
- **Decompression without limits**: `zlib.gunzip`, `zipfile.extractall`, `tar.extractall`, `decompress(` without checking decompressed size or file count. Grep: `(extractall|gunzip|inflate|decompress)\s*\(`.
- **Sync in async context**: `readFileSync`, `execSync`, `crypto.*Sync` in Express handlers or async Python functions. Grep: `Sync\(` in route handler files.
- **Crash-prone patterns**: `JSON.parse(untrustedInput)` without try/catch, missing `process.on('unhandledRejection')`, absent global exception handler. Grep: `JSON\.parse\(` near request data without surrounding try/catch.

## Output Format

Each finding must conform to [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

```
id:          DOS-<NNN>
severity:    critical | high | medium | low
confidence:  high | medium | low
location:    file, line, function, snippet
description: What the DoS vector is and how an attacker can trigger it
impact:      How service availability is affected (crash, slowdown, resource exhaustion)
fix:         Concrete remediation with diff when possible
references:
  stride: "D"
  cwe:    CWE-400 (Uncontrolled Resource Consumption), CWE-1333 (ReDoS), or relevant CWE
metadata:
  tool:      dos
  framework: stride
  category:  D
```

### Severity Guidelines for Denial of Service

| Severity | Criteria |
|----------|----------|
| `critical` | ReDoS on unauthenticated endpoints, zip bomb handling without limits, unbounded memory allocation from user input causing OOM |
| `high` | No rate limiting on auth/search endpoints, missing request body size limits, unbounded database queries, missing global crash handler |
| `medium` | Missing timeouts on external calls, synchronous blocking on event loop, GraphQL without depth limits, connection pool exhaustion |
| `low` | Missing pagination max-page-size, single-threaded processing without worker pool, unbounded fan-out on internal low-volume endpoints |

### Common CWE References

| CWE | Description |
|-----|-------------|
| CWE-400 | Uncontrolled Resource Consumption |
| CWE-1333 | Inefficient Regular Expression Complexity (ReDoS) |
| CWE-770 | Allocation of Resources Without Limits |
| CWE-834 | Excessive Iteration |
| CWE-674 | Uncontrolled Recursion |
| CWE-409 | Improper Handling of Highly Compressed Data |
| CWE-755 | Improper Handling of Exceptional Conditions |
