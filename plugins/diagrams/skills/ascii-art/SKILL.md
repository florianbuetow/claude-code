---
name: diagrams:ascii-art
description: Draw ASCII-art / text diagrams for software documentation using extended ASCII box-drawing characters (IBM CP437 codes > 128 — single-line ┌─┐│└┘├┤┬┴┼, double-line ╔═╗║╚╝, shading ░▒▓█), never +, -, |, or /. Enforces ≤80-char width and strict row/column alignment, renders in monospaced fonts. Use when the user wants an ascii diagram, a text/box diagram, a terminal diagram, or a plain-text visualization.
disable-model-invocation: false
---

# Create ASCII Art Diagrams with Extended ASCII Characters (>128)

## Objective

Generate clean, professional ASCII art diagrams for software development documentation using
extended ASCII box-drawing characters (Unicode codes 128–255, specifically the IBM PC Code
Page 437 box-drawing set).

---

## ⚠️ Critical Requirements

1. **Use ONLY these box-drawing characters** (ASCII codes > 128 from CP437):
   - **Single-line characters**: `┌` (218), `─` (196), `┐` (191), `│` (179), `└` (192), `┘` (217), `├` (195), `┤` (180), `┬` (194), `┴` (193), `┼` (197)
   - **Double-line characters**: `╔` (201), `═` (205), `╗` (187), `║` (186), `╝` (188), `╚` (200), `╩` (202), `╦` (203), `╠` (204), `╣` (185), `╬` (206)
   - **Shading/Block**: `░` (176), `▒` (177), `▓` (178), `█` (219), `▄` (220), `▀` (223)

2. **Never use standard ASCII** (`+`, `-`, `|`, `/`) for box edges — only the extended characters above.

3. **Must render in monospaced fonts** only (terminal, VS Code, code editors).

4. **Maximum width: 80 characters** (fits standard terminal/code comments).

5. **Never use emojis — strictly forbidden.** No emoji (or any other wide / double-width / pictographic glyph) anywhere in the diagram: not in borders, not in labels, not inside boxes. Emojis render as two cells in most terminals and silently break column alignment. Use plain ASCII (codes 0–127) for all text and the box-drawing set above for structure.

---

## Character Reference Table (Copy-Paste Ready)

```
SINGLE LINE:
┌ (218) ─ (196) ┐ (191) │ (179) └ (192) ┘ (217)
├ (195) ┤ (180) ┬ (194) ┴ (193) ┼ (197)

DOUBLE LINE:
╔ (201) ═ (205) ╗ (187) ║ (186) ╝ (188) ╚ (200)
╠ (204) ╣ (185) ╦ (203) ╩ (202) ╬ (206)

SHADING:
░ (176) ▒ (177) ▓ (178) █ (219)
```

---

## Step-by-Step Instructions

### Step 1: Define Diagram Purpose

Choose one:
- [ ] System architecture (components + connections)
- [ ] Data structure (nodes, pointers, trees)
- [ ] Flowchart (decision paths, sequences)
- [ ] API/request flow (client → server → database)
- [ ] Table/grid (structured data)

### Step 2: Plan Layout

- Sketch mentally: how many boxes? What's the flow?
- Keep total width ≤ 80 chars.
- Use consistent spacing (2 spaces between components minimum).

### Step 3: Draw Boxes

Use single-line for primary boxes, double-line for highlighted/outer containers:

```
SINGLE-LINE BOX (component):
┌────────────┐
│   Label    │
└────────────┘

DOUBLE-LINE BOX (system/container):
╔════════════════╗
║  System Name   ║
╚════════════════╝
```

### Step 4: Connect Components

Use horizontal/vertical lines with proper junctions:

```
HORIZONTAL CONNECTION:
┌─────┐ ──────── ┌─────┐
│ Box │          │ Box │
└─────┘ ──────── └─────┘

VERTICAL CONNECTION:
     ┌──────┐
     │ Box  │
     │ (179)│
     │ (179)│
     └──┬───┘
        │ (179)
     ┌──┴──┐
     │ Box │
     └─────┘

JUNCTIONS (use correct corner):
├ (195) = vertical + right
┤ (180) = vertical + left
┬ (194) = horizontal + down
┴ (193) = horizontal + up
┼ (197) = cross (all 4 directions)
```

