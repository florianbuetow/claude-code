---
name: language
description: Add programming-language-specific entries (Node.js, Python, Java, Kotlin, C, Go, or Elixir build artifacts and tool caches) to a .gitignore file.
argument-hint: Optional — node, python, java, kotlin, c, go, elixir (any combination). Defaults to languages detected from project manifests.
disable-model-invocation: true
---

# Add language entries to .gitignore

Add the curated build-artifact, cache, and environment patterns for one
or more languages.

---

## Step 1: Resolve which language templates to apply

| Target | Template | Recognize |
|--------|----------|-----------|
| Node.js | `../../templates/node.gitignore` | node, nodejs, npm, yarn, pnpm, javascript, js, typescript, ts |
| Python | `../../templates/python.gitignore` | python, py, django, flask, fastapi, jupyter |
| Java | `../../templates/java.gitignore` | java, maven, gradle |
| Kotlin | `../../templates/kotlin.gitignore` | kotlin, kt, kts |
| C | `../../templates/c.gitignore` | c, gcc, clang, make, cmake |
| Go | `../../templates/go.gitignore` | go, golang |
| Elixir | `../../templates/elixir.gitignore` | elixir, ex, mix, phoenix |

With no target given, detect from the repository root:

```bash
root=$(git rev-parse --show-toplevel) && ls "$root"/{package.json,pyproject.toml,setup.py,requirements.txt,pom.xml,build.gradle,build.gradle.kts,go.mod,mix.exs,Makefile,CMakeLists.txt} 2>/dev/null
```

For Java vs Kotlin, check which sources dominate:

```bash
git ls-files '*.kt' '*.kts' | head -5; git ls-files '*.java' | head -5
```

Say which languages you detected and why, in one line. Do not add a
template for a language with no evidence in the repository — an unused
template is noise that hides nothing.

---

## Step 2: Read the templates

Read each selected template verbatim. Preserve its patterns, comments,
and the order of its negation blocks.

---

## Step 3: Merge

Follow `../../references/merge-procedure.md` exactly.

Canonical section headers: `# --- Node.js ---`, `# --- Python ---`,
`# --- Java ---`, `# --- Kotlin ---`, `# --- C ---`, `# --- Go ---`,
`# --- Elixir ---`.

Language templates overlap more than OS ones. The overlap table in
`../../references/curation-notes.md` lists what to expect — `.env`
blocks across Node/Python/Go, `*.class` and the Maven/Gradle blocks
across Java/Kotlin, `*.so`/`*.dll`/`*.exe` across C/Go. Each overlapping
entry is emitted once, under the first section that claims it.

---

## Language-specific notes

- **Node.js**: lockfiles stay versioned. `dist/`, `build/`, and `out/`
  are not in the template because whether they are generated or
  committed is project-specific — add them only on request, under their
  own header. Framework outputs (`.next/`, `.nuxt/`, `.svelte-kit/`,
  `.docusaurus/`) are likewise out of scope for the language template.
- **Python**: `/build/` and `/dist/` are root-anchored on purpose, so a
  `src/mypkg/build/` source directory is not hidden. `.python-version`
  is not ignored — it is repo policy in some projects.
- **Java / Kotlin**: `**/build/` pairs with `!**/src/**/build/`, and the
  Gradle wrapper negations must stay. Generic `*.jar` is omitted —
  repositories legitimately contain vendored libraries and wrapper
  binaries.
- **C**: broad names (`*.map`, `*.out`, bare `build/`) are omitted
  because they often describe real project data. The kernel-module
  patterns are narrow on purpose — `.*.cmd` matches the dot-prefixed
  files the kernel build generates, not a project's `gradlew.cmd` or
  `build.cmd`. `*.mod` collides with Go's `go.mod`: when both templates
  are selected, emit `!go.mod` right after it (see the conflict table in
  `../../references/curation-notes.md`). Build-system directories
  (`cmake-build-*`, Autotools output) go in their own section, on
  request.
- **Go**: `go.mod`, `go.sum`, `vendor/`, `go.work`, and `go.work.sum`
  stay versioned. A project that treats `go.work` as developer-local
  can add those two lines explicitly. `*.out` is the one broad pattern
  kept on purpose — it is `go test` coverage output — so check for
  golden files first (`git ls-files '*.out'`) and say so if the pattern
  would hide `testdata/*.out`.
- **Elixir**: `mix.lock` stays versioned for applications. A library
  with a different release policy can ignore it on request. `/doc/` is
  ExDoc output, but some repositories keep hand-written docs there —
  check `git ls-files doc/` first and flag the conflict instead of
  hiding tracked documentation.

---

## Constraints

- Never modify an existing entry or its comment, except the exact-match
  case defined in the merge procedure.
- Never add a framework or build-system pattern to a language section —
  give it its own header so the distinction stays visible.
- Never ignore lockfiles, manifests, or the Gradle wrapper without the
  user explicitly confirming (see the merge procedure's hazard list).
- Never write a `.gitignore` outside a Git repository.
