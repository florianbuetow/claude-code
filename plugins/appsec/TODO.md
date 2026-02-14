# AppSec Plugin — Development Guide

## What This Is

A Claude Code plugin called `appsec` that provides comprehensive application security analysis.

**Read these files first (in order):**
1. `IDEA.md` — Full design document. 50+ tools, 6 frameworks, 6 red team personas, scoping system, depth modes, DREAD scoring, education tools. This is the spec.
2. `RESEARCH.md` — Supporting research on frameworks (PASTA, LINDDUN, VAST, MITRE ATT&CK, DREAD, OCTAVE, Trike), red team roles (8 specializations with agent prompts), scanner inventory (25+ tools with integration notes), AI-powered security approaches, and compliance frameworks (NIST CSF, CIS, ISO 27001, SOC2, PCI-DSS, HIPAA, GDPR) with code-level automatable checks and cross-compliance mapping tables. Contains concrete implementation ideas for each.
3. `shared/frameworks/` — Reference docs for OWASP Top 10 2021 and STRIDE that can be included in skill prompts.

## Plugin Name

`appsec` — all commands use the prefix `/appsec:` (e.g., `/appsec:run`, `/appsec:owasp`).

## Directory Structure

```
appsec/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest (done)
├── skills/                      # One subdirectory per skill, each with SKILL.md
│   ├── run/SKILL.md             # Smart orchestrator
│   ├── status/SKILL.md          # Dashboard
│   ├── config/SKILL.md          # Preferences
│   ├── owasp/SKILL.md           # OWASP Top 10 framework dispatcher
│   ├── stride/SKILL.md          # STRIDE framework dispatcher
│   ├── access-control/SKILL.md  # A01
│   ├── crypto/SKILL.md          # A02
│   ├── injection/SKILL.md       # A03
│   ├── ... (see IDEA.md for full list)
│   ├── explain/SKILL.md         # Interactive explainer
│   ├── learn/SKILL.md           # Guided walkthrough
│   └── glossary/SKILL.md        # Quick reference
├── agents/                      # Red team and consolidator agents
│   ├── script-kiddie.md
│   ├── hacktivist.md
│   ├── insider.md
│   ├── organized-crime.md
│   ├── supply-chain.md
│   ├── nation-state.md
│   └── consolidator.md
├── hooks/
│   └── hooks.json               # PostToolUse on ExitPlanMode
├── shared/
│   ├── frameworks/              # Reference docs for OWASP, STRIDE, PASTA, etc.
│   └── schemas/                 # JSON schemas for findings, state files
├── IDEA.md                      # Full design document (50 tools)
├── RESEARCH.md                  # Supporting research on frameworks, tools, personas
└── CLAUDE.md                    # This file
```

## Implementation Order

Build in this order. Each phase should be testable via `claude --plugin-dir`.

### Phase 1: Core (MVP)

These are the minimum tools needed for a working plugin:

1. **`/appsec:start`** — The entry point. Assess codebase (tech stack, data sensitivity, architecture patterns, installed scanners) and recommend which tools to use, in what order, with rationale. This is the first thing a new user runs.

2. **`/appsec:status`** — Show scanner detection, findings count, top priorities. Simple and verifies the plugin loads correctly.

3. **`/appsec:run`** — The smart orchestrator. For MVP: detect installed scanners, run them on scoped files, have Claude triage results. Support `--scope` and `--depth quick|standard`.

4. **`/appsec:secrets`** — Secret detection. Run gitleaks/trufflehog if available, Claude fallback with grep patterns. Check git history, .gitignore, .env files.

5. **`/appsec:review-plan`** — The flagship. Analyze the plan from ExitPlanMode for security gaps. This is what makes the plugin unique.

6. **`hooks/hooks.json`** — PostToolUse on ExitPlanMode to trigger review-plan via subagent.

7. **`/appsec:explain`** — Explain any framework, category, or finding interactively.

### Phase 2: OWASP + STRIDE Individual Tools

8. Create the 10 OWASP individual tools (access-control through ssrf). Each is a focused skill that:
   - Accepts `--scope` to determine what files to analyze
   - Runs relevant scanners if available
   - Has Claude analyze code for that specific concern
   - Returns structured findings JSON

9. Create the `/appsec:owasp` framework dispatcher that launches relevant OWASP tools as parallel subagents via the Task tool.

10. Create the 6 STRIDE individual tools (spoofing through privilege-escalation).

11. Create the `/appsec:stride` dispatcher.

### Phase 3: Red Team Agents

12. Create the 6 red team agent `.md` files in `agents/`. Each agent gets:
    - A specific attacker persona with skill level, motivation, resources
    - Instructions on what to look for
    - DREAD scoring instructions
    - Structured output format

13. Create the consolidator agent that merges red team findings.

14. Wire `--depth expert` in `/appsec:run` to spawn red team agents after analysis.

### Phase 4: Additional Frameworks

