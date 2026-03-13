---
name: retrospective
version: 1.0.0
description: >
  This skill should be used when the user asks to "run a retrospective", "review my
  sessions", "what went well", "what didn't go well", "how can I improve my workflow",
  "analyze my Claude usage", "suggest skills I should create", "what should I automate",
  "find workflow improvements", or "review how I work with Claude". Also triggers when
  the user mentions session analysis, workflow optimization, skill opportunities,
  subagent suggestions, slash command ideas, or asks about improving their AI-assisted
  development process. Supports analyzing all dimensions at once or focusing on a single
  dimension.
---

# Retrospective — Developer-AI Workflow Analysis

Analyze Claude Code session logs to understand **how the developer-AI collaboration is
working** — what went well, what didn't, and what can be improved. Produce actionable
suggestions for new skills, subagents, slash commands, hooks, and workflow changes based
on actual usage patterns.

This is a true retrospective in the agile sense: looking back at past sessions to
improve future ones. The analysis examines real session logs, not hypothetical best
practices. Each retrospective builds on previous ones — tracking whether past
recommendations were acted on and whether the collaboration is actually improving.

## Dimensions

Five dimensions, each targeting a different axis of workflow improvement:

| Dimension | Question It Answers | Reference |
|-----------|-------------------|-----------|
| **What Went Well** | Which interactions were efficient, successful, and worth repeating? What strengths can be applied to recurring problems? | `references/success-patterns.md` |
| **What Didn't Go Well** | Where did the collaboration break down, waste time, or produce poor results? What is the root cause? | `references/failure-patterns.md` |
| **Skill Opportunities** | What repeated requests or workflows should become reusable skills or slash commands? | `references/skill-opportunities.md` |
| **Workflow Optimization** | How can subagents, hooks, and automation reduce manual effort? | `references/workflow-optimization.md` |
| **Collaboration Antipatterns** | What common developer-AI pitfalls are showing up in these sessions? | `references/collaboration-antipatterns.md` |

## Subcommands

| Command Pattern | Scope | Reference |
|----------------|-------|-----------|
| `retrospective` / `retrospective all` | All five dimensions | All references |
| `retrospective wins` / `retrospective good` | What Went Well | `references/success-patterns.md` |
| `retrospective problems` / `retrospective bad` | What Didn't Go Well | `references/failure-patterns.md` |
| `retrospective skills` | Skill & Slash Command Opportunities | `references/skill-opportunities.md` |
| `retrospective workflow` / `retrospective automation` | Workflow Optimization | `references/workflow-optimization.md` |
| `retrospective antipatterns` | Collaboration Antipatterns | `references/collaboration-antipatterns.md` |

When no subcommand is specified, default to all five dimensions.
When a dimension is mentioned by name (even without "retrospective"), match it.

## Workflow

### 1. Locate and Read Session Logs

Session logs are JSONL files stored at:
`~/.claude/projects/<project-path-encoded>/<session-id>.jsonl`

To find logs for the current project:
- Encode the current working directory path (replace `/` with `-`, strip leading `-`)
- Look in `~/.claude/projects/<encoded-path>/`
- Each `.jsonl` file is one session

Read all session logs from the last 3 months. Each `.jsonl` file has a modification
timestamp — include every file modified within the last 90 days. Each line in a file
is a JSON object representing one event.

**Key event types to extract:**
- `"type": "user"` — user messages (requests, corrections, interruptions, feedback)
- `"type": "assistant"` — Claude's responses (tool calls, text, thinking)
- `"type": "progress"` — hook events, subagent events
- Tool use results — success/failure of each tool call

**Key fields to examine:**
- `message.content` — what the user asked or what Claude said
- Tool use `name` and `input` — which tools were called and how
- `"is_error": true` — tool calls that were rejected or failed
- User messages containing corrections ("no", "not that", "instead", "wrong")
- Session duration and turn count — session length and density
- `"isSidechain": true` — branched/abandoned conversation paths

