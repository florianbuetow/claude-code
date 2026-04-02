---
name: no-destructive-bash
pattern: N/A (enforced via PreToolUse hook on Bash, not regex)
message: "Destructive command detected. Investigate alternatives or confirm this was explicitly requested."
hook_type: PreToolUse
hook_target: Bash
---

**Stop - destructive bash command detected.**

You attempted to run a destructive command that is hard to reverse (e.g., `rm -rf`, `git push --force`, `git reset --hard`, `git clean -f`, `git branch -D`). These commands destroy work:
1. **Prefer safe alternatives** — `git stash` over `git checkout -- .`, `git revert` over `git reset --hard`.
2. **Verify intent** — only run destructive commands when the user explicitly requested them.
3. **Never force-push to shared branches** — this overwrites others' work.

This rule is enforced by a PreToolUse hook on Bash that pattern-matches against known destructive commands.
