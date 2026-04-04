---
name: sessionlog:continue
description: >
  This skill should be used when the user asks to "continue session",
  "resume session", "pick up where I left off", "sessionlog continue",
  "continue from compact", "load session context", or wants to restore
  context from a previously compacted session file.
---

# Session Continue

Find and load a compacted session file to resume work from a previous session.

## Steps

### 1. Find compact files

```bash
ls -t docs/sessionlogs/*-compact.md 2>/dev/null
```

### 2. Select the compact file

- **If no files found:** Tell the user no compact files exist. Suggest running `/sessionlog:compact` first.
- **If exactly one file found:** Use it automatically.
- **If multiple files found:** Show the user a numbered list with the session ID and file modification date for each. Ask which one to continue from. Format:

```
Found multiple compact files:
  1. claude-<id1>-compact.md (2025-01-15)
  2. claude-<id2>-compact.md (2025-01-14)
  3. claude-<id3>-compact.md (2025-01-13)

Which session do you want to continue? (number)
```

### 3. Load and present the compact file

Read the selected `-compact.md` file in full.

Print the content to the user so they can see the restored context.

### 4. Follow the instructions

After presenting the context, follow the "Instructions for Continuation" section from the compact file:

1. Run `git status` and `git log --oneline -5` to verify current state
2. Check for any drift between the compact file's description and actual repo state
3. Report what matches and what has changed since compaction

Then ask the user what they'd like to work on — suggest the first item from "Work In Progress" or "Open Issues / Next Steps" as a starting point.
