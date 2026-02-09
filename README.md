# solid-principles

Automated SOLID principles analysis for Claude Code

`1 skill` · `5 principles` · `~2K tokens` · `Minimal context window impact`

---

## What This Does

SOLID violations accumulate silently during development. By the time they surface — through rigid code, tangled dependencies, or brittle inheritance — refactoring is expensive.

This plugin lets you audit any class, module, or file **on demand**, getting severity-rated findings with concrete refactoring suggestions, right in your workflow.

| Principle | Focus |
|-----------|-------|
| **SRP** — Single Responsibility | One reason to change per class |
| **OCP** — Open/Closed | Extend without modifying |
| **LSP** — Liskov Substitution | Subtypes honor parent contracts |
| **ISP** — Interface Segregation | Small, focused interfaces |
| **DIP** — Dependency Inversion | Depend on abstractions, not details |

### Subcommands

Check all five at once or focus on one:

| Command | What it checks |
|---------|---------------|
| `solid` / `solid all` | All five principles |
| `solid srp` | Single Responsibility only |
| `solid ocp` | Open/Closed only |
| `solid lsp` | Liskov Substitution only |
| `solid isp` | Interface Segregation only |
| `solid dip` | Dependency Inversion only |

---

## How It Works

The skill uses progressive disclosure to minimize context window usage. Metadata is always loaded, but reference files are pulled in only when needed.

1. **Trigger** — Ask Claude to check SOLID, or mention a principle by name ("check SRP", "is this violating LSP?")
2. **Identify target code** — Files, classes, or modules you point to
3. **Load references** — Only the relevant principle reference(s) are read
4. **Analyze** — Code is checked against violation patterns and heuristics, with language-specific awareness
5. **Report** — Findings with severity, locations, and refactoring suggestions

### What You Get

Each violation is reported with:
- **Severity** — HIGH (active pain), MEDIUM (growing smell), LOW (minor impurity)
- **Location** — File, class, and line range
- **Issue** — What violates the principle and why it matters
- **Suggestion** — Concrete refactoring approach

Plus a summary: count table, top 3 priorities, and overall structural health assessment.

### Refactor Mode

Ask Claude to "fix this" or "refactor it" after an audit, and it produces refactored code resolving the identified violations.

---

## Installation

**Option 1: Marketplace (recommended)**

```bash
claude install florianbuetow/claude-code
```

**Option 2: Ask Claude**

> "Install the solid-principles plugin from florianbuetow/claude-code"

**Verify it works** — open any OO codebase and ask:

> "Check this file for SOLID violations"

<details>
<summary>Manual / Development Installation</summary>

```bash
git clone https://github.com/florianbuetow/claude-code.git
cd claude-code
# The plugin is now available locally
```

</details>

---

## Project Structure

```
.claude-plugin/
  └── marketplace.json              # Plugin registry
plugins/
  └── solid-principles/
      ├── .claude-plugin/
      │   └── plugin.json           # Plugin manifest
      └── skills/
          └── solid-principles/
              ├── SKILL.md           # Skill definition & workflow
              └── references/
                  ├── srp.md         # Single Responsibility patterns
                  ├── ocp.md         # Open/Closed patterns
                  ├── lsp.md         # Liskov Substitution patterns
                  ├── isp.md         # Interface Segregation patterns
                  └── dip.md         # Dependency Inversion patterns
```

---

## FAQ

**What languages does it support?**
Any OO language — Python, Java, TypeScript, C#, C++, Kotlin, Go (struct methods), Rust (impl blocks). The analysis adapts to the idioms of each language.

**Is it too strict?**
No. The skill includes pragmatism guidelines. A 50-line script doesn't get the same scrutiny as a large production system. Conscious trade-offs are acknowledged, not flagged.

**How much context does it use?**
Only references for requested principles are loaded. A single-principle check adds ~500 tokens of reference. A full audit adds ~2K tokens.

---

## License

MIT

---

[GitHub](https://github.com/florianbuetow/claude-code) | [Issues](https://github.com/florianbuetow/claude-code/issues) | [License](LICENSE)
