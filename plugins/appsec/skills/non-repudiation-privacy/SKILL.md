---
name: non-repudiation-privacy
description: >
  This skill should be used when the user asks to "check for non-repudiation
  privacy risks", "analyze excessive audit logging", "find privacy issues
  related to accountability", "check for forced identity linking", or mentions
  "non-repudiation" in a privacy context. Maps to LINDDUN category N. This is
  the INVERSE of STRIDE repudiation -- here too much proof is the threat.
---

# Non-Repudiation Privacy Analysis (LINDDUN N)

Analyze source code for non-repudiation threats where forced accountability
creates privacy risks. In privacy, non-repudiation becomes a threat when it
creates irrefutable proof linking users to sensitive activities where plausible
deniability should be preserved. This is the inverse of STRIDE Repudiation.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Non-Repudiation-Specific Behavior |
|------|-----------------------------------|
| `--scope` | Default `changed`. Focuses on files containing audit logging, digital signatures, transaction receipts, and immutable record storage. |
| `--depth quick` | Grep patterns only: scan for comprehensive audit logging and signature mechanisms. |
| `--depth standard` | Full code read, classify logged actions by sensitivity, assess deniability gaps. |
| `--depth deep` | Trace audit trail coverage across the system. Map which sensitive actions create irrefutable evidence. |
| `--depth expert` | Deep + adversarial subpoena simulation: model what a legal adversary can prove from system records. |
| `--severity` | Filter output. Severity depends on sensitivity of the activity being irrefutably logged. |
| `--fix` | Generate selective logging, retention limits, and anonymous channel implementations. |

## Framework Context

**LINDDUN N -- Non-repudiation (Privacy Context)**

Non-repudiation in a privacy context occurs when the system creates irrefutable
proof that a specific user performed a sensitive action, in situations where
plausible deniability should be available. Read
[`../../shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) for the
full LINDDUN framework reference including the relationship between LINDDUN N
and STRIDE R.

**Privacy Property Violated**: Plausible Deniability

**STRIDE Mapping**: Repudiation (inverse relationship -- STRIDE treats
deniability as a security threat; LINDDUN treats forced accountability as a
privacy threat)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: audit logging modules, transaction logging,
   digital signature implementations, blockchain integrations, session
   recording, and compliance audit code.
4. Prioritize files containing: audit trail logic, activity logging, digital
   signature verification, immutable storage writes, and user action recording.

### Step 2 -- Analyze for Non-Repudiation Privacy Threats

Read each scoped file and assess whether accountability mechanisms create
privacy risks:

1. **Classify logged actions by sensitivity**: Distinguish routine actions
   (login, purchase) from sensitive ones (health queries, political content,
   whistleblowing, personal searches).
2. **Check audit granularity**: Determine whether logging is applied uniformly
   or selectively based on sensitivity classification.
3. **Assess digital signature scope**: Identify where signatures create
   irrefutable proof of user involvement in sensitive activities.
4. **Examine retention policies**: Check whether audit logs of sensitive
   actions have appropriate retention limits or persist indefinitely.
5. **Look for anonymous alternatives**: Check whether sensitive features
   allow pseudonymous or anonymous participation.

At `--depth deep` or `--depth expert`, model the full audit trail and determine
what a legal adversary or data breach could reveal about user behavior.

### Step 3 -- Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `NREP-NNN` id, title, severity (based on activity sensitivity
and irrefutability of proof), location with snippet, description of evidence
created, impact (what can be proven if logs are subpoenaed), fix (selective
logging, retention limits, or anonymous channels), and CWE/LINDDUN references.

## Analysis Checklist

1. Does the system log every user action regardless of sensitivity classification?
2. Are sensitive queries (health, legal, political) logged with user identity?
3. Do digital signatures create irrefutable proof of user involvement in sensitive actions?
4. Are there features (whistleblowing, reporting) that require real identity?
5. Can audit logs be subpoenaed to prove user behavior in sensitive contexts?
6. Do immutable storage systems (blockchain, append-only logs) prevent erasure?
7. Are there retention policies limiting how long sensitive action logs persist?
8. Is there a sensitivity classification for routine vs. sensitive actions?

## What to Look For

1. **Blanket audit logging**: All actions logged without sensitivity classification.
   - Grep: `audit\.log|auditLog|audit_trail|AuditEvent|createAuditEntry|logActivity`
2. **User identity in sensitive action logs**: User IDs linked to sensitive operations.
   - Grep: `log.*userId.*search|audit.*user.*query|record.*identity.*action`
3. **Digital signatures on all transactions**: Signatures applied without privacy assessment.
   - Grep: `sign\(|createSignature|digitalSignature|crypto\.sign|jwt\.sign.*action`
4. **Immutable storage of user actions**: Append-only or blockchain storage linking users to actions.
   - Grep: `blockchain|immutable|append.only|ledger|write.*once|WORM`
5. **Session recording with identity**: Full session capture linked to identified users.
   - Grep: `sessionRecording|screenCapture|fullStory|hotjar|mouseflow|session.replay`
6. **Missing anonymous channels**: No pseudonymous alternatives for sensitive features.
   - Grep: `anonymous|pseudonym|whistleblow|report.*anonymous|tipline`
7. **Indefinite retention of action logs**: No TTL or cleanup for sensitive audit records.
   - Grep: `retention|ttl|cleanup|purge|expire.*audit|delete.*log.*older`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Art. 17 | Right to erasure | Irrefutable audit trails may conflict with deletion rights |
| GDPR Art. 5(1)(e) | Storage limitation | Indefinite audit logs violate storage limitation principle |
| GDPR Art. 5(1)(c) | Data minimization | Excessive logging collects more data than necessary |
| EU Directive 2019/1937 | Whistleblower protection | Anonymous reporting channels must protect identity |
| HIPAA Privacy Rule | Minimum necessary standard | Access logs should record minimum necessary detail |
| CCPA 1798.105 | Right to delete | Users may request deletion of activity records |

## Output Format

Use finding ID prefix **NREP** (e.g., `NREP-001`, `NREP-002`).

All findings follow the schema in
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-779` (Logging of Excessive Data)
- `references.owasp`: `A09:2021` (Security Logging & Monitoring Failures -- excessive audit trail)
- `metadata.tool`: `"non-repudiation-privacy"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"N"`

**Summary table** after all findings:

```
| Non-Repudiation Pattern     | Critical | High | Medium | Low |
|-----------------------------|----------|------|--------|-----|
| Blanket audit logging       |          |      |        |     |
| Identity in sensitive logs  |          |      |        |     |
| Mandatory signatures        |          |      |        |     |
| Immutable action records    |          |      |        |     |
| Session recording           |          |      |        |     |
| Missing anonymous channels  |          |      |        |     |
```

Followed by: top 3 priorities, sensitivity classification gaps, and overall assessment.
