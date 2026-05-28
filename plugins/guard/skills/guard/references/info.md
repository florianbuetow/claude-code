# info

Summarize current guard state: collections (with protection status) and guarded files that are not part of any collection.

## Steps
1. Run `guard show`.
2. Parse:
   - Collection lines: `G|- collection: <name> (<n> files)`.
   - File lines: `G|- <path> (<collections>)`. A file is *loose* when its collection list is empty `()`.
3. Render two sections to the user. Print collections first; blank line; then loose guarded files.

## Output format

```
Collections (<n>):
  [G] <name> (<n> files)
  [-] <name> (<n> files)
  ...

Guarded files not in any collection (<total>):
  <path>
  <path>
  ...
  ... (showing 20 of <total>)
```

- Use `[G]` for guarded, `[-]` for unguarded.
- If there are no collections, print `Collections: none`.
- If there are no loose guarded files, print `Guarded files not in any collection: none`.
- For the loose-files section: show at most 20. If `total > 20`, append the `... (showing 20 of $TOTAL)` line.

## Sudo
Not needed. Read-only.
