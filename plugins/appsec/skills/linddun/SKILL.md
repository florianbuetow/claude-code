---
name: linddun
description: >
  This skill should be used when the user asks to "run LINDDUN analysis",
  "check privacy threats", "privacy threat model", "GDPR analysis",
  "check data protection", or invokes /appsec:linddun. Dispatches 7
  category subagents in parallel for comprehensive LINDDUN privacy
  threat coverage.
---

# LINDDUN Privacy Threat Dispatcher

Dispatch parallel subagents covering all 7 LINDDUN privacy threat
categories. Each category runs as an independent subagent analyzing the
scoped code for that class of privacy threat. LINDDUN fills the gap that
security frameworks like STRIDE and OWASP leave: a system can be fully
secure (encrypted, authenticated, authorized) and still violate user
privacy. LINDDUN systematically identifies these privacy-specific threats.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This dispatcher supports all cross-cutting flags.

| Flag | Dispatcher-Specific Behavior |
|------|------------------------------|
| `--scope` | Propagated to all subagents. Default `changed`. |
| `--depth` | Propagated to all subagents. Default `standard`. |
| `--severity` | Applied during consolidation to filter the merged output. |
| `--format` | Applied to final consolidated output. |
| `--only L,I,D2` | Run only the listed categories. Accepts: `L`, `I`, `N1`, `D1`, `D2`, `U`, `N2`. Use `N1` for Non-repudiation (privacy) and `N2` for Non-compliance. Use `D1` for Detectability and `D2` for Data Disclosure. |
| `--fix` | Propagated to subagents; each produces fix suggestions inline. |
| `--quiet` | Propagated to subagents; suppress explanations. |
| `--explain` | Propagated to subagents; add regulatory context per finding. |

## Framework Reference

