---
name: no-dismissing
pattern: (?i)(not a real (bug|issue|error|problem)|can be ignored|just a warning|pre-existing (error|warning|bug|issue)|safe to ignore|not worth (fixing|investigating|worrying)|doesn'?t matter|not important|harmless|benign|false positive|not a concern|don'?t worry about|nothing to worry about|expected (error|warning|failure))
message: "Don't dismiss issues without investigation. Diagnose the cause, then decide if action is needed."
---

**Stop - you're dismissing an issue without investigation.**

You dismissed a warning, error, or bug without verifying the cause (e.g., "not a real bug", "can be ignored", "just a warning", "pre-existing error", "safe to ignore"). Don't hand-wave issues:
1. **Investigate** the root cause of the warning or error.
2. **Show evidence** for why it's safe to ignore, or fix it.
3. Never dismiss without proof.
