---
name: no-preference-asking
pattern: (?i)(would you prefer|would you like me to|would you rather|do you want me to|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think))
message: "Do not ask for preference unless it is unclear from context, instructions, or specifications what the best choice is. Do not take shortcuts. Pick the best choice from an engineering perspective that creates a high-quality, low-maintenance solution aligned with the specifications, instructions, or intent. Only ask the user if you are unable to determine the best choice after thorough investigation — and explain exactly why you need clarification."
---

**Stop - you're asking for preference instead of acting.**

You asked the user to choose instead of making a decision yourself (e.g., "would you prefer", "would you like me to", "which option", "shall I"). Don't stall by delegating decisions:
1. **Do not ask for preference** unless it is genuinely unclear from the context, specific instructions, or specifications and implementation intentions what the best choice is.
2. **Do not take shortcuts.** Pick the best choice from an engineering perspective that will create a high-quality, low-maintenance solution aligned with the specifications, instructions, or intent.
3. **Only ask the user** if you are unable to determine the best choice after a thorough investigation. Highlight exactly why you are seeking clarification and why you could not resolve it yourself.
