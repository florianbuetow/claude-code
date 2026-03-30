---
name: changelog
description: This skill should be used when the user asks to "update the changelog", "generate a changelog", "create CHANGELOG.md", "write release notes", "update CHANGELOG", "add changelog entry", "changelog from commits", or mentions changelog generation, release documentation, or keeping a changelog up to date. Auto-detects whether to create or update based on file existence. Follows Keep a Changelog format with Semantic Versioning.
---

# Changelog

Generate or maintain a `CHANGELOG.md` file from git commit history following [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Routing

This skill auto-selects the correct workflow based on whether a changelog already exists.

### Step 1: Detect Existing Changelog

Check for `CHANGELOG.md` in the project root (case-insensitive: also check `changelog.md`, `Changelog.md`).

### Step 2: Route

- **File exists** — Follow the `changelog:update` workflow.
- **No file** — Follow the `changelog:create` workflow.

Invoke the appropriate subskill. Do not duplicate their logic here.
