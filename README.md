# Claude Code Plugins and Skills

![Made with AI](https://img.shields.io/badge/Made%20with-AI-333333?labelColor=f00) ![Verified by Humans](https://img.shields.io/badge/Verified%20by-Humans-333333?labelColor=brightgreen)

A collection of `17 plugins` and `80+ skills` for Claude Code.

## Quickstart

```bash
# 1. Add the marketplace
claude plugin marketplace add florianbuetow/claude-code

# 2. Install plugins (pick what you need)
claude plugin install agent-guardrails
claude plugin install appsec
claude plugin install archibald
claude plugin install beyond-solid-principles
claude plugin install cache-money
claude plugin install changelog
claude plugin install explain-system-tradeoffs
claude plugin install fixclaude
claude plugin install iso27001-sdlc
claude plugin install kiss
claude plugin install logbook
claude plugin install onboarding
claude plugin install retrospective
claude plugin install solid-principles
claude plugin install spec-dd
claude plugin install sessionlog
claude plugin install spec-writer

# 3. Restart Claude Code

# Update all installed plugins to latest versions
claude plugin marketplace update florianbuetow-plugins
```

### Skills

| Skill | Description |
|-------|-------------|
| [agent-guardrails](#agent-guardrails) | Agent behavioral guardrails - 11 rules across Stop, PreToolUse, and PostToolUse hooks |
| [appsec](#appsec) | Comprehensive application security toolbox - 62 skills, 8 frameworks, red team simulation |
| [archibald](#archibald) | Software architecture quality assessment - smells, metrics, antipatterns, dependencies, risks, debt |
| [beyond-solid-principles](#beyond-solid-principles) | System-level architecture principles analysis |
| [cache-money](#cache-money) | Keep the Anthropic prompt cache warm during peak hours - adapts ping interval to your cache TTL (5-min or 1-hour) |
| [changelog](#changelog) | Generate and maintain CHANGELOG.md from git history - Keep a Changelog format with Semantic Versioning |
| [context-research](#context-research) | Autonomous AI research pipeline - discovers, ranks, and synthesizes SOTA papers via Hugging Face & ArXiv |
| [explain-system-tradeoffs](#explain-system-tradeoffs) | Distributed system tradeoff analysis |
| [fixclaude](#fixclaude) | Production-grade CLAUDE.md directives that override Claude Code's built-in limitations |
| [iso27001-sdlc](#iso27001-sdlc) | ISO 27001:2022 software development compliance scanner - Annex A controls 8.4, 8.25–8.33 |
| [K.I.S.S.](#kiss) | Code and architecture simplicity analysis - complexity, abstraction, redundancy, architecture |
| [logbook](#logbook) | Session log analytics - time spent and messages exchanged per project/branch, with monthly + yearly reports |
| [onboarding](#onboarding) | Project onboarding - status briefing from git, issues, and build system |
| [retrospective](#retrospective) | Developer-AI workflow analysis - session log retros with feedback loops |
| [sessionlog](#sessionlog) | Export session logs as standard LLM conversation JSON and TXT transcripts |
| [solid-principles](#solid-principles) | Automated SOLID principles analysis for OO code |
| [spec-dd](#spec-dd) | Specification-driven development workflow |
| [spec-writer](#spec-writer) | Expert-guided software specification documents |

---

## Installation

All plugins are installed from the same marketplace.

```bash
# Add the marketplace (one time)
claude plugin marketplace add florianbuetow/claude-code

# Install any plugin by name
claude plugin install <plugin-name>
```

Restart Claude Code after installing. Available plugins: `solid-principles`, `beyond-solid-principles`, `archibald`, `kiss`, `appsec`, `spec-writer`, `spec-dd`, `explain-system-tradeoffs`, `retrospective`, `onboarding`, `iso27001-sdlc`, `cache-money`, `logbook`, `changelog`, `agent-guardrails`, `fixclaude`, `sessionlog`.

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

`3 skills` · `1 export script` · `JSON + TXT output` · `Batch export`

Every Claude Code session is stored as JSONL in `~/.claude/projects/`, but that format is internal — you can't feed it to another LLM, share it with a colleague, or archive it alongside your code. This plugin converts session logs into two portable formats: standard LLM conversation JSON (the `{role, content}` array format used by OpenAI, Anthropic, and every major inference API) and a human-readable TXT transcript.

| Command | What it does |
|---------|-------------|
| `sessionlog:info` | Show current session ID, log file path, and project session directory |
| `sessionlog:export` | Export current session to JSON + TXT (default: `docs/sessionlogs/`) |
| `sessionlog:export-all` | Batch-export every session for the current project |

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

**Trigger** — Ask Claude to "show session info", "export session log", "export this session", "export all sessions", "convert session to json", or mention session log export.

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

## agent-guardrails

Data-driven agent behavioral guardrails for Claude Code sessions.

`3 skills` · `11 rules` · `3 hook types` · `Iterative refinement`

Enforces agent discipline through three hook types: **Stop hooks** block anti-patterns in assistant output (hedging, stalling, skipping, false completions, plan echoing, robotic comments, over-explaining), **PreToolUse hooks** intercept dangerous tool calls before execution (editing unread files, destructive bash commands), and a **PostToolUse hook** tracks file reads for stateful enforcement.

| Command | What it does |
|---------|-------------|
| `agent-guardrails:analyze` | Scan session logs for anti-patterns - produces ranked frequency report with excerpts |
| `agent-guardrails:install` | Install all 11 rules into `.claude/` - works immediately, no restart. Re-run to upgrade after plugin update. |
| `agent-guardrails:update` | Re-analyze logs against installed rules - finds false positives, missed patterns, suggests refinements |

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
  ├── agent-guardrails/
  │   ├── .claude-plugin/
  │   │   └── plugin.json             # Plugin manifest
  │   ├── LICENSE
  │   ├── rules/                      # Rule definitions (source of truth)
  │   │   ├── no-speculative-language.md
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
  └── fixclaude/
      ├── .claude-plugin/
      │   └── plugin.json             # Plugin manifest
      ├── LICENSE
      ├── references/
      │   └── claude-md-template.md   # Production-grade CLAUDE.md template
      └── skills/
          ├── install/
          │   └── SKILL.md            # Auto-detect init vs update
          ├── init/
          │   └── SKILL.md            # Create new CLAUDE.md
          ├── update/
          │   └── SKILL.md            # Merge into existing CLAUDE.md
          └── analyze/
              ├── SKILL.md            # Gap analysis
              └── references/
                  └── source-leak-findings.md  # 7 documented findings
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

MIT

---

[GitHub](https://github.com/florianbuetow/claude-code) | [Issues](https://github.com/florianbuetow/claude-code/issues) | [License](LICENSE)
