# terminator

Claude Code Stop hooks that **terminate a session** — and optionally its terminal — when the
agent's final message contains a kill phrase.

## Two scripts, you choose by installing

| Script | On phrase match |
|--------|-----------------|
| `single-kill.sh` | Terminates Claude. Terminal stays open. |
| `double-kill.sh` | Terminates Claude, then the terminal shell that launched it. |

Behaviour is chosen by **which script you install**, each bound to its **own phrase** — not by a
runtime flag. Install one or both.

## Matching

The hook fires when the agent's final message **contains** the configured phrase (case-sensitivity
configurable). Contains-match is used deliberately: models often prepend text like "I'll provide
the requested output," which would defeat a whole-message exact match.

Install and update skills reject obvious phrases. Use a phrase with a random component, not normal
completion words like `done`, `finished`, `single kill`, or `double kill`.

## How termination works

- Walks up the process tree to the owning `claude` process and signals it (SIGTERM, then SIGKILL).
- `double-kill.sh` additionally walks to the **top-most shell ancestor** (the terminal's
  controlling shell — robust to any wrapper/launcher between it and Claude) and signals that too,
  ~1s after Claude.
- **Never signals pid ≤ 2** (init/launchd/kernel) — the one hard safety rule.

> macOS note: killing the shell ends the shell *session*. Whether the Terminal *window* then
> closes depends on the terminal app's profile ("When the shell exits" → "Close the window").
> A process cannot close a GUI window with a signal.

## Usage (skills)

| Skill | Purpose |
|-------|---------|
| `/terminator:install` | Install single-kill and/or double-kill, each with its phrase. |
| `/terminator:update`  | Change a phrase or case sensitivity (live, no restart). |
| `/terminator:remove`  | Uninstall, leaving other Stop hooks intact. |
| `/terminator:whendone`| Arm the session to self-terminate once work is finished. |

## Files it writes (project-local)

```
.claude/hooks/single-kill.sh   and/or   .claude/hooks/double-kill.sh
.claude/terminator.json        # { single_killphrase, double_killphrase, case_sensitive }
.claude/settings.local.json    # Stop hook entries (merged in, never clobbering others)
```

## Requirements

`bash`, `jq`, and standard POSIX tools (`ps`, `kill`). macOS and Linux (the macOS path is
covered by tests; the Linux path uses the same POSIX `ps` interface).
