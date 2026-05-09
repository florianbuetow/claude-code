# Building Effective Claude Plugins and Skills: State of the Art

> Research synthesis across Anthropic documentation, academic research, and practitioner guides.
> Generated: 2026-04-08

---

## Key Takeaways

- **Architecture**: The field has shifted from monolithic prompts to composable skill libraries using progressive disclosure -- load metadata first (~100 tokens), full skill on trigger, reference files on demand.
- **The #1 lever is description engineering**. Write in third person, front-load the use case, include trigger keywords, cap at 250 chars. This is your retrieval vector -- Claude selects from 100+ skills using it.
- **Conciseness is a design principle**. Context window is a public good. Keep SKILL.md under 500 lines. Claude is already smart -- only add what it doesn't know. 2-3 well-crafted plugins beat 20 mediocre ones.
- **Match freedom to fragility**: High freedom for code reviews (many valid approaches), low freedom for deployments (exact scripts). Use the "narrow bridge vs open field" mental model.
- **Always include feedback loops**: Execute -> Validate -> Fix -> Re-validate. Skills that skip verification leave broken work.
- **Test across models**: What works for Opus may need more detail for Haiku. Build evaluations before writing skills. Use the Claude A/B pattern (design with one instance, test with another).
- **Plugin structure**: Components go at plugin root, NOT inside `.claude-plugin/`. Only `plugin.json` goes there.

---

## 1. Architectural Shifts: From Monolithic Prompts to Composable Skills

The dominant paradigm shift in 2025-2026 is the move from **monolithic mega-prompts** to **modular, composable skill libraries**. This mirrors findings across both industry practice and academic research.

### The Progressive Disclosure Architecture

Anthropic's Agent Skills system implements a **three-level information hierarchy** that solves the fundamental tension between capability and context efficiency:

| Level | What Loads | When | Token Cost |
|-------|-----------|------|------------|
| **L1: Metadata** | `name` + `description` from frontmatter | Session start | ~100 tokens/skill |
| **L2: Full Skill** | Complete `SKILL.md` body | When skill is triggered | Variable (keep <500 lines) |
| **L3: References** | Supporting files (`reference.md`, scripts, etc.) | On-demand during execution | Zero until accessed |

This is consistent with the **CUA-Skill** research (Microsoft, 2026) which demonstrated that structured skill abstractions with dynamic retrieval achieve 57.5% success rates on WindowsAgentArena -- substantially outperforming monolithic approaches. Their key insight: skills should encode **parameterized execution patterns** coupled with **composition graphs**, not static instruction blobs.

The **ScaleMCP** paper (PwC, 2025) extends this further for tool ecosystems, showing that dynamic tool retrieval with auto-synchronizing registries outperforms static tool lists across all 10 LLM models tested. Their Tool Document Weighted Average (TDWA) embedding strategy selectively emphasizes tool names and synthetic questions during indexing -- directly applicable to how skill descriptions should be written.

### The Plugin Component Model

Claude Code plugins bundle four distinct extension types, each solving different problems:

| Component | Purpose | Context Impact | Determinism |
|-----------|---------|---------------|-------------|
| **Skills** | On-demand instructions injected inline | Additive (loads when relevant) | Low (LLM-interpreted) |
| **Agents** | Isolated AI with custom prompts/tools/models | Separate context window | Low (LLM-driven) |
| **Hooks** | Shell commands at lifecycle events | Zero (runs externally) | High (deterministic) |
| **MCP Servers** | External tool/API connections | Tool definitions only | High (code-executed) |

**Decision framework**: Use Skills when the task needs conversation history. Use Agents when you need isolation or cost optimization (e.g., Haiku for cheap subtasks). Use Hooks when you need *guaranteed* execution (formatting, validation). Use MCP when connecting to external systems.

---

## 2. Universal Patterns: What Makes Skills Work

Cross-referencing Anthropic's official best practices, the CodeAct research, and practitioner guides reveals converging design principles.

### 2.1 Description Engineering is the #1 Lever

The description field is the single most impactful element of any skill. Claude uses it to select from potentially 100+ available skills -- it's effectively a **retrieval query** against the agent's capability index.

**Rules from Anthropic's official guide:**

- **Third person always**: "Processes Excel files and generates reports" -- never "I can help you" or "You can use this to"
- **Front-load the key use case**: Descriptions are truncated at 250 characters
- **Include both WHAT and WHEN**: "Extract text and tables from PDF files. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
- **Include trigger keywords**: Match the natural language users would actually say
- **Max 1024 characters**, but aim for concise

**Anti-patterns**: "Helps with documents", "Processes data", "Does stuff with files"

The ScaleMCP research validates this empirically: their TDWA strategy found that **selectively weighting tool names and synthetic trigger questions** during embedding produced the highest retrieval accuracy. Translate this to skills: your description IS your embedding vector.

### 2.2 Conciseness as a Design Principle

From Anthropic's best practices: "The context window is a public good." Every token in your skill competes with conversation history, other skills, and the system prompt.

