---
name: no-skipping
pattern: (?i)(i('m| am) skipping|skip(ping)? this|let('s| us) skip|we('ll| will) skip|i('ll| will) skip|the rest (looks|seems|is) fine|everything else (seems|looks|is) (correct|fine|ok)|that part should be fine|should be straightforward|without (seeing|running|testing)|I haven'?t tested this|similar changes would be needed|you get the idea|the pattern is the same|and so on|the other files don'?t need|don'?t think we need to change|I won'?t go through every|and similar for the (other|rest)|the same (approach|pattern|logic) (applies|works) for|I'?ll leave (that|the rest|it) (to|for|as)|left as an exercise|beyond the scope|outside the scope|for brevity|I don'?t have access|I can'?t access)
message: "Don't skip or hand-wave. If something shouldn't be done, explain why. If it should be done, do it."
---

**Stop - you're skipping or glossing over work.**

You either announced you're skipping something, or you glossed over details (e.g., "the rest looks fine", "without running it", "similar changes would be needed", "you get the idea", "for brevity", "I don't have access"). Don't skip and don't hand-wave:
1. If something shouldn't be done, **explain why**.
2. If it should be done, **do it**.
3. Never skip without the user's explicit approval.
