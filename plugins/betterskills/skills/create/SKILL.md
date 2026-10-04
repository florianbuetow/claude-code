---
name: create
description: Write a new, minimal skill from a correction the user keeps making, or mine session history for corrections worth a skill.
argument-hint: [the correction you keep making] [personal|project|plugin <path>]
disable-model-invocation: true
---

# Create a skill

Load `../../references/standard.md` and
`../../references/leading-words.md` first.

## Step 1 — Name the correction

Take it from the arguments. Without one, run the query in
`../../references/corrections.md` over the last 30 days, cluster the
hits, and present the top five clusters ranked by distinct sessions:

| # | Correction | Sessions | Example | Failing step |
|---|------------|----------|---------|--------------|

Ask the user to pick one. With no history, ask: "What output did you
last send back, and what did you change?"

Write down, before drafting anything:

- **Correction** — what the user sends back and what they change.
- **Failing step** — the one step where the output goes wrong (R1.b).

## Step 2 — Earn the skill

Stop at the first gate that fails and report the alternative instead of
writing a skill.

1. **Overlap (R5.c)** — list installed skills (command in
   `../../references/skills-on-disk.md`). If one covers the behavior,
   recommend `/betterskills:improve <that skill>` with the correction as
   input. If several compose into it, show the composition.
2. **Default behavior (R1.d)** — when the Agent tool is available, give
   a subagent the task with no skill and judge whether its output would
   be sent back. Acceptable output means no skill is needed.
3. **One-liner** — if the fix is a single standing rule with no
   procedure, recommend a `CLAUDE.md` line instead.

## Step 3 — Draft

- **Name** — a short verb or leading word (`grill-me`, `premortem`).
- **Words** — pick leading words for the failing step (R2) before
  writing any sentence of explanation.
- **Body** — only the instructions that fix the failing step, one
  sentence each, stated as desired behavior. Add a confirmation gate
  when the failure is asset rush (R1.c). Aim for under 20 lines.
- **Frontmatter** — `name`, a one-line `description`, and
  `disable-model-invocation: true` unless the skill must fire on a
  trigger the user would forget (R3).

## Step 4 — Self-check

Run `betterskills:critique` Step 4 against the draft and fix every
finding.

## Step 5 — Write

Place it per the arguments, else by scope: a correction tied to one
repository goes to `.claude/skills/<name>/SKILL.md`, anything else to
`~/.claude/skills/<name>/SKILL.md`. For a plugin, write
`skills/<name>/SKILL.md` inside the plugin's source tree.

Report the path, the invocation (`/<name>`), and the next step: use it
on real work for about a week, then run `/betterskills:improve <name>`.
