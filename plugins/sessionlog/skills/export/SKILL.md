---
name: sessionlog:export
description: >
  This skill should be used when the user asks to "export session log",
  "convert session to json", "export conversation", "save session",
  "sessionlog export", "export this session", or wants to export the
  current Claude Code session as a standard LLM conversation JSON file
  and human-readable TXT transcript.
---

# Session Log Export

Export the current Claude Code session to standard LLM conversation JSON and a human-readable TXT transcript.

## Steps

### 1. Identify current session

Run the following to find the session file:

```bash
project_dir="$HOME/.claude/projects/$(pwd | sed 's|/|-|g')"
current_session=$(ls -t "$project_dir"/*.jsonl 2>/dev/null | head -1)
session_id=$(basename "$current_session" .jsonl)
echo "Session: $session_id"
echo "Source: $current_session"
```

### 2. Determine output directory

Use the output directory specified in the user's prompt. If none was specified, default to `docs/sessionlogs/` relative to the current working directory.

### 3. Run the export script

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/export-session.sh" "$current_session" "<output-dir>" "$session_id"
```

The script produces two files:
- `<output-dir>/claude-<session-id>.json` — standard LLM conversation JSON (array of `{role, content}` objects)
- `<output-dir>/claude-<session-id>.txt` — human-readable transcript with `[user]`/`[assistant]` prefixes

### 4. Report results

Show the user:
- The two output file paths
- Number of messages exported
- File sizes

## Output Format

**JSON** — Array of message objects following the standard LLM conversation format:

```json
[
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": [{"type": "text", "text": "Hi there!"}]}
]
```

**TXT** — Human-readable transcript:

```
Session: <session-id>

[user] Hello

[assistant] Hi there!
```
