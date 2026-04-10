---
name: no-dismissing
pattern: (?i)(not a real (bug|issue|error|problem)|can be ignored|just a warning|(is a |just a |only a )pre-existing|the only (failure|error|issue|problem|warning|bug) (is|was|being|comes from)|safe to ignore|not worth (fixing|investigating|worrying)|doesn'?t matter|not important|harmless|benign|false positive|not a concern|don'?t worry about|nothing to worry about|expected (error|warning|failure)|that'?s fine|this is fine|a non-issue|just (cosmetic|informational|noise)|shouldn'?t (matter|cause|be a problem))
message: "Do not dismiss issues without investigation. Diagnose the root cause and show evidence for your conclusion — test output, code references, or logs. No evidence means no dismissal."
---

Do not dismiss issues without investigation.

1. Diagnose the root cause of the warning, error, or concern.
2. Show evidence for your conclusion — test output, code references, git blame, or logs.
3. No evidence means no dismissal. If you investigated and it is benign, show your work.
