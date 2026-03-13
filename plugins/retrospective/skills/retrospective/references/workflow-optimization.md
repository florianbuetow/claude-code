# Workflow Optimization — Subagents, Hooks, and Automation

> "The best workflow optimization is the one that removes a step entirely."

## Core Idea

Beyond skills (which the developer invokes explicitly), Claude Code offers several
automation mechanisms that work silently or semi-automatically: subagents for
delegation, hooks for automated checks, settings for permissions, and CLAUDE.md for
persistent instructions. Session logs reveal which of these mechanisms would reduce
friction in the developer's actual workflow.

The hierarchy of automation options, from most to least autonomous:
1. **Hooks** — run automatically on events, no human action needed
2. **Settings** — configure once, change behavior permanently
3. **CLAUDE.md** — persistent instructions that shape every session
4. **Subagents** — delegated tasks that run in parallel or background
5. **Skills** — developer-invoked structured workflows

## Detection Heuristics

What to look for in session logs to identify optimization opportunities:

### Subagent Opportunities
- **Complex research in main context**: Long Grep/Glob/Read sequences that could be
  delegated to an Explore subagent
- **Independent parallel tasks**: Multiple unrelated tasks done sequentially that
  could run in parallel subagents
- **Context-polluting tasks**: Large file reads or searches that bloat the main
  context when a subagent could summarize the findings
- **Repeated delegation patterns**: Same type of task delegated to subagents
  repeatedly — should be a custom subagent definition

### Hook Opportunities
- **Repeated manual checks**: "Run the tests" / "check types" / "lint this" after
  every edit — should be a PostToolUse hook
- **Repeated pre-action validation**: "Make sure X before doing Y" — should be a
  PreToolUse hook
- **Manual guardrails**: "Don't edit that file" / "Don't push to main" — should be
  a hook that enforces automatically
- **Post-session cleanup**: "Commit everything" / "sync beads" — should be a Stop hook

### Settings Opportunities
- **Permission fatigue**: Rapid-fire approvals for safe operations that could be
  auto-allowed in settings
- **Repeated denials**: Same type of operation always denied — should be in deny list
- **Tool restrictions**: Agent using tools it shouldn't — should be restricted in
  settings

### CLAUDE.md Improvements
- **Repeated context at session start**: User explains the same project context every
  session — should be in CLAUDE.md
- **Repeated constraints**: "We use X not Y", "Always do Z" — should be CLAUDE.md rules
- **Build/test command reminders**: "The test command is..." — should be in CLAUDE.md

## Optimization Catalog

### 1. Custom Subagent Definitions
**Signal**: Same type of task delegated repeatedly, or complex tasks where the prompt
to the subagent is always similar.

**Implementation**: Create a `.claude/agents/[name].md` file with:
```yaml
---
name: [agent-name]
description: [when to use this agent]
allowedTools: [tool list]
model: [sonnet/opus/haiku]
---

[System prompt with instructions for the agent]
```

**Common custom subagent types**:
- **Test writer**: Given a function, generate comprehensive tests
- **PR reviewer**: Review a diff for bugs, style, and conventions
- **Documentation writer**: Generate docs from code
- **Migration helper**: Analyze and plan database/API migrations

### 2. PreToolUse Hooks
**Signal**: User repeatedly says "don't do X" or denies the same type of tool call.

**Implementation**: Add to `.claude/settings.json` or hooks config:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "echo $TOOL_INPUT | grep -q 'dangerous-pattern' && exit 2"
      }
    ]
  }
}
```

**Common hook types**:
- Block writes to protected files (CLAUDE.md, config files)
- Block destructive git commands (force push, reset --hard)
- Block operations on wrong branches
- Validate file paths before edits

### 3. PostToolUse Hooks
**Signal**: User always runs the same check after Claude makes changes.

**Implementation**: Hook that runs automatically after edits:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "run-typecheck-on-changed-file.sh"
      }
    ]
  }
}
```

**Common hook types**:
- Auto-format after file edits
- Run relevant tests after code changes
- Type-check modified files
- Lint changed files

### 4. Permission Tuning
**Signal**: Analysis of tool call approvals/denials reveals patterns.

**Optimization patterns**:
- **Allow safe reads**: File reads, glob searches, grep — low risk, high frequency
- **Allow formatters**: prettier, ruff format, gofmt — safe, deterministic
- **Allow single test runs**: `pytest path/to/test.py` — safe, informative
- **Ask for installs**: pip install, npm install — moderate risk
- **Deny destructive**: rm -rf, git push --force — high risk

### 5. CLAUDE.md Enrichment
**Signal**: Same information provided verbally in multiple sessions.

**What to add**:
- Project build/test/lint commands
- Project architecture overview (key directories, patterns)
- Coding conventions specific to this project
- List of files that should not be modified
- Common pitfalls and how to avoid them
- Links to relevant documentation

### 6. Parallel Workflow Design
**Signal**: Sequential tasks in logs that have no dependencies between them.

**Optimization**: Restructure workflows to use parallel subagents:
- Run tests in one subagent while linting in another
- Research multiple files simultaneously with multiple Explore agents
- Review multiple PRs in parallel

## How to Present Optimization Suggestions

For each suggestion, provide:

1. **Type**: Hook / Subagent / Setting / CLAUDE.md / Workflow change
2. **Evidence**: What session patterns justify it
3. **Concrete config**: The actual JSON/YAML/markdown to add
4. **Before/after**: What the workflow looks like now vs. after the change

## False Positives to Avoid

- Don't suggest hooks for checks that already run in CI — hooks add local latency
  and should only cover the most frequent/valuable checks
- Don't suggest auto-allowing operations that genuinely need review — the goal is
  reducing friction on safe operations, not removing all safety
- Don't suggest subagents for simple tasks — the overhead of spawning a subagent isn't
  worth it for 1-2 tool calls
- Don't suggest CLAUDE.md additions for things the AI can infer from the codebase —
  CLAUDE.md is for non-obvious project conventions
