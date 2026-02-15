---
name: access-control
description: >
  This skill should be used when the user asks to "check for access control issues",
  "analyze authorization", "find IDOR vulnerabilities", "audit CORS configuration",
  "check for privilege escalation", or mentions "access control", "authorization",
  "IDOR", "CORS", "JWT tampering", or "directory traversal" in a security context.
  Maps to OWASP Top 10 2021 A01: Broken Access Control.
---

# Broken Access Control (A01:2021)

Analyze source code for broken access control vulnerabilities including missing
authorization checks, insecure direct object references, CORS misconfiguration,
JWT manipulation, directory traversal, and privilege escalation.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks middleware chains
- `--depth deep` traces authorization across call graphs and middleware stacks
- `--severity` filters output (access control issues are often `high` or `critical`)

## Framework Context

Read `../../shared/frameworks/owasp-top10-2021.md`, section **A01:2021 - Broken
Access Control**, for the full category description, common vulnerabilities, and
prevention guidance.

Key CWEs in scope:
- CWE-200: Exposure of Sensitive Information
- CWE-284: Improper Access Control
- CWE-285: Improper Authorization
- CWE-352: Cross-Site Request Forgery
- CWE-639: Authorization Bypass Through User-Controlled Key (IDOR)
- CWE-862: Missing Authorization
- CWE-863: Incorrect Authorization

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain access control logic:

- Route/controller definitions (`**/routes/**`, `**/controllers/**`, `**/handlers/**`)
- Middleware files (`**/middleware/**`, `**/middlewares/**`)
- Authorization modules (`**/auth/**`, `**/authz/**`, `**/policies/**`, `**/guards/**`)
- API endpoint definitions (`**/api/**`, `**/endpoints/**`)
- Configuration files for CORS, JWT, and session management

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` — primary scanner for access control patterns
2. `bandit` — Python-specific authorization issues
3. `brakeman` — Rails mass assignment and authorization bypasses

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting access control:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching access control, authorization, CORS, JWT, and
IDOR patterns. Normalize output to the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **Route inventory**: Grep for route definitions and check each has authorization middleware.
2. **Object access**: Find database lookups using user-supplied IDs and verify ownership checks.
3. **CORS config**: Locate CORS configuration and check for wildcard or overly permissive origins.
4. **JWT handling**: Find JWT verification code and check that claims are validated.
5. **Path handling**: Find file path operations using user input and check for traversal prevention.
6. **Role checks**: Identify role-based decisions and verify they cover both horizontal and vertical access.

When `--depth deep`, additionally trace:
- Full middleware chains from route to handler
- Authorization decorator/annotation inheritance
- Cross-service authorization delegation

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `AC` prefix
(e.g., `AC-001`, `AC-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Impact description specific to the access control failure
- Concrete fix with diff when possible
- CWE and OWASP references

## What to Look For

These are the high-signal patterns specific to broken access control. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **Routes without authorization middleware** — Endpoints that handle sensitive
   data or mutations but have no auth middleware in their chain.

2. **Direct object references without ownership** — Database lookups using
   `req.params.id` or similar without filtering by the authenticated user.

3. **CORS wildcard or reflection** — `Access-Control-Allow-Origin: *` or
   reflecting the `Origin` header without validation, especially with credentials.

4. **JWT claims used without verification** — Reading JWT payload without
   verifying signature, or trusting client-supplied role/permission claims.

5. **Path traversal via user input** — File operations using user-supplied
   paths without canonicalization or allowlist validation.

6. **Missing function-level access control** — Admin endpoints accessible to
   regular users, or API actions without role verification.

7. **Forced browsing to predictable URLs** — Sequential IDs or predictable
   resource paths without authorization checks.

8. **Horizontal privilege escalation** — Users can access other users' data by
   changing an identifier, with no server-side ownership verification.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | IDOR, missing auth middleware, CORS, JWT issues | `semgrep scan --config auto --json --quiet <target>` |
| bandit | Python authorization patterns | `bandit -r <target> -f json -q` |
| brakeman | Rails mass assignment, authorization | `brakeman -q -f json -o /dev/stdout` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find route definitions, database queries with user-controlled IDs, CORS headers,
and JWT decode calls. Report findings with `confidence: medium`.

Relevant semgrep rule categories:
- `python.django.security.audit.unvalidated-*`
- `javascript.express.security.audit.missing-auth-*`
- `java.spring.security.audit.missing-authorization`
- `generic.cors.security.wildcard-origin`

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `AC` (e.g., `AC-001`)
- **metadata.tool**: `access-control`
- **metadata.framework**: `owasp`
- **metadata.category**: `A01`
- **references.owasp**: `A01:2021`
- **references.stride**: `E` (Elevation of Privilege) or `I` (Information Disclosure)

Severity guidance for this category:
- **critical**: Unauthenticated access to admin functions, mass IDOR exposing all user data
- **high**: Authenticated IDOR, missing authorization on mutation endpoints, CORS with credentials + wildcard
- **medium**: CORS misconfiguration without credentials, missing rate limiting on auth endpoints
- **low**: Verbose error messages revealing authorization logic, minor forced browsing risks
