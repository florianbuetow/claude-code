---
name: insecure-design
description: >
  This skill should be used when the user asks to "check for design flaws",
  "analyze security design", "find insecure design patterns", "review threat
  model", "check business logic security", "find missing security controls",
  or mentions "insecure design" in a security context. Maps to OWASP Top 10
  2021 A04:2021 - Insecure Design.
---

# Insecure Design Analysis (OWASP A04:2021)

Analyze application architecture and code for missing or ineffective security
controls that result from absent threat modeling, insufficient security
requirements, or failure to use secure design patterns. This is the most
subjective OWASP category -- automated scanners provide minimal coverage, so
Claude's architectural reasoning is the primary value.

## Supported Flags

Read `shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key behaviors:

| Flag | Insecure Design-Specific Behavior |
|------|------------------------------------|
| `--scope` | Default `changed`. Broader scopes (`branch`, `full`) are strongly recommended since design flaws are architectural. |
| `--depth quick` | Check for obvious missing controls (rate limiting, CSRF tokens, security headers). Pattern scan only. |
| `--depth standard` | Full code read of scoped files, analyze request flows and business logic for design gaps. |
| `--depth deep` | Standard + map full request lifecycle, identify trust boundaries, analyze defense-in-depth layering across the codebase. |
| `--depth expert` | Deep + threat model construction, attack tree analysis, DREAD scoring per design flaw. |
| `--severity` | Filter output. Insecure design findings span all severity levels. |
| `--fix` | Generate implementation suggestions for missing controls. |
| `--explain` | Especially useful for this category: adds threat modeling context and design rationale. |

## Framework Context

**OWASP A04:2021 - Insecure Design**

Missing or ineffective security controls as a result of missing threat modeling
during design. Unlike implementation bugs (e.g., SQL injection), insecure design
refers to the absence of security controls that should have been designed in from
the start. No amount of perfect implementation can fix a fundamentally insecure
design.

Key concern areas:

- **Missing threat modeling**: No systematic identification of threats during design
- **Insufficient security requirements**: Security not considered in user stories or specs
- **No secure design patterns**: Missing rate limiting, account lockout, CSRF protection
- **Missing defense in depth**: Single layer of security with no backup controls
- **Business logic security gaps**: Exploitable workflows, race conditions in transactions
- **Trust boundary violations**: Client-side enforcement of server-side rules

**STRIDE Mapping**: All categories (Spoofing, Tampering, Repudiation, Information
Disclosure, Denial of Service, Elevation of Privilege)

## Detection Patterns

Read `references/detection-patterns.md` for the full pattern catalog with
language-specific examples, regex heuristics, and false positive guidance.

**Pattern Summary**:
1. Missing rate limiting on sensitive endpoints
2. No CSRF protection on state-changing operations
3. Missing account lockout after failed authentication attempts
4. Absence of input validation layer
5. No security headers middleware
6. Trust-the-client design patterns (client-side-only validation)

## Workflow

### Step 1: Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. For design analysis, prioritize these file categories:
   - **HTTP handlers/controllers**: Routes, endpoints, API handlers
   - **Authentication flows**: Login, registration, password reset, MFA
   - **Middleware/interceptors**: Request processing pipeline configuration
   - **Configuration files**: Framework config, security settings, CORS setup
   - **Business logic**: Transaction processing, workflows, state machines
   - **Client-side validation**: Form validation, input checking in frontend code
4. If scope is narrow (`file:` or `changed`), warn that design analysis benefits
   from broader scope and suggest `--scope branch` or `--scope full`.

### Step 2: Check for Scanners

Design flaws have minimal scanner coverage. Check for:

| Scanner | Detect | Design Coverage |
|---------|--------|-----------------|
| semgrep | `which semgrep` | Limited: can detect some missing security headers, CSRF patterns |

For this category, Claude analysis is the primary detection method. Scanners
provide supplementary signal at best. Note in output: "Insecure design analysis
is primarily reasoning-based. Scanner coverage for this category is minimal."

### Step 3: Run Scanners

If semgrep is available, run with rules targeting:
- Missing security headers
- CSRF token absence
- Missing rate limiting decorators/middleware

```
semgrep scan --config auto --json --quiet <target>
```

Filter results to design-relevant rules only. Normalize to findings schema.

### Step 4: Claude Analysis

This is the core of insecure design detection. Read scoped files and evaluate:

1. **Map the application architecture**:
   - Identify entry points (routes, API endpoints, event handlers).
   - Identify trust boundaries (client/server, service/service, user/admin).
   - Map the request processing pipeline (middleware, filters, interceptors).
   - Identify business-critical workflows (payments, authentication, authorization).

2. **Evaluate security control presence**:
   - Rate limiting: Are sensitive endpoints (login, registration, password reset,
     API) protected against abuse?
   - CSRF protection: Do state-changing endpoints validate CSRF tokens?
   - Account lockout: Do authentication flows implement lockout or progressive delays?
   - Input validation: Is there a server-side validation layer, or only client-side?
   - Security headers: Is there middleware setting CSP, HSTS, X-Frame-Options, etc.?
   - Error handling: Do errors leak implementation details or stack traces?

3. **Analyze trust boundaries**:
   - Is server-side validation present for everything validated client-side?
   - Are service-to-service calls authenticated and authorized?
   - Are admin functions separated from user functions?
   - Is there proper tenant isolation in multi-tenant systems?

4. **Evaluate defense in depth**:
   - Is there only one layer of security for critical operations?
   - If the primary control fails, what is the fallback?
   - Are security controls applied consistently across all entry points?
   - Are there monitoring and alerting mechanisms for security events?

5. **Assess business logic security**:
   - Can workflows be executed out of order?
   - Are there race conditions in financial or state-changing operations?
   - Can quantity, price, or privilege fields be manipulated client-side?
   - Are there proper idempotency controls on critical operations?

At `--depth deep` or `--depth expert`, construct a lightweight threat model:
- List identified assets, threat actors, and attack surfaces.
- Map missing controls to specific threat scenarios.
- Evaluate the overall security posture against the STRIDE model.

### Step 5: Report

Output findings using the format from `shared/schemas/findings.md`.

Each finding must include:
- **id**: `DESGN-001`, `DESGN-002`, etc.
- **title**: Concise description of the missing control or design flaw.
- **severity**: Based on exploitability and business impact of the missing control.
- **location**: File(s), line range(s), and architectural component affected.
- **description**: What control is missing and why it matters.
- **impact**: What an attacker can achieve due to the design gap.
- **fix**: Implementation approach for the missing control, with code sketch.
- **references**: CWE, OWASP A04:2021, STRIDE mapping.

Because design findings are inherently more subjective than implementation bugs,
include clear reasoning for each finding. Explain why the control is expected and
what threat it mitigates. Use `confidence: medium` for most design findings unless
the absence is unambiguous (e.g., zero rate limiting on a public login endpoint).

## What to Look For

These are the primary insecure design patterns to detect. Each has detailed
examples and heuristics in `references/detection-patterns.md`.

1. **Missing rate limiting**: Login, registration, password reset, OTP verification,
   API endpoints with no throttling or abuse prevention.
2. **No CSRF protection**: State-changing POST/PUT/DELETE endpoints without
   CSRF token validation.
3. **Missing account lockout**: Authentication systems that allow unlimited
   login attempts with no lockout, delay, or CAPTCHA.
4. **No server-side validation**: Input validation only in client-side JavaScript
   with no corresponding server-side checks.
5. **Missing security headers**: No Content-Security-Policy, Strict-Transport-Security,
   X-Content-Type-Options, X-Frame-Options, or Referrer-Policy headers.
6. **Client-side trust**: Price calculations, authorization decisions, or business
   rules enforced only in client-side code.
7. **No defense in depth**: Single authentication check with no session validation,
   or single authorization layer with no audit trail.
8. **Missing error handling strategy**: Inconsistent error responses that leak
   internal state, stack traces, or database details.
9. **No idempotency controls**: Financial or state-changing operations that can
   be replayed or executed concurrently without protection.
10. **Missing tenant isolation**: Multi-tenant systems without proper data
    segregation at the query or middleware level.

## Scanner Integration

**Primary**: Claude reasoning-based analysis (scanners provide minimal coverage
for design flaws).
**Supplementary**: semgrep (limited rules for missing headers, CSRF patterns).
**Fallback**: Grep regex patterns from `references/detection-patterns.md`.

This category relies primarily on Claude's ability to:
- Understand application architecture by reading code.
- Identify missing controls by reasoning about what should be present.
- Evaluate trust boundaries and defense-in-depth layering.
- Assess business logic for exploitable design patterns.

Scanner findings for this category should be treated as supplementary evidence,
not primary detection. Report scanner status but emphasize that design analysis
is reasoning-based.

## Output Format

Use finding ID prefix **DESGN** (e.g., `DESGN-001`, `DESGN-002`).

All findings follow the schema in `shared/schemas/findings.md` with:
- `references.owasp`: `"A04:2021"`
- `references.stride`: One or more of `"S"`, `"T"`, `"R"`, `"I"`, `"D"`, `"E"`
- `metadata.tool`: `"insecure-design"`
- `metadata.framework`: `"owasp"`
- `metadata.category`: `"A04"`

**CWE Mapping by Design Flaw Type**:

| Design Flaw | CWE | Typical Severity |
|------------|-----|-----------------|
| Missing rate limiting | CWE-770 | high |
| No CSRF protection | CWE-352 | high |
| Missing account lockout | CWE-307 | high |
| Client-side-only validation | CWE-602 | high |
| Missing security headers | CWE-693 | medium |
| No defense in depth | CWE-657 | medium |
| Business logic flaws | CWE-840 | high |
| Missing tenant isolation | CWE-284 | critical |
| No idempotency controls | CWE-362 | medium |

### Summary Table

After all findings, output a summary:

```
| Design Flaw Category   | Critical | High | Medium | Low |
|------------------------|----------|------|--------|-----|
| Rate Limiting          |          |      |        |     |
| CSRF Protection        |          |      |        |     |
| Account Security       |          |      |        |     |
| Input Validation       |          |      |        |     |
| Security Headers       |          |      |        |     |
| Trust Boundaries       |          |      |        |     |
| Defense in Depth       |          |      |        |     |
| Business Logic         |          |      |        |     |
```

Followed by: top 3 priorities, threat model observations (at `--depth deep`+),
and overall design security assessment.
