---
name: improve
description: Rewrite an existing skill to the betterskills standard — prune no-ops, swap explanation for leading words, fold in observed corrections as one-sentence fixes.
argument-hint: <skill name or path> [precise|aggressive] [corrections you still make]
disable-model-invocation: true
---

# Improve a skill

## Step 1 — Critique first

Follow `betterskills:critique` Steps 1–4 on the target. Keep the
findings; skip the report.

If the target is an installed plugin copy, locate the plugin's source
repository (see `../../references/skills-on-disk.md`) and edit there.

## Step 2 — Collect the corrections still being made

Take every correction the user names in the arguments or the
conversation. Add the ones from session history: run the query in
`../../references/corrections.md` for the period since the skill file
last changed, filtered by the skill's topic. Cluster them and write one
sentence of desired behavior per recurring cluster, placed at the step
that failed.

Add instructions only for corrections that actually occurred (R4).

## Step 3 — Rewrite

Apply in this order:

1. Delete every R5.a no-op as a whole sentence.
2. Replace each R2.a explanation with its leading word.
3. Rewrite each R5.b prohibition as the desired behavior.
4. Insert the Step 2 fixes. Add a confirmation gate where R1.c found
   asset rush.
5. Set `disable-model-invocation` per R3.b and shorten the description
   per R3.c.
6. Act on R5.c: merge the overlapping skill's unique instructions in, or
   replace duplicated steps with a call to the other skill.

Preserve the `name`, every referenced file that exists, and prohibitions
that guard a specific dangerous act.

## Step 4 — Verify by mode

**Aggressive** (default): apply all changes at once.

**Precise**: apply one change at a time. When the Agent tool is
available, run the skill before and after the change on the same real
task in two subagents and compare outputs. Keep a deletion when the
output is unchanged; revert any change that makes the output worse.

## Step 5 — Write and report

Copy the original to a temporary file, write the revision, and show
`diff -u` between them. Then report:

```
<name>: <words before> → <words after> words · invocation <old> → <new>
| Change | Rule | Why |
|--------|------|-----|
```

Close with the revision loop: use the skill on real work for about a
week, then run `/betterskills:improve <name>` again.
