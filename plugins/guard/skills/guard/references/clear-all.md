# clear-all

Restore every tracked file, empty the registry, keep the config (mode/owner/group).

## Steps
1. `guard show`. If nothing is tracked, stop.
2. If any file is guarded, the immutable flags must be cleared as root first. Print for the user to run:
   ```
   sudo guard reset
   ```
   `reset` disables all guarded files but keeps them registered.
3. After reset (or if nothing was guarded), wipe the registry without sudo:
   - `guard destroy "<name>"` for each collection
   - `guard remove file "<path>"` for each remaining file
   - `guard cleanup`
4. Confirm: `guard show` is empty, `guard config show` still shows the original mode/owner/group.
