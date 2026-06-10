---
name: terminator
description: Router for the terminator plugin — Stop hooks that end a Claude Code session (and optionally its terminal) when the agent's final message contains a kill phrase. Routes to install, remove, update, or whendone. Use when the user says "terminator", "install the kill hook", "set up a kill phrase", "single kill", "double kill", "remove the terminator hook", "change the kill phrase", or "terminate when done".
disable-model-invocation: false
---

# Terminator: Router

Auto-detect the right subcommand from the user's request and dispatch to it.

The user's request is:
"""
$ARGUMENTS
"""

## What this plugin does

Terminator installs **Stop hooks**. When the agent's final message **contains** a configured
kill phrase, the hook terminates the session. There are two scripts; you pick by installing one
or both:

- **single-kill.sh** — ends Claude. Terminal stays open.
- **double-kill.sh** — ends Claude, then the terminal shell that launched it.

The kill walks the process tree to the owning `claude` (and, for double-kill, the top-most shell
ancestor), and never signals pid ≤ 2.

## Detection Rules (first match wins)

| Intent in the request | Route to |
|------------------------|----------|
| "install", "set up", "add", "enable", "single kill", "double kill", first-time setup | `terminator:install` |
| "remove", "uninstall", "disable", "delete the hook" | `terminator:remove` |
| "update", "change the phrase", "new phrase", "rename phrase", "toggle case" | `terminator:update` |
| "when done", "whendone", "terminate when finished", "self-terminate when complete" | `terminator:whendone` |
| "info", "show phrase", "what is my kill phrase", "show config", "terminator status" | `terminator:info` |

If ambiguous, ask:

> What would you like to do with terminator?
> - **install** — set up single-kill and/or double-kill hooks (local or global scope)
> - **remove** — uninstall the hooks
> - **update** — change a kill phrase or case sensitivity
> - **whendone** — have me end this session by uttering the kill phrase once work is finished
> - **info** — show configured kill phrases for local and global scope

## Dispatching

1. Announce: `Routing to /terminator:SUBCOMMAND`
2. Invoke that subcommand skill and follow it exactly.
