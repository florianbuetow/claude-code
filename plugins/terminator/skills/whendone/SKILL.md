---
name: terminator:whendone
description: Arm the current Claude Code session to self-terminate by uttering a kill phrase once all work is finished and no questions remain. Use when the user says "terminate when done", "whendone", "end the session when finished", or "self-terminate when complete".
disable-model-invocation: false
---

# Terminator: When Done

Arm the **current session** to self-terminate: keep working until everything is finished, then
emit the configured kill phrase so the terminator Stop hook ends the session.

## Step 1 — Read the phrase

```bash
test -f .claude/terminator.json && jq -r '{single_killphrase, double_killphrase}' .claude/terminator.json || echo "NOT INSTALLED"
```

If `NOT INSTALLED`, tell the user to run `/terminator:install` first and stop.

Choose the phrase by intent: the **single_killphrase** ends only Claude; the **double_killphrase**
ends Claude and the terminal. Default to `single_killphrase` unless the user wants the terminal
closed too. Call the chosen phrase `<PHRASE>`.

Also confirm the hook is loaded this session (if installed during this session, it needs a restart).

## Step 2 — Adopt the standing instruction

State to the user that you will now operate under this rule, then follow it:

> **Self-termination armed.** I will keep working until there is genuinely no remaining work and
> no open question. When everything is complete and verified, my message will contain the exact
> phrase `<PHRASE>` — which the Stop hook detects (contains-match) and terminates the session.

## Step 3 — Honor it

- Do all the work. Do not stop early to ask permission to terminate.
- If you still need to report results or ask something, send that message normally **without** the
  phrase — emitting the phrase ends the session.
- Only when nothing remains: send a final message containing `<PHRASE>`.
