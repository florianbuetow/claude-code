# Session Inventory — Cataloging Every Session Analyzed

> "Before you can find patterns, you need a map of the territory."

## Core Idea

The session inventory is the foundation layer of every retrospective. Before analyzing
patterns across sessions, catalog every session individually. This gives the reader a
complete map of the data — which sessions were analyzed, what each one covered, how each
one ended, and which ones need attention.

The inventory is not interpretation — it is structured observation. Each session gets a
factual entry with metadata, topic detection, and completion status classification. The
pattern analysis (5 dimensions) builds on top of this inventory.

## Session Discovery

Session logs are JSONL files stored at:
`~/.claude/projects/<project-path-encoded>/<session-id>.jsonl`

To find logs for the current project:
- Encode the current working directory path (replace `/` with `-`, strip leading `-`)
- Look in `~/.claude/projects/<encoded-path>/`
- Each `.jsonl` file is one session
- Include every file modified within the last 90 days (by file modification timestamp)

**Exclude tiny sessions:** Sessions with fewer than 10 lines of actual conversation
(excluding metadata lines like `file-history-snapshot`) should be noted in the summary
statistics but do not need per-session detail blocks.

## Per-Session Metadata Extraction

For each session, extract:

### Basic Metadata
- **Session ID**: The filename (without `.jsonl` extension)
- **Lines**: Total line count of the JSONL file
- **Modified**: File modification timestamp
- **Date**: Derived from the modification timestamp

### Topic Detection
Determine the session's topic from the first substantive user message:
- Read the first `"type": "user"` message with meaningful content
- Summarize the topic in one phrase (e.g., "Refactored auth middleware",
  "Debug pipeline failures", "Plan for new feature")
- If the session covered multiple topics, list the primary one and note
  "multi-topic session" in the detail block

### Turn Count
Count the number of user ↔ assistant exchanges:
- Each `"type": "user"` message followed by a `"type": "assistant"` response
  counts as one turn
- Exclude system messages, progress events, and metadata

## Completion Status Classification

Every session must be classified into exactly one of three categories.
**Do not guess — base classification on specific evidence from the session's
final messages.**

### Completed
The session ended with clear completion markers:
- Explicit completion statements: "All done", "That's everything", summary of work
- Task-completing actions: git commit created, file written, test passing
- User satisfaction signals: "thanks", "perfect", "looks good", "exactly"
- Natural Q&A conclusion: user asked a question, got an answer, no follow-up

**Evidence pattern:** The last 3-5 messages show a completed task or natural
conversation ending. No pending tool calls, no stated intent to continue.

### Prematurely Terminated
The session was cut short with work remaining:
- **Unanswered tool call**: The assistant's last message is a tool call that never
  received a result (the session ended mid-execution)
- **Stated intent to continue**: The assistant said "Now let's..." or "Next, I'll..."
  but the session ended before that work began
- **User interruption markers**: `[Request interrupted by user for tool use]` with
  the interrupted work never completed
- **In-progress work**: The assistant was mid-edit or mid-implementation when the
  session ended

**Evidence pattern:** The last messages show incomplete work — a tool call without
a response, or stated next steps that never happened.

### User-Initiated Exit
The user deliberately chose to stop:
- **Rejected ExitPlanMode**: User declined to execute a completed plan — the plan
  was done, the user just chose not to proceed in this session
- **Explicit stop**: "never mind", "forget it", "let's stop here"
- **Deliberate topic change**: User consciously moved on, not from frustration
  but from a decision to defer

**Evidence pattern:** The session shows a conscious user decision to end, not an
unexpected cutoff. The key distinction from premature termination: the user was
in control of the ending.

**Critical distinction:** A user rejecting ExitPlanMode after a plan was
successfully written is NOT premature termination. The plan was completed;
the user chose not to execute it in that session. This is a deliberate choice,
not an interruption.

## Scaling Heuristics

For projects with many sessions, scale the detail level:

| Session Size | Summary Table | Detail Block |
|-------------|--------------|-------------|
| < 20 lines (metadata-only, no real conversation) | One row, marked as "minimal" | None — note in summary statistics only |
| 20-100 lines | Full row | 2-3 sentence summary with status and evidence |
| 100+ lines | Full row | Full detail block with evidence paragraph, notable patterns, and quoted messages |

## Output Format

### Summary Table

Present all sessions in a summary table, sorted by date (most recent first):

```
| # | Session ID | Date | Lines | Topic | Status |
|---|-----------|------|-------|-------|--------|
| 1 | `abc12345` | 2026-03-10 | 890 | Debug pipeline failures | Prematurely terminated |
| 2 | `def67890` | 2026-03-09 | 450 | Refactored auth middleware | Completed |
| 3 | `ghi11111` | 2026-03-08 | 110 | Plan for caching layer | User-initiated exit |
| ... | | | | | |
```

Follow the table with summary statistics:

```
**Sessions analyzed:** [N] sessions from [earliest date] to [latest date]
**Completed normally:** [N]
**Prematurely terminated:** [N]
**User-initiated exits:** [N]
**Minimal sessions excluded from detail:** [N]
```

### Per-Session Detail Blocks

For each session (above the minimum size threshold), provide a detail block:

```
#### Session [N]: `[session-id]`
- **Lines:** [N] | **Modified:** [date time] | **Turns:** [N]
- **Topic:** [one-phrase topic summary]
- **Status:** [Completed / Prematurely terminated / User-initiated exit]
- **Evidence:** [Paragraph explaining HOW the status was determined. Quote specific
  messages, tool calls, or user actions. For completed sessions, quote the completion
  marker. For premature terminations, describe what was in progress when the session
  ended. For user-initiated exits, describe the user's decision.]
- **Notable patterns:** [Any patterns relevant to the 5 dimension analysis — efficient
  completion, correction spirals, frustration signals, skill usage, etc. This field
  connects the inventory to the pattern analysis that follows.]
```

**Evidence depth:** The Evidence field must be a full paragraph, not a phrase.
It should quote actual messages from the session and explain the reasoning behind
the classification. See ANALYSIS.md for the expected level of detail — each session
entry has 2-5 sentences of specific evidence.

### Sessions Requiring Attention

After the per-session details, highlight sessions that need follow-up:

```
### Prematurely Terminated Sessions

[For each prematurely terminated session, provide:]
- A 1-2 paragraph summary of what was happening when the session ended
- What work remains unfinished
- Resume command: `claude --resume [session-id]`

### Sessions with Unresolved Work

[Sessions that completed but mentioned TODOs, follow-up items, or deferred work.
These are not failures — they're context for the next session.]
```

## How This Connects to Pattern Analysis

The session inventory feeds into the 5 dimension subagents. Each dimension subagent
receives the inventory and uses it to:
- Reference specific sessions by ID when presenting findings
- Verify that pattern claims are supported by the session data
- Identify which sessions contribute to each pattern

When a dimension subagent reports a finding, it should reference the inventory:
"This pattern appeared in sessions `abc123`, `def456`, and `ghi789` (see inventory
entries 3, 7, and 12)."

## False Positives to Avoid

- Sessions with no user messages (only system/metadata) are not "prematurely terminated"
  — they never started
- A short session is not automatically problematic — some tasks are genuinely quick
- User-initiated exits are not failures unless preceded by frustration signals
- Multi-topic sessions are not "unfocused" by default — sometimes the developer
  intentionally chains related tasks
