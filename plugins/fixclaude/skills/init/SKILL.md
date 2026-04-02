---
name: init
description: >
  Create a brand new CLAUDE.md with production-grade agent directives that
  override Claude Code's built-in limitations. Only use when no CLAUDE.md
  exists in the project. Use when the user says "fixclaude init", "create
  claude md", or "initialize claude directives".
---

# Fix Claude -- Init

Create a new CLAUDE.md from the production-grade template that reverses
Claude Code's built-in limitations discovered in the source code leak.

## Workflow

### Step 1: Verify No Existing CLAUDE.md

Check that CLAUDE.md does not already exist:

```bash
if [ -f "CLAUDE.md" ] || [ -L "CLAUDE.md" ]; then
  echo "ERROR: CLAUDE.md already exists. Use fixclaude:update instead."
  exit 1
fi
```

If it exists, tell the user to use `fixclaude:update` instead and stop.

### Step 2: Read the Template

Read the template from the plugin's references directory:

```
${CLAUDE_PLUGIN_ROOT}/references/claude-md-template.md
```

This template contains the full production-grade agent directives.

### Step 3: Write CLAUDE.md

Write the template content to `CLAUDE.md` in the project root.

Add this attribution comment at the very end of the file:

```markdown

<!-- Agent directives based on https://github.com/iamfakeguru/claude-md (MIT, fakeguru) -->
<!-- Installed by fixclaude plugin -->
```

### Step 4: Confirm

Tell the user:
- CLAUDE.md has been created with production-grade agent directives
- Briefly list the 9 sections that were installed
- Mention they can run `fixclaude:analyze` to see how each directive maps to a specific Claude Code limitation
