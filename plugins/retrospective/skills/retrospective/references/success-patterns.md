# Success Patterns — What Good Developer-AI Collaboration Looks Like

> "The best interactions are invisible — the task flows from intent to completion
> without friction."

## Core Idea

Identifying what went well is as important as finding problems. Success patterns are
workflows, habits, and interaction styles that produce efficient, correct results with
minimal wasted effort. Recognizing them helps the developer do more of what works and
provides a baseline for measuring improvements.

Success in developer-AI collaboration is not "the AI did everything automatically."
It's the right division of labor — the developer provides intent, constraints, and
judgment while the AI handles execution, exploration, and boilerplate.

## Detection Heuristics

What to look for in session logs to identify successful patterns:

### Efficient Task Completion
- **Low turn count**: Task completed in 1-3 turns without corrections
- **No sidechains**: Linear conversation path, no abandoned branches
- **No corrections**: User never said "no", "wrong", "not that", "instead"
- **First-attempt success**: Tool calls succeeded without retries
- **Positive emotional signals**: User expressed satisfaction ("perfect", "exactly",
  "nice", "great", "thanks") — these mark interactions worth replicating

### Effective Tool Usage
- **Right tool for the job**: Grep for search, Read for files, not Bash for everything
- **Parallel tool calls**: Multiple independent tool calls in a single response
- **Subagent delegation**: Complex research delegated to Explore or other subagents
- **Minimal redundant reads**: Files read once, not repeatedly

### Good Prompting Patterns
- **Specific requests**: User provided file paths, function names, or clear scope
- **Upfront constraints**: User stated what NOT to do, saving correction cycles
- **Iterative refinement**: User built on Claude's output rather than restarting
- **Context provided**: User shared relevant background, reducing guesswork

### Effective Skill/Plugin Usage
- **Slash commands used**: User invoked skills for structured workflows
- **Plugins leveraged**: Domain-specific plugins used for specialized tasks
- **Hooks working silently**: Pre/post hooks caught issues without manual intervention

## Pattern Catalog

### 1. The Clean Handoff
**What it looks like**: User gives a clear, scoped request. Claude executes in 1-2
turns. Result accepted without modification.

**Evidence in logs**: Short turn sequence, no error tool results, no user corrections,
task-completing message from user ("thanks", "perfect", next topic).

**Why it works**: Clear intent + appropriate scope = efficient execution.

### 2. Effective Delegation
**What it looks like**: Complex or research-heavy tasks delegated to subagents.
Main context stays focused on high-level decisions.

**Evidence in logs**: Agent tool calls with clear prompts, subagent results used
directly without re-research in main context.

**Why it works**: Preserves main context window, parallelizes work, keeps the human
focused on decisions rather than information gathering.

### 3. The Correction-Free Sequence
**What it looks like**: Multiple related tasks completed sequentially, each building
on the last, without the user needing to correct course.

**Evidence in logs**: Multiple tool call sequences with consistent approach, user
confirmations between steps, no "actually" or "wait" messages.

**Why it works**: Good mental model alignment between developer and AI — shared
understanding of the goal and approach.

### 4. Proactive Verification
**What it looks like**: Claude runs tests, linters, or type checkers after making
changes without being asked.

**Evidence in logs**: Bash tool calls for test/lint/typecheck immediately after
Edit/Write tool calls, before reporting completion.

**Why it works**: Catches errors before the developer sees them, reducing
correction cycles.

### 5. Skill-Driven Workflows
**What it looks like**: Developer invokes a skill (slash command) and gets a
structured, comprehensive result in a predictable format.

**Evidence in logs**: Skill tool call followed by reference file reads and structured
output. Minimal post-skill corrections.

**Why it works**: Skills encode best practices and reduce the cognitive load of
formulating complex requests from scratch.

### 6. Good Context Management
**What it looks like**: Long sessions remain productive because context is managed
well — relevant files read at the right time, not too much loaded upfront.

**Evidence in logs**: Targeted file reads (specific files, not entire directories),
subagent delegation for exploration, incremental context building.

**Why it works**: Prevents context window bloat, keeps the AI focused on the
current task.

## Solution-Focused Application

Success patterns are not just things to celebrate — they are tools for fixing problems.
For each success pattern identified, ask: **can this strength be applied to a recurring
failure?**

This is the solution-focused approach: instead of inventing entirely new behaviors to
address weaknesses, deploy existing strengths against them.

**How to connect strengths to weaknesses:**
- Identify the developer's most effective interaction style (e.g., providing file paths
  upfront, using specific constraints, iterating in small steps)
- Look at recurring failures and ask: would applying that same style prevent them?
- If the developer writes excellent prompts for code generation but vague prompts for
  refactoring, the fix is to transfer the specificity habit — not to create a new skill

**Examples of strength transfer:**
- Developer is good at specifying constraints for new code ("don't use library X, follow
  pattern Y") → Apply the same constraint-setting to refactoring requests where scope
  creep is a recurring problem
- Developer effectively delegates research to subagents → Apply the same delegation
  pattern to test writing, which currently happens manually in the main context
- Developer's "finish" workflow (test → lint → commit) works smoothly → Apply the same
  structured sequencing to the "start" workflow, which is currently ad-hoc

When presenting strengths, always note which weaknesses they could address. This makes
the "What Went Well" section actionable rather than purely celebratory.

## What to Highlight in the Report

When reporting on what went well, include:
- **Specific examples**: "The refactoring of auth.py was completed in 2 turns with
  no corrections" — not vague praise
- **Quantitative evidence**: "5 out of 8 tasks completed on first attempt"
- **Patterns to repeat**: Name the pattern so the developer can consciously do it
  again ("your habit of specifying file paths upfront saved an average of 2 turns
  per task")
- **Effective tool/skill usage**: Highlight when the right tool was chosen and
  the result was good
- **Strengths applicable to weaknesses**: For each success pattern, note which failure
  patterns it could address ("your constraint-setting habit works well for code gen —
  applying it to refactoring tasks could prevent the correction spirals seen there")

## False Positives to Avoid

- Short sessions aren't automatically "successful" — they might just be simple tasks
- A session with no corrections might mean the user gave up correcting rather than
  the AI being correct
- Skill usage is only successful if the output was actually useful — check for
  follow-up corrections after skill invocations
