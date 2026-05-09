---
name: update
description: Update an existing .claudeignore file by adding, removing, or revising
  entries based on current repository state.
argument-hint: Optional — what to add, remove, or change (e.g., "add data/", "remove debug/").
disable-model-invocation: true
---

# Update .claudeignore

Modify an existing `.claudeignore` file based on the user's request or
a fresh analysis of the repository.

---

## Step 1: Read the current file

Read `.claudeignore` from the project root.

If the file does not exist, tell the user:

> "No `.claudeignore` found in this project. Use `claudeignore:create`
> to generate one from scratch."

Do not fall through to creation logic.

---

## Step 2: Determine what changed

There are three update modes:

### Mode A: Explicit request

The user asks to add or remove specific entries (e.g., "add data/",
"remove debug/", "stop ignoring reports/").

- Parse the request into add/remove operations.
- Skip the scan — the user knows what they want.

### Mode B: Drift check

The user asks to "review" or "refresh" the claudeignore, or simply
invokes `claudeignore:update` without specifics.

1. Scan the repository (same as create Step 1).
2. Compare the scan results against the current `.claudeignore`:
   - **Missing entries**: directories that should be ignored but aren't.
     Apply the heuristic: large, generated, noisy, secret, or not useful
     for day-to-day coding decisions → should be ignored.
   - **Missing secrets**: check for `.env`, `.env.*`, `*.pem`, `*.key`,
     or credential files that aren't ignored yet.
   - **Stale entries**: directories in `.claudeignore` that no longer
     exist in the repo.
   - **Questionable entries**: source directories, manifests
     (`pyproject.toml`, `package.json`), or key docs (`README.md`,
     `CLAUDE.md`) that are being ignored — likely a mistake.
   - **Over-ignored**: files Claude needs to understand the project
     structure (core config, tooling config) that are currently ignored.
3. Present findings as a diff.

### Mode C: From arguments

If arguments are provided, parse them as directives:

- Bare directory names → add them (e.g., `update data/ logs/`)
- Prefixed with `-` or `!` → remove them (e.g., `update -debug/ !reports/`)
- `--refresh` or `--check` → trigger drift check (Mode B)

---

## Step 3: Present the changes

Show the user what will change using a before/after or diff format:

```
Changes to .claudeignore:

+ data/              # add — 450 MB data files, not source code
+ logs/              # add — log output, not useful for context
- debug/             # remove — user wants debug scripts indexed
~ stubs/ → stubs/py  # modify — narrow the scope
```

Ask:
> "Here are the proposed changes. Apply them? (yes / edit / no)"

---

## Step 4: Apply changes

After confirmation:

1. Read the current `.claudeignore` content.
2. Apply the additions, removals, and modifications.
3. Maintain the category comment structure — add new entries under the
   appropriate category header, or create a new category if needed.
4. Remove empty category sections (header with no entries below it).
5. Write the updated file.

---

## Step 5: Report

After writing, report:

- Summary of changes (N added, N removed, N modified)
- Any stale entries that were cleaned up
- Reminder about on-demand reading of ignored paths

---

## Constraints

- **Never remove entries without confirmation.** Even stale entries
  might be intentional (anticipating future directories).
- **Preserve existing comments and structure.** Don't reformat the
  entire file just to add one entry.
- **Warn on source directory ignores.** If the user asks to ignore
  `src/`, `lib/`, `tests/`, or `scripts/`, flag it:
  > "Warning: `src/` contains source code. Ignoring it means I won't
  > see your application code. Are you sure?"
- **Warn on manifest/config ignores.** If the user asks to ignore
  `pyproject.toml`, `package.json`, `tsconfig.json`, or similar, flag it:
  > "Warning: this is a project manifest. Ignoring it means I won't
  > understand your project's dependencies and tooling. Are you sure?"
- **Always recommend secrets.** During drift checks, if `.env`,
  `.env.*`, `*.pem`, `*.key`, or credential files exist and aren't
  ignored, flag them as recommended additions — defense in depth
  against sensitive content entering context.
- **Validate entries exist.** When adding directories, check that they
  actually exist. If they don't, warn the user but still add if they
  confirm — they may be anticipating future directories.
- **Read-only on error.** If the file can't be parsed or written,
  report the error and stop. Do not silently create a new file.

---

## Argument handling

Arguments are parsed as directives (see Mode C above). If no arguments
are provided and the user's message doesn't specify what to change,
default to Mode B (drift check).
