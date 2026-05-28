# init

Create a `.guardfile` in the current directory.

## Defaults
- Mode `0750` — owner full, group read+execute (so the user keeps r-x on guarded files), others nothing.
- Owner `$(id -nu 0)` — the super-user (`root`).
- Group `$(id -ng)` — the current user's group.

## Steps
1. If `.guardfile` already exists, show `guard config show` and stop (don't overwrite).
2. `guard init 0750 "$(id -nu 0)" "$(id -ng)"`. No sudo.
3. Show `guard config show`.
