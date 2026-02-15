---
name: full-audit
description: >
  This skill should be used when the user asks for a "full security audit",
  "exhaustive audit", "comprehensive security review", or invokes
  /appsec:full-audit. Launches every framework, every tool, and every
  red team agent, producing a dated report file.
---

# AppSec Full Audit -- Exhaustive Security Review

Launches every framework, every scanner, every specialized tool, and every
red team agent. Produces a comprehensive dated report file. This is the
most thorough analysis available -- it runs everything, omits nothing, and
preserves every subagent's output verbatim.

Unlike `/appsec:run` which selects relevant tools, `full-audit` runs ALL
tools regardless of detected stack. Unlike `/appsec:run` which consolidates
subagent outputs into a unified list, `full-audit` preserves each agent's
raw output as a separate report section.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification.

| Flag | Full Audit Behavior |
|------|---------------------|
| `--scope` | Propagated to all subagents. Default `full` (NOT `changed`). |
| `--depth` | Forced to `expert` for all subagents. Flag is accepted but overridden. |
| `--severity` | Applied only to the summary table. All findings appear in the full report regardless. |
| `--format` | Ignored. Full audit always produces a Markdown report file. |
| `--quiet` | Suppress progress messages. Report content is unchanged. |
| `--explain` | Propagated to subagents; add learning material per finding. |
| `--fix` | Propagated to subagents; each produces fix suggestions inline. |
| `--skip-redteam` | Skip red team phase. Saves time but loses attack chain analysis. |
| `--skip-frameworks <list>` | Skip specific frameworks. Accepts: `owasp`, `stride`, `pasta`, `linddun`, `sans25`, `mitre`. |
| `--output <filename>` | Custom output filename. Default: `<YYYYMMDD>_appsec_report.md`. |

## Workflow

The full audit runs in 5 phases. Phases 1-3 launch subagents. Phase 4
runs red team agents. Phase 5 assembles the report. Each phase must
complete before the next begins (except where noted for parallelism within
a phase).

### Phase 1: Assessment & Scanners (Main Agent)

#### Step 1.1: Resolve Scope

Default scope is `full` (the entire codebase). Parse flags and resolve to a
concrete file list. For `--scope full`, enumerate all tracked files:

```
git ls-files
```

Filter out binary files, images, and vendored dependencies.

#### Step 1.2: Detect Stack & Scanners

Run the same detection as `/appsec:start` Steps 1-4:
- Detect languages, frameworks, databases from manifests.
- Detect architecture patterns and data sensitivity.
- Detect installed scanners via `which` commands.

#### Step 1.3: Run All Detected Scanners

