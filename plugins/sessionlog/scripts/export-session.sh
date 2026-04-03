#!/usr/bin/env bash
# export-session.sh — Convert a Claude Code session JSONL file to:
#   1. Standard LLM conversation JSON (array of {role, content} objects)
#   2. Human-readable TXT transcript
#
# Usage: export-session.sh <session.jsonl> <output-dir> [session-id]
#
# Outputs:
#   <output-dir>/claude-<session-id>.json
#   <output-dir>/claude-<session-id>.txt

set -euo pipefail

input_file="$1"
output_dir="$2"
session_id="${3:-$(basename "$input_file" .jsonl)}"

if [ ! -f "$input_file" ]; then
  printf "Error: Session file not found: %s\n" "$input_file" >&2
  exit 1
fi

mkdir -p "$output_dir"

json_output="$output_dir/claude-$session_id.json"
txt_output="$output_dir/claude-$session_id.txt"

# --- JSON export: standard LLM conversation format ---
jq -s '
  [
    .[]
    | select(.type == "user" or .type == "assistant")
    | .message
    | {role, content}
  ]
' "$input_file" > "$json_output"

# --- TXT export: human-readable transcript ---
{
  printf "Session: %s\n\n" "$session_id"
  jq -r '
    select(.type == "user" or .type == "assistant")
    | "[" + .message.role + "] " + (
        if (.message.content | type) == "string" then
          .message.content
        else
          [.message.content[] | select(.type == "text") | .text] | join("\n")
        end
      ) + "\n"
  ' "$input_file"
} > "$txt_output"

printf "%s\n%s\n" "$json_output" "$txt_output"
