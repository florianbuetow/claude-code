---
name: changelog:update
description: This skill should be used when the user asks to "update the changelog", "add to the changelog", "changelog for new release", "update CHANGELOG.md", or when the main changelog skill detects an existing CHANGELOG.md file. Appends new version entries by analyzing commits since the last documented version.
---

# Update Changelog

Update an existing `CHANGELOG.md` with new entries by analyzing commits since the last documented version. Follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Reasoning Discipline

This task involves multi-step reasoning across many commits: read each commit message, infer the user-facing impact, choose a category, and synthesize related commits into a single bullet. Think carefully through each commit before writing — do not fall back to keyword-only classification or verbatim copying of commit messages.

## Concision Target

Calibrate output to these exact shapes. Do not exceed them.

- **One bullet:** ≤15 words, one sentence, past tense, capitalized first word, ends with a period.
- **One category:** 2–5 bullets. If a category would have >5 bullets, merge related ones until ≤5.
- **One version section:** 2–5 populated category headings. Omit any category with zero bullets.
- **Whole output:** a reader should scan the new section in under 30 seconds.

### Preferred bullet examples

> - Added OAuth 2.0 login with Google and GitHub providers.
> - Fixed crash when uploading files larger than 2GB.
> - Reduced dashboard load time by 40%.
> - **BREAKING:** Removed `/api/v1/users`. Migrate to `/api/v2/users`.

### Preferred new-version section example

```markdown
## [1.3.0] - 2026-04-19

### Added

- OAuth 2.0 login with Google and GitHub providers.

### Fixed

- Fixed crash when uploading files larger than 2GB.
```

## Workflow

### Step 1: Read Existing Changelog

Read `CHANGELOG.md` from the project root (case-insensitive: also check `changelog.md`, `Changelog.md`).

Parse to determine:
- **Latest documented version** — The most recent `## [X.Y.Z]` heading that is **not** marked `[YANKED]`. A yanked version is not a valid boundary because its release was withdrawn; skip it and use the next non-yanked version above it.
- **Any `[YANKED]` markers present?** — Record their positions so you preserve them untouched.
- **Has `[Unreleased]` section?** — Note its position and any existing bullets.
- **Has version links section?** — Note its position at the bottom.

### Step 2: Find the Boundary Commit

The boundary commit is the last commit already documented in the changelog. Everything after it is new.

**Strategy (try in order until one succeeds):**

1. **Tag match** — If the latest documented version (e.g., `1.2.0`) has a corresponding git tag (`v1.2.0` or `1.2.0`), use that tag as the boundary: `git log <tag>..HEAD`.
2. **Date match** — If no tag matches, use the release date from the version heading (`## [1.2.0] - 2026-03-15`) and find commits after that date: `git log --after="2026-03-15"`.
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

### Step 5: Insert New Entries

Consult `../changelog/references/format-guide.md` for formatting rules.

**Insertion rules:**
- Place new version sections directly below `## [Unreleased]` (or below the header/intro if no Unreleased section exists)
- Maintain reverse chronological order — newest version first
- If new commits are being tagged as a release: clear the `[Unreleased]` bullets and add a fresh empty `[Unreleased]` section above the new version
- If commits are untagged: add bullets to the existing `[Unreleased]` section, merging with any existing bullets there
- Update the version links section at the bottom with new comparison URLs
- Use ASCII hyphen (`-`) between version and date: `## [X.Y.Z] - YYYY-MM-DD`. Never en-dash (`–`) or em-dash (`—`).
- **Preserve `[YANKED]` markers**: if an existing heading reads `## [X.Y.Z] - YYYY-MM-DD [YANKED]`, keep the `[YANKED]` tag and the yanked section body untouched.
- **Never modify or delete existing entries** — only append above them

Use ISO date format (`YYYY-MM-DD`). Only include category headings that have entries.

### Step 6: Present the Result

Show only the new section(s) that were added, not the entire file.

## Key Rules

- **Concision target** — ≤15 words per bullet, 2–5 bullets per category, 2–5 categories per section.
- **Preserve history** — Never modify, rewrite, or delete existing changelog entries.
- **Preserve `[YANKED]`** — Keep yanked version headings and bodies exactly as they are. A yanked release is not a valid boundary commit; use the newest non-yanked version instead.
- **For humans, not machines** — Write user-facing descriptions (e.g., "Added dark mode toggle"). Do not dump raw git log lines.
- **Be specific** — Write "Fixed crash when uploading large files" rather than "Bug fixes".
- **Canonical category order** — Added, Changed, Deprecated, Removed, Fixed, Security.
- **Omit empty categories** — Only include headings that have entries.
- **Past tense consistently** — "Added", "Fixed", "Removed".
- **Call out breaking changes** — Prefix with `**BREAKING:**`, describe impact, provide migration path.
- **Deprecate before removing** — Mention the target major version when deprecating.
- **No-op is valid** — If there are no new commits since the last version, say so. Do not fabricate entries.
- **ASCII hyphen in version headings** — `## [X.Y.Z] - YYYY-MM-DD`. Never en-dash (`–`) or em-dash (`—`).

## Reference Files

- **`../changelog/references/format-guide.md`** — Complete format spec, template, style rules, antipatterns, breaking change handling
