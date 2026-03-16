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

The inventory remains detailed, but in the final retrospective it should live in the
**Evidence Appendix** (after recommendations), not before them.

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

For each session (above the minimum size threshold), provide a detail block with an
evidence ID so recommendations can reference it:

#### Session 1: `a1b2c3d4-5678-90ab-cdef-1234567890ab`
- **Evidence ID:** `E##`
- **Lines:** 619 | **Modified:** 2026-03-08 23:34 | **Turns:** 18
- **Topic:** Rename preprocess script, fix glob patterns for IDs with brackets
- **Status:** Prematurely terminated
- **Evidence:** The very last message is an assistant `TOOL_USE: Bash` call to `ls -la .../data/input/iL3uDrk-i_E/` to "Verify bundle contents". The command was issued but never received a result. The assistant had just said "Bundle created successfully. Let me verify the contents." and the session ended before the verification completed.
- **Notable patterns:** Script ran successfully but verification was cut off. Near-complete session — only the final check was lost.

#### Session 2: `e5f6a7b8-1234-56cd-ef78-abcdef012345`
- **Evidence ID:** `E##`
- **Lines:** 83 | **Modified:** 2026-02-07 15:08 | **Turns:** 4
- **Topic:** Commit all changes as a series of small grouped commits
- **Status:** Completed
- **Evidence:** The assistant's last message is a summary table of 11 commits created, stating "All done." This is a clear completion with no pending work.
- **Notable patterns:** Efficient commit session — 4 turns, zero corrections. Good example of scoped imperative request.

#### Session 3: `c9d0e1f2-3456-78ab-cdef-567890abcdef`
- **Evidence ID:** `E##`
- **Lines:** 110 | **Modified:** 2026-02-07 01:25 | **Turns:** 6
- **Topic:** Check how cleaned transcripts are stored (SRT vs text), plan to add .txt conversion
- **Status:** User-initiated exit
- **Evidence:** The assistant completed a plan and called `ExitPlanMode`, but the user rejected it ("The user doesn't want to proceed with this tool use"). This is a deliberate user choice to not proceed, not a premature termination. The plan was written to a file and the session ended after the rejection.
- **Notable patterns:** Plan completed successfully — user chose to defer execution to a future session.

Each entry must follow this exact format. The Evidence field is a full paragraph
(2-5 sentences) quoting specific messages/tool calls. Keep these details in the
appendix; recommendation sections should reference these entries by `E##`.

### Sessions Requiring Attention

After the per-session details, highlight sessions that need follow-up:

**3 sessions were prematurely terminated:**

1. **`a1b2c3d4`** (2026-03-08) — The assistant was verifying the output of a script it had just fixed and run. The `ls` command to verify bundle contents was issued but the result never came back. The work was nearly done (script ran successfully) but the verification step was cut off.

2. **`f3e4d5c6`** (2026-02-07) — The user explicitly interrupted the assistant mid-edit with `[Request interrupted by user for tool use]`. The assistant was editing `generate-config.py` to fix how `optional_angle` is handled. The edit was rejected and the session ended with this fix unfinished.

**Resume commands:**
```bash
claude --resume a1b2c3d4-5678-90ab-cdef-1234567890ab
claude --resume f3e4d5c6-7890-12ab-cdef-abcdef345678
```

**Note:** 3 sessions ended with the user rejecting `ExitPlanMode`. These are classified as normal terminations (user-initiated exits) since the user made a deliberate choice to stop. The plans remain saved in files for future use.

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
