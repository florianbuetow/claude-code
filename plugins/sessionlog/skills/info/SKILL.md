---
name: sessionlog:info
description: >
  This skill should be used when the user asks to "show session info",
  "find session log", "where are session logs", "current session id",
  "session path", "sessionlog info", or wants to identify the current
  Claude Code session and its log file location on disk.
---

# Session Log Info

Identify the current Claude Code session and report its log file location.

## Steps

1. **Determine the project session directory.** Run:

```bash
project_dir="$HOME/.claude/projects/$(pwd | sed 's|/|-|g')"
echo "Project session directory: $project_dir"
```

2. **Find the current session** (most recently modified JSONL file):

```bash
current_session=$(ls -t "$project_dir"/*.jsonl 2>/dev/null | head -1)
session_id=$(basename "$current_session" .jsonl)
echo "Session ID: $session_id"
echo "Session file: $current_session"
```

3. **Report session metadata.** Read the first user message to get basic info:

```bash
jq -r 'select(.type == "user") | {sessionId, version, entrypoint, cwd, gitBranch, timestamp} | to_entries[] | "\(.key): \(.value)"' "$current_session" | head -6
```

4. **Count messages:**

```bash
echo "Messages: $(jq -c 'select(.type == "user" or .type == "assistant")' "$current_session" | wc -l | tr -d ' ')"
```

5. **List all sessions for this project:**

```bash
echo ""
echo "All sessions in this project:"
ls -lt "$project_dir"/*.jsonl 2>/dev/null | awk '{print $NF}' | while read f; do
  sid=$(basename "$f" .jsonl)
  msgs=$(jq -c 'select(.type == "user" or .type == "assistant")' "$f" | wc -l | tr -d ' ')
  echo "  $sid ($msgs messages)"
done
```

## Output

Present results as a clean summary:

- **Session ID** — the UUID
- **Session file** — full path to the JSONL file
- **Project session directory** — the folder containing all sessions for this project
- **Session count** — how many sessions exist for this project
- **Current session message count**
