---
name: auth
description: >
  This skill should be used when the user asks to "check for authentication issues",
  "analyze auth", "find credential vulnerabilities", "review login security",
  "check session management", or mentions "authentication", "passwords", "MFA",
  "sessions", or "brute force" in a security context. Maps to OWASP Top 10 2021
  A07: Identification and Authentication Failures.
---

# Identification and Authentication Failures

Analyze source code for authentication and session management vulnerabilities. Detect
weak credential handling, missing brute force protections, insecure session management,
and absent multi-factor authentication. Produce actionable findings with severity
ratings, code locations, and concrete remediation steps.

## Supported Flags

All flags from `shared/schemas/flags.md` are supported:

| Flag | Relevant Behavior |
|------|-------------------|
| `--scope <value>` | Determines which files to analyze (default: `changed`) |
| `--depth <value>` | `quick`: pattern scan only. `standard`: full read + analysis. `deep`: trace auth flows cross-file. `expert`: red team simulation with DREAD scoring |
| `--severity <value>` | Filter findings by minimum severity |
| `--format <value>` | Output format: `text`, `json`, `sarif`, `md` |
| `--fix` | Chain into remediation after analysis |
| `--quiet` | Findings only, no explanations |
| `--explain` | Add learning context to each finding |

## Framework Context

**OWASP Top 10 2021 - A07: Identification and Authentication Failures**

Confirmation of the user's identity, authentication, and session management is critical
to protect against authentication-related attacks. Applications are vulnerable when they:

- Permit automated attacks such as credential stuffing or brute force
- Permit default, weak, or well-known passwords
- Use weak credential recovery processes (e.g., knowledge-based answers)
- Store passwords in plain text, encrypted, or with weak hashes (MD5, SHA1)
- Lack or have ineffective multi-factor authentication
- Expose session identifiers in URLs
- Reuse session identifiers after successful login
- Fail to properly invalidate sessions on logout or timeout

**STRIDE Mapping**: Spoofing, Repudiation

**CWE References**: CWE-287 (Improper Authentication), CWE-384 (Session Fixation),
CWE-307 (Brute Force), CWE-521 (Weak Password Requirements), CWE-916 (Weak Password Hash),
CWE-613 (Insufficient Session Expiration), CWE-308 (Missing MFA)

## Detection Patterns

Read [`references/detection-patterns.md`](references/detection-patterns.md) before
performing analysis. It contains detailed Grep heuristics, language-specific code
examples, scanner coverage, and false positive guidance for each vulnerability pattern.

## Workflow

### 1. Determine Scope

Parse `--scope` flag and resolve to a concrete file list:

1. Apply scope resolution per `shared/schemas/flags.md`.
2. Filter to files relevant to authentication:
   - Route handlers, middleware, and controllers (login, register, password reset endpoints)
   - Authentication modules and services
   - Session configuration files
   - Password hashing and validation utilities
   - JWT/token generation and validation code
   - OAuth/OIDC integration code
   - Configuration files (session timeout, password policy settings)
3. Include framework-specific auth files (e.g., `passport.js` configs, Django `auth` backends,
   Spring Security configs, Go `auth` middleware).

### 2. Check for Scanners

Detect available scanners in order of preference:

| Scanner | Detect | Relevant Rules |
|---------|--------|----------------|
| semgrep | `which semgrep` | Auth bypass, weak hashing, JWT issues, session management |
| bandit | `which bandit` | Hardcoded passwords, weak hashes (Python) |
| gosec | `which gosec` | Hardcoded credentials, weak crypto (Go) |
| gitleaks | `which gitleaks` | Hardcoded secrets, API keys, passwords in code |

If no scanner is available, proceed with Claude analysis using Grep patterns from
`references/detection-patterns.md`. Note in output: "No scanner available -- findings
based on code pattern analysis only."

### 3. Run Scanners

For each available scanner:

1. Execute against the scoped file list.
2. Parse JSON output.
3. Filter to authentication-related rules only.
4. Normalize findings to the schema in `shared/schemas/findings.md`.
5. Set `scanner.confirmed: true` for scanner-detected findings.

### 4. Claude Analysis

