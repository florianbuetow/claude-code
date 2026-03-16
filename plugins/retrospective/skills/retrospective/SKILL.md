---
name: retrospective
version: 1.1.0
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
| **Session Inventory** | What happened in each session? Which sessions need attention? | `references/session-inventory.md` |

## Subcommands

| Command Pattern | Scope | Reference |
|----------------|-------|-----------|
| `retrospective` / `retrospective all` | All five dimensions | All references |
| `retrospective wins` / `retrospective good` | What Went Well | `references/success-patterns.md` |
| `retrospective problems` / `retrospective bad` | What Didn't Go Well | `references/failure-patterns.md` |
| `retrospective skills` | Skill & Slash Command Opportunities | `references/skill-opportunities.md` |
| `retrospective workflow` / `retrospective automation` | Workflow Optimization | `references/workflow-optimization.md` |
| `retrospective antipatterns` | Collaboration Antipatterns | `references/collaboration-antipatterns.md` |

| `retrospective inventory` / `retrospective sessions` | Session catalog only | `references/session-inventory.md` |

When no subcommand is specified, default to all dimensions plus session inventory.
When a dimension is mentioned by name (even without "retrospective"), match it.

## Execution Principle: One Script, One Approval

**Do not make dozens of individual Bash calls to read and process session logs.**

Session log analysis involves reading many JSONL files and running many text-processing
operations. Each individual Bash tool call requires user approval, which creates exactly
the "Approval Fatigue" antipattern this skill is designed to detect.

**The pattern**: Create a single shell script file using the Write tool (no approval
needed). Then execute that script with one Bash call (one approval). When you need
different data, edit the same script file and re-run it (one more approval). This way
each analysis query costs exactly one user approval instead of one per file or grep.

**How it works in practice:**

1. **Write** a shell script to `/tmp/retro-analyze.sh` using the Write tool. This
   script should handle file discovery, reading, grepping, and extraction — outputting
   structured results to stdout.
2. **Execute** it with `bash /tmp/retro-analyze.sh` — one approval from the user.
3. **Analyze** the output. If you need to drill deeper into a specific pattern or
   extract different data, **edit** the same script with the Edit tool to change the
   query, then re-run it — one more approval.

Each step in the workflow that touches session logs should follow this pattern:
- **Step 1** (log analysis): The script finds all JSONL files from the last 90 days
  and extracts user messages, tool calls, errors, corrections, and emotional signals.
  Edit and re-run it to investigate specific patterns found in the first pass.
- **Step 4** (inventory subagent): The subagent writes its own script to catalog all
  sessions, extract metadata, and classify completion status.
- **Step 8** (feedback loop subagent): The subagent writes its own script that checks
  for evidence of previous recommendations being implemented (hook events in logs,
  skill invocations, CLAUDE.md changes).

**Do not** read log files one at a time with individual Read or Bash tool calls.
**Do not** run individual grep commands for each pattern you're looking for.
**Do** put all the work into the script and let it run in one shot.

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

**Use the single-script approach** (see "Execution Principle" above). Write the
analysis script to `/tmp/retro-analyze.sh`, execute it once, then edit and re-run it
as needed to drill into specific patterns. Do not read log files one at a time.

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

- `references/session-inventory.md` — session cataloging methodology and output format
- `references/success-patterns.md` — patterns of effective collaboration
- `references/failure-patterns.md` — patterns of wasted effort and breakdowns
- `references/skill-opportunities.md` — detecting automatable patterns
- `references/workflow-optimization.md` — subagents, hooks, automation
- `references/collaboration-antipatterns.md` — known developer-AI pitfalls

For a full retrospective (`retrospective all`), read all six.

### 3. Load Previous Retrospective Reports

Check for previous retrospective reports in `docs/retrospective/`. Read the most recent
3 reports (or fewer if fewer exist). These are needed for the feedback loop in step 8.

If no previous reports exist, this is the first retrospective — skip step 8 and note
this in the output.

### 4. Build Session Inventory

**Launch a dedicated inventory subagent** before the dimension subagents. This subagent
catalogs every session from the last 3 months, producing the session inventory that
serves as the foundation for the pattern analysis.

