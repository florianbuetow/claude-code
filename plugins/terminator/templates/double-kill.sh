#!/usr/bin/env bash
# DOUBLE-KILL Stop hook.
# If the agent's final message CONTAINS the double-kill phrase, terminate THIS
# Claude session AND the terminal shell that launched it. NEVER signals pid <= 2.
set -uo pipefail

scope="${1:-}"
case "$scope" in LOCAL|GLOBAL) ;; *) echo "Usage: $(basename "$0") LOCAL|GLOBAL" >&2; exit 1 ;; esac

emit_noop() { echo '{}'; exit 0; }

input="$(cat)"
[ "$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)" = "true" ] && emit_noop

script_dir="$(cd "$(dirname "$0")" 2>/dev/null && pwd || true)"
config="${script_dir}/../terminator.json"
[ -f "$config" ] || emit_noop

phrase="$(jq -r '.double_killphrase // ""' "$config" 2>/dev/null || true)"
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

# Walk up: cpid = claude; tshell = TOP-MOST shell ancestor (the terminal's
# controlling shell — robust to any launcher/wrapper between it and claude).
cpid=""; tshell=""; pid="$$"
for _ in $(seq 1 40); do
  ppid="$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')"
  comm="$(ps -o comm= -p "$pid" 2>/dev/null)"; comm="${comm##*/}"; comm="${comm#-}"
  [ -z "$ppid" ] && break
  [ -z "$cpid" ] && [ "$comm" = "claude" ] && cpid="$pid"
  if [ -n "$cpid" ] && [ "$pid" != "$cpid" ]; then
    case "$comm" in sh|bash|zsh|fish|ksh|tcsh|csh|dash|ash) tshell="$pid" ;; esac
  fi
  [ "$ppid" -le 1 ] && break
  pid="$ppid"
done
[ -n "$cpid" ] && [ "$cpid" -gt 2 ] || emit_noop

# Detached: claude first (SIGTERM->SIGKILL), then the terminal shell. NEVER pid<=2.
nohup bash -c '
  c="'"$cpid"'"; t="'"$tshell"'"
  kill_one() {
    local p="${1:-}" n
    case "$p" in (""|*[!0-9]*) return 0 ;; esac
    [ "$p" -gt 2 ] || return 0
    kill -TERM "$p" 2>/dev/null
    for n in $(seq 1 6); do kill -0 "$p" 2>/dev/null || return 0; sleep 0.5; done
    kill -KILL "$p" 2>/dev/null
  }
  kill_one "$c"
  sleep 1
  kill_one "$t"
' </dev/null >/dev/null 2>&1 &
disown 2>/dev/null || true

emit_noop
