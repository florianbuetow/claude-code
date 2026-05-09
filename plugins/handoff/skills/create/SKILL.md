---
name: create
description: Compact the current conversation into a structured handoff document
  so a fresh agent (or human) can continue the work with zero prior context.
argument-hint: What will the next session focus on? (optional)
disable-model-invocation: true
---

# Handoff skill

Write a structured handoff document and save it to `./docs/handoffs/`
(create the directory if it doesn't exist: `mkdir -p ./docs/handoffs/`).
Use a path produced by `mktemp ./docs/handoffs/handoff-XXXXXX.md`.

The goal is task continuity: the next agent should act with the same
intent and respect the same constraints from turn one.

---

## Reference micro-format

All file and URL references in Tier 1 and Tier 2 MUST use this format:

```
`path-or-url` — *what it is.* **When:** <trigger>. **Why:** <what it
constrains>. **Read:** <scope and stance>.
```

Tier 3 references use a one-line description.

If you cannot fill in **When** or **Why** for a Tier 1 or Tier 2
reference, omit the file.

---

## Document template

Sections marked **[infer]** are usually implicit in the conversation.
Infer them from what the user pushed back on, accepted quickly, called
"good enough", or rejected as "missing the point". Verify inferred
sections with the user before saving (see Verification step).

````markdown
# Handoff: <short topic>

## Next agent: start here
1. First concrete action: <the specific move the next agent should make>.
   Valid forms include "make change X to file Y", "draft section Z",
   "present options A/B/C to the user and let them choose". If the
   session ended mid-deliberation, name the deliberation honestly — do
   not fabricate a decisive next action.
2. Read these first (Tier 1 — required before acting):
   - `path` — *what it is.* **Why now:** <reason>. **Read:** <scope>.
3. If this handoff is part of a chain, also read the prior handoff
   (linked in Metadata) as Tier 1.
4. Then summarise your understanding of goal, intent, and next action
   back to the user and wait for confirmation before doing anything else.

## Goal
The deliverable. One or two sentences.

## Intent  [infer]
- **Optimizing for:** 1–2 dominant priorities (speed, correctness,
  learning, defensibility, reversibility, clarity-for-X).
- **Not optimizing for:** what to deprioritize so the next agent doesn't
  gold-plate.
- **Beyond the deliverable:** what success enables.
- **Non-negotiables:** hard constraints.
- **Preferences:** soft constraints.

## Stance & ways of working  [infer]
- **Stance:** the role to take in this task (e.g., "pair-programming
  partner who pushes back on premature optimization", "Socratic teacher",
  "ghostwriter matching the user's voice").
- **Behavioural rules:** task-specific operational rules (e.g., "show
  plan before executing", "scoped edits not rewrites", "ask before
  adding dependencies").
- **Tonal calibration:** stylistic preferences specific to this task and
  this user — tone, formatting, pet peeves, things the user has pushed
  back on.

## Status
- Done: …
- In progress: …
- Next: …
- Blocked: …

Relabel if a different vocabulary fits the task better (e.g., for
writing: "drafted / current section / remaining sections / unresolved
decisions").

## Read when relevant (Tier 2 — conditional)
Files and URLs that matter only under specific conditions.

- `path-or-url` — *what it is.* **When:** <trigger condition>.
  **Why:** <what it constrains>. **Read:** <scope and stance>.

## Reference index (Tier 3 — on-demand)
Files and URLs the next agent probably won't need but should know exist.

- `path-or-url` — <one-sentence description>.

## Decisions & rationale
What was chosen and why. Bullet format, each decision under ~3 lines.
Push detailed rationale into linked ADRs or drafts.

## Tried and rejected
Dead-ends, with the reason they failed. If you cannot remember earlier
dead-ends with confidence, say so — do not fabricate.

## Open questions
Things only the user can answer.

## Suggested resources
Skills, prompts, or tools the next agent should consult first. One line
each on why.

## Metadata
- Timestamp: <ISO 8601>.
- Mode: software / conversational / planning / mixed.
- Branch + last commit: <if applicable, else "(n/a)">.
- Prior handoff: <path or "(none)">.
- Verification: interactive / non-interactive.
````

---

## Constraints

- **Pointers over copies.** If it lives in a file, link it.
- **Structure over prose.** Lists where lists fit; prose only where
  reasoning needs to flow.
- **~300–600 lines total.**
- **No invented content.** If a section has no content, write "(none)".
- **No duplication across sections.** Each fact lives in one place.
- **Honesty about uncertainty.** Where inference is shaky, say so.

---

## Verification step (before saving)

**Interactive mode (default).** Before writing the file, show the
drafted **Intent** and **Stance & ways of working** sections to the
user and ask:

> "Does this capture what you're actually trying to achieve, and how
> you want me to work? Anything to correct or add?"

Revise based on their answer, then save.

**Non-interactive mode (fallback).** If verification with the user is
not possible (auto-trigger on context-full, scripted invocation, etc.):

1. Mark inferred sections with confidence: **(high)**, **(medium)**,
   **(low)**.
2. Add a note at the top of **Next agent: start here**:
   "Intent and Stance were inferred without user verification. Treat
   low/medium-confidence items as hypotheses; confirm with the user on
   first turn before acting on them."
3. Set Metadata > Verification to "non-interactive".

---

## Argument handling

If the user passes arguments to the skill (e.g., via `$ARGUMENTS` in
Claude Code, or as inline text in other systems), treat them as the
next session's focus and weight **Status > Next**, **First concrete
action**, and **Tier 1 files** accordingly.

---

## Self-critical review (after drafting, before saving)

After producing the draft, run this review and iterate until no
objection survives. Save only when the document passes all ten checks.

For each section:

1. **Filled, not filler?** Sections with "(none)" are fine; padded vague
   text is not.
2. **Anything duplicated elsewhere?** Each fact lives in one place.
3. **Could the next agent act on this?** Descriptive-but-not-actionable
   content should be sharpened or cut.
4. **Is the inference honest?** For [infer] sections, signal confidence
   where it's shaky.

For the document as a whole:

5. **Could a fresh agent perform the first concrete action correctly
   using only this document and the Tier 1 files?**
6. **Are the Tier boundaries right?** Anything needed before the first
   action belongs in Tier 1; anything only conditionally needed belongs
   in Tier 2.
7. **Does Intent disambiguate Goal?** If the goal is "redesign auth" and
   Intent doesn't say whether this is a stopgap or a foundation, the
   section has failed.
8. **Does Stance tell the next agent how to be, not just what to do?**
9. **Are dead-ends captured with reasons?**
10. **Will anything go stale within a day?** If so, replace with a
    pointer to the source of truth.
