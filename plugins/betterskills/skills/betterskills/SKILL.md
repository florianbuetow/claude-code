---
name: betterskills
description: Critique, improve, or create Claude Code skills against the betterskills standard. Use when the user asks to "critique my skill", "review this skill", "improve/prune/shorten a skill", "create a skill", "turn this correction into a skill", or "which of my corrections should become skills".
argument-hint: critique|improve|create <skill name, path, or correction>
disable-model-invocation: false
---

# betterskills

Route the request to one subskill. Each one applies
`../../references/standard.md`.

| The user wants to… | Route to |
|---|---|
| judge, review, audit, score, or compare skills; "is this skill any good" | `betterskills:critique` |
| improve, revise, prune, shorten, tighten, or fix a skill; fold new corrections into it | `betterskills:improve` |
| write a new skill; turn a correction into a skill; find which corrections deserve a skill | `betterskills:create` |

Read the first word of the arguments as the subcommand when it is
`critique`, `improve`, or `create`. Otherwise infer it from the table.

When the request names a correction the user keeps making but no
existing skill, route to `create`; `create` checks whether an existing
skill should absorb it instead.

Invoke the subskill and pass the remaining arguments through.
