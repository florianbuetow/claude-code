---
name: terminator:whendone
description: Arm the current Claude Code session to self-terminate by uttering a kill phrase once all work is finished and no questions remain. Use when the user says "terminate when done", "whendone", "end the session when finished", or "self-terminate when complete".
disable-model-invocation: false
---

# Terminator: When Done

**The user invoking this skill is the instruction to execute it. Execute Steps 1–3 now, in order,
in one uninterrupted turn.** Never ask whether to run the skill, whether to proceed, whether to
terminate, or for confirmation of any kind. Those decisions are already made.

The user's request (the work to finish before terminating; may be empty):
"""
$ARGUMENTS
"""

## Step 1 — Read the phrase

Run this now. It is read-only.

```bash
local_config=".claude/terminator.json"
global_config="$HOME/.claude/terminator.json"
found=""

if [ -f "$local_config" ]; then
  echo "=== LOCAL ($local_config) ==="
  jq -r '{single_killphrase, double_killphrase, case_sensitive}' "$local_config"
  found=1
fi

if [ -f "$global_config" ]; then
  echo "=== GLOBAL ($global_config) ==="
  jq -r '{single_killphrase, double_killphrase, case_sensitive}' "$global_config"
  found=1
fi

[ -n "$found" ] || echo "NOT INSTALLED"
```

- Output is `NOT INSTALLED`: reply `Terminator is not installed. Run /terminator:install.` and stop.
  This is the only case where you end without the phrase.
- Otherwise pick `<PHRASE>` and go straight to Step 2:
  - `single_killphrase` by default; `double_killphrase` only if the user's request asks to close
    the terminal too.
  - If both scopes define it, use the local one.

## Step 2 — Do the work

- Do the task in the user's request above, or in the conversation so far, to completion and verify it.
- If there is no task, the work is already finished: go to Step 3.
- Do not end your turn after Step 1. Do not announce that you are "armed". Start working.
- Do not write `<PHRASE>` in any message except the Step 3 message.
- The only reason to send a message without the phrase is a question about the task itself that
  blocks the work and that you cannot decide yourself. Questions about this skill, the phrase, or
  termination are never allowed.

## Step 3 — Terminate

Send one final message: a short summary of what was done, followed by `<PHRASE>` written verbatim
as plain text. The Stop hook finds the phrase in that message and ends the session.
