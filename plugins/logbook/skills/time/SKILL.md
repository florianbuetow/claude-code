---
name: logbook:time
description: Analyze time spent per project across all Claude Code sessions. Generates monthly and yearly markdown reports with per-project/branch breakdowns. Use when the user asks about "time spent", "hours per project", "session time", "time report", "logbook time", or wants to know how long they spent coding.
---

# Logbook — Time Report

Generate time-per-project reports from Claude Code session logs. Groups branches under their parent project. Excludes idle gaps > 15 minutes.

## Workflow

### Step 1: Run the analysis script

The script lives at the plugin path. Find it relative to this skill:

```bash
SCRIPT="$(dirname "$(dirname "$(dirname "$0")")")/scripts/logbook.py"
```

But in practice, run it from the project root:

```bash
python3 plugins/logbook/scripts/logbook.py time --out docs/reports
```

This generates:
- One file per calendar month: `YYYYMM-logbook-time.md`
- One file per year: `YYYY-logbook-time.md`

To limit to a specific period:
```bash
python3 plugins/logbook/scripts/logbook.py time --year 2026 --month 3 --out docs/reports
```

For preview only (no files written):
```bash
python3 plugins/logbook/scripts/logbook.py time --preview
```

### Step 2: Show the preview

After running the script, display the top 10 table from stdout directly to the user. This is the inline preview — do NOT hide it behind a file path.

### Step 3: List generated files

Show the user which report files were created and their paths.

## Report Structure

Each report contains:

1. **Summary** — total active time, project count, session count
2. **Top 10 table** — project name + time
3. **Detailed breakdown** — every project with branch-level rows showing time and session counts

## Notes

- Gaps > 15 minutes between messages are excluded (configurable in script as `GAP_THRESHOLD`)
- Branches are detected from git worktree patterns (`-git-<branch>`, `--claude-worktrees-<branch>`)
- Excluded projects are configured in the `EXCLUDED` list in the script
