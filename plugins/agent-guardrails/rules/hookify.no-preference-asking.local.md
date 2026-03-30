---
name: no-preference-asking
enabled: true
event: stop
pattern: (?i)(would you prefer|would you like me to|would you rather|do you want me to|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think))
action: block
---

**Stop - you're asking for preference instead of acting.**

You asked the user to choose instead of making a decision yourself (e.g., "would you prefer", "would you like me to", "which option", "shall I"). Don't stall by delegating decisions:
1. **Pick the best option** and do it.
2. If genuinely ambiguous with significant trade-offs, **state your recommendation and why**, then act on it.
3. The user can redirect you if they disagree.