Regardless of scanner availability, perform manual code analysis:

1. Read `references/detection-patterns.md` for the full pattern catalog.
2. Use Grep with the regex patterns to locate suspicious constructs.
3. Read surrounding code context (30-50 lines) to assess each match.
4. Trace authentication flows from entry point to credential validation.
5. At `--depth deep` or higher: follow imports, trace session lifecycle, map the
   complete auth flow across files.
6. Deduplicate against scanner findings (same file + line = same finding).
7. Set `confidence: medium` for Claude-only findings, `confidence: high` when
   confirmed by a scanner.

### 5. Report Findings

Format output per `--format` flag. Each finding uses the schema from
`shared/schemas/findings.md` with these specifics:

- **ID prefix**: `AUTH` (e.g., `AUTH-001`, `AUTH-002`)
- **references.owasp**: `A07:2021`
- **references.stride**: `S` (Spoofing) or `R` (Repudiation)
- **metadata.tool**: `auth`
- **metadata.framework**: `owasp`
- **metadata.category**: `A07`

**Summary block** (appended after all findings):

```
## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |

**Scanners used**: [list or "none"]
**Scanners missing**: [list of recommended but unavailable]
**Top priorities**: [top 3 findings to fix first and why]
```

## What to Look For

These are the primary vulnerability patterns. See `references/detection-patterns.md`
for detailed regex patterns and code examples.

1. **Missing rate limiting on login** -- No throttling, delay, or account lockout on
   authentication endpoints, enabling brute force and credential stuffing.
2. **Weak password validation** -- No complexity requirements, missing minimum length
   checks, or no check against common password lists.
3. **Plaintext or weakly hashed passwords** -- Passwords stored with MD5, SHA1, plain
   SHA256, or without salting. Must use Argon2, bcrypt, or scrypt.
4. **Session ID in URL parameters** -- Session tokens passed via query strings, visible
   in logs, referrer headers, and browser history.
5. **Missing session regeneration after login** -- Same session ID used before and after
   authentication, enabling session fixation attacks.
6. **JWT with none algorithm accepted** -- JWT verification allows `alg: "none"`, letting
   attackers forge unsigned tokens.
7. **Hardcoded JWT secrets** -- Signing keys embedded in source code rather than loaded
   from environment or secrets management.
8. **Missing or ineffective MFA** -- No multi-factor authentication on sensitive
   operations, or MFA that can be bypassed.
9. **Insufficient session invalidation** -- Sessions not destroyed on logout, or no
   server-side session expiration/timeout.

## Scanner Integration

Refer to `shared/schemas/scanners.md` for full scanner details.

**Primary**: semgrep (broad auth rule coverage across languages)
**Secondary**: bandit (Python), gosec (Go), gitleaks (hardcoded credentials)
**Fallback**: Grep-based pattern matching from `references/detection-patterns.md`

When running as a subagent of the OWASP dispatcher, receive scope and flags from the
parent agent prompt. Do not re-parse user input.

## Output Format

All findings conform to the schema defined in `shared/schemas/findings.md`.

**ID prefix**: `AUTH` (registered in the ID Prefix Registry as OWASP A07)

Example finding:

```json
{
  "id": "AUTH-001",
  "title": "Passwords hashed with MD5 in user registration",
  "severity": "critical",
  "confidence": "high",
  "location": {
    "file": "src/auth/register.py",
    "line": 34,
    "function": "create_user",
    "snippet": "password_hash = hashlib.md5(password.encode()).hexdigest()"
  },
  "description": "User passwords are hashed with MD5, which is cryptographically broken and trivially reversible with rainbow tables or GPU cracking.",
  "impact": "An attacker with database access can recover all user passwords within minutes, enabling account takeover across the application and any services where users reuse passwords.",
  "fix": {
    "summary": "Replace MD5 with bcrypt or Argon2id",
    "diff": "- password_hash = hashlib.md5(password.encode()).hexdigest()\n+ password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())"
  },
  "references": {
    "cwe": "CWE-916",
    "owasp": "A07:2021",
    "stride": "S"
  },
  "metadata": {
    "tool": "auth",
    "framework": "owasp",
    "category": "A07"
  }
}
```
