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

Run detected scanners in the main agent context using Bash. Launch ALL
scanner commands in parallel Bash calls within a SINGLE response.

For each detected scanner, use the invocation pattern from
[`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md).

**Scanner dispatch pattern:**

```
# Run each scanner in parallel Bash calls
semgrep scan --config auto --json --quiet <scope_path>
gitleaks detect --source <scope_path> --report-format json --no-banner
npm audit --json    (if Node.js project)
pip-audit --format json    (if Python project)
trivy fs --format json <scope_path>    (if installed)
```

Capture scanner output. Parse JSON results into the findings schema format.
Scanner findings get `scanner.confirmed: true` and the scanner's name in
`scanner.name`.

**Error handling for scanners:**

- **Non-zero exit code**: Many scanners exit non-zero when they find issues
  (e.g., `npm audit` exits 1 when vulnerabilities exist). This is normal.
  Only treat an exit code as a failure if the output is not valid JSON or
  is empty.
- **Malformed JSON output**: If a scanner produces output that cannot be
  parsed as JSON, log the scanner name and skip it. Do not abort the run.
  Include the scanner in the `TOOLS FAILED` section of the output.
- **Timeout**: If a scanner does not return within 120 seconds, skip it
  and note the timeout. Include it in `TOOLS FAILED`.
- **Scanner not found**: If a scanner from the plan is not installed (the
  Bash command fails with "command not found"), note it in `SCANNERS MISSING`
  and continue.
- Track all scanner errors for the output summary:
  ```
  scanner_errors = []  # list of {scanner, error_type, details}
  ```

If `--depth quick` is set, STOP HERE. Output scanner findings only and
skip Phases 3 and 4.

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

STEP 4: Output findings in the schema format. Set metadata.tool to "{TOOL_NAME}"
and metadata.framework to "{FRAMEWORK}".

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: Return ONLY the findings list. Do NOT produce a summary or
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
team agents AFTER Phase 3 consolidation completes. Red team agents receive
the consolidated findings to build multi-step attack chains.

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

PRIOR FINDINGS (from automated analysis):
{CONSOLIDATED_FINDINGS_JSON}

Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

Read the DREAD scoring framework at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/frameworks/dread.md

Attempt to chain vulnerabilities into multi-step attack scenarios. Score each
finding using DREAD. Return ONLY a JSON array of findings with prefix "RT".
```

### Phase 5: Consolidation (Main Agent)

After ALL subagents (category skills and optionally red team agents) return:

**Subagent failure handling**: Before merging, check each subagent's result:

- **Subagent returned empty output or errored**: Record the skill name and
  error. Do NOT redo the subagent's work in the main agent context — this
  would consume the main context window and produce lower quality results.
  Instead, note the gap.
- **Subagent returned malformed output**: If the output is not valid JSON
  or does not match the findings schema, attempt to extract any structured
  findings from the output. If extraction fails, record the skill as failed.
- **Track all failures** in a `tools_failed` list for the output summary.
  Each entry should include the tool name and the reason for failure.

Include a `TOOLS FAILED` section in the output if any subagents failed:
```
TOOLS FAILED:
  <tool_name>  <reason>
  <tool_name>  <reason>
```

This makes gaps visible so the user can rerun specific tools or investigate.

#### 1. Merge Findings

Collect findings from:
- Scanner output (Phase 2)
- Category skill subagents (Phase 3)
- Red team agents (Phase 4, if run)

#### 2. Deduplicate

Two findings are duplicates if they share the same `location.file` AND
`location.line` (or overlapping line ranges). When duplicates exist:
- Keep the finding with the higher severity.
- Merge cross-framework references.
- Prefer scanner-confirmed findings over heuristic-only.
- Note the duplicate in the retained finding's description.

#### 3. Cross-Reference

For each finding, populate cross-framework references:
- `references.cwe`: CWE identifier
- `references.owasp`: OWASP Top 10 category
- `references.stride`: STRIDE category letter(s)
- `references.mitre_attck`: ATT&CK technique ID
- `references.sans_cwe25`: SANS/CWE Top 25 rank if applicable

#### 4. Rank

Sort findings: critical > high > medium > low. Within the same severity,
sort by confidence (high > medium > low). Within the same confidence,
scanner-confirmed findings rank higher.

#### 5. Apply Severity Filter

If `--severity` is set, remove findings below the threshold.

#### 6. Write State

Write consolidated findings to `.appsec/findings.json` for use by
`/appsec:status` and future scans.

### Phase 6: Output

Present the consolidated report in the requested `--format`.

#### Text Format (default)

```
=====================================================
              APPSEC RUN -- Security Scan
=====================================================

SCOPE: <scope description>
DEPTH: <quick|standard|deep|expert>
STACK: <detected languages, frameworks>
SCANNERS: <scanner1> OK  <scanner2> OK  <scanner3> N/A

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

TOOLS RUN: <list of tools/categories that ran>
TOOLS SKIPPED: <list of tools skipped and why>
SCANNERS MISSING: <scanners that would help but are not installed>

=====================================================
  <total> findings saved to .appsec/findings.json
  Run /appsec:explain <ID> for details on any finding
  Run /appsec:run --fix to auto-generate fixes
=====================================================
```

#### JSON Format

Output the aggregate format from `shared/schemas/findings.md` with all
fields populated.

#### SARIF Format

Output SARIF 2.1.0 format for GitHub Security tab integration. Each
finding maps to a SARIF result with location, message, and rule metadata.

#### Markdown Format

Output a Markdown report with headings, tables, and code blocks suitable
for wiki or README inclusion.

## Caching and State

After each run, write state to `.appsec/`:

| File | Content |
|------|---------|
| `.appsec/start-assessment.json` | Stack detection, scanner availability, execution plan |
| `.appsec/findings.json` | Consolidated findings from this run |
| `.appsec/last-run.json` | Timestamp, scope, depth, tools used, finding count |

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
