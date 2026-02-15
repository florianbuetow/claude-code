# AppSec File-Based Output Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prevent context window overflow by having appsec subagents write findings to files instead of returning them in context.

**Architecture:** Subagents write JSON to `reports/appsec/{scanners,skills,redteam}/`. Main orchestrator receives only one-line status per agent. A consolidator subagent reads all files, deduplicates, ranks, and returns the final report.

**Tech Stack:** Claude Code plugins (markdown skill definitions), no runtime code

**Design doc:** `docs/plans/2026-02-15-appsec-file-based-pipeline-design.md`

---

### Task 1: Add reports/appsec/ to .gitignore

**Beads:** `claude-code-jy5`

**Files:**
- Modify: `.gitignore`

**Step 1: Add gitignore entry**

Add `reports/` to the project `.gitignore` (transient scan output should not be committed):

```
reports/
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "Add reports/ to .gitignore for appsec scan output"
```

---

### Task 2: Rewrite run/SKILL.md Phase 2 — Scanner file redirect

**Beads:** `claude-code-gwo`

**Files:**
- Modify: `plugins/appsec/skills/run/SKILL.md` (lines 153-202)

**Step 1: Replace Phase 2 scanner section**

Replace the Phase 2 section (lines 153-202) with scanner output redirected to files. The key changes:

1. Add `mkdir -p reports/appsec/scanners` before launching scanners
2. Redirect each scanner's stdout to `reports/appsec/scanners/<scanner>.json`
3. Main agent checks exit codes and file sizes, NOT file contents
4. Parse scanner status from exit code + file existence only

Replace the scanner dispatch pattern:

```markdown
### Phase 2: Run Scanners (Main Agent)

Run detected scanners in the main agent context using Bash. Launch ALL
scanner commands in parallel Bash calls within a SINGLE response.

For each detected scanner, use the invocation pattern from
[`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md).

**Before launching scanners**, create the output directory:

```
mkdir -p reports/appsec/scanners
```

**Scanner dispatch pattern — redirect output to files:**

```
# Run each scanner in parallel Bash calls — redirect to files
semgrep scan --config auto --json --quiet <scope_path> > reports/appsec/scanners/semgrep.json 2>&1
gitleaks detect --source <scope_path> --report-format json --no-banner > reports/appsec/scanners/gitleaks.json 2>&1
npm audit --json > reports/appsec/scanners/npm-audit.json 2>&1    (if Node.js project)
pip-audit --format json > reports/appsec/scanners/pip-audit.json 2>&1    (if Python project)
trivy fs --format json <scope_path> > reports/appsec/scanners/trivy.json 2>&1    (if installed)
```

**IMPORTANT — do NOT read scanner output into context.** After scanners
complete, check each result using ONLY exit code and file size:

```
# Check scanner results without reading content
ls -la reports/appsec/scanners/    (verify files exist and have content)
```

For each scanner, record status based on:
- **File exists and non-empty + exit code 0 or 1**: OK (scanners exit 1 when findings exist)
- **File exists but empty**: FAILED (scanner produced no output)
- **File missing**: FAILED (scanner command errored before writing)
- **Exit code > 1 with non-empty file**: PARTIAL (scanner ran with warnings)

Track scanner statuses for the output summary. The consolidator subagent
(Phase 5) will read and parse the scanner JSON files.
```

The rest of Phase 2 (error handling rules, `--depth quick` early exit) stays the same, except update the `--depth quick` block:

```markdown
If `--depth quick` is set, launch the consolidator subagent (Phase 5)
with only scanner results, then STOP. Skip Phases 3 and 4.
```

**Step 2: Commit**

```bash
git add plugins/appsec/skills/run/SKILL.md
git commit -m "Redirect scanner output to reports/appsec/scanners/ files"
```

---

### Task 3: Rewrite run/SKILL.md Phase 3 — Subagent file output

**Beads:** `claude-code-bzd`

**Files:**
- Modify: `plugins/appsec/skills/run/SKILL.md` (lines 244-281)

**Step 1: Replace the subagent prompt template**

Replace the current template (lines 250-271) with:

````markdown
#### Subagent Prompt Template

Each subagent Task call must include a FULLY self-contained prompt.
Subagents get their own isolated context window and cannot see the main
conversation.

```
Analyze the following files for {TOOL_DESCRIPTION} vulnerabilities:

FILES:
{FILE_LIST}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Follow the workflow defined in that skill to analyze the listed files.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 4: Write findings as a JSON object (using the aggregate output format
from the findings schema) to this file using the Write tool:
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/{TOOL_NAME}.json

Set metadata.tool to "{TOOL_NAME}" and metadata.framework to "{FRAMEWORK}".
If there are zero findings, still write: {"tool":"{TOOL_NAME}","total_findings":0,"findings":[]}

