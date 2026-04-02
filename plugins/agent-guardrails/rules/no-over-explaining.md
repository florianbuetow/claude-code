---
name: no-over-explaining
pattern: (?i)(The reason (I|for this|behind this|we)|This change (ensures|makes sure|guarantees|is needed)|I (chose|went with|opted for|decided on|used) this approach because|This is (necessary|needed|required) because|What this does is|The purpose of this (change|update|fix|refactor) is|I made this change (because|to ensure|so that)|This (ensures|guarantees|makes sure) that the)
message: "Don't over-explain obvious changes. The diff speaks for itself."
---

**Stop - you're over-explaining your changes.**

You narrated the reasoning behind changes that are self-evident from the diff (e.g., "The reason I made this change is...", "This ensures that the...", "I chose this approach because..."). The code speaks for itself:
1. **Skip the narration** — if the change is obvious from the diff, don't explain it.
2. **Only explain surprises** — non-obvious decisions, counterintuitive approaches, or tradeoffs deserve explanation.
3. **Be concise** — if you must explain, one sentence beats a paragraph.
