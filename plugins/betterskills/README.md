# betterskills

Critique, improve, and create Claude Code skills against one standard:
**a skill is a correction you got tired of making.**

## Usage

```
/betterskills critique grill-me
/betterskills improve resume:review
/betterskills create "it keeps writing the code before we agree on the plan"
/betterskills:critique all
/betterskills:improve my-skill precise
/betterskills:create
```

## Skills

| Skill | Purpose |
|-------|---------|
| `betterskills` | Router — sends the request to one subskill |
| `betterskills:critique` | Judges a skill (or all of them) against the standard; reports findings with fixes, edits nothing |
| `betterskills:improve` | Rewrites a skill: prunes no-ops, swaps explanation for leading words, folds observed corrections in as one-sentence fixes |
| `betterskills:create` | Mines session history for repeated corrections, checks overlap and default behavior, drafts a minimal user-invoked skill |

## The standard

`references/standard.md` holds five rules, each with checks (R1.a … R5.c)
that every finding cites:

1. **Target a correction you keep sending back** — aim at the step that
   fails; guard against asset rush.
2. **Use leading words** — established terms recruit training priors;
   coined terms cost definition tokens.
3. **Keep it small; invoke it deliberately** — prefer
   `disable-model-invocation: true`.
4. **Grow it from real use** — every instruction traces to an observed
   failure; revise weekly.
5. **Delete instructions that do no work** — no-ops, prohibitions that
   could be stated positively, overlapping skills.

`references/corrections.jq` lists the corrections you made in
`~/.claude/projects` session logs, so `create` and `improve` work from
evidence rather than guesses. It needs `jq`.
