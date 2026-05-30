---
name: terminator:update
description: Update the terminator kill phrases or case sensitivity for the current project. Rewrites only the changed fields in .claude/terminator.json; new phrases must be non-obvious; no restart needed since the hooks read config live. Use when the user asks to "update the kill phrase", "change the single/double kill phrase", or "toggle case sensitivity".
disable-model-invocation: false
---

# Terminator: Update

Change the single-kill phrase, double-kill phrase, and/or case sensitivity for the **current
project**. The hooks read `.claude/terminator.json` live on every stop, so changes take effect
immediately — no restart.

## Step 1 — Check installed

```bash
test -f .claude/terminator.json && cat .claude/terminator.json || echo "NOT INSTALLED"
```

If `NOT INSTALLED`, offer `/terminator:install` and stop.

## Step 2 — Get the new value(s)

Ask which to change: `single_killphrase`, `double_killphrase`, and/or `case_sensitive`. Keep any
the user does not change.

## Step 3 — Validate phrase strength

Terminator uses a contains-match against the final assistant message, so obvious phrases are unsafe:
normal conversation or quoted user text could trigger the hook. Do not write `.claude/terminator.json`
until the final configured phrase set passes this gate.

A phrase is acceptable only if all of these are true:

- It is at least 18 characters after trimming whitespace.
- It includes an uncommon random component, such as 16+ lowercase hex characters, 12+ base64url
  characters, or four unrelated random words.
- It is not a normal completion word or short instruction, including `done`, `finish`, `finished`,
  `complete`, `completed`, `exit`, `quit`, `stop`, `kill`, `terminate`, `single kill`,
  `double kill`, `all done`, `goodbye`, or close variants.
- It is not a phrase the assistant is likely to say in a normal final answer.
- If `case_sensitive` is false, the lowercased phrase still passes the same gate.
- If both `single_killphrase` and `double_killphrase` are configured, they are distinct and neither
  phrase contains the other.

If a requested phrase fails, do not update the config with it. Explain the failing condition briefly
and ask for a stronger phrase or offer a generated one, such as
`term-single-<16 random lowercase hex chars>` or `term-double-<16 random lowercase hex chars>`.

## Step 4 — Write (read-modify-write — preserve other fields)

Update only the fields the user changed; never rebuild the file from scratch.

```bash
tmp="$(mktemp)"
# example: change both phrases, keep case_sensitive as-is
jq --arg s "<new single>" --arg d "<new double>" \
  '.single_killphrase=$s | .double_killphrase=$d' .claude/terminator.json > "$tmp" \
  && mv "$tmp" .claude/terminator.json
cat .claude/terminator.json
```

## Step 5 — Report

```
## Terminator updated
  single_killphrase : <s>
  double_killphrase : <d>
  case sensitive    : <true|false>
Effective immediately — hooks read config live.
```