Read `references/session-inventory.md` for the complete cataloging methodology,
classification heuristics, and output format.

The inventory subagent must:
1. Read `references/session-inventory.md` for methodology and output format.
2. Write an analysis script to `/tmp/retro-inventory.sh` (single-script approach)
   that discovers all JSONL session files, extracts metadata, detects topics from
   first user messages, and classifies completion status.
3. Execute the script, analyze the output, and edit/re-run as needed.
4. Write the structured inventory output to `/tmp/retro-inventory-output.md`.

**This step must complete before step 5 launches.** The inventory output is passed
to each dimension subagent as input context so they can reference specific sessions
in their findings.

**Output:** The session inventory (summary table + per-session detail blocks +
sessions requiring attention) as specified in `references/session-inventory.md`.

### 5. Analyze Session Patterns — One Subagent Per Dimension

**Launch one subagent per dimension.** Do not split work by time period or session
count — split by dimension. Each subagent analyzes ALL session logs from the last 3
months but focuses exclusively on its assigned dimension.

For a full retrospective, launch 5 subagents in parallel:

| Subagent | Dimension | Reference File | Script Path |
|----------|-----------|----------------|-------------|
| 1 | What Went Well | `references/success-patterns.md` | `/tmp/retro-dim1.sh` |
| 2 | What Didn't Go Well | `references/failure-patterns.md` | `/tmp/retro-dim2.sh` |
| 3 | Skill Opportunities | `references/skill-opportunities.md` | `/tmp/retro-dim3.sh` |
| 4 | Workflow Optimization | `references/workflow-optimization.md` | `/tmp/retro-dim4.sh` |
| 5 | Collaboration Antipatterns | `references/collaboration-antipatterns.md` | `/tmp/retro-dim5.sh` |

**Each subagent must:**
1. Read its assigned reference file for detection heuristics and pattern catalogs.
2. Read the session inventory from `/tmp/retro-inventory-output.md` (produced in step 4)
   to understand the full session landscape and reference specific sessions by ID.
3. Write a shell script (using the single-script approach) that searches ALL session
   logs from the last 3 months for patterns relevant to its dimension.
4. Execute the script, analyze the output, and edit/re-run the script as needed to
   drill into specific patterns.
5. Return all significant findings, each backed by paragraph-level evidence with quoted
   session content. A finding is significant if it appeared in 2+ sessions or had notable
   impact in a single session. Reference specific session IDs from the inventory when
   presenting evidence. Each finding must include session ID(s), quoted messages or tool
   calls, turn counts, and full reasoning — not one-liner summaries.

**What each subagent looks for:**

**Subagent 1 — What Went Well:**
- Tasks completed efficiently (few turns, no corrections)
- Effective tool usage (right tool, right approach)
- Good delegation patterns (subagents used well)
- Successful first attempts (no retries needed)
- Positive emotional signals (user satisfaction, explicit praise)

**Subagent 2 — What Didn't Go Well:**
- Tasks requiring many corrections or restarts
- Misunderstandings that wasted multiple turns
- Tool call failures or rejections
- Abandoned sidechains (user said "no" and redirected)
- Context loss (user had to repeat information)
- Frustration signals (terse corrections, resignation, task abandonment)

**Subagent 3 — Skill Opportunities:**
- Same type of request made multiple times across sessions
- Multi-step manual workflows that follow a predictable pattern
- Complex prompts that could be templated
- Repeated setup or configuration instructions

**Subagent 4 — Workflow Optimization:**
- Tasks done in main context that should be delegated to subagents
- Manual checks that could be hooks
- Sequential work that could be parallelized
- Missing tools or plugins that would help

**Subagent 5 — Collaboration Antipatterns:**
- Under-specification leading to wrong approach
- Over-correction loops (fix → new problem → fix → ...)
- Premature implementation (coding before understanding)
- Context overload (too much in one session)
- Emotional escalation (frustration building across turns)

For a single-dimension retrospective (e.g., `retrospective skills`), launch only the
relevant subagent.

### 6. Generate Insights — Ask "Why"

