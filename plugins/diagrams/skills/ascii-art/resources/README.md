# ascii-connector-check test fixtures

Sample diagrams for exercising `../scripts/ascii-connector-check.sh`. Run the whole suite:

```
./run-tests.sh
```

It runs the checker against every fixture in `fixtures/` and asserts the expected exit code and
violation count. Exit 0 = all fixtures behaved as expected.

To run the checker against one fixture by hand:

```
../scripts/ascii-connector-check.sh fixtures/invalid-offbyone.txt
cat fixtures/invalid-offbyone.txt | ../scripts/ascii-connector-check.sh
```

## Valid fixtures (expect exit 0, no output)

| Fixture | What it proves |
|---------|----------------|
| `valid-single-box.txt` | A closed single-line box — every end meets a complementary end. |
| `valid-double-box.txt` | Same for double-line glyphs (`╔ ═ ╗ ║ ╚ ╝`). |
| `valid-tee-junctions.txt` | The **correct** way to join two boxes: `├───┤` (tees expose the horizontal ends the walls lack). |
| `valid-arrows.txt` | Arrowheads (`◀ ▶ ▼`) act as line terminators and connect cleanly. |
| `valid-ascii-cross.txt` | ASCII connectors `= | +` with arrowheads, fully connected (recognised in default mode). |

## Invalid fixtures (expect exit 1)

Each row shows the exact output the checker produces.

**`invalid-offbyone.txt`** — bottom row shifted one space right (the classic alignment bug):
```
in line 2 col 1 the connector '│' does not have a bottom connector to attach to — found a space
in line 2 col 4 the connector '│' does not have a bottom connector to attach to — found '─' (no top open end)
in line 3 col 2 the connector '└' does not have a top connector to attach to — found a space
in line 3 col 5 the connector '┘' does not have a top connector to attach to — found the edge of the diagram
```

**`invalid-into-text.txt`** — a horizontal line running into letters:
```
in line 1 col 2 the connector '─' does not have a left connector to attach to — found the character 'A'
in line 1 col 6 the connector '─' does not have a right connector to attach to — found the character 'B'
```

**`invalid-weight-mismatch.txt`** — a single line meeting a double line (`◀─═▶`):
```
in line 1 col 2 the connector '─' does not have a right connector to attach to — found '═' (line-weight mismatch)
in line 1 col 3 the connector '═' does not have a left connector to attach to — found '─' (line-weight mismatch)
```

**`invalid-wall-attach.txt`** — `│──│` butts a horizontal line against a vertical wall instead of using
tees. Kept strict by design (compare `valid-tee-junctions.txt`):
```
in line 2 col 6 the connector '─' does not have a left connector to attach to — found '│' (no right open end)
in line 2 col 7 the connector '─' does not have a right connector to attach to — found '│' (no left open end)
```

**`invalid-bare-equals.txt`** — a lone `=` in text (`x = y`); produces the canonical message:
```
in line 1 col 3 the connector '=' does not have a left connector to attach to — found a space
in line 1 col 3 the connector '=' does not have a right connector to attach to — found a space
```

**`invalid-emoji.txt`** — a box that is character-aligned but contains an emoji. The connector
checks pass, but the emoji is flagged outright (this is exactly why emoji are forbidden: they slip
past character alignment yet break *visual* alignment). Flagged in **both** default and `--box-only`
mode:
```
in line 2 col 3 the character '🎉' is forbidden — emoji and other non-ASCII glyphs break monospace alignment (only ASCII text and the box-drawing/arrow/shading set are allowed)
```

## Dual-mode fixture

`label-hyphen.txt` is a box-drawing box whose label contains an ASCII hyphen (`│ a-b test│`). It shows
why `--box-only` exists:

- **default mode** → exit 1: the `-` inside the word is treated as a connector and flagged.
  ```
  in line 2 col 4 the connector '-' does not have a left connector to attach to — found the character 'a'
  in line 2 col 4 the connector '-' does not have a right connector to attach to — found the character 'b'
  ```
- **`--box-only`** → exit 0: ASCII `- = | +` are ignored, so the label is left alone and the box is clean.

See `../references/connector-rules.md` for the full rule set these fixtures exercise.
