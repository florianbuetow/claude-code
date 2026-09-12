---
name: add
description: Add user-specified entries to a .gitignore file, creating the file if it does not exist.
argument-hint: The paths, directories, or globs to ignore (e.g. "scratch/ *.bak data/raw/").
disable-model-invocation: true
---

# Add entries to .gitignore

Add the entries the user named — the default path when the request is
"ignore X" rather than "set up a gitignore for a Python project".

---

## Step 1: Parse the requested entries

Take the paths, directories, and globs from the arguments or the user's
message. Normalize each one without changing its meaning:

- A directory gets a trailing slash: `scratch` → `scratch/` when
  `scratch` exists and is a directory.
- Strip a leading `./`: `./scratch/` → `scratch/`.
- Keep a leading `/` only if the user anchored it deliberately, or the
  artifact is specifically a repository-root product. Say so if you add
  one.
- Do not convert a name into `**/name` — a slashless pattern already
  matches at any depth (see `../../references/curation-notes.md`).

If an entry looks like a template's worth of patterns — "ignore Python
stuff", "ignore mac files" — route to `gitignore:language` or
`gitignore:os` instead of hand-writing patterns here.

---

## Step 2: Check each entry against reality

```bash
ls -d <entry> 2>/dev/null
git ls-files -- <entry> | head -5
```

- **Does not exist**: add it anyway if the user is anticipating it, but
  say that nothing currently matches — a typo'd pattern silently
  ignores nothing.
- **Already tracked**: the pattern will not untrack it. Report this
  before writing and offer `git rm --cached <path>` as a separate,
  explicit step.
- **On the hazard list** (lockfiles, manifests, `src/`, `tests/`,
  `README.md`, `CLAUDE.md`, `vendor/`, Gradle wrapper — see
  `../../references/curation-notes.md`): name the risk in one line and
  ask before adding.

---

## Step 3: Merge

Follow `../../references/merge-procedure.md` exactly.

Entries land under `# --- Project-specific ---` unless they clearly
belong to a canonical section that already exists in the file — a
`.DS_Store` request joins `# --- macOS ---`, `__pycache__/` joins
`# --- Python ---`. When an entry belongs to a template section that is
not in the file yet, offer the whole template instead of adding the one
line: "that's part of the Python template — want all of it?"

Give each added entry a short comment saying what produces it, in the
style of the templates:

```gitignore
# --- Project-specific ---

# Local scratch work
scratch/

# Editor backups of generated SQL
*.bak
```

---

## Step 4: Report

Per the merge procedure: what was added, what was skipped as already
covered, what was withheld as a hazard, and any tracked-but-now-ignored
files.

---

## Constraints

- Never modify an existing entry or its comment, except the exact-match
  case defined in the merge procedure.
- Never expand a user's single entry into a whole category on your own —
  offer the template and let them choose.
- Never add a negation (`!`) without the positive pattern it depends on
  appearing before it.
- Never write a `.gitignore` outside a Git repository.
