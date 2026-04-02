---
name: agent-guardrails-install
description: Install agent behavioral guardrail rules into a project's .claude/ directory. Generates a Stop hook bash script and configures settings.local.json. Includes six battle-tested rules (no-speculative-language, no-stalling, no-preference-asking, no-false-completion, no-skipping, no-dismissing). Use when user asks to "install guardrails", "set up agent guardrails", "add behavioral hooks", "agent-guardrails install", or wants to enforce assistant discipline.
---

# Agent Guardrails Install

Install agent behavioral guardrail rules into the current project. Generates a bash script Stop hook and configures `settings.local.json` — no external plugin dependencies.

## How It Works

1. A bundled bash script template lives at `templates/stop-guardrails.sh` inside this plugin
2. Rule definitions in `rules/no-*.md` are the source of truth for patterns and messages
3. The install skill copies the template to `.claude/hooks/stop-guardrails.sh` in the target project
4. The script is registered as a Stop hook in `.claude/settings.local.json`
5. No runtime dependencies — just bash, jq, and grep

## Curated Rule Set

**Rule definitions:** `plugins/agent-guardrails/rules/no-*.md`
**Bundled script:** `plugins/agent-guardrails/templates/stop-guardrails.sh`

| # | Rule | Description |
|---|------|-------------|
| 1 | `no-speculative-language` | Blocks hedging, guessing, unverified claims |
| 2 | `no-stalling` | Blocks stalling language, padding before action |
| 3 | `no-preference-asking` | Blocks delegating decisions to the user |
| 4 | `no-false-completion` | Blocks unverified completion claims |
| 5 | `no-skipping` | Blocks skipping work or hand-waving |
| 6 | `no-dismissing` | Blocks dismissing issues without investigation |

## Workflow

### Step 1: Check Current State

Check what guardrail files already exist in the project:

```bash
ls .claude/hooks/stop-guardrails.sh 2>/dev/null
cat .claude/settings.local.json 2>/dev/null
```

### Step 2: Determine What to Install

**If `$ARGUMENTS` contains specific rule names** (e.g., "install no-stalling no-skipping"):
- Copy the template, then remove the grep blocks for rules NOT in the list.

**If `$ARGUMENTS` mentions "all" or "curated"** (e.g., "install all"):
- Copy the full template as-is.

**If `$ARGUMENTS` is empty:**
- Copy the full template as-is. This is the default — do not ask the user to choose.

### Step 3: Create Directories

```bash
mkdir -p .claude/hooks
```

### Step 4: Copy the Bash Script Template

Read the bundled template from `${CLAUDE_PLUGIN_ROOT}/templates/stop-guardrails.sh` and write it to `.claude/hooks/stop-guardrails.sh` in the target project.

If only a subset of rules was requested (Step 2), remove the unwanted grep blocks from the copied script before writing.

If the user has an existing `.claude/hooks/stop-guardrails.sh` with custom rules (grep blocks not in the curated set), preserve those custom blocks when overwriting.

### Step 5: Make Script Executable

```bash
chmod +x .claude/hooks/stop-guardrails.sh
```

### Step 6: Configure settings.local.json

Read the existing `.claude/settings.local.json` if it exists. Merge the Stop hook entry into it, preserving any existing hooks and permissions.

The Stop hook entry to add:

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
    ]
  }
}
```

If a Stop hook for `stop-guardrails.sh` already exists, leave it as-is (just update the script file).

### Step 7: Verify Installation

After writing all files, verify:

```bash
ls -la .claude/hooks/stop-guardrails.sh
head -5 .claude/hooks/stop-guardrails.sh
cat .claude/settings.local.json | jq '.hooks.Stop'
```

### Step 8: Report Results

Show what was installed:

```
## Agent Guardrails Installed

| Rule | Status |
|------|--------|
| no-speculative-language | Installed |
| no-stalling | Installed |
| no-preference-asking | Installed |
| no-false-completion | Installed |
| no-skipping | Installed |
| no-dismissing | Installed |

**Script:** `.claude/hooks/stop-guardrails.sh`
**Config:** `.claude/settings.local.json` (Stop hook)
**Runtime:** bash + jq + grep (no plugin dependencies)
**Effect:** Requires a session restart. Run `/exit` and start a new Claude session for hooks to take effect.

Rules trigger on the assistant's Stop event. To test after restarting, run `/agent-guardrails:test`.

**To customize:** Edit `.claude/hooks/stop-guardrails.sh` directly.
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