**Emotional signal detection:**
Pay attention to user frustration and satisfaction markers in messages:
- ALL CAPS or exclamation-heavy language indicating frustration
- Increasingly terse messages (detailed instructions degrading to one-word corrections)
- Explicit frustration ("this is frustrating", "why can't you", "I give up")
- Resignation signals (user does the task themselves, or says "never mind", "forget it")
- Sarcasm or exasperation ("sure, whatever", "fine")
- Rapid topic switches (user abandons a task without resolution)
- Positive signals: "perfect", "exactly", "nice", "that's great" — mark what worked

A user who silently gives up is a worse outcome than one who corrects Claude five times
and gets the right result. Frustration and resignation are the highest-priority signals
because they represent problems the user stopped trying to fix.

### 2. Load Dimension References

Before analyzing, read the reference file(s) for the requested dimension(s):

- `references/success-patterns.md` — patterns of effective collaboration
- `references/failure-patterns.md` — patterns of wasted effort and breakdowns
- `references/skill-opportunities.md` — detecting automatable patterns
- `references/workflow-optimization.md` — subagents, hooks, automation
- `references/collaboration-antipatterns.md` — known developer-AI pitfalls

For a full retrospective (`retrospective all`), read all five.

### 3. Load Previous Retrospective Reports

Check for previous retrospective reports in `docs/retrospective/`. Read the most recent
3 reports (or fewer if fewer exist). These are needed for the feedback loop in step 7.

If no previous reports exist, this is the first retrospective — skip step 7 and note
this in the output.

### 4. Analyze Session Patterns

For each dimension, extract concrete evidence from the session logs:

**What Went Well:**
- Tasks completed efficiently (few turns, no corrections)
- Effective tool usage (right tool, right approach)
- Good delegation patterns (subagents used well)
- Successful first attempts (no retries needed)
- Positive emotional signals (user satisfaction, explicit praise)

**What Didn't Go Well:**
- Tasks requiring many corrections or restarts
- Misunderstandings that wasted multiple turns
- Tool call failures or rejections
- Abandoned sidechains (user said "no" and redirected)
- Context loss (user had to repeat information)
- Frustration signals (terse corrections, resignation, task abandonment)

**Skill Opportunities:**
- Same type of request made multiple times across sessions
- Multi-step manual workflows that follow a predictable pattern
- Complex prompts that could be templated
- Repeated setup or configuration instructions

**Workflow Optimization:**
- Tasks done in main context that should be delegated to subagents
- Manual checks that could be hooks
- Sequential work that could be parallelized
- Missing tools or plugins that would help

**Collaboration Antipatterns:**
- Under-specification leading to wrong approach
- Over-correction loops (fix → new problem → fix → ...)
- Premature implementation (coding before understanding)
- Context overload (too much in one session)
- Emotional escalation (frustration building across turns)

### 5. Generate Insights — Ask "Why"

**This step is critical. Do not skip it.**

For each pattern identified in step 4, go beyond observation and ask **why** the
pattern exists. The goal is root cause analysis, not symptom listing. Without this
step, the retrospective produces shallow observations that recycle from one
retrospective to the next — the single most common retrospective failure mode.

For each finding, answer:

1. **Why does this pattern recur?** Is it a missing skill, a bad habit, an
   architectural constraint, a tooling gap, or a communication mismatch?
2. **Is this systemic or a one-off?** Systemic issues need structural fixes
   (skills, hooks, CLAUDE.md changes). One-offs need nothing.
3. **What strength can address this weakness?** Connect success patterns to failure
   patterns. If the developer communicates effectively in domain X, can that same
   approach fix recurring miscommunication in domain Y? This solution-focused framing
   deploys existing strengths against current problems rather than inventing entirely
   new behaviors.

### 6. Score Each Dimension

For each dimension analyzed, assign a score from 1–5:

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Major problems in this area, significant improvement needed. |
| 2 | Fair | Notable issues that regularly cause friction. |
| 3 | Okay | Some issues but generally functional. Room for improvement. |
| 4 | Good | Working well with only minor improvement opportunities. |
| 5 | Excellent | This area is highly effective. Keep doing what you're doing. |

