#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

CONFIG_FILES="README.md AGENTS.md CLAUDE.md GEMINI.md USER.md TOOLS.md BOOTSTRAP.md DESIGN.md NOTICE.md"

# Determine whether we are inside a git work tree. When we are, only
# git-tracked files count as "visible"; untracked and gitignored files are
# treated as non-existent for the purposes of this audit. Git never applies
# ignore rules to an already-tracked file, so a single "is it tracked?" check
# satisfies both conditions: visible <=> tracked.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_REPO=1
else
  GIT_REPO=0
fi

# Enumerate visible markdown files, one per line, as paths relative to the
# current directory without a leading "./". In a git repo this is the set of
# tracked .md files; otherwise it falls back to a filtered filesystem walk.
list_visible_md() {
  if [ "$GIT_REPO" -eq 1 ]; then
    git ls-files --cached -- '*.md' | sort -u
  else
    find . -name '*.md' \
      -not -path './.git/*' \
      -not -path './node_modules/*' \
      -not -path './.claude/*' \
      -not -path './vendor/*' \
      -not -path './.venv/*' | sed 's|^\./||' | sort -u
  fi
}

# Canonical location of a path, following one level of symlink and resolving
# the directory to its physical form. Two paths that print the same value are
# the same underlying file (e.g. a symlink and its target). Portable: relies
# only on dirname/basename/readlink/cd/pwd, not on stat or realpath flags.
canon() {
  local p="$1" d b t
  if [ -L "$p" ]; then
    t=$(readlink "$p")
    case "$t" in
      /*) p="$t" ;;
      *)  p="$(dirname "$p")/$t" ;;
    esac
  fi
  d=$(dirname "$p")
  b=$(basename "$p")
  ( cd "$d" 2>/dev/null && printf '%s/%s\n' "$(pwd -P)" "$b" ) || printf '%s\n' "$p"
}

# Classify a referenced path. Prints one of:
#   MISSING   - no such file on disk
#   UNTRACKED - file exists on disk but is invisible to git (untracked/ignored)
#   EXISTS    - file is present and visible
# The MISSING check runs first, so paths with anchors/fragments
# (docs/foo.md#section) short-circuit before reaching the git check.
ref_state() {
  local target="$1"
  if [ ! -f "$target" ]; then
    echo "MISSING"
    return
  fi
  if [ "$GIT_REPO" -eq 1 ] && ! git ls-files --error-unmatch -- "$target" >/dev/null 2>&1; then
    echo "UNTRACKED"
    return
  fi
  echo "EXISTS"
}

echo "=== GIT TRACKING ==="
if [ "$GIT_REPO" -eq 1 ]; then
  echo "Inside git work tree: only tracked files are visible (untracked and gitignored files are treated as non-existent)"
else
  echo "Not a git repository: all matching files are included"
fi

echo ""
echo "=== ROOT CONFIGURATION FILES ==="
for f in $CONFIG_FILES; do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f" | tr -d ' ')
    words=$(wc -w < "$f" | tr -d ' ')
    echo "FOUND: $f (${lines} lines, ${words} words)"
  fi
done

echo ""
echo "=== DOCUMENTATION FILES ==="
list_visible_md | while read -r f; do
  lines=$(wc -l < "$f" | tr -d ' ')
  words=$(wc -w < "$f" | tr -d ' ')
  h1=$(grep -m1 '^# ' "$f" 2>/dev/null | sed 's/^# //' || echo "(no H1)")
  echo "DOC: $f | ${words}w | $h1"
done

echo ""
echo "=== SYMLINKS ==="
echo "Markdown files that are symbolic links, and groups of files that resolve"
echo "to the same underlying file. Files in a SAME-CONTENT group are NOT"
echo "duplicates — they are one file under multiple names; never flag them as"
echo "duplicate content."
sym_tmp=$(mktemp)
canon_tmp=$(mktemp)
list_visible_md | while read -r f; do
  [ -L "$f" ] && echo "SYMLINK: $f -> $(readlink "$f")" >> "$sym_tmp"
  printf '%s\t%s\n' "$(canon "$f")" "$f" >> "$canon_tmp"
done
sort "$canon_tmp" -o "$canon_tmp"
groups_tmp=$(mktemp)
cut -f1 "$canon_tmp" | uniq -d | while read -r key; do
  members=$(awk -F'\t' -v k="$key" '$1 == k { print $2 }' "$canon_tmp" | paste -sd' ' -)
  echo "SAME-CONTENT: $members" >> "$groups_tmp"
done
if [ -s "$sym_tmp" ] || [ -s "$groups_tmp" ]; then
  [ -s "$sym_tmp" ] && cat "$sym_tmp"
  [ -s "$groups_tmp" ] && cat "$groups_tmp"
else
  echo "(none)"
fi
rm -f "$sym_tmp" "$canon_tmp" "$groups_tmp"

echo ""
echo "=== REFERENCE GRAPH ==="
untracked_refs=$(mktemp)
for cfg in $CONFIG_FILES; do
  [ -f "$cfg" ] || continue
  echo "FROM: $cfg"
  grep -oE '\[([^]]*)\]\(([^)]+\.md[^)]*)\)' "$cfg" 2>/dev/null | grep -v '://' | while read -r match; do
    target=$(echo "$match" | sed 's/.*](//' | sed 's/)//')
    label=$(echo "$match" | sed 's/\[//' | sed 's/\].*//')
    state=$(ref_state "$target")
    echo "  -> $target ($label) [$state]"
    [ "$state" = "UNTRACKED" ] && echo "$cfg -> $target ($label)" >> "$untracked_refs"
  done || true
  grep -oE '`[A-Za-z0-9_./-]+\.md`' "$cfg" 2>/dev/null | tr -d '`' | sort -u | while read -r target; do
    state=$(ref_state "$target")
    echo "  ~> $target (backtick ref) [$state]"
    [ "$state" = "UNTRACKED" ] && echo "$cfg ~> $target (backtick ref)" >> "$untracked_refs"
  done || true
  grep -oE '@[A-Za-z0-9_./-]+\.md' "$cfg" 2>/dev/null | sed 's/^@//' | sort -u | while read -r target; do
    state=$(ref_state "$target")
    echo "  @> $target (import) [$state]"
    [ "$state" = "UNTRACKED" ] && echo "$cfg @> $target (import)" >> "$untracked_refs"
  done || true
done

echo ""
echo "=== UNTRACKED REFERENCES ==="
echo "References from root configuration files to files that exist on disk but"
echo "are invisible to git (untracked or gitignored). Each is a phantom"
echo "reference: either remove the reference or add the file to git."
if [ "$GIT_REPO" -eq 0 ]; then
  echo "(skipped: not a git repository)"
elif [ -s "$untracked_refs" ]; then
  sort -u "$untracked_refs" | while read -r line; do
    echo "UNTRACKED-REF: $line"
  done
else
  echo "(none)"
fi
rm -f "$untracked_refs"

echo ""
echo "=== ORPHAN DETECTION ==="
refs_file=$(mktemp)
for cfg in $CONFIG_FILES; do
  [ -f "$cfg" ] || continue
  grep -oE '\[([^]]*)\]\(([^)]+\.md[^)]*)\)' "$cfg" 2>/dev/null | grep -v '://' | sed 's/.*](//' | sed 's/)//' >> "$refs_file" || true
  grep -oE '`[A-Za-z0-9_./-]+\.md`' "$cfg" 2>/dev/null | tr -d '`' >> "$refs_file" || true
  grep -oE '@[A-Za-z0-9_./-]+\.md' "$cfg" 2>/dev/null | sed 's/^@//' >> "$refs_file" || true
done
for f in $CONFIG_FILES; do
  echo "$f" >> "$refs_file"
done
sort -u "$refs_file" -o "$refs_file"

list_visible_md | while read -r f; do
  if ! grep -qxF "$f" "$refs_file" 2>/dev/null; then
    echo "ORPHAN: $f"
  fi
done

rm -f "$refs_file"

echo ""
echo "=== METRICS ==="
total_docs=$(list_visible_md | wc -l | tr -d ' ')
config_count=0
for f in $CONFIG_FILES; do
  [ -f "$f" ] && config_count=$((config_count + 1))
done
echo "Total documentation files: $total_docs"
echo "Root configuration files present: $config_count"
if [ -f AGENTS.md ]; then
  words=$(wc -w < AGENTS.md | tr -d ' ')
  echo "AGENTS.md word count: $words (recommended: <1500)"
fi
if [ -f CLAUDE.md ]; then
  lines=$(wc -l < CLAUDE.md | tr -d ' ')
  words=$(wc -w < CLAUDE.md | tr -d ' ')
  echo "CLAUDE.md: ${lines} lines, ${words} words (recommended: <300 lines)"
fi
