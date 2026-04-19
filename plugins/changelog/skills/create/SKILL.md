---
name: changelog:create
description: This skill should be used when the user asks to "create a changelog", "initialize CHANGELOG.md", "start a changelog", or when the main changelog skill detects no existing CHANGELOG.md file. Creates a new CHANGELOG.md from scratch by analyzing the full git commit history and organizing changes by date-based version sections.
---

# Create Changelog

Create a new `CHANGELOG.md` from scratch by analyzing the full git history. Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Reasoning Discipline

This task involves multi-step reasoning across many commits: read each commit message, infer the user-facing impact, choose a category, and synthesize related commits into a single bullet. Think carefully through each commit before writing — do not fall back to keyword-only classification or verbatim copying of commit messages.

## Concision Target

Calibrate output to these exact shapes. Do not exceed them.

- **One bullet:** ≤15 words, one sentence, past tense, capitalized first word, ends with a period.
- **One category:** 2–5 bullets. If a category would have >5 bullets, merge related ones until ≤5.
- **One version or date section:** 2–5 populated category headings. Omit any category with zero bullets.
- **Whole output:** a reader should scan one version section in under 30 seconds.

### Preferred bullet examples

> - Added OAuth 2.0 login with Google and GitHub providers.
> - Fixed crash when uploading files larger than 2GB.
> - Reduced dashboard load time by 40%.
> - **BREAKING:** Removed `/api/v1/users`. Migrate to `/api/v2/users`.

### Preferred section example

```markdown
## 2026-03-15

### Added

- OAuth 2.0 login with Google and GitHub providers.
- Dark mode toggle in the settings panel.

### Fixed

- Fixed crash when uploading files larger than 2GB.
- Corrected timezone display in the activity log.
```

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

**Skip merge commits** — Merge commits whose subject starts with `Merge branch ` or `Merge pull request ` duplicate the merged commits. Skip them unconditionally.

**Omit these commit types unless the change is visible to end users of the software (not developers):**

- CI/CD config: files under `.github/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `azure-pipelines.yml`
- Docs-only: `README.md`, `CONTRIBUTING.md`, `docs/**`, inline comments, docstrings
- Lint/format config: `.eslintrc*`, `.prettierrc*`, `.editorconfig`, `.rubocop.yml`, `pyproject.toml` tool sections
- Dependency bumps with no behavior change: dependabot, renovate, `package-lock.json`-only, `Gemfile.lock`-only
- Whitespace-only, typo-only, or comment-only edits
- Test-only additions (`tests/**`, `*_test.go`, `*.spec.ts`) with no corresponding source change

**Keep** commits in the above categories when they ship user-visible behavior — e.g., a CI fix that unblocks a release, a test that fixes a regression users reported, a dependency bump that closes a CVE.

**Prefix priority** — When a conventional commit prefix is present (`feat:`, `fix:`, `refactor:`, `perf:`, `security:`, `deprecate:`, `remove:`, with optional scope like `feat(auth):`), the prefix determines the category. Do not re-infer from the body. Fall back to keyword matching only when no recognized prefix exists.

**Synthesize, do not copy** — Group related commits into single user-facing bullet points describing the end state, not the chronology. Commits are "related" if **any** of these apply:

- Same user-visible feature or capability (e.g., three commits all touching the login flow)
- Same file, directory, or module scope
- Shared conventional-commit scope prefix (e.g., `feat(auth):` then `fix(auth):` then `refactor(auth):`)
- Iterative fixes on the same bug: initial fix commit plus one or more follow-up correction commits

Write one short, specific, past-tense sentence per bullet focused on what the user sees or feels.

### Step 4: Write the File

Consult `../changelog/references/format-guide.md` for the full template and formatting rules.

Build the file with:
1. `# Changelog` header and standard intro paragraph referencing Keep a Changelog and SemVer
2. `## [Unreleased]` section (just the heading, no empty sub-headings)
3. One section per version or date group, in reverse chronological order:
   - **Tagged releases:** `## [X.Y.Z] - YYYY-MM-DD` (use ASCII hyphen, not en-dash)
   - **Date-based groups:** `## YYYY-MM-DD` (start date of the group)
4. Only category headings that have entries (omit empty ones)
5. Reference-style version comparison links at the bottom (for tagged versions; omit for date-based groups)

Use ISO date format (`YYYY-MM-DD`). Detect the remote URL for version links from `git remote get-url origin`.

### Step 5: Present the Result

Show the full generated changelog content inline.

## Key Rules

- **Concision target** — ≤15 words per bullet, 2–5 bullets per category, 2–5 categories per section.
- **Date-based sections are mandatory** — Never produce a single flat list. Every changelog must have multiple dated sections that tell the project's story over time.
- **For humans, not machines** — Write user-facing descriptions (e.g., "Added dark mode toggle"). Do not dump raw git log lines.
- **Be specific** — Write "Fixed crash when uploading large files" rather than "Bug fixes".
- **Canonical category order** — Added, Changed, Deprecated, Removed, Fixed, Security.
- **Omit empty categories** — Only include headings that have entries.
- **Past tense consistently** — "Added", "Fixed", "Removed".
- **Call out breaking changes** — Prefix with `**BREAKING:**`, describe impact, provide migration path.
- **Deprecate before removing** — Mention the target major version when deprecating.
- **ASCII hyphen in version headings** — `## [X.Y.Z] - YYYY-MM-DD`. Never en-dash (`–`) or em-dash (`—`).

## Reference Files

- **`../changelog/references/format-guide.md`** — Complete format spec, template, style rules, antipatterns, breaking change handling