**The default assumption**: Claude is already very smart. Only add context Claude doesn't already have.

````markdown
# Good (~50 tokens)
## Extract PDF text
Use pdfplumber for text extraction:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

# Bad (~150 tokens)
## Extract PDF text
PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library. There are many libraries available...
````

**Context budget**: Skill description listing uses 1% of context window (fallback: 8,000 chars). Override with `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var.

### 2.3 Degrees of Freedom

Match instruction specificity to task fragility:

| Freedom Level | When to Use | Example |
|--------------|------------|---------|
| **High** (text guidance) | Multiple valid approaches, context-dependent | Code review checklists |
| **Medium** (pseudocode/templates) | Preferred pattern exists, some variation OK | Report generation with configurable format |
| **Low** (exact scripts) | Fragile operations, consistency critical | Database migrations, deployments |

**Analogy from Anthropic**: "Narrow bridge with cliffs = low freedom (exact commands). Open field = high freedom (general direction)."

### 2.4 The Read-Before-Write Pattern

Practitioner consensus across all guides: **skills that read existing context first produce dramatically better output**.

The most productive skill instruction sequence:
1. Read existing project structure/conventions
2. Ask 2-3 clarifying questions (if needed)
3. Match existing code style and patterns
4. Include verification steps

The CodeAct research (192 upvotes on HF) validates this at a deeper level: LLM agents using **executable code actions** achieve 20% higher success rates than JSON/text-based approaches, precisely because code actions enable richer context gathering and iterative refinement.

### 2.5 Feedback Loops and Verification

Every non-trivial skill should include a validation loop:

```
Execute -> Validate -> Fix -> Re-validate -> Proceed
```

Anthropic's official pattern: "Run validator -> fix errors -> repeat. This pattern greatly improves output quality."

For complex workflows, provide checklists Claude can track:
```markdown
Task Progress:
- [ ] Step 1: Analyze input
- [ ] Step 2: Create plan
- [ ] Step 3: Validate plan
- [ ] Step 4: Execute
- [ ] Step 5: Verify output
```

---

## 3. Production Trade-offs: The Cost of Implementation

### 3.1 Context Window Economics

**The 2-3 plugin rule**: Practitioner consensus is that 2-3 well-crafted plugins outperform 20 mediocre ones. Each skill's metadata consumes session startup budget. Twenty skills competing for attention is worse than three focused ones.

**Token budget math**:
- ~100 tokens per skill at L1 (metadata only)
- 500-line recommended max for SKILL.md body
- Supporting files: zero cost until accessed
- Description listing: 1% of context window

**Optimization strategy**: Use progressive disclosure aggressively. Put the 80% case in SKILL.md, push edge cases to reference files.

### 3.2 Testing Across Models

Skills act as additions to models -- effectiveness varies by underlying model:

| Model | Consideration |
|-------|--------------|
| **Haiku** (fast, cheap) | Needs more explicit guidance, less inference |
| **Sonnet** (balanced) | Sweet spot for most skills |
| **Opus** (powerful) | Avoid over-explaining; trust its reasoning |

**Anthropic's recommendation**: "What works perfectly for Opus might need more detail for Haiku. Aim for instructions that work well with all of them."

### 3.3 Evaluation-Driven Development

Build evaluations BEFORE writing skills:

1. **Identify gaps**: Run Claude on representative tasks without a skill. Document failures.
2. **Create evaluations**: Build 3+ scenarios testing those gaps.
3. **Establish baseline**: Measure performance without the skill.
4. **Write minimal instructions**: Just enough to pass evaluations.
5. **Iterate**: Execute, compare, refine.

**The Claude A/B pattern**: Use one Claude instance ("Claude A") to design the skill. Test it with a fresh instance ("Claude B") on real tasks. Observe failures. Return to Claude A for refinements.

### 3.4 Plugin Structure Gotchas

Common mistakes from official docs:

- **Don't put components inside `.claude-plugin/`** -- only `plugin.json` goes there. Skills, agents, hooks, commands go at plugin root.
- **Avoid deeply nested references** -- keep file references one level deep from SKILL.md.
- **Don't assume tools are installed** -- explicitly list dependencies and installation steps.
- **Use forward slashes** in all file paths, even on Windows.
- **Don't offer too many options** -- provide a default with an escape hatch, not a menu of 5 alternatives.

---

## 4. Skill Authoring Checklist (from Anthropic)

### Core Quality
- [ ] Description is specific, third-person, includes trigger keywords
- [ ] Description includes both WHAT and WHEN
- [ ] SKILL.md body under 500 lines
- [ ] Additional details in separate reference files
- [ ] No time-sensitive information
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract
- [ ] File references one level deep
- [ ] Progressive disclosure used appropriately

### Code and Scripts
- [ ] Scripts handle errors explicitly (don't punt to Claude)
- [ ] No magic numbers (all values justified)
- [ ] Required packages listed and verified
- [ ] Validation/verification steps for critical operations
- [ ] Feedback loops for quality-critical tasks

### Testing
- [ ] 3+ evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated

---

## 5. Plugin Architecture Reference

### Directory Structure
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Manifest (required)
├── skills/
│   └── my-skill/
│       ├── SKILL.md          # Main instructions (required)
│       ├── reference.md      # Detailed docs (loaded on-demand)
│       └── scripts/
│           └── validate.py   # Utility scripts (executed, not loaded)
├── agents/                   # Custom subagents
├── hooks/
│   └── hooks.json            # Event handlers
├── commands/                 # Slash commands
├── .mcp.json                 # MCP server configs
├── .lsp.json                 # LSP server configs
├── bin/                      # Executables added to PATH
├── settings.json             # Default settings
└── README.md                 # Documentation
```

