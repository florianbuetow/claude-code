# AppSec File-Based Output Pipeline

## Problem

The appsec orchestrator skills (`/appsec:run`, `/appsec:full-audit`) hit context window limits because all subagent results return verbatim to the main agent's context. With 4 scanner JSON outputs + 7+ subagent analysis results, the main context overflows before consolidation can begin.

Observed: `/appsec:run` on a small Python/FastAPI project launched 4 scanners + 7 subagents. Context limit reached before the orchestrator could consolidate any findings.

## Root Cause

Subagent results (5-30KB each) all return to the main orchestrator's context window simultaneously. Scanner JSON output (10-50KB each) also accumulates in context. Combined: 120-400KB of results in a single context window.

## Solution

File-based output pipeline: subagents write findings to files and return only a one-line status. A consolidator subagent reads all files to produce the final report.

### Output Directory

```
reports/appsec/
  ├── scanners/           # Raw scanner JSON output
  │   ├── semgrep.json
  │   ├── bandit.json
  │   └── ...
  ├── skills/             # Skill findings in schema format
  │   ├── injection.json
  │   ├── secrets.json
  │   └── ...
  ├── redteam/            # Red team agent findings
  │   ├── script-kiddie.json
  │   ├── insider.json
  │   └── ...
  ├── findings.json       # Consolidated, deduped, ranked
  └── <YYYYMMDD>_report.md  # Full-audit report (when applicable)
```

### Phase Changes for `/appsec:run`

**Phase 2 (Scanners)**: Redirect output to files. Main agent checks exit code + file existence, never reads JSON content.
```bash
mkdir -p reports/appsec/scanners
semgrep scan --config auto --json --quiet <scope> > reports/appsec/scanners/semgrep.json 2>&1
```

**Phase 3 (Subagents)**: New prompt template instructs subagents to write to files and return one-liner.
```
STEP 4: Write findings as JSON (aggregate output format from findings schema) to:
  reports/appsec/skills/{TOOL_NAME}.json
Use the Write tool to create the file.

STEP 5: Return ONLY a one-line status in this exact format:
  "{TOOL_NAME}: {N} findings ({critical}C {high}H {medium}M {low}L)"

IMPORTANT: Do NOT return findings in your response text. Write them to the file only.
The orchestrator will use a separate consolidation agent to read the files.
```

**Phase 4 (Red team)**: Same pattern, writes to `reports/appsec/redteam/{persona}.json`.

**Phase 5 (Consolidation)**: Replace in-context consolidation with a consolidator subagent:
- Reads all JSON files from `reports/appsec/scanners/`, `skills/`, `redteam/`
- Deduplicates (same file:line → keep higher severity)
- Cross-references (CWE, OWASP, STRIDE, MITRE mappings)
- Ranks (critical > high > medium > low, then confidence)
- Writes `reports/appsec/findings.json`
- Returns formatted summary report to main agent

### Phase Changes for `/appsec:full-audit`

Same file-based pattern. Additionally, the report assembler subagent reads all files to produce the dated markdown report at `reports/appsec/<YYYYMMDD>_report.md`.

### Context Budget

| Phase | Before | After |
|-------|--------|-------|
| Scanner results in main | ~50-200KB JSON | ~200 bytes (exit codes) |
| 7 subagent results in main | ~70-210KB | ~700 bytes (one-liners) |
| Consolidation | In main context (overflows) | Isolated subagent |
| **Main agent total** | **~120-400KB** | **~2KB + final report** |

### Files to Modify

| File | Change |
|------|--------|
| `skills/run/SKILL.md` | Scanner redirect, new subagent prompt template, consolidator step |
| `skills/full-audit/SKILL.md` | Same pattern, report assembler writes to `reports/appsec/` |

### Files NOT Changed

- Individual skill SKILL.md files (subagent prompt tells them where to write)
- Agent persona files (red team prompt tells them where to write)
- Shared schemas (findings.md, flags.md, scanners.md)
- Hooks
- Plugin manifest

### Edge Cases

- **Subagent fails to write file**: Consolidator detects missing file, reports gap
- **Malformed JSON in file**: Consolidator logs error, skips file, reports in TOOLS DEGRADED
- **Empty findings**: Subagent still writes `{"findings": [], "total_findings": 0}` to file
- **Directory doesn't exist**: Subagent prompt includes `mkdir -p` step
- **Concurrent runs**: Each run overwrites previous results (acceptable; add timestamp subdirs later if needed)
- **gitignore**: Add `reports/appsec/` to `.gitignore` (transient scan results)
