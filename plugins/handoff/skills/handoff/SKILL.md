---
name: handoff
description: This skill should be used when the user wants to "hand off", "create a handoff", "wrap up for the next session", "pass this to another agent", "continue from a handoff", "pick up where I left off", "resume a previous session", "load a handoff", or mentions handoff documents, session continuity, or task continuation.
disable-model-invocation: false
---

# Handoff

Create or continue from structured handoff documents for seamless task continuity across sessions.

## Routing

### Step 1: Determine Intent

From the user's message, determine whether they want to:

- **Create a handoff** — they want to capture the current session's context for a future agent or session.
- **Continue from a handoff** — they want to resume work from an existing handoff document.

### Step 2: Route

- **Create** — Follow the `handoff:create` workflow.
- **Continue** — Follow the `handoff:continue` workflow.

Invoke the appropriate subskill. Do not duplicate their logic here.
