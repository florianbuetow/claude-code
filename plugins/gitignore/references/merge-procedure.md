# Merge procedure

Every `gitignore` subskill writes the file through this procedure. It is
the single definition of how entries are deduplicated, where they land,
and what must never be touched.

Read `curation-notes.md` alongside this file — it defines pattern
equivalence, template overlaps, and the canonical section headers.

---

## Step 1: Locate the file

```bash
git rev-parse --show-toplevel
```

Write `.gitignore` at the repository root unless the user names a
different path (e.g. a per-directory `.gitignore`). If the command fails,
the directory is not a Git repository — say so and stop. Do not create a
`.gitignore` outside a repository.

If `.gitignore` does not exist, this is a create; if it does, this is an
update. Both follow the same steps.

---

## Step 2: Read the existing file verbatim

```bash
cat .gitignore
```

Record, in order of appearance:

- every entry line (non-blank, not starting with `#`)
- every comment line and its position
- which entries sit under a canonical section header and which do not

This inventory is what protects user-authored structure in Step 5.

---

## Step 3: Build the candidate set

Collect the entries to add, in this order:

1. OS template(s), in the order the user named them
2. Language template(s), in the order the user named them
3. Literal entries the user specified

Then deduplicate **within** the candidate set: an entry claimed by an
earlier section is not repeated in a later one. Apply the equivalence
rules from `curation-notes.md` (so `**/.DS_Store` does not survive
alongside `.DS_Store`). Keep negation blocks intact — if a `!` line's
positive pattern is claimed by an earlier section, the `!` line moves
with it.

---

## Step 4: Deduplicate against the existing file

Drop every candidate that is already covered by an entry in the file, per
the equivalence rules. Dropping is silent bookkeeping, not a change — it
must leave the existing line, its position, and its comments exactly as
they were.

Report the count of skipped entries so the user can see the overlap.

---

## Step 5: Comment and structure rules

These are absolute:

- **Never rewrite, reword, reorder, or delete an existing entry.**
- **Never touch a comment attached to an existing entry.** The one
  exception: when an existing entry is an *exact* string match for a
  candidate entry, its comment may be replaced with the template's
  comment for that entry. Equivalent-but-not-identical patterns
  (`**/X` vs `X`) do not qualify — leave those comments alone.
- **Never move existing entries between sections**, even when a
  canonical section for them now exists.
- **Never reformat the file** — no blank-line normalization, no sorting
  of pre-existing lines.

New content is organized and commented:

- Group new entries under the canonical section header from
  `curation-notes.md` (`# --- Python ---`, `# --- Project-specific ---`, …).
- If that header already exists in the file, append the new entries at
  the end of that section rather than creating a second header.
- Keep each template's own inline comments (`# Bytecode`,
  `# Virtual environments`, …) with their entries.
- Separate sections with one blank line.
- Append new sections at the end of the file. Never insert them above
  user-authored content.

---

## Step 6: Write, then verify

Write the file, then run the checks:

```bash
git check-ignore -v --no-index <a few representative paths>
git ls-files -ci --exclude-standard
```

The first confirms the new patterns match what they should. The second
lists files that are **tracked but now ignored** — adding a pattern does
not untrack anything. If it returns rows, report them and offer:

```bash
git rm --cached <path>
```

Do not run `git rm` without the user agreeing to it.

---

## Step 7: Report

- entries added, grouped by section
- entries skipped as already covered
- any candidate withheld as a hazard (see the "deliberately not ignored"
  table in `curation-notes.md`)
- tracked-but-now-ignored files, if any

---

## Hazards: stop and ask

Apply changes directly — do not ask for confirmation on routine
additions. Stop and ask only when:

- a requested entry appears in the "deliberately not ignored" table
  (lockfiles, manifests, `vendor/`, `mix.lock`, Gradle wrapper, `*.jar`)
- a requested entry would ignore a source directory (`src/`, `lib/`,
  `tests/`, `scripts/`) or a key doc (`README.md`, `CLAUDE.md`,
  `AGENTS.md`)
- a requested entry matches files that are already tracked
- the existing file contains conflicting negations that a new pattern
  would silently break

Name the risk in one line and let the user decide.
