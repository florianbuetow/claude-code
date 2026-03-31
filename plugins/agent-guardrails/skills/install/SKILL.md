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

**Source of truth:** `plugins/agent-guardrails/rules/hookify.no-*.local.md`

| # | Rule | Installed as |
|---|------|-------------|
| 1 | `no-speculative-language` | `.claude/hookify.no-speculative-language.local.md` |
| 2 | `no-stalling` | `.claude/hookify.no-stalling.local.md` |
| 3 | `no-preference-asking` | `.claude/hookify.no-preference-asking.local.md` |
| 4 | `no-false-completion` | `.claude/hookify.no-false-completion.local.md` |
| 5 | `no-skipping` | `.claude/hookify.no-skipping.local.md` |

Read the canonical rule content from the `rules/` directory when installing. Do not hardcode rule content in this skill — the `rules/` files are the single source of truth.

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
