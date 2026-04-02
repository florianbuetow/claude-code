# agent-guardrails

Behavioral guardrails for Claude Code agents. Eleven rules across three hook types, with skills for data-driven analysis and tuning.

## Installation

```bash
claude plugin marketplace add florianbuetow/claude-code
claude plugin install agent-guardrails
```

<details>
<summary>Manual / Development Installation</summary>

```bash
git clone https://github.com/florianbuetow/claude-code.git
cd claude-code
claude --plugin-dir ./plugins/agent-guardrails
```

</details>

## How It Works

Guardrails are enforced by bash scripts registered as Claude Code [hooks](https://docs.anthropic.com/en/docs/claude-code/hooks). Three hook types work together:

- **Stop hooks** check assistant output after each response and block anti-patterns
- **PreToolUse hooks** intercept tool calls before execution and block dangerous operations
- **PostToolUse hooks** track tool usage for stateful rules (e.g., recording file reads)

**No external plugin dependencies** — just bash, jq, and grep.

```
Stop:         Assistant response  -> stop-guardrails.sh       -> block / allow
PreToolUse:   Edit tool call      -> pretooluse-edit-guardrail -> block / allow
PreToolUse:   Bash tool call      -> pretooluse-bash-guardrail -> block / allow
PostToolUse:  Read tool call      -> posttooluse-read-tracker  -> record (silent)
```

## Rules

### Stop Hook Rules

| Rule | What It Catches |
|------|----------------|
| `no-speculative-language` | Hedging, guessing, unverified claims ("probably", "I think", "this should work") |
| `no-stalling` | Padding before action ("before I proceed", "a few things to consider") |
| `no-preference-asking` | Delegating decisions to the user ("would you prefer", "shall I") |
| `no-false-completion` | Claiming completion without evidence ("all done", "fully implemented", "Done!") |
| `no-skipping` | Skipping work or hand-waving ("the rest looks fine", "for brevity") |
| `no-dismissing` | Dismissing issues without investigation ("not a real bug", "can be ignored", "this is fine") |
| `no-echo-back` | Restating the plan instead of executing ("I'll now proceed to...", "Let me start by...") |
| `no-robotic-comments` | AI-style verbose code comments ("// This function handles...", "// Initialize the...") |
| `no-over-explaining` | Unnecessary post-change narration ("The reason I made this change...", "This ensures that...") |

### PreToolUse Hook Rules

| Rule | What It Catches |
|------|----------------|
| `no-blind-edit` | Editing files that haven't been Read first in this session |
| `no-destructive-bash` | Destructive commands: `rm -rf /`, `git push --force`, `git reset --hard`, `git clean -f`, `git branch -D` |

## Quick Start

```
/agent-guardrails:install     # Install all eleven rules into your project
/agent-guardrails:analyze     # Scan session logs for anti-patterns
/agent-guardrails:update      # Tune rules based on real usage data
```

### Install

Copies bundled bash scripts to `.claude/hooks/` and registers them in `.claude/settings.local.json`. Specify rule names to install a subset, or run with no arguments for all eleven.

### Analyze

Scans recent Claude Code session logs for anti-pattern frequency. Produces a ranked report with match counts, example excerpts, and recommendations for which rules to install.

### Update

Re-analyzes session logs against your installed rules. Identifies false positives (pattern too aggressive), false negatives (pattern too lenient), and uncovered gaps. Applies refinements to the bash scripts directly.

## Files

After installation, your project will have:

```
.claude/
  hooks/
    stop-guardrails.sh            # Stop hook: 9 output rules
    pretooluse-edit-guardrail.sh   # PreToolUse: blocks Edit without prior Read
    posttooluse-read-tracker.sh    # PostToolUse: records Read calls for no-blind-edit
    pretooluse-bash-guardrail.sh   # PreToolUse: blocks destructive bash commands
  settings.local.json              # Hook configuration (Stop + PreToolUse + PostToolUse)
```

## Customization

Edit scripts in `.claude/hooks/` directly. Stop rules are grep blocks:

```bash
# no-speculative-language
if echo "$message" | grep -qiE '(pattern...)'; then
  blocked+=("**no-speculative-language**: Message...")
fi
```

PreToolUse rules inspect tool input JSON and return `{"decision": "block", "reason": "..."}` to block.

Add, remove, or modify rules as needed. Changes take effect immediately.

## License

[MIT](LICENSE)
