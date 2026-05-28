# remove-collection

Remove a collection.

## Steps
1. List collections (`guard show collection`); confirm which one.
2. Check its files with `guard show collection "<name>"` — are any guarded (line starts with `G`)?
3. **None guarded:** `guard destroy "<name>"` directly.
4. **Any guarded:** print for the user to run as root:
   ```
   sudo guard disable collection "<name>"
   guard destroy "<name>"
   ```
5. Confirm with `guard show collection "<name>"` (should be gone).

Note: `guard destroy` removes the collection but leaves its files registered. To also unregister them, `guard remove file "<path>"` each (needs sudo only if the file is still guarded).
