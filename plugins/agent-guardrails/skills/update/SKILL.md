---
name: agent-guardrails-update
description: Re-analyze Claude Code session logs against existing agent guardrail rules to measure effectiveness, catch false positives, identify missed anti-patterns, and refine regex patterns. Use when user asks to "update guardrails", "refine guardrail rules", "check guardrail effectiveness", "agent-guardrails update", "tune guardrails", or wants to improve existing behavioral rules based on real usage data.
---

# Agent Guardrails Update

Re-analyze session logs against installed guardrail rules to measure effectiveness and refine patterns. This is the feedback loop: install rules with `/agent-guardrails:install`, use them for a while, then run `/agent-guardrails:update` to tune.

## Workflow

### Step 1: Load Installed Rules

Read the installed guardrail script:

```bash
cat .claude/hooks/stop-guardrails.sh 2>/dev/null
```

Parse each grep block to extract:
- Rule name (from the `# {name}` comment)
- Pattern (from the `grep -qiE` argument)
- Message (from the `blocked+=` argument)

If no script exists, tell the user to run `/agent-guardrails:install` first and stop.

### Step 2: Load Canonical Rule Definitions

Read the canonical rule definitions from the plugin's `rules/` directory:

**Source of truth:** `${CLAUDE_PLUGIN_ROOT}/rules/no-*.md`

Read each rule file's YAML frontmatter to extract `name`, `pattern`, and `message` fields. The six baseline categories are: `no-guessing`, `no-stalling`, `no-preference-asking`, `no-false-completion`, `no-skipping`, `no-dismissing`.

### Step 3: Analyze Recent Sessions

Find session logs from the period since rules were installed. Default to last 7 days; accept `$ARGUMENTS` for custom ranges (e.g., "update last 30 days").

```bash
find ~/.claude/projects/ -name "*.jsonl" -mtime -7 ! -path "*/subagents/*" 2>/dev/null | head -30
```

Build and run a Python analysis script at `/tmp/agent-guardrails-update.py` that:

1. Reads each JSONL session file
2. Extracts assistant message text from `type: "assistant"` entries
3. For each installed rule, tests every assistant message against the rule's regex pattern
4. Records:
   - **Matches per rule** — how many times each rule's pattern was found in raw assistant text
   - **Match excerpts** — 200-char context around each match (up to 10 per rule)
   - **Phrase frequency** — which specific phrases trigger each rule most often
5. Also runs a full anti-pattern scan using the canonical rule definitions to find **uncovered patterns** — anti-patterns present in logs that no installed rule catches
6. Outputs structured JSON to stdout

**Script requirements:**
- Python stdlib only (json, re, os, glob, sys, collections)
- Handle malformed JSONL gracefully
- Skip subagent sessions
- Accept `--days N` argument

### Step 4: Assess Rule Effectiveness

For each installed rule, classify it into one of four states:

#### State: Working Well
- Pattern matches anti-pattern instances correctly
- No evidence of false positives (matches on legitimate content)
- **Action:** Keep as-is. Report match count.

#### State: Too Aggressive (False Positives)
Detected when the pattern matches legitimate assistant text. Common indicators:
- Rule matches inside code blocks or tool output (not assistant prose)
- Rule matches in contexts where the phrase is appropriate (e.g., "I think" in "I think we should" when giving a recommendation the user asked for)
- Very high match count relative to other rules (over-triggering)

**Action:** Suggest tightening the regex. Provide the specific false-positive excerpts and a refined pattern.

#### State: Too Lenient (False Negatives)
Detected when the full anti-pattern scan finds instances that the installed rule misses. Common indicators:
- Novel phrases that express the same anti-pattern but don't match the regex
- Variations or synonyms the pattern doesn't cover
- Multi-sentence hedging that no single-phrase regex catches

**Action:** Suggest expanding the regex with the missed phrases. Provide the specific missed excerpts and an updated pattern.

#### State: Inactive / No Data
- Rule is enabled but had zero matches in the analysis period
- Either the rule is working perfectly (preventing the behavior) or the pattern never triggers

