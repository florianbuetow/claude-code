# Failure Patterns — Where Developer-AI Collaboration Breaks Down

> "Every correction the user makes is a signal. Three corrections in a row is a
> workflow problem."

## Core Idea

Failures in developer-AI collaboration are not just bugs or wrong answers. They include
wasted turns, misunderstood intent, abandoned approaches, context loss, and friction
that makes the developer do work the AI should handle. The most costly failures are
silent — the developer adapts around problems instead of fixing the workflow.

Understanding failure patterns is the highest-leverage part of a retrospective because
each failure represents a concrete improvement opportunity.

## Detection Heuristics

What to look for in session logs to identify failures and friction:

### Explicit Corrections
- **"No" / "wrong" / "not that"**: User rejected Claude's output or approach
- **"Instead, do..."**: User redirected after a wrong approach
- **"I already told you..."**: User had to repeat information (context loss)
- **"Stop" / "wait"**: User interrupted an unwanted action
- **Tool use rejected**: User denied a tool call (is_error with rejection message)

### Wasted Effort
- **Abandoned sidechains**: `"isSidechain": true` — conversation paths that were
  abandoned (user went back and tried differently)
- **Repeated tool calls**: Same file read multiple times, same search run twice
- **Long turn sequences for simple tasks**: 5+ turns for what should be 1-2 turns
- **Retry loops**: Same tool call attempted multiple times with errors

### Misunderstandings
- **Scope creep**: Claude changed files the user didn't ask about
- **Wrong file/function**: Claude edited the wrong location
- **Over-engineering**: Claude added unnecessary complexity, abstractions, or features
- **Under-delivery**: Claude did less than asked, requiring follow-up prompts

### Emotional Signals
- **Frustration escalation**: User's tone shifts from collaborative to terse across
  a turn sequence — messages get shorter, corrections get blunter
- **ALL CAPS or exclamation patterns**: "NO, not THAT file" — emotional emphasis
  indicates a repeated misunderstanding
- **Resignation / abandonment**: User says "never mind", "forget it", "I'll do it
  myself" — the worst outcome, because the problem goes unresolved AND the user loses
  trust in the workflow
- **Sarcasm or exasperation**: "sure, whatever", "fine, close enough" — signals that
  the user is accepting a suboptimal result because they've run out of patience
- **Silent topic switch**: User moves to a completely different task mid-conversation
  without the previous task being completed — often means they gave up
- **Positive-then-negative shift**: User starts a session enthusiastically but
  becomes curt later — indicates a specific interaction broke the momentum

These signals are higher-priority than explicit corrections. A user who corrects five
times and gets the right result had a friction-heavy but ultimately successful
interaction. A user who silently gives up had a failed interaction that won't show up
in correction counts.

### Context and Session Issues
- **Context loss after compaction**: Quality degraded partway through a long session
- **Repeated setup**: Same setup/context provided at the start of every session
- **Session too long**: Quality degraded as the session grew
- **Session too fragmented**: Many short sessions with repeated context loading

## Pattern Catalog

### 1. The Correction Spiral
**What it looks like**: User corrects one thing → Claude introduces a new problem while
fixing → user corrects that → cycle continues for 5+ turns.

**Evidence in logs**: Alternating user corrections and Claude edits to the same file,
with each edit introducing a new issue.

**Root cause**: Usually attempting to fix a symptom rather than understanding the
underlying issue. Also happens when Claude doesn't read enough context before editing.

**Improvement opportunity**: Better upfront specification, or a skill that enforces
"read first, then plan, then edit."

### 2. The Wrong Approach
**What it looks like**: Claude spent several turns implementing something, then the
user says "no, that's not what I meant" and they start over.

**Evidence in logs**: Multiple tool calls (5+) followed by a user message that
rejects the entire approach and redirects. Often includes abandoned sidechains.

**Root cause**: Ambiguous request + Claude diving into implementation before
confirming understanding. Or Claude not reading enough code context to understand
the actual architecture.

**Improvement opportunity**: CLAUDE.md instruction to confirm approach before
implementing for non-trivial tasks. Or a planning skill that separates design from
implementation.

### 3. The Repeated Request
**What it looks like**: User asks for the same type of thing in session after session
(e.g., "run the tests", "format the code", "review this PR", "deploy to staging").

**Evidence in logs**: Same or very similar user messages appearing across multiple
sessions. Same tool call sequences triggered manually each time.

**Root cause**: A workflow that should be automated as a skill, slash command, or hook.

**Improvement opportunity**: Create a skill or slash command for the repeated workflow.

### 4. The Manual Multi-Step
**What it looks like**: User walks Claude through a multi-step process step by step,
providing each instruction sequentially.

**Evidence in logs**: User messages that read like a script: "first do X", "now do Y",
"next, Z". Claude executes each step but doesn't connect them into a workflow.

**Root cause**: Complex workflow that the user knows but hasn't encoded into a
reusable format.

**Improvement opportunity**: Bundle the steps into a skill with a single trigger.

### 5. The Permission Fatigue
**What it looks like**: User approves tool calls mechanically, barely reviewing them,
because Claude asks too often for routine operations.

**Evidence in logs**: Rapid succession of tool approvals with no user messages between
them. Or user configures overly permissive settings to avoid the friction.

**Root cause**: Permission configuration too restrictive for the actual risk level.

