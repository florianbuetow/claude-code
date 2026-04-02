---
name: no-preference-asking
pattern: (?i)(would you prefer|would you like me to|would you rather|do you want me to|want me to\b.*\?|should I\b.*\?|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think)|let me know\b|does (this|that) look (right|good|ok)\??|how does (this|that) look|look good\??|what do you think\??|sound good\??|anything else (you|to)|is there anything else|need anything else|what else would you|your call|up to you|your choice|your decision|whatever you('d| would)|what would you like to\b|or do you (want|need|prefer)|or should (I|we)\b)
message: "Do not ask for preference, seek approval, or defer decisions unless it is genuinely unclear from context what the best choice is. Do not use 'let me know', 'does this look right', 'anything else', 'your call', or 'what would you like' — make the engineering decision yourself. Only ask the user if you cannot determine the best choice after thorough investigation."
---

**Stop - you're asking for preference, seeking approval, or deferring instead of acting.**

You asked the user to choose, sought approval for work, or deferred a decision instead of making it yourself (e.g., "would you prefer", "does this look right", "let me know", "anything else", "your call", "what would you like to work on"). Don't stall by delegating decisions:
1. **Do not ask for preference or approval** unless it is genuinely unclear from the context, specific instructions, or specifications and implementation intentions what the best choice is.
2. **Do not defer with "let me know", "your call", or "up to you".** Pick the best choice from an engineering perspective that will create a high-quality, low-maintenance solution aligned with the specifications, instructions, or intent.
3. **Do not fish with "anything else"** — if there's more work to do, do it. If you're done, say so.
4. **Only ask the user** if you are unable to determine the best choice after a thorough investigation. Highlight exactly why you are seeking clarification and why you could not resolve it yourself.
