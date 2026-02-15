---
name: stride
description: >
  This skill should be used when the user asks to "run STRIDE analysis",
  "check STRIDE", "threat model with STRIDE", or invokes /appsec:stride.
  Dispatches 6 category subagents (S-T-R-I-D-E) in parallel for comprehensive
  STRIDE threat modeling coverage.
---

# STRIDE Threat Model Dispatcher

Dispatch parallel subagents covering all 6 STRIDE threat categories. Each
category runs as an independent subagent analyzing the scoped code for that
class of threat. STRIDE maps each category to a violated security property:
Spoofing (Authentication), Tampering (Integrity), Repudiation (Non-repudiation),
Information Disclosure (Confidentiality), Denial of Service (Availability),
Elevation of Privilege (Authorization).

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This dispatcher supports all cross-cutting flags.

| Flag | Dispatcher-Specific Behavior |
|------|------------------------------|
| `--scope` | Propagated to all subagents. Default `changed`. |
| `--depth` | Propagated to all subagents. Default `standard`. |
| `--severity` | Applied during consolidation to filter the merged output. |
| `--format` | Applied to final consolidated output. |
| `--only S,T,E` | Run only the listed categories. Accepts comma-separated STRIDE letters (e.g., `S`, `T`, `R`, `I`, `D`, `E`). Unlisted categories are skipped. |
| `--fix` | Propagated to subagents; each produces fix suggestions inline. |
| `--quiet` | Propagated to subagents; suppress explanations. |
| `--explain` | Propagated to subagents; add learning material per finding. |

## Framework Reference

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md)
for the full STRIDE framework specification including threat descriptions,
per-element applicability matrix, risk assessment guidance, and documentation
templates.

## Pre-flight Relevance Check

All 6 STRIDE categories are typically relevant to any codebase with
user-facing functionality. However, perform a lightweight scan to confirm
the codebase has code to analyze, and to build a targeted file list for
each subagent.

| Category | Skill | Relevant File Patterns | Notes |
|----------|-------|----------------------|-------|
| S - Spoofing | `spoofing` | Auth controllers, session middleware, token validation, login/register routes | Almost always relevant if the app has users |
| T - Tampering | `tampering` | Input handlers, database queries, API endpoints, file operations, config files | Almost always relevant |
| R - Repudiation | `repudiation` | Logging config, audit trail, transaction records, security event handlers | Relevant if there are security-sensitive actions |
| I - Information Disclosure | `info-disclosure` | Error handlers, API responses, log statements, config files, environment variables | Almost always relevant |
| D - Denial of Service | `dos` | Input parsers, regex patterns, resource allocation, file uploads, API rate limiting | Almost always relevant |
| E - Elevation of Privilege | `privilege-escalation` | Authorization middleware, role checks, admin routes, permission models, RBAC config | Almost always relevant if the app has roles |

For each category, use Glob and Grep to build a focused file list of the most
relevant files. Pass this scoped list to the subagent rather than the full
scope, so each subagent focuses on its area of expertise.

If `--only` is specified, dispatch only the listed categories.

## Dispatch Category Subagents

**CRITICAL**: All Task tool calls MUST appear in the SAME response message.
This is what triggers parallel execution. If you emit them across separate
messages, they run sequentially and waste time.

### Dispatch Table

| Letter | Subagent Skill | Finding Prefix | Security Property | Focus |
|--------|---------------|----------------|-------------------|-------|
| S | `skills/spoofing/SKILL.md` | `SPOOF` | Authentication | Credential theft, session hijacking, token manipulation, identity impersonation |
| T | `skills/tampering/SKILL.md` | `TAMP` | Integrity | SQL injection, parameter tampering, MITM, file modification, config tampering |
| R | `skills/repudiation/SKILL.md` | `REPUD` | Non-repudiation | Missing audit logs, log tampering, insufficient forensic evidence |
| I | `skills/info-disclosure/SKILL.md` | `DISC` | Confidentiality | Data breaches, error message leaks, timing attacks, cleartext transmission |
| D | `skills/dos/SKILL.md` | `DOS` | Availability | Resource exhaustion, algorithmic complexity, DDoS, decompression bombs |
| E | `skills/privilege-escalation/SKILL.md` | `PRIV` | Authorization | Broken access control, IDOR, JWT manipulation, role confusion |

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
Analyze the following files for STRIDE {LETTER} ({CATEGORY_NAME}) threats:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Follow the workflow defined in that skill to analyze the listed files.
Focus on threats to the {SECURITY_PROPERTY} security property.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 4: Output findings in the schema format. Set metadata.framework to "stride"
and metadata.category to "{LETTER}".

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: Return ONLY the findings list. Do NOT produce a summary or
cross-category analysis. The dispatcher handles consolidation.
```

### Launching

Emit one Task tool call per relevant category, ALL in a single response:

- `subagent_type`: `"general-purpose"`
- `description`: `"STRIDE {LETTER} - {CATEGORY_NAME}"`
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
- Merge STRIDE category tags (a finding tagged `T` and `I` keeps both in
  `references.stride`).
- Note the duplicate in the retained finding's description.

### 3. Cross-Reference

For each finding, populate cross-framework references where known:
- `references.owasp`: Map to OWASP Top 10 category.
- `references.cwe`: Map to CWE identifier.
- `references.mitre_attck`: Map to ATT&CK technique ID.
- `references.sans_cwe25`: Map to SANS/CWE Top 25 rank if applicable.

Use the cross-framework mapping tables in `stride.md` for guidance.

### 4. Per-Element Threat Matrix

Build a summary matrix showing which STRIDE categories produced findings
for each component or trust boundary. This mirrors the STRIDE per-element
analysis approach:

| Component | S | T | R | I | D | E | Findings |
|-----------|---|---|---|---|---|---|----------|
| Auth controller | X | | | | | X | SPOOF-001, PRIV-003 |
| API gateway | | X | | X | X | | TAMP-002, DISC-001 |

### 5. Rank by Severity

Sort findings: critical > high > medium > low. Within the same severity,
sort by confidence (high > medium > low).

### 6. Produce Aggregate Output

Wrap the consolidated findings in the aggregate output format from
`shared/schemas/findings.md`, including `categories_checked`,
`categories_skipped`, `total_findings`, and `by_severity`.

### 7. Present Results

Output the consolidated report in the requested `--format`. Include:
- Summary: categories checked, total findings, severity breakdown.
- Per-element threat matrix.
- Findings list in severity order.
- Trust boundary analysis: findings that cross trust boundaries are
  highlighted as higher risk.

## Expert Mode

If `--depth expert` is set, after consolidation, launch red team subagents
to simulate exploitation of the findings. Each red team agent receives the
consolidated findings and constructs multi-step attack chains that cross
STRIDE categories (e.g., Spoofing leads to Elevation of Privilege).

Read [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md) for
DREAD scoring criteria. Each finding receives a DREAD score in expert mode.

Launch red team agents as parallel Task calls (same single-response rule).
Red team output is appended to findings with prefix `RT` and
`metadata.tool` set to `"red-team"`.
