#!/usr/bin/env bash
#
# ascii-connector-check.sh — scan an ASCII-art / box-drawing diagram and flag
# connectors whose open ends have no matching connector to attach to. Catches
# dangling line ends and the classic off-by-one alignment error (a vertical that
# stops one cell short of the corner below it).
#
# It also flags any emoji / wide (non-ASCII, non-box-drawing) glyph found
# ANYWHERE in the input — border, label, or inside a box. Emoji are strictly
# forbidden in ascii-art diagrams: they render as two terminal cells and silently
# break the monospace column alignment the box-drawing glyphs depend on.
#
# The connection rules it enforces are documented in
# ../references/connector-rules.md.
#
# Usage:
#   ./ascii-connector-check.sh [--box-only] [FILE]
#   cat diagram.txt | ./ascii-connector-check.sh [--box-only]
#
# Options:
#   -b, --box-only   Treat only Unicode box-drawing glyphs and arrowheads as
#                    connectors; ignore ASCII - = | + (use this when a diagram
#                    draws structure with box glyphs and uses ASCII for labels,
#                    to avoid flagging hyphens/pipes inside text). Emoji are
#                    flagged regardless of this option.
#   -h, --help       Show this help and exit.
#
# Output (one line per violation):
#   in line L col C the connector 'G' does not have a <left|right|top|bottom>
#   connector to attach to — found <reason>
#
# Exit status:
#   0  no violations
#   1  violations found
#   2  usage error or I/O error
#
# Requires: bash (3.2+) and standard POSIX tools only. No python, no awk.
# Character columns are reported using bash's multibyte-aware ${#s} / ${s:i:1},
# so a UTF-8 locale is needed (the script sets one if the environment lacks it).

set -u

# Ensure a UTF-8 locale so ${#s} counts characters and ${s:i:1} indexes by
# character (otherwise box-drawing glyphs would be split mid-byte).
case "${LC_ALL:-}${LC_CTYPE:-}${LANG:-}" in
  *UTF-8* | *UTF8* | *utf8*) : ;;
  *) export LC_ALL="C.UTF-8" ;;
esac

usage() {
  cat <<'EOF'
Usage:
  ascii-connector-check.sh [--box-only] [FILE]
  cat diagram.txt | ascii-connector-check.sh [--box-only]

Flags box-drawing / ASCII connectors whose open ends have nothing to attach to,
and any emoji / non-ASCII glyph found anywhere (emoji are forbidden in diagrams).

Options:
  -b, --box-only   Ignore ASCII - = | + (only box-drawing glyphs and arrows).
                   Emoji are flagged regardless of this option.
  -h, --help       Show this help.

Exit: 0 = clean, 1 = violations found, 2 = usage/IO error.
EOF
}

mode="all"
file=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    -b | --box-only) mode="box"; shift ;;
    -h | --help) usage; exit 0 ;;
    --) shift; if [ "$#" -gt 0 ]; then file="$1"; fi; break ;;
    -*) printf 'error: unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *) file="$1"; shift ;;
  esac
done

# --- read the whole diagram into lines[] ---------------------------------------
if [ -n "$file" ]; then
  if [ ! -f "$file" ]; then
    printf 'error: not a readable file: %s\n' "$file" >&2
    exit 2
  fi
  exec < "$file"
fi

lines=()
_line=""
while IFS= read -r _line || [ -n "$_line" ]; do
  lines+=("$_line")
  _line=""
done
nlines=${#lines[@]}

# --- glyph tables --------------------------------------------------------------
# set_ends <char> -> EOUT = space-separated "DIR:WEIGHT" tokens.
# DIR is L|R|U|D (left/right/up/down open end); WEIGHT is S(ingle) D(ouble) A(ny).
EOUT=""
set_ends() {
  case "$1" in
    '─') EOUT="L:S R:S" ;;
    '│') EOUT="U:S D:S" ;;
    '┌') EOUT="R:S D:S" ;;
    '┐') EOUT="L:S D:S" ;;
    '└') EOUT="R:S U:S" ;;
    '┘') EOUT="L:S U:S" ;;
    '├') EOUT="U:S D:S R:S" ;;
    '┤') EOUT="U:S D:S L:S" ;;
    '┬') EOUT="L:S R:S D:S" ;;
    '┴') EOUT="L:S R:S U:S" ;;
    '┼') EOUT="L:S R:S U:S D:S" ;;
    '═') EOUT="L:D R:D" ;;
    '║') EOUT="U:D D:D" ;;
    '╔') EOUT="R:D D:D" ;;
    '╗') EOUT="L:D D:D" ;;
    '╚') EOUT="R:D U:D" ;;
    '╝') EOUT="L:D U:D" ;;
    '╠') EOUT="U:D D:D R:D" ;;
    '╣') EOUT="U:D D:D L:D" ;;
    '╦') EOUT="L:D R:D D:D" ;;
    '╩') EOUT="L:D R:D U:D" ;;
    '╬') EOUT="L:D R:D U:D D:D" ;;
    '▶' | '→') EOUT="L:A" ;;
    '◀' | '←') EOUT="R:A" ;;
    '▲' | '↑') EOUT="D:A" ;;
    '▼' | '↓') EOUT="U:A" ;;
    '-' | '=') if [ "$mode" = "box" ]; then EOUT=""; else EOUT="L:A R:A"; fi ;;
    '|') if [ "$mode" = "box" ]; then EOUT=""; else EOUT="U:A D:A"; fi ;;
    '+') if [ "$mode" = "box" ]; then EOUT=""; else EOUT="L:A R:A U:A D:A"; fi ;;
    *) EOUT="" ;;
  esac
}

