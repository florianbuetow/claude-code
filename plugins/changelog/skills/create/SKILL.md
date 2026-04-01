---
name: changelog:create
description: This skill should be used when the user asks to "create a changelog", "initialize CHANGELOG.md", "start a changelog", or when the main changelog skill detects no existing CHANGELOG.md file. Creates a new CHANGELOG.md from scratch by analyzing the full git commit history and organizing changes by date-based version sections.
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
- **Tags present?** — If semver tags exist (e.g., `v1.2.0`, `1.0.0`), use them as version boundaries to create one section per tagged release. Commits after the latest tag go under `[Unreleased]`.
- **No tags?** — Use date-based grouping (see Step 2).
- **Remote URL** — Extract the GitHub/GitLab base URL for version comparison links.

### Step 2: Group Commits into Sections

**Always produce date-based sections.** Never dump all commits into a single flat `[Unreleased]` list.

#### When tags exist

Use tags as primary version boundaries. Within each tagged version, order entries chronologically. Commits after the latest tag go under `[Unreleased]`.

#### When no tags exist

Group commits by date into meaningful sections. Use the commit dates to find natural boundaries:

1. **Scan commit dates** — Identify clusters of activity separated by gaps.
2. **Choose a grouping granularity** based on the project's history span:
   - **< 1 month of history** — Group by week (e.g., `## Week of 2026-03-24`).
   - **1–6 months** — Group by week or biweekly, whichever produces 4–12 sections.
   - **> 6 months** — Group by month (e.g., `## 2026-03`).
3. **Use ISO date headings** — Format sections as `## YYYY-MM-DD` (for the start date of each group) rather than invented version numbers.
4. **Place commits after the most recent group boundary** under `[Unreleased]`.

The goal is **4–12 sections** that each tell a coherent story. Adjust granularity to hit that range. A single flat list is never acceptable.

### Step 3: Analyze Commits

For each section (tag-based or date-based), classify commits into six categories:

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

### Step 4: Write the File

Consult `../changelog/references/format-guide.md` for the full template and formatting rules.

Build the file with:
1. `# Changelog` header and standard intro paragraph referencing Keep a Changelog and SemVer
2. `## [Unreleased]` section (just the heading, no empty sub-headings)
3. One section per version or date group, in reverse chronological order:
   - **Tagged releases:** `## [X.Y.Z] – YYYY-MM-DD`
   - **Date-based groups:** `## YYYY-MM-DD` (start date of the group)
4. Only category headings that have entries (omit empty ones)
5. Reference-style version comparison links at the bottom (for tagged versions; omit for date-based groups)

Use ISO date format (`YYYY-MM-DD`). Detect the remote URL for version links from `git remote get-url origin`.

### Step 5: Present the Result

Show the full generated changelog content inline.

## Key Rules

- **Date-based sections are mandatory** — Never produce a single flat list. Every changelog must have multiple dated sections that tell the project's story over time.
- **For humans, not machines** — Never dump raw git log. Synthesize into user-facing descriptions.
- **Be specific** — "Fixed crash when uploading large files", not "Bug fixes".
- **Canonical category order** — Added, Changed, Deprecated, Removed, Fixed, Security.
- **Omit empty categories** — Only include headings that have entries.
- **Past tense consistently** — "Added", "Fixed", "Removed".
- **Call out breaking changes** — Prefix with `**BREAKING:**`, describe impact, provide migration path.
- **Deprecate before removing** — Mention the target major version when deprecating.

## Reference Files

- **`../changelog/references/format-guide.md`** — Complete format spec, template, style rules, antipatterns, breaking change handling
