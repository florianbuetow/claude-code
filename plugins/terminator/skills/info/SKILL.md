---
name: terminator:info
description: Show the configured kill phrases and case sensitivity for both local (project) and global (user) terminator installations. Use when the user asks "what is my kill phrase", "show terminator config", "terminator info", or "what phrase is configured".
disable-model-invocation: false
---

# Terminator: Info

Show the currently configured kill phrases for local and/or global scope.

## Step 1 — Read both scopes

```bash
local_config=".claude/terminator.json"
global_config="$HOME/.claude/terminator.json"

echo "=== LOCAL scope ($local_config) ==="
if [ -f "$local_config" ]; then
  cat "$local_config"
else
  echo "not installed"
fi

echo ""
echo "=== GLOBAL scope ($global_config) ==="
if [ -f "$global_config" ]; then
  cat "$global_config"
else
  echo "not installed"
fi
```

## Step 2 — Report

Present the findings clearly:

```
## Terminator Info

LOCAL scope (.claude/terminator.json):
  single_killphrase : <phrase or "not set">
  double_killphrase : <phrase or "not set">
  case sensitive    : <true|false|"not set">

GLOBAL scope (~/.claude/terminator.json):
  single_killphrase : <phrase or "not set">
  double_killphrase : <phrase or "not set">
  case sensitive    : <true|false|"not set">
```

If a scope is not installed, show `— not installed —` for that block.
If neither scope is installed, offer `/terminator:install`.
