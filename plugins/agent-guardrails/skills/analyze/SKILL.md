---
name: agent-guardrails-analyze
description: Scan Claude Code chat session logs for recurring agent anti-patterns (hedging, stalling, skipping, false completions, preference-asking, dismissing) and produce a ranked report with frequency counts, example excerpts, and suggested guardrail rules. Use when user asks to "analyze sessions for anti-patterns", "find bad patterns in logs", "what anti-patterns am I seeing", "agent-guardrails analyze", or wants data-driven guardrail recommendations.
---

# Agent Guardrails Analyze

Scan Claude Code session logs to detect recurring anti-patterns in assistant responses. Produce a ranked frequency report with excerpts and ready-to-use guardrail rule suggestions.

## Known Anti-Pattern Categories

The canonical regex patterns live in the plugin's `rules/` directory — one `.md` file per category. **Always read the patterns from those files** rather than hardcoding them, so analysis stays in sync with installed/refined rules.

**Source of truth:** `${CLAUDE_PLUGIN_ROOT}/rules/no-*.md`

Read each rule file's YAML frontmatter to extract the `name`, `pattern`, and `message` fields. The six categories are:

| # | Category | Rule file |
|---|----------|-----------|
| 1 | Speculative Language | `no-speculative-language.md` |
| 2 | Stalling | `no-stalling.md` |
| 3 | Preference-Asking | `no-preference-asking.md` |
| 4 | False Completion | `no-false-completion.md` |
| 5 | Skipping | `no-skipping.md` |
| 6 | Dismissing | `no-dismissing.md` |

Scan for ALL of them plus any novel patterns discovered during analysis.

## Workflow

### Step 1: Locate Session Logs

Find recent Claude Code session logs:

```bash
find ~/.claude/projects/ -name "*.jsonl" -mtime -7 ! -path "*/subagents/*" 2>/dev/null | head -30
```

If the user specifies a project or time range, narrow the search accordingly.

### Step 2: Build and Run Analysis Script

Create a Python script at `/tmp/agent-guardrails-analyze.py` that:

1. Reads each JSONL file
2. Extracts assistant message text from `type: "assistant"` entries where `message.content[].type == "text"`
3. Tests each message against ALL six anti-pattern regexes loaded from the `rules/` files (see table above)
4. For each match, records:
   - Category name
   - The matched phrase
   - A 200-character excerpt surrounding the match
   - The session file path
5. Also scans for novel patterns not covered by the five categories:
   - Apologies: "I apologize", "sorry about that", "my mistake"
   - Over-explaining: paragraphs > 500 chars that contain no code blocks
   - Repeating user input: assistant restating what user said before acting
6. Outputs a JSON report to stdout

**Script requirements:**
- Use only Python stdlib (json, re, os, glob, sys, collections)
- Process files in parallel where possible
- Skip subagent session files
- Handle malformed JSON lines gracefully (skip them)
- Accept command-line args: `--days N` (default 7), `--project PATH` (optional filter)

### Step 3: Present Results

Format the analysis as a ranked report, inline in the response:

```
## Agent Guardrails Analysis Report

**Sessions scanned:** {count}
**Time range:** {oldest} to {newest}
**Total anti-pattern matches:** {total}

### Rankings (by frequency)

| # | Category | Matches | % of Total |
|---|----------|---------|------------|
| 1 | Speculative Language | 47 | 38% |
| 2 | Stalling | 28 | 23% |
| 3 | Preference-Asking | 21 | 17% |
| ... | ... | ... | ... |

### Category Details

#### 1. Speculative Language (47 matches)

**Top phrases:**
- "this should work" (12x)
- "I think" (9x)
- "probably" (8x)

**Example excerpts:**
> "...I think this change will fix the issue. The error was probably caused by..."
> "...this should work now. Let me know if..."

**Recommended rule:** Install via /agent-guardrails:install

---
[Continue for each category...]
```

### Step 4: Suggest Next Steps

After presenting the report, state which categories have the highest frequency and recommend running `/agent-guardrails:install` to install rules for them. Do not ask the user which ones they want — recommend based on the data.

## Important Notes

- Always show the report inline — never hide results behind a file path
- Include actual excerpts from the logs so the user can see real examples
- If a category has zero matches, still list it with 0 to show it was checked
- If novel patterns are found that don't fit the five categories, report them in a "Novel Patterns" section
- The analysis script runs locally — no data leaves the machine
