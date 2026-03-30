---
name: agent-guardrails-update
description: Re-analyze Claude Code session logs against existing agent guardrail rules to measure effectiveness, catch false positives, identify missed anti-patterns, and refine regex patterns. Use when user asks to "update guardrails", "refine guardrail rules", "check guardrail effectiveness", "agent-guardrails update", "tune guardrails", or wants to improve existing behavioral rules based on real usage data.
---

# Agent Guardrails Update

Re-analyze session logs against installed guardrail rules to measure effectiveness and refine patterns. This is the feedback loop: install rules with `/agent-guardrails:install`, use them for a while, then run `/agent-guardrails:update` to tune.

## Workflow

### Step 1: Load Existing Rules

Read all installed guardrail rules:

```bash
ls .claude/hookify.*.local.md 2>/dev/null
```

For each rule file, extract:
- `name` from frontmatter
- `enabled` status
- `event` type
- `pattern` regex
- `action` (warn/block)

If no rules are installed, tell the user to run `/agent-guardrails:install` first and stop.

### Step 2: Analyze Recent Sessions

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
5. Also runs the full anti-pattern scan using the five baseline regexes below to find **uncovered patterns** — anti-patterns present in logs that no installed rule catches
6. Outputs structured JSON to stdout

**Baseline anti-pattern regexes** (use these for the uncovered-pattern scan):

| Category | Regex |
|----------|-------|
| Speculative Language | `(?i)(probably\|most likely\|possibly\|perhaps\|presumably\|I believe\|I think\|I'?m (fairly \|not entirely \|pretty )?confident\|if I recall correctly\|as far as I know\|from my understanding\|it (seems\|appears) (like\|that\|to be)\|it looks like\|this (looks\|seems) (correct\|right)\|that looks right\|I'?ll? assume\|assuming that\|this should (work\|fix\|resolve\|handle\|do the trick)\|should be fine\|everything should be working\|that should do it\|likely caused by\|might be happening because\|could be (due to\|a\|caused)\|one possible explanation\|a common cause\|may have (already\|been)\|may be (a\|the\|related\|caused)\|might have\|could have been\|not sure (if\|whether\|why\|what)\|I'?m not certain)` |
| Stalling | `(?i)(let me take a step back\|taking a step back\|before I proceed\|before we proceed\|before I continue\|a few things to consider\|there are some considerations\|it'?s worth noting\|it'?s important to note\|one thing to keep in mind\|let me (first )?explain\|to summarize what\|to clarify what\|let me first understand\|let me first check\|now let me also)` |
| Preference-Asking | `(?i)(would you prefer\|would you like me to\|would you rather\|do you want me to\|which approach would you\|which option would you\|what would you prefer\|let me know which\|let me know how you\|there are a few approaches\|there are several options\|here are some options\|which would you like\|happy to go either way\|shall I\|what.*feels right\|which level feels right\|which.*do you (want\|prefer\|think))` |
| False Completion | `(?i)(all done\|all set\|we'?re all set\|we'?re good\|you'?re all set\|that'?s everything\|nothing else needs\|no other changes\|the fix is complete\|implementation is complete\|fully implemented\|fully working\|everything is working\|everything works)` |
| Skipping | `(?i)(i('m\| am) skipping\|skip(ping)? this\|let('s\| us) skip\|we('ll\| will) skip\|i('ll\| will) skip\|the rest (looks\|seems\|is) fine\|everything else (seems\|looks\|is) (correct\|fine\|ok)\|that part should be fine\|should be straightforward\|without (seeing\|running\|testing)\|I haven'?t tested this\|similar changes would be needed\|you get the idea\|the pattern is the same\|and so on\|the other files don'?t need\|don'?t think we need to change\|I won'?t go through every\|and similar for the (other\|rest)\|the same (approach\|pattern\|logic) (applies\|works) for\|I'?ll leave (that\|the rest\|it) (to\|for\|as)\|left as an exercise\|beyond the scope\|outside the scope\|for brevity\|I don'?t have access\|I can'?t access)` |

**Script requirements:**
- Python stdlib only (json, re, os, glob, sys, collections)
- Handle malformed JSONL gracefully
- Skip subagent sessions
- Accept `--days N` argument

### Step 3: Assess Rule Effectiveness

For each installed rule, classify it into one of four states:

#### State: Working Well
- Pattern matches anti-pattern instances correctly
- No evidence of false positives (matches on legitimate content)
- **Action:** Keep as-is. Report match count.

#### State: Too Aggressive (False Positives)
Detected when the pattern matches legitimate assistant text. Common indicators:
- Rule matches inside code blocks or tool output (not assistant prose)
- Rule matches in contexts where the phrase is appropriate (e.g., "I think" in "I think we should" when giving a recommendation the user asked for)
- Very high match count relative to other rules (possible over-triggering)

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

### Step 4: Check for Uncovered Patterns

Compare the full anti-pattern scan results against installed rules. For each anti-pattern category:

- If a rule exists for it → covered (assess effectiveness above)
- If no rule exists → **uncovered gap**

Report uncovered gaps with:
- Category name
- Match count from scan
- Top phrases found
- Recommended rule (use curated rule from `/agent-guardrails:install` if available)

### Step 5: Present Update Report

Format results inline:

```
## Agent Guardrails Update Report

**Rules analyzed:** {count}
**Sessions scanned:** {count}
**Time range:** {date range}

### Rule Effectiveness

| Rule | Status | Matches | Assessment |
|------|--------|---------|------------|
| no-speculative-language | enabled | 23 | Working well |
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

**Suggested new rule:** `hookify.no-apologizing.local.md`
(Use /agent-guardrails:install to add it, or provide custom content below)

### Recommendations

1. **Update no-stalling** — tighten pattern to reduce false positives
2. **Update no-skipping** — expand pattern to catch missed phrases
3. **Install no-apologizing** — new pattern detected, not yet covered
4. **Keep no-speculative-language** — working well, no changes needed
5. **Monitor no-preference-asking** — no data yet, keep enabled
```

### Step 6: Apply Updates

After presenting the report, apply the recommended changes:

1. **For pattern refinements:** Edit the `.claude/hookify.*.local.md` file with the updated regex using the Edit tool
2. **For new rules:** Create the file using the Write tool
3. **Also update** the `hooks/` copy if it exists

After each edit, read the file back to verify the change was applied correctly.

Report what was changed:

```
## Changes Applied

- Updated `.claude/hookify.no-stalling.local.md` — removed "let me first check" from pattern
- Updated `.claude/hookify.no-skipping.local.md` — added 4 new phrases to pattern
- Created `.claude/hookify.no-apologizing.local.md` — new rule

All changes are active immediately.
```

## Edge Cases

**If all rules are working well:** Report that with match counts and congratulate the user on well-tuned rules. Suggest running update again after more sessions accumulate.

**If no session logs exist:** Tell the user to run some sessions first, then come back to update.

**If rules were recently installed (< 2 days):** Note that the sample size is small and results may not be representative. Still run the analysis but flag the limitation.

**If a rule has been customized from the curated version:** Respect the customization. Base refinement suggestions on the user's version, not the curated original.
