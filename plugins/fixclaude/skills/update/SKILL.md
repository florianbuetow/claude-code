---
name: update
description: >
  Update an existing CLAUDE.md (or the file it symlinks to) with production-grade
  agent directives that override Claude Code's built-in limitations. Merges new
  directives without destroying existing project-specific instructions. Use when
  the user says "fixclaude update", "update claude md", "add claude fixes", or
  "augment claude md".
---

# Fix Claude -- Update

Augment an existing CLAUDE.md with production-grade agent directives. Preserves
existing project-specific instructions while adding overrides for Claude Code's
built-in limitations.

## Workflow

### Step 1: Resolve the Target File

If a specific path was passed (from the install router handling a symlink),
use that path. Otherwise:

```bash
TARGET="CLAUDE.md"
if [ -L "$TARGET" ]; then
  TARGET=$(readlink -f "$TARGET")
  echo "Resolved symlink to: $TARGET"
fi
```

### Step 2: Read the Existing File

Read the target file completely. Understand its structure:
- What sections does it have?
- What conventions does it follow?
- Is there a table of contents or numbered sections?

### Step 3: Read the Template

Read the full template from:

```
${CLAUDE_PLUGIN_ROOT}/references/claude-md-template.md
```

### Step 4: Analyze the Gap

Read the source leak findings reference for full context on what each
directive fixes:

```
${CLAUDE_PLUGIN_ROOT}/skills/analyze/references/source-leak-findings.md
```

Compare the existing CLAUDE.md against all 7 findings. For each finding,
determine whether the existing file already addresses it:

| Finding | Check |
|---------|-------|
| 1. Verification gate | Has forced verification / compile-check mandate? |
| 2. Context death spiral | Has Step 0 cleanup / phased execution rules? |
| 3. Brevity mandate | Has senior dev override / quality reframing? |
| 4. Agent swarm | Has sub-agent swarming rules? |
| 5. 2,000-line blind spot | Has file read budget / chunked read rules? |
| 6. Tool result blindness | Has truncation awareness / narrow scoping rules? |
| 7. grep not AST | Has multi-search mandate for renames? |

### Step 5: Merge Directives

For each missing or incomplete directive:

1. **Extract the relevant sections** from the template
2. **Adapt the style** to match the existing file's conventions (heading levels, formatting, tone)
3. **Append new sections** at the end of the file, under a clear heading:

```markdown
---

## Agent Override Directives

> Production-grade overrides for Claude Code limitations.
> Based on https://github.com/iamfakeguru/claude-md (MIT, fakeguru)
> Installed by fixclaude plugin
```

4. Only add directives that are **missing or significantly weaker** than the template version
5. Do NOT duplicate directives that already exist in equivalent form
6. Do NOT rearrange or reformat existing content

### Step 6: Write and Confirm

Write the updated file. Then tell the user:
- Which directives were added (list them)
- Which were already present and skipped
- The total number of overrides now in place
- Mention they can run `fixclaude:analyze` for a detailed gap analysis
