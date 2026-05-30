#!/usr/bin/env bash
#
# Test scenarios for discover.sh git-visibility behavior.
#
# Each scenario builds an isolated throwaway repository in a temp directory,
# runs discover.sh against it, and asserts on the output. Nothing here touches
# the real project tree. Run directly:
#
#   ./plugins/progressive-disclosure/tests/test_discover.sh
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DISCOVER="$SCRIPT_DIR/../skills/analyze/scripts/discover.sh"

PASS=0
FAIL=0

# --- assertion helpers -------------------------------------------------------

assert_contains() {
  local output="$1" pattern="$2" desc="$3"
  if printf '%s\n' "$output" | grep -qF -- "$pattern"; then
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $desc"
    echo "        expected to find: $pattern"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_contains() {
  local output="$1" pattern="$2" desc="$3"
  if printf '%s\n' "$output" | grep -qF -- "$pattern"; then
    echo "  FAIL: $desc"
    echo "        did not expect to find: $pattern"
    FAIL=$((FAIL + 1))
  else
    echo "  PASS: $desc"
    PASS=$((PASS + 1))
  fi
}

# Create a fresh git repo in a temp dir, echo its path. Quiet, isolated config.
make_repo() {
  local dir
  dir="$(mktemp -d)"
  git -C "$dir" init -q
  git -C "$dir" config user.email "test@example.com"
  git -C "$dir" config user.name "Test"
  git -C "$dir" config commit.gpgsign false
  echo "$dir"
}

commit_all() {
  local dir="$1"
  git -C "$dir" add -A
  git -C "$dir" commit -q -m "snapshot" >/dev/null 2>&1
}

run_discover() {
  "$DISCOVER" "$1" 2>&1
}

CLEANUP_DIRS=()
cleanup() {
  for d in "${CLEANUP_DIRS[@]:-}"; do
    [ -n "$d" ] && rm -rf "$d"
  done
}
trap cleanup EXIT

# --- Scenario 1: untracked file is invisible ---------------------------------
echo "Scenario 1: untracked doc is invisible and its reference is flagged"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf '# Config\nSee [notes](tracked.md) and [draft](untracked.md)\n' > "$repo/CLAUDE.md"
printf '# Tracked\nbody\n' > "$repo/tracked.md"
commit_all "$repo"
printf '# Untracked draft\nbody\n' > "$repo/untracked.md"   # created, never added
out="$(run_discover "$repo")"
assert_contains "$out" "Inside git work tree" "git tracking detected"
assert_contains "$out" "DOC: tracked.md" "tracked doc is listed"
assert_not_contains "$out" "DOC: untracked.md" "untracked doc is NOT listed"
assert_contains "$out" "-> tracked.md (notes) [EXISTS]" "tracked reference marked EXISTS"
assert_contains "$out" "-> untracked.md (draft) [UNTRACKED]" "untracked reference marked UNTRACKED"
assert_contains "$out" "UNTRACKED-REF: CLAUDE.md -> untracked.md (draft)" "untracked reference flagged as issue"
assert_contains "$out" "Total documentation files: 2" "metrics count excludes untracked doc"

# --- Scenario 2: gitignored file is invisible --------------------------------
echo "Scenario 2: gitignored doc is invisible (untracked because ignored)"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf 'secret.md\n' > "$repo/.gitignore"
printf '# Config\nSee [secret](secret.md)\n' > "$repo/AGENTS.md"
commit_all "$repo"
printf '# Secret\nbody\n' > "$repo/secret.md"   # exists on disk but gitignored
out="$(run_discover "$repo")"
assert_not_contains "$out" "DOC: secret.md" "gitignored doc is NOT listed"
assert_contains "$out" "-> secret.md (secret) [UNTRACKED]" "gitignored reference marked UNTRACKED"
assert_contains "$out" "UNTRACKED-REF: AGENTS.md -> secret.md (secret)" "gitignored reference flagged as issue"

# --- Scenario 3: missing reference stays MISSING (not UNTRACKED) --------------
echo "Scenario 3: reference to a nonexistent file is MISSING, not UNTRACKED"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf '# Config\nSee [gone](nonexistent.md)\n' > "$repo/CLAUDE.md"
commit_all "$repo"
out="$(run_discover "$repo")"
assert_contains "$out" "-> nonexistent.md (gone) [MISSING]" "nonexistent reference marked MISSING"
assert_not_contains "$out" "UNTRACKED-REF: CLAUDE.md -> nonexistent.md" "missing ref is not a phantom/untracked ref"

# --- Scenario 4: untracked doc is invisible, not an orphan -------------------
echo "Scenario 4: untracked unreferenced doc is invisible, not reported as orphan"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf '# Config\n' > "$repo/CLAUDE.md"
printf '# Tracked orphan\nbody\n' > "$repo/lonely.md"   # tracked, unreferenced -> orphan
commit_all "$repo"
printf '# Untracked floater\nbody\n' > "$repo/floater.md"  # untracked, unreferenced
out="$(run_discover "$repo")"
assert_contains "$out" "ORPHAN: lonely.md" "tracked unreferenced doc IS an orphan"
assert_not_contains "$out" "ORPHAN: floater.md" "untracked unreferenced doc is NOT an orphan"

# --- Scenario 5: untracked README is not indexed (dual-role check) -----------
echo "Scenario 5: README obeys visibility rule in its indexed-content role"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf '# Config\n' > "$repo/CLAUDE.md"
commit_all "$repo"
printf '# Readme\nbody\n' > "$repo/README.md"   # untracked README
out="$(run_discover "$repo")"
assert_not_contains "$out" "DOC: README.md" "untracked README is NOT indexed as documentation"

# --- Scenario 6: non-git directory falls back to filesystem walk -------------
echo "Scenario 6: non-git directory uses filesystem fallback"
plain="$(mktemp -d)"; CLEANUP_DIRS+=("$plain")
printf '# Config\n' > "$plain/CLAUDE.md"
printf '# Plain doc\nbody\n' > "$plain/plain.md"
out="$(run_discover "$plain")"
assert_contains "$out" "Not a git repository" "non-git directory detected"
assert_contains "$out" "DOC: plain.md" "doc listed via filesystem fallback when not in git"
assert_contains "$out" "(skipped: not a git repository)" "untracked-ref section skipped outside git"

# --- Scenario 7: symlinked files are grouped as same content -----------------
echo "Scenario 7: symlinked files are reported as same content, not duplicates"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf '# Shared agent instructions\nbody\n' > "$repo/AGENTS.md"
ln -s AGENTS.md "$repo/CLAUDE.md"          # CLAUDE.md is a symlink to AGENTS.md
printf '# Standalone\nbody\n' > "$repo/standalone.md"
commit_all "$repo"
out="$(run_discover "$repo")"
assert_contains "$out" "SYMLINK: CLAUDE.md -> AGENTS.md" "symlink reported with its target"
assert_contains "$out" "SAME-CONTENT: AGENTS.md CLAUDE.md" "symlinked pair grouped as same content"
assert_not_contains "$out" "SAME-CONTENT: standalone.md" "independent file not grouped"

# --- Scenario 8: no symlinks reports (none) ----------------------------------
echo "Scenario 8: repo without symlinks reports no shared-content groups"
repo="$(make_repo)"; CLEANUP_DIRS+=("$repo")
printf '# A\nbody\n' > "$repo/a.md"
printf '# B\nbody\n' > "$repo/b.md"
commit_all "$repo"
out="$(run_discover "$repo")"
# isolate the SYMLINKS section and confirm it says (none)
sym_section="$(printf '%s\n' "$out" | awk '/=== SYMLINKS ===/{f=1} /=== REFERENCE GRAPH ===/{f=0} f')"
assert_contains "$sym_section" "(none)" "symlink section reports (none) when there are no symlinks"
assert_not_contains "$sym_section" "SAME-CONTENT:" "no same-content groups without symlinks"

# --- summary -----------------------------------------------------------------
echo ""
echo "================================"
echo "  PASS: $PASS   FAIL: $FAIL"
echo "================================"
[ "$FAIL" -eq 0 ]