STEP 5: Return ONLY a one-line status in this exact format:
  {TOOL_NAME}: N findings (Xc Xh Xm Xl)

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: Do NOT return findings in your response text. Write them to the
file ONLY. The orchestrator uses a separate consolidation agent to read files.
```
````

Also update the Launching section to include `mkdir -p`:

```markdown
#### Launching

Before emitting Task calls, create the output directory:
```
mkdir -p reports/appsec/skills
```

Emit ALL Task tool calls in a single response:

- `subagent_type`: `"general-purpose"`
- `description`: `"{TOOL_NAME} - {SHORT_DESCRIPTION}"`
- `prompt`: The fully self-contained prompt above, filled in for this tool.

Do NOT emit Task calls one at a time. Do NOT wait between dispatches.
```

**Step 2: Commit**

```bash
git add plugins/appsec/skills/run/SKILL.md
git commit -m "Rewrite subagent prompt to write findings to files"
```

---

### Task 4: Rewrite run/SKILL.md Phase 4 — Red team file output

**Beads:** `claude-code-x5g`

**Files:**
- Modify: `plugins/appsec/skills/run/SKILL.md` (lines 283-329)

**Step 1: Replace the red team subagent prompt template**

Key changes:
1. Red team agents no longer receive `{CONSOLIDATED_FINDINGS_JSON}` inline — instead they read from the skill result files
2. They write to `reports/appsec/redteam/{persona}.json`
3. They return one-line status

Replace the red team prompt template (lines 308-329):

````markdown
#### Red Team Subagent Prompt Template

```
You are a red team agent. Read your persona definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/agents/{PERSONA_NAME}.md

Analyze the following codebase for exploitable vulnerabilities from your persona's
perspective:

FILES:
{FILE_LIST}

STEP 1: Read prior findings from the skill result files in:
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/
Read each .json file in that directory to understand what automated analysis found.

STEP 2: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 3: Read the DREAD scoring framework at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/frameworks/dread.md

STEP 4: Attempt to chain vulnerabilities into multi-step attack scenarios.
Score each finding using DREAD.

STEP 5: Write your findings as a JSON object (aggregate output format) to:
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/redteam/{PERSONA_NAME}.json

Use finding ID prefix "RT". Include attack_chain narratives in each finding's
description field.

STEP 6: Return ONLY a one-line status:
  RT-{PERSONA_NAME}: N findings, M attack chains (Xc Xh Xm Xl)

IMPORTANT: Write findings to the file ONLY. Do NOT return them in your response.
```
````

Also add `mkdir -p` before launching:

```markdown
Before emitting red team Task calls, create the output directory:
```
mkdir -p reports/appsec/redteam
```
```

**Step 2: Commit**

```bash
git add plugins/appsec/skills/run/SKILL.md
git commit -m "Rewrite red team prompt to write findings to files"
```

---

### Task 5: Replace run/SKILL.md Phase 5 — Consolidator subagent

**Beads:** `claude-code-0p4`

**Files:**
- Modify: `plugins/appsec/skills/run/SKILL.md` (lines 331-497, Phase 5 + Phase 6 + Caching + Follow-Up)

**Step 1: Replace Phase 5 consolidation with consolidator subagent**

This is the largest change. The entire Phase 5 (merge, dedup, cross-ref, rank, filter) + Phase 6 (output formatting) moves into a consolidator subagent prompt. The main agent launches ONE consolidator subagent and receives the final report.

Replace everything from `### Phase 5: Consolidation` through the end of the file with:

````markdown
### Phase 5: Consolidation (Consolidator Subagent)

After ALL subagents (category skills and optionally red team agents) have
returned their one-line statuses, launch a SINGLE consolidator subagent
to read the result files, merge, deduplicate, rank, and produce the report.

**IMPORTANT**: Do NOT attempt consolidation in the main agent context.
The consolidator subagent has its own isolated context window and can
read all result files without overflowing the main context.

#### Subagent Failure Tracking

Before launching the consolidator, build a failure list from the one-line
statuses received. If any subagent returned an error instead of the
expected status format, record it:

```
tools_failed = []     # [{tool, reason}]
tools_completed = []  # [{tool, finding_count}]
```

Pass both lists to the consolidator.

#### Consolidator Subagent Prompt

