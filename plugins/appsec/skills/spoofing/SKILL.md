---
name: spoofing
description: >
  This skill should be used when the user asks to "check for spoofing",
  "analyze identity spoofing risks", "find authentication vulnerabilities",
  or mentions "spoofing" in a security context. Maps to STRIDE category S.
---

# Spoofing Identity Analysis

Analyze source code for spoofing threats where attackers can impersonate legitimate users or system components. Maps to **STRIDE S** -- violations of the **Authentication** security property.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full flag specification. This skill supports all cross-cutting flags including `--scope`, `--depth`, `--severity`, `--format`, `--fix`, `--quiet`, and `--explain`.

## Framework Context

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md), specifically the **S - Spoofing Identity** section, for the threat model backing this analysis. Key concerns: credential theft/reuse, session hijacking, token theft, IP spoofing, certificate spoofing.

## Workflow

### 1. Determine Scope

Parse flags and resolve the target file list per the flags spec. Filter to files likely relevant to authentication and identity:

- Route handlers and API controllers with login/register/auth logic
- Authentication middleware and guard functions
- Session management modules and cookie configuration
- Token generation, signing, and validation code
- OAuth/OIDC integration points and callback handlers
- Configuration files containing credential settings or auth parameters
- Password reset and account recovery flows

### 2. Analyze for Spoofing Threats

For each in-scope file, apply the Analysis Checklist below. Read each file fully at `--depth standard` or trace cross-file auth flows at `--depth deep`. Pay special attention to trust boundaries where identity is established or propagated between components.

### 3. Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) using the `SPOOF` ID prefix (e.g., `SPOOF-001`). Set `references.stride` to `"S"` on every finding.

## Analysis Checklist

Work through these questions against the scoped code. Each "yes" may produce a finding.

1. **Plaintext credentials** -- Are passwords, API keys, or tokens stored in plaintext in source, config, or database fields? Search for assignment patterns to variables named `password`, `secret`, `api_key`, `token`. Check database migration files for password columns without encryption or hashing annotations.
2. **Weak hashing** -- Are passwords hashed with MD5, SHA-1, or unsalted SHA-256 instead of bcrypt/scrypt/argon2? Look for `md5(`, `sha1(`, `hashlib.sha256` without salt, `crypto.createHash('md5')`. Check if a work factor / cost parameter is configured for adaptive hashing.
3. **Missing authentication** -- Are there route handlers or API endpoints with no auth middleware applied? Check route definitions for missing `authenticate`, `requireAuth`, `@login_required`, or equivalent guards. Map all routes and flag any that handle sensitive data but lack auth in their middleware chain.
4. **Session fixation** -- Is the session ID regenerated after login? Look for session creation that does not call `regenerate()`, `rotate()`, or equivalent after credential verification. Also check that session cookies use `Secure`, `HttpOnly`, and `SameSite` attributes.
5. **Token validation gaps** -- Are JWTs verified with proper algorithm pinning? Search for `algorithms=["none"]`, missing `verify_signature`, or absent `aud`/`iss` claims checks. Verify that token expiration (`exp`) is enforced and that refresh token rotation is implemented.
6. **Certificate verification disabled** -- Is TLS certificate validation turned off? Look for `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true`, or `CURLOPT_SSL_VERIFYPEER` set to 0. Even in test code, this pattern often leaks to production.
7. **IP-based authentication** -- Is access granted solely based on IP address or `X-Forwarded-For` without additional factors? These headers are trivially spoofable. Check if internal APIs rely on source IP as the only access control.
8. **Credential comparison timing** -- Are secrets compared with `==` instead of constant-time comparison (`hmac.compare_digest`, `crypto.timingSafeEqual`, `ConstantTimeCompare`)? Timing attacks can leak credential bytes progressively.
9. **Default credentials** -- Are there hardcoded default usernames/passwords (e.g., `admin`/`admin`, `test`/`test`) in source or seed data that may ship to production? Check if seed scripts are gated behind environment checks.
10. **OAuth/OIDC misconfig** -- Is the `state` parameter missing from OAuth flows, enabling CSRF? Is the redirect URI validated loosely or with wildcards? Check if the `nonce` claim is verified in OIDC ID tokens.
11. **MFA bypass paths** -- If MFA is implemented, are there code paths that skip the second factor? Look for conditional checks that short-circuit MFA for certain user types, remember-me tokens without expiry, or backup code implementations without rate limiting.
12. **Account enumeration** -- Do login or password-reset endpoints return different responses for valid vs. invalid accounts? Check error messages and HTTP status codes for discrepancies that reveal whether a username exists.

