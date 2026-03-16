---
name: retrospective
version: 1.3.1
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

## Execution Principle: One Script Per Agent, Zero Raw Bash Calls

**MANDATORY. Every agent (main context and every subagent) MUST use a dedicated shell
script for ALL Bash operations. No agent may run raw Bash commands like grep, find, jq,
cat, rg, or any data extraction directly. Every command goes into the script.**

Each Bash tool call requires user approval. Running dozens of individual commands causes
confirmation fatigue — the exact antipattern this skill detects. The fix: each agent
creates one script, makes it executable, and only ever runs that script. When the agent
needs different data, it edits the script and re-runs it.

### How every agent must work

1. **Write** a shell script using the Write tool (no approval needed):
   `/tmp/retro-<agent-name>.sh`
2. **Make it executable once:** `chmod +x /tmp/retro-<agent-name>.sh` (one approval)
3. **Run it:** `./tmp/retro-<agent-name>.sh` (one approval)
4. **Need different data?** Edit the script with the Edit tool (no approval), then
   re-run `./tmp/retro-<agent-name>.sh` (one approval). Never create a new Bash call.

### Script assignments (one per agent, no sharing)

| Agent | Script path |
|-------|------------|
| Main context (step 1) | `/tmp/retro-analyze.sh` |
| Inventory subagent (step 4) | `/tmp/retro-inventory.sh` |
| Dimension 1 subagent (step 5) | `/tmp/retro-dim1.sh` |
| Dimension 2 subagent (step 5) | `/tmp/retro-dim2.sh` |
| Dimension 3 subagent (step 5) | `/tmp/retro-dim3.sh` |
| Dimension 4 subagent (step 5) | `/tmp/retro-dim4.sh` |
| Dimension 5 subagent (step 5) | `/tmp/retro-dim5.sh` |
| Feedback loop subagent (step 8) | `/tmp/retro-feedback.sh` |

### What goes in the script

Everything. File discovery, JSONL parsing, grep/rg searches, jq queries, line counting,
pattern extraction — all of it. The script outputs structured results to stdout. The
agent reads the output, thinks about it, edits the script for the next query, re-runs.

### Violations (NEVER do these)

- Running `grep`, `rg`, `find`, `jq`, `cat`, `wc`, `sort`, or `awk` as direct Bash calls
- Reading log files one at a time with individual Read or Bash calls
- Creating multiple different Bash commands instead of editing the script
- Any Bash tool call that is not `chmod +x` or executing the agent's own script

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
2. Write `/tmp/retro-inventory.sh` using the Write tool, then `chmod +x` it (one
   Bash approval). This script handles ALL data extraction: file discovery, JSONL
   parsing, metadata extraction, topic detection, status classification.
3. Run `./tmp/retro-inventory.sh` (one Bash approval). Analyze the output.
4. Need different data? Edit the script with the Edit tool, re-run it. Never run
   raw grep/find/jq/cat as separate Bash calls — everything goes in the script.
5. Write the structured inventory output to `/tmp/retro-inventory-output.md`.

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

**Each subagent must follow the script-only rule:**
1. Read its assigned reference file for detection heuristics and pattern catalogs.
2. Read the session inventory from `/tmp/retro-inventory-output.md` (produced in step 4)
   to understand the full session landscape and reference specific sessions by ID.
3. Write its dedicated script (e.g., `/tmp/retro-dim1.sh`) using the Write tool, then
   run `chmod +x /tmp/retro-dim1.sh` (one Bash approval). The script must contain ALL
   grep, find, jq, cat, rg, awk, wc, and sort operations — no raw Bash calls allowed.
4. Run `./tmp/retro-dim1.sh` (one Bash approval). Analyze the output.
5. Need different data? Edit the script with the Edit tool, re-run it. Repeat as needed.
   The agent may ONLY call Bash to run its own script — never for individual commands.
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

**Launch a subagent** to perform this comparison. The subagent MUST follow the
script-only rule: write `/tmp/retro-feedback.sh` using the Write tool, `chmod +x` it
(one Bash approval), run it (one Bash approval), edit and re-run as needed. No raw
Bash calls — all grep/find/jq/cat operations go in the script. The subagent should:

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

