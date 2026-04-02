#!/bin/bash
set -euo pipefail

# PreToolUse hook for Edit — blocks edits to files that haven't been Read first.
# Enforces the no-blind-edit rule (fixclaude §6: Edit Integrity).
# Depends on posttooluse-read-tracker.sh to record Read calls.

TRACK_DIR="/tmp/agent-guardrails-reads-$(echo "${CLAUDE_PROJECT_DIR:-$PWD}" | shasum | cut -c1-8)"

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

if [ -z "$file_path" ]; then
  echo '{}'
  exit 0
fi

if [ ! -f "$TRACK_DIR$file_path" ]; then
  jq -n --arg reason "**no-blind-edit**: You must Read a file before editing it. Re-read \`$file_path\` first to ensure you have current content." '{
    "decision": "block",
    "reason": $reason
  }'
else
  echo '{}'
fi
