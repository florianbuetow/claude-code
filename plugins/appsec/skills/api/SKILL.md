---
name: api
description: >
  This skill should be used when the user asks to "check API security",
  "audit REST API", "find BOLA vulnerabilities", "check for mass assignment",
  "analyze API rate limiting", "detect excessive data exposure", or mentions
  "API security", "BOLA", "IDOR", "mass assignment", "rate limiting",
  "broken function-level authorization", "excessive data exposure", or
  "OWASP API Top 10" in a security context.
---

# API Security (API)

Analyze REST and RPC APIs for security vulnerabilities aligned with the OWASP
API Security Top 10, including Broken Object-Level Authorization (BOLA), mass
assignment, missing rate limiting, broken function-level authorization, and
excessive data exposure. API-specific vulnerabilities arise from the unique
patterns of programmatic access, where client-side UI constraints do not apply.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks API endpoint handlers
- `--depth deep` traces data from request to database to response serialization
- `--severity` filters output (API issues are often `high` or `critical`)

## Framework Context

Key CWEs in scope:
- CWE-639: Authorization Bypass Through User-Controlled Key (BOLA)
- CWE-915: Improperly Controlled Modification of Dynamically-Determined Object Attributes
- CWE-770: Allocation of Resources Without Limits (rate limiting)
- CWE-862: Missing Authorization (function-level auth)
- CWE-200: Exposure of Sensitive Information (excessive data)

OWASP API Security Top 10 (2023) categories:
- API1:2023 Broken Object-Level Authorization
- API2:2023 Broken Authentication
- API3:2023 Broken Object Property-Level Authorization
- API4:2023 Unrestricted Resource Consumption
- API5:2023 Broken Function-Level Authorization

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain API logic:

- Route/endpoint definitions (`**/routes/**`, `**/api/**`, `**/endpoints/**`)
- Controllers and handlers (`**/controllers/**`, `**/handlers/**`, `**/views/**`)
- Serializers and DTOs (`**/serializers/**`, `**/dto/**`, `**/schemas/**`)
- Middleware (`**/middleware/**`, `**/middlewares/**`)
- Rate limiting configuration (`**/config/**`, `**/limiters/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for API patterns
2. `bandit` -- Python API security issues
3. `brakeman` -- Rails API vulnerabilities

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting API security:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching BOLA, mass assignment, authorization, and
data exposure patterns. Normalize output to the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **BOLA audit**: Find API endpoints that accept resource IDs and verify each
   enforces ownership or authorization before returning/modifying data.
2. **Mass assignment**: Find endpoints that accept request bodies and bind them
   directly to models without explicit field allowlisting.
3. **Rate limiting**: Check for rate limiting middleware on authentication
   endpoints, data-intensive endpoints, and mutation endpoints.
4. **Function-level authorization**: Verify admin/privileged endpoints have
   role-based authorization, not just authentication.
5. **Excessive data exposure**: Check API responses for fields that should not
   be exposed (passwords, internal IDs, sensitive user data).

When `--depth deep`, additionally trace:
- Full request-to-response data flow including serialization
- Authorization middleware chains across all API routes
- Rate limiting configuration and bypass scenarios

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `API` prefix
(e.g., `API-001`, `API-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- OWASP API Top 10 reference
- Concrete fix with diff when possible
- CWE references

## What to Look For

These are the high-signal patterns specific to API security. Each maps
to a detection pattern in `references/detection-patterns.md`.

1. **Broken Object-Level Authorization (BOLA)** -- API endpoints accept a
   resource ID from the client and return data without verifying the requesting
   user owns or is authorized to access that resource.

2. **Mass assignment** -- Request body fields are bound directly to database
   model attributes, allowing attackers to set fields they should not control
   (role, price, isAdmin).

3. **Missing rate limiting** -- API endpoints lack rate limiting, allowing
   brute-force attacks on authentication, enumeration, and resource exhaustion.

4. **Broken function-level authorization** -- Admin or privileged API endpoints
   are accessible to regular users because they check authentication but not
   authorization role/permissions.

5. **Excessive data exposure** -- API responses include sensitive fields
   (password hashes, tokens, internal metadata) that the client does not need.

6. **Missing input validation** -- API endpoints accept unbounded inputs
   (no max length, no type validation) enabling injection and resource abuse.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | BOLA, mass assignment, missing auth | `semgrep scan --config auto --json --quiet <target>` |
| bandit | Python API security patterns | `bandit -r <target> -f json -q` |
| brakeman | Rails mass assignment, authorization | `brakeman -q -f json -o /dev/stdout` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find API route definitions, model binding, rate limiting config, and response
serialization. Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `API` (e.g., `API-001`)
- **metadata.tool**: `api`
- **metadata.framework**: `api`
- **metadata.category**: `API`
- **references.api_top10**: `API1:2023`, `API3:2023`, etc.
- **references.cwe**: `CWE-639`, `CWE-915`, `CWE-770`
- **references.stride**: `I` (Information Disclosure) or `E` (Elevation of Privilege)

Severity guidance for this category:
- **critical**: BOLA on sensitive data (financial, medical, PII), mass assignment on role/privilege fields
- **high**: BOLA on user-scoped data, missing auth on admin endpoints, mass assignment on price/status
- **medium**: Missing rate limiting on auth endpoints, excessive data exposure of non-critical fields
- **low**: Minor data over-exposure, rate limit too generous but present
