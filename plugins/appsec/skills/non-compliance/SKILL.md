---
name: non-compliance
description: >
  This skill should be used when the user asks to "check for non-compliance",
  "analyze GDPR compliance", "find CCPA violations", "check HIPAA compliance",
  "audit regulatory requirements", or mentions "non-compliance" in a privacy
  context. Maps to LINDDUN category N2. No STRIDE equivalent exists.
---

# Non-Compliance Analysis (LINDDUN N2)

Analyze source code for regulatory non-compliance where data processing activities
violate GDPR, CCPA, or HIPAA. Non-compliance results from missing technical
controls, incorrect legal bases, or unimplemented data subject rights. This
category has no STRIDE equivalent and is unique to privacy threat modeling.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Non-Compliance-Specific Behavior |
|------|----------------------------------|
| `--scope` | Default `changed`. Focuses on files containing data retention, deletion logic, consent management, cross-border transfers, age verification, and processing records. |
| `--depth quick` | Grep patterns only: scan for missing deletion endpoints, hardcoded retention, and cross-border transfers. |
| `--depth standard` | Full code read, check data lifecycle implementation against regulatory requirements. |
| `--depth deep` | Trace data flows across storage layers. Verify deletion cascades through databases, backups, caches, and logs. |
| `--depth expert` | Deep + regulatory audit simulation: assess compliance posture against GDPR, CCPA, and HIPAA article by article. |
| `--severity` | Filter output. Missing data subject rights are `high`; documentation gaps are `medium`. |
| `--fix` | Generate retention enforcement, deletion cascades, and consent management implementations. |

## Framework Context

**LINDDUN N2 -- Non-compliance**

Non-compliance occurs when data processing activities violate applicable privacy
regulations. Read [`../../shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md)
for the full framework reference including regulatory mappings.

**Privacy Property Violated**: Regulatory Compliance |
**STRIDE Mapping**: No equivalent | **OWASP**: A04:2021 (Insecure Design)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: data retention logic, deletion handlers, consent
   management, user rights endpoints, data transfer configs, and age gates.
4. Prioritize files containing: cleanup jobs, TTL configs, deletion endpoints,
   consent flows, data exports, and cross-region deployment configs.

### Step 2 -- Analyze for Non-Compliance

Read each scoped file and assess regulatory compliance:

1. **Check data retention enforcement**: Verify that data retention periods
   are defined, configurable, and enforced through automated cleanup.
2. **Assess deletion completeness**: Verify that user deletion cascades
   through all storage layers (database, cache, logs, backups, third parties).
3. **Examine consent management**: Check for valid consent collection,
   withdrawal mechanisms, and purpose-specific processing controls.
4. **Check cross-border transfers**: Identify personal data flows to servers
   in non-adequate jurisdictions without transfer safeguards.
5. **Verify data subject rights**: Confirm implementation of access, correction,
   deletion, portability, and restriction of processing endpoints.
6. **Assess age verification**: Check for age gating where required (COPPA,
   GDPR Article 8).

At `--depth deep` or `--depth expert`, trace the complete data lifecycle and
verify compliance at every stage from collection through deletion.

### Step 3 -- Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `NCMPL-NNN` id, title, severity (based on regulatory penalty
risk and affected data subjects), location with snippet, description of unmet
regulatory requirement, impact (penalties and liability), fix (technical control
implementation), and CWE/LINDDUN/regulatory article references.

## Analysis Checklist

1. Are data retention periods defined and enforced through automated cleanup jobs?
2. Does user deletion cascade through all storage systems (DB, cache, logs, backups)?
3. Is there a consent management system with collection, withdrawal, and purpose tracking?
4. Are cross-border data transfers protected with adequate safeguards (SCCs, BCRs)?
5. Are data subject rights implemented (access, export, deletion, restriction)?
6. Does the system implement age verification for minors (COPPA, GDPR Article 8)?
7. Is there a breach notification capability within 72 hours?
8. Do hardcoded retention periods match the stated privacy policy?

## What to Look For

1. **Missing data retention enforcement**: No TTL, no cleanup jobs, no expiration.
   - Grep: `retention|ttl|time.to.live|cleanup|purge|expire|cron.*delete|scheduled.*removal`
2. **Incomplete deletion**: User deletion that misses storage layers.
   - Grep: `deleteUser|removeUser|eraseUser|destroyUser|delete.*account|purge.*user`
3. **Missing consent withdrawal**: No mechanism to revoke previously given consent.
   - Grep: `withdraw.*consent|revoke.*consent|opt.out|unsubscribe|consent.*revoke|removeConsent`
4. **Cross-border data transfers**: Data sent to non-adequate jurisdictions.
   - Grep: `region.*us-east|endpoint.*amazonaws|storage.*googleapis|azure.*region|cloudflare`
5. **Missing age verification**: No age gate or parental consent for minors.
   - Grep: `age.*verify|date.of.birth|dateOfBirth|minAge|age.*gate|parental.*consent|COPPA|under.*13`
6. **Hardcoded retention periods**: Retention values that may not match policy.
   - Grep: `days.*=.*365|retention.*=.*30|ttl.*=.*90|expire.*=.*\d+|keep.*days|max.*age.*=`
7. **Missing processing restriction**: No ability to pause processing on request.
   - Grep: `restrict.*processing|pause.*processing|freeze.*account|suspend.*data|processing.*hold`
8. **Missing breach notification**: No incident response or notification mechanism.
   - Grep: `breach.*notify|incident.*report|security.*alert|data.*breach|notify.*authority`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Art. 5-6 | Processing principles, lawful bases | Lawfulness, purpose limitation, data minimization |
| GDPR Art. 8 | Child's consent | Parental consent required for minors |
| GDPR Art. 17-18, 20 | Erasure, restriction, portability | Data subject rights implementation |
| GDPR Art. 28, 30 | Processor requirements, ROPA | DPAs and records of processing activities |
| GDPR Art. 33-35 | Breach notification, DPIA | 72-hour notification, impact assessments |
| GDPR Art. 44-49 | Cross-border transfers | Adequacy decisions, SCCs, or BCRs required |
| CCPA 1798.105, .120 | Right to delete, opt-out | Consumer deletion and sale opt-out |
| HIPAA 164.404, .530 | Breach notification, admin | PHI safeguards and breach notification |

## Output Format

Use finding ID prefix **NCMPL** (e.g., `NCMPL-001`, `NCMPL-002`).

All findings follow the schema in
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-359` (Exposure of Private Information)
- `references.owasp`: `A04:2021` (Insecure Design -- missing regulatory controls)
- `metadata.tool`: `"non-compliance"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"N2"`

**Summary table** after all findings:

```
| Non-Compliance Pattern        | Critical | High | Medium | Low |
|-------------------------------|----------|------|--------|-----|
| Missing data retention        |          |      |        |     |
| Incomplete deletion           |          |      |        |     |
| Missing consent management    |          |      |        |     |
| Cross-border transfers        |          |      |        |     |
| Missing data subject rights   |          |      |        |     |
| Missing age verification      |          |      |        |     |
| Missing breach notification   |          |      |        |     |
```

Followed by: top 3 priorities, compliance posture summary, and overall assessment.
