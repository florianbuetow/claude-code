# Curation notes

Shared reference for every `gitignore` skill. The templates in
`templates/` are intentionally conservative: they ignore files that are
generated, disposable, machine-local, or OS metadata, and avoid broad
patterns that can hide legitimate source files or reproducibility
metadata.

---

## Pattern semantics

A pattern containing **no slash** already matches that name at any
directory depth. So:

```gitignore
.DS_Store
node_modules/
__pycache__/
```

already match `foo/.DS_Store`, `packages/a/node_modules/`, and
`src/x/__pycache__/`.

`**/.DS_Store` is valid but redundant — treat it as a duplicate of
`.DS_Store`. Prefer the simpler Git-native form unless `**` expresses a
genuinely nested pattern (as in `**/build/` + `!**/src/**/build/`).

A leading `/` anchors a pattern to the repository root. Use it when the
artifact is specifically a project-root product (`/build/`, `/_build/`,
`/deps/`) rather than something that may recur in subprojects.

A `!` negation only works if it comes **after** the pattern it
re-includes, and Git cannot re-include a file inside an excluded
directory. Never split these blocks:

```gitignore
.yarn/*
!.yarn/patches/
...
.pixi/*
!.pixi/config.toml
**/build/
!**/src/**/build/
```

The Gradle wrapper negations in the Java and Kotlin templates are the one
sanctioned exception to "a negation needs a positive pattern above it":
nothing in those templates excludes the wrapper, so the lines are a guard
that only takes effect if a project later adds `*.jar` in another
section. Keep them, and do not invent new negations of this kind.

---

## Pattern equivalence (for deduplication)

Two entries are duplicates when:

- They are byte-identical after trimming trailing whitespace.
- One is `**/X` and the other is `X`, where `X` contains no slash.
- One is `/X` and the other is `X` **only at repository root** — these
  are not equivalent in general. If the file already has the broader
  `X`, do not add `/X`; if it has only `/X` and the template wants `X`,
  add `X` and leave `/X` alone rather than rewriting it.

`X` and `X/` are **not** duplicates (the second matches directories
only). If the file has `X` and the template wants `X/`, skip the
addition — the broader pattern already covers it.

---

## Overlaps between templates

When several templates are selected, these entries appear in more than
one and must be emitted only once:

| Entry | Templates |
|-------|-----------|
| `.env`, `.env.*`, `!.env.example`, `!.env.template` | node, python, go |
| `*.lcov` | node, python |
| `*.so`, `*.dylib`, `*.dll`, `*.exe` | c, go |
| `*.class`, `hs_err_pid*`, `replay_pid*` | java, kotlin |
| Maven block (`target/`, `pom.xml.*`, …) | java, kotlin |
| Gradle block (`.gradle/`, `**/build/`, wrapper negations) | java, kotlin |
| `coverage/` vs `coverage.*` | node, go (different patterns — keep both) |

## Conflicts between templates

Not every cross-template interaction is a duplicate. These actively fight
each other and must be handled when both templates are selected:

| Conflict | Handling |
|----------|----------|
| C's `*.mod` (Linux kernel module) matches Go's `go.mod`, which stays versioned | When C and Go are both selected, emit `!go.mod` immediately after `*.mod` in the C section and say why |
| C's `*.so`/`*.dll`/`*.dylib`/`*.exe` duplicate Go's | First section claims them; do not repeat |
| Go's `*.out` is broader than the C template allows (C omits `*.out` deliberately) | Keep Go's — it is coverage output — but warn if the repo has `testdata/*.out` golden files, which it would hide |

---

## Deliberately not ignored

Never add these unless the user explicitly asks, and warn when they do:

| File | Why it stays versioned |
|------|------------------------|
| `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` | npm documents committing the lockfile |
| `pyproject.toml`, `poetry.lock`, `uv.lock`, `Pipfile`, `Pipfile.lock`, `pdm.lock`, `pixi.lock` | reproducible resolution |
| `.python-version` | repo policy in some projects, developer-local in others |
| `go.mod`, `go.sum`, `go.work`, `go.work.sum`, `vendor/` | `vendor/` and workspaces are often intentional |
| `mix.lock` | applications normally commit it |
| `gradle-wrapper.jar`, `gradle-wrapper.properties` | wrapper must stay versioned |
| `*.jar`, `*.war`, `*.zip` | may be vendored libs, fixtures, or release artifacts |
| `dist/`, `build/`, `out/` (Node) | whether generated or committed is project-specific |

`*.map`, `*.out`, and bare `build/` are omitted from the C template for
the same reason: they often describe legitimate project data.

---

## Opt-in patterns (commented, never enabled by default)

Offer these only when the user's request names the tool or platform:

```gitignore
# Cygwin crash dump; enable if Cygwin is used
# *.stackdump

# Windows installer/package files can be legitimate release artifacts
# *.cab
# *.msi
# *.msix
# *.msm
# *.msp

# Windows shortcuts can be intentional repository content
# *.lnk
```

Editor backup patterns (`*~`, `*.swp`) are editor behavior, not OS
behavior. They belong in a global gitignore
(`~/.config/git/ignore`), not a project template — say so rather than
adding them.

Framework outputs (`.next/`, `.nuxt/`, `.svelte-kit/`, `.docusaurus/`)
and build-system directories (`cmake-build-*`, Autotools output) are not
part of the language templates. Add them only when the project actually
uses that framework or build system, under their own section header.

---

## Canonical section headers

Generated sections use exactly these headers so later runs can find and
extend them:

```text
# --- macOS ---
# --- Windows ---
# --- Linux ---
# --- Node.js ---
# --- Python ---
# --- Java ---
# --- Kotlin ---
# --- C ---
# --- Go ---
# --- Elixir ---
# --- Project-specific ---
```

Anything else in the file is user-authored structure. Leave it alone.

---

## Sources

Baseline: GitHub's maintained collection, https://github.com/github/gitignore
(Global/macOS, Global/Windows, Global/Linux, Node, Python, Java, C, Go,
Elixir, Kotlin, Gradle, Maven), trimmed of obsolete, overly broad,
editor-specific, and framework-specific patterns.

Verification: https://docs.github.com/en/get-started/git-basics/ignoring-files,
https://docs.npmjs.com/files/package-lock.json/,
https://specifications.freedesktop.org/trash/latest/,
https://go.dev/doc/tutorial/workspaces
