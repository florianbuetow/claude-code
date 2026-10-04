---
name: critique
description: Judge an existing skill against the betterskills standard and report every finding with its fix, without editing anything.
argument-hint: <skill name or path> | all
disable-model-invocation: true
---

# Critique a skill

Read-only. Produce findings; leave every file untouched.

## Step 1 — Load the standard

Read `../../references/standard.md` and `../../references/leading-words.md`.

## Step 2 — Resolve the target

Resolve the argument to a `SKILL.md` per
`../../references/skills-on-disk.md`. Read it and every file it links to.
With `all` or a directory, collect every `SKILL.md` under it and go to
Step 6.

## Step 3 — Gather evidence

- Measure: `wc -lw`, body only.
- List installed skills (command in `skills-on-disk.md`) for R5.c.
- When session history exists, run the corrections query in
  `../../references/corrections.md`, filtered by the skill's topic, for
  R4.c.

## Step 4 — Apply every check

Work through R1.a to R5.c in order. Each finding quotes the exact
sentence, names the check, and gives the fix as replacement text — a
leading word, a positive rewrite, a deletion, or a one-sentence
instruction.

When R1.a cannot be answered from the skill or its history, record it as
a finding and ask the owner which correction the skill was meant to stop.

## Step 5 — Report

```
## <name> — <verdict>
<path> · <lines> lines / <words> words · invocation: <model|user> → recommend <model|user>
Targets: <the correction, one sentence> · Failing step: <step>

| # | Check | Quote | Finding | Fix |
|---|-------|-------|---------|-----|

Projected size after fixes: <lines> lines / <words> words
```

Verdict is one of **Keep** (no findings above R5), **Revise**, **Merge
into <skill>**, or **Delete** (R1.d: Claude already does this). Order
rows by impact: R1, then R5.c, then the rest. End with the command that
applies the fixes: `/betterskills:improve <name>`.

## Step 6 — Many skills

Run Steps 3–4 per skill, then report one table sorted by verdict
(Delete, Merge, Revise, Keep):

| Skill | Words | Invocation | Verdict | Top finding |
|-------|-------|------------|---------|-------------|

Follow it with the overlap groups found under R5.c.
