# Claude Code Plugins and Skills

![Made with AI](https://img.shields.io/badge/Made%20with-AI-333333?labelColor=f00) ![Verified by Humans](https://img.shields.io/badge/Verified%20by-Humans-333333?labelColor=brightgreen)

A collection of `29 plugins` and `117 skills` for Claude Code.

## Quickstart

```bash
# 1. Add the marketplace
claude plugin marketplace add florianbuetow/claude-code

# 2. Install plugins (pick what you need)
claude plugin install agent-guardrails
claude plugin install appsec
claude plugin install arc42
claude plugin install archibald
claude plugin install beyond-solid-principles
claude plugin install cache-money
claude plugin install changelog
claude plugin install claudeignore
claude plugin install codebasescout
claude plugin install communicator
claude plugin install context-research
claude plugin install diagrams
claude plugin install explain-system-tradeoffs
claude plugin install fixclaude
claude plugin install guard
claude plugin install handoff
claude plugin install iso27001-sdlc
claude plugin install kiss
claude plugin install logbook
claude plugin install onboarding
claude plugin install orchestrator
claude plugin install progressive-disclosure
claude plugin install retrospective
claude plugin install solid-principles
claude plugin install spec-dd
claude plugin install sessionlog
claude plugin install spec-writer
claude plugin install terminator
claude plugin install tokeneconomics

# 3. Restart Claude Code

# Update all installed plugins to latest versions
claude plugin marketplace update florianbuetow-plugins
```

### Skills

| Skill | Description |
|-------|-------------|
| [agent-guardrails](#agent-guardrails) | Agent behavioral guardrails — 6 rules via Stop hook with intent-aligned feedback |
| [appsec](#appsec) | Comprehensive application security toolbox - 62 skills, 8 frameworks, red team simulation |
| [arc42](#arc42) | Generate arc42 architecture documentation from a codebase - evidence-grounded, Mermaid diagrams, GAP flags |
| [archibald](#archibald) | Software architecture quality assessment - smells, metrics, antipatterns, dependencies, risks, debt |
| [beyond-solid-principles](#beyond-solid-principles) | System-level architecture principles analysis |
| [cache-money](#cache-money) | Keep the Anthropic prompt cache warm during peak hours - adapts ping interval to your cache TTL (5-min or 1-hour) |
| [changelog](#changelog) | Generate and maintain CHANGELOG.md from git history - Keep a Changelog format with Semantic Versioning |
| [claudeignore](#claudeignore) | Generate and maintain .claudeignore files - analyzes repo structure to exclude caches and build artifacts from context |
| [codebasescout](#codebasescout) | Scout a codebase, rank findings by Impact x Opportunity, plan fixes, tag each task with a recommended model |
| [communicator](#communicator) | Communication-style toolkit — tldr skill switches Claude into military-style BLUF mode: extreme brevity, conclusion last, bullets over prose |
| [context-research](#context-research) | Autonomous AI research pipeline - discovers, ranks, and synthesizes SOTA papers via Hugging Face & ArXiv |
| [diagrams](#diagrams) | Diagramming toolkit — routes to ascii-art (CP437 box-drawing), mermaid (flowcharts, sequence, ER), or wardley (WTG2 DSL for SVG rendering) |
| [explain-system-tradeoffs](#explain-system-tradeoffs) | Distributed system tradeoff analysis |
| [fixclaude](#fixclaude) | Production-grade CLAUDE.md directives that override Claude Code's built-in limitations |
| [guard](#guard) | Helper for the guard CLI - protects files from accidental AI edits via immutable flags and root ownership |
| [handoff](#handoff) | Session handoff and continuation - compact sessions into structured handoff documents for task continuity |
| [iso27001-sdlc](#iso27001-sdlc) | ISO 27001:2022 software development compliance scanner - Annex A controls 8.4, 8.25–8.33 |
| [K.I.S.S.](#kiss) | Code and architecture simplicity analysis - complexity, abstraction, redundancy, architecture |
| [logbook](#logbook) | Session log analytics - time spent and messages exchanged per project/branch, with monthly + yearly reports |
| [onboarding](#onboarding) | Project onboarding - status briefing from git, issues, and build system |
| [orchestrator](#orchestrator) | Evidence-based model routing — maps engineering tasks to the best-suited AI model using a 30-category taxonomy |
| [progressive-disclosure](#progressive-disclosure) | Documentation structure analysis - maps soul files, detects orphaned docs, generates thematic indexes |
| [retrospective](#retrospective) | Developer-AI workflow analysis - session log retros with feedback loops |
| [sessionlog](#sessionlog) | Export session logs as standard LLM conversation JSON and TXT transcripts |
| [solid-principles](#solid-principles) | Automated SOLID principles analysis for OO code |
| [spec-dd](#spec-dd) | Specification-driven development workflow |
| [spec-writer](#spec-writer) | Expert-guided software specification documents |
| [terminator](#terminator) | Stop hooks that end a Claude Code session (and optionally its terminal) when a kill phrase appears in the agent's final message |
| [tokeneconomics](#tokeneconomics) | Session token usage analysis - cache efficiency, conversation sprawl, model selection, cost optimization |

---

## Useful Scripts

<img src="scripts/claude-status/statusbar.jpg" alt="Context window status bar" width="640">

A colored context window progress bar for the Claude Code CLI status line — see [scripts/claude-status/](scripts/claude-status/) for installation instructions.

### claudex — Run Claude Code with Local LM Studio Models

A shell helper that lets you interactively pick a local LM Studio model and launch Claude Code against it. Models are listed grouped by publisher with size and context length info. The selected model is auto-loaded before launching and auto-unloaded afterwards. See [scripts/claude-lmstudio/](scripts/claude-lmstudio/) for details.

### pix — Run pi with Local LM Studio Models

A shell helper that lets you interactively pick a local LM Studio model and launch [pi](https://github.com/badlogic/pi-mono) against it. Works the same as `claudex` but configures pi's `~/.pi/agent/models.json` instead of env vars. See [scripts/pi-lmstudio/](scripts/pi-lmstudio/) for details.

---

## Installation

All plugins are installed from the same marketplace.

```bash
# Add the marketplace (one time)
claude plugin marketplace add florianbuetow/claude-code

# Install any plugin by name
claude plugin install <plugin-name>
```

Restart Claude Code after installing. Available plugins: `agent-guardrails`, `appsec`, `arc42`, `archibald`, `beyond-solid-principles`, `cache-money`, `changelog`, `claudeignore`, `codebasescout`, `communicator`, `context-research`, `diagrams`, `explain-system-tradeoffs`, `fixclaude`, `guard`, `handoff`, `iso27001-sdlc`, `kiss`, `logbook`, `onboarding`, `orchestrator`, `progressive-disclosure`, `retrospective`, `sessionlog`, `solid-principles`, `spec-dd`, `spec-writer`, `terminator`, `tokeneconomics`.

### Updating

```bash
# Update all installed plugins to latest versions
claude plugin marketplace update florianbuetow-plugins

# Verify a plugin version
find ~/.claude/plugins -name "plugin.json" -path "*<plugin-name>*" -exec grep version {} \;
```

<details>
<summary>Manual / Development Installation</summary>

```bash
git clone https://github.com/florianbuetow/claude-code.git
cd claude-code
# Load a plugin directory for this session only
claude --plugin-dir ./plugins/<plugin-name>
```

</details>

### Using the Justfile

If you have [just](https://github.com/casey/just) installed, you can manage the marketplace and plugins with:

```bash
just install   # Add marketplace and install all plugins
just update    # Update marketplace and all installed plugins
just status    # Show installed vs repo plugin versions
just validate  # Validate plugin and marketplace manifests
```

### Using with Codex (OpenAI)

These skills follow the open [Agent Skills](https://agentskills.io) standard (`SKILL.md` files with YAML frontmatter), which means they work with [Codex](https://github.com/openai/codex) out of the box - no modifications needed. Codex recursively discovers all `SKILL.md` files within each plugin directory. Subcommands use namespaced names (e.g., `changelog:create`, `logbook:time`) to avoid collisions.

> **Important: Always install plugins as whole directories.** Each plugin directory contains all its skills, subcommands, reference files, and scripts. Never cherry-pick individual `SKILL.md` files out of their directory - they depend on sibling files for context.
>
> **Do not use `$skill-installer` or `npx skills`** - these tools flatten the directory tree by extracting each `SKILL.md` as a standalone skill. Plugins with subcommands that share common directory names (e.g., `update/`) across different plugins will collide when installed this way.

**Option 1** - Clone and copy plugin directories:

```bash
git clone https://github.com/florianbuetow/claude-code.git /tmp/claude-code
mkdir -p ~/.agents/skills

# Copy each plugin directory as a whole unit
for plugin in /tmp/claude-code/plugins/*/; do
  plugin_name=$(basename "$plugin")
  cp -r "$plugin" ~/.agents/skills/"$plugin_name"
done

rm -rf /tmp/claude-code
```

**Option 2** - Symlink for automatic sync:

```bash
git clone https://github.com/florianbuetow/claude-code.git ~/claude-code-plugins

# Symlink each plugin directory as a whole unit
mkdir -p ~/.agents/skills
for plugin in ~/claude-code-plugins/plugins/*/; do
  plugin_name=$(basename "$plugin")
  ln -sfn "$plugin" ~/.agents/skills/"$plugin_name"
done
```

With symlinking, a `git pull` in the cloned repo updates all skills automatically.

Skills are invoked in Codex with `$skill-name` (e.g., `$solid-principles`, `$changelog:create`) or auto-triggered by context. Codex discovers skills from `~/.agents/skills/` (user-level) and `.agents/skills/` (repo-level).

---

## solid-principles

Automated SOLID principles analysis for Claude Code.

`5 principles`

SOLID violations accumulate silently during development. By the time they surface - through rigid code, tangled dependencies, or brittle inheritance - refactoring is expensive.

This plugin lets you audit any class, module, or file **on demand**, getting severity-rated findings with concrete refactoring suggestions, right in your workflow.

| Principle | Focus |
|-----------|-------|
| **SRP** - Single Responsibility | One reason to change per class |
| **OCP** - Open/Closed | Extend without modifying |
| **LSP** - Liskov Substitution | Subtypes honor parent contracts |
| **ISP** - Interface Segregation | Small, focused interfaces |
| **DIP** - Dependency Inversion | Depend on abstractions, not details |

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

**Trigger** - Ask Claude to check SOLID, or mention a principle by name ("check SRP", "is this violating LSP?").

Each violation is reported with severity (HIGH / MEDIUM / LOW), location, issue description, and a concrete refactoring suggestion. Ask Claude to "fix this" or "refactor it" after an audit to get refactored code.

**Languages:** Any OO language - Python, Java, TypeScript, C#, C++, Kotlin, Go, Rust. The analysis adapts to each language's idioms.

---

## beyond-solid-principles

System-level architecture principles analysis for Claude Code.

`10 principles`

SOLID covers class-level design, but architecture rot happens at a larger scale - tangled services, leaky abstractions, hidden coupling between modules, brittle failure propagation. By the time these problems surface, untangling them is far more expensive than fixing a single class.

This plugin lets you audit modules, services, layers, and component boundaries **on demand**, getting severity-rated findings with concrete remediation suggestions that operate at the architecture scale.

| Principle | Focus |
|-----------|-------|
| **SoC** - Separation of Concerns | Distinct sections for distinct responsibilities |
| **SRP-Sys** - Single Responsibility (system-level) | One business capability per module/service |
| **DRY** - Don't Repeat Yourself | Eliminate knowledge duplication across boundaries |
| **Demeter** - Law of Demeter | Talk only to immediate collaborators |
| **Coupling** - Loose Coupling, High Cohesion | Minimize dependencies, maximize relatedness |
| **Evolvability** - Build for Change | Support incremental evolution without rewrites |
| **Resilience** - Design for Failure | Prevent cascading failures in distributed systems |
| **KISS** - Keep It Simple | Avoid accidental complexity and over-engineering |
| **POLA** - Principle of Least Surprise | Predictable APIs and system behavior |
| **YAGNI** - You Aren't Gonna Need It | Don't build for hypothetical future requirements |

### How to Use

Check all ten at once or focus on one:

| Command | What it checks |
|---------|---------------|
| `beyond-solid-principles` | All ten principles |
| `sw-soc` | Separation of Concerns only |
| `sw-srp-sys` | Single Responsibility (system-level) only |
| `sw-dry` | DRY only |
| `sw-demeter` | Law of Demeter only |
| `sw-coupling` | Loose Coupling, High Cohesion only |
| `sw-evolvability` | Build for Change only |
| `sw-resilience` | Design for Failure only |
| `sw-kiss` | KISS only |
| `sw-pola` | Principle of Least Surprise only |
| `sw-yagni` | YAGNI only |

**Trigger** - Ask Claude to check architecture principles, or mention a principle by name ("check separation of concerns", "is this violating DRY?", "Law of Demeter", "loose coupling").

Each violation is reported with severity (HIGH / MEDIUM / LOW), location, issue description, and a concrete remediation suggestion. Ask Claude to "fix this" or "refactor it" after an audit to get refactored code or an architecture proposal.

**Languages & architectures:** Any language, any architecture style - monoliths, modular monoliths, microservices, serverless, event-driven, layered, hexagonal. The analysis adapts to the idioms and scale of the target system.

---

## archibald

Software architecture quality assessment for Claude Code.

`6 dimensions` · `7 architectural smells` · `13 antipatterns` · `12 reference files`

SOLID checks class design. Beyond-SOLID checks design principles. But neither tells you whether your architecture is structurally healthy - whether dependencies form cycles, whether components have become god objects, whether coupling metrics are approaching dangerous thresholds, or whether technical debt is accumulating in central components. These are different questions that require different analysis.

Archibald assesses the structural health of a software architecture through six dimensions: smell detection, quantitative metrics, antipattern identification, dependency structure evaluation, risk/trade-off analysis, and technical debt measurement. The assessment approach is grounded in established frameworks (ATAM, SAAM, QUASAR) and research showing that architectural smells are independent from code smells (less than 30% correlation), making dedicated architecture-level assessment essential.

### Assessment Dimensions

| Dimension | What it covers |
|-----------|---------------|
| **Smells** | 7 core architectural smells - Cyclic Dependency, Unstable Dependency, Hub-Like Dependency, God Component, Feature Concentration, Scattered Functionality, Ambiguous Interface |
| **Antipatterns** | 13 flawed decision patterns - Big Ball of Mud, Abstraction Inversion, God Object, Inner Platform Effect, Interface Bloat, Stovepipe System, Anemic Domain Model, Sequential Coupling, Cargo Cult Programming, Technology-Driven Architecture, Golden Hammer, Malignant Growth, Over/Under-Engineering |
| **Metrics** | Quantitative measures with thresholds - CBO, afferent/efferent coupling, instability, LCOM, cohesion types, cyclomatic complexity, LOC, nesting depth |
| **Dependencies** | Dependency Structure Matrix (DSM) analysis - layering patterns, cycle detection, hub identification, partitioning algorithms |
| **Risks** | Trade-off and risk analysis (ATAM-derived) - risks, sensitivity points, trade-off points, quality attribute scenarios |
| **Debt** | Technical Debt Index (TDI), prioritization matrix (impact × change frequency), management strategies, remediation patterns (Strangler Fig, Façade) |

### How to Use

Run a full assessment or focus on a single dimension:

| Command | What it assesses |
|---------|-----------------|
| `archibald` / `archibald full` | Full assessment (all six dimensions) |
| `archibald smells` | Architectural smell detection |
| `archibald antipatterns` | Antipattern identification |
| `archibald metrics` | Quantitative metrics analysis |
| `archibald dependencies` | Dependency structure / DSM analysis |
| `archibald risks` | Risk & trade-off analysis |
| `archibald debt` | Technical debt assessment |

**Trigger** - Ask Claude to assess architecture quality, check for architectural smells, analyze dependencies, measure coupling/cohesion/complexity, evaluate technical debt, or mention a concept by name ("cyclic dependency", "god component", "CBO", "DSM", "instability metric").

Each finding is reported with severity (CRITICAL / HIGH / MEDIUM / LOW), location, evidence, impact description, and a concrete recommendation. The summary includes a health score per dimension, a prioritized top-3 list, and an improvement roadmap categorized as Critical / Important / Beneficial.

**Languages & architectures:** Any language, any architecture style - monoliths, modular monoliths, microservices, serverless, event-driven, layered, hexagonal. Severity is calibrated to project scale, team size, and lifecycle stage.

---

## K.I.S.S.

Code and architecture simplicity analysis for Claude Code.

`4 categories` · `20 violation patterns`

Unnecessary complexity accumulates silently during development. Clever one-liners that no one can debug, abstraction layers that add no value, dead code that misleads readers, architecture choices driven by resumes rather than requirements. By the time these problems surface - through slow onboarding, painful debugging, or fear of changing anything - simplification is expensive.

This plugin lets you audit any file, module, or system **on demand**, getting severity-rated findings with concrete simplification suggestions, right in your workflow. It analyzes without modifying code - you decide what to simplify.

| Category | Focus |
|----------|-------|
| **Complexity** | Deep nesting, long functions, convoluted control flow, high cyclomatic complexity, clever code |
| **Abstraction** | Premature generalization, unnecessary indirection, pattern overuse, excessive layering, abstraction inversion |
| **Redundancy** | Dead code, redundant validation, duplicate logic, unnecessary comments, unused parameters |
| **Architecture** | Premature microservices, architecture astronautics, resume-driven development, speculative generality, excessive middle tiers |

### How to Use

Check all four categories at once or focus on one:

| Command | What it checks |
|---------|---------------|
| `kiss` / `kiss all` | All four categories |
| `kiss complexity` | Code complexity only |
| `kiss abstraction` | Over-abstraction only |
| `kiss redundancy` | Redundancy only |
| `kiss architecture` | Architecture complexity only |

**Trigger** - Ask Claude to check for unnecessary complexity, simplify code, find over-engineering, or mention a category by name ("check complexity", "find dead code", "over-abstraction", "keep it simple").

Each violation is reported with severity (HIGH / MEDIUM / LOW), location, issue description, and a concrete simplification suggestion. Ask Claude to "fix this" or "simplify it" after an audit to get simplified code.

**Languages:** Any language - Python, Java, TypeScript, C#, C++, Kotlin, Go, Rust. The analysis adapts to each language's idioms. Essential complexity (inherent to the problem domain) is not flagged - only accidental complexity introduced by our choices.

---

## appsec

Comprehensive application security toolbox for Claude Code.

`62 skills` · `8 frameworks` · `7 agents` · `18 detection pattern references` · `4 depth modes`

Security vulnerabilities hide in code patterns, architectural decisions, and dependency choices. Finding them requires expertise across multiple frameworks - OWASP, STRIDE, PASTA, LINDDUN, MITRE ATT&CK - and the ability to think like different attackers. Most teams can't afford dedicated security engineers on every project.

This plugin brings that expertise into your workflow. Run a quick scan or launch a full audit with red team simulation. Every finding includes severity, CWE mapping, DREAD scoring, and concrete fix suggestions.

### Frameworks

| Framework | Skills | What it covers |
|-----------|--------|----------------|
| **OWASP Top 10** (2021) | 10 individual + dispatcher | Web application vulnerabilities (A01–A10) |
| **STRIDE** | 6 individual + dispatcher | Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Privilege Escalation |
| **PASTA** | 7 individual + dispatcher | 7-stage threat modeling methodology |
| **LINDDUN** | 7 individual + dispatcher | Privacy threats across 7 categories |
| **MITRE ATT&CK** | mapping skill | Adversary tactics and techniques |
| **SANS/CWE Top 25** | mapping skill | Most dangerous software weaknesses |
| **OWASP API Top 10** | `/appsec:api` | API-specific security risks |
| **DREAD** | scoring model | Risk scoring (Damage, Reproducibility, Exploitability, Affected Users, Discoverability) |

### Red Team Agents

At `--depth expert`, six attacker personas simulate real-world adversaries:

| Agent | Persona |
|-------|---------|
| script-kiddie | Low-skill opportunist - known CVEs, default credentials |
| hacktivist | Ideological attacker - data leaks, defacement |
| insider | Malicious authenticated user - privilege escalation, exfiltration |
| organized-crime | Professional criminal - payment data, PII, ransomware |
| supply-chain | Dependency compromiser - build pipeline, lockfiles |
| nation-state | Advanced persistent threat - multi-step chains, persistence |

A consolidator agent merges, deduplicates, and ranks all findings.

### How to Use

| Command | What it does |
|---------|-------------|
| `/appsec:start` | Assess codebase and recommend tools |
| `/appsec:run` | Smart orchestrator - picks the right checks |
| `/appsec:owasp` | Run all OWASP Top 10 checks |
| `/appsec:stride` | Full STRIDE threat analysis |
| `/appsec:pasta` | 7-stage PASTA methodology |
| `/appsec:linddun` | Privacy threat analysis |
| `/appsec:full-audit` | Exhaustive audit with dated report |
| `/appsec:secrets` | Detect hardcoded secrets |
| `/appsec:fix` | Generate code fixes for findings |
| `/appsec:explain` | Interactive framework/finding explainer |

All skills support `--scope`, `--severity`, `--depth`, `--format`, `--fix`, and `--explain` flags. Default scope is `changed` (only modified files).

**Depth modes:** `quick` (scanners only) · `standard` (scanner + Claude analysis) · `deep` (multi-framework) · `expert` (+ red team simulation with DREAD scoring)

**Specialized tools:** race-conditions, file-upload, graphql, websocket, serverless, api, business-logic, fuzz, model, attack-surface, data-flows, regression

**Education:** `/appsec:learn` (guided walkthroughs), `/appsec:glossary` (quick reference)

**Hook:** Automatically reviews plans on `ExitPlanMode` and checks for hardcoded secrets on file writes and edits.

**Languages & stacks:** Any - Python, JavaScript/TypeScript, Java, Go, C#, Ruby, PHP, Rust. Detects and uses installed scanners (semgrep, bandit, gitleaks, trivy, etc.) with Claude analysis fallback.

---

## spec-writer

Expert-guided software specification documents for greenfield projects.

`5 document types` · `5 framework levels` · `Evidence-backed (ISO 29148, IEEE 830, IREB, DDD, C4, BDD)`

Writing specifications is hard. Most teams either skip them entirely or produce documents that gather dust. This plugin walks you through creating professional, layered specification documents via an interactive guided interview - asking the right questions, suggesting intelligent defaults based on your project context, and outputting polished markdown documents.

### Document Types

The skill produces five document types, each building on the previous:

| Level | Command | Document | Core question |
|-------|---------|----------|---------------|
| L0 | `/spec-vision` | Product Vision & Strategic Alignment | "Why are we building this?" |
| L1 | `/spec-brs` | Business & Stakeholder Requirements | "What does the business need?" |
| L2 | `/spec-srs` | Software Requirements Specification | "What does the system do?" |
| L3 | `/spec-architecture` | Architecture & Design Specification | "How will it work?" |
| L4 | `/spec-test` | Behavioral Spec & Test Verification Plan | "Prove it with examples" |
| All | `/spec` | Full walkthrough - all five in sequence | End-to-end specification |

### How to Use

#### Full walkthrough

Use `/spec` to be guided through all five documents in sequence. Each level feeds into the next - goals become requirements, requirements become system behaviors, behaviors become architecture decisions, and decisions get verified by test plans.

#### Individual documents

You can create any document on its own, but **the documents form a hierarchy** - each level builds on the context established by the level above it. If you skip a level, the skill will ask you for the essential upstream context it needs.

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
- **1-3 questions per turn**, grouped thematically - it won't overwhelm you
- After each section, it **summarizes what was captured** and asks for confirmation
- It **challenges vague inputs** (e.g., "the system should be fast" becomes "p99 latency ≤ 200ms under 1,000 concurrent users")
- It provides **context-aware suggestions** based on your project domain (B2B SaaS, healthcare, startup MVP, etc.)

Output documents are saved as markdown files with traceability IDs that link across levels.

---

## spec-dd

Specification-driven development workflow for Claude Code.

`7 phases` · `5 reference guides` · `Advisory quality gates` · `Language-aware reviews`

Tests are a firewall between specification and implementation. You never modify tests during implementation - if the code can't pass the tests, the implementation approach is wrong, not the tests.

This plugin orchestrates a spec-first discipline: define behavioral specifications, derive test scenarios, plan test implementation, implement tests (verify they fail), implement features (make tests pass), and verify alignment across all artifacts and code. It acts as a workflow navigator with advisory quality gates - guiding you through each phase, surfacing gaps and ambiguity, and offering handoff prompts for coding agents when it's time to write actual code.

### Workflow Phases

| Phase | Command | What it does |
|-------|---------|-------------|
| 1 | `/spec-dd:spec` | Write behavioral specification - unambiguous requirements, edge cases, acceptance criteria |
| 2 | `/spec-dd:test` | Derive test scenarios (Given/When/Then) from spec only - no implementation knowledge |
| 3 | `/spec-dd:test-impl` | Map every test scenario to a technical approach for test implementation |
| 4 | *(handoff)* | Implement tests and verify they fail (feature code doesn't exist yet) |
| 5 | *(handoff)* | Make all tests pass by implementing the required features |
| 6 | `/spec-dd:verify` | Verify implementation satisfies the spec - requirement-level PASS/FAIL checklist |
| 7 | `/spec-dd:review` | Verify alignment across all artifacts and code, run tests |

### How to Use

| Command | What it does |
|---------|-------------|
| `/spec-dd` | Auto-detect phase, assess current state, recommend next step |
| `/spec-dd:spec` | Work on the behavioral specification |
| `/spec-dd:test` | Work on the test specification |
| `/spec-dd:test-impl` | Work on the test implementation specification |
| `/spec-dd:verify` | Verify implementation against any spec file (read-first, run-second) |
| `/spec-dd:review` | Run alignment review, execute tests, produce report |

All commands accept an optional feature name (e.g., `/spec-dd:spec user-auth`). `/spec-dd:verify` also accepts a spec file path (e.g., `/spec-dd:verify specifications.md chat-ui`) to verify against informal specs not created through spec-dd. Without a feature name, the skill lists available features and asks you to choose.

**Auto-detect router** - `/spec-dd` without a phase scans `docs/specs/` for existing artifacts, assesses which phases are complete, identifies gaps, and recommends the next action.

**Advisory quality gates** - The skill flags issues (unresolved ambiguity, missing traceability, coverage gaps) and recommends addressing them, but you can override and proceed.

**Language-aware** - Auto-detects your project's language and ecosystem (package.json, requirements.txt, go.mod, Cargo.toml, etc.) to ensure test scenarios are realistic and test implementation patterns are idiomatic.

**Test execution** - During review, detects and runs your project's test runner (Makefile, justfile, pytest, go test, cargo test, npm test, mvn test, gradle test).

**Implementation verification** - `/spec-dd:verify` checks whether code satisfies a specification at the requirement level. Works with any spec file (including informal ones outside the spec-dd workflow). Prefers reading code over running tests - only executes tests when runtime behavior can't be verified by inspection. Handles non-deterministic tests by verifying the test exists and exercises the right code path.

**Artifacts** - All documents live in `docs/specs/`: `<feature>-specification.md`, `<feature>-test-specification.md`, `<feature>-test-implementation-specification.md`, `<feature>-verification.md`, `<feature>-implementation-review.md`.

---

## explain-system-tradeoffs

Reverse-engineer distributed system tradeoffs from code, configuration, and architecture artifacts.

`6 tradeoff axes` · `3 evidence tiers` · `Parallel subagent analysis` · `Evidence-based (CAP, PACELC, SRE, chaos engineering)`

Every distributed system encodes its design tradeoffs in artifacts hiding in plain sight - configuration files, schema definitions, deployment manifests, timeout values, retry policies, and code patterns. A `synchronous_commit = off` in PostgreSQL, a `failure_mode_deny: false` in Envoy, a hashed shard key on time-series data - each is a decision with consequences that ripple across the system.

This plugin reads those artifacts like an architectural blueprint. Instead of looking for *violations* (that's what beyond-solid-principles does), it identifies *decisions* - what the system prioritizes, what it sacrifices, whether those choices appear deliberate or accidental, and where they conflict with each other.

### Tradeoff Axes

| Axis | Focus | Example indicators |
|------|-------|--------------------|
| **Consistency** | Consistency & Availability | Replication factors, quorum settings, cache TTLs, conflict resolution, schema compatibility modes |
| **Latency** | Latency & Throughput | GC flags, thread pool configs, Disruptor wait strategies, deadline propagation, hedged requests, compaction styles |
| **Data** | Data Distribution | Shard keys, partition strategies, rack-aware replication, data sovereignty constraints, cross-shard complexity |
| **Transactions** | Transaction Boundaries & Coordination | Sagas, outbox tables, schema evolution, API versioning, dependency boundaries, database-per-service |
| **Resilience** | Resilience & Failure Isolation | Circuit breakers, retry budgets, chaos experiments with steady-state hypotheses, canary analysis templates, service mesh outlier detection |
| **Operations** | Observability, Security & Cost | Tracing sampling rates, SLO/error-budget frameworks, mTLS posture, audit trail fidelity, multi-region cost topology |

### How to Use

Analyze all six axes at once or focus on one:

| Command | What it analyzes |
|---------|-----------------|
| `explain-system-tradeoffs` | All six axes (parallel) |
| `explain-system-consistency-tradeoffs` | Consistency & Availability only |
| `explain-system-latency-tradeoffs` | Latency & Throughput only |
| `explain-system-data-tradeoffs` | Data Distribution only |
| `explain-system-transaction-tradeoffs` | Transaction Boundaries & Coordination only |
| `explain-system-resilience-tradeoffs` | Resilience & Failure Isolation only |
| `explain-system-operations-tradeoffs` | Observability, Security & Cost only |

**Trigger** - Ask Claude to explain system tradeoffs, analyze architecture decisions, or mention a tradeoff by name ("consistency vs availability", "what are the latency tradeoffs", "CAP analysis", "PACELC").

### What to Expect

**Single-axis commands** run the analysis directly - Claude reads the reference for that axis, scans the codebase, and reports findings.

**Full analysis** (`explain-system-tradeoffs`) launches **six parallel subagents**, one per axis. Each subagent reads its own reference file and independently scans the codebase. The main agent then collects the six per-axis reports and produces a **cross-axis synthesis** - the part that requires seeing all six axes together: where tradeoff choices on one axis conflict with choices on another (e.g., AP consistency paired with synchronous saga coordination).

Each finding is backed by evidence classified into three tiers:

| Tier | What it means | Examples |
|------|---------------|---------|
| **A - Hard commitments** | User-facing guarantees, wire-protocol requirements | SLA language, quorum rules, schema invariants |
| **B - Mechanism evidence** | Concrete mechanisms enforcing the property | Consensus protocols, circuit breaker configs, GC flags, compaction strategies |
| **C - Operational signatures** | What engineers actually protect in production | Dashboards, alerts, SLO definitions, runbooks, error budgets |

The report distinguishes **deliberate choices** (asymmetric config, tuned values, documented rationale) from **accidental defaults** (framework defaults, copy-pasted settings, uniform config). Deliberate asymmetry - different compaction strategies per table, different TTLs per cache key, different timeout budgets per downstream call - is the hallmark of genuine tradeoff-making.

**Systems:** Any distributed system - microservices, modular monoliths, event-driven, serverless. Many indicators (caching, thread pools, GC tuning, storage engines, schema evolution) also apply to non-distributed systems with performance or reliability requirements.

---

## progressive-disclosure

Analyze and restructure how a repository progressively discloses its documentation through soul files.

`3 skills` · `Documentation structure analysis` · `Context rot prevention`

Soul files (CLAUDE.md, AGENTS.md, GEMINI.md, COPILOT.md) are the primary way repositories communicate context to AI agents. As projects grow, these files accumulate inline content that should live elsewhere, dangling references to documents that were moved or deleted, and orphaned files that no agent ever loads. Progressive disclosure breaks down: agents either miss critical context or are overwhelmed with everything at once.

This plugin maps how a repository's documentation is structured for AI agent consumption, detects orphaned documents and context rot risks, and restructures root configuration files into thematic, book-style indexes with clear reference hierarchies.

| Command | What it does |
|---------|-------------|
| `progressive-disclosure` | Auto-route: analyze or restructure based on context |
| `progressive-disclosure:analyze` | Map documentation references, find orphaned docs, report anti-patterns |
| `progressive-disclosure:restructure` | Restructure soul file into a thematic, book-style index |

**Trigger** - Ask Claude to "analyze documentation structure", "audit progressive disclosure", "find orphaned docs", "restructure CLAUDE.md", "create a documentation index", or mention soul file organization, context rot prevention, or documentation hierarchy.

---

## retrospective

Developer-AI workflow analysis for Claude Code.

`5 dimensions` · `10 collaboration antipatterns` · `Feedback loop tracking`

Most developers never look at their Claude Code session logs. Those logs are a goldmine of improvement signals - correction spirals, wasted effort, emotional escalation, repeated manual workflows, silent abandonment. By the time you notice these patterns yourself, you've already lost hours to them.

This plugin reads your session logs from the last 3 months and runs a structured retrospective across five dimensions. Each retrospective builds on previous ones - tracking whether past recommendations were acted on and whether the collaboration is actually improving.

| Dimension | Question It Answers |
|-----------|-------------------|
| **What Went Well** | Which interactions were efficient, successful, and worth repeating? |
| **What Didn't Go Well** | Where did the collaboration break down, waste time, or produce poor results? |
| **Skill Opportunities** | What repeated requests or workflows should become reusable skills? |
| **Workflow Optimization** | How can subagents, hooks, and automation reduce manual effort? |
| **Collaboration Antipatterns** | What common developer-AI pitfalls are showing up? |

### How to Use

Run a full retrospective or focus on a single dimension:

| Command | What it analyzes |
|---------|-----------------|
| `retrospective` / `retrospective all` | All five dimensions |
| `retrospective wins` / `retrospective good` | What Went Well |
| `retrospective problems` / `retrospective bad` | What Didn't Go Well |
| `retrospective skills` | Skill & Slash Command Opportunities |
| `retrospective workflow` / `retrospective automation` | Workflow Optimization |
| `retrospective antipatterns` | Collaboration Antipatterns |

**Trigger** - Ask Claude to run a retrospective, review your sessions, analyze your Claude usage, suggest workflow improvements, or mention a dimension by name ("what went well", "what should I automate", "find collaboration antipatterns").

### What to Expect

| Capability | How it works |
|------------|-------------|
| **Feedback loop** | Each retro writes a report to `docs/retrospective/`. The next retro reads previous reports and checks whether you acted on past recommendations. Recurring issues get escalated. |
| **Root cause analysis** | Goes beyond counting correction spirals - identifies whether the cause is a missing CLAUDE.md rule, a vague prompt pattern, or an architectural mismatch. |
| **Emotional signal detection** | Detects frustration escalation, resignation, and silent abandonment - problems that turn-counting alone misses. |
| **Strength-to-weakness mapping** | Connects what works well to what doesn't - if you specify constraints effectively for new code, can you apply that to refactoring where scope creep keeps happening? |

Each finding comes with evidence from your sessions, a root cause, and a concrete suggestion (skill skeleton, hook config, CLAUDE.md addition). Suggestions are rated by effort, impact, and concerns about measurability. The report includes a dimension scorecard (1-5 scale) and prioritized top 3 recommendations.

**Scope:** Reads session logs from `~/.claude/projects/` - requires at least one prior Claude Code session.

---

## onboarding

Project onboarding for Claude Code.

`1 skill` · `6-step briefing`

Starting a new session or resuming after a break? This plugin gathers context from multiple sources - project instructions, git state, issue tracker, and build system - and produces a concise status briefing so you can get oriented fast.

| Source | What It Checks |
|--------|---------------|
| **Project instructions** | AGENTS.md / CLAUDE.md - conventions, tech stack, rules |
| **Git status** | Current branch, uncommitted changes, ahead/behind remote |
| **Recent history** | Last 15 commits - what was worked on and when |
| **Issue tracker** | Ready issues (no blockers) and in-progress work |
| **Build system** | Justfile/Makefile - how to run tests, CI, and the project |

### How to Use

| Command | What it does |
|---------|-------------|
| `onboard` | Full project onboarding briefing |

**Trigger** - Ask Claude to onboard, get oriented, catch you up, show project state, or suggest what to work on next.

---

## sessionlog

Export Claude Code session logs as portable conversation files.

`7 skills` · `1 export script` · `JSON + TXT output` · `Batch export`

Every Claude Code session is stored as JSONL in `~/.claude/projects/`, but that format is internal — you can't feed it to another LLM, share it with a colleague, or archive it alongside your code. This plugin converts session logs into two portable formats: standard LLM conversation JSON (the `{role, content}` array format used by OpenAI, Anthropic, and every major inference API) and a human-readable TXT transcript.

| Command | What it does |
|---------|-------------|
| `sessionlog:info` | Show current session ID, log file path, and project session directory |
| `sessionlog:export` | Export current session to JSON + TXT (default: `docs/sessionlogs/`) |
| `sessionlog:export-all` | Batch-export every session for the current project |
| `sessionlog:compact` | Compress current session into a resumable context file |
| `sessionlog:continue` | Restore context from a previously compacted session |
| `sessionlog:tokenusage` | Report input/output token usage for the current session |
| `sessionlog:recap` | Quick TLDR summary of recent sessions |

**JSON output** follows the de facto standard for multi-turn LLM conversations:

```json
[
  {"role": "user", "content": "Hello"},
  {"role": "assistant", "content": [{"type": "text", "text": "Hi there!"}]}
]
```

**TXT output** is a plain-text transcript:

```
Session: f6c53fff-d3a3-460f-8347-11e2b7c757f8

[user] Hello

[assistant] Hi there!
```

**Trigger** — Ask Claude to "show session info", "export session log", "export all sessions", "compact session", "continue session", "token usage", "recap sessions", or mention session log export.

---

## handoff

Session handoff and continuation for Claude Code.

`3 skills` · `Structured handoff documents` · `Cross-session continuity`

Context is lost at session boundaries — compaction, new windows, switching agents, or picking up work after a break. The common workaround (paste a summary) is lossy and manual. This plugin compacts the current session into a structured handoff document saved to `docs/handoffs/`, then helps a fresh agent load and continue that work with full intent, stance, and tier-sorted file references.

Handoff documents follow a fixed schema: next action, goal, intent (what to optimize for and what to skip), stance and behavioral rules, status, tier-organized file references, decisions, dead-ends, and open questions. The `create` skill verifies the inferred intent with you before saving. The `continue` skill reads the document, follows prior-handoff chains, and summarizes back before acting.

| Command | What it does |
|---------|-------------|
| `handoff` | Auto-route: create a new handoff or continue from an existing one |
| `handoff:create` | Compact the current session into a structured handoff document |
| `handoff:continue` | Find and resume work from a previous handoff |

**Trigger** - Ask Claude to "hand off", "create a handoff", "wrap up for the next session", "pass this to another agent", "continue from a handoff", "pick up where I left off", or mention session continuity, handoff documents, or task continuation.

---

## iso27001-sdlc

ISO 27001:2022 software development compliance scanner for Claude Code.

`10 core controls` · `5 supporting controls` · `Two-phase scan → score architecture` · `Monorepo aware`

ISO 27001 certification requires demonstrating that your software development practices meet specific security controls - but most of those controls live in code, CI/CD configs, and repo artifacts that nobody systematically checks. Teams discover gaps during expensive audit prep, not during development.

This plugin scans your repository against the Annex A software development controls (8.4, 8.25–8.33) and produces a compliance gap report with evidence, status ratings, and concrete fix suggestions.

| Control | Focus |
|---------|-------|
| **8.4** | Access to source code - CODEOWNERS, branch protection, signed commits |
| **8.25** | Secure development life cycle - PR templates, CI security gates, SDLC policy |
| **8.26** | Application security requirements - security in issue templates, NFR checklists |
| **8.27** | Secure architecture - architecture docs, threat models, security design principles |
| **8.28** | Secure coding - linters, SAST, secrets scanning, dependency management |
| **8.29** | Security testing - SAST/DAST/SCA in CI, container scanning, security test files |
| **8.30** | Outsourced development - third-party contribution policies, supplier requirements |
| **8.31** | Separation of environments - env-specific configs, IaC separation, data protection |
| **8.32** | Change management - PR workflows, changelogs, rollback procedures, deployment gates |
| **8.33** | Test information and data - synthetic data, fixture factories, data masking |

### How It Works

The skill uses a two-phase architecture that separates evidence collection from compliance scoring:

| Phase | What it does |
|-------|-------------|
| **Phase 1 - Scan** | Runs `scan_repo.py` to collect all file evidence into a single JSON structure. Deterministic, no judgment calls. |
| **Phase 2 - Score** | Reads the JSON evidence and applies scoring rules from the controls reference to produce the markdown report. |

This ensures the same file never gets assessed differently across controls. Evidence is collected once, referenced everywhere.

### How to Use

| Command | What it does |
|---------|-------------|
| `iso27001-sdlc` | Full compliance scan of all 10 core + 5 supporting controls |

**Trigger** - Ask Claude to check ISO 27001 compliance, run a security audit, check Annex A controls, assess SDLC compliance, or mention audit readiness for software development controls.

Each control is rated PASS / WARNING / FAIL / NOT APPLICABLE / MANUAL REVIEW NEEDED with file-level evidence and concrete remediation steps. The report includes an executive summary with overall posture (STRONG / MODERATE / WEAK / CRITICAL GAPS), a prioritized action list, and an appendix of analysis limitations.

After the scan, you can ask Claude to generate template files for any missing documents or configurations.

**Monorepo aware:** Detects monorepos and produces one aggregate report with per-sub-project coverage summaries rather than per-package reports.

**Scope-honest:** The scan is explicit about what it can and cannot verify. Many ISO 27001 controls are process/organizational - the scan checks for artifacts and configurations, not whether processes are actually followed. Gap flags tell you what an auditor will expect to see beyond the repository.

---

## cache-money

Keep the Anthropic prompt cache warm during Claude Code sessions - especially during peak hours.

`1 skill` · `1 reference doc` · `TTL-adaptive` · `Peak-hour aware`

Every API call in Claude Code sends the full conversation context to the model. Anthropic caches this prefix server-side - cached tokens cost ~90% less than uncached. But the cache expires after a TTL period of inactivity, and the next call pays full cache-write price for the entire context (up to 1M tokens).

| TTL Tier | Duration | Cache Write Cost | Who Gets It |
|----------|----------|-----------------|-------------|
| **Default** | 5 minutes | 1.25x base input | All plans - CLI and API always use this unless explicit `ttl: "1h"` |
| **Extended** | 1 hour | 2x base input | Max-tier plans (server-side in Claude Code UI), or explicit `ttl: "1h"` via API |

During **peak hours** (weekdays 5am–11am PT), Anthropic's rolling session limits are consumed faster. Cache misses during peak windows are doubly expensive: full rebuild cost plus faster quota burn.

This plugin detects your cache TTL tier and schedules pings accordingly - every 4 minutes for 5-min TTL, every 55 minutes for 1-hour TTL. Each ping is a minimal API call that renews the cache at negligible cost.

| Command | What it does |
|---------|-------------|
| `cache-money` | Detect TTL tier, assess peak-hour timing, start the cache ping loop |

**Trigger** - Ask Claude to "keep the cache warm", "save tokens", "start cache ping", "reduce token usage", or mention prompt cache optimization.

---

## logbook

Session log analytics for Claude Code.

`2 skills` · `1 analysis script` · `Per-project/branch breakdown` · `Monthly + yearly reports`

Every Claude Code session is logged to `~/.claude/projects/` as JSONL files with timestamps. This plugin analyzes those logs to answer two questions: **how much time** did you spend on each project, and **how many messages** did you exchange?

Results are broken down per project with branches grouped under their parent. Git worktree variants (`-git-<branch>`, `--claude-worktrees-<branch>`) are automatically merged into the base project. Idle gaps > 15 minutes are excluded from time calculations.

| Command | What it does |
|---------|-------------|
| `logbook:time` | Generate time-per-project reports - monthly + yearly markdown files with inline top-10 preview |
| `logbook:messages` | Generate message-count reports - your messages vs agent messages, per project/branch |

Each command produces:
- **Monthly reports:** `YYYYMM-logbook-time.md` / `YYYYMM-logbook-messages.md`
- **Yearly reports:** `YYYY-logbook-time.md` / `YYYY-logbook-messages.md`
- **Inline preview:** Top 10 projects table shown directly in the terminal

**Trigger** - Ask Claude about "time spent per project", "session stats", "message count", "usage report", "logbook", or mention time tracking or session analysis.

**CLI usage:**
```bash
python3 plugins/logbook/scripts/logbook.py time --preview          # top-10 table only
python3 plugins/logbook/scripts/logbook.py messages --out docs/reports  # generate all reports
python3 plugins/logbook/scripts/logbook.py time --year 2026 --month 3   # single month
```

---

## changelog

Generate and maintain `CHANGELOG.md` files from git commit history.

`3 skills` · `Keep a Changelog format` · `Semantic Versioning` · `Auto-detect create vs update`

Analyzes git commits and tags to produce human-readable changelogs following the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) standard. Commits are classified into six categories (Added, Changed, Deprecated, Removed, Fixed, Security) using conventional commit prefixes and keyword matching. Merge commits and internal-only changes are filtered out. Breaking changes are surfaced with `**BREAKING:**` prefixes and migration guidance.

| Command | What it does |
|---------|-------------|
| `changelog` | Auto-detects whether to create or update based on file existence |
| `changelog:create` | Creates a new `CHANGELOG.md` from the full git history |
| `changelog:update` | Appends new entries since the last documented version |

The update skill uses a 3-strategy boundary detection (tag match, date match, content match) to find where the existing changelog left off. If no new commits exist, it reports the changelog is already up to date without modifying the file.

**Trigger** - Ask Claude to "update the changelog", "generate a changelog", "create CHANGELOG.md", "write release notes", or mention changelog generation.

---

## claudeignore

Generate and maintain `.claudeignore` files for Claude Code projects.

`3 skills`

Context tokens are finite. Build artifacts, caches, vendored dependencies, and large non-source directories consume them without adding value. This plugin analyzes your repository structure and produces a categorized `.claudeignore` file that excludes the noise — so Claude sees only the code that matters.

| Command | What it does |
|---------|-------------|
| `claudeignore` | Auto-detect: create a new `.claudeignore` or update the existing one |
| `claudeignore:create` | Create a `.claudeignore` from scratch by scanning the repo |
| `claudeignore:update` | Add, remove, or revise entries in an existing `.claudeignore` |

**Trigger** - Ask Claude to "create a claudeignore", "update claudeignore", "optimize context", "ignore folders", "reduce token usage", "set up .claudeignore", or mention context window optimization.

---

## communicator

Communication-style toolkit for Claude Code.

`1 skill`

Every word in a response competes for attention. Most AI responses pad, recap, and hand-hold. This plugin installs a communication discipline that cuts all of that — leaving only signal.

| Skill | What it does |
|-------|-------------|
| `communicator:tldr` | Switch Claude into military-style BLUF (Bottom Line Up Front) mode — extreme brevity, conclusion last, bullets over prose, no filler |

### tldr

The `tldr` skill enforces terse, instantly-parseable output structured around four elements:

1. **Critical issues only** — real bugs, blockers, security problems as a bullet list
2. **Chain of events** — coherent reasoning in bullets: assumption → goal → step → insight
3. **Actionable next step** — exact command, file change, or decision needed
4. **Bottom line** — one-sentence conclusion on its own line at the end

Format rules: bullets over paragraphs, active voice, no filler phrases ("Additionally", "Furthermore", "Great question!"), no meta-commentary, no preambles, no recaps. Assumes competence.

**Trigger** — Type `tldr`, `/tldr`, `short mode`, `be brief`, or `concise mode`. Once active, shapes all responses until you ask for normal output.

---

## diagrams

Diagramming toolkit for Claude Code.

`4 skills`

Diagrams live in multiple formats depending on context — ASCII art for inline terminal output, Mermaid for Markdown and docs, Wardley maps for strategic planning. This plugin routes your diagram request to the right format-specific skill automatically.

| Command | What it does |
|---------|-------------|
| `diagrams` | Auto-route to the right format based on the request |
| `diagrams:ascii-art` | Draw diagrams using CP437 box-drawing characters (┌─┐, ╔═╗, ░▒▓█) — never + - \| /, max 80 chars wide |
| `diagrams:mermaid` | Generate Mermaid diagrams — flowcharts, sequence, class, state, ER, gantt |
| `diagrams:wardley` | Generate Wardley maps in the WTG2/wardleyToGo DSL (`.wtg2` files for SVG rendering via wtg2svg) |

Default format when unspecified: `diagrams:ascii-art` (renders inline everywhere). Extensible — add a new skill per format and a row to the router table.

**Trigger** - Ask Claude to "draw a diagram", "diagram this", "make a chart", "visualize this as a diagram", "ascii diagram", "mermaid diagram", "flowchart", or "wardley map".

---

## agent-guardrails

Data-driven agent behavioral guardrails for Claude Code sessions.

`4 skills` · `6 rules` · `Stop hook` · `Iterative refinement`

Enforces agent discipline through a Stop hook that detects anti-patterns in assistant output: guessing without verification, stalling instead of acting, asking preferences instead of deciding, claiming completion without evidence, skipping work, and dismissing issues without investigation. Feedback messages guide the model toward the correct behavior without revealing which pattern triggered detection.

| Command | What it does |
|---------|-------------|
| `agent-guardrails:analyze` | Scan session logs for anti-patterns — produces ranked frequency report with excerpts |
| `agent-guardrails:install` | Install all 6 rules into `.claude/` — works immediately, no restart. Re-run to upgrade after plugin update. |
| `agent-guardrails:test` | Verify installed hook patterns — runs 2 test phrases per rule, stops on first failure |
| `agent-guardrails:update` | Re-analyze logs against installed rules — finds false positives, missed patterns, suggests refinements |

**No external dependencies** — just bash, jq, and grep. No hookify plugin required.

**Workflow:** `analyze` → `install` → use for a while → `update` → repeat. Or skip straight to `install` to get the curated set immediately.

**Trigger** - Ask Claude to "analyze my sessions for anti-patterns", "install agent guardrails", "set up behavioral guardrails", "update my guardrails", "refine guardrail rules", or mention anti-pattern detection.

---

## fixclaude

Production-grade CLAUDE.md directives that override Claude Code's built-in limitations.

`4 skills` · `9 directive sections` · `Gap analysis`

Reverse the built-in Claude Code limitations discovered in the source code leak. Installs production-grade agent directives covering pre-work discipline, intent understanding, code quality, context management, file system as state, edit safety, prompt cache awareness, self-improvement, and housekeeping.

| Command | What it does |
|---------|-------------|
| `fixclaude:install` | Auto-detect and route to init or update |
| `fixclaude:init` | Create a new CLAUDE.md with all 9 directive sections |
| `fixclaude:update` | Merge directives into an existing CLAUDE.md without destroying project-specific instructions |
| `fixclaude:analyze` | Gap analysis — maps each directive to a specific Claude Code limitation |

**Trigger** - Ask Claude to "fix claude", "create claude md", "install fixclaude directives", "analyze claude md gaps", or mention Claude Code limitations.

---

## guard

Helper skill for the `guard` CLI — protect files from accidental AI modification.

`1 skill`

AI agents can edit any file they can read. `guard` sets the immutable flag and root ownership on files you want to protect, making accidental overwrites impossible at the OS level. This plugin composes the right `guard` CLI commands for five intents: init, create-collection, remove-collection, clear-all, and info.

| Intent | What it does |
|--------|-------------|
| `guard init` | Set up guard and create a `.guardfile` in the project |
| `guard:create-collection` | Build a protected collection from a file list or description |
| `guard:remove-collection` | Remove a collection (unguard its files) |
| `guard:clear-all` | Restore everything to unguarded state and wipe the registry |
| `guard:info` | Show all collections and loose guarded files |

**Sudo rule:** The agent runs without root. Operations that change a file's guard state (enable, disable, toggle) require `sudo` — the skill prints the exact `sudo guard …` command for you to run rather than executing it directly.

**Trigger** - Ask Claude to "init guard", "guard my test files", "create a guard collection", "remove guard collection", "clear all guard", "guard status", or "what's guarded".

---

## context-research

Autonomous AI research pipeline that identifies, analyzes, and synthesizes SOTA research via Hugging Face and ArXiv.

`1 skill` · `3-phase pipeline` · `Weighted ranking` · `Parallel extraction`

Designed for engineering-grade deep dives into AI topics. Searches Hugging Face papers, ranks by relevance/recency/impact, extracts benchmarks and metrics from full-text markdown, and produces thematic synthesis reports organized by architectural shifts, universal bottlenecks, and production trade-offs.

**Phases:**
1. **Discovery & Ranking** — Weighted scoring (50% relevance, 25% recency, 25% impact) with sparse-result fallback to web search
2. **Deep Extraction** — Parallel fetch of top 3-5 papers with shallow-content detection and ArXiv PDF fallback
3. **Thematic Synthesis** — Cross-paper taxonomy: architectural shifts, bottlenecks/patterns, production trade-offs

**Trigger** - Ask for a deep dive, SOTA analysis, or implementation risk assessment on any AI topic (e.g., "research KV-cache optimization", "context compression SOTA").

---

## orchestrator

Evidence-based model routing for engineering tasks.

`1 skill` · `30-category taxonomy` · `15 decision rules` · `Multi-model workflow patterns`

Not all AI models are equally good at all tasks. Routing architecture planning to Haiku wastes quality; routing boilerplate to Opus wastes money. This plugin produces evidence-backed routing plans that map each work unit to the best-suited model — Claude, GPT, Gemini, or open-weight — with rationale, context briefings, and failure-mode warnings.

| Command | What it does |
|---------|-------------|
| `orchestrator:maptasks` | Produce a routing plan for a task or task list — checks decomposition sufficiency, categorizes each unit, assigns models, emits briefings |

### How It Works

1. **Breakdown check** — Verifies each task unit is scoped to a single category, model tier, artifact, and context budget before routing.
2. **Category lookup** — Maps each leaf unit to one of 30 task categories (architecture, boilerplate, frontend, debug, security audit, structured output, etc.).
3. **Model selection** — Applies 15 decision rules grounded in April 2026 practitioner benchmarks.
4. **Output** — A routing plan with model assignments, rationale citing category + rule numbers, per-unit context briefings, and a cost summary.

### Three-Tier Strategy

Every routing plan distributes work across tiers:

| Tier | Share | Models |
|------|-------|--------|
| **Flagship** | 5–10% | Opus 4.6, GPT-5.4 Pro, Gemini 3.1 Pro |
| **Mid-tier** | 40–50% | Sonnet 4.6, GPT-5.4, Codex, Gemini 2.5 Pro |
| **Fast** | 30–40% | Haiku 4.5, GPT-5.4 mini/nano, Gemini 3 Flash |

**Trigger** - Ask Claude to "route these tasks", "which model should handle this", "map tasks to models", "build a routing plan", or "maptasks".

---

## tokeneconomics

Analyze Claude Code session token usage to flag waste and optimization opportunities.

`1 skill` · `6 analysis dimensions` · `Scoring & cost estimation`

Reviews per-message token data from Claude Code sessions, analyzing cache efficiency, conversation sprawl, model selection, and estimated costs. Produces a scored report with actionable recommendations for reducing token spend.

**Trigger** - Ask to "analyze token usage", "check token efficiency", "audit token spend", or "reduce token costs".

---

## terminator

Stop hooks that end a Claude Code session when a kill phrase appears in the agent's final message.

`6 skills` · `2 termination scripts` · `Local and global scope`

Claude Code sessions don't end themselves. Terminator installs a Stop hook that watches for a configured kill phrase in the agent's last message — when found, it ends Claude (single-kill) or ends Claude and the terminal that launched it (double-kill). Useful for autonomous sessions, CI pipelines, and any workflow where human presence isn't guaranteed.

| Command | What it does |
|---------|-------------|
| `terminator` | Router — auto-detect intent and dispatch to the right subcommand |
| `terminator:install` | Install single-kill and/or double-kill hooks at local or global scope |
| `terminator:remove` | Uninstall the hooks |
| `terminator:update` | Change the kill phrase or toggle case sensitivity |
| `terminator:info` | Show configured kill phrases for local and global scope |
| `terminator:whendone` | Have Claude end the session by uttering the kill phrase once work is complete |

**Two scripts:**
- **single-kill** — ends Claude; terminal stays open
- **double-kill** — ends Claude, then walks the process tree to terminate the top-most shell ancestor

Both scripts never signal pid ≤ 2 and compose safely with existing Stop hooks.

**Trigger** - Ask Claude to "install the kill hook", "set up a kill phrase", "single kill", "double kill", "remove the terminator hook", "change the kill phrase", "terminate when done", or "terminator".

---

## arc42

Generate arc42 architecture documentation from a codebase.

`12 sections` · `Mermaid diagrams where structure is code-verifiable` · `GAP flags where human input is needed`

Software architecture decisions accumulate in code, configuration, and deployment artifacts. This plugin reads your repository into a structured evidence base, then authors all 12 arc42 sections from that evidence. Where the code gives high-confidence structure, it generates Mermaid diagrams. Where human context is needed (goals, constraints, quality requirements), it emits explicit `<!-- GAP -->` flags rather than fabricating content.

| Command | What it does |
|---------|-------------|
| `/arc42:generate` | Full run: scan repo → evidence base → author all 12 sections → `docs/arc42/` |
| `/arc42:fill-gaps` | Guided walkthrough of all open `<!-- GAP -->` flags — prompts for missing context and fills each section |
| `/arc42:gap-check` | *(coming)* Report all open GAPs without filling them |
| `/arc42:drift-check` | *(coming)* Detect drift between the evidence base and output sections |

Diagrams use Mermaid and are generated only where the code provides enough structure to be confident — typically the building block view (§5), runtime view (§6), and deployment view (§7). Sections where structure cannot be inferred from code alone are left as prose with `<!-- GAP -->` flags.

**Trigger** — Ask Claude to "generate arc42 docs", "document the architecture", "run arc42", or "fill in the arc42 gaps".

**License:** CC BY-SA 4.0 (this plugin only; all other plugins are MIT). Knowledge base adapted from arc42 by Peter Hruschka & Gernot Starke — see `plugins/arc42/NOTICE`.

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
  ├── beyond-solid-principles/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       └── beyond-solid-principles/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── soc.md          # Separation of Concerns patterns
  │               ├── srp-sys.md      # Single Responsibility (system-level)
  │               ├── dry.md          # Don't Repeat Yourself patterns
  │               ├── demeter.md      # Law of Demeter patterns
  │               ├── coupling.md     # Loose Coupling, High Cohesion
  │               ├── evolvability.md # Build for Change patterns
  │               ├── resilience.md   # Design for Failure patterns
  │               ├── kiss.md         # KISS patterns
  │               ├── pola.md         # Principle of Least Surprise
  │               └── yagni.md        # YAGNI patterns
  ├── archibald/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── archibald/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── cyclic-dependency.md      # Cyclic Dependency smell
  │               ├── unstable-dependency.md    # Unstable Dependency smell
  │               ├── hub-like-dependency.md    # Hub-Like Dependency smell
  │               ├── god-component.md          # God Component smell
  │               ├── feature-concentration.md  # Feature Concentration smell
  │               ├── scattered-functionality.md # Scattered Functionality smell
  │               ├── ambiguous-interface.md    # Ambiguous Interface smell
  │               ├── antipatterns.md           # 13 architectural antipatterns
  │               ├── metrics.md               # Coupling, cohesion, complexity metrics
  │               ├── dependency-structure.md   # DSM analysis
  │               ├── risk-analysis.md         # Risk & trade-off analysis
  │               └── technical-debt.md        # Technical debt assessment
  ├── kiss/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── kiss/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── complexity.md   # Code complexity patterns
  │               ├── abstraction.md  # Over-abstraction patterns
  │               ├── redundancy.md   # Redundancy patterns
  │               └── architecture.md # Architecture complexity patterns
  ├── appsec/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── skills/                     # 62 skills (OWASP, STRIDE, PASTA, LINDDUN, specialized, education)
  │   ├── agents/                     # 7 agents (6 red team + consolidator)
  │   ├── hooks/
  │   │   └── hooks.json              # PostToolUse hooks (plan review, secret detection)
  │   └── shared/
  │       ├── frameworks/             # 8 framework reference docs
  │       └── schemas/                # Findings, flags, scanners schemas
  ├── spec-writer/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       └── spec-writer/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── vision.md       # L0 - Product Vision reference
  │               ├── brs.md          # L1 - Business Requirements reference
  │               ├── srs.md          # L2 - Software Requirements reference
  │               ├── architecture.md # L3 - Architecture & Design reference
  │               └── verification.md # L4 - Test Verification reference
  ├── spec-dd/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── spec-dd/
  │           ├── SKILL.md            # Skill definition & phase router
  │           └── references/
  │               ├── specification.md                    # Behavioral specification guide
  │               ├── test-specification.md               # Test specification guide
  │               ├── test-implementation-specification.md # Test implementation specification guide
  │               └── review.md                           # Alignment review guide
  ├── explain-system-tradeoffs/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       └── explain-system-tradeoffs/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── consistency.md  # Consistency & Availability axis
  │               ├── latency.md      # Latency & Throughput axis
  │               ├── data-distribution.md # Data Distribution axis
  │               ├── transactions.md # Transaction Boundaries axis
  │               ├── resilience.md   # Resilience & Failure Isolation axis
  │               └── operations.md   # Observability, Security & Cost axis
  ├── retrospective/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── retrospective/
  │           ├── SKILL.md            # Skill definition & workflow
  │           └── references/
  │               ├── success-patterns.md          # Effective collaboration patterns
  │               ├── failure-patterns.md           # Wasted effort and breakdowns
  │               ├── collaboration-antipatterns.md # Developer-AI pitfalls
  │               ├── skill-opportunities.md        # Automatable pattern detection
  │               └── workflow-optimization.md      # Subagents, hooks, automation
  ├── iso27001-sdlc/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── iso27001-sdlc/
  │           ├── SKILL.md            # Skill definition & two-phase workflow
  │           ├── scripts/
  │           │   └── scan_repo.py    # Phase 1: deterministic evidence collection
  │           └── references/
  │               └── controls.md     # Per-control scoring rules & evidence mapping
  ├── cache-money/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       └── cache-money/
  │           ├── SKILL.md            # Skill definition & ping loop workflow
  │           └── references/
  │               └── cache-mechanics.md  # Anthropic prompt cache technical details
  ├── logbook/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── scripts/
  │   │   └── logbook.py              # Session log analysis engine
  │   └── skills/
  │       ├── time/
  │       │   └── SKILL.md            # Time-per-project report skill
  │       └── messages/
  │           └── SKILL.md            # Messages-per-project report skill
  ├── changelog/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       ├── changelog/
  │       │   ├── SKILL.md            # Router: auto-detect create vs update
  │       │   └── references/
  │       │       └── format-guide.md # Keep a Changelog format spec
  │       ├── create/
  │       │   └── SKILL.md            # Create new CHANGELOG.md from full history
  │       └── update/
  │           └── SKILL.md            # Update existing CHANGELOG.md with new entries
  ├── claudeignore/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       ├── claudeignore/
  │       │   └── SKILL.md            # Router: create vs update
  │       ├── create/
  │       │   └── SKILL.md            # Create .claudeignore from repo scan
  │       └── update/
  │           └── SKILL.md            # Update existing .claudeignore
  ├── communicator/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── tldr/
  │           └── SKILL.md            # Military-style BLUF communication mode
  ├── diagrams/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       ├── diagrams/
  │       │   └── SKILL.md            # Router: detect format and dispatch
  │       ├── ascii-art/
  │       │   └── SKILL.md            # CP437 box-drawing diagrams
  │       ├── mermaid/
  │       │   └── SKILL.md            # Mermaid flowcharts, sequence, ER, gantt
  │       └── wardley/
  │           └── SKILL.md            # Wardley maps in WTG2 DSL
  ├── agent-guardrails/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   ├── rules/                      # Rule definitions (source of truth)
  │   │   ├── no-guessing.md
  │   │   ├── no-stalling.md
  │   │   ├── no-preference-asking.md
  │   │   ├── no-false-completion.md
  │   │   ├── no-skipping.md
  │   │   ├── no-dismissing.md
  │   │   ├── no-echo-back.md
  │   │   ├── no-robotic-comments.md
  │   │   ├── no-over-explaining.md
  │   │   ├── no-blind-edit.md
  │   │   └── no-destructive-bash.md
  │   ├── templates/                   # Hook script templates
  │   │   ├── stop-guardrails.sh       # Stop hook (9 output rules)
  │   │   ├── pretooluse-edit-guardrail.sh   # PreToolUse: no-blind-edit
  │   │   ├── posttooluse-read-tracker.sh    # PostToolUse: read tracking
  │   │   └── pretooluse-bash-guardrail.sh   # PreToolUse: no-destructive-bash
  │   └── skills/
  │       ├── analyze/
  │       │   └── SKILL.md            # Scan session logs for anti-patterns
  │       ├── install/
  │       │   └── SKILL.md            # Install curated or custom rules
  │       └── update/
  │           └── SKILL.md            # Refine rules based on usage data
  ├── fixclaude/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   ├── references/
  │   │   └── claude-md-template.md   # Production-grade CLAUDE.md template
  │   └── skills/
  │       ├── install/
  │       │   └── SKILL.md            # Auto-detect init vs update
  │       ├── init/
  │       │   └── SKILL.md            # Create new CLAUDE.md
  │       ├── update/
  │       │   └── SKILL.md            # Merge into existing CLAUDE.md
  │       └── analyze/
  │           ├── SKILL.md            # Gap analysis
  │           └── references/
  │               └── source-leak-findings.md  # 7 documented findings
  ├── guard/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   └── skills/
  │       └── guard/
  │           └── SKILL.md            # Guard CLI helper (init, collections, clear, info)
  ├── orchestrator/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   └── skills/
  │       └── maptasks/
  │           └── SKILL.md            # Evidence-based model routing plan generator
  ├── terminator/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   ├── templates/
  │   │   ├── single-kill.sh          # Hook: end Claude session
  │   │   └── double-kill.sh          # Hook: end Claude + terminal
  │   └── skills/
  │       ├── terminator/
  │       │   └── SKILL.md            # Router: dispatch to install/remove/update/info/whendone
  │       ├── install/
  │       │   └── SKILL.md            # Install kill hooks at local or global scope
  │       ├── remove/
  │       │   └── SKILL.md            # Uninstall hooks
  │       ├── update/
  │       │   └── SKILL.md            # Change kill phrase or case sensitivity
  │       ├── info/
  │       │   └── SKILL.md            # Show configured kill phrases
  │       └── whendone/
  │           └── SKILL.md            # Self-terminate once work is complete
  └── arc42/
      ├── .claude-plugin/
      │   └── plugin.json             # Plugin manifest (CC-BY-SA-4.0)
      ├── LICENSE                     # CC BY-SA 4.0 license text
      ├── NOTICE                      # arc42 attribution notice
      ├── agents/
      │   ├── evidence-scout.md       # Phase 1: repo scan → evidence base
      │   ├── section-author.md       # Phase 2: evidence → arc42 sections
      │   └── consistency-checker.md  # Phase 3: cross-section coherence check
      ├── commands/
      │   ├── generate.md             # /arc42:generate — full pipeline
      │   ├── fill-gaps.md            # /arc42:fill-gaps — guided GAP walkthrough
      │   ├── gap-check.md            # /arc42:gap-check — report open GAPs (phase 2)
      │   └── drift-check.md          # /arc42:drift-check — detect stale sections (phase 2)
      ├── skills/
      │   └── arc42-framework/
      │       ├── SKILL.md            # Skill router
      │       └── references/         # 12 section guides + conventions + COVERAGE
      └── tests/
          ├── validate_output.py      # Output validator
          ├── check_corpus_contract.py # Corpus derivation contract checker
          └── fixtures/               # Good/bad output fixtures + sample repos
```

---

## FAQ

**What languages does solid-principles support?**
Any OO language - Python, Java, TypeScript, C#, C++, Kotlin, Go (struct methods), Rust (impl blocks). The analysis adapts to the idioms of each language.

**Is solid-principles too strict?**
No. The skill includes pragmatism guidelines. A 50-line script doesn't get the same scrutiny as a large production system.

**What's the difference between solid-principles, beyond-solid-principles, and archibald?**
They form a complementary trio at increasing abstraction levels. solid-principles operates at the class level - single classes, interfaces, and inheritance hierarchies. beyond-solid-principles checks adherence to design principles at the architecture level - modules, services, layers, and system boundaries. archibald assesses structural health through a different lens entirely - smell detection, quantitative metrics, dependency structure analysis, antipattern identification, risk/trade-off analysis, and technical debt measurement. Use solid-principles for "does this class follow good OO design?", beyond-solid-principles for "does this architecture follow sound principles?", and archibald for "how healthy is this architecture structurally?"

**Does beyond-solid-principles require a distributed system?**
No. The principles apply to any codebase with module or package boundaries. For monoliths, the analysis focuses on dependency direction, internal layering, and package cohesion. For distributed systems, it also covers service boundaries, API contracts, failure propagation, and operational resilience.

**Do I need all five spec documents?**
No. Each document can be created independently. Start at whatever level matches your needs. The full walkthrough (`/spec`) is there for when you want the complete suite.

**Can I use spec-writer for an existing project?**
The skill is optimized for greenfield projects, but you can start at any level. For existing projects, `/spec-architecture` and `/spec-test` are often the most useful starting points.

**What's the difference between spec-writer and spec-dd?**
spec-writer creates specification *documents* for greenfield projects - layered from vision through architecture to test plans. spec-dd orchestrates a *development workflow* - it assumes you have (or are writing) a behavioral spec and guides you through deriving tests, planning test implementation, implementing tests (verify they fail), implementing features (make tests pass), and verifying alignment. Use spec-writer when starting a new project and need formal specs. Use spec-dd when you have requirements and want to enforce a spec-first development discipline.

**Does spec-dd write code?**
No. spec-dd produces specification documents, assesses quality, surfaces gaps, and offers handoff prompts for coding agents. When it's time to write test code or implementation code, it proposes a prompt you can give to a coding agent.

**What's the difference between beyond-solid-principles and explain-system-tradeoffs?**
beyond-solid-principles finds *violations* of design principles - things that should be fixed. explain-system-tradeoffs identifies *tradeoff decisions* - things that were chosen (deliberately or not). A system can follow all design principles perfectly and still have interesting tradeoffs to understand. Use beyond-solid-principles for "what's wrong?", use explain-system-tradeoffs for "what was decided and why?"

**What's the difference between K.I.S.S. and the KISS check in beyond-solid-principles?**
beyond-solid-principles includes KISS as one of ten system-level principles, covering architecture-level over-engineering. The standalone K.I.S.S. plugin provides deeper, more granular analysis across four categories - code complexity, over-abstraction, redundancy, and architecture - with 20 specific violation patterns. Use beyond-solid-principles for a broad architecture health check; use K.I.S.S. for a focused simplicity audit.

**Does K.I.S.S. modify my code?**
No. By default it only reports findings. Ask Claude to "fix this" or "simplify it" after an audit to get refactored code.

**Does explain-system-tradeoffs require a distributed system?**
It's most useful for distributed systems, but many tradeoff indicators (caching, thread pools, GC tuning, storage engines, schema evolution) apply to any system with performance or reliability requirements.

**Does retrospective access my data or send anything externally?**
No. Everything stays local. The plugin reads session logs from `~/.claude/projects/` on your machine and writes reports to `docs/retrospective/` in your repo. Nothing leaves your environment.

**How far back does retrospective look?**
The last 3 months of session logs. Each `.jsonl` file in `~/.claude/projects/` has a modification timestamp - the skill includes every file modified within the last 90 days.

**How much context do the plugins use?**
All plugins use progressive disclosure - reference material is loaded only when needed to minimize token usage.

---

## Hooks

Behavioral hooks that enforce assistant discipline by blocking common AI anti-patterns. Bundled with the [agent-guardrails](plugins/agent-guardrails/) plugin - run `/agent-guardrails:install` to set up.

---

## License

MIT — except the `arc42` plugin, which is CC BY-SA 4.0 (its knowledge base is adapted from arc42; see `plugins/arc42/NOTICE`).

---

[GitHub](https://github.com/florianbuetow/claude-code) | [Issues](https://github.com/florianbuetow/claude-code/issues) | [License](LICENSE)