## Pragmatism Notes

- Not every application needs MFA. Evaluate auth requirements proportional to the sensitivity of the data and operations protected.
- Timing attacks on password comparison are real but require network proximity and many requests. Rate them `medium` unless the comparison protects a high-value secret with no rate limiting.
- Test/dev seed data with default credentials is common and acceptable if gated behind environment checks. Only flag if the gate is missing or weak.
- Cookie attribute issues (missing `SameSite`) are defense-in-depth. They matter more when combined with other findings like missing CSRF.

## What to Look For

Concrete code patterns and grep heuristics to surface spoofing risks:

- **Hardcoded secrets**: Strings assigned to variables matching `password|secret|key|token|credential` that contain literal values rather than env/vault references. Grep: `(password|secret|api_key|token)\s*[:=]\s*['"][^'"]{8,}`.
- **Weak hash imports**: `import md5`, `require('md5')`, `from hashlib import sha1`, `crypto.createHash('sha1')`, `MessageDigest.getInstance("MD5")`.
- **Unprotected routes**: Route definitions (`app.get`, `router.post`, `@app.route`, `@GetMapping`) without auth middleware in the chain. Compare against routes that do have auth to identify gaps.
- **Disabled TLS verification**: `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify`, `SSL_VERIFY_NONE`, `CURLOPT_SSL_VERIFYPEER.*0`.
- **JWT algorithm none**: `algorithm.*none`, `alg.*none`, `verify_signature.*false`, `algorithms.*HS256` when RS256 is expected (algorithm confusion). Also `jwt.decode(.*verify=False`.
- **Session handling**: Absence of `session.regenerate`, `req.session.destroy`, or session ID rotation logic near login handlers. Missing cookie flags: `secure`, `httpOnly`, `sameSite`.
- **Timing-unsafe comparison**: Direct `==` or `!=` on token/secret variables without constant-time wrappers. Grep: `(token|secret|key|hash)\s*[!=]=\s*`.
- **Account enumeration signals**: Different error messages at login -- e.g., `"user not found"` vs. `"wrong password"` instead of a uniform `"invalid credentials"` response.

## Output Format

Each finding must conform to [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

```
id:          SPOOF-<NNN>
severity:    critical | high | medium | low
confidence:  high | medium | low
location:    file, line, function, snippet
description: What the spoofing risk is and how it could be exploited
impact:      What an attacker gains by exploiting this
fix:         Concrete remediation with diff when possible
references:
  stride: "S"
  cwe:    CWE-287 (Improper Authentication) or relevant CWE
metadata:
  tool:      spoofing
  framework: stride
  category:  S
```

### Severity Guidelines for Spoofing

| Severity | Criteria |
|----------|----------|
| `critical` | Unauthenticated access to sensitive endpoints, plaintext credential storage, disabled certificate verification in production code |
| `high` | Weak password hashing (MD5/SHA-1), missing session regeneration after login, JWT algorithm confusion allowing forgery |
| `medium` | IP-based auth as sole factor, missing OAuth state parameter, timing-unsafe secret comparison, MFA bypass paths |
| `low` | Default credentials in dev/test seeds, verbose auth error messages revealing user existence, missing SameSite cookie attribute |

### Common CWE References

| CWE | Description |
|-----|-------------|
| CWE-287 | Improper Authentication |
| CWE-256 | Plaintext Storage of a Password |
| CWE-327 | Use of a Broken Crypto Algorithm |
| CWE-384 | Session Fixation |
| CWE-295 | Improper Certificate Validation |
| CWE-346 | Origin Validation Error |
| CWE-798 | Hardcoded Credentials |
| CWE-208 | Observable Timing Discrepancy |
