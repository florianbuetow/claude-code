---
name: no-preference-asking
pattern: (?i)((shall|should|can|could|may) (I|we)\b|(want|like|need|ready for) me to\b|(would|do) you (want|like|prefer|rather|think|need|mind)\b|would you\b.*\bor\b|your (call|choice|decision|preference)|up to you|let me know\b|(does|how does) (this|that|it) look|(sound|look) good|((any|some|no)thing|what) else (you|to|would|I|we|can)|is there anything else|what would you like|which (would|do) you|which (approach|option) would you|(there are|here are) (a few|some|several|multiple) (approaches|options|ways|alternatives|choices)|happy to .*(either|whichever|whatever)|or (should|do|would|can|could) (I|we|you)\b|what.*feels right|which.*feels right|which.*do you (want|prefer|think)|how about (we|I)\b|\b(what|which|who|whom|whose|where|when|why|how)\b[^.!:?]*\?)
message: "Do not ask for preference, seek approval, or defer decisions. The detection uses structural patterns (modal+I/we, want-me-to, do-you-X, your-decision-noun, approval-seeking, option-presenting, question-word+?) not a phrase list. If the grammatical structure of your sentence is asking the user to make a decision you should make yourself, it will be caught. Only ask the user if you genuinely cannot determine the best choice after thorough investigation, and explain exactly why."
---

Stop — you're asking for preference, seeking approval, or deferring instead of acting.

Detection uses three layers, not a phrase list:
1. Structural patterns catch deferral by grammar: modal+I/we (should I, can we), want/like/need-me-to, do/would-you-X, your-decision-noun (your call, your choice), option-presenting (there are a few approaches).
2. Statement-form deferrals catch non-question deferral: let me know, up to you, sound good, look good, anything else.
3. Question-word catch-all catches any novel wh-question ending in ? where no sentence-ending punctuation appears between the question word and the question mark.

Rules:
1. Do not ask for preference or approval unless it is genuinely unclear from context, instructions, or specifications what the best choice is.
2. Do not defer with "let me know", "your call", or "up to you." Pick the best engineering choice aligned with the specifications, instructions, or intent.
3. Do not fish with "anything else" — if there's more work to do, do it. If you're done, say so.
4. Only ask the user if you cannot determine the best choice after thorough investigation. Explain exactly why you need clarification and why you could not resolve it yourself.
