---
name: terminator:update
description: Update the terminator kill phrases or case sensitivity at local or global scope. Prints the current phrase before asking for a new one. Rewrites only the changed fields; hooks read config live so changes take effect immediately. Use when the user asks to "update the kill phrase", "change the single/double kill phrase", or "toggle case sensitivity".
disable-model-invocation: false
---

# Terminator: Update

Change the single-kill phrase, double-kill phrase, and/or case sensitivity. The hooks read their
config file live on every stop, so changes take effect immediately — no restart needed.

## Step 1 — Detect installed scope(s)

```bash
local_config=".claude/terminator.json"
global_config="$HOME/.claude/terminator.json"
[ -f "$local_config"  ] && echo "LOCAL:  $local_config"  || echo "LOCAL:  not installed"
[ -f "$global_config" ] && echo "GLOBAL: $global_config" || echo "GLOBAL: not installed"
```

- If **neither** is installed: offer `/terminator:install` and stop.
- If **only one** is installed: use that scope automatically.
- If **both** are installed: ask the user which scope to update.

## Step 2 — Show current config

Print the full current config for the chosen scope so the user can see what's active:

```bash
echo "=== Current config (<LOCAL|GLOBAL>: <CONFIG_FILE>) ==="
cat <CONFIG_FILE>
```

## Step 3 — Get the new value(s)

Ask which to change: `single_killphrase`, `double_killphrase`, and/or `case_sensitive`. Keep any
the user does not change.

## Step 4 — Phrase Safety Check

Terminator uses a **contains-match** against the final assistant message. Any phrase that appears
in normal assistant output will cause sessions to terminate **apparently at random**.

Recommend a memorable, rare phrase — a movie quote, a line of poetry, or a sentence unlikely to
appear in normal output (e.g. `I'll be back, but not this session`).

**⚠️ WARNING — short or common phrase:**
If the new phrase is a short clause or sentence that could plausibly appear in a typical assistant
response, warn the user:

> ⚠️ **Warning:** This phrase is short and may appear in ordinary responses, causing your session
> to terminate unexpectedly. A longer, more distinctive phrase is strongly recommended.
> Do you want to use it anyway?

Only proceed if the user confirms.

**🚨 STRONG WARNING — single common English word:**
If the phrase is a single word or a very common short term (e.g. `done`, `stop`, `finish`,
`complete`, `exit`, `quit`, `kill`, `terminate`, `goodbye`), issue a strong warning:

> 🚨 **Strong Warning:** Single common words **will** appear in normal assistant output and **will**
> cause your session to terminate at seemingly random moments. This is almost certainly not what
> you want. Are you absolutely sure you want to use this as your kill phrase?

Only proceed if the user explicitly confirms they are absolutely sure.

If both `single_killphrase` and `double_killphrase` are configured, they must be distinct and
neither may contain the other.

## Step 5 — Write (read-modify-write — preserve other fields)

Update only the fields the user changed; never rebuild the file from scratch.

```bash
tmp="$(mktemp)"
# example: change both phrases, keep case_sensitive as-is
jq --arg s "<new single>" --arg d "<new double>" \
  '.single_killphrase=$s | .double_killphrase=$d' <CONFIG_FILE> > "$tmp" \
  && mv "$tmp" <CONFIG_FILE>
cat <CONFIG_FILE>
```

## Step 6 — Report

```
## Terminator updated (<LOCAL|GLOBAL> scope)
  single_killphrase : <s>
  double_killphrase : <d>
  case sensitive    : <true|false>
Effective immediately — hooks read config live.
```
