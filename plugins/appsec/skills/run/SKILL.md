---
name: run
description: >
  This skill should be used when the user asks to "run security scan",
  "scan for vulnerabilities", "security check", "check security", or
  invokes /appsec:run. Smart orchestrator that detects the tech stack,
  selects relevant security tools, and runs them in parallel.
---

# AppSec Run -- Smart Orchestrator

The primary way to run security analysis. Detects the project's tech stack,
selects the most relevant scanners and category skills, runs everything in
parallel, consolidates results, and optionally launches red team simulation.

This skill is the automated version of `/appsec:start`. Where `start` gives
recommendations and lets the user choose, `run` makes the choices and
executes them. It handles ALL cross-cutting flags and adapts its behavior
to the detected codebase.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This orchestrator supports ALL cross-cutting flags.

| Flag | Orchestrator Behavior |
|------|----------------------|
| `--scope` | Propagated to all scanners and subagents. Default `changed`. |
| `--depth quick` | Scanners only. No code analysis subagents. Fastest mode. |
| `--depth standard` | Scanners + relevant category subagents (default). |
| `--depth deep` | Standard + cross-file data flow tracing + additional frameworks. |
| `--depth expert` | Deep + red team agent simulation with DREAD scoring. |
| `--severity` | Applied during consolidation to filter merged output. |
| `--format` | Applied to final consolidated output. |
| `--only A01,S,secrets` | Run only the listed tools/categories. Accepts OWASP codes (A01-A10), STRIDE letters (S,T,R,I,D,E), and tool names (secrets, deps, surface). |
| `--fix` | Propagated to subagents; each produces fix suggestions inline. |
| `--quiet` | Suppress explanations, output findings only. |
| `--explain` | Add learning material per finding. |
| `--persona all\|insider\|apt\|...` | Select red team personas (requires `--depth expert`). |
| `--skip-redteam` | Skip red team phase even in expert mode. |

## Workflow

### Phase 1: Detection (Main Agent)

Execute these steps sequentially in the main agent context before launching
any subagents. Use Glob, Grep, Read, and Bash tools to gather evidence.

#### Step 1.1: Check for Cached Assessment

Look for `.appsec/start-assessment.json`. If it exists and is fresh (less
than 24 hours old, and manifest files have not changed since), load it and
skip to Step 1.5.

The cached assessment is also stale if any of:
- Scanner availability has changed (a new scanner was installed or one was removed)
- `.appsec/config.yaml` has been modified since the assessment
- The current git branch differs from the branch recorded in the assessment

If no cache exists or it is stale, run Steps 1.2 through 1.4.

#### Step 1.2: Detect Tech Stack

Read project manifests to determine languages, frameworks, and databases.
Check for each of these files using Glob:

| File Pattern | Reveals |
|-------------|---------|
| `package.json` | Node.js, npm dependencies |
| `requirements.txt`, `Pipfile`, `pyproject.toml` | Python |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java/Kotlin |
| `*.csproj`, `*.sln` | .NET/C# |
| `composer.json` | PHP |
| `Dockerfile`, `docker-compose.yml` | Containers |
| `serverless.yml`, `serverless.yaml` | Serverless |
| `**/*.tf` | Terraform IaC |
| `.github/workflows/*.yaml`, `.github/workflows/*.yml` | GitHub Actions CI/CD |

Read each found manifest to extract framework names and notable dependencies.

#### Step 1.3: Detect Architecture & Data Sensitivity

Scan for patterns indicating sensitive data and architecture type:

**Architecture signals:**
- API-only: route handlers without templates, OpenAPI spec
- Full-stack: template engines alongside API, React/Vue/Angular
- GraphQL: `.graphql` files, `graphql` in dependencies
- WebSocket: `ws`, `socket.io` in dependencies
- Serverless: Lambda handlers, Cloud Functions

**Data sensitivity signals:**
- PII: `email`, `phone`, `ssn`, `date_of_birth` in models
- Financial: `stripe`, `paypal`, `card_number`, `transaction`
- Health: `hipaa`, `patient`, `diagnosis`, `medical_record`
- Auth: `jwt`, `oauth`, `bcrypt`, `session`

#### Step 1.4: Detect Installed Scanners

Check PATH for known scanner binaries using Bash `which` commands. Run
these checks in parallel:

```
which semgrep && which bandit && which gosec && which brakeman
which gitleaks && which trufflehog && which trivy && which osv-scanner
which npm && which pip-audit && which cargo-audit
```

