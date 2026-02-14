---
name: pasta
description: >
  This skill should be used when the user asks to "run PASTA analysis",
  "PASTA threat model", "risk-centric threat analysis", or invokes
  /appsec:pasta. Dispatches 7 stages SEQUENTIALLY -- each stage's output
  feeds the next. This is the ONLY framework that runs sequentially.
---

# PASTA Threat Model Dispatcher (Sequential)

Dispatch 7 PASTA stages in strict sequential order. Unlike all other
framework dispatchers, PASTA runs each stage as a Task, waits for its
output, and passes that output into the next stage's prompt. This is
because PASTA is a risk-centric process where business objectives
(Stage 1) constrain technical scope (Stage 2), which constrains
decomposition (Stage 3), and so on through risk analysis (Stage 7).

**Do NOT run stages in parallel. Do NOT skip stages. Do NOT reorder stages.**

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This dispatcher supports all cross-cutting flags.

| Flag | Dispatcher-Specific Behavior |
|------|------------------------------|
| `--scope` | Propagated to all stages. Default `changed`. Stages 2-3 may expand scope to trace architecture. |
| `--depth` | Propagated to all stages. Default `standard`. |
| `--severity` | Applied to final Stage 7 output to filter the risk-ranked findings. |
| `--format` | Applied to final consolidated output after Stage 7. |
| `--only 1,4,7` | Run only the listed stages (by number 1-7). Prior stages still run if their output is needed. E.g., `--only 5` implicitly runs 1-4 first. |
| `--fix` | Propagated to Stage 5 (vulnerability analysis) and Stage 7 (risk mitigation). |
| `--quiet` | Propagated to all stages; suppress explanations. |
| `--explain` | Propagated to all stages; add learning material per finding. |

## Framework Reference

Read [`../../shared/frameworks/pasta.md`](../../shared/frameworks/pasta.md) for
the full PASTA framework specification including all 7 stage definitions,
cross-framework mappings to OWASP/STRIDE/CWE, and compliance mapping templates.

## Stage Pipeline

The 7 stages execute strictly in order. Each stage is launched as a single
Task tool call, and you MUST wait for it to complete before launching the
next stage.

| Stage | Skill | Output | Feeds Into |
|-------|-------|--------|------------|
| 1. Business Objectives | `skills/pasta-objectives/SKILL.md` | Business context, risk tolerance, compliance requirements | Stage 2 |
| 2. Technical Scope | `skills/pasta-scope/SKILL.md` | Attack surface inventory, entry points, tech stack, DFD | Stage 3 |
| 3. Application Decomposition | `skills/pasta-decompose/SKILL.md` | Component inventory, trust boundaries, role-permission matrix | Stage 4 |
| 4. Threat Analysis | `skills/pasta-threats/SKILL.md` | Threat catalog, MITRE ATT&CK mappings, attack trees | Stage 5 |
| 5. Vulnerability Analysis | `skills/pasta-vulns/SKILL.md` | Vulnerability inventory with CWE mappings, exploitability scores | Stage 6 |
| 6. Attack Simulation | `skills/pasta-attack-sim/SKILL.md` | Exploit chains, DREAD scores, detection gap analysis | Stage 7 |
| 7. Risk & Impact Analysis | `skills/pasta-risk/SKILL.md` | Risk-ranked findings, mitigation roadmap, executive summary | Final output |

## Sequential Dispatch Workflow

### Step 1: Resolve Scope

Parse flags and resolve the target file list per the flags spec. Build the
initial file list that will be passed to Stage 1.

### Step 2: Execute Stages Sequentially

For EACH stage (1 through 7), follow this pattern:

1. **Build the subagent prompt** with all prior stage outputs embedded.
2. **Launch a single Task tool call** for this stage.
3. **Wait for the Task to complete** and capture its full output.
4. **Store the output** for inclusion in subsequent stage prompts.
5. **Proceed to the next stage.**

Do NOT launch the next stage until the current stage has returned.

### Subagent Prompt Template

Each stage gets a FULLY self-contained prompt including all prior outputs:

