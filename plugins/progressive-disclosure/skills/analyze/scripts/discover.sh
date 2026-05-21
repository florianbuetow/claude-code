#!/usr/bin/env bash
set -uo pipefail

REPO_ROOT="${1:-.}"
cd "$REPO_ROOT"

CONFIG_FILES="README.md AGENTS.md CLAUDE.md GEMINI.md USER.md TOOLS.md BOOTSTRAP.md DESIGN.md NOTICE.md"

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
find . -name '*.md' -not -path './.git/*' -not -path './node_modules/*' -not -path './.claude/*' -not -path './vendor/*' -not -path './.venv/*' | sort | while read -r f; do
  f="${f#./}"
  lines=$(wc -l < "$f" | tr -d ' ')
  words=$(wc -w < "$f" | tr -d ' ')
  h1=$(grep -m1 '^# ' "$f" 2>/dev/null | sed 's/^# //' || echo "(no H1)")
  echo "DOC: $f | ${words}w | $h1"
done

echo ""
echo "=== REFERENCE GRAPH ==="
for cfg in $CONFIG_FILES; do
  [ -f "$cfg" ] || continue
  echo "FROM: $cfg"
  grep -oE '\[([^]]*)\]\(([^)]+\.md[^)]*)\)' "$cfg" 2>/dev/null | grep -v '://' | while read -r match; do
    target=$(echo "$match" | sed 's/.*](//' | sed 's/)//')
    label=$(echo "$match" | sed 's/\[//' | sed 's/\].*//')
    if [ -f "$target" ]; then
      echo "  -> $target ($label) [EXISTS]"
    else
      echo "  -> $target ($label) [MISSING]"
    fi
  done || true
  grep -oE '`[A-Za-z0-9_./-]+\.md`' "$cfg" 2>/dev/null | tr -d '`' | sort -u | while read -r target; do
    if [ -f "$target" ]; then
      echo "  ~> $target (backtick ref) [EXISTS]"
    else
      echo "  ~> $target (backtick ref) [MISSING]"
    fi
  done || true
  grep -oE '@[A-Za-z0-9_./-]+\.md' "$cfg" 2>/dev/null | sed 's/^@//' | sort -u | while read -r target; do
    if [ -f "$target" ]; then
      echo "  @> $target (import) [EXISTS]"
    else
      echo "  @> $target (import) [MISSING]"
    fi
  done || true
done

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

find . -name '*.md' -not -path './.git/*' -not -path './node_modules/*' -not -path './.claude/*' -not -path './vendor/*' -not -path './.venv/*' | sed 's|^\./||' | sort | while read -r f; do
  if ! grep -qxF "$f" "$refs_file" 2>/dev/null; then
    echo "ORPHAN: $f"
  fi
done

rm -f "$refs_file"

echo ""
echo "=== METRICS ==="
total_docs=$(find . -name '*.md' -not -path './.git/*' -not -path './node_modules/*' -not -path './.claude/*' -not -path './vendor/*' -not -path './.venv/*' | wc -l | tr -d ' ')
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
