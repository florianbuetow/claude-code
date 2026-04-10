---
name: no-preference-asking
pattern: (?i)(would you prefer|would you like me to|would you rather|do you want me to|want me to\b.*\?|should I\b.*\?|which approach would you|which option would you|what would you prefer|let me know which|let me know how you|there are a few approaches|there are several options|here are some options|which would you like|happy to go either way|shall I|what.*feels right|which level feels right|which.*do you (want|prefer|think)|let me know\b|does (this|that) look (right|good|ok)\??|how does (this|that) look|look good\??|what do you think\??|sound good\??|anything else (you|to)|is there anything else|need anything else|what else would you|your call|up to you|your choice|your decision|whatever you('d| would)|what would you like to\b|or do you (want|need|prefer)|or should (I|we)\b)
message: "Re-read the requirements, specifications, and instructions you have been given. The answer to your question can be derived from the context. Make the best engineering decision based on what you already know. If after thorough review you genuinely cannot determine the answer, write on a single line: ESCALATING QUESTION: I am requiring an answer to the following — [state your question without a question mark]"
---

Re-read the requirements, specifications, and instructions you have been given. The answer to your question can be derived from the context.

1. Make the best engineering decision based on what you already know.
2. Do not defer with "let me know", "your call", or "up to you" — decide and act.
3. If after thorough review you genuinely cannot determine the answer, write on a single line: ESCALATING QUESTION: I am requiring an answer to the following — [state your question without a question mark]
