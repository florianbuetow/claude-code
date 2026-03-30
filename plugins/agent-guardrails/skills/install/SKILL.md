---
name: agent-guardrails-install
description: Install agent behavioral guardrail rules into a project's .claude/ directory. Includes a curated set of five battle-tested rules (no-speculative-language, no-stalling, no-preference-asking, no-false-completion, no-skipping) that can be installed immediately, or install custom rules from /agent-guardrails:analyze results. Use when user asks to "install guardrails", "set up agent guardrails", "add behavioral hooks", "agent-guardrails install", or wants to enforce assistant discipline. Requires the hookify plugin as the runtime engine.
---

# Agent Guardrails Install

Install agent behavioral guardrail rules into the current project. Includes five battle-tested curated rules ready for immediate use, plus support for custom rules from analysis results.

These rules are enforced by the [hookify](https://github.com/anthropics/claude-plugins-official) plugin, which provides the runtime engine that loads and evaluates `.claude/hookify.*.local.md` rule files on every tool use and stop event.

## Prerequisites

The hookify plugin must be installed for these rules to take effect. Verify:

```bash
ls ~/.claude/plugins/cache/*/hookify/*/hooks/stop.py 2>/dev/null | head -1
```

If no result, the hookify plugin is not installed. Tell the user to install it first:
```bash
claude plugin install hookify
```

## Curated Rule Set

These five rules are proven in production use. Each targets a specific anti-pattern in assistant behavior.

### Rule 1: no-speculative-language

**File:** `.claude/hookify.no-speculative-language.local.md`

```markdown
---
name: no-speculative-language
enabled: true
event: stop
pattern: (?i)(probably|most likely|possibly|perhaps|presumably|I believe|I think|I'?m (fairly |not entirely |pretty )?confident|if I recall correctly|as far as I know|from my understanding|it (seems|appears) (like|that|to be)|it looks like|this (looks|seems) (correct|right)|that looks right|I'?ll? assume|assuming that|this should (work|fix|resolve|handle|do the trick)|should be fine|everything should be working|that should do it|likely caused by|might be happening because|could be (due to|a|caused)|one possible explanation|a common cause|may have (already|been)|may be (a|the|related|caused)|might have|could have been|not sure (if|whether|why|what)|I'?m not certain)
action: block
---

**Stop - speculative language detected.**

You used hedging or speculative language (e.g., "probably", "I think", "this should work", "it seems like", "likely caused by", "may have been", "not sure if"). Don't guess. Either:
1. **Investigate** to confirm the cause or result, or
2. **State explicitly** what you know and what you don't know.

No hedging. No unverified claims. Verify before asserting.
```

### Rule 2: no-stalling

**File:** `.claude/hookify.no-stalling.local.md`

```markdown
---
name: no-stalling
enabled: true
event: stop
pattern: (?i)(let me take a step back|taking a step back|before I proceed|before we proceed|before I continue|a few things to consider|there are some considerations|it'?s worth noting|it'?s important to note|one thing to keep in mind|let me (first )?explain|to summarize what|to clarify what|let me first understand|let me first check|now let me also)
action: block
---

**Stop - you're stalling instead of acting.**

You used stalling language (e.g., "before I proceed", "let me first understand", "a few things to consider", "it's worth noting"). Stop padding and act:
1. If you need information, **go get it** — don't announce that you will.
2. If you have information, **act on it** — don't re-explain it.
3. If there's a real blocker, **state it directly** in one sentence.
```

### Rule 3: no-preference-asking

**File:** `.claude/hookify.no-preference-asking.local.md`

```markdown
---
name: no-preference-asking
enabled: true
event: stop
pattern: (?i)(would you prefer|would you like me to|would you rather|do you want me to|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think))
action: block
---

**Stop - you're asking for preference instead of acting.**

You asked the user to choose instead of making a decision yourself (e.g., "would you prefer", "would you like me to", "which option", "shall I"). Don't stall by delegating decisions:
1. **Pick the best option** and do it.
2. If genuinely ambiguous with significant trade-offs, **state your recommendation and why**, then act on it.
3. The user can redirect you if they disagree.
```

### Rule 4: no-false-completion

**File:** `.claude/hookify.no-false-completion.local.md`

```markdown
---
name: no-false-completion
enabled: true
event: stop
pattern: (?i)(all done|all set|we'?re all set|we'?re good|you'?re all set|that'?s everything|nothing else needs|no other changes|the fix is complete|implementation is complete|fully implemented|fully working|everything is working|everything works)
action: block
---

**Stop - unverified completion claim detected.**

You claimed the work is complete (e.g., "all done", "fully implemented", "everything works") without showing verification. Don't claim completion without evidence:
1. **Run the tests** or relevant verification commands.
2. **Show the output** proving it works.
3. Only claim completion after verification succeeds.
```

### Rule 5: no-skipping

**File:** `.claude/hookify.no-skipping.local.md`

```markdown
---
name: no-skipping
enabled: true
event: stop
pattern: (?i)(i('m| am) skipping|skip(ping)? this|let('s| us) skip|we('ll| will) skip|i('ll| will) skip|the rest (looks|seems|is) fine|everything else (seems|looks|is) (correct|fine|ok)|that part should be fine|should be straightforward|without (seeing|running|testing)|I haven'?t tested this|similar changes would be needed|you get the idea|the pattern is the same|and so on|the other files don'?t need|don'?t think we need to change|I won'?t go through every|and similar for the (other|rest)|the same (approach|pattern|logic) (applies|works) for|I'?ll leave (that|the rest|it) (to|for|as)|left as an exercise|beyond the scope|outside the scope|for brevity|I don'?t have access|I can'?t access)
action: block
---

**Stop - you're skipping or glossing over work.**

You either announced you're skipping something, or you glossed over details (e.g., "the rest looks fine", "without running it", "similar changes would be needed", "you get the idea", "for brevity", "I don't have access"). Don't skip and don't hand-wave:
1. If something shouldn't be done, **explain why**.
2. If it should be done, **do it**.
3. Never skip without the user's explicit approval.
```

## Workflow

### Step 1: Check Current State

Check what guardrail rules already exist in the project:

```bash
ls .claude/hookify.*.local.md 2>/dev/null
```

Read any existing rules to avoid overwriting customized versions.

### Step 2: Determine What to Install

**If `$ARGUMENTS` contains specific rule names** (e.g., "install no-stalling no-skipping"):
- Install only the named rules from the curated set above.

**If `$ARGUMENTS` mentions "all" or "curated"** (e.g., "install all"):
- Install all five curated rules.

**If `$ARGUMENTS` is empty:**
- Install all five curated rules. This is the default — do not ask the user to choose.

**If `$ARGUMENTS` references analysis results** (e.g., "install from analysis"):
- Use the analysis report from a prior `/agent-guardrails:analyze` run to determine which rules to install.
- If no analysis has been run in this conversation, run `/agent-guardrails:analyze` first, then install based on the top categories.

### Step 3: Create .claude Directory

```bash
mkdir -p .claude
```

### Step 4: Write Rule Files

For each rule to install:

1. If the rule file already exists AND has been customized (content differs from curated version), **skip it** and note that the existing version was preserved.
2. If the rule file already exists and matches the curated version, skip it silently.
3. If the rule file does not exist, create it using the Write tool with the exact content from the curated set above.

`.claude/` is the canonical location for installed rules. The curated rule files also live in this plugin's `rules/` directory as a reference.

### Step 5: Verify Installation

After writing all files, verify they were created correctly:

```bash
ls -la .claude/hookify.*.local.md
```

Read back one of the files to confirm content is correct.

### Step 6: Report Results

Show inline what was installed:

```
## Agent Guardrails Installed

| Rule | Status | Action |
|------|--------|--------|
| no-speculative-language | Installed | block |
| no-stalling | Installed | block |
| no-preference-asking | Installed | block |
| no-false-completion | Installed | block |
| no-skipping | Installed | block |

**Location:** .claude/hookify.*.local.md
**Runtime:** hookify plugin (stop event)
**Effect:** Immediate — no restart needed.

Rules will trigger on the assistant's next stop event. To test, try writing a response with "I think" or "this should work" — the stop hook will block it.

**To customize:** Edit any .claude/hookify.*.local.md file directly.
**To disable:** Set `enabled: false` in the rule's frontmatter.
**To refine:** Run /agent-guardrails:update after using the rules for a few sessions.
```

## Custom Rules

If the user provides a custom behavior description (not one of the five curated rules), create a new rule following this template:

```markdown
---
name: {kebab-case-name}
enabled: true
event: {bash|file|stop|prompt|all}
pattern: {regex pattern}
action: {warn|block}
---

**{Title of the violation}**

{Explanation of what was detected and why it's problematic.}

{Numbered steps for how to correct the behavior:}
1. {Step 1}
2. {Step 2}
3. {Step 3}
```

**Naming convention:** Start with `no-` for blocking rules, `warn-` for warning rules.

**Event selection:**
- `stop` — for assistant behavioral patterns (language, claims, stalling)
- `bash` — for dangerous shell commands
- `file` — for problematic code patterns in edits
- `prompt` — for user prompt validation
