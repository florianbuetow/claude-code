---
name: os
description: Add OS-specific entries (macOS, Windows, or Linux metadata and filesystem artifacts) to a .gitignore file.
argument-hint: Optional — macos, windows, linux (any combination). Defaults to the host OS.
disable-model-invocation: true
---

# Add OS entries to .gitignore

Add the curated OS metadata and filesystem-artifact patterns for one or
more operating systems.

---

## Step 1: Resolve which OS templates to apply

From arguments or the user's message:

| Target | Template | Recognize |
|--------|----------|-----------|
| macOS | `../../templates/macos.gitignore` | macos, mac, osx, darwin, apple |
| Windows | `../../templates/windows.gitignore` | windows, win |
| Linux | `../../templates/linux.gitignore` | linux, ubuntu, debian, fedora, wsl |

With no target given, detect the host with `uname -s` (`Darwin` → macOS,
`Linux` → Linux, `MINGW*`/`MSYS*`/`CYGWIN*` → Windows) and say which one
you picked.

Multiple targets are normal — a repository worked on from several
machines should carry all of them. Apply them in the order the user named
them (detected host first when detecting).

---

## Step 2: Read the templates

Read each selected template verbatim. Do not paraphrase, reorder, or
trim its patterns and comments — the curation is the point.

---

## Step 3: Merge

Follow `../../references/merge-procedure.md` exactly: build the candidate
set, deduplicate within it and against the existing file, obey the
comment and structure rules, write, verify, report.

Canonical section headers: `# --- macOS ---`, `# --- Windows ---`,
`# --- Linux ---`.

---

## OS-specific notes

- The Windows template deliberately omits `*.stackdump`, `*.msi`,
  `*.cab`, `*.msix`, `*.msm`, `*.msp`, and `*.lnk`. Offer them as
  commented opt-ins only if the user mentions Cygwin, installer builds,
  or committed shortcuts.
- The Linux template deliberately omits `*~` and `*.swp`. Those are
  editor behavior, not Linux behavior — if the user wants them, point
  them at a global ignore file (`~/.config/git/ignore`) rather than
  adding them to the project.
- The macOS template covers modern metadata only; classic Mac OS 6–9
  entries, quota files, and Time Machine backup directories are
  intentionally absent.
- `$RECYCLE.BIN/` and `.Trash-*/` contain a literal `$` and `*`. Write
  them exactly as the template has them.

---

## Constraints

- Never modify an existing entry or its comment, except the exact-match
  case defined in the merge procedure.
- Never add editor, IDE, or framework patterns here — this skill is OS
  artifacts only.
- Never write a `.gitignore` outside a Git repository.
