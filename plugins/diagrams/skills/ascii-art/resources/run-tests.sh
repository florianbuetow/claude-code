#!/usr/bin/env bash
#
# run-tests.sh — run ascii-connector-check.sh against the fixtures in ./fixtures
# and assert the expected exit code and violation count for each.
#
# Usage: ./run-tests.sh
# Exit:  0 if every fixture matches its expectation, 1 otherwise.

set -u

here="$(cd "$(dirname "$0")" && pwd)"
check="$here/../scripts/ascii-connector-check.sh"
fixtures="$here/fixtures"

if [ ! -f "$check" ]; then
  printf 'error: checker not found at %s\n' "$check" >&2
  exit 2
fi
[ -x "$check" ] || chmod +x "$check" 2>/dev/null || true

# file | mode | expected_exit | expected_violation_count
manifest='
valid-single-box.txt|default|0|0
valid-double-box.txt|default|0|0
valid-tee-junctions.txt|default|0|0
valid-arrows.txt|default|0|0
valid-ascii-cross.txt|default|0|0
invalid-offbyone.txt|default|1|4
invalid-into-text.txt|default|1|2
invalid-weight-mismatch.txt|default|1|2
invalid-wall-attach.txt|default|1|2
invalid-bare-equals.txt|default|1|2
label-hyphen.txt|default|0|0
label-hyphen.txt|box-only|0|0
invalid-emoji.txt|default|1|1
invalid-emoji.txt|box-only|1|1
valid-arrow-in-border.txt|default|0|0
valid-arrow-in-border.txt|box-only|0|0
valid-arrow-in-double-border.txt|default|0|0
valid-arrow-in-double-border.txt|box-only|0|0
valid-label-punct.txt|default|0|0
valid-label-punct.txt|box-only|0|0
'

pass=0
fail=0
printf '%-26s %-9s %-5s %-5s %s\n' "FIXTURE" "MODE" "EXIT" "VIOL" "RESULT"
printf -- '----------------------------------------------------------------\n'

while IFS='|' read -r file mode exp_exit exp_n; do
  [ -z "${file:-}" ] && continue
  if [ "$mode" = "box-only" ]; then
    out="$("$check" --box-only "$fixtures/$file" 2>&1)"; rc=$?
  else
    out="$("$check" "$fixtures/$file" 2>&1)"; rc=$?
  fi
  if [ -z "$out" ]; then n=0; else n="$(printf '%s\n' "$out" | grep -c .)"; fi
  if [ "$rc" = "$exp_exit" ] && [ "$n" = "$exp_n" ]; then
    printf '%-26s %-9s %-5s %-5s %s\n' "$file" "$mode" "$rc" "$n" "PASS"
    pass=$((pass + 1))
  else
    printf '%-26s %-9s %-5s %-5s %s\n' "$file" "$mode" "$rc" "$n" "FAIL (want exit=$exp_exit viol=$exp_n)"
    [ -n "$out" ] && printf '    | %s\n' "$out"
    fail=$((fail + 1))
  fi
done <<EOF
$manifest
EOF

echo
echo "passed=$pass failed=$fail"
[ "$fail" -eq 0 ]
