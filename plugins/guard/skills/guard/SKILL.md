---
name: guard
description: Use when the user wants to initialize, build a collection in, remove a collection from, clear, or inspect the `guard` CLI file-permission tool. Triggers on "init guard", "set up guard", "guard my test files", "create a guard collection", "remove guard collection", "delete guard collection", "unguard a collection", "clear all guard", "wipe guard", "reset guard", "guard status", "guard info", "show guard", "what's guarded".
---

# guard

Helper for the `guard` CLI (https://github.com/florianbuetow/guard). Guard protects files from accidental edits by setting the immutable flag and root ownership. This skill composes the right `guard` commands for the user.

## Routing

| Intent | Reference |
|---|---|
| Set up guard / `.guardfile` missing | `references/init.md` |
| Build a collection from a description or list | `references/create-collection.md` |
| Remove a collection | `references/remove-collection.md` |
| Restore everything, wipe the registry | `references/clear-all.md` |
| Show collections and loose guarded files | `references/info.md` |

## The sudo rule (the only non-obvious thing)

The agent runs as the user, without sudo. Operations that **change a file's guard state** require root (clearing the immutable flag is root-only), so the agent **cannot run them** — it prints the exact `sudo guard …` command for the user to run.

- **Print `sudo guard …`** for: `enable`, `disable`, `toggle`, `reset`, and `destroy`/`remove`/`clear` when the target files are **currently guarded**.
- **Run directly** (no sudo): `init`, `add`, `create`, `update … add`, `show`, `config`, and `destroy`/`remove` when files are **already unguarded**.

Check guard state with `guard show` before deciding. A file is guarded when its line starts with `G`.

## Quote arguments

Always quote collection names and file paths in any command you run or print: `guard destroy "$name"`, `sudo guard enable collection "$name"`. Paths can contain spaces.

## CLI reference

For exact syntax of any subcommand, run `guard help <sub>`. Don't reproduce it here.
