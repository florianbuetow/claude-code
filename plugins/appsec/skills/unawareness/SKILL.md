---
name: unawareness
description: >
  This skill should be used when the user asks to "check for unawareness",
  "analyze consent mechanisms", "find privacy issues related to transparency",
  "check for hidden data collection", "audit user consent flows", or mentions
  "unawareness" in a privacy context. Maps to LINDDUN category U. No STRIDE
  equivalent exists.
---

# Unawareness Analysis (LINDDUN U)

Analyze source code for unawareness threats where users do not know how their
personal data is collected, processed, or shared. Failing to inform users
violates transparency and may invalidate consent. This category has no STRIDE
equivalent and is unique to privacy threat modeling.

## Supported Flags

Read [`shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

| Flag | Unawareness-Specific Behavior |
|------|-------------------------------|
| `--scope` | Default `changed`. Focuses on files containing data collection, consent management, third-party integrations, analytics, and user data endpoints. |
| `--depth quick` | Grep patterns only: scan for analytics initialization, missing consent checks, and third-party scripts. |
| `--depth standard` | Full code read, verify consent flows precede data collection, check for undisclosed data sharing. |
| `--depth deep` | Trace all data collection points and verify each has corresponding consent and disclosure. Map undisclosed data flows. |
| `--depth expert` | Deep + transparency gap analysis: compare actual data practices against typical privacy policy claims. |
| `--severity` | Filter output. Data collection before consent is `high`; missing disclosure is `medium`. |
| `--fix` | Generate consent gates, privacy notice references, and data dashboard implementations. |

## Framework Context

**LINDDUN U -- Unawareness**

Unawareness occurs when data subjects do not know how their personal data is
collected, processed, or shared. Read
[`shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) for the
full framework reference including transparency obligations and consent requirements.

**Privacy Property Violated**: Transparency / Informed Consent |
**STRIDE Mapping**: No equivalent | **OWASP**: A04:2021 (Insecure Design)

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant files: data collection handlers, consent management
   modules, third-party SDK integrations, analytics initialization, user
   preference storage, data export/deletion endpoints, and privacy policy
   references.
4. Prioritize files containing: form submissions, registration flows, analytics
   setup, cookie management, third-party script loading, and user data APIs.

### Step 2 -- Analyze for Unawareness Threats

Read each scoped file and assess whether users are informed about data
practices:

1. **Check consent flow ordering**: Verify that consent is obtained before
   data collection begins -- not after or simultaneously.
2. **Audit third-party integrations**: Identify all third-party scripts, SDKs,
   and APIs that receive user data and verify disclosure.
3. **Examine analytics initialization**: Check whether analytics and telemetry
   start before the user has consented.
4. **Look for data subject rights**: Verify implementation of access, export,
   correction, and deletion endpoints.
5. **Assess consent granularity**: Check whether consent is all-or-nothing
   or granular by purpose.

At `--depth deep` or `--depth expert`, map every data collection point and
verify each has a corresponding consent mechanism and privacy policy disclosure.

### Step 3 -- Report Findings

Output findings per [`shared/schemas/findings.md`](../../shared/schemas/findings.md).
Each finding needs: `UNAWR-NNN` id, title, severity (based on whether users are
unaware of collection, sharing, or both), location with snippet, description of
what data practice users are unaware of, impact (uninformed consent consequences),
fix (consent gate, privacy notice, or user control), and CWE/LINDDUN references.

## Analysis Checklist

1. Is analytics or telemetry initialized before the user consents to tracking?
2. Are there third-party scripts that receive user data without privacy policy disclosure?
3. Does a consent management system exist with granular opt-in/opt-out controls?
4. Can users access, export, and delete their personal data (data subject rights)?
5. Is there consent version tracking to prove what each user agreed to?
6. Are data collection purposes explained at the point of collection?
7. Are cookies set before the user interacts with a cookie consent banner?
8. Do dark patterns pressure users into accepting broader data collection?

## What to Look For

1. **Analytics before consent**: Tracking scripts initialized before consent check.
   - Grep: `gtag\(|analytics\.init|mixpanel\.init|segment\.load|amplitude\.init|posthog\.init`
2. **Missing consent management**: No consent storage or preference system.
   - Grep: `consent|cookie.consent|gdpr.consent|privacy.preference|opt.in|opt.out`
3. **Third-party scripts without disclosure**: External services receiving user data.
   - Grep: `<script.*src=.*third.party|import.*analytics|require.*tracking|facebook.*pixel|intercom`
4. **Missing data export endpoint**: No user data portability implementation.
   - Grep: `export.*data|download.*my.*data|data.portability|DSAR|subject.*access|getMyData`
5. **Missing data deletion endpoint**: No right-to-erasure implementation.
   - Grep: `delete.*account|erase.*data|remove.*user.*data|right.*forgotten|deleteMyData|purgeUser`
6. **Cookies set before consent**: Cookie writes that execute before consent flow.
   - Grep: `document\.cookie.*=|res\.cookie\(|setCookie|set-cookie|cookie\.set`
7. **Hidden data collection**: Data gathered without visible user-facing disclosure.
   - Grep: `navigator\.geolocation|getCurrentPosition|deviceId|device_id|collectTelemetry|beacon`
8. **Missing consent versioning**: No tracking of what consent version users agreed to.
   - Grep: `consent.*version|policy.*version|terms.*version|consent.*timestamp|consent.*date`

## Regulatory Mapping

| Regulation | Provision | Relevance |
|-----------|-----------|-----------|
| GDPR Art. 7 | Conditions for consent | Consent must be freely given, specific, informed, unambiguous |
| GDPR Art. 12-15 | Transparency, right of access | Clear information about processing; access to held data |
| GDPR Art. 17, 20 | Erasure, portability | Deletion on request; export in portable format |
| CCPA 1798.100, .105, .120 | Know, delete, opt-out | Consumer rights to know, delete, and opt out of sale |
| ePrivacy Directive Art. 5(3) | Cookie consent | Prior consent required for non-essential cookies |

## Output Format

Use finding ID prefix **UNAWR** (e.g., `UNAWR-001`, `UNAWR-002`).

All findings follow the schema in
[`shared/schemas/findings.md`](../../shared/schemas/findings.md) with:
- `references.cwe`: `CWE-1021` (Improper Restriction of Rendered UI Layers)
- `references.owasp`: `A04:2021` (Insecure Design -- missing privacy by design)
- `metadata.tool`: `"unawareness"`
- `metadata.framework`: `"linddun"`
- `metadata.category`: `"U"`

**Summary table** after all findings:

```
| Unawareness Pattern          | Critical | High | Medium | Low |
|------------------------------|----------|------|--------|-----|
| Analytics before consent     |          |      |        |     |
| Missing consent management   |          |      |        |     |
| Undisclosed third-party data |          |      |        |     |
| Missing data export          |          |      |        |     |
| Missing data deletion        |          |      |        |     |
| Pre-consent cookies          |          |      |        |     |
| Hidden data collection       |          |      |        |     |
```

Followed by: top 3 priorities, transparency gap map, and overall assessment.
