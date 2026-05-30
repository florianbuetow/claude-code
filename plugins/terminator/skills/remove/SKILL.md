---
name: terminator:remove
description: Remove the terminator kill hooks from the current project. Strips the single-kill.sh and double-kill.sh Stop hook entries from .claude/settings.local.json (preserving other hooks), and deletes the hook scripts and config. Use when the user asks to "remove terminator", "uninstall the kill hooks", or "disable session termination".
disable-model-invocation: false
---

# Terminator: Remove

Uninstall the terminator hooks from the **current project**, leaving any other Stop hooks intact.

## Step 1 — Strip terminator entries from settings.local.json

Remove only the hook objects referencing `single-kill.sh` or `double-kill.sh`; drop a Stop entry
only once its hooks array is empty. Co-located non-terminator hooks are preserved.

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

## Step 2 — Delete scripts and config

```bash
rm -f .claude/hooks/single-kill.sh .claude/hooks/double-kill.sh .claude/terminator.json
```

Leave the `.claude/hooks/` directory in place (it may hold other hooks).

## Step 3 — Verify & report

```bash
ls .claude/hooks/ 2>/dev/null
jq '.hooks.Stop // "no Stop hooks"' .claude/settings.local.json 2>/dev/null
```

```
## Terminator removed
  single-kill.sh / double-kill.sh : deleted
  config: deleted
  settings.local.json: terminator entries stripped; other hooks preserved

Takes effect after a session restart.
```
