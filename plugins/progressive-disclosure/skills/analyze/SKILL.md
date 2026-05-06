---
name: progressive-disclosure:analyze
description: This skill should be used when the user asks to "analyze documentation structure", "audit progressive disclosure", "map documentation references", "find orphaned docs", "check context rot risk", "audit CLAUDE.md", "audit AGENTS.md", or wants to understand how a repository's documentation is structured for AI agent consumption. Produces a disclosure map, orphan report, and anti-pattern findings.
---

# Analyze Progressive Disclosure

Audit how a repository progressively discloses its documentation through soul files. Produce a structured report covering the disclosure hierarchy, reference graph, orphaned documents, anti-patterns, and actionable recommendations.

## Concepts

Progressive disclosure for AI agents operates on three layers:

- **Layer 1 — Discovery**: Lightweight metadata always loaded at session start (soul file names, one-line descriptions, file indexes). Consumes minimal instruction budget.
- **Layer 2 — Activation**: Specific instructional files fetched on-demand when the agent identifies a relevant task phase. Loaded via conversational links from soul files.
- **Layer 3 — Deep Dive**: Dense reference material, source code, API docs. Loaded only when the agent must execute against detailed content.

Soul files are the Layer 1 entry points. Their quality determines whether the rest of the repository is discoverable.

## Soul File Precedence

When multiple root configuration files exist, precedence is:

1. `AGENTS.md` — vendor-agnostic standard (highest)
2. `CLAUDE.md` — Anthropic-specific
3. `GEMINI.md` — Google-specific
4. `COPILOT.md` — GitHub Copilot-specific
5. `SOUL.md` — identity/persona definition

`README.md` is documentation *about* the project for humans — it belongs *in* the index, not *as* a soul file.

## Workflow

### Step 1: Run Discovery Script

Execute the discovery script to gather raw data:

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/analyze/scripts/discover.sh" "$(pwd)"
```

The `CLAUDE_PLUGIN_ROOT` variable resolves to the plugin's installed location. The script produces five sections: soul files found, documentation files, reference graph, orphan detection, and metrics.

### Step 2: Classify Disclosure Layers

For each soul file found, classify its contents against the three-layer model:

- **Layer 1 content** (belongs in soul file): project description, build commands, file indexes, conversational links to specialized docs
- **Layer 2 content** (should be linked, not inlined): coding conventions, architecture decisions, testing strategies, workflow instructions
- **Layer 3 content** (should never be in a soul file): full API references, schema dumps, extensive code examples, raw data

Flag any Layer 2 or Layer 3 content found inlined in soul files.

### Step 3: Detect Anti-Patterns

Check for these documented failure modes:

| Anti-Pattern | Detection | Severity |
|---|---|---|
| **Monolithic soul file** | CLAUDE.md >300 lines or AGENTS.md >1500 words | High |
| **Missing index** | Soul file has no links to other docs | High |
| **Generic instructions** | Phrases like "write clean code", "follow best practices", "think step by step" | Medium |
| **Style rules in soul file** | Formatting/linting rules that belong in tool config (eslint, prettier) | Medium |
| **Orphaned documentation** | .md files not referenced from any soul file | Medium |
| **Broken references** | Links in soul files pointing to non-existent files | Critical |
| **Duplicate content** | Same instructions in multiple soul files | Medium |
| **No soul files at all** | Repository has zero root configuration files | Critical |

### Step 4: Estimate Instruction Budget Impact

Provide a rough assessment:

- Count distinct imperative instructions in each soul file (lines starting with verbs, bullet points with directives, numbered steps)
- Recall: agents reliably follow ~150-200 instructions total; baseline system prompt consumes ~50
- Flag if soul file instructions exceed ~100 (leaves insufficient budget for task-specific context)

### Step 5: Produce Report

Present findings inline (never hide behind a file path). Structure the report as:

#### 1. Disclosure Map
Visual tree showing soul files → referenced docs → their sub-references. Mark each node with its disclosure layer (L1/L2/L3).

#### 2. Soul File Health
Per-file assessment: word count, line count, instruction estimate, layer violations found.

#### 3. Reference Graph
What links to what. Highlight broken links and circular references.

#### 4. Orphan Report
Documentation files not reachable from any soul file. Group by directory.

#### 5. Anti-Pattern Findings
Each finding with severity, location, and specific remediation.

#### 6. Recommendations
Prioritized list of changes to improve progressive disclosure. Lead with highest-impact, lowest-effort items. When restructuring would help, suggest running `progressive-disclosure:restructure`.

### Presentation Rules

- Show all findings inline — never say "see the report file"
- Use tables for structured data, trees for hierarchies
- Lead with the most critical findings
- Quantify: "CLAUDE.md has 847 words across 312 lines — 2.8x the recommended maximum"
- End with a clear next-step recommendation
