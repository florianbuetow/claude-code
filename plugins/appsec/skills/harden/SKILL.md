---
name: harden
description: >
  This skill should be used when the user asks to "harden code", "security
  hardening", "improve security posture", "add security headers", "tighten
  security", "defensive coding suggestions", or "proactive security
  improvements". Also triggers when the user asks about CSP, CORS
  hardening, rate limiting, input validation improvements, security
  logging, or defense-in-depth measures.
---

# Security Hardening

Proactive security improvement suggestions. Unlike vulnerability scanners
that find what is broken, this skill identifies what could be better --
defense-in-depth measures, missing security headers, insufficient input
validation, absent rate limiting, and other hardening opportunities that
reduce the blast radius of future vulnerabilities.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Hardening Behavior |
|------|-------------------|
| `--scope` | Default `changed`. Use `full` for comprehensive hardening review. |
| `--depth quick` | Check for missing security headers and obvious hardening gaps only. |
| `--depth standard` | Full hardening review: headers, validation, logging, error handling, configuration. |
| `--depth deep` | Standard + analyze middleware chains, review all trust boundaries, check defense layering. |
| `--depth expert` | Deep + compare against security benchmarks (CIS, OWASP ASVS), generate hardening scorecard. |
| `--severity` | Filter suggestions by impact level. |
| `--format` | Default `text`. Use `md` for a hardening checklist document. |

## Workflow

### Step 1: Identify Technology Stack

Scan the codebase to determine:

1. **Web framework(s)**: Express, Django, Flask, Spring, Rails, Next.js, ASP.NET, FastAPI, etc.
2. **Deployment target**: Container, serverless, VM, PaaS (from Dockerfile, serverless.yml, etc.).
3. **Reverse proxy/CDN**: Nginx, Apache, Cloudflare, AWS ALB (from config files).
4. **Database(s)**: SQL, NoSQL, cache layers.
5. **Authentication mechanism**: Session, JWT, OAuth, SAML.
6. **Existing security middleware**: Helmet, django-security, Spring Security, etc.

### Step 2: Check Security Headers

Verify the application sets these HTTP response headers (or that a reverse proxy / CDN handles them):

| Header | Recommended Value | Impact |
|--------|------------------|--------|
| `Content-Security-Policy` | Strict policy, no `unsafe-inline` / `unsafe-eval` | Mitigates XSS |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Enforces HTTPS |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME sniffing |
| `X-Frame-Options` | `DENY` or `SAMEORIGIN` | Prevents clickjacking |
| `Referrer-Policy` | `strict-origin-when-cross-origin` or stricter | Limits referrer leakage |
| `Permissions-Policy` | Disable unused browser features | Reduces attack surface |
| `Cross-Origin-Opener-Policy` | `same-origin` | Prevents cross-origin attacks |
| `Cross-Origin-Resource-Policy` | `same-origin` | Controls resource sharing |
| `Cache-Control` | `no-store` for sensitive responses | Prevents cache leaks |

Note: If a reverse proxy config (nginx.conf, etc.) is present and sets these headers, do not flag them as missing from application code.

### Step 3: Review CORS Configuration

Check for overly permissive CORS settings:

1. `Access-Control-Allow-Origin: *` on authenticated endpoints.
2. Reflecting the `Origin` header without validation.
3. `Access-Control-Allow-Credentials: true` with wildcard origins.
4. Overly broad allowed methods or headers.
5. Missing `Vary: Origin` when origin is dynamic.

### Step 4: Assess Input Validation

For each entry point discovered (or in scope):

1. **Schema validation**: Are request bodies validated against a schema (Joi, Zod, Pydantic, JSON Schema)?
2. **Type coercion**: Are string inputs properly typed before use?
3. **Length limits**: Are string lengths bounded? Are array sizes limited?
4. **Allowlist vs denylist**: Is validation positive (allowlist) rather than negative (denylist)?
5. **Nested input**: Are deeply nested objects limited to prevent DoS?
6. **File validation**: Are uploaded files validated beyond extension (magic bytes, size limits)?

### Step 5: Check Rate Limiting

Identify endpoints that should have rate limiting:

1. **Authentication endpoints**: Login, registration, password reset, MFA verification.
2. **API endpoints**: Especially those that are computationally expensive or return sensitive data.
3. **File upload endpoints**: To prevent storage exhaustion.
4. **Search/query endpoints**: To prevent enumeration and DoS.

Check if rate limiting is implemented and whether limits are reasonable.

### Step 6: Review Error Handling and Information Disclosure

1. **Stack traces**: Are stack traces exposed in production error responses?
2. **Verbose errors**: Do error messages reveal internal paths, versions, or database details?
3. **Error differentiation**: Do auth errors distinguish between "user not found" and "wrong password" (enables enumeration)?
4. **Default error pages**: Are framework default error pages replaced?
5. **Debug mode**: Is debug mode disabled in production configuration?

### Step 7: Assess Security Logging

Check that these security-relevant events are logged:

1. **Authentication events**: Login success/failure, logout, password changes.
2. **Authorization failures**: Access denied events with user and resource context.
3. **Input validation failures**: Rejected requests with sanitized details.
4. **Administrative actions**: Config changes, user management, privilege changes.
5. **Sensitive data access**: Audit trail for PII/financial data reads.

Verify logs do NOT contain: passwords, tokens, credit card numbers, SSNs, or other sensitive data.

### Step 8: Check Defensive Coding Patterns

1. **Fail-closed defaults**: Do authorization checks default to deny?
2. **Secure defaults**: Are new configurations secure by default?
3. **Least privilege**: Do database connections, API keys, and service accounts use minimal permissions?
4. **Timeout configuration**: Do HTTP clients, database connections, and external calls have timeouts?
5. **Resource limits**: Are memory/CPU-intensive operations bounded?
6. **Dependency security**: Is `npm audit` / `pip audit` / equivalent run in CI?

### Step 9: Report

Output hardening suggestions grouped by category.

## Output Format

Hardening suggestions are advisory and use a lighter format than vulnerability findings.

```
## Security Hardening Report

### Summary
- Hardening suggestions: N
- By priority: N HIGH, N MEDIUM, N LOW
- Categories covered: headers, cors, validation, rate-limiting, logging, error-handling, config

### HIGH Priority

#### [H-001] Missing Content-Security-Policy header
**Category**: Headers | **Effort**: Low
**Location**: src/middleware/security.ts
**Current**: No CSP header set
**Recommended**: Add strict CSP via helmet
```js
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:"],
  }
}));
```

### MEDIUM Priority
...

### LOW Priority
...
```

When hardening gaps represent actual vulnerabilities (e.g., CORS misconfiguration allowing credential theft), emit a formal finding using `../../shared/schemas/findings.md`.

Finding ID prefix: **HARD** (e.g., `HARD-001`).

- `metadata.tool`: `"harden"`
- `references.cwe`: Varies by suggestion (e.g., `CWE-693` Protection Mechanism Failure, `CWE-16` Configuration)

## Pragmatism Notes

- Hardening is contextual. An internal admin tool has different requirements than a public API.
- Do not recommend CSP for a CLI tool or rate limiting for a batch job.
- If a CDN or reverse proxy handles headers, note that rather than flagging missing headers in app code.
- Prioritize suggestions that are easy to implement with high security impact.
- Acknowledge when existing security measures are already good. Not every review needs findings.
- Some frameworks (Next.js, Rails) include secure defaults. Credit what is already done well.
