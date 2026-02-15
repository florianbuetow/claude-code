---
name: owasp
description: >
  This skill should be used when the user asks to "run OWASP analysis",
  "check OWASP Top 10", "OWASP scan", or invokes /appsec:owasp. Dispatches
  10 category subagents (A01-A10) in parallel for comprehensive OWASP Top 10
  coverage.
---

# OWASP Top 10 Dispatcher

Dispatch parallel subagents covering all 10 categories of the OWASP Top 10
(2021). Each category runs as an independent subagent with its own context
window, analyzing the scoped code for that specific class of vulnerability.
Results are consolidated, deduplicated, and ranked by severity.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This dispatcher supports all cross-cutting flags.

| Flag | Dispatcher-Specific Behavior |
|------|------------------------------|
| `--scope` | Propagated to all subagents. Default `changed`. |
| `--depth` | Propagated to all subagents. Default `standard`. |
| `--severity` | Applied during consolidation to filter the merged output. |
| `--format` | Applied to final consolidated output. |
| `--only A01,A03` | Run only the listed categories. Accepts comma-separated category codes (e.g., `A01`, `A03`, `A07`). Unlisted categories are skipped entirely. |
| `--fix` | Propagated to subagents; each produces fix suggestions inline. |
| `--quiet` | Propagated to subagents; suppress explanations. |
| `--explain` | Propagated to subagents; add learning material per finding. |

## Framework Reference

Read [`../../shared/frameworks/owasp-top10-2021.md`](../../shared/frameworks/owasp-top10-2021.md)
for the full OWASP Top 10 specification including vulnerability descriptions,
prevention guidance, and STRIDE cross-mappings for each category.

## Pre-flight Relevance Check

Before dispatching subagents, scan the scoped file list to determine which
categories are relevant. Skip categories that have no plausible attack surface
in the codebase. This avoids wasting subagent context windows on irrelevant
analysis.

| Category | Skill | Skip When |
|----------|-------|-----------|
| A01 Broken Access Control | `access-control` | No route handlers, no auth middleware, no API endpoints |
| A02 Cryptographic Failures | `crypto` | No crypto imports, no hashing, no TLS config, no secret storage |
| A03 Injection | `injection` | No database queries, no shell commands, no template rendering, no user input handling |
| A04 Insecure Design | `insecure-design` | Always relevant (design-level analysis applies to any code) |
| A05 Security Misconfiguration | `misconfig` | No configuration files, no deployment manifests, no environment variables |
| A06 Outdated Components | `outdated-deps` | No package manifest (`package.json`, `requirements.txt`, `go.mod`, `Gemfile`, `pom.xml`, `Cargo.toml`) |
| A07 Auth Failures | `auth` | No login, registration, session, or token handling code |
| A08 Integrity Failures | `integrity` | No CI/CD config, no deserialization, no package install scripts, no auto-update logic |
| A09 Logging Failures | `logging` | No log statements, no audit trail, no monitoring config |
| A10 SSRF | `ssrf` | No HTTP client calls, no URL fetching, no webhook handling, no image/document fetching from URLs |

**How to check**: Use Glob and Grep on the scoped files to detect relevant
patterns. For example, check for `fetch(`, `axios`, `requests.get`,
`http.Get` to determine A10 relevance. Check for `package.json`,
`requirements.txt`, `go.mod` to determine A06 relevance.

If `--only` is specified, skip the relevance check and dispatch only the
listed categories.

## Dispatch Category Subagents

**CRITICAL**: All Task tool calls MUST appear in the SAME response message.
This is what triggers parallel execution. If you emit them across separate
messages, they run sequentially and waste time.

### Dispatch Table

