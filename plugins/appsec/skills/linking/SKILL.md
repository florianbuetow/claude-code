---
name: linking
description: >
  This skill should be used when the user asks to "check for linkability",
  "analyze cross-service tracking", "find privacy issues related to user
  correlation", "check for cross-domain tracking", or mentions "linkability"
  in a privacy context. Maps to LINDDUN category L.
---

# Linkability Analysis (LINDDUN L)

Analyze source code for linkability threats where separate data points, actions,
or records can be correlated to the same individual across contexts, services,
or time periods -- even when the system is fully encrypted and authenticated.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Linkability-Specific Behavior |
|------|-------------------------------|
| `--scope` | Default `changed`. Focuses on files containing user identifiers, tracking logic, analytics events, and cross-service communication. |
| `--depth quick` | Grep patterns only: scan for shared IDs, tracking cookies, and fingerprinting code. |
| `--depth standard` | Full code read of scoped files, analyze identifier propagation within each file. |
| `--depth deep` | Trace identifier propagation across services, databases, and API boundaries. Map full correlation graph. |
| `--depth expert` | Deep + adversarial linkage simulation: model what an attacker can correlate given available data. |
| `--severity` | Filter output. Linkability findings range from `medium` to `critical` depending on data sensitivity. |
| `--fix` | Generate pseudonymization and identifier isolation replacements. |

## Framework Context

**LINDDUN L -- Linkability**

Linkability occurs when an adversary can determine that two or more items of
interest (data records, messages, actions, users) are related, even without
knowing the identity of the data subject. Read
[`../../shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) for the
full LINDDUN framework reference including cross-framework mappings and
regulatory context.

**Privacy Property Violated**: Unlinkability

**STRIDE Mapping**: Information Disclosure (linkability extends beyond data
access to correlation analysis across contexts)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: source code, configuration, database schemas,
   API definitions, analytics integrations, and cookie/session management.
4. Prioritize files containing: user ID references, session management,
   analytics event emission, cross-service API calls, database joins across
   user activity tables.

### Step 2 -- Analyze for Linkability Patterns

Read each scoped file and check for patterns that enable cross-context
correlation of user activity:

1. **Identify shared identifiers**: Find user IDs, email addresses, device
   IDs, or tokens that propagate across service boundaries.
2. **Trace identifier scope**: Determine whether identifiers are context-specific
   (scoped to one service) or global (shared across services).
3. **Check analytics events**: Look for events that combine user identity with
   behavioral data.
4. **Examine database schemas**: Look for foreign keys and joins that link user
   activity across tables or services.
5. **Assess cookie and session scope**: Check whether tracking cookies persist
   across domains or contexts.

At `--depth deep` or `--depth expert`, map the full identifier propagation graph
across the codebase and model what correlations an adversary can derive.

### Step 3 -- Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `LINK-NNN` id, title, severity (based on correlation potential
and data sensitivity), location with snippet, description of what can be linked,
impact (profile an adversary can build), fix (pseudonymization or isolation), and
CWE/LINDDUN references.

## Analysis Checklist

1. Do different microservices share the same user ID without pseudonymization?
2. Are there cookies or tokens that persist across different application contexts?
3. Do analytics events combine user identity with detailed behavioral data?
4. Can database tables be joined to correlate user activity across features?
5. Are device fingerprints (user agent, screen resolution, fonts) collected?
6. Do API responses include identifiers that allow cross-endpoint correlation?
7. Are session identifiers rotated, or do they persist across long time periods?
8. Can pseudonymized datasets be re-linked through common timestamps or IPs?

## What to Look For

1. **Global user IDs across services**: `userId`, `user_id`, `accountId` passed
   between microservices without per-service pseudonyms.
   - Grep: `userId|user_id|accountId|account_id` in API call payloads and headers
2. **Cross-domain tracking cookies**: Cookies with broad domain scope or third-party
   cookie setting.
   - Grep: `document\.cookie|Set-Cookie|domain=\.|SameSite=None`
3. **Device fingerprinting**: Collection of browser or device attributes for identification.
   - Grep: `navigator\.userAgent|screen\.width|screen\.height|navigator\.plugins|canvas\.toDataURL|fingerprint`
4. **Analytics with user identity**: Events that include both user ID and behavior.
   - Grep: `analytics\.track|analytics\.identify|gtag\(|mixpanel\.track|segment\.track`
5. **Database joins on user tables**: Queries that correlate user activity across domains.
   - Grep: `JOIN.*user|JOIN.*account|INNER JOIN.*activity|LEFT JOIN.*session`
6. **Persistent identifiers in URLs**: User IDs, email addresses, or tokens in URL paths
   or query parameters that appear in logs and referrer headers.
   - Grep: `req\.params\.userId|req\.query\.email|/users/\$\{|/api/.*userId=`
7. **Log correlation**: Log entries that combine user identity with action metadata.
   - Grep: `logger\.\w+\(.*userId|log\.\w+\(.*user_id|console\.log\(.*email`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Art. 5(1)(c) | Data minimization | Shared identifiers collect more linkable data than necessary |
| GDPR Art. 25 | Data protection by design | Pseudonymization required where feasible |
| GDPR Recital 26 | Identifiability test | Linkable data may constitute personal data |
| CCPA 1798.140(o) | Personal information definition | Includes data capable of being linked to a consumer |
| HIPAA Safe Harbor | De-identification standard | Linked health data is not de-identified |

## Output Format

Use finding ID prefix **LINK** (e.g., `LINK-001`, `LINK-002`).

All findings follow the schema in
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-359` or `CWE-212` as appropriate
- `references.owasp`: `A01:2021` (Broken Access Control -- cross-context leakage)
- `metadata.tool`: `"linking"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"L"`

**Summary table** after all findings:

```
| Linkability Pattern    | Critical | High | Medium | Low |
|------------------------|----------|------|--------|-----|
| Cross-service IDs      |          |      |        |     |
| Tracking cookies       |          |      |        |     |
| Device fingerprinting  |          |      |        |     |
| Analytics correlation  |          |      |        |     |
| Database joins         |          |      |        |     |
| Log correlation        |          |      |        |     |
```

Followed by: top 3 priorities, data flow correlation map, and overall assessment.
