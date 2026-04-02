---
name: no-dismissing
pattern: (?i)(not a real (bug|issue|error|problem)|can be ignored|just a warning|pre-existing (error|warning|bug|issue)|safe to ignore|not worth (fixing|investigating|worrying)|doesn'?t matter|not important|harmless|benign|\ba false positive|not a concern|don'?t worry about|nothing to worry about|expected (error|warning|failure)|that'?s fine|this is fine|a non-issue|just (cosmetic|informational|noise)|shouldn'?t (matter|cause|be a problem))
message: "Don't dismiss issues without investigation. Diagnose the cause, then decide if action is needed. If you believe something is fine, show the evidence."
---

**Stop - you're dismissing an issue without investigation.**

You dismissed a warning, error, or potential issue without showing evidence (e.g., "not a real bug", "can be ignored", "just a warning", "pre-existing error", "safe to ignore", "that's fine", "a non-issue", "just cosmetic", "shouldn't matter"). Don't hand-wave issues:
1. **Investigate** the root cause of the warning, error, or concern.
2. **Show irrefutable evidence** for why it's safe to ignore — a test output, a code snippet, a git blame, or a log line that proves your claim.
3. **Never dismiss without proof.** If you investigated and it truly is benign, say so — but show your work. The claim must be verifiable from the evidence you present.