```
You are the findings consolidator. Read all result files, merge, deduplicate,
rank, and produce the final security report.

PROJECT: {PROJECT_ROOT}
SCOPE: {SCOPE}
DEPTH: {DEPTH}
SEVERITY_FILTER: {SEVERITY}
FORMAT: {FORMAT}
STACK: {DETECTED_STACK}
SCANNERS_STATUS: {SCANNER_STATUS_SUMMARY}
TOOLS_COMPLETED: {TOOLS_COMPLETED_LIST}
TOOLS_FAILED: {TOOLS_FAILED_LIST}

STEP 1: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 2: Read all JSON files from these directories:
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/scanners/   (scanner results)
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/     (skill findings)
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/redteam/    (red team, if present)

For scanner files, parse the scanner-specific JSON format and convert findings
to the standard schema format. For skill and redteam files, findings are
already in schema format.

If a file contains malformed JSON:
- Log the filename in TOOLS DEGRADED
- Skip it and continue

STEP 3: MERGE all findings into a single list.

STEP 4: DEDUPLICATE. Two findings are duplicates if they share the same
location.file AND location.line (or overlapping line ranges). When duplicates:
- Keep the finding with the higher severity
- Merge cross-framework references
- Prefer scanner-confirmed over heuristic-only
- Note the duplicate source in the retained finding's description

STEP 5: CROSS-REFERENCE. For each finding, populate:
- references.cwe, references.owasp, references.stride
- references.mitre_attck, references.sans_cwe25

STEP 6: RANK. Sort: critical > high > medium > low. Within same severity,
sort by confidence (high > medium > low). Scanner-confirmed rank higher.

STEP 7: FILTER. If SEVERITY_FILTER is set, remove findings below threshold.

STEP 8: Write consolidated findings to:
  {ABSOLUTE_PATH_TO_PROJECT}/.appsec/findings.json
(This path is used by downstream skills like /appsec:status and /appsec:fix.)

Also write run metadata to:
  {ABSOLUTE_PATH_TO_PROJECT}/.appsec/last-run.json
Include: timestamp, scope, depth, tools list, finding count, scanner statuses.

STEP 9: Return the formatted report. Use FORMAT to determine output style:

--- TEXT FORMAT (default) ---
=====================================================
              APPSEC RUN -- Security Scan
=====================================================

SCOPE: <scope description>
DEPTH: <quick|standard|deep|expert>
STACK: <detected languages, frameworks>
SCANNERS: <scanner1> OK (N findings)  <scanner2> PARTIAL (warnings)  <scanner3> N/A

FINDINGS: <total> (<critical> critical, <high> high, <medium> medium, <low> low)

---  CRITICAL  ---

  [CRIT-1] <ID>: <title>
  File: <path>:<line>
  <description>
  Fix: <fix.summary>

---  HIGH  ---
  ...

---  MEDIUM  ---
  ...

---  LOW  ---
  ...

TOOLS RUN: <list>
TOOLS FAILED: <list with reasons>  (only if any failed)
TOOLS DEGRADED: <list>  (only if malformed output)
SCANNERS MISSING: <scanners not installed>

=====================================================
  <total> findings saved to .appsec/findings.json
  Run /appsec:explain <ID> for details on any finding
  Run /appsec:run --fix to auto-generate fixes
=====================================================

--- JSON FORMAT ---
Output the aggregate format from findings schema with all fields.

--- SARIF FORMAT ---
SARIF 2.1.0 format for GitHub Security tab.

--- MARKDOWN FORMAT ---
Markdown report with headings, tables, code blocks.
```

Launch the consolidator:

- `subagent_type`: `"general-purpose"`
- `description`: `"consolidator - merge and rank all findings"`
- `prompt`: The prompt above, fully filled in.

### Phase 6: Present Results

After the consolidator subagent returns, present its output directly to
the user. Do NOT reformat or summarize — the consolidator already produced
the final report in the requested format.

Then show the follow-up prompt:

```
Next steps:
  /appsec:explain <ID>         Explain any finding in detail
  /appsec:run --fix            Re-run and auto-generate fixes
  /appsec:run --depth expert   Add red team simulation
  /appsec:full-audit           Exhaustive audit with dated report
  /appsec:status               View security dashboard
```

## Caching and State

After each run, state is written by the consolidator subagent to `.appsec/`:

| File | Content |
|------|---------|
| `.appsec/start-assessment.json` | Stack detection, scanner availability, execution plan (written by Phase 1) |
| `.appsec/findings.json` | Consolidated findings from this run (written by consolidator) |
| `.appsec/last-run.json` | Timestamp, scope, depth, tools used, finding count (written by consolidator) |

Intermediate results are in `reports/appsec/` and persist until the next run
overwrites them. They are gitignored.
````

**Step 2: Commit**

```bash
git add plugins/appsec/skills/run/SKILL.md
git commit -m "Replace in-context consolidation with consolidator subagent"
```

---

### Task 6: Rewrite full-audit/SKILL.md for file-based pipeline

**Beads:** `claude-code-1hf`

**Files:**
- Modify: `plugins/appsec/skills/full-audit/SKILL.md`

