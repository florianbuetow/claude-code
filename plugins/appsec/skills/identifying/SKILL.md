---
name: identifying
description: >
  This skill should be used when the user asks to "check for identifiability",
  "analyze re-identification risks", "find privacy issues related to anonymization",
  "check for PII exposure", or mentions "identifiability" in a privacy context.
  Maps to LINDDUN category I.
---

# Identifiability Analysis (LINDDUN I)

Analyze source code for identifiability threats where individuals can be identified
from supposedly anonymous data. Combinations of quasi-identifiers (zip code, birth
date, gender) can uniquely identify individuals. Re-identification attacks on
"anonymized" data are the primary concern.

## Supported Flags

Read [`shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Identifiability-Specific Behavior |
|------|-----------------------------------|
| `--scope` | Default `changed`. Focuses on files handling user data, anonymization logic, data exports, analytics pipelines, and API responses. |
| `--depth quick` | Grep patterns only: scan for PII in logs, quasi-identifiers in exports, and missing anonymization. |
| `--depth standard` | Full code read, analyze data fields returned in APIs and stored in databases for re-identification risk. |
| `--depth deep` | Trace data flows from collection to storage to export. Assess quasi-identifier combinations across the system. |
| `--depth expert` | Deep + re-identification risk modeling: estimate k-anonymity violations and uniqueness of attribute combinations. |
| `--severity` | Filter output. Identifiability findings range from `low` (theoretical) to `critical` (direct PII exposure). |
| `--fix` | Generate anonymization, generalization, and suppression replacements. |

## Framework Context

**LINDDUN I -- Identifiability**

Identifiability occurs when a person can be identified from data that is supposed
to be anonymous or pseudonymous. Read
[`shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) for the
full LINDDUN framework reference including re-identification attack patterns and
regulatory definitions.

**Privacy Property Violated**: Anonymity / Pseudonymity

**STRIDE Mapping**: Information Disclosure (identifiability focuses specifically
on re-identification of anonymized data rather than general data access)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: data models, API handlers, data export logic,
   analytics pipelines, logging configuration, database schemas, and
   anonymization utilities.
4. Prioritize files containing: user data structures, data export endpoints,
   log statements with user context, report generation, and data sharing logic.

### Step 2 -- Analyze for Identifiability Patterns

Read each scoped file and assess re-identification risk:

1. **Identify direct identifiers**: Find fields like name, email, phone, SSN,
   or national ID that should not appear in anonymous contexts.
2. **Identify quasi-identifiers**: Find combinations of fields (zip code, age,
   gender, job title) that together may uniquely identify individuals.
3. **Check anonymization logic**: Verify that anonymization techniques are
   actually applied and are sufficient (not just removing the name field).
4. **Assess API responses**: Check whether endpoints return more personal
   attributes than the consumer needs.
5. **Examine logs and error messages**: Look for PII appearing in log output,
   stack traces, or debug messages.

At `--depth deep` or `--depth expert`, model quasi-identifier combinations and
estimate uniqueness across the population.

### Step 3 -- Report Findings

Output findings per [`shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `IDENT-NNN` id, title, severity (based on directness of
identification and data sensitivity), location with snippet, description of what
enables identification, impact (re-identification harm), fix (anonymization,
generalization, or suppression), and CWE/LINDDUN references.

## Analysis Checklist

1. Are direct identifiers (name, email, phone, SSN) present in data exports or analytics?
2. Do API responses return more user attributes than the consumer actually needs?
3. Are quasi-identifiers (zip code, birth date, gender) combined in any output?
4. Is anonymization actually implemented, or just assumed in comments?
5. Do logs contain IP addresses, user agents, or device identifiers alongside actions?
6. Can database queries return single-user results from "anonymous" tables?
7. Are email addresses or phone numbers used as primary keys or foreign keys?
8. Do error messages or stack traces expose personal data fields?

## What to Look For

1. **PII in log statements**: Personal data written to application logs.
   - Grep: `log\.\w+\(.*email|logger\.\w+\(.*name|console\.log\(.*phone|print\(.*ssn`
2. **Email or phone as primary key**: Using direct identifiers as database keys.
   - Grep: `PRIMARY KEY.*email|primary_key.*email|@Column.*email.*unique|findByEmail|findByPhone`
3. **IP address logging**: Recording IP addresses without anonymization.
   - Grep: `req\.ip|request\.remote_addr|X-Forwarded-For|ip_address|ipAddress|getRemoteAddr`
4. **Over-fetched API responses**: SELECT * or returning full user objects.
   - Grep: `SELECT \*.*FROM.*user|\.findAll\(|\.find\(\{\}\)|res\.json\(user\)|JSON\.stringify\(user`
5. **Insufficient anonymization**: Removing names but keeping detailed attributes.
   - Grep: `anonymize|anonymise|deidentify|de_identify|pseudonymize|mask.*data`
6. **Quasi-identifier combinations**: Multiple demographic fields in the same record.
   - Grep: `zip_code.*birth_date|zipCode.*gender|age.*location|dateOfBirth.*address`
7. **User agent collection**: Storing full browser fingerprint strings.
   - Grep: `user-agent|userAgent|navigator\.userAgent|req\.headers\[.user-agent.\]`
8. **Data exports without scrubbing**: Export endpoints that dump raw user data.
   - Grep: `export.*user|download.*report|csv.*user|toCSV|toJSON.*user`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Recital 26 | Identifiability test | Data is personal if any means can identify the subject |
| GDPR Art. 4(5) | Pseudonymization definition | Pseudonymized data is still personal data |
| GDPR Art. 25 | Data protection by design | Anonymization must be effective by design |
| HIPAA Safe Harbor | 18 identifier categories | All 18 must be removed for de-identification |
| CCPA 1798.140(h) | Deidentified information | Reasonably cannot be linked to a consumer |
| CCPA 1798.140(o) | Personal information | Includes information that identifies or could be linked |

## Output Format

Use finding ID prefix **IDENT** (e.g., `IDENT-001`, `IDENT-002`).

All findings follow the schema in
[`shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-359` or `CWE-200` as appropriate
- `references.owasp`: `A02:2021` (Cryptographic Failures -- weak anonymization)
- `metadata.tool`: `"identifying"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"I"`

**Summary table** after all findings:

```
| Identifiability Pattern     | Critical | High | Medium | Low |
|-----------------------------|----------|------|--------|-----|
| Direct PII exposure         |          |      |        |     |
| PII in logs                 |          |      |        |     |
| Quasi-identifier combos     |          |      |        |     |
| Insufficient anonymization  |          |      |        |     |
| Over-fetched API responses  |          |      |        |     |
| IP / device tracking        |          |      |        |     |
```

Followed by: top 3 priorities, re-identification risk assessment, and overall assessment.
