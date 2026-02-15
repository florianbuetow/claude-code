---
name: info-disclosure
description: >
  This skill should be used when the user asks to "check for information disclosure",
  "analyze data leakage risks", "find data exposure vulnerabilities", or mentions
  "information disclosure" in a security context. Maps to STRIDE category I.
---

# Information Disclosure Analysis

Analyze source code for information disclosure threats where sensitive data leaks to unauthorized parties. Maps to **STRIDE I** -- violations of the **Confidentiality** security property.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full flag specification. This skill supports all cross-cutting flags including `--scope`, `--depth`, `--severity`, `--format`, `--fix`, `--quiet`, and `--explain`.

## Framework Context

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md), specifically the **I - Information Disclosure** section, for the threat model backing this analysis. Key concerns: data breaches, directory traversal, error message leaks, timing attacks, memory dumps, cleartext transmission.

## Workflow

### 1. Determine Scope

Parse flags and resolve the target file list per the flags spec. Filter to files likely handling sensitive data:

- API response builders and serializers
- Error handlers and exception middleware
- Logging configuration and log output
- Database queries returning user data
- Configuration files and environment loaders
- Debug/diagnostic endpoints and health checks
- File-serving routes and static asset configuration
- Frontend templates and server-side rendering
- GraphQL schema definitions and resolvers

### 2. Analyze for Information Disclosure Threats

For each in-scope file, apply the Analysis Checklist below. At `--depth standard`, examine each file for data exposure patterns. At `--depth deep`, trace data flows from database/store through processing to API response to confirm sensitive fields are filtered before transmission across trust boundaries.

### 3. Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) using the `DISC` ID prefix (e.g., `DISC-001`). Set `references.stride` to `"I"` on every finding.

## Analysis Checklist

Work through these questions against the scoped code. Each "yes" may produce a finding.

1. **Verbose error messages** -- Do error responses expose stack traces, database schemas, SQL queries, internal file paths, or library versions to the client? Search for unfiltered exception serialization in error handlers and `catch` blocks. Check if `NODE_ENV=production` or `DEBUG=False` actually suppresses detail.
2. **Excessive API response data** -- Do API endpoints return full database objects instead of explicitly selected fields? Look for `SELECT *`, ORM `.toJSON()`, `serialize()`, or spreading entire model objects into responses without field allowlists. Compare the API response shape against the model definition to identify leaked internal fields (`password_hash`, `internal_id`, `created_by`).
3. **Sensitive data in logs** -- Are passwords, tokens, credit card numbers, SSNs, or PII written to logs? Search for log calls near authentication, payment, or user profile handlers that dump request bodies or sensitive variables. Check if log redaction middleware is configured.
4. **Debug endpoints in production** -- Are debug routes, profiling endpoints, or diagnostic pages accessible without feature flags or environment guards? Look for `/debug`, `/health` with excessive detail, `phpinfo()`, `/actuator`, `/graphiql`, `/__debug__`, `/metrics`, `/_profiler`, Swagger UI without auth.
5. **Directory traversal on reads** -- Can user input control file read paths? Look for `fs.readFile`, `open()`, `file_get_contents` where the path incorporates `req.params`, `request.args`, or URL segments without path canonicalization and containment checks (`realpath` + prefix validation).
6. **Missing encryption for sensitive data** -- Is PII, authentication data, or financial data stored or transmitted in cleartext? Check database schemas for unencrypted sensitive columns, API calls over HTTP instead of HTTPS, and missing field-level encryption on high-sensitivity data.
7. **Hardcoded secrets in source** -- Are API keys, database passwords, encryption keys, or private certificates committed in source files? Search for high-entropy strings assigned to variables named `key`, `secret`, `password`, `token`, `credential`. Check `.env` files, config files, and test fixtures.
8. **HTTP headers leaking info** -- Does the application set `Server`, `X-Powered-By`, `X-AspNet-Version`, or other headers that reveal technology stack details? Check response header configuration and whether helmet/equivalent suppression is applied.
9. **Timing side channels** -- Are operations on secret data (password comparison, token validation, license checks) performed with early-exit logic that leaks information through response time differences? Look for short-circuit `if` statements on secret bytes.
10. **Client-side data exposure** -- Is sensitive data embedded in HTML source, JavaScript bundles, or local storage? Look for server-side rendering that injects user data, API keys, internal URLs, or feature flag values into page templates or `window.__CONFIG__` objects.
11. **Verbose health/status endpoints** -- Do health check or status endpoints expose internal details like database connection strings, dependency versions, internal hostnames, queue sizes, or environment variable dumps? Check `/health`, `/status`, `/info`, `/env` endpoints.
12. **Source map exposure** -- Are JavaScript source maps deployed to production, allowing attackers to read original source code? Check for `.map` files in build output and `sourceMappingURL` references in bundled JavaScript.