**This step is critical. Do not skip it.**

For each pattern identified in step 5, go beyond observation and ask **why** the
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

### 7. Score Each Dimension

For each dimension analyzed, assign a score from 1–5:

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Major problems in this area, significant improvement needed. |
| 2 | Fair | Notable issues that regularly cause friction. |
| 3 | Okay | Some issues but generally functional. Room for improvement. |
| 4 | Good | Working well with only minor improvement opportunities. |
| 5 | Excellent | This area is highly effective. Keep doing what you're doing. |

### 8. Feedback Loop — Compare Against Previous Retrospectives

**Launch a subagent** to perform this comparison. The subagent should write its own
analysis script (e.g., `/tmp/retro-feedback.sh`) following the single-script approach
(see "Execution Principle" above). The subagent should:

1. Read the current analysis (from steps 5-7).
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
4. Produce the Action Tracking section (see step 9 output format).

If no previous retrospective reports exist, skip this step.

### 9. Produce Findings

Present findings in this structure. **Every finding must include paragraph-level
evidence with quoted session content. Do not compress findings into one-liner bullets.**

#### Session Inventory

Include the full session inventory from step 4 as the first section of the report.
This is the foundation — the reader's map of all sessions analyzed.

#### What Went Well

Report all significant success patterns with paragraph-level evidence:

- **[Pattern name]**

  [1-2 sentence summary of the pattern.]

  **Evidence:** In session `[session-id]` ([date], [N] lines), the user asked to
  "[quoted request]." The assistant [describe what happened — tools used, approach
  taken, corrections needed or not]. The user responded "[quoted response]."
  Total: [N] turns from request to completion.

  This pattern also appeared in sessions `[id1]` and `[id2]`, where [describe the
  commonality that makes this a pattern, not an anecdote].

  **Why this works:** [Root cause analysis — what about this interaction style
  produces efficiency. Reference the "Generate Insights" analysis from step 6.]

  **Applicable to:** [Which failure patterns this strength could address, with
  specific reference to the "What Didn't Go Well" findings.]

#### What Didn't Go Well

Report all significant failure patterns with paragraph-level evidence and root
cause analysis:

- **[Problem name]**

  [1-2 sentence summary of the problem.]

  **Evidence:** In session `[session-id]` ([date], [N] lines), the user asked to
  "[quoted request]." The assistant [describe what went wrong — wrong approach,
  misunderstanding, tool failures]. The user corrected with "[quoted correction]"
  but the assistant [describe what happened next]. This cost [N] turns before
  [resolution or abandonment].

  This pattern also appeared in sessions `[id1]` and `[id2]`, where [describe
  the commonality].

  **Root cause:** [Why this pattern exists — missing skill, bad habit,
  architectural constraint, tooling gap, communication mismatch. From step 6.]

  **Strength to apply:** [Which success pattern could address this — connecting
  strengths to weaknesses. If no applicable strength, say so.]

  **Severity:** Appeared in [N] sessions, costing approximately [N] turns total.

#### Improvement Suggestions

##### Summary

| # | Type | Suggestion | Effort | Impact |
|---|------|------------|--------|--------|
| 1 | Skill | Create /deploy skill | LOW | HIGH |
| 2 | Hook | Add post-edit type checking | LOW | MEDIUM |
| ... | | | | |

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

##### Details

For each suggestion in the summary table, provide a full evidence block:

**1. [Suggestion name]** ([Type] — [Effort] effort, [Impact] impact)

**Evidence:** [Paragraph-level description of the session patterns that justify this
suggestion. Include session IDs, quoted user messages, turn counts, and the total
cost of not having this automation. Reference the session inventory entries.]

**What it would do:**
[Numbered list of steps the skill/hook/subagent would perform]

**Skeleton:** [For skills: YAML frontmatter. For hooks: JSON config. For CLAUDE.md
changes: the exact text to add.]

**Concerns:** [If any — "Not measurable from logs", "Requires habit change",
"Not controllable". Leave blank if none.]

---

#### Action Tracking

If previous retrospective reports exist, include this section:

**Previous retrospective actions reviewed:** [N] items from [dates of previous reports]