Read [`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md)
for the full scanner registry. Only mark language-specific scanners as
relevant if that language is in the detected stack.

#### Step 1.5: Build Execution Plan

Based on detected stack, data sensitivity, architecture, and installed
scanners, build an execution plan that determines:

1. **Which scanners to run** (only those installed and relevant).
2. **Which category skills to dispatch** (based on architecture and data).
3. **Which frameworks to use** (OWASP is always included; STRIDE added for
   apps with user auth; LINDDUN added when PII detected).

**Tool selection rules:**

| Condition | Tools Selected |
|-----------|---------------|
| Always | `secrets`, `misconfig`, `insecure-design` |
| Has user auth | `access-control`, `auth`, `spoofing`, `privilege-escalation` |
| Has database | `injection` |
| Has HTTP client calls | `ssrf` |
| Has dependencies | `outdated-deps` |
| Has logging/audit | `logging`, `repudiation` |
| Has CI/CD | `integrity` |
| Has crypto imports | `crypto` |
| Has PII / GDPR signals | LINDDUN categories (all 7) |
| Has GraphQL | `graphql` (specialized) |
| Has WebSocket | `websocket` (specialized) |
| Has serverless config | `serverless` (specialized) |
| Has file upload | `file-upload` (specialized) |
| Has financial/business logic | `business-logic`, `race-conditions` |
| `--depth deep` or `expert` | `attack-surface`, `data-flows`, `sans25` |
| `--depth expert` | Red team agents (see Phase 4) |

If `--only` is specified, override the automatic selection and dispatch
only the listed tools/categories.

Cache the execution plan to `.appsec/start-assessment.json` with a
timestamp for future reuse.

### Phase 2: Run Scanners (Main Agent)

Create the output directory, then run detected scanners in the main agent
context using Bash. Launch ALL scanner commands in parallel Bash calls
within a SINGLE response.

```bash
mkdir -p reports/appsec/scanners
```

For each detected scanner, use the invocation pattern from
[`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md).
Redirect ALL scanner output to files — the main agent NEVER reads scanner
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
- Track all scanner statuses for the consolidator:
  ```
  scanner_status = []  # list of {scanner, status, file_path, file_size}
  ```

If `--depth quick` is set, skip Phases 3 and 4. Jump directly to Phase 5
and launch the consolidator subagent with scanner results only.

### Phase 3: Dispatch Category Skills (Parallel Subagents)

**CRITICAL**: All Task tool calls MUST appear in the SAME response message.
This is what triggers parallel execution. If you emit them across separate
messages, they run sequentially and waste time.

For each tool in the execution plan, launch a subagent Task call.

#### Resolving the Scope

Before dispatching, resolve the scope to a concrete file list:

| Scope | Resolution |
|-------|-----------|
| `changed` | `git diff HEAD --name-only` |
| `staged` | `git diff --cached --name-only` |
| `branch` | `git diff main...HEAD --name-only` |
| `file:<path>` | The single file |
| `path:<dir>` | `find <dir> -type f` (filtered) |
| `full` | All files in repository |

**Empty scope handling**: If the resolved file list is empty (e.g.,
`--scope changed` on a clean working tree, or `--scope staged` with nothing
staged), do NOT silently proceed with an empty analysis. Instead:

1. Inform the user that the scope resolved to zero files.
2. Suggest alternatives: `--scope full` for the entire repo, `--scope branch`
   for all branch changes, or stage some changes first.
3. Do NOT dispatch any subagents or scanners. Exit early.

For specific scope types, provide actionable error messages:
- `--scope file:<path>`: If the file does not exist, report "File not found:
  \<path\>" and suggest similar filenames using Glob.
- `--scope path:<dir>`: If the directory does not exist, report "Directory
  not found: \<dir\>".
- `--scope module:<name>`: If the module cannot be located, report "Module
  not found: \<name\>".
- `--scope branch`: If on the base branch with no divergence, report "No
  commits ahead of base branch."

#### Subagent Prompt Template

Before dispatching, create the output directory:

```bash
mkdir -p reports/appsec/skills
```

Each subagent Task call must include a FULLY self-contained prompt.
Subagents get their own isolated context window and cannot see the main
conversation. Subagents write their findings to a file and return ONLY
a one-line status summary.

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

