---
name: terminator:install
description: Install the terminator kill hooks at project (local) or user (global) scope. Installs single-kill.sh and/or double-kill.sh as Stop hooks, each bound to a phrase, merging into the appropriate settings file without clobbering existing hooks. Use when the user asks to "install terminator", "set up the kill hooks", "add single kill", "add double kill", or "enable session termination".
disable-model-invocation: false
---

# Terminator: Install

Install one or both kill hooks at **local** (this project) or **global** (all projects) scope.
Which behaviour you get is determined by **which script is installed**, not by a flag:

- `single-kill.sh` — phrase fires → terminate Claude. Terminal stays open.
- `double-kill.sh` — phrase fires → terminate Claude **and** the terminal shell that launched it.

Matching is **contains** (the message need only contain the phrase; robust to model preambles),
case-sensitivity configurable. The only hard safety rule in the kill path is: never signal pid ≤ 2.

## Step 1 — Scope

Ask the user (or read from `$ARGUMENTS`): **local** or **global**.

- **local** — installs into this project's `.claude/`. Only fires in this project.
- **global** — installs into `~/.claude/`. Fires in every Claude Code session on this machine.

Set paths accordingly:

| | Local | Global |
|---|---|---|
| Hooks dir | `.claude/hooks/` | `~/.claude/hooks/` |
| Config file | `.claude/terminator.json` | `~/.claude/terminator.json` |
| Settings file | `.claude/settings.local.json` | `~/.claude/settings.json` |
| Script arg | `LOCAL` | `GLOBAL` |

## Step 2 — Which hooks?

Ask the user (or read from `$ARGUMENTS`): **single**, **double**, or **both**.

## Step 3 — Phrases + case sensitivity

- Single-kill phrase (recommend a memorable, rare phrase — a movie quote, a line of poetry, a
  sentence unlikely to appear in normal output, e.g. `I'll be back, but not this session`).
- Double-kill phrase (same recommendation; must differ from single-kill phrase).
- Use distinct phrases; if both hooks are installed, neither phrase may equal or contain the other.
- Case-sensitive (default) or case-insensitive (`AskUserQuestion`).

### Phrase Safety Check

Terminator uses a **contains-match** against the final assistant message. Any phrase that appears
in normal assistant output will cause sessions to terminate **apparently at random**.

Apply this check before writing config:

**⚠️ WARNING — short or common phrase:**
If the phrase is a short clause or sentence that could plausibly appear in a typical assistant
response (e.g. `all done`, `I'm finished`, `goodbye`), warn the user:

> ⚠️ **Warning:** This phrase is short and may appear in ordinary responses, causing your session
> to terminate unexpectedly. A longer, more distinctive phrase is strongly recommended.
> Do you want to use it anyway?

Only proceed if the user confirms.

**🚨 STRONG WARNING — single common English word:**
If the phrase is a single word or a very common short term (e.g. `done`, `stop`, `finish`,
`complete`, `exit`, `quit`, `kill`, `terminate`, `goodbye`), issue a strong warning:

> 🚨 **Strong Warning:** Single common words **will** appear in normal assistant output and **will**
> cause your session to terminate at seemingly random moments. This is almost certainly not what
> you want. Are you absolutely sure you want to use this as your kill phrase?

Only proceed if the user explicitly confirms they are absolutely sure.

If the phrase passes without concern, or after the user confirms, proceed to install.

## Step 4 — Confirm (destructive)

```
About to install at <LOCAL|GLOBAL> scope:
  single-kill.sh  phrase="<single phrase>"   -> ends Claude
  double-kill.sh  phrase="<double phrase>"   -> ends Claude + terminal
  case sensitive  : <true|false>
  hooks dir       : <HOOKS_DIR>
  config          : <CONFIG_FILE>
  settings        : <SETTINGS_FILE>
```

## Step 5 — Copy the chosen script(s)

```bash
mkdir -p <HOOKS_DIR>
# copy ${CLAUDE_PLUGIN_ROOT}/templates/single-kill.sh  -> <HOOKS_DIR>/single-kill.sh   (if single/both)
# copy ${CLAUDE_PLUGIN_ROOT}/templates/double-kill.sh  -> <HOOKS_DIR>/double-kill.sh   (if double/both)
chmod +x <HOOKS_DIR>/*-kill.sh
```

## Step 6 — Write config

```bash
jq -n --arg s "<single phrase>" --arg d "<double phrase>" --argjson cs <true|false> \
  '{single_killphrase:$s, double_killphrase:$d, case_sensitive:$cs}' > <CONFIG_FILE>
```

(Omit the key for a script you are not installing; each script only reads its own key.)

## Step 7 — Merge the Stop hook(s) — never clobber existing hooks

The hook command must pass `LOCAL` or `GLOBAL` as `$1`; the scripts exit 1 if the arg is missing.

For LOCAL scope:
```bash
[ -f .claude/settings.local.json ] || echo '{}' > .claude/settings.local.json
for s in single-kill.sh double-kill.sh; do   # restrict to the ones you installed
  cmd="\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/$s LOCAL"
  tmp="$(mktemp)"
  jq --arg cmd "$cmd" --arg s "$s" '
    .hooks.Stop = ((.hooks.Stop // [])
      | if any(.hooks[]?.command? // "" | contains($s)) then .
        else . + [{matcher:"", hooks:[{type:"command", command:$cmd, timeout:10000}]}]
        end)
  ' .claude/settings.local.json > "$tmp" && mv "$tmp" .claude/settings.local.json
done
```

For GLOBAL scope:
```bash
[ -f ~/.claude/settings.json ] || echo '{}' > ~/.claude/settings.json
for s in single-kill.sh double-kill.sh; do   # restrict to the ones you installed
  cmd="$HOME/.claude/hooks/$s GLOBAL"
  tmp="$(mktemp)"
  jq --arg cmd "$cmd" --arg s "$s" '
    .hooks.Stop = ((.hooks.Stop // [])
      | if any(.hooks[]?.command? // "" | contains($s)) then .
        else . + [{matcher:"", hooks:[{type:"command", command:$cmd, timeout:10000}]}]
        end)
  ' ~/.claude/settings.json > "$tmp" && mv "$tmp" ~/.claude/settings.json
done
```

## Step 8 — Verify & report

```bash
ls -la <HOOKS_DIR>/*-kill.sh
cat <CONFIG_FILE>
jq '.hooks.Stop' <SETTINGS_FILE>
```

```
## Terminator installed (<LOCAL|GLOBAL> scope)
  single-kill.sh : phrase "<s>"   (Claude only)            [if installed]
  double-kill.sh : phrase "<d>"   (Claude + terminal)      [if installed]
  case sensitive : <true|false>
  config         : <CONFIG_FILE>
  Other Stop hooks: preserved

Takes effect after a session restart (/exit and start a new Claude session).
Change phrases: /terminator:update   Uninstall: /terminator:remove
```