### SKILL.md Template
```yaml
---
name: my-skill-name
description: Processes X and generates Y. Use when the user asks about X, mentions Y, or needs Z.
disable-model-invocation: false  # true = manual /slash only
user-invocable: true             # false = background knowledge only
allowed-tools: Read Grep Bash    # restrict tool access
context: fork                    # run in isolated subagent
agent: Explore                   # subagent type (if context: fork)
model: sonnet                    # model override
effort: high                     # effort level
---

# Skill Title

## Quick start
[Minimal example for the 80% case]

## Detailed workflow
1. Step with verification
2. Step with feedback loop

## References
- For advanced usage, see [reference.md](reference.md)
- For examples, see [examples.md](examples.md)
```

### plugin.json Manifest
```json
{
  "name": "my-plugin",
  "description": "What this plugin does",
  "version": "1.0.0",
  "author": {
    "name": "Your Name"
  }
}
```

---

## 6. Key Research Papers

| Paper | Year | Key Finding | Relevance |
|-------|------|------------|-----------|
| **CodeAct** (2402.01030) | 2024 | Code-based agent actions achieve 20% higher success vs JSON/text | Validates executable skills > static instructions |
| **CUA-Skill** (2601.21123) | 2026 | Parameterized skill abstractions + composition graphs = 57.5% WAA success | Architecture pattern for modular skill design |
| **ScaleMCP** (2505.06416) | 2025 | Dynamic tool retrieval with TDWA embedding outperforms static tool lists | Informs skill description engineering |
| **EASYTOOL** (2401.06201) | 2024 | Concise tool descriptions improve LLM tool selection accuracy | Confirms "concise is key" principle |
| **Learning to Rewrite Tool Descriptions** (2602.20426) | 2026 | Auto-rewriting tool descriptions improves reliability | Skill descriptions are a tunable parameter |
| **Gaming Tool Preferences** (2505.18135) | 2025 | Edited tool descriptions increase usage 10x -- security concern | Description engineering is powerful (and exploitable) |

---

## Sources

### Official Documentation
- [Create Plugins - Claude Code Docs](https://code.claude.com/docs/en/plugins)
- [Extend Claude with Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Skill Authoring Best Practices - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Agent Skills Overview - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Equipping Agents for the Real World with Agent Skills - Anthropic Engineering](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic Claude Code Plugins README](https://github.com/anthropics/claude-code/blob/main/plugins/README.md)

### Practitioner Guides
- [How to Build Claude Code Skills That Actually Work - DEV Community](https://dev.to/whoffagents/how-to-build-claude-code-skills-custom-slash-commands-that-actually-work-1nje)
- [Claude Code Extensions: MCP, Skills, Agents & Hooks Guide - Morph](https://www.morphllm.com/claude-code-extensions)
- [Best Claude Code Plugins 2026: 10 Tested, 4 Worth Keeping - Build to Launch](https://buildtolaunch.substack.com/p/best-claude-code-plugins-tested-review)
- [Skill Engineering in 2026 - Towards AI](https://pub.towardsai.net/skill-engineering-in-2026-how-to-build-ai-agent-skills-that-actually-work-26429abc6054)
- [5 Skills Every AI Agent Needs - Medium](https://medium.com/@Micheal-Lanham/5-skills-every-ai-agent-needs-and-why-your-mega-prompt-is-holding-you-back-4b4ab2471c0e)

### Academic Papers
- [Executable Code Actions Elicit Better LLM Agents (CodeAct)](https://huggingface.co/papers/2402.01030)
- [CUA-Skill: Develop Skills for Computer Using Agent](https://huggingface.co/papers/2601.21123)
- [ScaleMCP: Dynamic and Auto-Synchronizing MCP Tools](https://huggingface.co/papers/2505.06416)
- [EASYTOOL: Enhancing LLM-based Agents with Concise Tool Instruction](https://huggingface.co/papers/2401.06201)
- [Learning to Rewrite Tool Descriptions for Reliable LLM-Agent Tool Use](https://huggingface.co/papers/2602.20426)
- [Gaming Tool Preferences in Agentic LLMs](https://huggingface.co/papers/2505.18135)

### Ecosystem
- [awesome-claude-plugins (Composio)](https://github.com/ComposioHQ/awesome-claude-plugins)
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [awesome-agent-skills (Skillmatic)](https://github.com/skillmatic-ai/awesome-agent-skills)
