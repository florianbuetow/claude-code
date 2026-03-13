# Skill Opportunities — Detecting Patterns That Should Be Automated

> "If you've asked for the same thing three times, it should be a slash command."

## Core Idea

Skills (slash commands) and custom subagents are the primary mechanism for encoding
repeatable workflows in Claude Code. A skill transforms a multi-turn manual process
into a single invocation with a predictable, high-quality result. The session logs
contain the raw evidence for which skills the developer actually needs — not
hypothetically, but based on what they actually do repeatedly.

The key signals are **repetition** and **structure**. If a request appears multiple
times with similar wording, it's a skill candidate. If a request always involves the
same sequence of tool calls, it's a strong skill candidate.

## Detection Heuristics

What to look for in session logs to identify skill opportunities:

### Repeated Request Patterns
- **Same phrasing across sessions**: "review this PR", "run the tests and fix failures",
  "update the changelog", "deploy to staging"
- **Same intent, different wording**: "check types" / "run mypy" / "typecheck this"
  all mean the same workflow
- **Same tool sequence triggered**: User asks something → Claude always does the same
  3-5 tool calls in response

### Structured Multi-Step Workflows
- **Predictable sequences**: "first read X, then check Y, then update Z" — always
  the same order
- **Template-like outputs**: Claude produces the same format of output each time
  (tables, reports, summaries)
- **Reference-dependent analysis**: Claude reads the same reference material before
  performing the same type of analysis

### Existing Skill Underuse
- **Installed but unused plugins**: Skills available but never invoked
- **Manual versions of existing skills**: User asks for "code review" manually when
  a code-review skill exists
- **Partial skill usage**: User invokes a skill but then does additional manual steps
  that could be part of the skill

### Configuration-as-Workflow
- **Repeated CLAUDE.md references**: User says "remember, we do X in this project"
  across sessions — should be in CLAUDE.md or a skill
- **Repeated constraints**: "don't touch file X", "always run tests after" — should
  be hooks or settings, not verbal instructions

## Skill Candidate Catalog

### 1. Repeated Analysis/Audit Requests
**Signal**: User asks for the same type of analysis (code review, security check,
architecture assessment) multiple times with similar scope.

**Skill shape**: A slash command that loads references, applies a structured analysis
framework, and produces a consistent report format.

**Examples from common patterns**:
- `/review` — structured code review with checklist
- `/audit-security` — security analysis of recent changes
- `/check-quality` — code quality assessment

**Skeleton**:
```yaml
---
name: [analysis-name]
description: >
  Triggers on "[natural language triggers]". Reads reference files for
  [domain], analyzes [scope], produces [output format].
---
```

### 2. Repeated Build/Test/Deploy Workflows
**Signal**: User regularly asks "run tests", "build and check", "deploy to X" and
Claude performs the same Bash commands each time.

**Skill shape**: A slash command that runs a known sequence of commands and reports
results in a structured way.

**Examples**:
- `/test` — run tests, report failures, suggest fixes
- `/ci` — run the full CI pipeline locally
- `/deploy` — deploy with pre-flight checks

**Note**: These might be better as justfile/Makefile recipes than Claude skills. A
skill is better when it includes AI judgment (interpreting errors, suggesting fixes).

### 3. Repeated Code Generation Patterns
**Signal**: User asks Claude to generate the same type of code structure repeatedly
(new API endpoint, new test file, new component, new migration).

**Skill shape**: A slash command with a template that captures the boilerplate and
lets the user specify only the variable parts.

**Examples**:
- `/new-endpoint` — scaffold a new API endpoint with tests
- `/new-component` — create a React component with standard structure
- `/new-test` — generate a test file following project conventions

### 4. Repeated Documentation/Communication Requests
**Signal**: User asks Claude to write the same type of document (PR description,
commit message, changelog entry, status update).

**Skill shape**: A slash command that gathers context (git diff, recent commits) and
produces a formatted document.

**Examples**:
- `/pr-description` — generate PR description from branch diff
- `/changelog` — generate changelog entry from recent commits
- `/status-update` — summarize session work for a standup

### 5. Bundled Multi-Skill Workflows
**Signal**: User invokes multiple skills or commands in sequence every time they
finish a task.

**Skill shape**: A meta-skill that chains existing skills or commands.

**Examples**:
- `/finish` — run tests + lint + commit + create PR
- `/morning` — check issues + review PRs + pick next task

## Action Quality Tests

Before recommending a skill, evaluate it against these criteria:

### Controllability
Can the developer actually create and maintain this skill? A skill that depends on
external APIs, team-wide process changes, or tools the developer doesn't control is
less likely to be implemented. Prefer skills that are entirely within the developer's
power to create, test, and iterate on.

### Observability
Can you verify from future session logs whether the skill is being used and whether
it's working? This matters for the feedback loop — if a retrospective recommends a
skill and the next retrospective can't tell whether it was created or helped, the
recommendation has no accountability.

Good observability: "Create a /deploy skill" — future logs will show whether `/deploy`
is invoked, how many turns it takes, and whether corrections follow.

Poor observability: "Be more specific when asking for refactoring" — future logs won't
clearly show whether prompts became more specific, because there's no structural marker.

### The Habit Change Test
Skills that replace a manual habit with an automated one are high-value. Skills that
require the developer to remember a new behavior are low-follow-through. When in doubt,
prefer structural enforcement (a skill that asks clarifying questions automatically)
over behavioral advice (a recommendation to "include more context in requests").

Flag items in the Concerns column of the suggestions table when:
- **Not controllable**: Depends on external factors
- **Not measurable from logs**: No way to verify from session data
- **Requires habit change**: Depends on the developer remembering to act differently

## How to Present Skill Suggestions

For each suggested skill, provide:

1. **Name**: Proposed slash command name (`/name`)
2. **Evidence**: What session patterns justify it (with counts)
3. **Trigger phrases**: Natural language triggers for the YAML frontmatter
4. **Workflow**: What the skill would do (numbered steps)
5. **Effort**: How hard to create (most skills are LOW — a SKILL.md file)
6. **Skeleton**: A minimal YAML frontmatter + first paragraph to get started

## Existing Plugin Awareness

Before suggesting a new skill, check if it already exists. Common plugins that
developers forget they have:

- `kiss` — simplification opportunities (user might ask manually for "simplify this")
- `archibald` — architecture quality assessment
- `solid-principles` / `beyond-solid-principles` — design principle audits
- `spec-writer` — specification documents
- `appsec` — application security analysis
- `pr-review-toolkit` — PR review (built-in superpowers agents)

If the user is manually doing what a plugin already does, the suggestion should be
"use the existing plugin" rather than "create a new skill."

## False Positives to Avoid

- A request made twice is an anecdote, not a pattern. Look for 3+ occurrences or
  clear structural repetition
- Some tasks benefit from manual control — deployment, destructive operations, and
  security-sensitive workflows should keep human judgment in the loop
- Don't suggest skills for one-time tasks — skills are for recurring workflows
- Simple tasks (read a file, search for something) don't need skills — they're already
  single commands
