---
name: onboarding
description: This skill should be used when starting a new session, resuming work, or when the user asks to "onboard", "get oriented", "catch me up", "what's the state of the project", "what should I work on", or "where did we leave off". Gathers project context by reading instructions, checking git state, reviewing open issues, and identifying next steps.
---

# Project Onboarding

Orient in the current project by gathering context from multiple sources: project instructions, version control state, issue tracker, and build system. Produce a concise status briefing and suggest what to tackle next.

## Workflow

Execute all steps below. Run independent steps in parallel where possible.

### Step 1: Read Project Instructions (MANDATORY)

You MUST read `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and `COPILOT.md` in the project root. Skip any that don't exist, but read all that do. If a file explicitly instructs you to read another file, read that file too. If both files contain the same content (e.g., one simply redirects to the other), only read it once. When both files exist and their rules conflict, `AGENTS.md` takes precedence.

Extract from these files:
- Tech stack and language versions
- Project conventions and rules
- Directory structure
- What tools and validators are used

Follow the instructions and rules found in these files during this session.

### Step 2: Gather State (run in parallel)

Execute these four checks concurrently:

**2a. Git Status**
Run `git status` to identify:
- Current branch
- Uncommitted changes (staged and unstaged)
- Untracked files
- Whether the branch is ahead/behind remote

**2b. Recent Git History**
Run `git log --oneline --date=short --format="%h %ad %s" -15` to see:
- What was worked on recently
- When the last commits were made
- Whether there are work-in-progress commits

**2c. Open Issues**
Run `bd ready` to list issues with no blockers that are ready to work on.
Also run `bd list --status=in_progress` to check for any claimed but unfinished work.

If beads is not initialized (command fails), skip this step and note that no issue tracker is configured.

**2d. Build System**
Read the project's `justfile` (or `Makefile` if no justfile exists) to identify:
- How to run tests (`just test`, `just ci`, etc.)
- How to run the project (`just run`)
- Available quality gates and CI recipes
- Any project-specific commands

### Step 3: Synthesize and Brief

Present a concise status briefing covering:

1. **Project** — What this project is, tech stack, key conventions
2. **Current state** — Branch, uncommitted work, last activity date
3. **Recent activity** — Summary of recent commits (not a raw log dump)
4. **Open work** — Ready issues and any in-progress items
5. **Build commands** — How to run tests and CI
6. **Suggested next steps** — Based on open issues, uncommitted work, or recent activity, suggest what to tackle

### Presentation Rules

- Keep the briefing concise — one short paragraph per section, not walls of text
- Lead with what matters: uncommitted work and in-progress issues take priority
- If there is uncommitted work or in-progress issues, call that out prominently
- Do not dump raw command output — synthesize it into human-readable summaries
- End with a clear question: "What would you like to work on?"
