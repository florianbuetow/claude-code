---
name: claudeignore
description: This skill should be used when the user wants to "create a claudeignore", "update claudeignore", "optimize context", "ignore folders", "reduce token usage", "set up .claudeignore", or mentions .claudeignore, context window optimization, or ignoring directories from Claude Code indexing.
disable-model-invocation: false
---

# Claudeignore

Create or update `.claudeignore` files to exclude directories and files that waste context tokens during Claude Code sessions.

## Routing

### Step 1: Determine Intent

From the user's message and the current project state, determine intent:

- **Create** — No `.claudeignore` exists in the project root, or the user explicitly asks to create one from scratch.
- **Update** — A `.claudeignore` already exists and the user wants to add, remove, or revise entries.

If intent is ambiguous, check whether `.claudeignore` exists in the working directory. If it does, default to **Update**. If it doesn't, default to **Create**.

### Step 2: Route

- **Create** — Follow the `claudeignore:create` workflow.
- **Update** — Follow the `claudeignore:update` workflow.

Invoke the appropriate subskill. Do not duplicate their logic here.
