---
name: continue
description: Find handoff documents and continue work on a previous task with full
  context. Companion to the `handoff` skill.
argument-hint: Optional filter — topic keyword to narrow candidates.
disable-model-invocation: true
---

# Continue skill

Find handoff documents written by the `handoff` skill, present them to
the user, then execute the continuation protocol specified in the chosen
handoff.

---

## Step 1: Find candidate handoffs

Look in `docs/handoffs/*.md`, relative to the current working directory.

If the directory does not exist, tell the user:

> "No `docs/handoffs/` directory found here. If you're in the wrong
> working directory, change to the project root and run continue again.
> If you have a handoff elsewhere, share its path and I'll read it
> directly."

If a filter argument is provided, match it case-insensitively against
the H1 topic and the Goal section of each handoff.

---

## Step 2: Parse each candidate

For each handoff file, extract:

- **Topic** — from the H1 (`# Handoff: <topic>`).
- **Goal** — first non-empty line under `## Goal`.
- **First action** — first numbered item under `## Next agent: start here`.
- **Timestamp** — from `## Metadata` > `Timestamp:`.
- **Mode** — from `## Metadata` > `Mode:`.
- **Verification** — from `## Metadata` > `Verification:`.
- **Prior handoff** — from `## Metadata` > `Prior handoff:`.
- **Path** — full file path.

If a file is malformed, skip it but report "Skipped malformed: <path>
(<reason>)" so the user knows it exists. Treat as malformed if any of
these are missing: H1 starting with `# Handoff:`, `## Goal` section,
`## Next agent: start here` section, `## Metadata` section.

---

## Step 3: Present candidates

**Zero candidates.** Tell the user honestly:

> "No handoff files found in `docs/handoffs/`. If you have a handoff
> elsewhere, share its path and I'll read it directly."

Do not invent options.

**One candidate.** Don't make the user pick from a list of one. Show
the parsed preview and confirm:

> "Found one handoff:
>
> **<topic>** (<mode>, <relative age>)
> Goal: <goal>
> First action: <first action>
> Path: <path>
>
> Continue this? (yes / no)"

**Multiple candidates.** Sort by timestamp, newest first. Show as a
numbered list with parsed preview for each:

> "Found N handoffs. Newest first:
>
> 1. **<topic>** (<mode>, <relative age>)
>    Goal: <goal>
>    First action: <first action>
>
> 2. **<topic>** (<mode>, <relative age>)
>    ...
>
> Which would you like to continue? (number, or 'none')"

Flag any handoff with `Verification: non-interactive` using a
`[unverified]` marker — its Intent and Stance were inferred without
user confirmation.

Flag any handoff older than 30 days with a `[stale]` marker. Do not
hide it; the marker invites scrutiny.

---

## Step 4: Execute the continuation protocol

Once the user has chosen a handoff:

1. **Read the entire handoff file.**
2. **If the handoff is part of a chain** (Prior handoff is not "(none)"),
   read the prior handoff too. Follow the chain back at most 3 hops; if
   longer, tell the user the chain extends further and ask whether to
   keep traversing.
3. **Read all Tier 1 files** listed under "Next agent: start here".
4. **If the handoff is non-interactive** (unverified Intent and Stance),
   say:
   > "This handoff's Intent and Stance were inferred without verification.
   > Before I act on them, can you confirm or correct them? Here's what
   > was inferred:
   >
   > <quote Intent and Stance sections>"
5. **Summarise back to the user**, in this order:
   - Goal (one sentence).
   - Intent (1–2 sentences capturing what we're optimizing for and not).
   - Stance & ways of working (1 sentence).
   - First concrete action.
   - Any open questions from the handoff that block the first action.
6. **Wait for confirmation or correction** before doing anything else.
   Do not start executing.

---

## Step 5: After continuation

Leave the handoff file alone. Do not delete, move, rename, or modify it.
The user manages handoff files; this skill only reads them.

---

## Constraints

- **Read-only.** Never write to handoff files.
- **No fabrication.** If a section is missing or empty, report it
  honestly — do not guess what the previous session meant.
- **No silent execution.** Always summarise and confirm before acting,
  even if the first action seems obvious.
- **Honour the Tier system.** Read Tier 1 files before summarising.
  Read Tier 2 files only when their trigger condition fires during
  the continued work. Tier 3 files are not read unless the user asks.

---

## Argument handling

If the user passes an argument (e.g., `continue auth refactor`), treat
it as a filter against topic and goal. If exactly one handoff matches,
go directly to the single-candidate confirmation. If multiple match,
show the filtered list. If none match, fall back to showing all
handoffs and tell the user the filter matched nothing.