| Category | Subagent Skill | Finding Prefix | Description |
|----------|---------------|----------------|-------------|
| A01 | `skills/access-control/SKILL.md` | `AC` | Broken access control, IDOR, CORS, missing deny-by-default |
| A02 | `skills/crypto/SKILL.md` | `CRYPT` | Weak crypto, cleartext transmission, poor key management |
| A03 | `skills/injection/SKILL.md` | `INJ` | SQL/NoSQL/OS/LDAP injection, template injection |
| A04 | `skills/insecure-design/SKILL.md` | `DESGN` | Missing threat modeling, insecure patterns, business logic flaws |
| A05 | `skills/misconfig/SKILL.md` | `MSCFG` | Default configs, unnecessary features, verbose errors |
| A06 | `skills/outdated-deps/SKILL.md` | `DEP` | Known CVEs in dependencies, unmaintained packages |
| A07 | `skills/auth/SKILL.md` | `AUTH` | Credential stuffing, weak passwords, session management |
| A08 | `skills/integrity/SKILL.md` | `INTEG` | Insecure deserialization, CI/CD integrity, unsigned updates |
| A09 | `skills/logging/SKILL.md` | `LOG` | Missing audit logs, insufficient monitoring, log injection |
| A10 | `skills/ssrf/SKILL.md` | `SSRF` | Unvalidated URL fetching, internal network access |

### Subagent Prompt Template

Each subagent Task call must include a FULLY self-contained prompt. Subagents
get their own isolated context window and cannot see the main conversation.

Each subagent prompt must contain:

1. The **concrete file list** to analyze (resolved from scope).
2. The **absolute path to the category SKILL.md** to read and follow.
3. The **flags** to apply (`--scope`, `--depth`, `--severity`, `--format`, etc.).
4. The **findings schema path** (`shared/schemas/findings.md`) for output format.
5. An instruction to **return findings only** -- no summary, no cross-category
   commentary. The dispatcher handles consolidation.

```
Analyze the following files for OWASP {CATEGORY_CODE} ({CATEGORY_NAME}) vulnerabilities:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Follow the workflow defined in that skill to analyze the listed files.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 4: Output findings in the schema format. Set metadata.framework to "owasp"
and metadata.category to "{CATEGORY_CODE}".

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: Return ONLY the findings list. Do NOT produce a summary or
cross-category analysis. The dispatcher handles consolidation.
```

### Launching

Emit one Task tool call per relevant category, ALL in a single response:

- `subagent_type`: `"general-purpose"`
- `description`: `"OWASP {CATEGORY_CODE} - {CATEGORY_NAME}"`
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
- Merge cross-references (a finding tagged `A03` and `A01` keeps both).
- Note the duplicate in the retained finding's description.

### 3. Cross-Reference

For each finding, populate cross-framework references where known:
- `references.cwe`: Map to CWE identifier.
- `references.stride`: Map to STRIDE category letter(s).
- `references.mitre_attck`: Map to ATT&CK technique ID.
- `references.sans_cwe25`: Map to SANS/CWE Top 25 rank if applicable.

### 4. Rank by Severity

Sort findings: critical > high > medium > low. Within the same severity,
sort by confidence (high > medium > low).

### 5. Produce Aggregate Output

Wrap the consolidated findings in the aggregate output format from
`shared/schemas/findings.md`, including `categories_checked`,
`categories_skipped`, `skip_reason`, `total_findings`, and `by_severity`.

### 6. Present Results

Output the consolidated report in the requested `--format`. Include:
- Summary table: categories checked, categories skipped (with reasons).
- Severity breakdown: count by critical/high/medium/low.
- Findings list in severity order.
- Cross-category patterns (e.g., "injection findings in A03 also indicate
  broken access control in A01").

## Expert Mode

If `--depth expert` is set, after consolidation, launch red team subagents
to simulate exploitation of the findings. Each red team agent receives the
consolidated findings and attempts to construct multi-step attack chains.

Read [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md) for
DREAD scoring criteria. Each finding receives a DREAD score in expert mode.

Launch red team agents as parallel Task calls (same single-response rule).
Pass the full findings list to each persona. Red team output is appended
to findings with prefix `RT` and `metadata.tool` set to `"red-team"`.