This task applies the same patterns from Tasks 2-5 to the full-audit skill. The changes are parallel but the full-audit has additional complexity (framework teams, PASTA sequential pipeline, report assembly).

**Step 1: Update Phase 1.3 — Scanner redirect**

Same pattern as Task 2: redirect scanner output to `reports/appsec/scanners/`.

**Step 2: Update Phase 2 — Framework subagent prompts**

Replace the subagent prompt template (lines 146-167) with the file-output version from Task 3. Apply to ALL subagent launches (OWASP, STRIDE, LINDDUN, Specialized, SANS/CWE).

Key difference from `/appsec:run`: the full-audit template previously said "Return your FULL output verbatim." Change this to write to files:

````markdown
```
STEP 4: Write your COMPLETE analysis as a JSON object to:
  {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/{TOOL_NAME}.json

Include all findings in the schema format AND any narrative assessment.
Use the "notes" field in the aggregate output for narrative content.

STEP 5: Return ONLY a one-line status:
  {TOOL_NAME}: N findings (Xc Xh Xm Xl)

IMPORTANT: Write to the file ONLY. Do NOT return findings in your response.
FLAGS: --scope full --depth expert
```
````

Also update the PASTA sequential dispatch to write each stage to `reports/appsec/skills/pasta-stage-N.json`.

**Step 3: Update Phase 4 — Red team file output**

Same pattern as Task 4. Red team agents read prior findings from `reports/appsec/skills/` and write to `reports/appsec/redteam/`.

**Step 4: Replace Phase 5 — Report assembler subagent**

Replace the in-context report assembly with a report-assembler subagent that:
1. Reads ALL JSON files from `reports/appsec/`
2. Reads verbatim content from each file's "notes" field for the full report sections
3. Assembles the dated markdown report
4. Writes to `reports/appsec/<YYYYMMDD>_report.md`
5. Writes `.appsec/findings.json` and `.appsec/last-run.json`
6. Returns the completion summary

The report structure stays the same — the assembler subagent has its own context window to work with all the verbatim outputs that would have overflowed the main context.

````markdown
#### Report Assembler Subagent Prompt

```
You are the full audit report assembler. Read all result files and produce
the comprehensive dated report.

PROJECT: {PROJECT_NAME}
PROJECT_ROOT: {PROJECT_ROOT}
SCOPE: {SCOPE}
STACK: {DETECTED_STACK}
DATE: {YYYY-MM-DD}
OUTPUT_FILE: {OUTPUT_FILENAME}
SCANNERS_STATUS: {SCANNER_STATUS_SUMMARY}
TOOLS_COMPLETED: {TOOLS_COMPLETED_LIST}
TOOLS_FAILED: {TOOLS_FAILED_LIST}

STEP 1: Read ALL JSON files from:
  {PROJECT_ROOT}/reports/appsec/scanners/
  {PROJECT_ROOT}/reports/appsec/skills/
  {PROJECT_ROOT}/reports/appsec/redteam/

STEP 2: Assemble the report following this structure:
[... same report structure as current Phase 5, with sections for each
framework, red team agent, cross-framework analysis, and appendix ...]

For each framework section, use the verbatim "notes" field from the
corresponding skill result file. For findings, use the standard schema.

STEP 3: Write the report to:
  {PROJECT_ROOT}/reports/appsec/{OUTPUT_FILE}

STEP 4: Write consolidated findings to:
  {PROJECT_ROOT}/.appsec/findings.json

STEP 5: Write run metadata to:
  {PROJECT_ROOT}/.appsec/last-run.json

STEP 6: Return the completion summary:
  Full audit complete.
  Report: reports/appsec/{OUTPUT_FILE}
  Findings: N (Xc critical, Xh high, Xm medium, Xl low)
  Frameworks: OWASP, STRIDE, PASTA, LINDDUN, SANS/CWE Top 25
  Red Team: N attack chains identified
```
````

**Step 5: Commit**

```bash
git add plugins/appsec/skills/full-audit/SKILL.md
git commit -m "Rewrite full-audit for file-based pipeline with report assembler"
```

---

## Summary

| Task | Beads | File | What Changes |
|------|-------|------|-------------|
| 1 | jy5 | `.gitignore` | Add `reports/` |
| 2 | gwo | `run/SKILL.md` | Scanner output → files |
| 3 | bzd | `run/SKILL.md` | Subagent prompt → file write + one-liner |
| 4 | x5g | `run/SKILL.md` | Red team prompt → file write + one-liner |
| 5 | 0p4 | `run/SKILL.md` | Consolidation → consolidator subagent |
| 6 | 1hf | `full-audit/SKILL.md` | All phases → file-based + report assembler |

**What stays the same:** All 62 individual skill SKILL.md files, all 7 agent persona files, all shared schemas, hooks, and plugin manifest.
