---
name: install
description: >
  Default entry point for fixclaude. Detects whether CLAUDE.md exists in the
  current project and routes to the appropriate subcommand: init (create new)
  or update (augment existing). Handles symlinks transparently. Use when the
  user says "fixclaude", "fix claude", "install fixclaude", or "install claude
  fixes".
---

# Fix Claude -- Install

Detect the current project state and install production-grade agent directives
that override Claude Code's built-in limitations.

## Workflow

### Step 1: Detect CLAUDE.md

Run this bash command to check for CLAUDE.md and resolve symlinks:

```bash
TARGET="CLAUDE.md"
if [ -L "$TARGET" ]; then
  REAL_PATH=$(readlink -f "$TARGET")
  echo "SYMLINK: $TARGET -> $REAL_PATH"
elif [ -f "$TARGET" ]; then
  echo "EXISTS: $TARGET"
else
  echo "MISSING: $TARGET"
fi
```

### Step 2: Route

Based on the detection result:

- **MISSING** -- Invoke the `fixclaude:init` skill to create a new CLAUDE.md
- **EXISTS** -- Invoke the `fixclaude:update` skill to augment the existing file
- **SYMLINK** -- Invoke the `fixclaude:update` skill, passing the resolved real path as the target file. The update skill will modify the file that CLAUDE.md points to, not the symlink itself.

### Important

- Do NOT duplicate the logic from init or update here. Detect and delegate.
- Always resolve symlinks before passing to update.
- Tell the user which path was taken and why.