```
Execute PASTA Stage {N}: {STAGE_NAME}

STEP 1: Read the skill definition at:
{ABSOLUTE_PATH_TO_PLUGIN}/skills/{SKILL_NAME}/SKILL.md

STEP 2: Read the PASTA framework reference at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/frameworks/pasta.md
Focus on the "Stage {N}" section for guidance.

STEP 3: Read the findings schema at:
{ABSOLUTE_PATH_TO_PLUGIN}/shared/schemas/findings.md

PRIOR STAGE OUTPUTS (use these as input for your analysis):
--- Stage 1 Output ---
{STAGE_1_OUTPUT or "N/A - this is Stage 1"}
--- Stage 2 Output ---
{STAGE_2_OUTPUT or "Not yet executed"}
[... include all prior stage outputs ...]

FILES TO ANALYZE:
{FILE_LIST}

FLAGS: --scope {SCOPE} --depth {DEPTH} --severity {SEVERITY}

IMPORTANT: Your output will be passed to Stage {N+1} as input. Structure
your output clearly with headers and sections so the next stage can parse
it. Return your stage-specific output only -- do NOT attempt to execute
later stages.
```

### Stage Execution Details

**Stage 1 -- Business Objectives**: Receives only the file list. Infers
business context from code artifacts (payment processing, PII handling,
authentication flows, admin interfaces). Outputs business context
statement, risk tolerance, and compliance requirements.

**Stage 2 -- Technical Scope**: Receives Stage 1 output plus file list.
Maps entry points, protocols, external dependencies, and tech stack.
May request expanded file scanning to find architecture artifacts
(Dockerfiles, K8s manifests, API gateway configs).

**Stage 3 -- Application Decomposition**: Receives Stages 1-2 output.
Decomposes into components, maps trust boundaries, classifies data
sensitivity, documents auth/authz flows per component.

**Stage 4 -- Threat Analysis**: Receives Stages 1-3 output. Identifies
threats using real-world intelligence, maps to MITRE ATT&CK techniques,
builds attack trees for high-value targets identified in Stage 1.

**Stage 5 -- Vulnerability Analysis**: Receives Stages 1-4 output. Core
code analysis stage. Finds specific weaknesses that enable the threats
from Stage 4. Maps to CWE identifiers. Prioritizes vulnerabilities that
directly enable identified threats over theoretical weaknesses.

**Stage 6 -- Attack Simulation**: Receives Stages 1-5 output. Constructs
multi-step exploit chains combining threats (Stage 4) with vulnerabilities
(Stage 5). Scores each chain with DREAD. Identifies which attacks reach
business-critical assets from Stage 1.

**Stage 7 -- Risk & Impact Analysis**: Receives Stages 1-6 output.
Calculates business-weighted risk scores (Likelihood x Business Impact).
Produces risk-ranked finding list, mitigation roadmap (quick wins / short
term / long term), compliance gap report, and executive summary.

## Consolidation

After Stage 7 completes, the dispatcher:

### 1. Collect All Findings

Gather the final risk-ranked finding list from Stage 7 output. Stage 7
already incorporates context from all prior stages.

### 2. Format Output

Apply the `--format` flag to produce the final output. The Stage 7 output
should already contain:
- Executive summary (non-technical stakeholder audience)
- Risk-ranked finding list with business impact justification
- Mitigation roadmap with effort estimates
- Compliance gap report (if regulatory requirements identified in Stage 1)
- Residual risk assessment

### 3. Apply Severity Filter

If `--severity` is set, filter the finding list to show only findings at
or above the specified severity threshold.

### 4. Cross-Reference

Populate cross-framework references on all findings:
- `references.owasp`: Map to OWASP Top 10 category.
- `references.stride`: Map to STRIDE category letter(s).
- `references.mitre_attck`: Already populated by Stage 4.
- `references.cwe`: Already populated by Stage 5.

### 5. Present Results

Output the final PASTA report. Include the stage progression summary
showing how business objectives flowed through to risk-ranked mitigations.

## Expert Mode

If `--depth expert` is set, after Stage 7 completes, launch red team
subagents with the full PASTA output. Red team agents receive the exploit
chains from Stage 6 and attempt to extend them, finding additional attack
paths or chaining multiple exploit chains together.

Red team findings are appended to the final output with prefix `RT` and
`metadata.tool` set to `"red-team"`.