### Step 5: Add Arrows/Flow Indicators

```
Arrows:
──▶  (use ─ (196) + ▶)
├───▶
│
▼
┌───┐
```

### Step 6: Label Everything

- Every box must have a descriptive label.
- Labels centered horizontally in box.
- Use plain ASCII (codes 0–127) for text inside boxes.

### Step 7: Validate Alignment

- Check all vertical lines align (same column).
- Check all horizontal lines align (same row).
- No overlapping characters.
- Test in your terminal/editor.

### Automated connector check

Validate connector alignment with the bundled checker (self-contained, no network):

```
scripts/ascii-connector-check.sh diagram.txt      # or:  cat diagram.txt | scripts/ascii-connector-check.sh
```

It flags any connector whose open end has nothing to attach to — dangling ends, off-by-one shifts,
lines running into text, and line-weight mismatches — printing the line, column, glyph, and reason.
The connection rules it enforces are in `references/connector-rules.md`; sample diagrams and a
self-test suite live in `resources/` (run `resources/run-tests.sh`).

---

## Example Diagrams

### Example 1: System Architecture

```
╔═══════════════════════════════════════════╗
║           Microservices System            ║
╠═══════════════════════════════════════════╣
║  ┌──────────┐      ┌────────────┐         ║
║  │  Client  │ ───▶ │ API Gateway│         ║
║  └──────────┘      └────┬───────┘         ║
║                         │ (179)           ║
║              ┌──────────┼───────────┐     ║
║              │          │           │     ║
║         ┌────▼────┐ ┌───▼────┐ ┌────▼───┐ ║
║         │Service A│ │ServiceB│ │ServiceC│ ║
║         └────┬────┘ └───┬────┘ └────┬───┘ ║
║              │          │           │     ║
║              └──────────┼───────────┘     ║
║                         │ (179)           ║
║                    ┌────▼─────┐           ║
║                    │ Database │           ║
║                    └──────────┘           ║
╚═══════════════════════════════════════════╝
```

### Example 2: Data Structure (Linked List)

```
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ Node 1 │──│ Node 2 │──│ Node 3 │──│ Node 4 │
│  val:5 │  │ val:12 │  │ val:7  │  │ val:3  │
└───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘
    └───────────┴───────────┴───────────┘
               (next pointers)
```

### Example 3: API Request Flow

```
┌──────────┐     HTTP/JSON     ┌──────────────┐
│  Client  │ ─────────────────▶│ API Gateway  │
│ (Browser)│                   └──────┬───────┘
└──────────┘                          │
                                      │ (179)
                              ┌───────▼───────┐
                              │  Auth Service │
                              └───────┬───────┘
                                      │ (179)
                              ┌───────▼───────┐
                              │ User Database │
                              └───────────────┘
```

---

## Quality Checklist

Before finalizing, verify:
- ✅ All box edges use extended ASCII (codes > 128)
- ✅ No standard ASCII (`+`, `-`, `|`) for box edges
- ✅ No emojis or wide/pictographic glyphs anywhere (strictly forbidden)
- ✅ Width ≤ 80 characters
- ✅ All lines align perfectly (no gaps)
- ✅ Labels are descriptive and centered
- ✅ Arrows show direction clearly
- ✅ Renders correctly in monospaced terminal

---

## Common Pitfalls to Avoid

| ❌ Wrong     | ✅ Right        |
|-------------|-----------------|
| `+------+`  | `┌──────┐`      |
| `\| text \|`  | `│ text │`      |
| `---->`     | `───▶`          |
| Width 100+  | Width ≤ 80      |
| Mixed fonts | Monospaced only |
| Emoji in labels (🎉 ✅ ⚠) | Plain ASCII text only |

---

## Encoding Notes

- Save files as **UTF-8** (most modern terminals support this).
- On Windows CMD: use `chcp 65001` for UTF-8.
- On macOS/Linux: UTF-8 is default.
- If characters show as `?`, your terminal font doesn't support CP437/Unicode box drawing.

---

**Now create your ASCII art diagram following these instructions.** Start by defining the
diagram's purpose, then build it step-by-step using ONLY the characters from the reference table.