## Pragmatism Notes

- Debug mode in development is expected. Only flag `DEBUG=True` or equivalent when it appears in production configuration or when there is no environment gating.
- `SELECT *` is not always a disclosure risk. It depends on whether the full result is serialized to the API response. If application code filters fields before responding, the query itself is not the issue.
- Source maps in production are a trade-off: they improve error reporting but expose source code. Rate this `low` unless the source contains hardcoded secrets or sensitive business logic.
- Technology stack headers (`X-Powered-By`) are low severity on their own but contribute to reconnaissance. They matter more in combination with known vulnerabilities in the disclosed versions.

## What to Look For

Concrete code patterns and grep heuristics to surface information disclosure risks:

- **Stack traces in responses**: `traceback.format_exc()`, `e.stack`, `err.message` sent in HTTP responses, `DEBUG = True` in production config, `app.use(errorHandler)` without production mode filtering. Grep: `(stack|traceback|stackTrace)\b` near response serialization.
- **Full object serialization**: `res.json(user)`, `return JsonResponse(model.__dict__)`, `JSON.stringify(record)` without field selection -- compare against the model definition to see if `password_hash`, `ssn`, `internal_notes` fields leak.
- **Secrets in logs**: `logger.debug(f"token={token}")`, `console.log(req.headers.authorization)`, `log.info("password: " + pwd)`. Grep: `log\w*\.\w+\(.*\b(password|token|secret|key|authorization|ssn|credit.?card)\b`.
- **Path traversal reads**: `open(os.path.join(base, request.args['file']))` without `os.path.realpath` containment, `fs.readFile(req.params.name)` without validation. Grep: `(readFile|open|fopen)\s*\(.*req\.(params|query|body)`.
- **Debug routes**: `/debug/`, `/admin/phpinfo`, `/_profiler`, `/graphiql`, `/swagger`, `/actuator` without auth guards. Grep: `(debug|profiler|phpinfo|actuator|graphiql)` in route definitions.
- **Missing field filtering**: `SELECT * FROM users` returned directly via API, `.find({})` in MongoDB without projection, Sequelize `findAll` without `attributes` restriction. Grep: `SELECT \*|\.find\(\s*\{\s*\}\s*\)|findAll\(\s*\)`.
- **Technology headers**: `X-Powered-By`, `Server: Apache/2.4.51`, `X-AspNet-Version` -- check for `helmet`, `removeHeader`, or equivalent suppression. Grep: `X-Powered-By|x-powered-by|server.*header`.
- **Source maps in production**: `.map` files in build/dist directories, `sourceMappingURL=` in production JS bundles. Grep: `sourceMappingURL|\.js\.map`.

## Output Format

Each finding must conform to [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

```
id:          DISC-<NNN>
severity:    critical | high | medium | low
confidence:  high | medium | low
location:    file, line, function, snippet
description: What data is exposed and through which channel
impact:      What sensitive information an attacker can obtain
fix:         Concrete remediation with diff when possible
references:
  stride: "I"
  cwe:    CWE-200 (Exposure of Sensitive Info), CWE-209 (Error Messages), or relevant CWE
metadata:
  tool:      info-disclosure
  framework: stride
  category:  I
```

### Severity Guidelines for Information Disclosure

| Severity | Criteria |
|----------|----------|
| `critical` | Hardcoded production secrets in source, directory traversal exposing arbitrary files, PII/credentials in API responses |
| `high` | Stack traces with internal paths/queries in production errors, sensitive data in logs, debug endpoints without auth |
| `medium` | Excessive API fields exposing non-critical internal data, technology stack headers, timing side channels |
| `low` | Verbose health check responses, minor information in HTTP headers, source maps in production, client-side comments |

### Common CWE References

| CWE | Description |
|-----|-------------|
| CWE-200 | Exposure of Sensitive Information to Unauthorized Actor |
| CWE-209 | Generation of Error Message Containing Sensitive Info |
| CWE-532 | Insertion of Sensitive Info into Log File |
| CWE-22  | Path Traversal |
| CWE-215 | Insertion of Sensitive Info Into Debugging Code |
| CWE-312 | Cleartext Storage of Sensitive Information |
| CWE-319 | Cleartext Transmission of Sensitive Information |
| CWE-548 | Exposure of Information Through Directory Listing |
