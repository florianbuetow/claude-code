---
name: no-blind-edit
pattern: N/A (enforced via PreToolUse hook on Edit, not regex)
message: "You must Read a file before editing it. Re-read the file first to ensure you have current content."
hook_type: PreToolUse
hook_target: Edit
---

**Stop - you're editing a file you haven't read.**

You attempted to edit a file without reading it first in this session. Editing against stale or assumed content produces broken output:
1. **Read the file first** — use the Read tool to load current contents.
2. **Then edit** — only after confirming the file's actual state.
3. **After editing, verify** — re-read to confirm the change applied correctly.

This rule is enforced by a PreToolUse hook on Edit that checks whether the file was previously Read (tracked by a companion PostToolUse hook on Read).