# Allowed non-ASCII glyphs (connectors + arrows + shading). Any other non-ASCII
# character is forbidden (emoji / wide / symbol).
is_allowed_glyph() {
  case "$1" in
    '─' | '│' | '┌' | '┐' | '└' | '┘' | '├' | '┤' | '┬' | '┴' | '┼') return 0 ;;
    '═' | '║' | '╔' | '╗' | '╚' | '╝' | '╠' | '╣' | '╦' | '╩' | '╬') return 0 ;;
    '▶' | '◀' | '▲' | '▼' | '→' | '←' | '↑' | '↓') return 0 ;;
    '░' | '▒' | '▓' | '█' | '▄' | '▀') return 0 ;;
    *) return 1 ;;
  esac
}

# Byte length of one character (C locale counts bytes); BLEN <= 1 means ASCII.
BLEN=0
set_blen() { local LC_ALL=C; BLEN=${#1}; }

# CELL / CELLOOB: character at (row,col), or out-of-bounds flag. Set via a global
# (not command substitution) so a space cell is not lost to whitespace trimming.
CELL=""
CELLOOB=0
cell() {
  CELL=""; CELLOOB=0
  if [ "$1" -lt 0 ] || [ "$1" -ge "$nlines" ]; then CELLOOB=1; return; fi
  local row="${lines[$1]}"
  if [ "$2" -lt 0 ] || [ "$2" -ge "${#row}" ]; then CELLOOB=1; return; fi
  CELL="${row:$2:1}"
}

compat() { [ "$1" = "A" ] || [ "$2" = "A" ] || [ "$1" = "$2" ]; }

# --- scan ----------------------------------------------------------------------
violations=0
r=0
while [ "$r" -lt "$nlines" ]; do
  line="${lines[$r]}"
  len=${#line}
  c=0
  while [ "$c" -lt "$len" ]; do
    ch="${line:$c:1}"
    set_ends "$ch"
    ends="$EOUT"

    if [ -z "$ends" ]; then
      # not a connector: flag it only if it's a forbidden non-ASCII glyph
      if ! is_allowed_glyph "$ch"; then
        set_blen "$ch"
        if [ "$BLEN" -gt 1 ]; then
          printf "in line %d col %d the character '%s' is forbidden — emoji and other non-ASCII glyphs break monospace alignment (only ASCII text and the box-drawing/arrow/shading set are allowed)\n" \
            "$((r + 1))" "$((c + 1))" "$ch"
          violations=$((violations + 1))
        fi
      fi
      c=$((c + 1))
      continue
    fi

    # connector: every open end must meet a complementary end of compatible weight
    for tok in $ends; do
      d="${tok%%:*}"
      w="${tok#*:}"
      case "$d" in
        L) nr=$r; nc=$((c - 1)); o="R"; dn="left"; on="right" ;;
        R) nr=$r; nc=$((c + 1)); o="L"; dn="right"; on="left" ;;
        U) nr=$((r - 1)); nc=$c; o="D"; dn="top"; on="bottom" ;;
        D) nr=$((r + 1)); nc=$c; o="U"; dn="bottom"; on="top" ;;
      esac

      cell "$nr" "$nc"
      ok=0
      reason=""
      if [ "$CELLOOB" = "1" ]; then
        reason="the edge of the diagram"
      elif [ "$CELL" = " " ]; then
        reason="a space"
      else
        set_ends "$CELL"
        if [ -z "$EOUT" ]; then
          reason="the character '$CELL'"
        else
          nbw=""
          for nt in $EOUT; do
            case "$nt" in "$o":*) nbw="${nt#*:}"; break ;; esac
          done
          if [ -z "$nbw" ]; then
            reason="'$CELL' (no $on open end)"
          elif ! compat "$w" "$nbw"; then
            reason="'$CELL' (line-weight mismatch)"
          else
            ok=1
          fi
        fi
      fi

      if [ "$ok" = "0" ]; then
        printf "in line %d col %d the connector '%s' does not have a %s connector to attach to — found %s\n" \
          "$((r + 1))" "$((c + 1))" "$ch" "$dn" "$reason"
        violations=$((violations + 1))
      fi
    done
    c=$((c + 1))
  done
  r=$((r + 1))
done

[ "$violations" -gt 0 ] && exit 1
exit 0
