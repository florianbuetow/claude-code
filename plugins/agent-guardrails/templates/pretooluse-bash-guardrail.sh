#!/bin/bash
set -euo pipefail

# PreToolUse hook for Bash — blocks destructive commands that are hard to reverse.
# Enforces the no-destructive-bash rule (fixclaude §6: Destructive Action Safety).

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')

if [ -z "$command" ]; then
  echo '{}'
  exit 0
fi

blocked=()

# Catch rm -rf targeting root, home, or current directory
if echo "$command" | grep -qE 'rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|--force\s+)*(\/|~|\.)'; then
  blocked+=("**no-destructive-bash**: \`rm -rf\` targeting root, home, or current directory detected.")
fi

# Catch force push
if echo "$command" | grep -qE 'git\s+push\s+(-[a-zA-Z]*f|--force)'; then
  blocked+=("**no-destructive-bash**: \`git push --force\` detected. Use \`--force-with-lease\` or verify this was explicitly requested.")
fi

# Catch hard reset
if echo "$command" | grep -qE 'git\s+reset\s+--hard'; then
  blocked+=("**no-destructive-bash**: \`git reset --hard\` detected. This discards uncommitted work. Verify this was explicitly requested.")
fi

# Catch git checkout that discards all changes
if echo "$command" | grep -qE 'git\s+checkout\s+--\s+\.'; then
  blocked+=("**no-destructive-bash**: \`git checkout -- .\` detected. This discards all unstaged changes.")
fi

# Catch git clean -f (deletes untracked files)
if echo "$command" | grep -qE 'git\s+clean\s+(-[a-zA-Z]*f|--force)'; then
  blocked+=("**no-destructive-bash**: \`git clean -f\` detected. This permanently deletes untracked files.")
fi

# Catch git branch -D (force delete branch)
if echo "$command" | grep -qE 'git\s+branch\s+-D\b'; then
  blocked+=("**no-destructive-bash**: \`git branch -D\` detected. Use \`-d\` (safe delete) unless force-delete is explicitly requested.")
fi

if [ ${#blocked[@]} -eq 0 ]; then
  echo '{}'
  exit 0
fi

reason=$(printf '%s\n' "${blocked[@]}")

jq -n --arg reason "$reason" '{
  "decision": "block",
  "reason": $reason
}'
