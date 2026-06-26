# ASCII / Box-Drawing Connector Rules

These rules define **which connectors may attach to which**, in each direction. They are the spec
implemented by `scripts/ascii-connector-check.sh`.

## Model: open ends

Every connector glyph has a set of **open ends** — the directions in which it expects to join a
neighbour. Each open end has a **weight**:

- `S` — single line
- `D` — double line
- `*` — any (ASCII connectors and arrowheads connect regardless of weight)

Directions are **left (L)**, **right (R)**, **top (U)**, **bottom (D)**.

### Open-ends table

| Glyph | Open ends (dir=weight) | | Glyph | Open ends |
|-------|------------------------|---|-------|-----------|
| `─` | L=S, R=S | | `═` | L=D, R=D |
| `│` | U=S, D=S | | `║` | U=D, D=D |
| `┌` | R=S, D=S | | `╔` | R=D, D=D |
| `┐` | L=S, D=S | | `╗` | L=D, D=D |
| `└` | R=S, U=S | | `╚` | R=D, U=D |
| `┘` | L=S, U=S | | `╝` | L=D, U=D |
| `├` | U=S, D=S, R=S | | `╠` | U=D, D=D, R=D |
| `┤` | U=S, D=S, L=S | | `╣` | U=D, D=D, L=D |
| `┬` | L=S, R=S, D=S | | `╦` | L=D, R=D, D=D |
| `┴` | L=S, R=S, U=S | | `╩` | L=D, R=D, U=D |
| `┼` | L=S, R=S, U=S, D=S | | `╬` | L=D, R=D, U=D, D=D |

**Arrowheads (terminators — exactly one open end, any weight):**

| Glyph | Open end | | Glyph | Open end |
|-------|----------|---|-------|----------|
| `▶` `→` | L=* | | `◀` `←` | R=* |
| `▲` `↑` | D=* | | `▼` `↓` | U=* |

An arrowhead caps the end of a line, so it attaches *back toward* that line: `▶`/`→` attach to a
connector on their **left**, `◀`/`←` on their **right**, `▲`/`↑` **below** them, `▼`/`↓` **above**.

**Arrowhead embedded in a border (pass-through).** The skill's idiom draws an arrow flowing into a
box by embedding the arrowhead directly in the box's border line — `┌────▼────┐` (and the double-line
form `╔════▼════╗`). The `─`/`═` cells on either side of the arrowhead would otherwise dangle, because
the arrowhead has no left/right open end. So a **vertical** arrowhead (`▲ ▼ ↑ ↓`) sitting in a
**horizontal** border line *satisfies* that line's left/right open ends (it passes the line through),
and a **horizontal** arrowhead (`▶ ◀ → ←`) does the same for a **vertical** border's top/bottom ends.
The arrowhead still attaches its own single open end as usual (the `▼` in `┌────▼────┐` still needs a
line above it). This makes the bundled checker accept the construction the skill's Examples 1 and 3
teach. Note an arrowhead at the very top/edge of a diagram whose shaft runs off the grid is still
flagged — that is a genuine dangling end, not the border idiom.

**ASCII connectors (weight `*` — recognised by default, suppressed with `--box-only`):**

| Glyph | Open ends |
|-------|-----------|
| `-` `=` | L=*, R=* |
| `\|` | U=*, D=* |
| `+` | L=*, R=*, U=*, D=* |

## The connection rule

Two adjacent cells **connect** iff each has a complementary open end pointing at the other, with
compatible weight:

- the glyph's **right** end (R) requires the cell to its right to have a **left** end (L);
- the glyph's **left** end (L) requires the cell to its left to have a **right** end (R);
- the glyph's **top** end (U) requires the cell above to have a **bottom** end (D);
- the glyph's **bottom** end (D) requires the cell below to have a **top** end (U).

