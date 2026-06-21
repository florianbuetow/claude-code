---
name: diagrams
description: Router for the diagrams plugin — pick the right diagram format and dispatch to its skill. Routes to ascii-art (text/box-drawing diagrams), mermaid (flowcharts, sequence, class, state, ER, gantt), or wardley (Wardley maps in markdown). Use when the user says "draw a diagram", "diagram this", "make a chart", "visualize this as a diagram", "ascii diagram", "mermaid diagram", or "wardley map".
disable-model-invocation: false
---

# Diagrams: Router

Auto-detect the requested diagram format from the user's request and dispatch to the matching skill.

The user's request is:
"""
$ARGUMENTS
"""

## What this plugin does

The diagrams plugin turns a request to "draw X" into a concrete diagram in a specific format.
Each format is its own skill with its own rules. This router only decides **which format** and
hands off; the chosen skill owns how the diagram is actually produced.

## Detection Rules (first match wins)

| Intent in the request | Route to |
|------------------------|----------|
| "ascii", "ascii art", "text diagram", "box diagram", "terminal diagram", "plain-text diagram", or any diagram with no format named that should render inline as text | `diagrams:ascii-art` |
| "mermaid", "flowchart", "sequence diagram", "class diagram", "state diagram", "ER diagram", "gantt chart", or a diagram destined for Markdown/docs rendering | `diagrams:mermaid` |
| "wardley", "wardley map", "strategic map", "value chain map", "map the landscape" | `diagrams:wardley` |

If the format is genuinely ambiguous (the user just says "diagram this" with no other signal),
default to `diagrams:ascii-art` so the result renders inline, and mention the other formats are
available.

If the user clearly wants something none of these cover, say so and ask which format they want.

## Dispatching

1. Announce: `Routing to /diagrams:SUBSKILL`
2. Invoke that sub-skill and follow it exactly.
