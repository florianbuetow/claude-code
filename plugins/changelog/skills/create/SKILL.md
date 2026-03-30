---
name: changelog:create
description: This skill should be used when the user asks to "create a changelog", "initialize CHANGELOG.md", "start a changelog", or when the main changelog skill detects no existing CHANGELOG.md file. Creates a new CHANGELOG.md from scratch by analyzing the full git commit history and organizing changes by version tags.
---

# Create Changelog

Create a new `CHANGELOG.md` from scratch by analyzing the full git history. Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Workflow

### Step 1: Gather Git Context

Run these commands in parallel:

```bash
git tag --sort=-version:refname          # All tags, newest first
git log --oneline --date=short --format="%h %ad %s"       # Full commit history
git remote get-url origin 2>/dev/null    # Remote URL for version links
```

Determine:
- **Tags present?** — If semver tags exist (e.g., `v1.2.0`, `1.0.0`), use them as version boundaries to create one section per tagged release.
- **No tags?** — Place all commits under `[Unreleased]`.
- **Remote URL** — Extract the GitHub/GitLab base URL for version comparison links.

### Step 2: Analyze Commits

For each version range (tag-to-tag, or all commits if no tags), classify commits into six categories:

| Category | Signals |
|----------|---------|
| Added | `feat:`, "add", "new", "introduce", "implement" |
| Changed | `refactor:`, "update", "change", "rename", "migrate", "improve" |
| Deprecated | `deprecate:`, "sunset" |
| Removed | `remove:`, "drop", "delete", "strip" |
| Fixed | `fix:`, "bug", "patch", "resolve", "correct" |
| Security | `security:`, "CVE", "vulnerability" |

**Skip merge commits** — Merge commits (e.g., "Merge branch ...", "Merge pull request ...") duplicate the merged commits.

**Omit** commits that are purely internal (CI/CD, docs-only, trivial chores) unless user-facing.

**Prefix priority** — When a conventional commit prefix is present (e.g., `feat:`, `fix:`), use it to determine the category. Only fall back to keyword matching when no recognized prefix exists.

**Synthesize, do not copy** — Group related commits into single user-facing bullet points. Write short, specific, past-tense descriptions focused on what the user sees or feels.

### Step 3: Write the File

Consult `../changelog/references/format-guide.md` for the full template and formatting rules.

Build the file with:
1. `# Changelog` header and standard intro paragraph referencing Keep a Changelog and SemVer
2. `## [Unreleased]` section (just the heading, no empty sub-headings)
3. One `## [X.Y.Z] – YYYY-MM-DD` section per tagged version, in reverse chronological order
4. Only category headings that have entries (omit empty ones)
5. Reference-style version comparison links at the bottom (no heading, no separators)

Use ISO date format (`YYYY-MM-DD`). Detect the remote URL for version links from `git remote get-url origin`.

### Step 4: Present the Result

Show the full generated changelog content inline.

## Key Rules

- **For humans, not machines** — Never dump raw git log. Synthesize into user-facing descriptions.
- **Be specific** — "Fixed crash when uploading large files", not "Bug fixes".
- **Canonical category order** — Added, Changed, Deprecated, Removed, Fixed, Security.
- **Omit empty categories** — Only include headings that have entries.
- **Past tense consistently** — "Added", "Fixed", "Removed".
- **Call out breaking changes** — Prefix with `**BREAKING:**`, describe impact, provide migration path.
- **Deprecate before removing** — Mention the target major version when deprecating.

## Reference Files

- **`../changelog/references/format-guide.md`** — Complete format spec, template, style rules, antipatterns, breaking change handling