**Weight compatibility:** `S` connects to `S`, `D` connects to `D`, and `*` connects to anything.
So a single line never joins a double line cleanly (`─` beside `═` is a weight mismatch), but an
ASCII `=` or an arrowhead joins either.

## Which glyph may sit in each direction (derived adjacency)

A glyph with a **right** open end may be followed (to its right) by any glyph that has a **left**
open end of compatible weight — i.e. one of the **"has-left-end"** set below. The other three
directions work the same way against the matching set.

- **Has a LEFT open end** (may sit to the *right* of an R-end):
  - single: `─ ┐ ┘ ┤ ┬ ┴ ┼`
  - double: `═ ╗ ╝ ╣ ╦ ╩ ╬`
  - any: `- = + → ▶`
- **Has a RIGHT open end** (may sit to the *left* of an L-end):
  - single: `─ ┌ └ ├ ┬ ┴ ┼`
  - double: `═ ╔ ╚ ╠ ╦ ╩ ╬`
  - any: `- = + ← ◀`
- **Has a TOP open end** (may sit *below* a U-end):
  - single: `│ └ ┘ ├ ┤ ┴ ┼`
  - double: `║ ╚ ╝ ╠ ╣ ╩ ╬`
  - any: `| + ↑ ▲`
- **Has a BOTTOM open end** (may sit *above* a D-end):
  - single: `│ ┌ ┐ ├ ┤ ┬ ┼`
  - double: `║ ╔ ╗ ╠ ╣ ╦ ╬`
  - any: `| + ↓ ▼`

## What counts as a violation

For each open end of each connector, the checker looks at the neighbour cell in that direction.
It is a **violation** when that neighbour:

1. is **the edge of the diagram** (the end dangles off the grid), or
2. is **a space** (the line stops short — the classic off-by-one alignment error), or
3. is **a non-connector character** (a letter, digit, punctuation), or
4. is a connector that **lacks the complementary open end** (e.g. `─` to the left of `│`), or
5. is a connector whose end is the **wrong weight** (`─` meeting `═`).

A glyph is only ever checked on the directions in which *it* has an open end — so a vertical `│`
is never faulted for what sits to its left or right, only for what is above and below it. This is
why text inside a box (`│ Label │`) raises no violations: the wall glyphs only care about their
top/bottom neighbours.

## Forbidden glyphs: emoji and wide characters

Emoji and other wide / double-width or pictographic glyphs are **forbidden anywhere** in a diagram
(border, label, or inside a box) and are flagged unconditionally — independent of `--box-only`. They
render as two terminal cells, which silently breaks the monospace column alignment box-drawing
depends on. **Detected by allowlist:** any **non-ASCII** character (UTF-8 byte length greater than
1) that is **not** one of the permitted box-drawing / arrow / shading glyphs is forbidden. This
catches emoji, wide CJK, and stray symbols alike, needs no Unicode-codepoint tables, and is exactly
the skill's rule ("only these glyphs, plus plain ASCII text"). Plain ASCII characters (byte length
1) are never flagged.

## Known limitations

- ASCII `- = | +` also occur **inside text** (`general-purpose`, `key=value`, `a|b`, `1+2`). In
  default mode the checker treats such a glyph as **label text, not wiring**, when it sits inside a
  horizontal text run — i.e. a non-space, non-connector character (a letter, digit, or stray
  punctuation such as `>` `.`) is immediately to its left or right. So hyphenated/`=`-bearing labels no
  longer raise false positives. A bare ASCII connector flanked by spaces or other connectors (the
  dangling `x = y`, or ASCII-drawn wiring like `◀=+=▶`) is still checked. `--box-only` remains
  available to ignore ASCII `- = | +` entirely for diagrams that draw all structure with box glyphs.
- Columns are reported as 1-based **character** positions; this assumes single-width glyphs and
  spaces (not tabs) for indentation.
- Shading blocks `░ ▒ ▓ █` are treated as non-connectors, so a line ending into a block is flagged.
