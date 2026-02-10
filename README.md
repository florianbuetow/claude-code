# Claude Code Plugins

A collection of Claude Code plugins for software engineering workflows.

`2 plugins` · `2 skills` · `Minimal context window impact`

### Skills

| Skill | Description |
|-------|-------------|
| [solid-principles](#solid-principles) | Automated SOLID principles analysis for OO code |
| [spec-writer](#spec-writer) | Expert-guided software specification documents |

---

## Installation

All plugins are installed from the same marketplace.

**Step 1** — Add the marketplace:

```bash
claude plugin marketplace add florianbuetow/claude-code
```

**Step 2** — Install the plugin(s) you want:

```bash
claude plugin install solid-principles
claude plugin install spec-writer
```

**Step 3** — Restart Claude Code.

<details>
<summary>Manual / Development Installation</summary>

```bash
git clone https://github.com/florianbuetow/claude-code.git
cd claude-code
# Load a plugin directory for this session only
claude --plugin-dir ./plugins/solid-principles
claude --plugin-dir ./plugins/spec-writer
```

</details>

---

## solid-principles

Automated SOLID principles analysis for Claude Code.

`5 principles` · `~2K tokens` · `Minimal context window impact`

SOLID violations accumulate silently during development. By the time they surface — through rigid code, tangled dependencies, or brittle inheritance — refactoring is expensive.

This plugin lets you audit any class, module, or file **on demand**, getting severity-rated findings with concrete refactoring suggestions, right in your workflow.

| Principle | Focus |
|-----------|-------|
| **SRP** — Single Responsibility | One reason to change per class |
| **OCP** — Open/Closed | Extend without modifying |
| **LSP** — Liskov Substitution | Subtypes honor parent contracts |
| **ISP** — Interface Segregation | Small, focused interfaces |
| **DIP** — Dependency Inversion | Depend on abstractions, not details |

### How to Use

Check all five at once or focus on one:

| Command | What it checks |
|---------|---------------|
| `solid` / `solid all` | All five principles |
| `solid srp` | Single Responsibility only |
| `solid ocp` | Open/Closed only |
| `solid lsp` | Liskov Substitution only |
| `solid isp` | Interface Segregation only |
| `solid dip` | Dependency Inversion only |

**Trigger** — Ask Claude to check SOLID, or mention a principle by name ("check SRP", "is this violating LSP?").

Each violation is reported with severity (HIGH / MEDIUM / LOW), location, issue description, and a concrete refactoring suggestion. Ask Claude to "fix this" or "refactor it" after an audit to get refactored code.

**Languages:** Any OO language — Python, Java, TypeScript, C#, C++, Kotlin, Go, Rust. The analysis adapts to each language's idioms.

---

## spec-writer

Expert-guided software specification documents for greenfield projects.

`5 document types` · `5 framework levels` · `Evidence-backed (ISO 29148, IEEE 830, IREB, DDD, C4, BDD)`

Writing specifications is hard. Most teams either skip them entirely or produce documents that gather dust. This plugin walks you through creating professional, layered specification documents via an interactive guided interview — asking the right questions, suggesting intelligent defaults based on your project context, and outputting polished markdown documents.

### Document Types

The skill produces five document types, each building on the previous:

| Level | Command | Document | Core question |
|-------|---------|----------|---------------|
| L0 | `/spec-vision` | Product Vision & Strategic Alignment | "Why are we building this?" |
| L1 | `/spec-brs` | Business & Stakeholder Requirements | "What does the business need?" |
| L2 | `/spec-srs` | Software Requirements Specification | "What does the system do?" |
| L3 | `/spec-architecture` | Architecture & Design Specification | "How will it work?" |
| L4 | `/spec-test` | Behavioral Spec & Test Verification Plan | "Prove it with examples" |
| All | `/spec` | Full walkthrough — all five in sequence | End-to-end specification |

### How to Use

#### Full walkthrough

Use `/spec` to be guided through all five documents in sequence. Each level feeds into the next — goals become requirements, requirements become system behaviors, behaviors become architecture decisions, and decisions get verified by test plans.

#### Individual documents

You can create any document on its own, but **the documents form a hierarchy** — each level builds on the context established by the level above it. If you skip a level, the skill will ask you for the essential upstream context it needs.

**Recommended order when creating documents individually:**

```
L0: /spec-vision
 └─▶ L1: /spec-brs        (references Vision goals)
      └─▶ L2: /spec-srs   (references BRS stakeholder needs & business rules)
           └─▶ L3: /spec-architecture  (references SRS requirements as ASRs)
                └─▶ L4: /spec-test     (references SRS requirements for scenarios)
```

- **Start at L0** (`/spec-vision`) if you're beginning a new project from scratch.
- **Start at L1** (`/spec-brs`) if you already have a clear vision and need to formalize business requirements.
- **Start at L2** (`/spec-srs`) if business requirements are already understood and you need system-level specs.
- **Start at L3** (`/spec-architecture`) if you have an SRS and need to document design decisions.
- **Start at L4** (`/spec-test`) if you have requirements and need to elaborate test scenarios for specific features.

You don't need to complete all five levels. Pick the level(s) that match where you are in your project:

| Scenario | Recommended commands |
|----------|---------------------|
| New project, need full specs | `/spec` (full walkthrough) |
| New project, want to start light | `/spec-vision` then `/spec-brs` |
| Have requirements, need architecture | `/spec-architecture` |
| Need test plans for existing features | `/spec-test` |
| Stakeholder alignment needed | `/spec-vision` |

### What to Expect

The skill drives an interactive conversation:
- Questions are presented as **selectable options** with a free-text escape
- **1-3 questions per turn**, grouped thematically — it won't overwhelm you
- After each section, it **summarizes what was captured** and asks for confirmation
- It **challenges vague inputs** (e.g., "the system should be fast" becomes "p99 latency ≤ 200ms under 1,000 concurrent users")
- It provides **context-aware suggestions** based on your project domain (B2B SaaS, healthcare, startup MVP, etc.)

Output documents are saved as markdown files with traceability IDs that link across levels.

---

## Project Structure

```
.claude-plugin/
  └── marketplace.json                # Plugin registry
plugins/
  ├── solid-principles/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       └── solid-principles/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── srp.md          # Single Responsibility patterns
  │               ├── ocp.md          # Open/Closed patterns
  │               ├── lsp.md          # Liskov Substitution patterns
  │               ├── isp.md          # Interface Segregation patterns
  │               └── dip.md          # Dependency Inversion patterns
  └── spec-writer/
      ├── .claude-plugin/
      │   └── plugin.json             # Plugin manifest
      └── skills/
          └── spec-writer/
              ├── SKILL.md            # Skill definition & workflow
              └── references/
                  ├── vision.md       # L0 — Product Vision reference
                  ├── brs.md          # L1 — Business Requirements reference
                  ├── srs.md          # L2 — Software Requirements reference
                  ├── architecture.md # L3 — Architecture & Design reference
                  └── verification.md # L4 — Test Verification reference
```

---

## FAQ

**What languages does solid-principles support?**
Any OO language — Python, Java, TypeScript, C#, C++, Kotlin, Go (struct methods), Rust (impl blocks). The analysis adapts to the idioms of each language.

**Is solid-principles too strict?**
No. The skill includes pragmatism guidelines. A 50-line script doesn't get the same scrutiny as a large production system.

**Do I need all five spec documents?**
No. Each document can be created independently. Start at whatever level matches your needs. The full walkthrough (`/spec`) is there for when you want the complete suite.

**Can I use spec-writer for an existing project?**
The skill is optimized for greenfield projects, but you can start at any level. For existing projects, `/spec-architecture` and `/spec-test` are often the most useful starting points.

**How much context do the plugins use?**
Both plugins use progressive disclosure — reference material is loaded only when needed. solid-principles adds ~500 tokens per principle (~2K for all five). spec-writer loads one reference file per document type.

---

## License

MIT

---

[GitHub](https://github.com/florianbuetow/claude-code) | [Issues](https://github.com/florianbuetow/claude-code/issues) | [License](LICENSE)
