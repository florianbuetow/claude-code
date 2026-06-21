# diagrams

A diagramming toolkit for Claude Code. A **router skill** takes a "draw X" request, picks the right
diagram format, and dispatches to a format-specific skill.

## Skills

| Skill | Purpose |
|-------|---------|
| `/diagrams` | Router — detects the requested format and routes to the skill below. |
| `/diagrams:ascii-art` | Text/box-drawing diagrams that render inline (terminal or code block). |
| `/diagrams:mermaid` | Mermaid diagrams (flowchart, sequence, class, ER, state, gantt) for Markdown/docs rendering. |
| `/diagrams:wardley` | Wardley maps in the WTG2 (wardleyToGo) DSL, emitted as `.wtg2` (renders to SVG via `wtg2svg`). |

## ascii-art rules

The ASCII-art skill enforces rules that keep text diagrams clean:

1. **Extended ASCII box-drawing only (CP437 codes > 128), never `+`, `-`, `|`, or `/`.** Draw with
   `┌ ┐ └ ┘ ─ │` and joins `├ ┤ ┬ ┴ ┼`, double-line `╔ ═ ╗ ║ ╚ ╝` for highlighted/outer
   containers, and shading `░ ▒ ▓ █` — not ASCII punctuation.
2. **Maximum width 80 characters**, monospaced fonts only.
3. **Strict alignment.** Verticals must share a column and horizontals a row — the most common
   failure is a line drifting off by a cell; the skill makes alignment a final validation step.

## Adding a format

Add a `skills/<format>/SKILL.md` with a sharp `description:` (that is what triggers routing), then
add a row to the detection table in `skills/diagrams/SKILL.md`.

## Status

Infrastructure and all three skills (`ascii-art`, `mermaid`, `wardley`) are complete.