STEP 5: Write the complete JSON findings array to:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/{TOOL_NAME}.json
Use the Write tool. The file must contain a valid JSON array of finding objects.

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: After writing the file, return ONLY a one-line status in this exact format:
"{TOOL_NAME}: N findings (Xc Xh Xm Xl)"
where N is the total count and Xc/Xh/Xm/Xl are counts per severity.
Do NOT return the findings themselves. Do NOT produce a summary or
cross-tool analysis. The orchestrator handles consolidation.
```

#### Launching

Emit ALL Task tool calls in a single response:

- `subagent_type`: `"general-purpose"`
- `description`: `"{TOOL_NAME} - {SHORT_DESCRIPTION}"`
- `prompt`: The fully self-contained prompt above, filled in for this tool.

Do NOT emit Task calls one at a time. Do NOT wait between dispatches.

### Phase 4: Red Team Simulation (Expert Mode Only)

If `--depth expert` is set and `--skip-redteam` is NOT set, launch red
team agents AFTER Phase 3 subagents complete. Red team agents read prior
findings from files to build multi-step attack chains.

Before dispatching, create the output directory:

```bash
mkdir -p reports/appsec/redteam
```

#### Red Team Agent Registry

| Agent | Persona File | Focus |
|-------|-------------|-------|
| Script Kiddie | `agents/script-kiddie.md` | Automated tools, known CVEs, low-hanging fruit |
| Insider | `agents/insider.md` | Privilege escalation, data exfiltration, audit gaps |
| Organized Crime | `agents/organized-crime.md` | Financial fraud, payment exploitation, account takeover |
| Hacktivist | `agents/hacktivist.md` | Data leaks, defacement, public embarrassment |
| Nation State | `agents/nation-state.md` | APT chains, supply chain, persistent access |
| Supply Chain | `agents/supply-chain.md` | Dependency poisoning, build pipeline, artifact integrity |

By default, launch all 6 agents. If `--persona` is specified, launch only
the listed personas.

**CRITICAL**: All 6 (or selected) red team Task calls MUST appear in the
SAME response message for parallel execution.

#### Red Team Subagent Prompt Template

```
You are a red team agent. Read your persona definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/agents/{PERSONA_NAME}.md

Analyze the following codebase for exploitable vulnerabilities from your persona's
perspective:

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

