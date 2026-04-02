---
name: agent-guardrails-install
description: Install agent behavioral guardrail rules into a project's .claude/ directory. Generates hook scripts (Stop, PreToolUse, PostToolUse) and configures settings.local.json. Includes eleven rules across three hook types. Use when user asks to "install guardrails", "set up agent guardrails", "add behavioral hooks", "agent-guardrails install", or wants to enforce assistant discipline.
---

# Agent Guardrails Install

Install agent behavioral guardrail rules into the current project. Generates bash hook scripts and configures `settings.local.json` — no external plugin dependencies.

## How It Works

1. Bundled bash script templates live at `templates/` inside this plugin
2. Rule definitions in `rules/no-*.md` are the source of truth for patterns and messages
3. The install skill copies templates to `.claude/hooks/` in the target project
4. Scripts are registered as Stop, PreToolUse, and PostToolUse hooks in `.claude/settings.local.json`
5. No runtime dependencies — just bash, jq, and grep

## Curated Rule Set

**Rule definitions:** `plugins/agent-guardrails/rules/no-*.md`
**Bundled scripts:** `plugins/agent-guardrails/templates/`

### Stop Hook Rules (check assistant output after each response)

| # | Rule | Description |
|---|------|-------------|
| 1 | `no-speculative-language` | Blocks hedging, guessing, unverified claims |
| 2 | `no-stalling` | Blocks stalling language, padding before action |
| 3 | `no-preference-asking` | Blocks delegating decisions to the user |
| 4 | `no-false-completion` | Blocks unverified completion claims |
| 5 | `no-skipping` | Blocks skipping work or hand-waving |
| 6 | `no-dismissing` | Blocks dismissing issues without investigation |
| 7 | `no-echo-back` | Blocks restating the plan instead of executing |
| 8 | `no-robotic-comments` | Blocks AI-style verbose code comments |
| 9 | `no-over-explaining` | Blocks unnecessary post-change narration |

### PreToolUse Hook Rules (intercept before tool execution)

| # | Rule | Description |
|---|------|-------------|
| 10 | `no-blind-edit` | Blocks editing files that haven't been Read first |
| 11 | `no-destructive-bash` | Blocks destructive commands (rm -rf, git push --force, git reset --hard) |

## Workflow

### Step 1: Check Current State

Check what guardrail files already exist in the project:

```bash
ls .claude/hooks/stop-guardrails.sh .claude/hooks/pretooluse-edit-guardrail.sh .claude/hooks/posttooluse-read-tracker.sh .claude/hooks/pretooluse-bash-guardrail.sh 2>/dev/null
cat .claude/settings.local.json 2>/dev/null
```

### Step 2: Determine What to Install

**If `$ARGUMENTS` contains specific rule names** (e.g., "install no-stalling no-skipping"):
- Copy only the relevant templates. For Stop rules, edit the stop-guardrails.sh to remove unwanted grep blocks. For PreToolUse/PostToolUse rules, only copy the relevant scripts.

**If `$ARGUMENTS` mentions "all" or "curated"** (e.g., "install all"):
- Copy all templates as-is.

**If `$ARGUMENTS` is empty:**
- Copy all templates as-is. This is the default — do not ask the user to choose.

### Step 3: Create Directories

```bash
mkdir -p .claude/hooks
```

### Step 4: Copy All Bash Script Templates

Read the bundled templates from `${CLAUDE_PLUGIN_ROOT}/templates/` and write them to `.claude/hooks/` in the target project:

1. `stop-guardrails.sh` — Stop hook (9 rules)
2. `pretooluse-edit-guardrail.sh` — PreToolUse hook for Edit (no-blind-edit)
3. `posttooluse-read-tracker.sh` — PostToolUse hook for Read (tracks reads for no-blind-edit)
4. `pretooluse-bash-guardrail.sh` — PreToolUse hook for Bash (no-destructive-bash)

If only a subset of rules was requested (Step 2), only copy the relevant scripts and remove unwanted grep blocks from stop-guardrails.sh.

If the user has existing hook scripts with custom rules, preserve those custom blocks when overwriting.

### Step 5: Make Scripts Executable

```bash
chmod +x .claude/hooks/stop-guardrails.sh
chmod +x .claude/hooks/pretooluse-edit-guardrail.sh
chmod +x .claude/hooks/posttooluse-read-tracker.sh
chmod +x .claude/hooks/pretooluse-bash-guardrail.sh
```

### Step 6: Configure settings.local.json

Read the existing `.claude/settings.local.json` if it exists. Merge all hook entries into it, preserving any existing hooks and permissions.

The hook entries to add:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/stop-guardrails.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/pretooluse-edit-guardrail.sh",
            "timeout": 5000
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/pretooluse-bash-guardrail.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Read",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/posttooluse-read-tracker.sh",
            "timeout": 5000
          }
        ]
      }
    ]
  }
}
```

If hooks for these scripts already exist, leave them as-is (just update the script files).

### Step 7: Verify Installation

After writing all files, verify:

```bash
ls -la .claude/hooks/*.sh
head -5 .claude/hooks/stop-guardrails.sh
cat .claude/settings.local.json | jq '.hooks'
```

### Step 8: Report Results

Show what was installed:

```
## Agent Guardrails Installed

### Stop Hook Rules (9 rules)
| Rule | Status |
|------|--------|
| no-speculative-language | Installed |
| no-stalling | Installed |
| no-preference-asking | Installed |
| no-false-completion | Installed |
| no-skipping | Installed |
| no-dismissing | Installed |
| no-echo-back | Installed |
| no-robotic-comments | Installed |
| no-over-explaining | Installed |

### PreToolUse Hook Rules (2 rules)
| Rule | Status |
|------|--------|
| no-blind-edit | Installed |
| no-destructive-bash | Installed |

**Scripts:** `.claude/hooks/stop-guardrails.sh`, `pretooluse-edit-guardrail.sh`, `posttooluse-read-tracker.sh`, `pretooluse-bash-guardrail.sh`
**Config:** `.claude/settings.local.json` (Stop + PreToolUse + PostToolUse hooks)
**Runtime:** bash + jq + grep (no plugin dependencies)
**Effect:** Immediate — no restart needed.

Stop rules trigger when the assistant finishes a response. PreToolUse rules trigger before Edit and Bash tool calls. The read tracker (PostToolUse) silently records Read calls for the no-blind-edit rule.

**To customize:** Edit scripts in `.claude/hooks/` directly.
**To add/remove rules:** Re-run /agent-guardrails:install with specific rule names.
**To refine:** Run /agent-guardrails:update after using the rules for a few sessions.
```

## Custom Rules

If the user provides a custom behavior description (not one of the six curated rules), add a new grep block to the bash script following the same pattern:

```bash
# {kebab-case-name}
if echo "$message" | grep -qiE '{pattern}'; then
  blocked+=("**{kebab-case-name}**: {message}")
fi
```