Read [`../../shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md)
for the full LINDDUN framework specification including threat descriptions,
code-level indicators, regulatory mappings (GDPR, CCPA, HIPAA), per-element
applicability matrix, and cross-framework mappings to STRIDE/OWASP/CWE.

## Pre-flight Relevance Check

Before dispatching subagents, scan the scoped file list to determine which
categories are relevant. Unlike STRIDE (where all categories usually apply),
LINDDUN relevance depends heavily on whether the codebase handles personal
data.

**First, confirm the codebase handles personal data.** If there is no PII,
no user accounts, no analytics, and no data collection, LINDDUN analysis
is not applicable. Report this and exit.

| Category | Skill | Relevant When | Skip When |
|----------|-------|---------------|-----------|
| L - Linkability | `linking` | Shared user IDs across services, analytics tracking, cookies, cross-context identifiers | Single-service app with no analytics, no cross-context tracking |
| I - Identifiability | `identifying` | User data exports, quasi-identifiers (zip, age, gender), anonymized datasets, analytics pipelines | No user data exports, no analytics, no anonymization attempts |
| N - Non-repudiation | `non-repudiation-privacy` | Audit logs of sensitive actions (health, legal, political), digital signatures on sensitive transactions | No sensitive action logging, no compliance-mandated audit trails |
| D - Detectability | `detecting` | Different error codes for existing vs non-existing resources, timing side channels, user enumeration | No user-facing lookup endpoints, no existence checks |
| D - Data Disclosure | `data-disclosure` | PII in logs, third-party SDKs, API responses with excess fields, cross-border data flows | No PII handling, no third-party integrations, no logging of personal data |
| U - Unawareness | `unawareness` | Data collection, consent flows, privacy policies, analytics, third-party scripts, telemetry | No data collection, no user-facing features |
| N - Non-compliance | `non-compliance` | Regulatory requirements (GDPR, CCPA, HIPAA), data retention, deletion endpoints, cross-border transfers | No regulated data, no applicable privacy regulations |

**How to check**: Use Grep on the scoped files to detect:
- PII patterns: `email`, `phone`, `ssn`, `address`, `birthdate`, `name`
- User data: `user_id`, `profile`, `account`, `preferences`
- Analytics: `analytics`, `tracking`, `telemetry`, `pixel`, `gtag`
- Third-party: `stripe`, `segment`, `mixpanel`, `google-analytics`, `facebook`
- Consent: `consent`, `gdpr`, `ccpa`, `cookie`, `opt-in`, `opt-out`
- Data export: `export`, `download`, `portability`

If `--only` is specified, skip the relevance check and dispatch only the
listed categories.

## Dispatch Category Subagents

**CRITICAL**: All Task tool calls MUST appear in the SAME response message.
This is what triggers parallel execution. If you emit them across separate
messages, they run sequentially and waste time.

### Dispatch Table

| Letter | Subagent Skill | Finding Prefix | Privacy Property | Focus |
|--------|---------------|----------------|-----------------|-------|
| L | `skills/linking/SKILL.md` | `LINK` | Unlinkability | Cross-service correlation, shared identifiers, behavioral tracking |
| I | `skills/identifying/SKILL.md` | `IDENT` | Anonymity | Re-identification risks, quasi-identifiers, insufficient anonymization |
| N1 | `skills/non-repudiation-privacy/SKILL.md` | `NREP` | Plausible Deniability | Forced accountability for sensitive actions, irrefutable audit trails |
| D1 | `skills/detecting/SKILL.md` | `DTCT` | Undetectability | Existence inference, enumeration, timing side channels |
| D2 | `skills/data-disclosure/SKILL.md` | `DDSCL` | Confidentiality (Personal Data) | PII in logs, over-collection, third-party data sharing |
| U | `skills/unawareness/SKILL.md` | `UNAWR` | Transparency | Missing consent, no data access/deletion, hidden data flows |
| N2 | `skills/non-compliance/SKILL.md` | `NCMPL` | Regulatory Compliance | GDPR/CCPA/HIPAA violations, missing DPIA, data retention failures |

### Subagent Prompt Template

Each subagent Task call must include a FULLY self-contained prompt. Subagents
get their own isolated context window and cannot see the main conversation.

Each subagent prompt must contain:

1. The **concrete file list** to analyze (resolved from scope, filtered for relevance).
2. The **absolute path to the category SKILL.md** to read and follow.
3. The **flags** to apply (`--scope`, `--depth`, `--severity`, `--format`, etc.).
4. The **findings schema path** (`shared/schemas/findings.md`) for output format.
5. An instruction to **return findings only** -- no summary, no cross-category
   commentary. The dispatcher handles consolidation.

```
Analyze the following files for LINDDUN {LETTER} ({CATEGORY_NAME}) privacy threats:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Follow the workflow defined in that skill to analyze the listed files.
Focus on threats to the {PRIVACY_PROPERTY} privacy property.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 4: Output findings in the schema format. Set metadata.framework to "linddun"
and metadata.category to "{LETTER_CODE}".

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: Return ONLY the findings list. Do NOT produce a summary or
cross-category analysis. The dispatcher handles consolidation.
```

### Launching

Emit one Task tool call per relevant category, ALL in a single response:

- `subagent_type`: `"general-purpose"`
- `description`: `"LINDDUN {LETTER} - {CATEGORY_NAME}"`
- `prompt`: The fully self-contained prompt above, filled in for this category.

Do NOT emit Task calls one at a time. Do NOT wait between dispatches.

## Consolidation

After ALL subagents return their results:

### 1. Merge Findings

Collect all findings from all subagent responses into a single list.

### 2. Deduplicate

Two findings are duplicates if they share the same `location.file` AND
`location.line` (or overlapping line ranges). When duplicates exist:
- Keep the finding with the higher severity.
- Merge LINDDUN category tags.
- Note the duplicate in the retained finding's description.

### 3. Regulatory Mapping

For each finding, map to applicable regulatory articles:
- **GDPR**: Map to specific articles (Art. 5, 6, 7, 12-14, 15, 17, 20, 25, 30, 32, 35, 44-49).
- **CCPA**: Map to specific sections (1798.100, 1798.105, 1798.120, 1798.140, 1798.150).
- **HIPAA**: Map where health data is involved.
Use the regulatory mapping tables in `linddun.md` for guidance.

### 4. Cross-Reference

For each finding, populate cross-framework references:
- `references.cwe`: Map to CWE identifier (e.g., CWE-359, CWE-200, CWE-532).
- `references.owasp`: Map to OWASP Top 10 category where applicable.
- `references.stride`: Map to closest STRIDE category (see LINDDUN-to-STRIDE table).

### 5. Rank by Severity

Sort findings: critical > high > medium > low. Within the same severity,
consider regulatory impact (GDPR violations rank higher than best-practice
recommendations).

### 6. Present Results

Output the consolidated report in the requested `--format`. Include:
- Summary: categories checked, total findings, severity breakdown.
- Regulatory impact summary: which regulations are implicated.
- Per-element privacy matrix (similar to STRIDE per-element analysis but
  for LINDDUN categories).
- Findings list in severity order with regulatory article citations.
- Data flow privacy assessment: where personal data crosses trust boundaries.

## Expert Mode

If `--depth expert` is set, after consolidation, launch adversarial privacy
agents to simulate privacy attacks (re-identification, linkage, inference).
Each agent receives the consolidated findings and attempts to demonstrate
how an adversary could exploit privacy weaknesses to identify, track, or
profile data subjects.

Red team output is appended to findings with prefix `RT` and
`metadata.tool` set to `"red-team"`.
