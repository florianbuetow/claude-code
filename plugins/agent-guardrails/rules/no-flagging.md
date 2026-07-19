---
name: no-flagging
pattern: (?i)(\bto flag\b|\bflagging\b|\bflag(ged)? (this|that|it|these|those)\b|\b(I|we)('?ve| have| had)? flagged\b|\bas flagged\b|\bflagged (above|earlier|previously)\b|\b(should|shall|can|could|would|must|will|'?ll|let me|let'?s) flag\b|\bflag (a|an|one) (issue|concern|problem|risk|thing)\b)
message: "You flagged something, does that mean you saw an issue that stands in the way of completing our goal and producing results that align with the intent of what we are doing? If so I expect you to dive into it, find evidence that this is an issue, and then address it in alignment with our goal and intent. I am not interested in knowing about issues if there is nothing you can do about them. Only flag things to me when you are unable to resolve the flagged issues. Giving me more information than necessary to complete or judge the outcome of our task is counterproductive."
---

Do not flag issues you are able to resolve yourself.

1. Decide whether what you flagged actually stands in the way of the goal and the intent behind it.
2. If it does, dive in, find evidence that it is real, and fix it in alignment with that goal.
3. If you cannot resolve it, then flag it — that is the only case worth reporting.
4. Information beyond what is needed to complete or judge the task is counterproductive.

The pattern matches `flag` used as a verb (`to flag`, `flagging this`, `I have flagged`), not as a noun. Command-line flags, feature flags, and boolean flags do not trigger it.
