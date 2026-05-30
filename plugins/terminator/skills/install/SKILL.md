---
name: terminator:install
description: Install the terminator kill hooks into the current project. Installs single-kill.sh and/or double-kill.sh as Stop hooks, each bound to a non-obvious phrase, merging into .claude/settings.local.json without clobbering existing hooks. Use when the user asks to "install terminator", "set up the kill hooks", "add single kill", "add double kill", or "enable session termination".
disable-model-invocation: false
---

# Terminator: Install

Install one or both kill hooks into the **current project**. There are two independent scripts;
which behaviour you get is determined by **which script is installed**, not by a flag:

- `single-kill.sh` — phrase fires → terminate Claude. Terminal stays open.
- `double-kill.sh` — phrase fires → terminate Claude **and** the terminal shell that launched it.

Matching is **contains** (the message need only contain the phrase; robust to model preambles),
case-sensitivity configurable. The only hard safety rule in the kill path is: never signal pid ≤ 2.

> Scope: install into the project's `.claude/`. Do not touch global `~/.claude/settings.json`
> unless the user explicitly asks.

## Step 1 — Which hooks?

Ask the user (or read from `$ARGUMENTS`): **single**, **double**, or **both**.

## Step 2 — Phrases + case sensitivity

- Single-kill phrase (suggest a generated phrase such as `term-single-<16 random lowercase hex chars>`).
- Double-kill phrase (suggest a generated phrase such as `term-double-<16 random lowercase hex chars>`).
- Run the phrase strength gate below before accepting each phrase.
- Use distinct phrases; if both hooks are installed, neither phrase may equal or contain the other.
- Case-sensitive (default) or case-insensitive (`AskUserQuestion`).

### Phrase Strength Gate

Terminator uses a contains-match against the final assistant message, so obvious phrases are unsafe:
normal conversation or quoted user text could trigger the hook. Do not write `.claude/terminator.json`
until every configured phrase passes this gate.

A phrase is acceptable only if all of these are true:

- It is at least 18 characters after trimming whitespace.
- It includes an uncommon random component, such as 16+ lowercase hex characters, 12+ base64url
  characters, or four unrelated random words.
- It is not a normal completion word or short instruction, including `done`, `finish`, `finished`,
  `complete`, `completed`, `exit`, `quit`, `stop`, `kill`, `terminate`, `single kill`,
  `double kill`, `all done`, `goodbye`, or close variants.
- It is not a phrase the assistant is likely to say in a normal final answer.
- If `case_sensitive` is false, the lowercased phrase still passes the same gate.
- If both hooks are installed, the two phrases are distinct and neither phrase contains the other.

If a requested phrase fails, do not install with it. Explain the failing condition briefly and ask
for a stronger phrase or offer a generated one.

## Step 3 — Confirm (destructive)

```
About to install in this project:
  single-kill.sh  phrase="<single phrase>"   -> ends Claude
  double-kill.sh  phrase="<double phrase>"   -> ends Claude + terminal
  case sensitive  : <true|false>
```

## Step 4 — Copy the chosen script(s)

```bash
mkdir -p .claude/hooks
# copy ${CLAUDE_PLUGIN_ROOT}/templates/single-kill.sh  -> .claude/hooks/single-kill.sh   (if single/both)
# copy ${CLAUDE_PLUGIN_ROOT}/templates/double-kill.sh  -> .claude/hooks/double-kill.sh   (if double/both)
chmod +x .claude/hooks/*-kill.sh
```

## Step 5 — Write config

```bash
jq -n --arg s "<single phrase>" --arg d "<double phrase>" --argjson cs <true|false> \
  '{single_killphrase:$s, double_killphrase:$d, case_sensitive:$cs}' > .claude/terminator.json
```

(Omit the key for a script you are not installing; each script only reads its own key.)

## Step 6 — Merge the Stop hook(s) — never clobber existing hooks

For each script being installed, merge its entry in idempotently:

```bash
[ -f .claude/settings.local.json ] || echo '{}' > .claude/settings.local.json
for s in single-kill.sh double-kill.sh; do   # restrict to the ones you installed
  cmd="\"\$CLAUDE_PROJECT_DIR\"/.claude/hooks/$s"
  tmp="$(mktemp)"
  jq --arg cmd "$cmd" --arg s "$s" '
    .hooks.Stop = ((.hooks.Stop // [])
      | if any(.hooks[]?.command? // "" | contains($s)) then .
        else . + [{matcher:"", hooks:[{type:"command", command:$cmd, timeout:10000}]}]
        end)
  ' .claude/settings.local.json > "$tmp" && mv "$tmp" .claude/settings.local.json
done
```

## Step 7 — Verify & report

```bash
ls -la .claude/hooks/*-kill.sh
cat .claude/terminator.json
jq '.hooks.Stop' .claude/settings.local.json
```

```
## Terminator installed
  single-kill.sh : phrase "<s>"   (Claude only)            [if installed]
  double-kill.sh : phrase "<d>"   (Claude + terminal)      [if installed]
  case sensitive : <true|false>
  Other Stop hooks: preserved

Takes effect after a session restart (/exit and start a new Claude session).
Change phrases: /terminator:update   Uninstall: /terminator:remove
```
