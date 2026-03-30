# Hooks

Behavioral hooks for Claude Code that enforce assistant discipline. Each subdirectory contains hooks for a specific runtime engine.

## hookify/

Five hooks that block common AI anti-patterns by intercepting responses at the `stop` event.

| Hook | Blocks |
|------|--------|
| `no-speculative-language` | Hedging and guessing instead of investigating |
| `no-skipping` | Glossing over work instead of doing it |
| `no-preference-asking` | Asking for preference instead of deciding |
| `no-false-completion` | Claiming done without verification |
| `no-stalling` | Over-explaining instead of acting |

### Step 1 — Install hookify

These hooks require the **hookify** plugin as their runtime engine. Install it first:

```bash
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install hookify
```

See [hookify on GitHub](https://github.com/anthropics/claude-plugins-official) for details.

### Step 2 — Install the hooks

Copy the `.local.md` files into your project's `.claude/` directory:

```bash
# curl (from any project directory)
for hook in no-speculative-language no-skipping no-preference-asking no-false-completion no-stalling; do
  curl -sL "https://raw.githubusercontent.com/florianbuetow/claude-code/main/hooks/hookify/hookify.${hook}.local.md" \
    -o ".claude/hookify.${hook}.local.md"
done

# or clone and copy
git clone https://github.com/florianbuetow/claude-code.git /tmp/claude-code
cp /tmp/claude-code/hooks/hookify/*.local.md .claude/
rm -rf /tmp/claude-code
```

Hooks take effect immediately — no restart needed.
