# communicator

A communication-style toolkit for Claude Code. One skill for now.

## Skills

| Skill | Purpose |
|-------|---------|
| `/communicator:tldr` | Switch Claude into a military-style BLUF (Bottom Line Up Front) mode — extreme brevity, no filler. |

## tldr

The `tldr` skill enforces terse, instantly-parseable output:

- **Critical issues first** — real bugs and blockers as a bullet list, not preferences.
- **Actionable next step** — the exact command, file change, or decision needed.
- **Bottom line last** — a one-sentence conclusion, status, or answer on its own line.
- **No filler** — cuts preambles, recaps, meta-commentary, politeness padding, and over-explanation.

### Triggering

The skill fires when you type any of:

- `tldr` or `/tldr`
- `short mode`
- `be brief`
- `concise mode`

…or otherwise ask for terse, no-fluff output. Once active, it shapes the response style until you ask for normal output.