**Improvement opportunity**: Tune `.claude/settings.json` to allow safe operations
automatically. Add hooks for genuinely risky operations instead.

### 6. The Context Dump
**What it looks like**: User provides a massive amount of context upfront (paste long
files, explain entire architecture) before making a simple request.

**Evidence in logs**: Very long user messages at session start, or user asking Claude
to read many files before the actual task.

**Root cause**: User doesn't trust Claude to find the right context, or CLAUDE.md
doesn't have enough project information.

**Improvement opportunity**: Better CLAUDE.md/AGENTS.md with project structure info.
Or use subagents to explore the codebase rather than manual context loading.

### 7. The Scope Explosion
**What it looks like**: Claude changes files the user didn't ask about, "improves"
code that was fine, or adds features that weren't requested.

**Evidence in logs**: Edit/Write tool calls to files not mentioned in the user's
request. User messages like "don't change that", "revert that", "I only asked for X".

**Root cause**: Missing constraint instructions. Claude defaults to "helpful" which
can mean "do extra work."

**Improvement opportunity**: CLAUDE.md instruction about scope discipline. Or
explicit "only touch files X, Y, Z" in complex requests.

### 8. The Silent Abandonment
**What it looks like**: User stops engaging with a task without resolution. No "that's
wrong" — just a topic change or end of session with work incomplete.

**Evidence in logs**: A task thread (identifiable by topic) that ends without completion
markers (no "thanks", "done", "perfect") and is followed by an unrelated request or
session end. The absence of negative feedback makes this invisible to correction-based
analysis.

**Root cause**: User hit a threshold of frustration or lost confidence that the AI could
complete the task. Often preceded by 2-3 soft corrections that didn't fully resolve the
issue. The user decides the cost of continuing exceeds the cost of doing it themselves.

**Improvement opportunity**: This is the highest-priority failure pattern because it's
invisible without emotional signal detection. The fix depends on the root cause of the
original frustration — but the meta-fix is a CLAUDE.md instruction to notice when a
task thread drops without resolution and explicitly ask "should we continue with X, or
have you moved on?"

## Root Cause Analysis

**Every failure pattern in this catalog includes a "Root cause" field. This is not
optional decoration — it is the most important part of each entry.**

When analyzing session logs, do not stop at identifying which pattern occurred. Ask why
it occurred. The same observable pattern (e.g., "5 correction turns") can have different
root causes:
- Missing context (Claude didn't read enough code before editing)
- Ambiguous request (developer's intent had multiple valid interpretations)
- Wrong tool choice (Claude used Bash when Edit was appropriate)
- Architectural mismatch (Claude's approach didn't fit the existing codebase patterns)

Different root causes demand different fixes. A skill helps with repeated workflows.
A CLAUDE.md rule helps with missing constraints. A hook helps with automated checks.
A process change helps with communication patterns. Matching fix to root cause is what
makes retrospective recommendations actually work — otherwise you're treating symptoms.

## How to Present Failure Findings

When reporting failure patterns, provide paragraph-level evidence with root cause
analysis for each finding. Do not compress into metric bullets.

**Expected depth per finding:**

- **[Problem name]**

  [1-2 sentence summary of the problem.]

  **Evidence:** In session `abc123` (2026-03-01, 890 lines), the user asked to
  "fix the failing integration tests." The assistant edited `test_api.py` without
  first reading the error output. The user corrected: "No, read the test output
  first." The assistant then read the output but misidentified the root cause,
  editing `config.py` instead of `database.py`. The user corrected again: "Wrong
  file — the error is in the database connection setup." After a third correction
  ("don't change the connection string, fix the timeout"), the issue was resolved.
  Total: 9 turns for what should have been a 3-turn fix.

  This pattern also appeared in sessions `def456` (7 correction turns on a
  CSS layout task) and `ghi789` (5 correction turns on a migration script).

  **Root cause:** The assistant consistently dives into implementation before
  reading enough context. In all three sessions, the first edit happened before
  any Read/Grep calls for the relevant error messages or surrounding code. This
  is the "Premature Implementation" antipattern — and it's systemic, not a one-off.

  **Strength to apply:** In sessions where the developer provided explicit file
  paths upfront (the "Clean Handoff" pattern from the success analysis), zero
  corrections were needed. Transferring this constraint-setting habit to debugging
  tasks — "the error is in X, start by reading Y" — could prevent the correction
  spiral.

  **Severity:** Appeared in 3 sessions, costing approximately 12 turns total.

**What to include in each finding:**
- Session ID(s) and dates — traceable to the session inventory
- Quoted corrections — the user's actual words, showing the correction chain
- Turn count — how many turns were wasted
- Root cause — WHY this happened (from the "Generate Insights" step)
- Strength to apply — which success pattern could address this
- Severity metrics — frequency and total turn cost

**Quantitative summary** (include at the end of the section):
- Total correction turns across all sessions analyzed
- Average corrections per task
- Most common root cause category
- Sessions with the highest friction (by correction count or frustration signals)

## False Positives to Avoid

- Exploratory conversations are not failures — "try this, no try that" during design
  exploration is productive, not wasteful
- A single correction is normal — only flag correction *patterns* (2+ corrections on
  similar tasks across sessions, or notable single-session impact)
- Long sessions aren't automatically bad — some tasks genuinely require extended work
- User interruptions aren't always corrections — they might be adding context or
  changing priorities
