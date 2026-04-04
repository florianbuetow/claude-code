---
name: sessionlog:compact
description: >
  This skill should be used when the user asks to "compact session",
  "compress session", "save session context", "sessionlog compact",
  "compact this session", "prepare for clear", or wants to create a
  compressed summary of the current session that can be continued
  after clearing context.
---

# Session Compact

Export the current session and produce a compressed task continuity summary that captures all essential knowledge required to resume the task without re-reading the full session log.

## Steps

### 1. Identify current session

```bash
project_dir="$HOME/.claude/projects/$(pwd | sed 's|/|-|g')"
current_session=$(ls -t "$project_dir"/*.jsonl 2>/dev/null | head -1)
session_id=$(basename "$current_session" .jsonl)
echo "Session: $session_id"
echo "Source: $current_session"
```

### 2. Export the session transcript

Use the export script to produce the human-readable TXT:

```bash
output_dir="docs/sessionlogs"
mkdir -p "$output_dir"
"${CLAUDE_PLUGIN_ROOT}/scripts/export-session.sh" "$current_session" "$output_dir" "$session_id"
```

This produces `docs/sessionlogs/claude-<session-id>.txt`.

### 3. Read the exported TXT file

Read the full content of `docs/sessionlogs/claude-<session-id>.txt`.

### 4. Generate the compact continuation file

You are now acting as a structured reasoning assistant specializing in summarizing and compressing AI agent session logs. Your goal is to transform the full conversation history you just read into a task continuity summary.

**Purpose:** Compact the session log into a structured summary that communicates:
- The problem being solved and its current status.
- What has been done and what progress was made.
- What worked, what failed, and why.
- Lessons learned and constraints to avoid repeating past mistakes.
- The next steps and reasoning context to continue effectively.

Create `docs/sessionlogs/claude-<session-id>-compact.md` with the following structure. Accuracy and clarity are more important than brevity.

```markdown
# Task Continuity Summary

> Compacted from session `<session-id>` on <date>

## 1. Task Overview

Brief summary of the main purpose or goal the session was working on.
Any key constraints, requirements, or parameters identified.

## 2. Current Status

What has been completed or achieved so far.
The current state of the problem or solution.

## 3. Environment and Assets

List the specific file paths, code snippets, library versions, or exact error codes that are currently active.

## 4. Attempts and Learnings

List of major approaches attempted (what was tried).
Why each attempt failed or succeeded (causes, issues, or insights).
Highlight recurring problems or misunderstandings.

## 5. Key Discoveries and Reasoning

Important facts, decisions, or deductions that shape the next steps.
Core assumptions or definitions that should remain stable in future work.

## 6. Pending Questions or Unresolved Issues

Specific open questions, blockers, or design uncertainties that remain.

## 7. Next Steps

Recommended next logical actions to continue progress.
Suggestions on how to avoid repeating previous errors.

## 8. Practical Memory Summary

A concise "mission context recap" of 10-15 lines, phrased as if handing off the project to a new agent instance. This must be self-contained enough that a fresh agent can pick up immediately where the last left off.
```

**Compression Rules:**
- Prioritize actionable context over surface dialogue.
- Remove filler, conversational fluff, and meta-comments.
- Preserve all facts, reasoning, and lessons that affect future outcomes.
- Highlight contradictions or missteps to help future iterations avoid them.
- Focus on knowledge propagation, not chronological fidelity.
- When uncertain, assume the next agent must be able to pick up immediately where the last left off.

### 5. Report to user

Print an abridged version of the compact file — show the section headings and 1-2 key bullets from each section so the user can verify the summary looks right.

Then tell the user:

> Compact file saved to `docs/sessionlogs/claude-<session-id>-compact.md`
>
> To continue in a fresh session:
> 1. Run `/clear` to reset context
> 2. Then run `/sessionlog:continue` to pick up where you left off