✅ **Resolved (no longer flagged):**
- [Action from previous retro] — Evidence: [how we know it was addressed]

🔄 **Recurring (still appearing):**
- [Action from previous retro] — Still observed: [current evidence]

❓ **Unknown (could not verify):**
- [Action from previous retro] — [why verification was not possible]

**Action completion rate**: [X of Y] previous recommendations addressed ([percentage]%)

*Research on ~2,000 Scrum teams found that tracking whether retrospective actions were
implemented is itself a key predictor of team effectiveness. Recurring items deserve
escalated attention — if an issue survived multiple retrospectives, it either needs a
different approach or needs to be accepted as a known limitation.*

#### Dimension Scorecard

| Dimension                  | Score | Label |
|----------------------------|-------|-------|
| What Went Well             | 4/5   | Good  |
| What Didn't Go Well        | 2/5   | Fair  |
| Skill Opportunities        | 3/5   | Okay  |
| Workflow Optimization       | 2/5   | Fair  |
| Collaboration Antipatterns | 3/5   | Okay  |

#### Top 3 Recommendations

These are the highest-impact, lowest-effort suggestions with the fewest concerns.

**Recommendation 1: [Name]**

**What:** [What to create or change — be specific about the artifact]

**Why:** [Why it matters — reference specific session evidence, with session IDs
and quoted content. This is not a generic justification; it's grounded in the
data from this retrospective.]

**Root cause it addresses:** [Which failure pattern or antipattern from this
retrospective, and the root cause identified in step 6]

**First step:** [Concrete action — not "create a skill" but the actual file
content, hook config JSON, or CLAUDE.md addition. Show enough that the developer
could implement it in under 5 minutes.]

---

**Recommendation 2: [Name]**
[... same structure ...]

---

**Recommendation 3: [Name]**
[... same structure ...]

### 10. Write Report to Persistence Store

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

### 11. Summary

One paragraph on the overall health of the developer-AI collaboration — what's the
biggest theme, what single change would have the most impact, and what should stay the
same.

If the feedback loop found recurring issues from previous retrospectives, call out
the most persistent one and suggest a different approach to addressing it.

## Pragmatism Guidelines

These are guidelines, not laws. Apply judgment:

- **Evidence over theory.** Every finding should reference specific session evidence.
  Don't suggest improvements based on hypothetical problems.
- **Quantity matters.** A pattern seen once is an anecdote. A pattern seen in 2+
  sessions or with notable impact in a single session is a real finding.
- **Context matters.** Some "inefficiencies" are exploratory work that shouldn't be
  optimized away. Learning and experimentation are valuable.
- **User corrections are gold.** Every time the user corrected Claude, there's a
  workflow improvement hiding. These are the highest-signal data points.
- **Emotional signals are platinum.** Frustration, resignation, and silent abandonment
  are even higher-signal than explicit corrections — they indicate problems the user
  stopped trying to fix.
- **Always ask why.** An observation without a root cause is incomplete. The "Generate
  Insights" step (step 6) is what separates useful retrospectives from recycled
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
1. Reads all six reference files (including session-inventory.md) and loads
   previous retrospective reports from docs/retrospective/
2. Launches inventory subagent — catalogs every session from the last 3 months,
   classifies completion status, produces per-session detail blocks. Writes
   inventory to `/tmp/retro-inventory-output.md`.
3. Launches 5 dimension subagents in parallel — each receives the session
   inventory as input context, reads its dimension reference file, writes an
   analysis script, and returns all significant findings with paragraph-level
   evidence and quoted session content.
4. Collects results from all 5 subagents
5. For each pattern, asks "why" — identifies root causes and connects strengths
   to weaknesses
6. Launches a feedback subagent to compare current findings against previous
   retrospective recommendations, verifying which were acted on
7. Produces the full report: session inventory, per-dimension findings (with
   paragraph-level evidence), improvement suggestions (with detailed evidence
   blocks), action tracking, dimension scorecard, and top 3 recommendations
   with concrete first steps
8. Writes the report to docs/retrospective/YYYY-MM-DD-v1.md
