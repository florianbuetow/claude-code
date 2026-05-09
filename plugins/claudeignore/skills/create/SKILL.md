---
name: create
description: Analyze a repository and generate a new .claudeignore file that excludes
  directories and files wasting context tokens.
argument-hint: Optional — specific directories or patterns to include.
disable-model-invocation: true
---

# Create .claudeignore

Analyze the repository structure and generate a `.claudeignore` file that
excludes directories and files which waste context tokens without
providing useful source code.

---

## Step 1: Scan the repository

Run these commands to understand the project structure:

1. List all top-level directories:
   ```
   find . -maxdepth 1 -type d | sort
   ```

2. Measure directory sizes to identify large non-source content:
   ```
   du -sh */ .*/ 2>/dev/null | sort -rh | head -30
   ```

3. Detect the project type from manifest files:
   - Python: `pyproject.toml`, `setup.py`, `requirements.txt`
   - Node/JS: `package.json`
   - Rust: `Cargo.toml`
   - Go: `go.mod`
   - Java/Kotlin: `pom.xml`, `build.gradle`
   - Ruby: `Gemfile`
   - Mixed: multiple of the above

4. Check what `.gitignore` already excludes (for reference, not copying):
   ```
   cat .gitignore 2>/dev/null
   ```

---

## Step 2: Classify directories and files

Apply this heuristic to every entry: **"Would I ever want Claude to
edit or inspect this for normal coding tasks?"** If no, it belongs in
`.claudeignore`.

Things that are **large, generated, noisy, secret, or not useful for
day-to-day coding decisions** should be ignored. Source code, key
configs, and docs should stay visible.

Start from `.gitignore` as a baseline, then:
- **Remove** anything Claude still needs for reasoning (manifests,
  core config, docs).
- **Add** anything generated or irrelevant to code changes that
  `.gitignore` keeps (e.g., `data/`, `notebooks/`, large media).

Sort entries into these categories:

### Always ignore (caches, build artifacts, dependencies)

These never contain useful source code for Claude:

| Pattern | Ecosystem | Why |
|---------|-----------|-----|
| `.venv/`, `venv/`, `env/` | Python | Virtual environment packages |
| `node_modules/` | Node.js | npm/yarn packages |
| `__pycache__/` | Python | Bytecode cache |
| `*.pyc` | Python | Compiled bytecode files |
| `.mypy_cache/` | Python | Type checker cache |
| `.ruff_cache/` | Python | Linter cache |
| `.pytest_cache/` | Python | Test runner cache |
| `.cache/` | General | Generic caches |
| `target/` | Rust/Java | Build artifacts |
| `build/`, `dist/` | General | Build output |
| `.gradle/` | Java/Kotlin | Gradle cache |
| `.next/` | Next.js | Build output |
| `.nuxt/` | Nuxt.js | Build output |
| `.turbo/` | Turborepo | Build cache |
| `vendor/` | Go/PHP | Vendored dependencies |
| `coverage/`, `htmlcov/` | General | Coverage reports |
| `.tox/`, `.nox/` | Python | Test environment tools |
| `.cargo/` | Rust | Cargo cache |

### Always ignore (secrets and credentials)

These reduce the chance sensitive content enters context:

| Pattern | Why |
|---------|-----|
| `.env` | Environment secrets |
| `.env.*` | Per-environment secrets |
| `*.pem`, `*.key` | Private certificates and keys |
| `*-credentials.json` | Service account credentials |
| `.secrets/` | Secret stores |

### Always ignore (tool/IDE config)

| Pattern | Why |
|---------|-----|
| `.cursor/` | Cursor IDE state |
| `.idea/` | JetBrains IDE config |
| `.vscode/` | VS Code config (unless project-shared) |
| `.playwright-mcp/` | Playwright MCP temp files |
| `.dolt/`, `.doltcfg/` | Dolt/beads database internals |

### Always ignore (logs and noise)

| Pattern | Why |
|---------|-----|
| `*.log` | Log files |
| `logs/` | Log directories |
| `*.sqlite`, `*.db` | Local databases |

### Ignore if large (> 1 MB) and not source code

Review these on a case-by-case basis:

- `notebooks/` — Jupyter notebooks with embedded outputs
- `reports/` — Generated analysis reports
- `docs/` — If dominated by generated API docs or large assets
- `stubs/` — Type stubs
- `debug/` — Ephemeral diagnostic scripts
- `data/`, `datasets/` — Data files (unless small config/fixture data)
- `assets/`, `static/`, `public/` — Media and static files
- `fixtures/` — Test fixtures if large

### Never ignore (source code and key files — keep readable)

- `src/`, `lib/`, `app/` — Application source
- `tests/`, `test/`, `spec/` — Test source
- `scripts/` — Build/utility scripts
- `config/` — Configuration files
- `prompts/` — Prompt templates
- `tools/` — Developer tools
- `frontend/` — Frontend source (but ignore `frontend/node_modules/`)
- `README.md`, `CLAUDE.md`, `AGENTS.md` — Project documentation
- `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod` — Manifests
- `tsconfig.json`, `eslint.config.*` — Core tooling config

Over-ignoring these makes Claude guess incorrectly about app structure
and tooling.

---

## Step 3: Present the plan

Show the user a table of what will be ignored and why:

```
| Directory | Size | Category | Reason |
|-----------|------|----------|--------|
| .venv/ | 1.7 GB | dependency cache | Python packages |
| ...       | ...  | ...      | ...    |
```

Also note any borderline decisions where the user might disagree.

Ask:
> "Here's what I'd ignore. Want me to add or remove anything before I
> write the file?"

---

## Step 4: Write the file

After confirmation, write `.claudeignore` in the project root.

Group entries by category with comment headers. Use trailing slashes
for directories. Example:

```
# Python caches
.venv/
__pycache__/
.mypy_cache/
.ruff_cache/
.pytest_cache/

# Build artifacts
build/
dist/

# IDE/tool config
.cursor/
.idea/

# Large non-source directories
notebooks/
data/
```

---

## Step 5: Report

After writing, report:

- Number of entries added
- Estimated context savings (rough, based on directory sizes)
- Reminder that specific files from ignored directories can still be
  read on demand via explicit path

---

## Constraints

- **Never ignore source code directories** (`src/`, `lib/`, `tests/`,
  `scripts/`, etc.) unless the user explicitly asks.
- **Never silently ignore `config/`** — it almost always contains
  important configuration.
- **Never ignore project manifests** (`pyproject.toml`, `package.json`,
  `Cargo.toml`, `go.mod`, `tsconfig.json`) — Claude needs these to
  understand the project stack.
- **Never ignore `README.md` or `CLAUDE.md`** — these orient Claude.
- **Always include secrets.** `.env`, `.env.*`, private keys, and
  credential files should always be in `.claudeignore`, even if not
  in `.gitignore` — defense in depth against leaking into context.
- **Present the plan before writing.** Do not write without user
  confirmation.
- **Use .gitignore as starting point, not as copy source.**
  `.claudeignore` serves a different purpose — `.gitignore` excludes
  from version control, `.claudeignore` excludes from AI context.
  They often overlap but are not the same. Start from `.gitignore`,
  remove what Claude needs, add what Claude doesn't.
- **Prefer directories over globs.** `node_modules/` is better than
  `**/node_modules/**` for readability.

---

## Argument handling

If the user passes arguments (e.g., `create data/ logs/`), treat them
as additional directories to include in the ignore list. Still run the
full scan — the arguments are additions, not the complete list.
