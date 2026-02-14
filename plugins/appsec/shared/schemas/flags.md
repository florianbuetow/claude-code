# Cross-Cutting Flags Specification

Every appsec skill supports a common set of flags. Parse these from the user's invocation before executing any analysis.

## Scope Flags

Scope determines which files are analyzed. Default: `--scope changed`.

| Flag | Value | Resolves To |
|------|-------|-------------|
| `--scope changed` | git diff HEAD | Changed files in working tree (default) |
| `--scope staged` | git diff --cached | Staged files only |
| `--scope branch` | git diff main...HEAD | All changes on current branch |
| `--scope file:<path>` | Single file | Exact file path |
| `--scope path:<dir>` | Directory tree | All files under directory |
| `--scope module:<name>` | Auto-detect | Module boundaries (package.json dir, go.mod dir, etc.) |
| `--scope full` | Entire codebase | All files in repository |
| `--scope plan` | Plan content | The implementation plan from ExitPlanMode |

### Scope Resolution

1. Parse the `--scope` value from user input.
2. Resolve to a concrete file list using Git or Glob.
3. Filter to relevant file types for the specific skill (e.g., injection skill skips image files).
4. Pass the file list to analysis steps.

If no `--scope` flag is provided and the user mentions specific files or directories, use those as the scope. If truly ambiguous, default to `--scope changed`.

## Depth Flags

Depth determines analysis thoroughness. Default: `--depth standard`.

| Flag | Behavior |
|------|----------|
| `--depth quick` | Scanners only (if available), pattern matching, no deep analysis |
| `--depth standard` | Full code read + analysis for scoped files (default) |
| `--depth deep` | Standard + trace imports, cross-file data flows, call graphs |
| `--depth expert` | Deep + red team agent simulation with DREAD scoring |

### Adaptive Depth

When scope is narrow (single file), automatically increase analysis depth:
- `file:` scope with `--depth standard` behaves like `--depth deep` (trace all paths).
- `full` scope with `--depth standard` uses sampling (entry points, critical paths, config).

## Severity Filter

Report only findings at or above the specified severity. Default: report all.

| Flag | Minimum Severity |
|------|-----------------|
| `--severity critical` | CRITICAL only |
| `--severity high` | CRITICAL + HIGH |
| `--severity medium` | CRITICAL + HIGH + MEDIUM |
| `--severity low` | All findings (default) |

## Output Format

| Flag | Format |
|------|--------|
| `--format text` | Human-readable terminal output (default) |
| `--format json` | Structured JSON matching `findings.md` schema |
| `--format sarif` | SARIF 2.1.0 for GitHub Security tab integration |
| `--format md` | Markdown report suitable for wiki/README |

## Behavioral Flags

| Flag | Effect |
|------|--------|
| `--fix` | After analysis, chain into `/appsec:fix` for each finding |
| `--quiet` | Findings only, suppress explanations and context |
| `--explain` | Add contextual explanations and learning material to each finding |
| `--only A01,A03` | Run specific categories only (framework dispatchers) |
| `--persona all\|insider\|apt\|...` | Select red team personas (requires `--depth expert`) |
| `--skip-redteam` | Skip red team phase even in expert mode |
| `--skip-frameworks <list>` | Skip specific frameworks in full-audit |
| `--output <filename>` | Custom output filename (for report/full-audit) |

## Flag Parsing Rules

1. Flags can appear in any order after the skill name.
2. Unknown flags are ignored with a warning.
3. Conflicting flags: last one wins.
4. Flags are case-insensitive for values (e.g., `--severity HIGH` equals `--severity high`).
5. When invoked as a subagent by a dispatcher, flags are passed in the subagent prompt, not parsed from user input.

## Flag Propagation

When a dispatcher (e.g., `/appsec:owasp`) launches subagent skills:
- `--scope`, `--severity`, `--depth`, `--format` propagate to all subagents.
- `--only` is consumed by the dispatcher to select which subagents to launch.
- `--persona` is consumed by the orchestrator to select red team agents.
- `--fix`, `--quiet`, `--explain` propagate to subagents.