**Action:** Note as "no matches" — cannot determine effectiveness without matches. Suggest the user check if the behavior was actually prevented or if the pattern needs testing.

### Step 5: Check for Uncovered Patterns

Compare the full anti-pattern scan results against installed rules. For each anti-pattern category:

- If a rule exists for it -> covered (assess effectiveness above)
- If no rule exists -> **uncovered gap**

Report uncovered gaps with:
- Category name
- Match count from scan
- Top phrases found
- Recommended rule (use curated rule from `/agent-guardrails:install` if available)

### Step 6: Present Update Report

Format results inline:

```
## Agent Guardrails Update Report

**Rules analyzed:** {count}
**Sessions scanned:** {count}
**Time range:** {date range}

### Rule Effectiveness

| Rule | Status | Matches | Assessment |
|------|--------|---------|------------|
| no-guessing | enabled | 23 | Working well |
| no-stalling | enabled | 5 | Too aggressive (2 false positives) |
| no-preference-asking | enabled | 0 | No data |
| no-false-completion | enabled | 8 | Working well |
| no-skipping | enabled | 12 | Too lenient (missed 4 instances) |

### Detailed Findings

#### no-stalling — Too Aggressive
**False positive excerpts:**
> "...let me first check if the file exists before writing to it..." (line 234, session abc123)
> This is legitimate — checking before writing is correct behavior, not stalling.

**Suggested pattern refinement:**
Remove "let me first check" from the pattern since it often occurs in legitimate pre-action verification.

**Current pattern:**
`(?i)(...|let me first check|...)`

**Proposed pattern:**
`(?i)(...|let me (first )?explain|...)`
(removed "let me first check" — kept "let me first explain" which is actual stalling)

---

#### no-skipping — Too Lenient
**Missed instances:**
> "...I won't bother with the edge cases since they're unlikely..." (not matched)
> "...that's close enough for now..." (not matched)

**Suggested pattern additions:**
Add: `I won'?t bother|close enough|good enough for now|that'?ll do`

**Proposed updated pattern:**
`(?i)(...existing...|I won'?t bother|close enough|good enough for now|that'?ll do)`

---

### Uncovered Gaps

| Category | Matches Found | Has Rule? |
|----------|--------------|-----------|
| Excessive apologizing | 7 | No |

**Suggested new rule:** Add a `# no-apologizing` grep block to `.claude/hooks/stop-guardrails.sh`

### Recommendations

1. **Update no-stalling** — tighten pattern to reduce false positives
2. **Update no-skipping** — expand pattern to catch missed phrases
3. **Install no-apologizing** — new pattern detected, not yet covered
4. **Keep no-guessing** — working well, no changes needed
5. **Monitor no-preference-asking** — no data yet, keep enabled
```

### Step 7: Apply Updates

After presenting the report, apply the recommended changes:

1. **For pattern refinements:** Edit `.claude/hooks/stop-guardrails.sh` with the updated grep pattern using the Edit tool
2. **For new rules:** Add a new grep block to `.claude/hooks/stop-guardrails.sh` following the existing pattern

After each edit, read the file back to verify the change was applied correctly.

Report what was changed:

```
## Changes Applied

- Updated `no-stalling` pattern in `.claude/hooks/stop-guardrails.sh` — removed false-positive trigger
- Updated `no-skipping` pattern in `.claude/hooks/stop-guardrails.sh` — added 4 new phrases
- Added `no-apologizing` rule to `.claude/hooks/stop-guardrails.sh` — new grep block

Script changes are active immediately.
```

## Edge Cases

**If all rules are working well:** Report that with match counts and congratulate the user on well-tuned rules. Suggest running update again after more sessions accumulate.

**If no session logs exist:** Tell the user to run some sessions first, then come back to update.

**If rules were recently installed (< 2 days):** Note that the sample size is small and results may not be representative. Still run the analysis but flag the limitation.

**If the user has custom rules not in the curated set:** Respect the customization. Base refinement suggestions on the user's version, not the curated original.
