---
name: data-disclosure
description: >
  This skill should be used when the user asks to "check for personal data
  disclosure", "analyze PII exposure", "find privacy issues related to data
  leakage", "check for unauthorized data sharing", or mentions "disclosure"
  in a privacy context. Maps to LINDDUN category D2. Focuses specifically
  on PERSONAL data disclosure, complementing STRIDE information disclosure.
---

# Disclosure of Information Analysis (LINDDUN D2)

Analyze source code for disclosure threats where personal data is accessible to
unauthorized parties. Focuses specifically on personal and sensitive data rather
than general system information. Covers direct disclosure (data breach vectors)
and indirect disclosure (third-party sharing, over-collection).

## Supported Flags

Read [`shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Disclosure-Specific Behavior |
|------|------------------------------|
| `--scope` | Default `changed`. Focuses on files handling personal data: API handlers, data models, logging, caching, third-party integrations, and error handling. |
| `--depth quick` | Grep patterns only: scan for PII in logs, error messages, and third-party data sharing. |
| `--depth standard` | Full code read, trace personal data flows within each file, check access controls on personal data stores. |
| `--depth deep` | Cross-file personal data flow tracing. Map all paths where PII exits the application boundary. |
| `--depth expert` | Deep + breach simulation: model what personal data is exposed in each attack scenario. |
| `--severity` | Filter output. PII in logs is typically `high`; over-fetching is `medium`. |
| `--fix` | Generate redaction, field-level access control, and data minimization replacements. |

## Framework Context

**LINDDUN D2 -- Disclosure of Information**

Disclosure of information in the LINDDUN context refers specifically to
unauthorized access to personal data. Read
[`shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) for the
full LINDDUN framework reference including the distinction between LINDDUN
disclosure (personal data focus) and STRIDE information disclosure (general
system information).

**Privacy Property Violated**: Confidentiality of Personal Data

**STRIDE Mapping**: Information Disclosure (LINDDUN narrows focus specifically
to personal data rather than general system information)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: API handlers, data models, logging configuration,
   error handling, caching logic, third-party SDK integrations, data export
   endpoints, and serialization logic.
4. Prioritize files containing: user data structures, PII fields, third-party
   API calls with user data, log statements, cache writes, and error responses.

### Step 2 -- Analyze for Personal Data Disclosure

Read each scoped file and assess personal data exposure vectors:

1. **Check logging for PII**: Scan log statements for personal data fields
   (name, email, phone, address, SSN, health data, financial data).
2. **Assess API response data**: Determine whether endpoints return more
   personal fields than the consumer needs (over-fetching).
3. **Examine third-party data sharing**: Identify where personal data flows
   to external services (analytics, advertising, logging, error tracking).
4. **Check error handling**: Look for personal data in error messages, stack
   traces, and debug output.
5. **Evaluate cache and temporary storage**: Determine whether personal data
   in caches, temp files, or browser storage is properly protected.

At `--depth deep` or `--depth expert`, trace all paths where personal data
exits the application boundary and map the full disclosure surface.

### Step 3 -- Report Findings

Output findings per [`shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `DDSCL-NNN` id, title, severity (based on data sensitivity
and exposure scope), location with snippet, description of what personal data is
disclosed and through which channel, impact (unauthorized data access), fix
(redaction, minimization, or encryption), and CWE/LINDDUN references.

## Analysis Checklist

1. Do log statements include personal data (names, emails, phone numbers, addresses)?
2. Are API responses returning full user objects instead of only needed fields?
3. Is personal data sent to third-party analytics or error tracking services?
4. Do error messages or stack traces contain personal data values?
5. Is PII passed through URL query parameters (visible in logs and referrer headers)?
6. Are personal data fields encrypted at rest, or stored in plaintext?
7. Do caching layers store personal data without appropriate TTLs or access controls?
8. Do debug modes expose additional personal data that production would not?

## What to Look For

1. **PII in log statements**: Personal data written to logs, console, or debug output.
   - Grep: `log\.\w+\(.*email|logger\.\w+\(.*password|console\.log\(.*ssn|print\(.*credit.card`
2. **Over-fetched API responses**: Returning complete user objects with unnecessary fields.
   - Grep: `res\.json\(user\)|response\.send\(userData\)|SELECT \*.*FROM.*user|\.toJSON\(\)`
3. **Third-party data sharing**: PII sent to analytics, error tracking, or advertising SDKs.
   - Grep: `Sentry\.captureException.*user|analytics\.track.*email|gtag.*user_id|bugsnag.*user`
4. **PII in error responses**: Personal data leaked through error handling.
   - Grep: `res\.status\(.*\.json\(.*user|catch.*res\.send\(.*err|error.*message.*email`
5. **Personal data in URLs**: PII in query parameters or path segments.
   - Grep: `\?email=|&phone=|/users/\$\{email\}|encodeURIComponent\(.*email\)|queryString.*ssn`
6. **Plaintext PII storage**: Personal data stored without encryption.
   - Grep: `password.*varchar|ssn.*text|credit_card.*string|healthData.*column|plaintext.*pii`
7. **Cache with personal data**: PII stored in cache layers without protection.
   - Grep: `cache\.set\(.*user|redis\.set\(.*email|localStorage\.setItem\(.*token|sessionStorage.*user`
8. **Missing field-level access control**: No column or field restriction on personal data.
   - Grep: `SELECT \*|findAll\(\)|\.find\(\{\}\)|\.aggregate\(\[|include:.*all`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Art. 5(1)(f) | Integrity and confidentiality | Personal data must be protected against unauthorized disclosure |
| GDPR Art. 32 | Security of processing | Appropriate technical measures to protect personal data |
| GDPR Art. 33-34 | Breach notification | Disclosure of personal data triggers 72-hour notification |
| CCPA 1798.100 | Right to know | Consumers must know what personal data is collected and shared |
| CCPA 1798.150 | Private right of action | Data breaches exposing personal data create liability |
| HIPAA 164.312 | Technical safeguards | Protected health information requires access controls and encryption |

## Output Format

Use finding ID prefix **DDSCL** (e.g., `DDSCL-001`, `DDSCL-002`).

All findings follow the schema in
[`shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-200`, `CWE-311`, or `CWE-532` as appropriate
- `references.owasp`: `A01:2021` (Broken Access Control) or `A02:2021` (Cryptographic Failures)
- `metadata.tool`: `"data-disclosure"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"D2"`

**Summary table** after all findings:

```
| Disclosure Pattern           | Critical | High | Medium | Low |
|------------------------------|----------|------|--------|-----|
| PII in logs                  |          |      |        |     |
| Over-fetched API responses   |          |      |        |     |
| Third-party data sharing     |          |      |        |     |
| PII in error messages        |          |      |        |     |
| Personal data in URLs        |          |      |        |     |
| Plaintext PII storage        |          |      |        |     |
| Cache / temp storage leaks   |          |      |        |     |
```

Followed by: top 3 priorities, personal data flow map, and overall assessment.
