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

Capture all scanner output. Store for report assembly.

### Phase 2: Framework Analysis (Parallel Subagents)

Launch framework dispatchers as parallel subagents. The OWASP, STRIDE,
LINDDUN, and specialized tool subagents run in parallel. PASTA runs
sequentially (its stages are chained).

**CRITICAL**: All parallel Task tool calls MUST appear in the SAME response
message. This is what triggers concurrent execution.

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

Use the same subagent prompt template as `/appsec:run` Phase 3, but with
`--depth expert` and `--scope full` hardcoded into every prompt.

```
Analyze the following files for {TOOL_DESCRIPTION}:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Follow the workflow defined in that skill to analyze the listed files.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 4: Output your COMPLETE analysis. Include all findings in the schema format.
Also include any narrative assessment, evidence, or context your skill produces.
Do NOT summarize or abbreviate -- the full audit preserves verbatim output.

FLAGS: --scope full --depth expert

IMPORTANT: Return your FULL output. Do not abbreviate. The audit report will
include your output verbatim as a dedicated section.
```

#### Sequential: PASTA (7 stages)

After the parallel batch completes (or concurrently if the runtime supports
it), run the PASTA pipeline. PASTA stages are STRICTLY sequential -- each
stage's output feeds the next.

Launch Stage 1 as a Task call, wait for it to complete, then launch Stage 2
with Stage 1's output embedded, and so on through Stage 7.

| Stage | Skill | Description |
|-------|-------|-------------|
| 1 | `skills/pasta-objectives/SKILL.md` | Business Objectives |
| 2 | `skills/pasta-scope/SKILL.md` | Technical Scope |
| 3 | `skills/pasta-decompose/SKILL.md` | Application Decomposition |
| 4 | `skills/pasta-threats/SKILL.md` | Threat Analysis |
| 5 | `skills/pasta-vulns/SKILL.md` | Vulnerability Analysis |
| 6 | `skills/pasta-attack-sim/SKILL.md` | Attack Simulation |
| 7 | `skills/pasta-risk/SKILL.md` | Risk & Impact Analysis |

Use the sequential dispatch pattern from
[`skills/pasta/SKILL.md`](../pasta/SKILL.md) -- each stage prompt includes
all prior stage outputs.

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

| Agent | Persona File | Focus |
|-------|-------------|-------|
| Script Kiddie | `agents/script-kiddie.md` | Automated tools, known CVEs |
| Insider | `agents/insider.md` | Privilege escalation, exfiltration |
| Organized Crime | `agents/organized-crime.md` | Financial fraud, account takeover |
| Hacktivist | `agents/hacktivist.md` | Data leaks, defacement |
| Nation State | `agents/nation-state.md` | APT chains, persistent access |
| Supply Chain | `agents/supply-chain.md` | Dependency poisoning, build pipeline |

Each red team agent receives:
1. The full file list.
2. Their persona definition file path.
3. ALL findings from Phase 2 (so they can chain vulnerabilities).
4. The findings schema path.
5. The DREAD scoring framework path.

```
You are a red team agent. Read your persona definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/agents/{PERSONA_NAME}.md

Analyze the following codebase for exploitable vulnerabilities from your
persona's perspective:

FILES:
{FILE_LIST}

PRIOR FINDINGS (from automated analysis):
{ALL_PHASE_2_FINDINGS}

Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

Read the DREAD scoring framework at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/frameworks/dread.md

Attempt to chain vulnerabilities into multi-step attack scenarios. Score
each finding using DREAD. Return your FULL analysis -- attack narratives,
chain descriptions, and findings with DREAD scores.

IMPORTANT: Return your FULL output verbatim. Do not abbreviate. The audit
report preserves each red team agent's narrative in full.
```

### Phase 5: Report Assembly

Assemble ALL outputs into a single dated Markdown report file. Do NOT
consolidate or summarize subagent outputs -- each appears as its own section
with the agent's raw output preserved verbatim.

#### Report Filename

Default: `<YYYYMMDD>_appsec_report.md` (e.g., `20260214_appsec_report.md`).
Override with `--output <filename>`.

#### Report Structure

```markdown
# AppSec Full Audit Report
**Date:** YYYY-MM-DD
**Scope:** <scope description>
**Project:** <project name>
**Stack:** <detected languages, frameworks, databases>

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
| semgrep | Ran / Not installed | N |
| gitleaks | Ran / Not installed | N |
| ... | ... | ... |

---

## Scanner Results
<Raw scanner output, parsed into findings format>

---

## OWASP Top 10

### A01: Broken Access Control
<Verbatim output from access-control subagent>

### A02: Cryptographic Failures
<Verbatim output from crypto subagent>

... (A03 through A10)

---

## STRIDE Threat Model

### S - Spoofing
<Verbatim output from spoofing subagent>

### T - Tampering
<Verbatim output from tampering subagent>

... (R, I, D, E)

---

## PASTA Risk Analysis

### Stage 1: Business Objectives
<Verbatim output from pasta-objectives subagent>

### Stage 2: Technical Scope
<Verbatim output from pasta-scope subagent>

... (Stages 3 through 7)

---

## LINDDUN Privacy Threats

### L - Linkability
<Verbatim output from linking subagent>

### I - Identifiability
<Verbatim output from identifying subagent>

... (N1, D1, D2, U, N2)

---

## SANS/CWE Top 25
<Verbatim output from sans25 subagent>

---

## Specialized Analysis

### Secrets Detection
<Verbatim output from secrets subagent>

### Attack Surface
<Verbatim output from attack-surface subagent>

### Data Flows
<Verbatim output from data-flows subagent>

---

## Red Team Simulation

### Script Kiddie
<Verbatim output from script-kiddie agent>

### Insider Threat
<Verbatim output from insider agent>

### Organized Crime
<Verbatim output from organized-crime agent>

### Hacktivist
<Verbatim output from hacktivist agent>

### Nation State APT
<Verbatim output from nation-state agent>

### Supply Chain
<Verbatim output from supply-chain agent>

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

### Methodology
This report was generated by the AppSec plugin full audit.
Frameworks: OWASP Top 10 (2021), STRIDE, PASTA, LINDDUN, SANS/CWE Top 25.
Red team personas: Script Kiddie, Insider, Organized Crime, Hacktivist,
Nation State, Supply Chain.
```

#### Writing the Report

Write the assembled report to the output file using the Write tool. Then
write state files:

| File | Content |
|------|---------|
| `<YYYYMMDD>_appsec_report.md` | The full report |
| `.appsec/findings.json` | All findings in JSON format |
| `.appsec/last-run.json` | Timestamp, scope, depth, tool list, finding count |

## Completion Message

After writing the report:

```
Full audit complete.

Report: <YYYYMMDD>_appsec_report.md
Findings: <total> (<critical> critical, <high> high, <medium> medium, <low> low)
Frameworks: OWASP, STRIDE, PASTA, LINDDUN, SANS/CWE Top 25
Red Team: <N> attack chains identified

  /appsec:explain <ID>    Explain any finding
  /appsec:status           View security dashboard
```
