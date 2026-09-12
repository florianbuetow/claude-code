---
name: gitignore
description: This skill should be used when the user wants to "create a gitignore", "create a .gitignore for X", "update my gitignore", "add entries to gitignore", "ignore this in git", "gitignore for Python/Node/Java/Kotlin/C/Go/Elixir", "mac/windows/linux gitignore entries", or mentions .gitignore files, git ignore patterns, or keeping generated files out of version control.
disable-model-invocation: false
---

# Gitignore

Create or update a `.gitignore` file from a curated, conservative template
library — OS metadata, language build artifacts, or entries the user names
directly — without duplicating what the file already covers and without
disturbing what the user already wrote.

## Routing

### Step 1: Resolve the request into targets

A request like "create me a gitignore for a macOS Python project" or
"gitignore for Go on Linux, and also ignore `scratch/`" names three kinds
of target. Extract all of them from the user's wording:

**Operating systems** — `../../templates/macos.gitignore`,
`../../templates/windows.gitignore`, `../../templates/linux.gitignore`.
Recognize: macOS, mac, OSX, Darwin, Apple; Windows, win; Linux, Ubuntu,
Debian, Fedora, WSL.

**Languages** — `../../templates/node.gitignore`, and likewise
`python.gitignore`, `java.gitignore`, `kotlin.gitignore`, `c.gitignore`,
`go.gitignore`, `elixir.gitignore`.
Recognize: Node, Node.js, npm, yarn, pnpm, JavaScript, JS, TypeScript, TS;
Python, py, Django, Flask, FastAPI, Jupyter; Java, Maven, Gradle; Kotlin,
KT; C; Go, Golang; Elixir, Mix, Phoenix.

**Literal entries** — specific paths, directories, or globs the user
names (`scratch/`, `*.bak`, `data/raw/`).

A framework name implies its language (Phoenix → Elixir, Django →
Python, Next.js → Node.js), but framework-specific outputs are not in
the language templates — see the opt-in section of
`../../references/curation-notes.md`.

### Step 2: Fill the gaps by detection

If the request names no OS, detect the host:

```bash
uname -s
```

`Darwin` → macOS, `Linux` → Linux, `MINGW*`/`MSYS*`/`CYGWIN*` → Windows.

If it names no language, detect from manifests at the repository root —
resolve the root first, since the skill may be invoked from a
subdirectory:

```bash
root=$(git rev-parse --show-toplevel) && ls "$root"/{package.json,pyproject.toml,setup.py,requirements.txt,pom.xml,build.gradle,build.gradle.kts,go.mod,mix.exs,Makefile,CMakeLists.txt} 2>/dev/null
```

`package.json` → Node.js; `pyproject.toml`/`setup.py`/`requirements.txt` →
Python; `pom.xml`/`build.gradle*` → Java (Kotlin if `*.kt` sources or
`build.gradle.kts` dominate); `go.mod` → Go; `mix.exs` → Elixir;
`Makefile`/`CMakeLists.txt` with `*.c`/`*.h` sources → C.

State what you detected in one line. Do not add a template for a
language the repository shows no sign of.

### Step 3: Route

Dispatch in this order so sections land in a predictable order and
deduplication works on a stable sequence:

1. **OS targets** — follow the `gitignore:os` workflow.
2. **Language targets** — follow the `gitignore:language` workflow.
3. **Literal entries** — follow the `gitignore:add` workflow.

Skip any step with no targets. When only literal entries were named —
"add `scratch/` to my gitignore" — go straight to `gitignore:add` and do
no detection at all.

All three subskills share `../../references/merge-procedure.md`, so
running them in sequence cannot produce duplicate entries or a second
copy of a section header.

Invoke the appropriate subskills. Do not duplicate their logic here.
