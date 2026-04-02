#!/bin/bash
set -euo pipefail

# PostToolUse hook for Read — tracks which files have been read in this session.
# Companion to pretooluse-edit-guardrail.sh (no-blind-edit rule).

TRACK_DIR="/tmp/agent-guardrails-reads-$(echo "${CLAUDE_PROJECT_DIR:-$PWD}" | shasum | cut -c1-8)"

# Clean tracking dir if older than 24 hours
if [ -d "$TRACK_DIR" ]; then
  if find "$TRACK_DIR" -maxdepth 0 -mmin +1440 -print -quit 2>/dev/null | grep -q .; then
    rm -rf "$TRACK_DIR"
  fi
fi

mkdir -p "$TRACK_DIR"

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

if [ -n "$file_path" ]; then
  dir=$(dirname "$file_path")
  mkdir -p "$TRACK_DIR$dir"
  touch "$TRACK_DIR$file_path"
fi

echo '{}'
