---
name: progressive-disclosure:analyze
description: This skill should be used when the user asks to "analyze documentation structure", "audit progressive disclosure", "map documentation references", "find orphaned docs", "check context rot risk", "audit CLAUDE.md", "audit AGENTS.md", or wants to understand how a repository's documentation is structured for AI agent consumption. Produces a disclosure map, orphan report, and anti-pattern findings.
disable-model-invocation: false
---

# Analyze Progressive Disclosure

Audit how a repository progressively discloses its documentation through root configuration files. Produce a structured report covering the disclosure hierarchy, reference graph, orphaned documents, anti-patterns, and actionable recommendations.

## Concepts

Progressive disclosure for AI agents operates on three layers:

- **Layer 1 — Discovery**: Lightweight metadata always loaded at session start (root configuration file names, one-line descriptions, file indexes). Consumes minimal instruction budget.
- **Layer 2 — Activation**: Specific instructional files fetched on-demand when the agent identifies a relevant task phase. Loaded via conversational links from root configuration files.
- **Layer 3 — Deep Dive**: Dense reference material, source code, API docs. Loaded only when the agent must execute against detailed content.

Root configuration files are the Layer 1 entry points. Their quality determines whether the rest of the repository is discoverable.

## Git Visibility

When the target is inside a git repository, only **git-tracked** files are part of the repository. Untracked files and gitignored files are treated as **invisible** — they do not appear in the documentation pool, the orphan report, or the metrics, because an agent cloning the repo will never see them. Git never ignores an already-tracked file, so a single "is it tracked?" test enforces both conditions (tracked *and* not ignored).

The one exception is root configuration **entry points** themselves (AGENTS.md, CLAUDE.md, GEMINI.md, …): these are detected by existence, since they are often audited *before* being committed. In its indexed-documentation role, `README.md` follows the visibility rule like any other doc.

If a root configuration file *references* an invisible file, that is a **phantom reference** — the link points at content no one else can load. Flag it and recommend either removing the reference or adding the file to git.

When the target is **not** a git repository, every matching file is included (filesystem walk with standard excludes).

## Symbolic Links

Two paths can be the same underlying file via a symbolic link — most commonly `CLAUDE.md` symlinked to `AGENTS.md`. The discovery script reports these as `SYMLINK:` lines and `SAME-CONTENT:` groups. Files in a `SAME-CONTENT` group are one file under several names; **never** report them as duplicate content.

## Default File List

When no target is explicitly specified, scan for the following files (in order):

1. `README.md` — human-facing documentation about the project; treat as indexed content, not a configuration entry point
2. `AGENTS.md`
3. `CLAUDE.md`
4. `GEMINI.md`
5. `USER.md`
6. `TOOLS.md`
7. `BOOTSTRAP.md`
8. `DESIGN.md`
9. `NOTICE.md`

## Workflow

### Step 0: Resolve Target File

Check whether the user explicitly named a target file in their prompt (e.g. "analyze `docs/CONTRIBUTING.md`", "audit `README.md`").

- **If a file was named**: scope the analysis to that file only. Skip root configuration file precedence resolution — treat the named file as the subject of Steps 2–5.
- **If no file was named**: analyze all root configuration files found by the discovery script as normal.

### Step 1: Run Discovery Script

Execute the discovery script to gather raw data:

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/analyze/scripts/discover.sh" "$(pwd)"
```

The `CLAUDE_PLUGIN_ROOT` variable resolves to the plugin's installed location. The script produces these sections:

- **Git tracking** — whether the target is inside a git work tree (determines visibility, above)
- **Root configuration files** — entry points found
- **Documentation files** — visible `.md` files (tracked-only inside a git repo)
- **Symlinks** — `SYMLINK:` lines and `SAME-CONTENT:` groups (do not treat grouped files as duplicates)
- **Untracked references** — `UNTRACKED-REF:` phantom references from config files to invisible files
- **Reference graph** — each reference marked `[EXISTS]`, `[UNTRACKED]`, or `[MISSING]`
- **Orphan detection** — visible docs not reachable from any config file
- **Metrics** — counts and budget figures

### Step 2: Classify Disclosure Layers

For each root configuration file found, classify its contents against the three-layer model:

- **Layer 1 content** (belongs in root configuration file): project description, build commands, file indexes, conversational links to specialized docs
- **Layer 2 content** (should be linked, not inlined): coding conventions, architecture decisions, testing strategies, workflow instructions
- **Layer 3 content** (should never be in a root configuration file): full API references, schema dumps, extensive code examples, raw data

Flag any Layer 2 or Layer 3 content found inlined in root configuration files.

### Step 3: Detect Anti-Patterns

Check for these documented failure modes:

| Anti-Pattern | Detection | Severity |
|---|---|---|
| **Monolithic root configuration file** | CLAUDE.md >300 lines or AGENTS.md >1500 words | High |
| **Missing index** | Root configuration file has no links to other docs | High |
| **Generic instructions** | Phrases like "write clean code", "follow best practices", "think step by step" | Medium |
| **Style rules in root configuration file** | Formatting/linting rules that belong in tool config (eslint, prettier) | Medium |
| **Orphaned documentation** | .md files not referenced from any root configuration file | Medium |
| **Broken references** | Links in root configuration files pointing to non-existent files (`[MISSING]`) | Critical |
| **Phantom references** | Links to files that exist on disk but are untracked or gitignored (`UNTRACKED-REF:` / `[UNTRACKED]`) | Critical |
| **Duplicate content** | Same instructions in multiple root configuration files — but first exclude `SAME-CONTENT:` symlink groups, which are one file, not duplicates | Medium |
| **No root configuration files at all** | Repository has zero root configuration files | Critical |

### Step 4: Estimate Instruction Budget Impact

Provide a rough assessment:

- Count distinct imperative instructions in each root configuration file (lines starting with verbs, bullet points with directives, numbered steps)
- Recall: agents reliably follow ~150-200 instructions total; baseline system prompt consumes ~50
- Flag if root configuration file instructions exceed ~100 (leaves insufficient budget for task-specific context)

### Step 5: Produce Report

Present findings inline (never hide behind a file path). Structure the report as:

#### 1. Disclosure Map
Visual tree showing root configuration files → referenced docs → their sub-references. Mark each node with its disclosure layer (L1/L2/L3).

#### 2. Root Configuration File Health
Per-file assessment: word count, line count, instruction estimate, layer violations found.

#### 3. Reference Graph
What links to what. Highlight broken links (`[MISSING]`), phantom links to untracked/gitignored files (`[UNTRACKED]`), and circular references. For each phantom reference, recommend removing the reference or adding the target to git.

#### 4. Orphan Report
Documentation files not reachable from any root configuration file. Group by directory.

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
