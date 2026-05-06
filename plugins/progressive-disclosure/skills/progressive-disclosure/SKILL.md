---
name: progressive-disclosure
description: This skill should be used when the user asks to "analyze documentation structure", "audit progressive disclosure", "restructure CLAUDE.md", "restructure AGENTS.md", "create a documentation index", "organize project docs", "find orphaned docs", "map documentation references", "improve context loading", or mentions progressive disclosure, documentation hierarchy, soul file organization, or context rot prevention. Analyzes or restructures how a repository discloses documentation through root configuration files.
disable-model-invocation: false
---

# Progressive Disclosure

Analyze and restructure how a repository progressively discloses its documentation through soul files (AGENTS.md, CLAUDE.md, GEMINI.md, COPILOT.md). Maps reference graphs, detects orphaned documents, and generates thematic book-style indexes to prevent context rot.

## Routing

This skill auto-selects the correct workflow based on user intent.

### Step 1: Determine Mode

- **User asks to analyze, audit, map, or assess** — Route to `progressive-disclosure:analyze`
- **User asks to restructure, refactor, index, or organize** — Route to `progressive-disclosure:restructure`
- **No explicit mode specified** — Default to `progressive-disclosure:analyze`

### Step 2: Invoke

Invoke the appropriate subskill. Do not duplicate their logic here.
