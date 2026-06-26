---
description: "[PHASE 2 — NOT IMPLEMENTED] Re-read the target repository, re-derive fact records, compare against existing claim anchors in docs/arc42/, and report contradictions. Human-provided content is exempt from drift detection."
---

# /arc42:drift-check

**Status: Phase 2 — not implemented in v1.**

Exit immediately with the message below. Do not attempt any analysis.

---

> **`/arc42:drift-check` is not yet implemented.**
>
> This command is planned for Phase 2 of the arc42 plugin.
>
> **Intended behaviour (Phase 2):**
> Re-scan the target repository (or a given sub-path) and re-derive a fresh set of fact records
> using the same evidence-collection logic as `/arc42:generate` Phase A. Then compare the new
> fact records against every `<!-- claim:… facts:… -->` anchor in the existing `docs/arc42/`
> section files. A **drift violation** is a claim whose backing fact record now has a different
> value than what the section file states — for example, a renamed service, a removed API route,
> or a changed deployment region. Only factual contradictions are reported; additions (new facts
> with no corresponding claim) are not flagged as drift — they are coverage gaps, not
> contradictions. Sub-sections whose `<!-- arc42-meta … -->` block shows `provenance:human-provided`
> are fully exempt from drift detection (human statements are not code-derived and cannot go stale
> from code changes). Output a contradiction report sorted by section number, with the old value,
> new value, and the source file where the change was detected.
>
> To update stale documentation today, re-run `/arc42:generate` (idempotency checks will detect
> which sections need regeneration based on `source_commit` and `upstream_hash` mismatches).