15. PASTA (7 stage tools)
16. LINDDUN (7 privacy tools)
17. MITRE ATT&CK mapping
18. SANS/CWE Top 25

### Phase 5: Guide Tools + Full Audit

19. `/appsec:fix` — Generate actual code fixes for findings
20. `/appsec:harden` — Proactive hardening suggestions
21. `/appsec:verify` — Confirm fixes resolved findings
22. `/appsec:report` — Generate reports (md, html, json, sarif)
23. **`/appsec:full-audit`** — Exhaustive audit that launches every framework, every tool, and every red team agent. Writes a dated report (`<YYYYMMDD>_appsec_report.md`) with each agent's raw output as its own section (no consolidation), then appends an executive summary and prepends an introduction with project details and tools used. Depends on most other tools being implemented first.

### Phase 6: Specialized Tools

24. `/appsec:race-conditions` — TOCTOU, double-spend, concurrent request exploitation
25. `/appsec:file-upload` — File upload attack surface analysis
26. `/appsec:graphql` — GraphQL-specific vulnerabilities
27. `/appsec:websocket` — WebSocket security analysis
28. `/appsec:serverless` — Serverless function security
29. `/appsec:regression` — Verify previously fixed vulnerabilities stay fixed
30. `/appsec:api` — OWASP API Security Top 10
31. `/appsec:business-logic` — Business logic flaws
32. `/appsec:fuzz` — Generate intelligent fuzz test inputs

### Phase 7: Education

33. `/appsec:learn` — Interactive walkthroughs
34. `/appsec:glossary` — Quick reference

## Key Design Decisions

### Every skill must support these flags

```
--scope changed|staged|branch|file:<path>|path:<dir>|full
--severity critical|high|medium|low
--depth quick|standard|deep|expert
--format text|json|sarif|md
--fix
--quiet
--explain
--only A01,A03 (framework tools)
--persona all|insider|apt|... (expert mode)
```

Implement scope first — it's the most important. Default is `--scope changed`.

### Subagent pattern for framework dispatchers

Framework tools (owasp, stride, linddun) should use the Task tool to launch individual category skills as parallel subagents. Example pattern for `/appsec:owasp`:

```
1. Pre-flight: Read file list in scope, detect which categories are relevant
2. For each relevant category: spawn a Task subagent running that skill
3. Collect all results
4. Consolidate: deduplicate, cross-reference, rank by severity
5. If --depth expert: spawn red team agents with the findings
6. Return consolidated output
```

### Skill YAML frontmatter

Each SKILL.md needs:
```yaml
---
name: skill-name
description: One-line description for auto-discovery triggering
allowed-tools: Read, Glob, Grep, Bash(semgrep:*), Bash(gitleaks:*), ...
---
```

The `description` field is critical — it determines when Claude auto-activates the skill. Write it to match the commands in IDEA.md.

### Scanner integration

Every tool that runs scanners should:
1. Check if the scanner binary exists on PATH
2. If yes: run it with appropriate flags, capture output
3. If no: fall back to Claude analysis with Grep/Read, and note "no scanner available"
4. Never pretend Claude analysis equals a real scanner

### Findings format

All tools should output findings in this structure:
```json
{
  "tool": "injection",
  "framework": "owasp",
  "category": "A03",
  "scope": "changed",
  "scanners_used": ["semgrep"],
  "findings": [
    {
      "id": "INJ-001",
      "title": "SQL injection in user lookup",
      "severity": "critical",
      "location": "src/db/queries.ts:45",
      "description": "...",
      "fix": "Use parameterized query",
      "cwe": "CWE-89",
      "owasp": "A03",
      "stride": "T",
      "mitre": "T1190",
      "dread": { "D": 9, "R": 8, "E": 7, "A": 8, "D2": 6, "score": 7.6 }
    }
  ]
}
```

### State directory

Tools should write findings to `.appsec/` (not `.threatmodel/`):
```
.appsec/
├── config.yaml
├── findings/
│   ├── by-tool/
│   ├── aggregate.json
│   ├── accepted.json
│   └── fixed-history.json
├── model/
│   ├── components.json
│   ├── data-flows.json
│   └── diagrams/
├── reports/
│   ├── latest.md
│   └── <YYYYMMDD>_appsec_report.md   # from /appsec:full-audit
└── scanners/
    └── detected.json
```

## Reference Plugins

Look at these existing plugins in the same directory for patterns:
- `solid-principles/` — Simple skill-only plugin, good reference for SKILL.md format
- `beyond-solid-principles/` — Similar structure
- `explain-system-tradeoffs/` — Another skill-only plugin
- `spec-writer/` — Multi-skill plugin

## Testing

Test with: `claude --plugin-dir /Users/flo/Developer/github/claude-code/plugins/appsec`

Verify:
1. `/appsec:status` loads and responds
2. Skills appear in the skill list
3. Hook fires after ExitPlanMode
4. Subagent dispatch works for framework tools
