---
name: agent-guardrails-analyze
description: Scan Claude Code chat session logs for recurring agent anti-patterns (hedging, stalling, skipping, false completions, preference-asking) and produce a ranked report with frequency counts, example excerpts, and suggested guardrail rules. Use when user asks to "analyze sessions for anti-patterns", "find bad patterns in logs", "what anti-patterns am I seeing", "agent-guardrails analyze", or wants data-driven guardrail recommendations.
---

# Agent Guardrails Analyze

Scan Claude Code session logs to detect recurring anti-patterns in assistant responses. Produce a ranked frequency report with excerpts and ready-to-use guardrail rule suggestions.

## Known Anti-Pattern Categories

These are the established categories with proven regex patterns. Scan for ALL of them plus any novel patterns discovered during analysis.

### 1. Speculative Language
**What it looks like:** Hedging, guessing, unverified claims.
**Signal phrases:** "probably", "I think", "this should work", "it seems like", "likely caused by", "may have been", "not sure if", "I'm fairly confident", "if I recall correctly", "as far as I know", "one possible explanation"
**Proven regex:**
```
(?i)(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'?m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'?ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'?m not certain)
```

### 2. Stalling
**What it looks like:** Padding, announcing intent instead of acting, re-explaining known context.
**Signal phrases:** "let me take a step back", "before I proceed", "a few things to consider", "it's worth noting", "let me first understand", "now let me also"
**Proven regex:**
```
(?i)(let me take a step back|taking a step back|before I proceed|before we proceed|before I continue|a few things to consider|there are some considerations|it'?s worth noting|it'?s important to note|one thing to keep in mind|let me (first )?explain|to summarize what|to clarify what|let me first understand|let me first check|now let me also)
```

### 3. Preference-Asking
**What it looks like:** Delegating decisions to user instead of choosing and acting.
**Signal phrases:** "would you prefer", "would you like me to", "shall I", "which option would you", "happy to go either way", "let me know which"
**Proven regex:**
```
(?i)(would you prefer|would you like me to|would you rather|do you want me to|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think))
```

### 4. False Completion
**What it looks like:** Claiming work is done without showing verification output.
**Signal phrases:** "all done", "we're all set", "fully implemented", "everything is working", "the fix is complete"
**Proven regex:**
```
(?i)(all done|all set|we'?re all set|we'?re good|you'?re all set|that'?s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works)
```

### 5. Skipping
**What it looks like:** Glossing over work, hand-waving, leaving things "as an exercise".
**Signal phrases:** "I'm skipping", "the rest looks fine", "without running it", "you get the idea", "for brevity", "beyond the scope", "I don't have access"
**Proven regex:**
```
(?i)(i('m| am) skipping|skip(ping)? this|let('s| us) skip|we('ll| will) skip|i('ll| will) skip|the rest (looks|seems|is) fine|everything else (seems|looks|is) (correct|fine|ok)|that part should be fine|should be straightforward|without (seeing|running|testing)|I haven'?t tested this|similar changes would be needed|you get the idea|the pattern is the same|and so on|the other files don'?t need|don'?t think we need to change|I won'?t go through every|and similar for the (other|rest)|the same (approach|pattern|logic) (applies|works) for|I'?ll leave (that|the rest|it) (to|for|as)|left as an exercise|beyond the scope|outside the scope|for brevity|I don'?t have access|I can'?t access)
```

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
3. Tests each message against ALL five known anti-pattern regexes above
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

**Recommended rule:** `hookify.no-speculative-language.local.md` (see /agent-guardrails:install)

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
