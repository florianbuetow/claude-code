# Claude Code Plugins

![Made with AI](https://img.shields.io/badge/Made%20with-AI-333333?labelColor=f00) ![Verified by Humans](https://img.shields.io/badge/Verified%20by-Humans-333333?labelColor=brightgreen)

A collection of Claude Code plugins for software engineering workflows.

`5 plugins` · `66+ skills`

### Skills

| Skill | Description |
|-------|-------------|
| [appsec](#appsec) | Comprehensive application security toolbox - 62 skills, 8 frameworks, red team simulation |
| [solid-principles](#solid-principles) | Automated SOLID principles analysis for OO code |
| [beyond-solid-principles](#beyond-solid-principles) | System-level architecture principles analysis |
| [spec-writer](#spec-writer) | Expert-guided software specification documents |
| [explain-system-tradeoffs](#explain-system-tradeoffs) | Distributed system tradeoff analysis |

---

## Installation

All plugins are installed from the same marketplace.

**Step 1** - Add the marketplace:

```bash
claude plugin marketplace add florianbuetow/claude-code
```

**Step 2** - Install the plugin(s) you want:

```bash
claude plugin install appsec
claude plugin install solid-principles
claude plugin install beyond-solid-principles
claude plugin install spec-writer
claude plugin install explain-system-tradeoffs
```

**Step 3** - Restart Claude Code.

<details>
<summary>Manual / Development Installation</summary>

```bash
git clone https://github.com/florianbuetow/claude-code.git
cd claude-code
# Load a plugin directory for this session only
claude --plugin-dir ./plugins/appsec
claude --plugin-dir ./plugins/solid-principles
claude --plugin-dir ./plugins/beyond-solid-principles
claude --plugin-dir ./plugins/spec-writer
claude --plugin-dir ./plugins/explain-system-tradeoffs
```

</details>

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

**Hook:** Automatically reviews plans on `ExitPlanMode` and checks for hardcoded secrets on file writes.

**Languages & stacks:** Any - Python, JavaScript/TypeScript, Java, Go, C#, Ruby, PHP, Rust. Detects and uses installed scanners (semgrep, bandit, gitleaks, trivy, etc.) with Claude analysis fallback.

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

## Project Structure

```
.claude-plugin/
  └── marketplace.json                # Plugin registry
plugins/
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
  └── explain-system-tradeoffs/
      ├── .claude-plugin/
      │   └── plugin.json             # Plugin manifest
      └── skills/
          └── explain-system-tradeoffs/
              ├── SKILL.md            # Skill definition & workflow
              └── references/
                  ├── consistency.md  # Consistency & Availability axis
                  ├── latency.md      # Latency & Throughput axis
                  ├── data-distribution.md # Data Distribution axis
                  ├── transactions.md # Transaction Boundaries axis
                  ├── resilience.md   # Resilience & Failure Isolation axis
                  └── operations.md   # Observability, Security & Cost axis
```

---

## FAQ

**What languages does solid-principles support?**
Any OO language - Python, Java, TypeScript, C#, C++, Kotlin, Go (struct methods), Rust (impl blocks). The analysis adapts to the idioms of each language.

**Is solid-principles too strict?**
No. The skill includes pragmatism guidelines. A 50-line script doesn't get the same scrutiny as a large production system.

**What's the difference between solid-principles and beyond-solid-principles?**
solid-principles operates at the class level - single classes, interfaces, and inheritance hierarchies. beyond-solid-principles operates at the architecture level - modules, services, layers, and system boundaries. They complement each other: use solid-principles for OO design quality, beyond-solid-principles for structural health at scale.

**Does beyond-solid-principles require a distributed system?**
No. The principles apply to any codebase with module or package boundaries. For monoliths, the analysis focuses on dependency direction, internal layering, and package cohesion. For distributed systems, it also covers service boundaries, API contracts, failure propagation, and operational resilience.

**Do I need all five spec documents?**
No. Each document can be created independently. Start at whatever level matches your needs. The full walkthrough (`/spec`) is there for when you want the complete suite.

**Can I use spec-writer for an existing project?**
The skill is optimized for greenfield projects, but you can start at any level. For existing projects, `/spec-architecture` and `/spec-test` are often the most useful starting points.

**What's the difference between beyond-solid-principles and explain-system-tradeoffs?**
beyond-solid-principles finds *violations* of design principles - things that should be fixed. explain-system-tradeoffs identifies *tradeoff decisions* - things that were chosen (deliberately or not). A system can follow all design principles perfectly and still have interesting tradeoffs to understand. Use beyond-solid-principles for "what's wrong?", use explain-system-tradeoffs for "what was decided and why?"

**Does explain-system-tradeoffs require a distributed system?**
It's most useful for distributed systems, but many tradeoff indicators (caching, thread pools, GC tuning, storage engines, schema evolution) apply to any system with performance or reliability requirements.

**How much context do the plugins use?**
All plugins use progressive disclosure - reference material is loaded only when needed to minimize token usage.

---

## License

MIT

---

[GitHub](https://github.com/florianbuetow/claude-code) | [Issues](https://github.com/florianbuetow/claude-code/issues) | [License](LICENSE)
