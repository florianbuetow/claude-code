# create-collection

Build a collection from a description ("my test files") or an explicit file list.

## Steps
1. Find the files: use the explicit list, or Glob/Grep the repo from the description. Show the list; let the user prune. Stop if empty.
2. Check for an existing collection covering the same files (`guard show collection`, then `guard show collection "<name>"`). If there's a strong overlap, ask: update that one or create a new one? Suggest a name; let the user override.
3. Create and fill (no sudo):
   - `guard create "<name>"`
   - `guard update "<name>" add "<file1>" "<file2>" …`
4. Show `guard show collection "<name>"`.

## Protecting them
Creating a collection only registers the files; it does not lock them. To actually guard them, print for the user to run:

```
sudo guard enable collection "<name>"
```
