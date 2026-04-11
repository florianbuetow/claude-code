#!/bin/bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name')
USED_PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
CTX_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
USED_TOKENS=$((USED_PCT * CTX_SIZE / 100))

BAR_WIDTH=10
FILLED=$((USED_PCT * BAR_WIDTH / 100))
EMPTY=$((BAR_WIDTH - FILLED))

if [ "$USED_PCT" -ge 80 ]; then
  FILL_COLOR="\033[31m"   # red
elif [ "$USED_PCT" -ge 70 ]; then
  FILL_COLOR="\033[33m"   # yellow
else
  FILL_COLOR="\033[32m"   # green
fi
EMPTY_COLOR="\033[90m"    # dim gray
RESET="\033[0m"

FILLED_STR=""
[ "$FILLED" -gt 0 ] && printf -v _f "%${FILLED}s" && FILLED_STR="${_f// /▓}"
EMPTY_STR=""
[ "$EMPTY" -gt 0 ] && printf -v _e "%${EMPTY}s" && EMPTY_STR="${_e// /░}"

BAR="${FILL_COLOR}${FILLED_STR}${EMPTY_COLOR}${EMPTY_STR}${RESET}"
echo -e "[${MODEL}] ${BAR} ${USED_PCT}% (${USED_TOKENS}/${CTX_SIZE})"