### 7. Feedback Loop — Compare Against Previous Retrospectives

**Launch a subagent** to perform this comparison. The subagent should:

1. Read the current analysis (from steps 4-6).
2. Read the previous retrospective reports (loaded in step 3).
3. For each recommendation from previous reports, determine its status:
   - **Resolved**: The issue no longer appears in the current analysis. The subagent
     must verify this by checking session logs for concrete evidence that the fix is
     in place (e.g., if a previous retro recommended creating a hook, check whether
     hook events appear in the session logs from the last 3 months;
     if it recommended a skill, check whether the skill is being invoked;
     if it recommended a CLAUDE.md change, check whether the
     CLAUDE.md contains the recommended addition).
   - **Recurring**: The same or a similar issue appears again in the current analysis.
     This means the recommendation was not acted on, or the action taken was
     insufficient.
   - **Unknown**: Cannot determine from current session data whether the recommendation
     was addressed. Needs manual verification.
4. Produce the Action Tracking section (see step 8 output format).

If no previous retrospective reports exist, skip this step.

### 8. Produce Findings

Present findings in this structure:

#### What Went Well

List 3-5 specific examples from the sessions with evidence:
```
- **[Pattern name]**: [Specific example from the session]. This worked because [reason].
```

#### What Didn't Go Well

List 3-5 specific problems with evidence and root cause analysis:
```
- **[Problem name]**: [Specific example from the session]. This cost [N turns / time].
  Root cause: [why this pattern exists — from the "Generate Insights" step].
  Strength to apply: [which success pattern could address this, if applicable].
```

#### Suggestions Table

For each improvement opportunity:

```
| # | Type | Suggestion | Evidence | Effort | Impact | Concerns |
|---|------|------------|----------|--------|--------|----------|
| 1 | Skill | Create /deploy skill for repeated deploy workflow | Asked 4x across sessions | LOW | HIGH | |
| 2 | Subagent | Create test-writer subagent for test generation | Manual test writing took 12 turns | MEDIUM | HIGH | |
| 3 | Hook | Add pre-commit hook for type checking | Manually ran tsc 6 times | LOW | MEDIUM | |
| 4 | Workflow | Improve prompt specificity for refactoring tasks | 3 correction spirals on refactoring | LOW | MEDIUM | Not measurable from logs |
```

**Type** categories:
- **Skill**: A new slash command / skill to create
- **Subagent**: A custom subagent definition to create
- **Hook**: A Claude Code hook to add
- **Plugin**: An existing plugin to install or configure
- **Workflow**: A process change (not tooling)
- **Config**: A CLAUDE.md / AGENTS.md / settings change

**Effort** ratings:
- **LOW**: < 30 minutes, write a skill file or config change
- **MEDIUM**: 1–4 hours, requires designing and testing
- **HIGH**: Half-day+, requires significant new tooling

**Impact** ratings:
- **LOW**: Minor convenience improvement
- **MEDIUM**: Saves noticeable time on recurring tasks
- **HIGH**: Transforms a painful workflow into an efficient one

**Concerns** column — flag issues with actionability:
- **Not controllable**: Depends on external factors the developer cannot change
- **Not measurable from logs**: No way to verify from session data whether the change worked
- **Requires habit change**: Depends on the developer remembering to do something differently
  (prefer structural fixes over behavioral ones — they have higher follow-through)

Leave the Concerns column empty when there are no issues. Items with concerns are not
automatically excluded — they require acknowledgment that follow-through is harder.

#### Action Tracking

If previous retrospective reports exist, include this section:

```
**Previous retrospective actions reviewed:** [N] items from [dates of previous reports]

✅ **Resolved (no longer flagged):**
- [Action from previous retro] — Evidence: [how we know it was addressed]

🔄 **Recurring (still appearing):**
- [Action from previous retro] — Still observed: [current evidence]

❓ **Unknown (could not verify):**
- [Action from previous retro] — [why verification was not possible]

**Action completion rate**: [X of Y] previous recommendations addressed ([percentage]%)
```

