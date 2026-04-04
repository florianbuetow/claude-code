---
name: sessionlog:recap
description: >
  This skill should be used when the user asks to "recap", "brief me",
  "remind me", "what did we work on", "what happened last time",
  "catch me up on recent sessions", "sessionlog recap", "session recap",
  "recent session summary", "tldr sessions", or wants a quick summary
  of what was worked on in recent sessions for this project.
---

# Session Recap

Read the last 3 session logs for this project and produce a concise TLDR of what was worked on.

## Steps

### 1. Find recent sessions

```bash
project_dir="$HOME/.claude/projects/$(pwd | sed 's|/|-|g')"
sessions=$(ls -t "$project_dir"/*.jsonl 2>/dev/null | head -4)
echo "$sessions"
```

We grab up to 4 because the most recent one is the *current* session. Skip it and use the 3 before it.

### 2. Export each session to readable TXT

For each of the 3 previous sessions (skip the first/current one):

```bash
output_dir=$(mktemp -d)
sessions=$(ls -t "$project_dir"/*.jsonl 2>/dev/null | head -4 | tail -3)
for session_file in $sessions; do
  sid=$(basename "$session_file" .jsonl)
  "${CLAUDE_PLUGIN_ROOT}/scripts/export-session.sh" "$session_file" "$output_dir" "$sid"
done
echo "Exported to: $output_dir"
```

If fewer than 3 previous sessions exist, use however many are available.

### 3. Read each exported TXT

Read the full content of each exported `claude-<session-id>.txt` file from the temp directory. Read them in reverse chronological order (most recent first).

### 4. Generate the recap

You are summarizing recent work sessions for a developer returning to this project. Your goal is a quick, scannable recap — not a full continuity document.

**Output format — print directly to the user (do NOT write to a file):**

```
## Session Recap

Last time we worked on:

1. **<topic>** — <one-sentence summary of what was done and the outcome>
2. **<topic>** — <one-sentence summary>
3. **<topic>** — <one-sentence summary>
...
```

**Rules:**
- Group by topic/theme, not by session. If two sessions touched the same feature, merge them into one bullet.
- Each bullet should answer: *what was done* and *what was the outcome* (shipped, in progress, blocked, etc.)
- Keep it to 3-7 bullets total. Fewer is better.
- Lead with the most important/recent work.
- Skip meta-activity (reading files, exploring code) — focus on actual outcomes.
- If something was left incomplete or blocked, say so explicitly.
- Do NOT create any files. Print the recap directly.

### 5. Clean up

```bash
rm -rf "$output_dir"
```
