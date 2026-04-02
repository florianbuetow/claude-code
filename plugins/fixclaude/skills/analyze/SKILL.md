---
name: analyze
description: >
  Analyze an existing CLAUDE.md against all 7 Claude Code source leak findings
  and produce a detailed gap report showing which limitations are mitigated,
  partially addressed, or completely unaddressed. Use when the user says
  "fixclaude analyze", "analyze claude md", "check claude md coverage",
  "audit claude directives", or "what's missing from my claude md".
---

# Fix Claude -- Analyze

Analyze an existing CLAUDE.md file against the 7 structural bottlenecks
discovered in the Claude Code source code leak. Produce a gap report explaining
what each issue is, why it matters, and whether the current directives mitigate it.

## Workflow

### Step 1: Resolve and Read Target

```bash
TARGET="CLAUDE.md"
if [ -L "$TARGET" ]; then
  TARGET=$(readlink -f "$TARGET")
  echo "Resolved symlink to: $TARGET"
fi
```

Read the full target file. If it doesn't exist, tell the user to run
`fixclaude:init` first and stop.

### Step 2: Load the Findings

Read the source leak findings reference:

```
${CLAUDE_PLUGIN_ROOT}/skills/analyze/references/source-leak-findings.md
```

This contains all 7 findings with their source locations, problems, check
criteria, and overrides.

### Step 3: Analyze Each Finding

For each of the 7 findings, evaluate the existing CLAUDE.md using the
**"What to check"** criteria from the reference. Rate each finding:

- **MITIGATED** -- The CLAUDE.md contains a directive that fully addresses this issue
- **PARTIAL** -- The CLAUDE.md touches on this but is missing key aspects
- **UNADDRESSED** -- The CLAUDE.md does not address this issue at all

### Step 4: Produce the Report

Present the analysis inline (never hide behind a file path). Use this format:

```
# CLAUDE.md Gap Analysis

Analyzed: <file path>
Lines: <line count>
Date: <today>

## Summary

<X>/7 findings mitigated | <Y>/7 partial | <Z>/7 unaddressed

## Findings

### 1. Employee-Only Verification Gate
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** Claude Code's success metric for file writes is: did bytes hit
disk? Anthropic's internal verification loop (compile check, linter, test suite)
is gated behind `process.env.USER_TYPE === 'ant'`. Their own docs cite a
29-30% false-claims rate.

**Source:** `services/tools/toolExecution.ts`

**Your coverage:** <Explain what the CLAUDE.md does or doesn't do. Quote
relevant lines if present. Be specific about what's missing.>

**Recommended override:** <If not fully mitigated, provide the specific
directive text they should add.>

---

### 2. Context Death Spiral
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** Auto-compaction fires at ~167K tokens. Keeps 5 files (5K tokens
each), compresses everything else into a 50K-token summary. Every file read,
reasoning chain, and intermediate decision is destroyed. Dead code in the
project accelerates this.

**Source:** `services/compact/autoCompact.ts`

**Your coverage:** <...>

**Recommended override:** <...>

---

### 3. The Brevity Mandate
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** System prompt contains: "Try the simplest approach first,"
"Don't refactor code beyond what was asked," "Three similar lines of code is
better than a premature abstraction." These fight user intent when structural
fixes are needed.

**Source:** `constants/prompts.ts`

**Your coverage:** <...>

**Recommended override:** <...>

---

### 4. The Agent Swarm Nobody Told You About
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** Sub-agents run in isolated AsyncLocalStorage with own memory,
compaction cycle, and token budget. No MAX_WORKERS limit. One agent = ~167K
tokens. Five parallel agents = 835K. Users default to single-agent sequential
processing.

**Source:** `utils/agentContext.ts`

**Your coverage:** <...>

**Recommended override:** <...>

---

### 5. The 2,000-Line Blind Spot
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** File reads hard-capped at 2,000 lines / 25,000 tokens.
Everything past that is silently truncated. The agent hallucinates the rest.

**Source:** `tools/FileReadTool/limits.ts`

**Your coverage:** <...>

**Recommended override:** <...>

---

### 6. Tool Result Blindness
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** Tool results exceeding 50,000 characters are persisted to disk
and replaced with a 2,000-byte preview. The agent works from the preview and
doesn't know results were truncated.

**Source:** `utils/toolResultStorage.ts`

**Your coverage:** <...>

**Recommended override:** <...>

---

### 7. grep Is Not an AST
**Status: <MITIGATED|PARTIAL|UNADDRESSED>**

**The issue:** GrepTool is raw text matching. It can't distinguish function
calls from comments or differentiate identically named imports from different
modules. Renames that rely on grep miss dynamic imports, re-exports, and
string references.

**Source:** GrepTool implementation

**Your coverage:** <...>

**Recommended override:** <...>
```

### Step 5: Recommend Next Steps

Based on the gap count:
- **0 unaddressed:** "Your CLAUDE.md covers all known issues. Run `fixclaude:update` if you want to strengthen any partial mitigations."
- **1-3 unaddressed:** "Run `fixclaude:update` to add the missing directives."
- **4+ unaddressed:** "Run `fixclaude:update` for a comprehensive upgrade, or `fixclaude:init` to start fresh with the full template (backs up your existing file first)."

## Important Rules

- Always show the full report inline. Never write it to a file and point to it.
- Quote specific lines from the user's CLAUDE.md when rating coverage.
- Be honest about partial coverage -- don't inflate ratings.
- The analysis must be useful to someone who has never heard of the source leak.
  Each finding section should be self-contained and educational.
