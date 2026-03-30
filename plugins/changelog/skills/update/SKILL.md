---
name: changelog:update
description: This skill should be used when the user asks to "update the changelog", "add to the changelog", "changelog for new release", "update CHANGELOG.md", or when the main changelog skill detects an existing CHANGELOG.md file. Appends new version entries by analyzing commits since the last documented version.
---

# Update Changelog

Update an existing `CHANGELOG.md` with new entries by analyzing commits since the last documented version. Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Workflow

### Step 1: Read Existing Changelog

Read `CHANGELOG.md` from the project root (case-insensitive: also check `changelog.md`, `Changelog.md`).

Parse to determine:
- **Latest documented version** — The most recent `## [X.Y.Z]` heading.
- **Has `[Unreleased]` section?** — Note its position and any existing bullets.
- **Has version links section?** — Note its position at the bottom.

### Step 2: Find the Boundary Commit

The boundary commit is the last commit already documented in the changelog. Everything after it is new.

**Strategy (try in order until one succeeds):**

1. **Tag match** — If the latest documented version (e.g., `1.2.0`) has a corresponding git tag (`v1.2.0` or `1.2.0`), use that tag as the boundary: `git log <tag>..HEAD`.
2. **Date match** — If no tag matches, use the release date from the version heading (`## [1.2.0] – 2026-03-15`) and find commits after that date: `git log --after="2026-03-15"`.
3. **Content match** — As a last resort, search the git log for a commit message that corresponds to a notable entry in the latest version section, and use that commit as the boundary.

If none of these strategies produce a clear boundary, inform the user and ask which commit to start from.

### Step 3: Gather New Commits

Run these commands in parallel:

```bash
git tag --sort=-version:refname          # All tags, newest first
git log --oneline --date=short --format="%h %ad %s" <boundary>..HEAD  # Commits since boundary
git remote get-url origin 2>/dev/null    # Remote URL for version links
```

Determine:
- **New tags since boundary?** — Create one section per new tag.
- **Untagged commits after latest tag?** — Add them to `[Unreleased]`.
- **No new commits?** — **Stop here.** Do not modify the file. Inform the user: "CHANGELOG.md is already up to date — no new commits found since version X.Y.Z (YYYY-MM-DD)."

### Step 4: Analyze New Commits

For each new version range, classify commits into six categories:

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

### Step 5: Insert New Entries

Consult `../changelog/references/format-guide.md` for formatting rules.

**Insertion rules:**
- Place new version sections directly below `## [Unreleased]` (or below the header/intro if no Unreleased section exists)
- Maintain reverse chronological order — newest version first
- If new commits are being tagged as a release: clear the `[Unreleased]` bullets and add a fresh empty `[Unreleased]` section above the new version
- If commits are untagged: add bullets to the existing `[Unreleased]` section, merging with any existing bullets there
- Update the version links section at the bottom with new comparison URLs
- **Never modify or delete existing entries** — only append above them

Use ISO date format (`YYYY-MM-DD`). Only include category headings that have entries.

### Step 6: Present the Result

Show only the new section(s) that were added, not the entire file.

## Key Rules

- **Preserve history** — Never modify, rewrite, or delete existing changelog entries.
- **For humans, not machines** — Never dump raw git log. Synthesize into user-facing descriptions.
- **Be specific** — "Fixed crash when uploading large files", not "Bug fixes".
- **Canonical category order** — Added, Changed, Deprecated, Removed, Fixed, Security.
- **Omit empty categories** — Only include headings that have entries.
- **Past tense consistently** — "Added", "Fixed", "Removed".
- **Call out breaking changes** — Prefix with `**BREAKING:**`, describe impact, provide migration path.
- **Deprecate before removing** — Mention the target major version when deprecating.
- **No-op is valid** — If there are no new commits since the last version, say so. Do not fabricate entries.

## Reference Files

- **`../changelog/references/format-guide.md`** — Complete format spec, template, style rules, antipatterns, breaking change handling
