---
name: logbook:messages
description: Analyze messages exchanged per project across all Claude Code sessions. Generates monthly and yearly markdown reports with per-project/branch breakdowns. Use when the user asks about "message count", "messages per project", "how many messages", "message report", "logbook messages", or wants usage statistics.
---

# Logbook — Messages Report

Generate message-count reports from Claude Code session logs. Groups branches under their parent project. Separates human-typed messages from automated user turns (tool results, hooks).

## Workflow

### Step 1: Run the analysis script

```bash
python3 plugins/logbook/scripts/logbook.py messages --out docs/reports
```

This generates:
- One file per calendar month: `YYYYMM-logbook-messages.md`
- One file per year: `YYYY-logbook-messages.md`

To limit to a specific period:
```bash
python3 plugins/logbook/scripts/logbook.py messages --year 2026 --month 3 --out docs/reports
```

For preview only (no files written):
```bash
python3 plugins/logbook/scripts/logbook.py messages --preview
```

### Step 2: Show the preview

After running the script, display the top 10 table from stdout directly to the user. This is the inline preview — do NOT hide it behind a file path.

### Step 3: List generated files

Show the user which report files were created and their paths.

## Report Structure

Each report contains:

1. **Summary** — your messages, agent messages, session count
2. **Top 10 table** — project + you + agent + sessions
3. **Detailed breakdown** — every project with branch-level rows

## Message Types

- **You (human-typed)** — messages where you typed text directly
- **User turns** — all user-role messages including tool results, hooks, automated inputs
- **Agent** — all assistant-role messages

The reports show "You" (human-typed) and "Agent" counts for clarity.