STEP 5: Write your findings as a JSON array (prefix "RT") to:
{ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/redteam/{PERSONA_NAME}.json
Use the Write tool. The file must contain a valid JSON array of finding objects.

IMPORTANT: After writing the file, return ONLY a one-line status in this exact format:
"{PERSONA_NAME}: N findings (Xc Xh Xm Xl)"
Do NOT return the findings themselves.
```

### Phase 5: Consolidation (Consolidator Subagent)

After ALL subagents (category skills and optionally red team agents) return,
the main agent builds a status summary and launches ONE consolidator subagent.

#### Build Status Summary

From each subagent's one-line status return, build two lists:

```
tools_ok = []      # e.g. ["injection: 3 findings (0c 1h 2m 0l)", ...]
tools_failed = []  # e.g. ["crypto: empty output", "ssrf: error ..."]
```

A subagent that returned an empty string, errored, or did not match the
expected status format goes into `tools_failed`. Do NOT re-read any
findings files in the main agent context.

Also include scanner statuses from Phase 2:

```
scanners_ok = []      # e.g. ["semgrep: OK", "npm-audit: OK"]
scanners_failed = []  # e.g. ["gitleaks: FAILED (timeout)"]
scanners_missing = [] # e.g. ["trivy", "bandit"]
```

#### Launch Consolidator Subagent

Launch a single consolidator subagent with the following FULLY self-contained
prompt. This subagent reads all result files, merges, deduplicates, and
produces the final report.

```
You are the appsec consolidator. Your job is to merge all security findings
from scanners, category skills, and red team agents into a single deduplicated
report.

STEP 1: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

STEP 2: Read all JSON result files from these directories using Glob + Read:
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/scanners/*.json
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/skills/*.json
- {ABSOLUTE_PATH_TO_PROJECT}/reports/appsec/redteam/*.json  (if directory exists)

For scanner files: each scanner produces its own JSON format. Parse each
scanner's native format and convert findings to the standard schema. Set
scanner.confirmed to true and scanner.name to the scanner name (derived
from the filename, e.g. "semgrep.json" -> "semgrep").

For skill and red team files: these already use the standard schema format.

If any file contains malformed JSON that cannot be parsed, log the filename
in a TOOLS DEGRADED list and skip it. Continue processing other files.

STEP 3: Deduplicate findings.
Two findings are duplicates if they share the same location.file AND
location.line (or overlapping line ranges). When duplicates exist:
- Keep the finding with the higher severity.
- Merge cross-framework references from both.
- Prefer scanner-confirmed findings over heuristic-only.
- Note the duplicate source in the retained finding's description.

STEP 4: Cross-reference each finding. Populate:
- references.cwe: CWE identifier
- references.owasp: OWASP Top 10 category
- references.stride: STRIDE category letter(s)
- references.mitre_attck: ATT&CK technique ID
- references.sans_cwe25: SANS/CWE Top 25 rank if applicable

STEP 5: Rank findings.
Sort: critical > high > medium > low. Within the same severity, sort by
confidence (high > medium > low). Within the same confidence,
scanner-confirmed findings rank higher.

STEP 6: Apply severity filter.
{SEVERITY_FILTER_INSTRUCTION}

STEP 7: Write consolidated output files using the Write tool:
- {ABSOLUTE_PATH_TO_PROJECT}/.appsec/findings.json — the full findings array
  in the aggregate schema format (for downstream skills like /appsec:status,
  /appsec:fix)
- {ABSOLUTE_PATH_TO_PROJECT}/.appsec/last-run.json — run metadata:
  {{"timestamp": "<ISO 8601>", "scope": "{SCOPE}", "depth": "{DEPTH}",
    "tools_run": [...], "tools_failed": [...], "scanners_used": [...],
    "scanners_missing": [...], "total_findings": N,
    "by_severity": {{"critical": N, "high": N, "medium": N, "low": N}}}}

STEP 8: Return the formatted report in {FORMAT} format.

TOOL STATUS (from orchestrator):
Tools OK: {TOOLS_OK_LIST}
Tools failed: {TOOLS_FAILED_LIST}
Scanners OK: {SCANNERS_OK_LIST}
Scanners failed: {SCANNERS_FAILED_LIST}
Scanners missing: {SCANNERS_MISSING_LIST}

CONTEXT:
Scope: {SCOPE}
Depth: {DEPTH}
Stack: {DETECTED_STACK}

For TEXT format (default), use this exact template:

=====================================================
              APPSEC RUN -- Security Scan
=====================================================

SCOPE: {SCOPE_DESCRIPTION}
DEPTH: {DEPTH}
STACK: {DETECTED_STACK}
SCANNERS: <scanner1> OK (N findings)  <scanner2> PARTIAL (warnings)  <scanner3> N/A
WARNINGS:                   (only if any category fell back to pattern-based analysis)
  <category>: No scanner installed. Detection is pattern-based only (higher false-negative risk).
  Recommended: Install <scanner-names> for reliable detection.

FINDINGS: <total> (<critical> critical, <high> high, <medium> medium, <low> low)

---  CRITICAL  ---

  [CRIT-1] <ID>: <title>
  File: <path>:<line>
  <description>
  Fix: <fix.summary>

  [CRIT-2] ...

---  HIGH  ---

  [HIGH-1] ...

---  MEDIUM  ---

  ...

---  LOW  ---

  ...

TOOLS RUN: <list of tools/categories from Tools OK>
TOOLS FAILED: <list from Tools failed, with reasons>
TOOLS DEGRADED: <list of files with malformed JSON, if any>
SCANNERS MISSING: <list from Scanners missing>

=====================================================
  <total> findings saved to .appsec/findings.json
  Run /appsec:explain <ID> for details on any finding
  Run /appsec:run --fix to auto-generate fixes
=====================================================

For JSON format: output the aggregate format from the findings schema.
For SARIF format: output SARIF 2.1.0 for GitHub Security tab integration.
For MARKDOWN format: output a Markdown report with headings, tables, and
code blocks.

IMPORTANT: Return ONLY the formatted report. The orchestrator will present
it directly to the user.
```

### Phase 6: Output

Present the consolidator subagent's returned output directly to the user.
The consolidator already produces the final formatted report (text, JSON,
SARIF, or Markdown), so no reformatting is needed in the main agent.

## Caching and State

After each run, state is written to `.appsec/`:

| File | Written By | Content |
|------|-----------|---------|
| `.appsec/start-assessment.json` | Phase 1 (main agent) | Stack detection, scanner availability, execution plan |
| `.appsec/findings.json` | Phase 5 (consolidator subagent) | Consolidated findings from this run |
| `.appsec/last-run.json` | Phase 5 (consolidator subagent) | Timestamp, scope, depth, tools used, finding count |

Intermediate results persist in `reports/appsec/` (subdirectories:
`scanners/`, `skills/`, `redteam/`) until the next run overwrites them.

This state powers `/appsec:status` and enables delta detection on
subsequent runs.

## Follow-Up Prompt

After presenting results:

```
Next steps:
  /appsec:explain <ID>         Explain any finding in detail
  /appsec:run --fix            Re-run and auto-generate fixes
  /appsec:run --depth expert   Add red team simulation
  /appsec:full-audit           Exhaustive audit with dated report
  /appsec:status               View security dashboard
```
