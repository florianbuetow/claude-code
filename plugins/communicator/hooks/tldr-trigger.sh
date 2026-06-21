#!/usr/bin/env bash
# communicator:tldr — UserPromptSubmit hook.
# Guarantees the tldr brevity directive fires whenever the user's prompt
# contains a trigger token. Emits the skill body as added context for the reply.
set -euo pipefail

input="$(cat)"

prompt=""
if command -v jq >/dev/null 2>&1; then
  prompt="$(printf '%s' "$input" | jq -r '.prompt // empty' 2>/dev/null || true)"
fi
[ -n "$prompt" ] || prompt="$input"

# Triggers: tldr, /tldr (standalone), "short mode", "be brief", "concise mode".
if printf '%s' "$prompt" | grep -qiE '(^|[^[:alnum:]])/?tldr([^[:alnum:]]|$)|short mode|be brief|concise mode'; then
  skill="${CLAUDE_PLUGIN_ROOT}/skills/tldr/SKILL.md"
  echo "[communicator:tldr] Trigger detected — obey this communication directive for your reply:"
  echo
  if [ -f "$skill" ]; then
    # Print the skill body (everything after the closing YAML frontmatter line).
    awk 'body{print} /^---[[:space:]]*$/{c++; if(c==2){body=1}}' "$skill"
  fi
fi
exit 0
