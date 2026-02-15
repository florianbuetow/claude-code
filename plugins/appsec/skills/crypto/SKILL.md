---
name: crypto
description: >
  This skill should be used when the user asks to "check for cryptographic issues",
  "analyze encryption", "find weak hashing", "audit password storage",
  "check for hardcoded keys", or mentions "cryptography", "encryption",
  "hashing", "TLS", "certificates", or "random number generation" in a security
  context. Maps to OWASP Top 10 2021 A02: Cryptographic Failures.
---

# Cryptographic Failures (A02:2021)

Analyze source code for cryptographic weaknesses including use of broken or weak
algorithms, hardcoded encryption keys, improper password hashing, cleartext
transmission of sensitive data, missing encryption at rest, and insecure random
number generation.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` checks imports, function calls, and configuration values
- `--depth deep` traces key material origin and data flow for sensitive values
- `--severity` filters output (crypto issues range from `low` to `critical`)

## Framework Context

Read `../../shared/frameworks/owasp-top10-2021.md`, section **A02:2021 -
Cryptographic Failures**, for the full category description, common
vulnerabilities, and prevention guidance.

Key CWEs in scope:
- CWE-261: Weak Encoding for Password
- CWE-327: Use of a Broken or Risky Cryptographic Algorithm
- CWE-328: Use of Weak Hash
- CWE-330: Use of Insufficiently Random Values
- CWE-331: Insufficient Entropy
- CWE-338: Use of Cryptographically Weak PRNG
- CWE-759: Use of a One-Way Hash without a Salt
- CWE-760: Use of a One-Way Hash with a Predictable Salt
- CWE-798: Use of Hard-coded Credentials

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain cryptographic operations:

- Crypto/security utility modules (`**/crypto/**`, `**/security/**`, `**/utils/encrypt*`)
- Authentication modules (`**/auth/**`, `**/login/**`, `**/password*`)
- Configuration files (`**/.env*`, `**/config/**`, `**/settings*`)
- Database models with password fields (`**/models/**`)
- TLS/SSL configuration (`**/ssl/**`, `**/tls/**`, `**/certs/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` — primary scanner for crypto pattern detection
2. `bandit` — Python-specific weak crypto detection
3. `gosec` — Go-specific crypto issues
4. `gitleaks` / `trufflehog` — hardcoded keys and secrets

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching cryptographic patterns, weak hashing, hardcoded
keys, and TLS configuration. Normalize output to the findings schema.

If gitleaks is available (for hardcoded key detection):
```
gitleaks detect --source <target> --report-format json --report-path /dev/stdout --no-banner
```

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **Hash algorithm audit**: Grep for MD5, SHA1, SHA-256 (without key) used in
   security contexts (password hashing, token generation, signature verification).
2. **Key management**: Find encryption keys, API secrets, and IVs — check if
   they are hardcoded, loaded from environment, or from a key management service.
3. **Password storage**: Locate password hashing code and verify use of bcrypt,
   argon2, or scrypt with appropriate cost factors.
4. **Random number generation**: Find random value generation and verify
   cryptographically secure sources are used for security-sensitive operations.
5. **TLS configuration**: Check for TLS enforcement, certificate validation,
   and minimum protocol version.
6. **Encryption mode**: Identify block cipher usage and verify ECB mode is not
   used for anything beyond single-block encryption.

When `--depth deep`, additionally trace:
- Where encryption keys originate and how they flow through the application
- Whether sensitive data is encrypted before storage and in transit
- Key rotation mechanisms and lifecycle

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `CRYPT` prefix
(e.g., `CRYPT-001`, `CRYPT-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Impact description specific to the cryptographic weakness
- Concrete fix with diff showing the secure alternative
- CWE and OWASP references

## What to Look For

These are the high-signal patterns specific to cryptographic failures. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **Weak hash algorithms for security** — MD5 or SHA1 used for password
   hashing, token generation, integrity verification, or digital signatures.

2. **Hardcoded encryption keys and IVs** — Symmetric keys, asymmetric private
   keys, or initialization vectors embedded directly in source code.

3. **Insecure random number generation** — `Math.random()`, `rand()`, or
   `random.random()` used for tokens, session IDs, or cryptographic operations.

4. **Password storage without proper hashing** — Passwords stored in plaintext,
   with reversible encryption, or with fast hashes (MD5, SHA-family) instead of
   purpose-built password hashing functions.

5. **ECB mode usage** — Block cipher encryption using ECB mode, which reveals
   patterns in the plaintext.

6. **Missing TLS enforcement** — HTTP used where HTTPS is required, disabled
   certificate validation, or outdated TLS versions allowed.

7. **Insufficient key derivation** — Using encryption keys directly from
   passwords without a proper key derivation function (PBKDF2, HKDF).

8. **Static or predictable IVs/nonces** — Initialization vectors or nonces
   that are hardcoded, reused, or derived from predictable sources.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | Weak crypto, hardcoded keys, insecure random | `semgrep scan --config auto --json --quiet <target>` |
| bandit | Python crypto issues (MD5, DES, hardcoded passwords) | `bandit -r <target> -f json -q` |
| gosec | Go crypto (weak TLS, hardcoded creds) | `gosec -fmt json ./...` |
| gitleaks | Hardcoded keys and secrets | `gitleaks detect --source <target> --report-format json --report-path /dev/stdout --no-banner` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find hash function calls, encryption operations, key assignments, and random
number generation. Report findings with `confidence: medium`.

Relevant semgrep rule categories:
- `python.cryptography.security.insecure-hash-*`
- `python.cryptography.security.insecure-cipher-*`
- `javascript.crypto.security.weak-*`
- `java.crypto.security.weak-*`
- `generic.secrets.security.detected-*`

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `CRYPT` (e.g., `CRYPT-001`)
- **metadata.tool**: `crypto`
- **metadata.framework**: `owasp`
- **metadata.category**: `A02`
- **references.owasp**: `A02:2021`
- **references.stride**: `I` (Information Disclosure) or `T` (Tampering)

Severity guidance for this category:
- **critical**: Plaintext password storage, hardcoded production encryption keys, disabled TLS verification
- **high**: MD5/SHA1 for password hashing, ECB mode on sensitive data, `Math.random()` for tokens
- **medium**: Weak key derivation, outdated TLS versions (TLS 1.0/1.1), missing encryption at rest
- **low**: SHA-256 for password hashing (not broken but not ideal), non-security use of weak hash