Run every detected scanner in parallel Bash calls within a SINGLE response.
Use invocation patterns from
[`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md).

Before launching scanners, create the output directory:

```bash
mkdir -p reports/appsec/scanners
```

Redirect ALL scanner output to files -- the main agent NEVER reads scanner
JSON content.

**Scanner dispatch pattern:**

```bash
# Run each scanner in parallel Bash calls — redirect output to files
semgrep scan --config auto --json --quiet <scope_path> > reports/appsec/scanners/semgrep.json 2>&1
gitleaks detect --source <scope_path> --report-format json --no-banner > reports/appsec/scanners/gitleaks.json 2>&1
npm audit --json > reports/appsec/scanners/npm-audit.json 2>&1           # if Node.js project
pip-audit --format json > reports/appsec/scanners/pip-audit.json 2>&1    # if Python project
trivy fs --format json <scope_path> > reports/appsec/scanners/trivy.json 2>&1   # if installed
```

After ALL scanners complete, check exit codes and file sizes ONLY. Do NOT
read or parse scanner JSON files in the main agent context.

```bash
# Check each scanner result — exit code + file size only
ls -l reports/appsec/scanners/*.json
```

Build a scanner status list from exit codes and file sizes:

- **Exit code 0 or 1 AND file size > 0**: Mark as `OK`.
- **Exit code > 1 AND file size > 0**: Mark as `PARTIAL (ran with warnings)`.
- **File size 0 or file missing**: Mark as `FAILED (no output)`.
- **Exit code 127 (command not found)**: Mark as `MISSING`.

**Error handling for scanners:**

- **Non-zero exit code**: Many scanners exit non-zero when they find issues
  (e.g., `npm audit` exits 1 when vulnerabilities exist). This is normal.
  Only treat it as a failure if the output file is empty (0 bytes).
- **Timeout**: If a scanner does not return within 120 seconds, skip it
  and note the timeout. Mark as `FAILED (timeout)`.
- **Scanner not found**: If a scanner from the plan is not installed (exit
  code 127), note it in `SCANNERS MISSING` and continue.
- Track all scanner statuses for the report assembler:
  ```
  scanner_status = []  # list of {scanner, status, file_path, file_size}
  ```

### Phase 2: Framework Analysis (Parallel Subagents)

Launch framework dispatchers as parallel subagents. The OWASP, STRIDE,
LINDDUN, and specialized tool subagents run in parallel. PASTA runs
sequentially (its stages are chained).

**CRITICAL**: All parallel Task tool calls MUST appear in the SAME response
message. This is what triggers concurrent execution.

Before dispatching, create the output directory:

```bash
mkdir -p reports/appsec/skills
```

#### Parallel Batch 1: OWASP + STRIDE + LINDDUN + Specialized + SANS/CWE + MITRE

Launch ALL of the following as parallel Task calls in ONE response:

**OWASP Top 10 (10 subagents):**

| Category | Skill | Description |
|----------|-------|-------------|
| A01 | `skills/access-control/SKILL.md` | Broken Access Control |
| A02 | `skills/crypto/SKILL.md` | Cryptographic Failures |
| A03 | `skills/injection/SKILL.md` | Injection |
| A04 | `skills/insecure-design/SKILL.md` | Insecure Design |
| A05 | `skills/misconfig/SKILL.md` | Security Misconfiguration |
| A06 | `skills/outdated-deps/SKILL.md` | Vulnerable Components |
| A07 | `skills/auth/SKILL.md` | Auth Failures |
| A08 | `skills/integrity/SKILL.md` | Integrity Failures |
| A09 | `skills/logging/SKILL.md` | Logging Failures |
| A10 | `skills/ssrf/SKILL.md` | SSRF |

**STRIDE (6 subagents):**

| Letter | Skill | Description |
|--------|-------|-------------|
| S | `skills/spoofing/SKILL.md` | Spoofing |
| T | `skills/tampering/SKILL.md` | Tampering |
| R | `skills/repudiation/SKILL.md` | Repudiation |
| I | `skills/info-disclosure/SKILL.md` | Information Disclosure |
| D | `skills/dos/SKILL.md` | Denial of Service |
| E | `skills/privilege-escalation/SKILL.md` | Elevation of Privilege |

**LINDDUN (7 subagents):**

| Category | Skill | Description |
|----------|-------|-------------|
| L | `skills/linking/SKILL.md` | Linkability |
| I | `skills/identifying/SKILL.md` | Identifiability |
| N1 | `skills/non-repudiation-privacy/SKILL.md` | Non-repudiation (privacy) |
| D1 | `skills/detecting/SKILL.md` | Detectability |
| D2 | `skills/data-disclosure/SKILL.md` | Data Disclosure |
| U | `skills/unawareness/SKILL.md` | Unawareness |
| N2 | `skills/non-compliance/SKILL.md` | Non-compliance |

**Specialized Tools (up to 6 subagents, as relevant):**

| Tool | Skill | Description |
|------|-------|-------------|
| Secrets | `skills/secrets/SKILL.md` | Hardcoded secrets, leaked credentials |
| Attack Surface | `skills/attack-surface/SKILL.md` | Entry point inventory |
| Data Flows | `skills/data-flows/SKILL.md` | Data flow mapping |

**SANS/CWE Top 25 (1 subagent):**

| Tool | Skill | Description |
|------|-------|-------------|
| SANS25 | `skills/sans25/SKILL.md` | CWE Top 25 analysis |

Launch ALL of these as parallel Task calls in a SINGLE response.

#### Subagent Prompt Template

Each subagent Task call must include a FULLY self-contained prompt.
Subagents get their own isolated context window and cannot see the main
conversation. Subagents write their findings to a file and return ONLY
a one-line status summary.

Use `--depth expert` and `--scope full` hardcoded into every prompt.

```
Analyze the following files for {TOOL_DESCRIPTION} vulnerabilities:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Follow the workflow defined in that skill to analyze the listed files.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 4: Produce findings in the schema format. Set metadata.tool to "{TOOL_NAME}"
and metadata.framework to "{FRAMEWORK}".

STEP 5: Write findings using the AGGREGATE OUTPUT format from the findings schema to:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/{TOOL_NAME}.json

Use the Write tool. The file must be a JSON object with fields:
  tool, total_findings, by_severity (object with critical/high/medium/low counts),
  notes (string with narrative assessment, evidence, or context your skill produces),
  findings (array)

The "notes" field is REQUIRED for the full audit. Include any narrative assessment,
evidence, or context your skill produces. The report assembler will include this
verbatim in the report section for your framework/tool.

If zero findings, write: {"tool":"{TOOL_NAME}","total_findings":0,"by_severity":{"critical":0,"high":0,"medium":0,"low":0},"notes":"<your narrative assessment>","findings":[]}

FLAGS: --scope full --depth expert

IMPORTANT: After writing the file, return ONLY a one-line status in this exact format:
"{TOOL_NAME}: N findings (Xc Xh Xm Xl)"
where N is the total count and Xc/Xh/Xm/Xl are counts per severity.
Example: "injection: 3 findings (0c 1h 2m 0l)"
Do NOT return the findings themselves. Do NOT produce a summary or
cross-tool analysis. The orchestrator handles report assembly.
```

#### Sequential: PASTA (7 stages)

After the parallel batch completes (or concurrently if the runtime supports
it), run the PASTA pipeline. PASTA stages are STRICTLY sequential -- each
stage's output feeds the next stage via file.

| Stage | Skill | Output File |
|-------|-------|-------------|
| 1 | `skills/pasta-objectives/SKILL.md` | `reports/appsec/skills/pasta-stage-1.json` |
| 2 | `skills/pasta-scope/SKILL.md` | `reports/appsec/skills/pasta-stage-2.json` |
| 3 | `skills/pasta-decompose/SKILL.md` | `reports/appsec/skills/pasta-stage-3.json` |
| 4 | `skills/pasta-threats/SKILL.md` | `reports/appsec/skills/pasta-stage-4.json` |
| 5 | `skills/pasta-vulns/SKILL.md` | `reports/appsec/skills/pasta-stage-5.json` |
| 6 | `skills/pasta-attack-sim/SKILL.md` | `reports/appsec/skills/pasta-stage-6.json` |
| 7 | `skills/pasta-risk/SKILL.md` | `reports/appsec/skills/pasta-stage-7.json` |

Launch Stage 1 as a Task call, wait for it to complete, then launch Stage 2,
and so on through Stage 7. Each stage reads the PREVIOUS stage's file
instead of receiving inline output.

**PASTA stage prompt template:**

```
Analyze the following project for {STAGE_DESCRIPTION}:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{PASTA_SKILL_NAME}/SKILL.md

STEP 2: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 3: Read the previous stage output at:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/pasta-stage-{N-1}.json
(Skip this step for Stage 1 -- there is no prior stage.)

STEP 4: Follow the workflow defined in the skill. Use the previous stage's
output as input context for your analysis.

STEP 5: Write your output using the AGGREGATE OUTPUT format to:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/pasta-stage-{N}.json

Use the Write tool. The file must be a JSON object with fields:
  tool, total_findings, by_severity (object with critical/high/medium/low counts),
  notes (string with your FULL stage narrative -- business objectives, scope analysis,
  decomposition, threat list, etc. as appropriate for this stage),
  findings (array)

The "notes" field is REQUIRED. Include the complete stage output narrative.

FLAGS: --scope full --depth expert

IMPORTANT: After writing the file, return ONLY a one-line status in this exact format:
"pasta-stage-{N}: N findings (Xc Xh Xm Xl)"
Do NOT return the stage output itself.
```

### Phase 3: Wait for All Framework Results

**CRITICAL -- Do NOT proceed to Phase 4 until every subagent from Phase 2
has returned.** Do NOT:
- Redo failed subagent work yourself.
- Skip frameworks that are still running.
- Start assembling the report before all results are in.

If a subagent fails, note the failure. Include it in the report as a gap.
Do NOT retry or redo it yourself.

### Timeout Handling

- **Individual subagent timeout**: 5 minutes. If a subagent has not returned after 5 minutes, mark it as TIMED OUT and proceed without its results.
- **PASTA pipeline timeout**: 15 minutes total for all 7 stages.
- **Total audit timeout**: 30 minutes for all phases combined.
- **Progress reporting**: After each subagent returns, output a brief progress line: `[audit] Completed: <skill-name> (<N> findings). Waiting for <M> more subagents.`
- **Timed-out subagents**: List in the report under a TIMED OUT section, distinct from TOOLS FAILED.

### Phase 4: Red Team Simulation (6 Agents in Parallel)

Unless `--skip-redteam` is set, launch ALL 6 red team attacker agents in parallel.

**CRITICAL**: All 6 Task tool calls MUST appear in the SAME response.

Before dispatching, create the output directory:

```bash
mkdir -p reports/appsec/redteam
```

| Agent | Persona File | Focus |
|-------|-------------|-------|
| Script Kiddie | `agents/script-kiddie.md` | Automated tools, known CVEs |
| Insider | `agents/insider.md` | Privilege escalation, exfiltration |
| Organized Crime | `agents/organized-crime.md` | Financial fraud, account takeover |
| Hacktivist | `agents/hacktivist.md` | Data leaks, defacement |
| Nation State | `agents/nation-state.md` | APT chains, persistent access |
| Supply Chain | `agents/supply-chain.md` | Dependency poisoning, build pipeline |

Each red team agent reads prior findings from files (not inline), writes
findings to a file, and returns only a one-line status.

```
You are a red team agent. Read your persona definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/agents/{PERSONA_NAME}.md

Analyze the following codebase for exploitable vulnerabilities from your
persona's perspective:

FILES:
{FILE_LIST}

STEP 1: Read prior findings from these directories using the Read tool:
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/scanners/*.json
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/*.json
These contain the automated analysis results. Use Glob to list the files, then
read each one.

STEP 2: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 3: Read the DREAD scoring framework at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/frameworks/dread.md

STEP 4: Attempt to chain vulnerabilities into multi-step attack scenarios.
Score each finding using DREAD.

STEP 5: Write findings using the AGGREGATE OUTPUT format from the findings schema to:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/redteam/{PERSONA_NAME}.json

Use the Write tool. The file must be a JSON object with fields:
  tool, total_findings, by_severity (object with critical/high/medium/low counts),
  notes (string with your FULL attack narratives, chain descriptions, and DREAD
  scoring rationale -- the report assembler will include this verbatim),
  findings (array)

If zero findings, write: {"tool":"{PERSONA_NAME}","total_findings":0,"by_severity":{"critical":0,"high":0,"medium":0,"low":0},"notes":"<your assessment narrative>","findings":[]}

Use "RT" prefix for finding IDs.

IMPORTANT: After writing the file, return ONLY a one-line status in this exact format:
"{PERSONA_NAME}: N findings (Xc Xh Xm Xl)"
where N is the total count and Xc/Xh/Xm/Xl are counts per severity (critical, high, medium, low).
Example: "insider: 4 findings (1c 2h 1m 0l)"
Do NOT return the findings themselves.
```

### Phase 5: Report Assembly (Report Assembler Subagent)

After ALL subagents (framework skills and optionally red team agents) return,
the main agent builds a status summary and launches ONE report assembler
subagent. The main agent does NOT read any findings files or assemble the
report itself.

#### Build Status Summary

From each subagent's one-line status return, build two lists:

```
tools_ok = []      # e.g. ["injection: 3 findings (0c 1h 2m 0l)", ...]
tools_failed = []  # e.g. ["crypto: empty output", "ssrf: error ..."]
```

A subagent result goes into `tools_failed` if:
- The Task tool returned an error or exception message
- The subagent returned an empty string
- The subagent's output does not match the pattern "{TOOL_NAME}: N findings (...)"

Record the tool name and the first 100 characters of the response as the error reason.

Do NOT re-read any findings files in the main agent context.

Also include scanner statuses from Phase 1.3:

```
scanners_ok = []      # e.g. ["semgrep: OK", "npm-audit: OK"]
scanners_failed = []  # e.g. ["gitleaks: FAILED (timeout)"]
scanners_missing = [] # e.g. ["trivy", "bandit"]
```

#### Launch Report Assembler Subagent

Launch a single report assembler subagent with the following FULLY self-contained
prompt. This subagent reads all result files, assembles the full dated markdown
report with VERBATIM sections, and writes all output files.

```
You are the appsec full-audit report assembler. Your job is to read all
security findings from scanners, category skills, and red team agents, and
assemble a comprehensive dated Markdown report.

STEP 1: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 2: Read all JSON result files from these directories using Glob + Read:
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/scanners/*.json
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/*.json
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/redteam/*.json  (if directory exists)

For scanner files: each scanner produces its own JSON format. Read the scanner
registry and format reference at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/scanners.md

Convert scanner findings to the standard schema format. Set scanner.confirmed
to true and scanner.name to the scanner name (derived from the filename,
e.g. "semgrep.json" -> "semgrep").

For skill and red team files: these already use the AGGREGATE OUTPUT format
with fields: tool, total_findings, by_severity, notes, findings.

If any file contains malformed JSON that cannot be parsed, log the filename
in a TOOLS DEGRADED list and skip it. Continue processing other files.

STEP 3: For each skill file, extract the "notes" field and all findings.
The notes contain the narrative assessment that must appear VERBATIM in the
corresponding report section. The findings array contains structured findings
in schema format.

STEP 4: Build the full dated Markdown report. Use this structure:

# AppSec Full Audit Report
**Date:** YYYY-MM-DD
**Scope:** {SCOPE_DESCRIPTION}
**Project:** {PROJECT_NAME}
**Stack:** {DETECTED_STACK}

## Executive Summary

### Severity Overview
| Severity | Count |
|----------|-------|
| Critical | N |
| High     | N |
| Medium   | N |
| Low      | N |
| **Total** | **N** |

### Top 5 Priorities
1. <highest severity finding with location and one-line description>
2. ...

### Scanners Used
| Scanner | Status | Findings |
|---------|--------|----------|
| <scanner> | Ran / Not installed | N |

---

## Scanner Results
<Scanner findings converted to standard format>

---

## OWASP Top 10

### A01: Broken Access Control
<VERBATIM notes from access-control.json + formatted findings>

### A02: Cryptographic Failures
<VERBATIM notes from crypto.json + formatted findings>

... (A03 through A10, using skill files: injection, insecure-design,
misconfig, outdated-deps, auth, integrity, logging, ssrf)

---

## STRIDE Threat Model

### S - Spoofing
<VERBATIM notes from spoofing.json + formatted findings>

### T - Tampering
<VERBATIM notes from tampering.json + formatted findings>

... (R from repudiation, I from info-disclosure, D from dos,
E from privilege-escalation)

---

## PASTA Risk Analysis

### Stage 1: Business Objectives
<VERBATIM notes from pasta-stage-1.json + formatted findings>

### Stage 2: Technical Scope
<VERBATIM notes from pasta-stage-2.json + formatted findings>

... (Stages 3 through 7)

---

## LINDDUN Privacy Threats

### L - Linkability
<VERBATIM notes from linking.json + formatted findings>

### I - Identifiability
<VERBATIM notes from identifying.json + formatted findings>

... (N1 from non-repudiation-privacy, D1 from detecting,
D2 from data-disclosure, U from unawareness, N2 from non-compliance)

---

## SANS/CWE Top 25
<VERBATIM notes from sans25.json + formatted findings>

---

## Specialized Analysis

### Secrets Detection
<VERBATIM notes from secrets.json + formatted findings>

### Attack Surface
<VERBATIM notes from attack-surface.json + formatted findings>

### Data Flows
<VERBATIM notes from data-flows.json + formatted findings>

---

## Red Team Simulation

### Script Kiddie
<VERBATIM notes from script-kiddie.json + formatted findings>

### Insider Threat
<VERBATIM notes from insider.json + formatted findings>

### Organized Crime
<VERBATIM notes from organized-crime.json + formatted findings>

### Hacktivist
<VERBATIM notes from hacktivist.json + formatted findings>

### Nation State APT
<VERBATIM notes from nation-state.json + formatted findings>

### Supply Chain
<VERBATIM notes from supply-chain.json + formatted findings>

---

## Cross-Framework Analysis

### Finding Overlap
<Table showing findings that appear in multiple frameworks>

### Coverage Gaps
<Frameworks that found issues others missed>

### Attack Chain Summary
<Red team chains that combine findings across frameworks>

---

## Appendix

### Framework Coverage Matrix
| Finding ID | OWASP | STRIDE | PASTA | LINDDUN | CWE | MITRE |
|-----------|-------|--------|-------|---------|-----|-------|
| ... | ... | ... | ... | ... | ... | ... |

### Tool Failures
<Any subagents that failed, with error details>

### Tools Degraded
<Any files with malformed JSON that were skipped>

### Methodology
This report was generated by the AppSec plugin full audit.
Frameworks: OWASP Top 10 (2021), STRIDE, PASTA, LINDDUN, SANS/CWE Top 25.
Red team personas: Script Kiddie, Insider, Organized Crime, Hacktivist,
Nation State, Supply Chain.

For any tool/framework that has no corresponding file (it was skipped via
--skip-frameworks, or the subagent failed), include the section heading
with a note: "This analysis was not performed. Reason: <reason>."

STEP 5: Write the report to:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/{YYYYMMDD}_report.md

Use the Write tool. If --output was specified, use that filename instead
(still in the reports/appsec/ directory).

STEP 6: Write consolidated state files.

First ensure the output directory exists:
  mkdir -p {ABSOLUTE_PATH_TO_PROJECT}/.appsec

Write:
- {ABSOLUTE_PATH_TO_PROJECT}/.appsec/findings.json -- all findings merged
  into a single aggregate format JSON (for downstream skills like
  /appsec:status, /appsec:fix)
- {ABSOLUTE_PATH_TO_PROJECT}/.appsec/last-run.json -- run metadata:
  {{"timestamp": "<ISO 8601>", "scope": "{SCOPE}", "depth": "expert",
    "mode": "full-audit",
    "tools_run": [...], "tools_failed": [...], "scanners_used": [...],
    "scanners_missing": [...], "total_findings": N,
    "by_severity": {{"critical": N, "high": N, "medium": N, "low": N}},
    "report_file": "reports/appsec/{YYYYMMDD}_report.md"}}

TOOL STATUS (from orchestrator):
Tools OK: {TOOLS_OK_LIST}
Tools failed: {TOOLS_FAILED_LIST}
Scanners OK: {SCANNERS_OK_LIST}
Scanners failed: {SCANNERS_FAILED_LIST}
Scanners missing: {SCANNERS_MISSING_LIST}

CONTEXT:
Scope: {SCOPE}
Project: {PROJECT_NAME}
Stack: {DETECTED_STACK}
Date: {YYYYMMDD}
Output filename: {OUTPUT_FILENAME}
Frameworks skipped: {SKIP_FRAMEWORKS_LIST}

IMPORTANT: After writing all files, return a short completion summary:
"Report written to reports/appsec/{YYYYMMDD}_report.md — N total findings
(Xc critical, Xh high, Xm medium, Xl low). State saved to .appsec/."
Do NOT return the report content itself.
```

## Caching and State

After each run, state is written to `.appsec/`:

| File | Written By | Content |
|------|-----------|---------|
| `.appsec/findings.json` | Phase 5 (report assembler subagent) | Consolidated findings from this audit |
| `.appsec/last-run.json` | Phase 5 (report assembler subagent) | Timestamp, scope, depth, tools used, finding count, report file path |

Intermediate results persist in `reports/appsec/` (subdirectories:
`scanners/`, `skills/`, `redteam/`) until the next run overwrites them.
The dated report lives at `reports/appsec/<YYYYMMDD>_report.md`.

This state powers `/appsec:status` and enables delta detection on
subsequent runs.

## Completion Message

Present the report assembler subagent's returned completion summary to the
user, then show follow-up options:

```
Full audit complete.

Report: reports/appsec/<YYYYMMDD>_report.md
Findings: <total> (<critical> critical, <high> high, <medium> medium, <low> low)
Frameworks: OWASP, STRIDE, PASTA, LINDDUN, SANS/CWE Top 25
Red Team: <N> attack chains identified

  /appsec:explain <ID>    Explain any finding
  /appsec:status           View security dashboard
```
