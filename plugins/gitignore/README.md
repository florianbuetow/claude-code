# gitignore

Create and maintain `.gitignore` files from a curated, conservative
template library.

## Usage

```
/gitignore create me a gitignore for a macOS Python project
/gitignore ignore scratch/ and *.bak
/gitignore:os macos linux
/gitignore:language python go
/gitignore:add scratch/ *.bak
```

The router reads the request, works out which operating systems,
languages, and literal entries it names, fills any gap by detection
(`uname -s`, project manifests), and dispatches to the subskills in the
order OS → language → project-specific.

## Skills

| Skill | Purpose |
|-------|---------|
| `gitignore` | Router — resolves a free-text request into targets and dispatches |
| `gitignore:os` | macOS, Windows, Linux metadata and filesystem artifacts |
| `gitignore:language` | Node.js, Python, Java, Kotlin, C, Go, Elixir artifacts and caches |
| `gitignore:add` | Entries the user names directly |

## What the templates will not do

They are trimmed from GitHub's maintained collection, and the trimming is
the point:

- Lockfiles and manifests stay versioned — `package-lock.json`,
  `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `pdm.lock`,
  `pixi.lock`, `mix.lock`, `go.sum`.
- Broad patterns that can hide real source or release artifacts are
  omitted — `*.jar`, `*.map`, bare `build/` for C, `dist/` for Node.
- The Gradle wrapper and `vendor/` stay committed.
- Editor backups (`*~`, `*.swp`) belong in a global ignore file, not a
  project one.
- Framework outputs (`.next/`, `.nuxt/`, `.svelte-kit/`) are added only
  on request, under their own section.

Full rationale and sources: `references/curation-notes.md`.

## Merge behavior

`references/merge-procedure.md` is the single definition of how the file
is written, and it is strict about existing content:

- No duplicate entries — candidates are deduplicated within the
  selection (Linux + Python share nothing, but Node + Python + Go all
  carry `.env`, and Java + Kotlin share the Maven and Gradle blocks) and
  against what the file already has. `**/X` is recognized as a duplicate
  of `X`.
- Existing entries are never rewritten, reordered, or moved, and their
  comments are never touched — the sole exception being an entry that is
  an exact string match for one being added.
- New entries are grouped under canonical section headers
  (`# --- Python ---`) with the templates' own inline comments, appended
  after user-authored content.
- After writing, `git ls-files -ci --exclude-standard` reports files that
  are tracked but now ignored, since a new pattern does not untrack
  anything.
