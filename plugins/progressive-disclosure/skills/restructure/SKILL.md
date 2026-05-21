---
name: progressive-disclosure:restructure
description: This skill should be used when the user asks to "restructure CLAUDE.md", "restructure AGENTS.md", "create a documentation index", "add a table of contents to CLAUDE.md", "organize project docs", "refactor root configuration file", "build a doc index", or wants to restructure how a repository's root configuration file references its documentation. Generates a thematic, book-style index in the highest-precedence root configuration file.
disable-model-invocation: false
---

# Restructure Progressive Disclosure

Refactor the repository's highest-precedence root configuration file to contain a thematic, book-style index of all documentation. Organizes references like a table of contents — grouped by theme, ordered for progressive discovery.

## Principles

- **Preserve existing content**: The root configuration file's existing rules and instructions are kept intact. The index is inserted as a clearly delimited section.
- **Idempotent**: Re-running produces the same result. HTML comment markers delineate the generated section so subsequent runs replace rather than duplicate.
- **Thematic ordering**: Documents are grouped by theme following the taxonomy in `references/themes.md`, not by directory structure. The ordering mimics a book's table of contents.
- **Conversational links**: Each reference uses a natural-language description that tells the agent *when* to load the document, not just *what* it contains. Example: "For TypeScript conventions, see `docs/typescript.md`" rather than a bare link.

## Workflow

### Step 0: Resolve Target File

Check whether the user explicitly named a target file in their prompt (e.g. "restructure `docs/CONTRIBUTING.md`", "update `README.md`").

- **If a file was named**: use it as the target. Verify it exists before proceeding; if it does not, halt and report the missing path.
- **If no file was named**: fall through to Step 1.

### Step 1: Select Target Root Configuration File

*Skip this step if Step 0 resolved a target.*

Apply precedence rules to find the highest-precedence existing root configuration file:

1. `AGENTS.md`
2. `CLAUDE.md`
3. `GEMINI.md`
4. `COPILOT.md`

If none exist, create `AGENTS.md` as the target.

Read the target file to understand its existing structure.

### Step 2: Discover All Documentation

Run the discovery script to enumerate all `.md` files:

```bash
"${CLAUDE_PLUGIN_ROOT}/skills/analyze/scripts/discover.sh" "$(pwd)"
```

Exclude root configuration files themselves from the index (they are the *container*, not indexed content). Include `README.md` as an indexed document.

### Step 3: Classify Documents by Theme

For each discovered document, classify it into a theme using the taxonomy in `references/themes.md`. Apply signals in order:

1. **Path-based** — match directory components against the path signal table
2. **Filename-based** — match against the filename signal table
3. **Heading-based** — read the first H1 or H2 and match keywords
4. **Fallback** — place in Appendix

This classification is semantic — use judgment for ambiguous documents. A file at `docs/auth-flow.md` with H1 "Authentication Architecture" belongs in Architecture, not Security.

### Step 4: Generate the Index

Build the index section with this structure:

```markdown
<!-- progressive-disclosure:index:start -->
## Documentation Index

### Getting Started
- For initial setup and installation, see [`docs/quickstart.md`](docs/quickstart.md)

### Architecture
- For system design and component relationships, see [`docs/architecture.md`](docs/architecture.md)
- For data flow diagrams, see [`docs/data-flow.md`](docs/data-flow.md)

### Development
- For TypeScript conventions, see [`docs/typescript.md`](docs/typescript.md)

[...additional themes with documents...]
<!-- progressive-disclosure:index:end -->
```

Rules for the generated index:
- Only include themes that have at least one document
- Each entry is a single line with a conversational prefix and a markdown link
- The conversational prefix describes *when* the agent should load that document
- Within each theme, order per `references/themes.md` within-theme rules
- Skip themes with zero documents

### Step 5: Insert or Replace in Target File

**If markers already exist** (`<!-- progressive-disclosure:index:start -->` and `<!-- progressive-disclosure:index:end -->`):
Replace everything between the markers (inclusive) with the new index block.

**If no markers exist**:
Check for an existing section heading like `## Documentation`, `## Index`, `## Table of Contents`, or `## References`. If found, insert the index block immediately after that heading (replacing its body up to the next `##`). If no matching section exists, append the index block at the end of the file.

### Step 6: Verify

After writing the index:

1. Confirm all linked files actually exist (no broken references)
2. Confirm the marker pair is present exactly once
3. Count documents indexed vs total documents found — report coverage percentage
4. If coverage is below 100%, list unindexed documents and their paths

### Presentation

After restructuring, display:
- Which root configuration file was modified
- How many documents were indexed across how many themes
- Coverage percentage
- Any documents that were skipped and why
- A reminder that re-running is safe (idempotent via markers)
