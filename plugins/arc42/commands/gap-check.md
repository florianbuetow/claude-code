---
description: "[PHASE 2 — NOT IMPLEMENTED] Check docs/arc42/ for missing topic coverage against the expected-topics catalog, excluding generated GAP flags. Reports which arc42 topics have no documented coverage in the generated sections."
---

# /arc42:gap-check

**Status: Phase 2 — not implemented in v1.**

Exit immediately with the message below. Do not attempt any analysis.

---

> **`/arc42:gap-check` is not yet implemented.**
>
> This command is planned for Phase 2 of the arc42 plugin.
>
> **Intended behaviour (Phase 2):**
> Read `docs/arc42/` and compare the generated section files against the expected-topics catalog in
> `skills/arc42-framework/references/expected-topics.md`. For each expected topic that has no
> documented coverage in any section file — and is not already represented by an open GAP flag —
> report it as a missing-coverage finding with the section where it should appear and a suggested
> sub-section heading. Exclude topics that are already flagged as `GAP:human-input` or
> `GAP:no-evidence` (those are tracked in `_gaps.md` and handled by `/arc42:fill-gaps` or a
> re-run of `/arc42:generate`). Output a prioritised list of missing-coverage findings sorted by
> section number.
>
> To resolve documentation gaps today, use `/arc42:fill-gaps` for human-input gaps or
> re-run `/arc42:generate` with updated source evidence for code-derivable gaps.