### 9. Merge Results Into Report

**CRITICAL: Keep the analysis methodology unchanged, but change the presentation.
The final report must be recommendation-first, scannable in 30 seconds, and use
fixed fields per block.**

Do not dump raw subagent prose into the main body. Synthesize findings into a fixed
structure, then move detailed evidence into a numbered appendix.

#### Required Output Order (fixed)

1. **Recommendations Table (FIRST section in the report)**
2. **Recommendation Blocks (numbered, fixed fields)**
3. **Concrete Implementation (copy-paste artifacts)**
4. **Action Tracking (resolved/recurring/unknown from step 8)**
5. **Dimension Scorecard (from step 7)**
6. **Summary (short)**
7. **Evidence Appendix (numbered, after recommendations)**

#### Recommendations Table (FIRST)

Start the report with a table:

`| # | Action | Effort | Impact | Status | Evidence Ref(s) |`

Rules:
- `Status` must be `new` or `recurring` for every recommendation.
- Mark `recurring` when step 8 found a materially similar unresolved recommendation.
- Mark `new` when no prior equivalent recommendation exists.
- Sort by highest impact, then lowest effort.

#### Recommendation Blocks (fixed fields)

After the table, include one block per recommendation in strict field order:

`Recommendation #`  
`Action:`  
`Effort:`  
`Impact:`  
`Status:` (`new` or `recurring`)  
`Why now:` (1-2 sentences, no long evidence dump)  
`Expected outcome:`  
`Evidence refs:` (`E01`, `E07`, etc.; no inline quote walls)

#### Concrete Implementation (copy-paste)

Provide an implementation block for every recommendation with exact text/config:

`Recommendation #`  
`Target artifact:` (file path, hook config path, skill file, etc.)  
`Exact content to apply:` (full markdown/json/yaml/code block ready to copy-paste)  
`Verification:` (one concrete check command or acceptance condition)

This section must be immediately usable without interpretation.

#### Action Tracking

Use the feedback-loop output from step 8, but keep it concise and structured:
- Completion rate percentage
- Resolved items
- Recurring items
- Unknown items

#### Dimension Scorecard

Include the 1-5 scores from step 7 as a table. Keep to one compact table.

#### Evidence Appendix (numbered, after recommendations)

All detailed analysis lives here, after the recommendation sections.

Rules:
- Assign evidence IDs `E01`, `E02`, ... and reference these IDs from recommendations.
- Put session inventory details, quotes, long reasoning, and per-dimension findings
  in this appendix only.
- Do not repeat full evidence inline in recommendation blocks.

Each appendix entry must use fixed fields:

`Evidence ID:`  
`Dimension:` (`inventory`, `success`, `failure`, `skill`, `workflow`, `antipattern`, `feedback`)  
`Sessions:`  
`Observation:`  
`Supporting evidence:` (quoted snippets/tool traces)  
`Root cause:`  
`Impact/cost:`  
`Related recommendation(s):` (`#1`, `#3`, etc.)

#### Summary

One short paragraph: biggest theme, highest-leverage change, and what to preserve.

### 10. Write Report to Persistence Store

Save the merged report to `docs/retrospective/YYYY-MM-DD-v1.md`. Increment the
version number if a file for today already exists. This is the authoritative record
for the feedback loop — future retrospectives read these files.

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
1. Reads all six reference files and loads previous retrospective reports
2. Launches inventory subagent — catalogs every session, classifies completion
   status, produces per-session detail blocks with evidence paragraphs
3. Launches 5 dimension subagents in parallel — each produces comprehensive
   findings with paragraph-level evidence and quoted session content
4. For each pattern, asks "why" — root causes, connects strengths to weaknesses
5. Launches feedback subagent to compare against previous retrospective
6. **Builds a recommendation-first report with fixed blocks** — recommendations
   and copy-paste implementation first, numbered evidence appendix last
7. Writes the report to docs/retrospective/YYYY-MM-DD-v1.md
