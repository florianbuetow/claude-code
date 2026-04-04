---
name: tokeneconomics
description: >
  Analyze Claude Code session token usage to flag waste and optimization
  opportunities. Use when the user asks to "analyze token usage", "check
  token efficiency", "audit token spend", "tokeneconomics", "reduce token
  costs", "optimize token usage", "check my burn rate", or mentions token
  waste, session costs, usage limits, cache efficiency, or conversation
  sprawl.
---

# Token Economics — Usage Analysis & Optimization

Analyze Claude Code session logs to measure token efficiency across six
dimensions: cost, cache efficiency, conversation sprawl, model selection,
output efficiency, and session patterns. Produces a scored report with
risks, opportunities, and actionable recommendations.

## Workflow

### Step 1: Determine scope

From the user's request, determine:
- **Project scope** (default): analyze the current working directory's sessions
- **Global scope**: if the user says "all projects", "everything", "all repos", or "overall"

Also determine the time window:
- Default: 30 days
- Override if the user specifies a different period (e.g., "last week" → 7, "last 3 months" → 90)

### Step 2: Run the analysis

Run the analysis script with the determined scope:

**Project scope:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tokeneconomics.py" --days <N>
```

**Global scope:**
```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tokeneconomics.py" --all --days <N>
```

### Step 3: Present findings

Display the full report output inline. Do NOT hide it behind a file path.

After the report, highlight:
1. The **single highest-impact action** the user can take right now
2. Any **critical** (score 1) or **poor** (score 2) dimensions that need attention

### Step 4: Offer deeper analysis

If the user wants to dig into a specific dimension or session, offer to:
- Read the waste taxonomy reference: `references/waste-taxonomy.md`
- Show the scoring benchmarks: `references/benchmarks.md`
- Run with different time windows or project filters

## Key Rules

- Always show the report inline — never just save to a file
- The report uses API pricing as a proxy; for subscription users, frame costs as
  "relative token burn" that affects usage limits, not actual billing
- Do not editorialize beyond what the data shows — let the numbers speak
- If no usage data is found, check that the project slug matches and suggest
  using `--all` to see all projects
