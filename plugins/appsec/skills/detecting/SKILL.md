---
name: detecting
description: >
  This skill should be used when the user asks to "check for detectability",
  "analyze timing side channels", "find privacy issues related to traffic
  analysis", "check for metadata leakage", or mentions "detectability" in a
  privacy context. Maps to LINDDUN category D1.
---

# Detectability Analysis (LINDDUN D1)

Analyze source code for detectability threats where an observer can determine
that a user is interacting with a system, that a record exists, or that a
specific action was performed -- even without accessing the content itself. Privacy
is compromised when the mere existence of an interaction or record reveals
sensitive information.

## Supported Flags

Read [`shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Detectability-Specific Behavior |
|------|--------------------------------|
| `--scope` | Default `changed`. Focuses on files containing API handlers, error responses, presence indicators, and encrypted message handling. |
| `--depth quick` | Grep patterns only: scan for enumeration endpoints, timing differences, and presence indicators. |
| `--depth standard` | Full code read, analyze response patterns for information leakage through existence proofs. |
| `--depth deep` | Trace API response behaviors across endpoints. Map enumeration surfaces and timing oracle opportunities. |
| `--depth expert` | Deep + adversarial detectability simulation: model what an observer can infer from response patterns and metadata. |
| `--severity` | Filter output. Severity depends on sensitivity of what can be detected. |
| `--fix` | Generate constant-time responses, uniform error handling, and padding implementations. |

## Framework Context

**LINDDUN D1 -- Detectability**

Detectability occurs when an adversary can determine that an item of interest
exists, even without accessing its content. Read
[`shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) for the
full LINDDUN framework reference including detectability patterns, timing
side channels, and traffic analysis threats.

**Privacy Property Violated**: Undetectability / Unobservability

**STRIDE Mapping**: Information Disclosure (detectability focuses on existence
proofs and metadata patterns rather than direct content access)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: API handlers, error handling middleware, presence
   or status indicators, encrypted message handling, notification systems,
   and cache management.
4. Prioritize files containing: HTTP error responses, user existence checks,
   online status indicators, read receipts, and response timing logic.

### Step 2 -- Analyze for Detectability Patterns

Read each scoped file and assess what an observer can detect about system
usage or data existence:

1. **Check error response uniformity**: Determine whether different error codes
   or messages reveal record existence (e.g., "user not found" vs. "wrong password").
2. **Assess timing consistency**: Look for code paths where response time differs
   based on record existence (cache hit vs. database miss).
3. **Examine presence indicators**: Find online status, typing indicators, read
   receipts, or activity signals that lack opt-out mechanisms.
4. **Check message padding**: Determine whether encrypted messages have uniform
   size or leak content type through size variation.
5. **Evaluate enumeration surfaces**: Identify endpoints that allow probing for
   existence of users, records, or resources.

At `--depth deep` or `--depth expert`, model the full observable surface and
determine what an adversary can infer from response patterns and metadata.

### Step 3 -- Report Findings

Output findings per [`shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `DTCT-NNN` id, title, severity (based on sensitivity of
detectable information and ease of observation), location with snippet, description
of what can be detected and through which channel, impact (what an observer infers),
fix (uniform responses, constant-time ops, or padding), and CWE/LINDDUN references.

## Analysis Checklist

1. Do error responses differentiate "not found" from "access denied" for user lookups?
2. Can an observer enumerate valid usernames, emails, or account IDs?
3. Do response times vary based on whether a record exists (timing oracle)?
4. Are there presence indicators or read receipts without opt-out?
5. Do encrypted messages vary in size, revealing content type or length?
6. Can push notification patterns reveal when a user receives messages?
7. Do API rate limit responses differ for authenticated vs. non-existing users?
8. Can traffic analysis reveal which features or services a user accesses?

## What to Look For

1. **User enumeration via error messages**: Different responses for existing vs. non-existing accounts.
   - Grep: `user not found|invalid username|no such user|email not registered|account does not exist`
2. **Timing oracles**: Early-return patterns that reveal record existence.
   - Grep: `if.*!user.*return|if.*notFound.*return|findOne.*then.*404|catch.*404`
3. **Presence and activity indicators**: Online status, typing, and read receipt systems.
   - Grep: `isOnline|online_status|lastSeen|last_active|typing.*indicator|read.*receipt|seen.*at`
4. **Account enumeration endpoints**: Registration, password reset, or login that reveal existence.
   - Grep: `already registered|email.*taken|username.*exists|account.*already|duplicate.*email`
5. **Unpadded encrypted content**: Variable-length encrypted messages.
   - Grep: `encrypt\(|cipher\.update|AES.*encrypt|padding|PKCS|NoPadding`
6. **Observable API patterns**: Sequential IDs or predictable resource identifiers.
   - Grep: `autoIncrement|SERIAL|sequence|nextval|uuid.*v1|ObjectId`
7. **Notification metadata leakage**: Push notification patterns revealing user behavior.
   - Grep: `sendNotification|pushNotif|FCM|APNs|webpush|notify\(.*user`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Art. 25 | Data protection by design | Systems must prevent unauthorized detection of data existence |
| GDPR Art. 32 | Security of processing | Includes protection against unauthorized disclosure via side channels |
| CCPA 1798.150 | Private right of action | Unauthorized access including inference from observable patterns |
| HIPAA 164.312(e) | Transmission security | Health record existence must not be detectable |
| ePrivacy Directive Art. 5 | Confidentiality of communications | Communication metadata must be protected |

## Output Format

Use finding ID prefix **DTCT** (e.g., `DTCT-001`, `DTCT-002`).

All findings follow the schema in
[`shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-203` (Observable Discrepancy) or `CWE-208` (Observable Timing Discrepancy)
- `references.owasp`: `A05:2021` (Security Misconfiguration -- information leakage in responses)
- `metadata.tool`: `"detecting"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"D1"`

**Summary table** after all findings:

```
| Detectability Pattern       | Critical | High | Medium | Low |
|-----------------------------|----------|------|--------|-----|
| User enumeration            |          |      |        |     |
| Timing side channels        |          |      |        |     |
| Presence indicators         |          |      |        |     |
| Account enumeration         |          |      |        |     |
| Message size leakage        |          |      |        |     |
| Notification patterns       |          |      |        |     |
```

Followed by: top 3 priorities, enumeration surface map, and overall assessment.
