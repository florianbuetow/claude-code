---
description: Walk through each open GAP flag in docs/arc42/_gaps.md, prompt for human input, write the answer into the relevant section file, re-tag that sub-section's arc42-meta provenance to human-provided, and remove the resolved GAP flag from _gaps.md. Resumable and idempotent — gaps already tagged human-provided are skipped automatically.
---

# /arc42:fill-gaps

You are the **gap resolver** for arc42 documentation. Walk the user through every open human-input GAP flag, collect answers, and write them back into the correct section files. Operate interactively — ask one gap at a time.

---

## Setup — locate the docs root

1. Determine `docs-root`: look for `docs/arc42/` relative to `git rev-parse --show-toplevel`. If the repository has no git root, use `./docs/arc42/`. If `docs-root` does not exist, stop with:

   > No arc42 documentation found. Run `/arc42:generate` first to produce `docs/arc42/`.

2. Verify `<docs-root>/_gaps.md` exists. If it does not, stop with:

   > `docs/arc42/_gaps.md` not found. Run `/arc42:generate` to create the GAP registry, then re-run this command.

3. Read `<docs-root>/_gaps.md` fully. Parse every gap entry:
   - Gap type (`human-input` or `no-evidence`)
   - Question / sought text
   - Section file (relative path within `docs-root`)
   - Arc42-meta sub-section id

---

## Step 1 — Filter to actionable gaps

Only **human-input** gaps require interactive resolution. `no-evidence` gaps cannot be resolved here (they require adding evidence files and re-running `/arc42:generate`).

From the parsed list:

- Include: `human-input` gaps whose corresponding sub-section in the section file still has `provenance:gap-human` in its `<!-- arc42-meta … -->` block. These are **open**.
- Skip: gaps whose sub-section already shows `provenance:human-provided` in the section file. These are **already resolved** — the gap was filled in a previous run.
- Note: `no-evidence` gaps are **not actionable here**; list them at the end of the session as a reminder to add evidence and re-run `/arc42:generate`.

If there are zero open human-input gaps, print:

> All human-input gaps are already resolved. No action needed.
> 
> `no-evidence` gaps remaining: <N> — these require code evidence; re-run `/arc42:generate` after the missing code artifacts are added to the repository.

Then exit.

---

## Step 2 — Interactive gap resolution loop

For each open human-input gap (in the order they appear in `_gaps.md`):

### 2.1 Present the gap

Print a numbered prompt:

```
Gap <i> of <total_open>
Section: <NN-slug> — <sub-section id>
File:    docs/arc42/<section-file>

Question: <question text from GAP flag>

Your answer (or press Enter to skip this gap for now):
```

### 2.2 Collect the answer

- If the user provides a non-empty answer: proceed to step 2.3.
- If the user presses Enter (empty answer): mark this gap as **deferred** and move to the next one. Do not modify any file.
- If the user types `quit` or `exit`: stop the loop immediately. Summarise progress (resolved, deferred, remaining) and exit.

### 2.3 Write the answer into the section file

Open `<docs-root>/<section-file>`. Locate the sub-section whose id matches `<sub-section id>` from the gap entry. The sub-section is identified by its `<!-- arc42-meta section:<id> … -->` block.

Perform the following edits atomically (read the file, apply all changes, write once):

**a) Replace the GAP flag** — find the `<!-- GAP:human-input <question> -->` line(s) within this sub-section and replace them with the user's answer formatted as prose (wrap at ~100 characters; do not add headers or bullet points unless the answer itself contains them).

**b) Add a per-claim anchor** — immediately after the inserted prose, append:
```
<!-- claim:<sub-section-id>.human facts:human-provided -->
```

**c) Update the arc42-meta block** — in the `<!-- arc42-meta section:<id> … -->` block for this sub-section:
- Change `provenance:gap-human` to `provenance:human-provided`
- Change `confidence:low` to `confidence:medium` (human statement without verifiable source)
- Clear the `gaps:` list entry for this gap (set to `[]` if all gaps in the sub-section are now resolved)

Do not modify any other part of the file. Do not change other sub-sections.

### 2.4 Confirm the write

After writing the file, print:

```
✓ Gap <i> resolved — docs/arc42/<section-file> updated.
```

---

## Step 3 — Update `_gaps.md`

After the interactive loop finishes (all gaps answered, skipped, or the user quit):

Rewrite `<docs-root>/_gaps.md`:

1. Remove every resolved gap entry (those where the section file now has `provenance:human-provided`).
2. Keep all deferred gaps (user pressed Enter), `no-evidence` gaps, and any gaps that were already in the file before this run.
3. Update the front-matter: recalculate `total_gaps` and update `generated_at` to now.

Write the file atomically (read current content, apply removals, write once). Do not append — overwrite.

---

## Step 4 — Session summary

Print a final summary block:

```
/arc42:fill-gaps session complete
  Resolved this session: <R> gaps
  Deferred (skipped):    <D> gaps
  Already resolved:      <A> gaps (skipped — already human-provided)
  No-evidence gaps:      <E> gaps (not actionable here — re-run /arc42:generate after adding evidence)
  Remaining open:        <O> human-input gaps in _gaps.md
```

If `Remaining open` > 0:

> Run `/arc42:fill-gaps` again to continue resolving the remaining gaps.

---

## Hard constraints

- **Never fabricate** answers. Only text the user types becomes content in the section file.
- **Never modify** the evidence base (`_evidence.md`), other section files, or any file outside `docs/arc42/`.
- **Never remove** a `no-evidence` GAP flag — those can only be resolved by `/arc42:generate` after the missing evidence is added to the repository.
- **Idempotent** — running this command multiple times produces the same result as running it once. Already-resolved gaps are detected and skipped automatically.
- **Resumable** — if the user quits mid-session, all resolved gaps are preserved. The next run of `/arc42:fill-gaps` picks up at the first remaining open gap.
