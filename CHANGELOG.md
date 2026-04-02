# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added 5 new agent-guardrails rules: no-echo-back, no-robotic-comments, no-over-explaining (Stop), no-blind-edit (PreToolUse/Edit + PostToolUse/Read), and no-destructive-bash (PreToolUse/Bash) — introducing PreToolUse and PostToolUse hook support (v3.0.0).
- Added Quickstart section to README with one-command installation for all plugins.
- Added fixclaude plugin (v0.1.0) with 4 skills for overriding Claude Code's built-in limitations discovered in the source code leak: install (auto-detect router), init (create new CLAUDE.md), update (augment existing), and analyze (gap analysis against 7 findings). Based on fakeguru's claude-md (MIT).

### Fixed

- Synced no-preference-asking stop hook patterns with rule file — 18 patterns from v2.1.4 (let me know, does this look right, sound good, your call, up to you, anything else, etc.) were defined in the rule but never added to the hook template (v3.0.2).
- Fixed incorrect "no restart needed" claim in agent-guardrails install skill — hook registration in settings.local.json requires a session restart (v3.0.1).

### Changed

- Expanded no-false-completion and no-dismissing guardrail patterns in agent-guardrails (v3.0.0).
- Registered fixclaude plugin in marketplace manifest.
- Consolidated README installation docs into Quickstart section with alphabetically sorted plugin list.
- Condensed README subtitle into single line.
- Expanded no-preference-asking guardrail with 6 new pattern families: seeking-approval, "let me know", "anything else", "your call/up to you", "what would you like to", and "or do you/should we" alternatives — catching ~350 additional low-legit questions identified from 850-session analysis (v2.1.4).
- Added `want me to...?` and `should I...?` patterns to no-preference-asking guardrail (v2.1.3).
- Improved no-preference-asking guardrail prompt for fewer false positives (v2.1.1).
- Used `$CLAUDE_PROJECT_DIR` variable for hook command path instead of relative `bash` invocation in agent-guardrails install skill (v2.1.2).

### Fixed

- Fixed literal `\n\n` appearing in stop hook output instead of actual newlines in agent-guardrails (v2.1.3).
- Added infinite loop prevention guard to stop-guardrails hook to avoid re-triggering when `stop_hook_active` is already set (v2.1.2).

### Added

- Added no-dismissing rule to agent-guardrails plugin (v2.1.0).
- Added plugin.json manifest for agent-guardrails plugin.
- Added agent-guardrails plugin with five behavioral guardrail rules for blocking AI anti-patterns (speculative language, stalling, preference-asking, false completion, skipping).
- Added Codex (OpenAI) installation instructions to README — skills CLI, clone-and-copy, and symlink methods.
- Added changelog plugin for generating and maintaining changelogs from git history.
- Added logbook plugin for tracking time and messages across Claude Code sessions.
- Added cache-money plugin for Anthropic prompt cache optimization and TTL-aware ping intervals.
- Added iso27001-sdlc plugin with secure coding scanner for ISO 27001:2022 compliance auditing.
- Added onboarding plugin for project orientation and context gathering at session start.
- Added retrospective plugin for AI-assisted session reviews with structured recommendations.
- Added K.I.S.S. plugin for detecting simplification opportunities and unnecessary complexity.
- Added archibald plugin for software architecture quality assessment (coupling, cohesion, complexity).
- Added spec-dd plugin for specification-driven development with behavioral specs and test derivation.
- Added appsec plugin with 61 security skills, 7 agents, and hooks for application security auditing.
- Added explain-system-tradeoffs plugin for distributed system tradeoff analysis (CAP, PACELC, etc.).
- Added beyond-solid-principles plugin for system-level architecture principle checking.
- Added spec-writer plugin for creating layered software specification documents.
- Added MIT LICENSE to root and all plugins.
- Added CLAUDE.md with bd (beads) issue tracking workflow instructions.

### Changed

- Replaced hookify dependency with self-contained bash Stop hook in agent-guardrails (v2.0.0).
- Removed hooks section from README - hooks are an implementation detail of plugins.
- Replaced unicode em dashes with ASCII hyphens in README.
- Deduplicated regex patterns in agent-guardrails: analyze, install, and update skills now read from `rules/` files as single source of truth.
- Consolidated hookify hook rules from top-level `hooks/` directory into agent-guardrails plugin as single source of truth.
- Cleaned up README: deduplicated hooks section, fixed skill count, updated paths.
- Updated cache-money with TTL-adaptive ping intervals and accurate cost documentation (1.1.0).
- Updated spec-dd with `/spec-dd:verify` subcommand for implementation alignment review (1.1.0).
- Updated iso27001-sdlc with major secure coding scanner rewrite (1.0.0).
- Restructured retrospective output to lead with recommendations and use session-scoped temp directories (1.4.0).
- Rewrote appsec `run` and `full-audit` skills for file-based output pipeline.
- Updated SANS/CWE Top 25 reference from 2023 to 2024 edition in appsec plugin.
- Renamed marketplace from reserved name to florianbuetow-plugins.

### Fixed

- Fixed `tools` frontmatter format in all 7 appsec agent files from comma-separated string to proper YAML array, ensuring tool restrictions are enforced.
- Fixed 5 plugins (cache-money, changelog, logbook, onboarding, agent-guardrails) claiming MIT license without including a LICENSE file.
- Fixed "let me first check" false positive in agent-guardrails no-stalling rule pattern.
- Fixed stale `hooks/` path reference in agent-guardrails update skill.
- Fixed Codex installation instructions to install whole plugin directories instead of individual skills.
- Fixed appsec hooks.json schema to wrap PostToolUse in required hooks object.
- Fixed stale 2023 CWE references in appsec SANS Top 25 category tables.
- Fixed 23 documentation inconsistencies found during appsec PR review.
- Fixed retrospective plugin enforcing script-only execution for all subagents.
- Fixed installation instructions to use correct plugin CLI commands.

[Unreleased]: https://github.com/florianbuetow/claude-code/compare/045d39e...HEAD