Include a note: *Research on ~2,000 Scrum teams found that tracking whether
retrospective actions were implemented is itself a key predictor of team effectiveness.
Recurring items deserve escalated attention — if an issue survived multiple
retrospectives, it either needs a different approach or needs to be accepted as a
known limitation.*

#### Dimension Scorecard

```
| Dimension                  | Score | Label |
|----------------------------|-------|-------|
| What Went Well             | 4/5   | Good  |
| What Didn't Go Well        | 2/5   | Fair  |
| Skill Opportunities        | 3/5   | Okay  |
| Workflow Optimization       | 2/5   | Fair  |
| Collaboration Antipatterns | 3/5   | Okay  |
```

#### Top 3 Recommendations

Highlight the **top 3 suggestions** — highest impact, lowest effort, fewest concerns.
For each:
- What to create or change
- Why it matters (with evidence from sessions)
- Root cause it addresses (from the "Generate Insights" step)
- Concrete first step (e.g., a skill file skeleton, a hook config, a CLAUDE.md addition)

### 9. Write Report to Persistence Store

Save the full retrospective report to `docs/retrospective/`. The filename format is:

```
docs/retrospective/YYYY-MM-DD-v1.md
```

Where:
- `YYYY-MM-DD` is the current date
- `v1` is the version number, incremented if a retrospective already exists for today
  (v2, v3, etc.)

**Before writing**, check if a file for today's date already exists. If so, increment
the version number.

The saved report is the authoritative record for the feedback loop. Future
retrospectives will read these files to track action completion.

### 10. Summary

One paragraph on the overall health of the developer-AI collaboration — what's the
biggest theme, what single change would have the most impact, and what should stay the
same.

If the feedback loop found recurring issues from previous retrospectives, call out
the most persistent one and suggest a different approach to addressing it.

## Pragmatism Guidelines

These are guidelines, not laws. Apply judgment:

- **Evidence over theory.** Every finding should reference specific session evidence.
  Don't suggest improvements based on hypothetical problems.
- **Quantity matters.** A pattern seen once is an anecdote. A pattern seen 3+ times
  across sessions is a real finding.
- **Context matters.** Some "inefficiencies" are exploratory work that shouldn't be
  optimized away. Learning and experimentation are valuable.
- **User corrections are gold.** Every time the user corrected Claude, there's a
  workflow improvement hiding. These are the highest-signal data points.
- **Emotional signals are platinum.** Frustration, resignation, and silent abandonment
  are even higher-signal than explicit corrections — they indicate problems the user
  stopped trying to fix.
- **Always ask why.** An observation without a root cause is incomplete. The "Generate
  Insights" step (step 5) is what separates useful retrospectives from recycled
  complaint lists.
- **Connect strengths to weaknesses.** The most actionable fix is often applying
  something that already works well to a problem area. This solution-focused approach
  has higher follow-through than inventing new behaviors.
- **Prefer structural fixes over behavioral ones.** "Remember to be more specific"
  fails. A CLAUDE.md rule or a skill that enforces specificity succeeds.
- **Don't over-automate.** Not every repeated task should become a skill. Some tasks
  benefit from human judgment each time.
- **Suggest concrete artifacts.** Don't say "create a skill for X" — sketch the
  skill's YAML frontmatter and purpose. Don't say "add a hook" — show the hook config.

## Example Interaction

**User**: `retrospective`

**Claude**:
1. Finds session log files for the current project
2. Reads all session logs from the last 3 months
3. Reads all five reference files
4. Loads previous retrospective reports from docs/retrospective/
5. Extracts patterns: successful interactions, failures, repeated requests, wasted turns,
   emotional signals (frustration, satisfaction)
6. For each pattern, asks "why" — identifies root causes and connects strengths to
   weaknesses
7. Launches subagent to compare current findings against previous retrospective
   recommendations, verifying which were acted on
8. Produces the findings report with wins, problems (with root causes), suggestions
   table (with concerns column), action tracking, scorecard, and top 3 recommendations
   with concrete next steps
9. Writes the report to docs/retrospective/YYYY-MM-DD-v1.md
