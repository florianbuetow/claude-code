# Skills on Disk

## Where skills live

| Scope | Path |
|---|---|
| Personal | `~/.claude/skills/<name>/SKILL.md` |
| Project | `<repo>/.claude/skills/<name>/SKILL.md` |
| Plugin (installed copy) | `<installPath>/skills/<name>/SKILL.md`, install paths in `~/.claude/plugins/installed_plugins.json` |

A plugin skill is invoked as `/<plugin>:<name>`. Its installed copy is
overwritten on the next plugin update, so edit the plugin's **source**
repository, never the cache. Find the source from the marketplace entry
in `~/.claude/plugins/known_marketplaces.json`, or ask the user where
the repository is checked out.

## Resolve a skill name to a file

Accept a path, a bare name (`grill-me`), or a plugin-qualified name
(`resume:review`). Search in this order and stop at the first hit:

1. The path as given.
2. `.claude/skills/<name>/SKILL.md` in the current repository.
3. `~/.claude/skills/<name>/SKILL.md`.
4. `skills/<name>/SKILL.md` under each install path of
   `~/.claude/plugins/installed_plugins.json` (match the plugin part when
   qualified).
5. `plugins/*/skills/<name>/SKILL.md` in the current repository, for a
   plugin source tree.

Several hits for a bare name: list them and ask which one.

## List every installed skill with its description

Use this to check overlap (R5.c) and composition before creating a
skill:

```bash
{ find -L ~/.claude/skills .claude/skills -name SKILL.md 2>/dev/null
  jq -r '.plugins[][].installPath' ~/.claude/plugins/installed_plugins.json 2>/dev/null \
    | while IFS= read -r p; do find -L "$p" -name SKILL.md 2>/dev/null; done
} | while IFS= read -r f; do
  printf '%s\t%s\n' "$f" "$(sed -n 's/^description: *//p' "$f" | head -1 | cut -c1-200)"
done
```

## Frontmatter fields that matter here

| Field | Effect |
|---|---|
| `name` | The invocation name. |
| `description` | What the model reads to decide whether to invoke the skill; in context every turn while model invocation is on. |
| `disable-model-invocation: true` | Only the user can invoke the skill (`/name`); its description leaves the model's context. |
| `argument-hint` | Hint shown after `/name` in the command menu. |

Measure size with `wc -lw SKILL.md` and count frontmatter separately
from body.
