---
name: status
description: >
  This skill should be used when the user asks for "security status",
  "show findings", "security dashboard", "security posture", or invokes
  /appsec:status. Shows current security posture overview.
---

# AppSec Status -- Security Dashboard

Read the `.appsec/` state directory and present a concise security posture
dashboard. Shows what has been scanned, what was found, what has changed
since the last scan, and what to do next.

This skill runs entirely in the main agent context. It does NOT dispatch
subagents. It reads state files produced by `/appsec:run` and
`/appsec:full-audit`.

## Supported Flags

| Flag | Behavior |
|------|----------|
| `--format text` | ASCII dashboard (default). |
| `--format json` | Structured JSON summary. |
| `--format md` | Markdown summary. |
| `--quiet` | Findings count only, no details. |

## State Files

Read these files from the `.appsec/` directory:

| File | Content | Required |
|------|---------|----------|
| `.appsec/findings.json` | Consolidated findings from last run | Yes |
| `.appsec/last-run.json` | Timestamp, scope, depth, tools used | Yes |
| `.appsec/start-assessment.json` | Stack detection, scanner availability | Optional |
| `.appsec/config.yaml` | User preferences (from `/appsec:config`) | Optional |

## Workflow

### Step 1: Check State Exists

Use Glob to check for `.appsec/findings.json` and `.appsec/last-run.json`.

If NO state files exist, output:

```
=====================================================
         APPSEC STATUS -- No Data
=====================================================

No security scan data found. Run a scan first:

  /appsec:start       Assess project and get recommendations
  /appsec:run          Run smart security scan
  /appsec:full-audit   Exhaustive audit with report

=====================================================
```

### Step 2: Load State

Read `.appsec/findings.json` and `.appsec/last-run.json`. Optionally read
`.appsec/start-assessment.json` and `.appsec/config.yaml` if they exist.

### Step 3: Detect Changes Since Last Scan

Run `git diff --name-only` against the timestamp in `last-run.json` to
determine which files have changed since the last scan. Classify changes:

- **Modified files with findings**: existing findings may be resolved or new
  issues introduced.
- **New files**: not yet scanned.
- **Deleted files**: findings for these files are now stale.

Count the changed files and note the high-risk ones (files that had
findings in the last scan).

### Step 4: Compute Summary Statistics

From the findings data, compute:

- Total findings by severity (critical, high, medium, low).
- Findings by framework (OWASP, STRIDE, PASTA, LINDDUN, etc.).
- Findings by tool (secrets, injection, access-control, etc.).
- Top 5 files by finding count.
- Scanner coverage (which scanners ran, which are missing).
- Stale findings (in files that have been modified since the scan).

### Step 5: Output Dashboard

#### Text Format (default)

```
=====================================================
            APPSEC STATUS -- Dashboard
=====================================================

LAST SCAN: <timestamp> (<relative time, e.g., "2 hours ago">)
SCOPE:     <scope from last run>
DEPTH:     <depth from last run>

FINDINGS:
  +-------+----------+------+--------+-----+-------+
  |       | Critical | High | Medium | Low | Total |
  +-------+----------+------+--------+-----+-------+
  | Count |    N     |  N   |   N    |  N  |   N   |
  +-------+----------+------+--------+-----+-------+

TOP PRIORITIES:
  1. <ID>  <severity>  <title>  (<file>:<line>)
  2. <ID>  <severity>  <title>  (<file>:<line>)
  3. <ID>  <severity>  <title>  (<file>:<line>)
  4. <ID>  <severity>  <title>  (<file>:<line>)
  5. <ID>  <severity>  <title>  (<file>:<line>)

CHANGES SINCE LAST SCAN:
  Files modified:  N
  New files:       N
  Files with existing findings modified:  N
  Stale findings (file changed):          N

SCANNER STATUS:
  <scanner>  installed  <N findings>
  <scanner>  installed  <N findings>
  <scanner>  missing    (would cover: <categories>)

FRAMEWORKS RUN:
  OWASP Top 10    <N findings>
  STRIDE          <N findings>
  PASTA           <N findings>   (or "not run")
  LINDDUN         <N findings>   (or "not run")
  SANS/CWE 25     <N findings>   (or "not run")

HOTSPOT FILES:
  <file>  <N findings>  (<severities>)
  <file>  <N findings>  (<severities>)
  <file>  <N findings>  (<severities>)

=====================================================
  /appsec:run                 Re-scan (detects changes)
  /appsec:explain <ID>        Explain a finding
  /appsec:run --scope changed Scan only changed files
=====================================================
```

#### JSON Format

```json
{
  "last_scan": {
    "timestamp": "2026-02-14T10:30:00Z",
    "scope": "full",
    "depth": "standard",
    "tools_used": ["secrets", "injection", "access-control"]
  },
  "findings": {
    "total": 12,
    "by_severity": { "critical": 1, "high": 3, "medium": 5, "low": 3 },
    "by_framework": { "owasp": 8, "stride": 3, "secrets": 1 },
    "top_priorities": [
      { "id": "INJ-001", "severity": "critical", "title": "...", "file": "..." }
    ]
  },
  "changes_since_scan": {
    "modified_files": 5,
    "new_files": 2,
    "files_with_findings_modified": 1,
    "stale_findings": 3
  },
  "scanners": {
    "semgrep": { "installed": true, "findings": 4 },
    "gitleaks": { "installed": false }
  }
}
```

## Important Rules

- Do NOT invent findings or statistics. Only report what is in the state
  files.
- Do NOT fabricate compliance scores or percentages. There is no meaningful
  way to express security posture as a single percentage.
- Do NOT claim the codebase is "secure" or "insecure" based on finding
  count alone. Zero findings from a narrow scan does not mean secure.
- If the last scan used `--scope changed` on 3 files, note that coverage
  is limited.
- If the state data is more than 7 days old, flag it prominently as stale.
