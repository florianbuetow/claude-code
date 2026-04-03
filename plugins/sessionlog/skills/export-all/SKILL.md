---
name: sessionlog:export-all
description: >
  This skill should be used when the user asks to "export all sessions",
  "export all session logs", "batch export sessions", "sessionlog export-all",
  "convert all sessions", or wants to export every Claude Code session
  for the current project as standard LLM conversation JSON and TXT files.
---

# Session Log Export All

Export all Claude Code sessions for the current project to standard LLM conversation JSON and human-readable TXT transcripts.

## Steps

### 1. Identify the project session directory

```bash
project_dir="$HOME/.claude/projects/$(pwd | sed 's|/|-|g')"
echo "Project session directory: $project_dir"
session_count=$(ls "$project_dir"/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
echo "Sessions found: $session_count"
```

### 2. Determine output directory

Use the output directory specified in the user's prompt. If none was specified, default to `docs/sessionlogs/` relative to the current working directory.

### 3. Export each session

Iterate over every JSONL file in the project session directory and run the export script for each:

```bash
output_dir="<output-dir>"
for session_file in "$project_dir"/*.jsonl; do
  session_id=$(basename "$session_file" .jsonl)
  "${CLAUDE_PLUGIN_ROOT}/scripts/export-session.sh" "$session_file" "$output_dir" "$session_id"
done
```

Each invocation produces two files per session:
- `<output-dir>/claude-<session-id>.json`
- `<output-dir>/claude-<session-id>.txt`

### 4. Report results

Show the user:
- Total number of sessions exported
- Output directory
- Total file count (2 files per session)
- Combined size of all exported files
