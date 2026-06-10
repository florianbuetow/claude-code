---
name: terminator:remove
description: Remove the terminator kill hooks from local or global scope. Strips single-kill.sh and double-kill.sh Stop hook entries from the appropriate settings file (preserving other hooks), and deletes the hook scripts and config. Use when the user asks to "remove terminator", "uninstall the kill hooks", or "disable session termination".
disable-model-invocation: false
---

# Terminator: Remove

Uninstall the terminator hooks, leaving any other Stop hooks intact.

## Step 1 — Detect installed scope(s) and ask

```bash
local_config=".claude/terminator.json"
global_config="$HOME/.claude/terminator.json"
[ -f "$local_config"  ] && echo "LOCAL:  $local_config"  || echo "LOCAL:  not installed"
[ -f "$global_config" ] && echo "GLOBAL: $global_config" || echo "GLOBAL: not installed"
```

- If **neither** is installed: report "not installed" and stop.
- Otherwise: **always ask** the user which scope to remove — even if only one is installed.
  Show what is and isn't installed so the user can make an informed choice.
  Offer: **local**, **global**, or **both** (only show options that are actually installed).

## Step 2 — Strip terminator entries from settings file

For each scope being removed:

**LOCAL** (`SETTINGS_FILE=.claude/settings.local.json`):
```bash
if [ -f .claude/settings.local.json ]; then
  tmp="$(mktemp)"
  jq '
    if .hooks.Stop then
      .hooks.Stop |= (
        map(.hooks = ((.hooks // []) | map(select((.command? // "")
              | (contains("single-kill.sh") or contains("double-kill.sh")) | not))))
        | map(select((.hooks | length) > 0))
      )
      | if (.hooks.Stop | length) == 0 then del(.hooks.Stop) else . end
    else . end
  ' .claude/settings.local.json > "$tmp" && mv "$tmp" .claude/settings.local.json
fi
```

**GLOBAL** (`SETTINGS_FILE=~/.claude/settings.json`):
```bash
if [ -f ~/.claude/settings.json ]; then
  tmp="$(mktemp)"
  jq '
    if .hooks.Stop then
      .hooks.Stop |= (
        map(.hooks = ((.hooks // []) | map(select((.command? // "")
              | (contains("single-kill.sh") or contains("double-kill.sh")) | not))))
        | map(select((.hooks | length) > 0))
      )
      | if (.hooks.Stop | length) == 0 then del(.hooks.Stop) else . end
    else . end
  ' ~/.claude/settings.json > "$tmp" && mv "$tmp" ~/.claude/settings.json
fi
```

## Step 3 — Delete scripts and config

**LOCAL:**
```bash
rm -f .claude/hooks/single-kill.sh .claude/hooks/double-kill.sh .claude/terminator.json
```

**GLOBAL:**
```bash
rm -f ~/.claude/hooks/single-kill.sh ~/.claude/hooks/double-kill.sh ~/.claude/terminator.json
```

Leave the hooks directory in place (it may hold other hooks).

## Step 4 — Verify & report

```bash
# For each removed scope:
ls <HOOKS_DIR>/ 2>/dev/null
jq '.hooks.Stop // "no Stop hooks"' <SETTINGS_FILE> 2>/dev/null
```

```
## Terminator removed (<LOCAL|GLOBAL> scope)
  single-kill.sh / double-kill.sh : deleted
  config: deleted
  settings: terminator entries stripped; other hooks preserved

Takes effect after a session restart.
```
