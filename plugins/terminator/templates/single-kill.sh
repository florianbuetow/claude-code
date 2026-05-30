#!/usr/bin/env bash
# SINGLE-KILL Stop hook.
# If the agent's final message CONTAINS the single-kill phrase, terminate THIS
# Claude session. The terminal is left open.
set -uo pipefail

emit_noop() { echo '{}'; exit 0; }

input="$(cat)"
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" = "true" ] && emit_noop

script_dir="$(cd "$(dirname "$0")" 2>/dev/null && pwd || true)"
config="${script_dir}/../terminator.json"
[ -f "$config" ] || emit_noop

phrase="$(jq -r '.single_killphrase // ""' "$config" 2>/dev/null || true)"
case_sensitive="$(jq -r 'if .case_sensitive == false then "false" else "true" end' "$config" 2>/dev/null || true)"
[ -n "$phrase" ] || emit_noop

message="$(printf '%s' "$input" | jq -r '.last_assistant_message // ""' 2>/dev/null || true)"
[ -n "$message" ] || emit_noop

hay="$message"; needle="$phrase"
if [ "$case_sensitive" = "false" ]; then
  hay="$(printf '%s' "$hay" | tr '[:upper:]' '[:lower:]')"
  needle="$(printf '%s' "$needle" | tr '[:upper:]' '[:lower:]')"
fi
case "$hay" in *"$needle"*) ;; *) emit_noop ;; esac

# Find the claude process that owns this hook.
cpid=""; pid="$$"
for _ in $(seq 1 40); do
  ppid="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')"
  comm="$(ps -o comm= -p "$pid" 2>/dev/null)"; comm="${comm##*/}"; comm="${comm#-}"
  [ -z "$ppid" ] && break
  [ "$comm" = "claude" ] && { cpid="$pid"; break; }
  [ "$ppid" -le 1 ] && break
  pid="$ppid"
done
[ -n "$cpid" ] && [ "$cpid" -gt 2 ] || emit_noop

# Detached: SIGTERM then SIGKILL. NEVER pid <= 2.
nohup bash -c '
  p="'"$cpid"'"
  [ "$p" -gt 2 ] 2>/dev/null || exit 0
  kill -TERM "$p" 2>/dev/null
  for n in $(seq 1 12); do kill -0 "$p" 2>/dev/null || exit 0; sleep 0.5; done
  kill -KILL "$p" 2>/dev/null
' </dev/null >/dev/null 2>&1 &
disown 2>/dev/null || true

emit_noop
