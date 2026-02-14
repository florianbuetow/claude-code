# AppSec Toolbox — Design Document

## Vision

A comprehensive application security toolbox for Claude Code that gives solo developers maximum security feedback before code hits CI/CD. Language-agnostic. Works standalone, gets better with optional scanners. Soft gates that flag critical issues but let you override.

The core principle: **use each tool for what it's actually good at.** Real SAST scanners for pattern detection. Claude for understanding intent, design, and business logic. Red team agents for reasoning about exploitability. Never pretend one can do the other's job.

---

## Architecture

### Three Layers

```
Layer 1: DETECT    — Find real vulnerabilities (scanners + Claude)
Layer 2: ANALYZE   — Understand architecture, threats, attack surface
Layer 3: GUIDE     — Fix issues, harden code, verify remediations
```

### Three Levels of Access

```
Level 1: Orchestrator   /appsec:run              "run everything relevant"
Level 2: Frameworks     /appsec:owasp            "check OWASP Top 10"
Level 3: Focused tools  /appsec:injection        "check A03 specifically"
                        /appsec:owasp --only A03  (same thing, different path)
```

Every tool works standalone. Framework tools orchestrate their categories. The orchestrator picks the right combination based on context. Everything composes.

---

## Subagent Architecture

Every focused tool is a subagent. Framework tools and the orchestrator are dispatchers.

```
/appsec:owasp
    |
    +-- spawn --> [A01: access-control agent]  --+
    +-- spawn --> [A03: injection agent]         |
    +-- spawn --> [A07: auth agent]              +-- parallel
    +-- spawn --> [A10: ssrf agent]              |
    +-- spawn --> [...remaining relevant ones]  --+
                                                  |
                                            consolidator
                                                  |
                                            deduplicate
                                            cross-reference
                                            rank by severity
                                                  |
                                       (if depth=expert)
                                                  |
                                       spawn --> [red team agent]
                                                  |
                                            chain findings
                                            into attack paths
                                                  |
                                            final output
```

### Why Subagents

| Approach | 10 OWASP checks | Context cost |
|----------|-----------------|-------------|
| Sequential in main context | ~10 min, eats entire context window | ~20K+ tokens |
| **Parallel subagents** | **~1-2 min, main context stays clean** | **~500 tokens (summary only)** |

Each subagent gets:
- The scoped file list
- The relevant framework reference (OWASP category / STRIDE category)
- Scanner output for its domain (if available)
- Instructions for its specific concern

Each subagent returns:
- Structured findings JSON
- Nothing else — no preamble, no explanation, just data

The consolidator is the only thing that touches the main context.

### Smart Dispatch

The orchestrator doesn't blindly launch 10 agents. It checks relevance first:

```
Pre-flight (fast, in main context):
  1. Read file list in scope
  2. Detect: has DB queries? has auth? has file uploads? has APIs?
  3. Only spawn agents for relevant categories

Example: scope is a single React component
  --> Skip: injection, ssrf, crypto, logging, outdated-deps, integrity
  --> Run: access-control, misconfig, insecure-design
  --> 3 agents instead of 10 = faster + less noise
```

---

## The Full Toolbox (61 Tools)

### Orchestration

| Command | Purpose |
|---------|---------|
| `/appsec:start` | Assess codebase and recommend which tools to use |
| `/appsec:run` | Smart orchestrator — detects stack, runs relevant tools |
| `/appsec:full-audit` | Exhaustive audit — every framework, every tool, dated report |
| `/appsec:status` | Dashboard — posture, findings, scanner availability |
| `/appsec:config` | Preferences, thresholds, scanner paths |

### Framework Tools

| Command | Purpose |
|---------|---------|
| `/appsec:owasp` | OWASP Top 10 2021 — all 10 categories |
| `/appsec:stride` | STRIDE — all 6 threat categories |
| `/appsec:sans25` | SANS/CWE Top 25 most dangerous software weaknesses |
| `/appsec:pasta` | PASTA 7-stage risk-centric analysis (business context + technical) |
| `/appsec:linddun` | LINDDUN privacy threat modeling — 7 privacy threat categories |
| `/appsec:mitre` | MITRE ATT&CK mapping — map findings to real-world attacker TTPs |

### OWASP Individual Tools

| Command | Category | Focus |
|---------|----------|-------|
| `/appsec:access-control` | A01 | Broken Access Control |
| `/appsec:crypto` | A02 | Cryptographic Failures |
| `/appsec:injection` | A03 | Injection (SQL, NoSQL, OS, LDAP) |
| `/appsec:insecure-design` | A04 | Insecure Design |
| `/appsec:misconfig` | A05 | Security Misconfiguration |
| `/appsec:outdated-deps` | A06 | Vulnerable & Outdated Components |
| `/appsec:auth` | A07 | Identification & Authentication Failures |
| `/appsec:integrity` | A08 | Software & Data Integrity Failures |
| `/appsec:logging` | A09 | Security Logging & Monitoring Failures |
| `/appsec:ssrf` | A10 | Server-Side Request Forgery |

### STRIDE Individual Tools

| Command | Category | Focus |
|---------|----------|-------|
| `/appsec:spoofing` | S | Can attackers impersonate? |
| `/appsec:tampering` | T | Can data be modified? |
| `/appsec:repudiation` | R | Can actions be denied? |
| `/appsec:info-disclosure` | I | Can data leak? |
| `/appsec:dos` | D | Can service be disrupted? |
| `/appsec:privilege-escalation` | E | Can permissions be gained? |

### PASTA Individual Tools (7 Stages)

| Command | Stage | Focus |
|---------|-------|-------|
| `/appsec:pasta-objectives` | Stage 1 | Define business objectives — what are we protecting and why? |
| `/appsec:pasta-scope` | Stage 2 | Define technical scope — DFDs, attack surface, entry points |
| `/appsec:pasta-decompose` | Stage 3 | Decompose application — components, roles, permissions, trust |
| `/appsec:pasta-threats` | Stage 4 | Threat analysis — cross-reference with MITRE ATT&CK, real-world intel |
| `/appsec:pasta-vulns` | Stage 5 | Vulnerability analysis — CWE mapping, SAST/DAST integration |
| `/appsec:pasta-attack-sim` | Stage 6 | Attack simulation — simulate exploit chains, score exploitability |
| `/appsec:pasta-risk` | Stage 7 | Risk & impact — business-weighted risk scores, prioritized mitigations |

PASTA is the most thorough framework. It ties business context to technical threats.
Unlike STRIDE (which classifies), PASTA prioritizes based on real-world risk and business impact.
Best used with `--depth deep` or `--depth expert` on critical systems.

### LINDDUN Individual Tools (Privacy Threats)

| Command | Category | Focus |
|---------|----------|-------|
| `/appsec:linking` | L | Can separate data points be linked to the same person? |
| `/appsec:identifying` | I | Can a person be identified from supposedly anonymous data? |
| `/appsec:non-repudiation-privacy` | N | Does forced accountability create privacy issues? |
| `/appsec:detecting` | D | Can usage patterns or behavior be observed? |
| `/appsec:data-disclosure` | D | Can personal data be accessed by unauthorized parties? |
| `/appsec:unawareness` | U | Are users unaware of how their data is collected/used? |
| `/appsec:non-compliance` | N | Does the code violate GDPR/CCPA/HIPAA requirements? |

LINDDUN fills the gap that security frameworks miss entirely: **privacy**.
STRIDE asks "can data leak?" LINDDUN asks "should we have this data at all?"
Critical for any app handling PII, especially under GDPR/CCPA/HIPAA.

### MITRE ATT&CK Mapping Tool

`/appsec:mitre` maps findings to real-world attacker behavior:

- Takes findings from any other tool and maps them to ATT&CK tactics and techniques
- Shows what an attacker could actually do post-exploitation
- Maps vulnerability chains to kill chain stages (reconnaissance → execution → exfiltration)
- Links to ATT&CK Navigator for visualization
- Cross-references with known threat actor TTPs

Example output:
```
Finding: SQL Injection in src/api/users.ts:45
  ATT&CK Mapping:
    Tactic: Initial Access (TA0001)
    Technique: T1190 Exploit Public-Facing Application
    Post-exploitation chain:
      --> T1059 Command and Scripting Interpreter (if OS command injection possible)
      --> T1005 Data from Local System (DB dump)
      --> T1041 Exfiltration Over C2 Channel
    Known actors using this technique: APT28, FIN7, Lazarus Group
```

### Specialized Tools

| Command | Purpose |
|---------|---------|
| `/appsec:secrets` | Credential & secret detection (code + git history) |
| `/appsec:attack-surface` | Map all entry points, APIs, inputs |
| `/appsec:data-flows` | Map how data moves through the system |
| `/appsec:review-plan` | Analyze implementation plan before coding |
| `/appsec:fix` | Generate fix for a specific finding |
| `/appsec:harden` | Proactive hardening suggestions |
| `/appsec:verify` | Confirm a fix resolved the finding |
| `/appsec:report` | Generate human-readable report |
| `/appsec:race-conditions` | TOCTOU bugs, double-spend, concurrent request exploitation |
| `/appsec:file-upload` | File upload attack surface (type bypass, polyglots, path traversal, zip bombs) |
| `/appsec:graphql` | GraphQL-specific vulnerabilities (depth, batching, per-field auth, alias DoS) |
| `/appsec:websocket` | WebSocket security (auth on upgrade, CSWSH, message injection) |
| `/appsec:serverless` | Serverless function security (IAM, event injection, /tmp reuse, timeout abuse) |
| `/appsec:regression` | Verify previously fixed vulnerabilities haven't been reintroduced |
| `/appsec:api` | OWASP API Security Top 10 (BOLA, BFLA, mass assignment, data exposure) |
| `/appsec:business-logic` | Business logic flaws (workflow bypass, price manipulation, feature abuse) |
| `/appsec:fuzz` | Generate intelligent fuzz test inputs based on code analysis |

### Education & Explain Tools

| Command | Purpose |
|---------|---------|
| `/appsec:explain` | Interactive explainer for any framework, category, or finding |
| `/appsec:learn` | Guided walkthrough of a framework with your codebase as examples |
| `/appsec:glossary` | Quick reference for security terms, acronyms, categories |

---

## Scoping System

Every tool accepts `--scope`. The scope determines what files are analyzed AND how deep the analysis goes.

### Scope Types

```
--scope changed          git diff HEAD (default)
--scope staged           git diff --cached
--scope branch           git diff main...HEAD (all changes on branch)
--scope file:<path>      single file
--scope path:<dir>       directory tree
--scope module:<name>    auto-detect module boundaries
--scope full             entire codebase
--scope plan             the plan just approved (for review-plan)
```

### Adaptive Depth

The narrower the scope, the deeper the analysis automatically:

| Scope | Files | Agent behavior |
|-------|-------|---------------|
| `file:src/auth.ts` | 1 | Read every line. Trace every function call. Check every branch. |
| `path:src/api/` | ~10-30 | Read all files. Trace cross-file flows. Check patterns. |
| `changed` | ~5-15 | Read changed files + direct imports. Focus on the diff. |
| `branch` | ~10-50 | Read all changed files. Look for systemic patterns. |
| `full` | all | Sample-based. Entry points, critical paths, config. |

---

## Depth Modes

```
--depth quick       Surface scan regardless of scope
--depth standard    Normal analysis (default)
--depth deep        Thorough analysis, trace all paths
--depth expert      Maximum depth + red team simulation
```

### Scope + Depth Matrix

```
                quick       standard      deep         expert
file:x.ts      scanners    full read     full read    full read
                            + analysis    + trace      + trace
                                          imports      + red team

path:src/api/  scanners    read all      read all     read all
                            + patterns    + cross-file + cross-file
                                          flows        + red team
                                                       + attack chains

changed        scanners    read diffs    read diffs   read diffs
                            + context     + imports    + imports
                                          + trace      + red team

full           scanners    entry points  entry points everything
               only        + critical     + all flows  reachable
                           paths          + all config + red team
                                                       + full attack
                                                         simulation
```

---

## Red Team Agents (Expert Mode)

When `--depth expert` is used, after the regular analysis completes, red team agents spawn. Analysis agents think defensively ("is this input validated?"). Red team agents think offensively ("how would I exploit this?").

Red team agents simulate distinct threat actor personas, each with different skill levels, motivations, and attack patterns. This produces findings rated by real-world exploitability, not pattern matching.

### Threat Actor Personas

Each red team agent adopts a specific persona that determines what they look for and how they reason:

| Agent | Persona | Skill | Motivation | What they target |
|-------|---------|-------|------------|-----------------|
| Script Kiddie | Low-skill opportunist | Low | Fame, curiosity | Known CVEs, default creds, unpatched software, exposed admin panels |
| Hacktivist | Ideological attacker | Medium | Protest, disruption | Public-facing apps, data leaks, defacement vectors, info disclosure |
| Insider Threat | Disgruntled employee | Variable | Revenge, profit | Access controls, monitoring gaps, data exfiltration with domain knowledge |
| Organized Crime | Professional operation | High | Financial gain | Payment systems, PII for sale, ransomware vectors, credential harvesting |
| Supply Chain Attacker | Targeted compromise | High | Broad access | Dependencies, build pipelines, update mechanisms, code signing |
| Nation State (APT) | Advanced persistent threat | Very high | Espionage, sabotage | Zero-day potential, persistence mechanisms, encrypted channels, lateral movement |

### Red Team Agent Details

**Script Kiddie Agent** — What can a low-skill attacker find with automated tools?

```
Input: Attack surface, exposed endpoints, dependency list
Task: "You have access to Shodan, exploit-db, and common scanning tools.
       What can you find and exploit without writing custom code?"

Looks for:
  - Known CVEs in dependencies (cross-ref with NVD)
  - Default credentials left in place
  - Exposed debug endpoints (/debug, /admin, /status)
  - Common misconfigurations (directory listing, CORS *, verbose errors)
  - Automated brute-force targets (login without rate limiting)
```

**Hacktivist Agent** — What can an ideologically motivated attacker leak or deface?

```
Input: Public-facing endpoints, data stores, info disclosure findings
Task: "You want maximum public embarrassment. What data can you
       leak, what can you deface, what can you disrupt?"

Looks for:
  - Mass data extraction paths (IDOR + no rate limit = dump all users)
  - Public info disclosure (stack traces, config leaks, .git exposure)
  - DDoS amplification vectors
  - Defacement opportunities (stored XSS, template injection)
```

**Insider Threat Agent** — What can an authenticated employee abuse?

```
Input: All routes/endpoints, auth checks, role definitions, data access patterns
Task: "You are a malicious authenticated user with the lowest
       privilege level. You know the system. Find ways to access
       data or functions you shouldn't."

Looks for:
  - Horizontal privilege escalation (access other users' data)
  - Vertical privilege escalation (gain admin from regular user)
  - Data exfiltration with legitimate access (over-fetching, bulk export)
  - Audit log gaps (actions you can take without being logged)
  - Backdoor creation (persistent access after role revocation)
```

**Organized Crime Agent** — What's the most profitable attack path?

```
Input: Payment flows, PII storage, session management, auth system
Task: "You want money. Find paths to financial data, credentials
       for sale, or ransomware deployment opportunities."

Looks for:
  - Payment data interception (card numbers, tokens in logs)
  - Credential harvesting at scale (weak hashing, credential stuffing surface)
  - PII for dark web sale (SSN, medical, financial records)
  - Ransomware deployment vectors (write access to critical data + weak backups)
  - Session hijacking for account takeover
```

**Supply Chain Agent** — What if a dependency is compromised?

```
Input: package.json/requirements.txt, build scripts, CI config, update mechanisms
Task: "You've compromised one of this project's dependencies.
       What damage can you do? What's the blast radius?"

Looks for:
  - Dependencies with excessive permissions (file system, network, env vars)
  - Build scripts that execute arbitrary code from packages
  - Auto-update mechanisms without integrity verification
  - Transitive dependencies (deep chains = larger attack surface)
  - Post-install scripts in package managers
```

**Nation State (APT) Agent** — What does a sophisticated, patient attacker find?

```
Input: Full architecture, all findings from other agents, data flows
Task: "You have unlimited time and resources. Find paths to
       persistent access, data exfiltration, and lateral movement.
       Chain multiple weaknesses together."

Looks for:
  - Multi-step attack chains (3+ weaknesses combined)
  - Persistence mechanisms (can you maintain access after patches?)
  - Lateral movement paths (from one component to another)
  - Covert data exfiltration (DNS tunneling, timing channels, steganography)
  - Weaknesses in crypto implementation (not just "is it encrypted" but "is the implementation correct")
```

### Risk Scoring: DREAD Model

Each red team finding is scored using the DREAD model, which Claude can automate
by reasoning about each factor from code context:

```
Risk Score = (Damage + Reproducibility + Exploitability + Affected Users + Discoverability) / 5
```

| Factor | Score 0-10 | What Claude evaluates |
|--------|-----------|----------------------|
| **Damage** | What's the worst outcome? | Data loss scope, system compromise depth, business impact |
| **Reproducibility** | How reliable is the exploit? | Works every time (10) vs requires rare race condition (2) |
| **Exploitability** | How hard to execute? | Copy-paste from exploit-db (10) vs custom zero-day (1) |
| **Affected Users** | How many impacted? | All users (10) vs single admin account (2) |
| **Discoverability** | How easy to find? | Visible in URL (10) vs requires source code access (2) |

DREAD Severity Mapping:
```
8.0 - 10.0  CRITICAL
5.0 - 7.9   HIGH
3.0 - 4.9   MEDIUM
0.0 - 2.9   LOW
```

This replaces guessing severity from pattern matches. Claude reasons about each
DREAD factor based on actual code context, producing scores grounded in
exploitability rather than theoretical risk.

### Red Team Execution Flow

```
Phase 1: Analysis agents complete (OWASP/STRIDE/etc)
  |
  v
Phase 2: Red team dispatch (parallel)
  |
  +-- spawn --> Script Kiddie agent (what's easy to find?)
  +-- spawn --> Insider agent (what can auth'd users abuse?)
  +-- spawn --> Organized Crime agent (where's the money?)
  +-- spawn --> Supply Chain agent (what if deps are hostile?)
  +-- (optional, --depth expert --persona nation-state)
  +-- spawn --> Nation State agent (what does a patient APT find?)
  +-- spawn --> Hacktivist agent (what can be leaked/defaced?)
  |
  v
Phase 3: Red team consolidation
  |
  +-- Merge attack paths from all personas
  +-- Score each path with DREAD model
  +-- Deduplicate overlapping paths
  +-- Rank by DREAD score
  +-- Map to MITRE ATT&CK techniques
  |
  v
Phase 4: Final output
  +-- Attack paths with kill chain stages
  +-- DREAD scores per finding
  +-- Prioritized remediation order
  +-- "Fix this first" recommendation
```

### Red Team Persona Selection

Not all personas run every time. The orchestrator picks based on context:

```
--depth expert                    Default set: Script Kiddie, Insider, Organized Crime, Supply Chain
--depth expert --persona all      All 6 personas
--depth expert --persona insider  Just the insider agent
--depth expert --persona apt      Just the nation state agent

Auto-selection by project type:
  Has payment handling?     --> always include Organized Crime
  Has user auth?            --> always include Insider
  Has many dependencies?    --> always include Supply Chain
  Is public-facing?         --> always include Script Kiddie + Hacktivist
  Is critical infrastructure? --> include Nation State
```

---

## Scanner Integration

Auto-detection, not configuration. Never pretend Claude analysis equals a real scanner.

### Supported Scanners (when present)

```
Languages:
  semgrep        any language, custom rules
  bandit         Python
  gosec          Go
  cargo-audit    Rust
  brakeman       Ruby/Rails
  phpstan        PHP
  spotbugs       Java

Dependencies:
  npm audit      Node.js
  pip-audit      Python
  trivy          containers, IaC, deps, secrets
  osv-scanner    Google's OSV database

Secrets:
  gitleaks       git history + current files
  trufflehog     high-signal secret detection

IaC:
  checkov        Terraform, CloudFormation, K8s, Docker
  tfsec          Terraform specific
  kics           multi-IaC
```

### Detection Flow

```
1. On first run or /appsec:config:
   - Check PATH for known scanner binaries
   - Check common install locations
   - Check if Docker is available
   - Store results in .appsec/scanners/detected.json

2. On scan:
   - Read detected.json
   - For each available scanner, run with appropriate flags
   - All scanners run in parallel (background tasks)
   - Normalize results to internal finding format (SARIF-compatible)

3. If no scanners detected:
   - Claude does what it can (grep patterns, code analysis)
   - Status clearly shows: "No scanners detected"
   - Suggests: "Install semgrep for better scanning: pip install semgrep"
   - Never pretends Claude analysis = SAST scan
```

---

## Individual Tool Details

### `/appsec:start`

**The entry point. Run this first on any codebase.**

Assesses the project and recommends exactly which `/appsec:*` tools are relevant, in what order, and why.

**What Claude does:**

1. **Detect tech stack**: Read `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, `*.csproj`, `Dockerfile`, `docker-compose.yml`, `serverless.yml`, `terraform/*.tf`, `.github/workflows/`, etc. Build a complete picture of languages, frameworks, and infrastructure.

2. **Detect data sensitivity**: Scan for patterns that indicate what kind of data is handled:
   - PII: user models with email/phone/address/SSN fields, GDPR consent flows
   - Financial: payment integrations (Stripe, PayPal), card number patterns, transaction models
   - Health: HIPAA-related terms, PHI fields, medical record models
   - Auth: JWT/OAuth/session handling, password storage, MFA implementations

3. **Detect architecture patterns**: Identify what kind of application this is:
   - API-only backend? → prioritize `/appsec:api`, `/appsec:auth`, `/appsec:injection`
   - Full-stack with file uploads? → add `/appsec:file-upload`
   - GraphQL? → add `/appsec:graphql`
   - WebSocket real-time? → add `/appsec:websocket`
   - Serverless? → add `/appsec:serverless`
   - Heavy on business logic (e-commerce, fintech)? → add `/appsec:business-logic`, `/appsec:race-conditions`
   - Many dependencies? → prioritize `/appsec:outdated-deps`
   - CI/CD pipelines present? → add `/appsec:integrity`

4. **Detect installed scanners**: Check PATH for semgrep, bandit, gitleaks, trivy, etc.

5. **Check for existing security configs**: `.eslintrc` security rules, CSP headers, CORS config, rate limiting middleware, WAF rules.

6. **Output a tailored recommendation:**

```
═══════════════════════════════════════════════════════════
              APPSEC START — Project Assessment
═══════════════════════════════════════════════════════════

PROJECT: my-saas-app
STACK: TypeScript (Next.js 14), PostgreSQL, Redis, Stripe
DATA: PII (user profiles), Financial (payment processing)
SCANNERS: semgrep ✓  gitleaks ✓  npm-audit ✓  trivy ✗

RECOMMENDED TOOLS (priority order):

  1. /appsec:secrets --scope full
     WHY: Always run first. Catches committed credentials.

  2. /appsec:injection --scope full
     WHY: PostgreSQL queries detected in 8 files. SQL injection is
     the #1 risk for database-backed apps.

  3. /appsec:auth --scope path:src/auth/
     WHY: JWT + session handling detected. Auth flaws = account takeover.

  4. /appsec:api --scope path:src/api/
     WHY: 34 API endpoints detected. BOLA/BFLA are the top API risks.

  5. /appsec:business-logic --scope path:src/payments/
     WHY: Stripe integration detected. Payment logic flaws = financial loss.

  6. /appsec:race-conditions --scope path:src/payments/
     WHY: Transaction processing detected. Double-spend is critical for fintech.

  7. /appsec:outdated-deps
     WHY: 142 npm packages. 3 have known CVEs (run npm audit).

  8. /appsec:linddun --scope full
     WHY: PII detected. Privacy analysis needed for GDPR compliance.

SKIP (not relevant for this project):
  - /appsec:graphql (no GraphQL schema found)
  - /appsec:websocket (no WS handlers found)
  - /appsec:serverless (not a serverless project)

QUICK START:
  /appsec:run                          # Run top priorities automatically
  /appsec:run --depth deep             # Thorough analysis
  /appsec:run --depth expert           # + Red team simulation
  /appsec:full-audit                   # Everything, with dated report

═══════════════════════════════════════════════════════════
```

This tool makes the 61-tool toolbox approachable. Instead of "which of these 61 tools do I need?", the developer runs `/appsec:start` once and gets a curated, prioritized list with rationale.

### `/appsec:scan` (core scanner within /run)

**Step 1 — Real tools first.** Auto-detect and run everything available in parallel.

**Step 2 — Claude fills the gaps.** For areas no scanner covered:
- Business logic analysis (auth flows, permission checks, data handling)
- Configuration review (environment variables, feature flags, defaults)
- Input validation completeness (not just "does validation exist" but "is it sufficient")
- Error handling (does it leak info? fail open or closed?)

**Step 3 — Claude triages everything.** Takes all findings and:
- Deduplicates (scanner A and B found the same XSS)
- Removes false positives using code context (that `eval` is in a test file)
- Assigns severity based on actual exploitability
- Groups related findings into root causes
- Ranks by risk: what to fix first

### `/appsec:secrets`

Dedicated credential scanner — the #1 thing solo devs ship accidentally.

- Runs gitleaks/trufflehog if available
- Claude fallback: high-entropy strings, API key patterns, connection strings, private keys
- Scans git history too — catches "committed then deleted"
- Checks `.env.example` vs `.env` for leaked values
- Checks `.gitignore` for missing exclusions
- Verifies secrets aren't hardcoded in Docker/CI configs
- Output: findings + immediate actionable steps

### `/appsec:outdated-deps`

- Runs npm audit / pip-audit / cargo-audit / trivy as available
- Claude analyzes reachability: are vulnerable deps actually called?
- Checks for abandoned/unmaintained dependencies
- Checks for typosquatting risks on recently added deps
- License analysis (GPL in a commercial project?)
- Transitive dependency depth warnings

### `/appsec:review-plan`

**The flagship feature. No other tool does this.**

Fires automatically after `ExitPlanMode`. Reads the plan and analyzes it for:

- Missing security concerns ("adds file upload without mentioning validation")
- Implicit trust assumptions ("assumes frontend validates input")
- Data flow risks ("PII crosses network boundary without encryption mention")
- Authentication/authorization gaps ("new endpoint without access control")
- Third-party integration risks ("Stripe webhook without signature verification")
- Threat scenarios ("if attacker controls redirect_url, open redirect")

### `/appsec:model`

Full architecture-level threat model:

1. **Discovery** — Entry points, data stores, external integrations, auth mechanisms, data classification
2. **Data flow mapping** — What goes in/out, protocols, encryption, trust boundary crossings, Mermaid diagrams
3. **STRIDE per component** — Specific, not generic. References actual code.
4. **Attack trees** — For critical threats, full attack path diagrams

Persistent and incremental. `--diff` shows changes since last run.

### `/appsec:attack-surface`

Maps every way into the application:

- All HTTP/API endpoints with methods, auth, input parameters
- WebSocket connections, file upload endpoints
- Admin/debug endpoints (dangerous if exposed)
- GraphQL introspection
- Environment variable injection points
- CLI argument parsing

Ranked by exposure level. Highlights unauthenticated endpoints, missing rate limits, unbounded input, exposed admin/debug routes.

### Education & Explain Tools

#### `/appsec:explain [framework|category|finding-id]`

Interactive explainer. Works at any level of specificity:

```bash
# Explain a whole framework
/appsec:explain stride
  --> What is STRIDE? When to use it. All 6 categories explained.
      Real examples from YOUR codebase for each category.
      "Want me to run a STRIDE analysis on your code? [y/n]"

# Explain a specific category
/appsec:explain spoofing
  --> What is Spoofing? What it targets. Common attack patterns.
      Shows relevant code in YOUR project that relates to spoofing.
      "Want me to check your auth system for spoofing risks? [y/n]"

# Explain a specific finding
/appsec:explain INJ-003
  --> What this finding means. Why it's dangerous. How it's exploited.
      The OWASP/STRIDE/ATT&CK context. Real-world incidents.
      Step-by-step fix explanation. "Want me to generate the fix? [y/n]"

# Compare frameworks
/appsec:explain stride vs pasta
  --> Side-by-side comparison. When to use each.
      "Your project would benefit most from X because..."
```

#### `/appsec:learn [framework]`

Guided walkthrough using your actual codebase as the teaching material:

```bash
/appsec:learn owasp
  --> Walks through all 10 OWASP categories one by one.
      For each: explains the category, shows examples from YOUR code,
      asks "Do you see why this is a risk?", explains the fix.
      Interactive quiz-style: "Which OWASP category does this belong to?"

/appsec:learn stride
  --> Interactive STRIDE tutorial.
      Picks a component from your code, asks you to identify threats.
      Reveals what the tool found. Teaches threat modeling by doing.

/appsec:learn red-team
  --> Explains each attacker persona.
      "If you were a script kiddie, what would you target first?"
      Shows what the red team agent found vs what you guessed.
```

#### `/appsec:glossary [term]`

Quick reference:

```bash
/appsec:glossary idor
  --> "IDOR (Insecure Direct Object Reference): When an app uses
       user-supplied input to access objects directly without
       authorization checks. Example: changing /api/users/123
       to /api/users/456 to access another user's data.
       OWASP: A01. STRIDE: Elevation of Privilege. CWE-639."

/appsec:glossary                    # no argument = full glossary
/appsec:glossary csrf vs xss        # compare terms
```

#### Follow-Up Prompts

Every tool output ends with a contextual follow-up offer:

```
After /appsec:owasp:
  "Want me to explain any of these OWASP categories in detail?
   Or run /appsec:fix on the critical findings?"

After /appsec:run --depth expert:
  "Want me to explain the attack paths the red team found?
   Or walk you through the DREAD scoring for the top finding?"

After /appsec:stride:
  "New to STRIDE? Run /appsec:learn stride for an interactive
   walkthrough using your codebase as examples."

After any finding:
  "Run /appsec:explain <finding-id> to understand why this
   matters and how attackers exploit it in the real world."
```

This turns every analysis into a learning opportunity without being patronizing —
the developer chooses whether to dig deeper.

### `/appsec:fix <finding-id|file:line>`

Takes a finding and generates the actual fix — not generic advice, real code:

```python
# Before (finding: SQL injection)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# After
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

For architectural fixes, provides a step-by-step implementation plan. Offers to apply the fix via Edit tool.

### `/appsec:harden <file|module|component>`

Proactive mode — not "what's broken" but "what could be better":

- Security headers, CSP policies, CORS configuration
- Rate limiting recommendations
- Input validation rules for specific fields
- Logging/monitoring points
- Defensive coding patterns

### `/appsec:verify <finding-id>`

Closes the loop. After a fix:

- Re-runs the specific check that found the issue
- If scanner found it: re-runs that scanner on the file
- If Claude found it: re-analyzes the specific code
- Confirms "FIXED" or "Still vulnerable because..."
- Updates findings state

### `/appsec:report [--format md|html|json|sarif]`

Real report:

- **Executive summary** — One paragraph, overall risk, top 3 priorities
- **Findings table** — Sorted by severity, grouped by category
- **Architecture diagram** — Mermaid with threat annotations
- **Scanner coverage** — What ran, what wasn't covered
- **Remediation progress** — Fixed, outstanding, accepted risk
- **Attack paths** — From red team analysis (if expert mode was used)

Formats: md (repo/wiki), html (sharing), json (automation), sarif (GitHub Security tab)

### `/appsec:full-audit`

**The exhaustive audit. Every framework. Every tool. Every agent. One dated report.**

Unlike `/appsec:run` (which selects relevant tools) or `/appsec:report` (which summarizes existing findings), `/appsec:full-audit` launches **everything** and writes the raw, unfiltered results into a timestamped report file.

**Key design principle: NO consolidation of individual agent outputs.** Each agent's section appears verbatim in the report. The reader gets the full picture, not a summary's interpretation.

**Execution flow:**

```
Phase 1: Project Assessment (sequential, in main context)
  |
  +-- Detect stack, scanners, data sensitivity (same as /appsec:start)
  +-- Generate project metadata for report header
  |
Phase 2: Scanner Execution (parallel background tasks)
  |
  +-- Run all detected scanners in parallel
  +-- Collect raw output
  |
Phase 3: Framework Agents (parallel subagents, batched)
  |
  +-- Batch 1: OWASP (up to 10 agents in parallel)
  +-- Batch 2: STRIDE (up to 6 agents in parallel)
  +-- Batch 3: PASTA (7 stages, sequential — each feeds the next)
  +-- Batch 4: LINDDUN (up to 7 agents in parallel)
  +-- Batch 5: Specialized tools (race-conditions, file-upload, graphql,
  |             websocket, serverless, api, business-logic — parallel)
  +-- Batch 6: MITRE ATT&CK mapping (takes all prior findings)
  +-- Batch 7: Secrets + outdated-deps + attack-surface (parallel)
  |
Phase 4: Red Team Agents (parallel, all 6 personas)
  |
  +-- Script Kiddie, Hacktivist, Insider, Organized Crime,
  |   Supply Chain, Nation State — all run in parallel
  |
Phase 5: Report Assembly (sequential, in main context)
  |
  +-- Write introduction section (project details, tools used)
  +-- Append each agent's raw output as its own section
  +-- Append executive summary at the end
  +-- Save to file
```

**Report file:** `<YYYYMMDD>_appsec_report.md`

**Report structure:**

```markdown
# Application Security Full Audit Report
## <Project Name> — <YYYY-MM-DD>

---

## 1. Introduction

### Project Details
- **Repository**: <repo name and path>
- **Tech Stack**: <languages, frameworks, databases, infra>
- **Data Classification**: <PII, financial, health, etc.>
- **Codebase Size**: <files, lines, modules>
- **Git Branch**: <current branch, commit hash>

### Tools & Scanners Used
- **Scanners**: semgrep v1.x, gitleaks v8.x, npm audit, ...
- **Frameworks Applied**: OWASP Top 10, STRIDE, PASTA, LINDDUN, MITRE ATT&CK
- **Specialized Tools**: secrets, api, business-logic, race-conditions, ...
- **Red Team Personas**: Script Kiddie, Hacktivist, Insider, Organized Crime,
  Supply Chain, Nation State
- **Analysis Depth**: expert (maximum)
- **Scope**: full codebase

### Methodology
Brief description of the analysis approach and what each section covers.

---

## 2. Scanner Results

### 2.1 semgrep
<raw semgrep output, formatted>

### 2.2 gitleaks
<raw gitleaks output, formatted>

### 2.3 npm audit
<raw npm audit output, formatted>

(one subsection per scanner that ran)

---

## 3. OWASP Top 10 Analysis

### 3.1 A01 — Broken Access Control
<full output from access-control agent>

### 3.2 A02 — Cryptographic Failures
<full output from crypto agent>

### 3.3 A03 — Injection
<full output from injection agent>

... (all 10 categories, including those with no findings)

---

## 4. STRIDE Threat Analysis

### 4.1 Spoofing
<full output from spoofing agent>

### 4.2 Tampering
<full output from tampering agent>

... (all 6 categories)

---

## 5. PASTA Risk-Centric Analysis

### 5.1 Stage 1 — Business Objectives
<full output from pasta-objectives agent>

### 5.2 Stage 2 — Technical Scope
<full output from pasta-scope agent>

... (all 7 stages)

---

## 6. LINDDUN Privacy Analysis

### 6.1 Linking
<full output from linking agent>

... (all 7 categories)

---

## 7. Specialized Analysis

### 7.1 Secrets Detection
<full output from secrets agent>

### 7.2 API Security (OWASP API Top 10)
<full output from api agent>

### 7.3 Business Logic
<full output from business-logic agent>

### 7.4 Race Conditions
<full output from race-conditions agent>

... (one subsection per specialized tool that ran)

---

## 8. Attack Surface Map
<full output from attack-surface agent>

---

## 9. MITRE ATT&CK Mapping
<full output from mitre agent — maps all findings to TTPs>

---

## 10. Red Team Analysis

### 10.1 Script Kiddie Perspective
<full output from script-kiddie agent — verbatim>

### 10.2 Hacktivist Perspective
<full output from hacktivist agent — verbatim>

### 10.3 Insider Threat Perspective
<full output from insider agent — verbatim>

### 10.4 Organized Crime Perspective
<full output from organized-crime agent — verbatim>

### 10.5 Supply Chain Attack Perspective
<full output from supply-chain agent — verbatim>

### 10.6 Nation State (APT) Perspective
<full output from nation-state agent — verbatim>

---

## 11. Executive Summary

### Overall Risk Assessment
- **Critical findings**: N
- **High findings**: N
- **Medium findings**: N
- **Low findings**: N
- **Total unique findings**: N (after cross-reference dedup)

### Top 5 Priorities
1. [CRITICAL] ...
2. [CRITICAL] ...
3. [HIGH] ...
4. [HIGH] ...
5. [HIGH] ...

### Key Themes
- Theme 1: e.g., "Access control is inconsistently applied across API endpoints"
- Theme 2: e.g., "Secrets management relies on environment variables without rotation"
- Theme 3: ...

### Attack Path Highlights
The most dangerous multi-step attack paths identified by red team agents.

### Recommendations
Prioritized list of remediation actions, grouped by effort level
(quick wins, medium effort, architectural changes).
```

**Why no consolidation in the body:** Consolidation loses nuance. The insider agent's perspective on an auth flaw is different from the organized crime agent's perspective on the same flaw. A summary would merge them. The raw sections preserve the full reasoning chain, making the report suitable for:
- Security audits that need evidence
- Compliance reviews that need thoroughness
- Development teams that need specific, actionable details per domain
- Management that can skip to the executive summary

**The summary at the end (not the beginning)** is intentional: the reader encounters the evidence first, then the conclusions. This is how professional security audit reports work.

**Flags:**
```
/appsec:full-audit                                # Full audit, default filename
/appsec:full-audit --output custom-name.md        # Custom filename
/appsec:full-audit --skip-frameworks pasta,linddun # Skip specific frameworks
/appsec:full-audit --skip-redteam                  # Skip red team (faster)
/appsec:full-audit --format md|html|json           # Output format
```

### `/appsec:race-conditions [--scope]`

Detects non-atomic patterns where concurrent requests can cause exploitable behavior.

**What Claude reads and checks:**

- Database read-then-write without transactions:
  ```
  balance = db.query("SELECT balance FROM accounts WHERE id = ?", userId)
  // <-- race window: another request can read the same balance here
  db.query("UPDATE accounts SET balance = ? WHERE id = ?", balance - amount, userId)
  ```
  Fix: wrap in `BEGIN`/`COMMIT` transaction with `SELECT ... FOR UPDATE`

- Check-then-act without locks:
  ```
  if (inventory.count > 0) {
    // <-- race window: count could hit 0 between check and decrement
    inventory.count -= 1
  }
  ```
  Fix: atomic decrement (`UPDATE inventory SET count = count - 1 WHERE count > 0`)

- File check-then-use (TOCTOU):
  ```
  if (fs.existsSync(path)) {
    fs.readFileSync(path)  // <-- file could be swapped between check and read
  }
  ```

- Shared state across async boundaries:
  ```
  // Node.js: req.session mutations across await points
  req.session.cart = await getCart()
  await processPayment()  // <-- another request could modify cart here
  req.session.cart.status = 'paid'
  ```

- Counter/balance operations without atomicity (Redis INCR vs GET+SET, etc.)
- Coupon/discount redemption without idempotency keys
- Account creation without unique constraint races

**Output:** Each finding includes the race window location, what two concurrent requests could do, and the atomic fix pattern.

### `/appsec:file-upload [--scope]`

Analyzes file upload handlers for the full range of upload attacks.

**What Claude reads and checks:**

- **Validation location**: Is validation client-side only (`accept=` attribute) or server-side?
- **Extension checking**: Whitelist or blacklist? Does it handle double extensions (`.php.jpg`)? Null bytes (`shell.php%00.jpg`)?
- **Content-type validation**: Does it trust the `Content-Type` header from the client, or verify via magic bytes?
- **Magic byte verification**: Does it read actual file headers, or just the extension?
- **Filename sanitization**: Is the filename used directly? Can `../../etc/cron.d/backdoor` escape the upload directory?
- **Storage location**: Inside or outside the web root? Can uploaded files be directly accessed via URL?
- **Size limits**: Enforced server-side before reading the full body into memory?
- **Dangerous types blocked**: .php, .jsp, .aspx, .exe, .sh, .svg (can contain scripts), .xml (XXE)
- **Archive handling**: If zip/tar uploads accepted — is there decompression bomb protection? Path traversal in archive entries (zip slip)?
- **Image processing**: If images are re-encoded — is ImageMagick/GD configured securely? (ImageTragick CVE-2016-3714)
- **Post-upload execution**: Can uploaded files be executed by the web server?

**Output:** Checklist-style findings with severity. Critical if uploaded files can be executed. High if path traversal possible. Medium for missing validation layers.

### `/appsec:graphql [--scope]`

GraphQL-specific security analysis. Reads schema definitions, resolver implementations, and middleware configuration.

**What Claude reads and checks:**

- **Introspection**: Is `__schema` / `__type` queryable? Should be disabled in production.
- **Query depth limits**: Is middleware like `graphql-depth-limit` configured? What's the max depth? (Unbounded = DoS via deeply nested queries)
- **Query complexity/cost analysis**: Is there a cost limit? Can an attacker craft a query that's cheap to write but expensive to resolve?
- **Batching limits**: Can a client send an array of 10,000 queries in one request?
- **Alias abuse**: Can a client use aliases to request the same expensive field 1,000 times in one query?
  ```graphql
  { a1: expensiveQuery, a2: expensiveQuery, ..., a1000: expensiveQuery }
  ```
- **Per-field authorization**: Does each resolver check permissions, or is auth only at the query root? Can a regular user query `user { adminSettings { secretKey } }`?
- **Variable injection**: Are variables sanitized before being used in database queries or system calls within resolvers?
- **Error verbosity**: Do errors leak stack traces, internal paths, or database structure?
- **Field suggestions**: When introspection is disabled, do error messages still suggest valid field names? ("Did you mean 'password'?")
- **Subscription security**: Are WebSocket-based subscriptions authenticated? Can a client subscribe to events they shouldn't see?

**Output:** Findings mapped to both OWASP API Top 10 and standard OWASP Top 10.

### `/appsec:websocket [--scope]`

Analyzes WebSocket connection handlers, message processing, and connection lifecycle.

**What Claude reads and checks:**

- **Authentication on upgrade**: Does the HTTP upgrade handler verify the user's session/token before establishing the WS connection? Or can anyone connect?
- **Origin header validation**: Does the server check the `Origin` header to prevent Cross-Site WebSocket Hijacking (CSWSH)? A malicious page could open a WS connection to your server using the victim's cookies.
- **Message input validation**: Are incoming WS messages validated and sanitized the same way HTTP inputs are? (Injection via WS messages bypasses WAF rules that only inspect HTTP)
- **Message rate limiting**: Is there protection against message flooding? (Client sends 10,000 messages/second)
- **Connection rate limiting**: Can an attacker open thousands of connections to exhaust server resources?
- **Encryption**: Is `wss://` enforced, or is `ws://` (unencrypted) accepted?
- **Authorization per message**: After connection, does each message type check if the user is allowed to perform that action? Or does initial auth grant unlimited access?
- **Connection cleanup**: Are connections properly closed on logout/session expiry? Are resources freed?
- **Broadcast isolation**: In multi-user scenarios, can messages leak between users/rooms/channels?

**Output:** Findings with CSWSH as typically critical (full session hijacking), missing auth as high, missing validation as medium.

### `/appsec:serverless [--scope]`

Analyzes serverless function configurations, IAM policies, and event handling.

**What Claude reads and checks:**

- **IAM permissions**: Does each function have its own minimal IAM role, or do all functions share one overprivileged role? Look for `"Action": "*"` or `"Resource": "*"` in policies.
- **Event input validation**: Is the trigger payload (S3 event, API Gateway, SQS message, Pub/Sub) validated before use? Event injection: a malicious S3 filename could contain shell commands if passed to `exec()`.
- **Secrets management**: Are secrets in environment variables (visible in console, logs, crash dumps) or a secrets manager (AWS Secrets Manager, SSM Parameter Store)?
- **`/tmp` reuse**: Does the function write sensitive data to `/tmp`? In warm invocations, `/tmp` persists between calls — another invocation could read leftover data.
- **Timeout configuration**: Excessively long timeouts (15 min on Lambda) could be exploited for reverse shells or crypto mining. Is the timeout set to the minimum needed?
- **Concurrency limits**: Is there a max concurrency set? Without it, an attacker can trigger thousands of invocations simultaneously (billing DoS).
- **VPC configuration**: Does the function need network access? Is it in a VPC with proper security groups, or does it have open internet access?
- **Layer/dependency security**: Are Lambda layers or shared dependencies from trusted sources? Are they pinned to specific versions?
- **Logging**: Are function logs capturing security-relevant events? Are they NOT logging sensitive data (PII, tokens, passwords)?
- **Dead letter queues**: Do failed invocations go to a DLQ? Could failed events containing sensitive data pile up in an unmonitored queue?

**Output:** Findings grouped by function, with IAM over-privilege as typically the highest severity.

### `/appsec:regression`

State-tracking tool that ensures previously fixed vulnerabilities stay fixed.

**How it works:**

1. **Track fixes**: When `/appsec:verify` confirms a finding is fixed, it records:
   - The finding ID, original location, what was wrong, what the fix was
   - A "signature" of the fix (the pattern that should remain present)

2. **Check for regressions**: On each run, for every previously fixed finding:
   - Is the vulnerable pattern back? (code reverted, similar code added elsewhere)
   - Is the fix still in place? (the parameterized query still parameterized?)
   - Has the file been deleted and recreated without the fix?

3. **Output:**
   ```
   REGRESSION CHECK: 24 previously fixed findings

   REGRESSIONS FOUND: 2
     [CRIT] INJ-003: SQL injection in user lookup — REINTRODUCED
       Fixed on 2024-01-15 in src/db/queries.ts:45
       Vulnerable pattern found again at src/db/queries.ts:52
       (new query added without parameterization)

     [HIGH] AC-007: Missing auth on export endpoint — REINTRODUCED
       Fixed on 2024-02-01 in src/routes/api.ts:120
       New endpoint src/routes/api-v2.ts:85 has same pattern without auth

   VERIFIED STILL FIXED: 22
   ```

4. **State stored in:** `.appsec/findings/fixed-history.json`

Designed for CI/CD integration: run `/appsec:regression` on every PR to catch reintroduced vulns.

### `/appsec:api [--scope]`

Dedicated API security analysis against the OWASP API Security Top 10 (2023).

**What Claude reads and checks:**

- **API1 — Broken Object Level Authorization (BOLA):**
  Does each endpoint that takes an object ID check that the requesting user owns/can access that object? Not just "is authenticated" but "is authorized for THIS resource."
  ```
  // Vulnerable: checks auth but not ownership
  app.get('/api/orders/:id', authMiddleware, (req, res) => {
    const order = db.getOrder(req.params.id)  // any user can read any order
  })
  ```

- **API2 — Broken Authentication:**
  Weak auth mechanisms, missing rate limits on login, token issues.

- **API3 — Broken Object Property Level Authorization:**
  Can users read/write object properties they shouldn't? Mass assignment:
  ```
  // Vulnerable: spreads all body fields into update
  db.updateUser(userId, { ...req.body })  // attacker sends { role: "admin" }
  ```

- **API4 — Unrestricted Resource Consumption:**
  Missing rate limits, pagination limits, file size limits, query cost limits.

- **API5 — Broken Function Level Authorization:**
  Are admin endpoints protected at the route/middleware level? Or just hidden in the UI?

- **API6 — Unrestricted Access to Sensitive Business Flows:**
  Can automated tools abuse business flows? (Ticket scalping, bulk purchasing, spam)

- **API7 — Server-Side Request Forgery (SSRF):**
  Does any endpoint fetch URLs from user input?

- **API8 — Security Misconfiguration:**
  CORS, security headers, verbose errors, unnecessary HTTP methods enabled.

- **API9 — Improper Inventory Management:**
  Are there old API versions still running? Undocumented endpoints? Debug endpoints?

- **API10 — Unsafe Consumption of APIs:**
  When your app calls third-party APIs, does it validate responses? Trust but verify.

**Output:** Findings mapped to API Top 10 IDs (API1-API10) with cross-references to OWASP Top 10 and STRIDE.

### `/appsec:business-logic [--scope]`

Analyzes application business logic for flaws that scanners cannot detect. This is where Claude's reasoning ability is the primary value — understanding what code is supposed to do and finding ways to abuse it.

**What Claude reads and checks:**

- **Workflow bypass**: Can steps in a multi-step process be skipped?
  ```
  // Can a user POST to /checkout without going through /cart and /shipping?
  // Is there server-side state enforcing the order?
  ```

- **Price/amount manipulation**: Can negative values, zero values, or extreme values break logic?
  ```
  // What happens if quantity = -1? Does the user get a refund?
  // What happens if price is modified in the request body?
  ```

- **Feature abuse**: Can legitimate features be used maliciously?
  - Referral bonus: can you refer yourself?
  - Free trial: can you re-register with a different email?
  - Coupon codes: can they be applied multiple times? To already-discounted items?
  - Export/download: can it be used for mass data scraping?

- **State manipulation**: Can the user put the application in an inconsistent state?
  - Cancel an order after it shipped but before payment captured
  - Modify a submitted form by replaying the edit endpoint
  - Delete a resource that other resources depend on

- **Privilege through normal workflows**:
  - Can a user invite themselves to a higher role?
  - Can a group admin remove the group owner?
  - Can deleting and recreating an account bypass a ban?

- **Time-based logic**: Are there time-sensitive operations with exploitable windows?
  - Auction sniping with clock skew
  - Expiring tokens that are still accepted
  - Schedule-based access that doesn't check timezone

**Output:** Each finding includes: the business rule being violated, how a user could exploit it, the impact, and a suggested fix. Rated by business impact rather than technical severity.

### `/appsec:fuzz [--scope]`

Generates intelligent test inputs based on code analysis. Not a runtime fuzzer — it produces the test cases.

**What Claude does:**

1. **Reads input parsing code**: What format does the function expect? What are the boundaries?
2. **Generates targeted inputs by category:**

   - **Boundary values**: MAX_INT, MIN_INT, 0, -1, empty string, null, undefined
   - **Type confusion**: String where int expected, array where string expected, object where array expected, nested objects 100 levels deep
   - **Encoding edge cases**: Unicode null (U+0000), RTL override (U+202E), zero-width characters, emoji in strings, multi-byte sequences that break at wrong boundaries
   - **Injection payloads tailored to context**: If input goes to SQL → SQL injection payloads. If to shell → command injection. If to HTML → XSS. If to file path → traversal. Context-aware, not a generic list.
   - **Format-specific**: If JSON → malformed JSON, duplicate keys, extremely long keys. If XML → entity expansion, DTD injection. If CSV → formula injection.
   - **Protocol abuse**: If HTTP headers → header injection, smuggling payloads. If URL → open redirect, SSRF payloads.

3. **Output format:**
   ```json
   {
     "target": "POST /api/users",
     "parameter": "email",
     "test_cases": [
       { "input": "a@b.c", "tests": "minimum valid email", "expected": "accept" },
       { "input": "", "tests": "empty string", "expected": "reject" },
       { "input": "a".repeat(10000) + "@b.c", "tests": "length overflow", "expected": "reject" },
       { "input": "user@[127.0.0.1]", "tests": "IP literal in email domain", "expected": "depends on policy" },
       { "input": "user+tag@domain.com", "tests": "plus addressing", "expected": "accept" },
       { "input": "user@evil.com\\n\\nBCC: attacker@evil.com", "tests": "email header injection", "expected": "reject" }
     ]
   }
   ```

4. **Can chain with external tools**: Output can be fed to actual fuzzers (Burp Intruder, ffuf, custom scripts) for execution.

### `/appsec:status`

```
=====================================================
              SECURITY POSTURE
=====================================================

Scanners: semgrep Y  gitleaks Y  npm-audit Y  trivy N
Last scan: 2 hours ago (changed files only)
Last full model: 3 days ago

FINDINGS: 12 total
  Critical: 1  High: 3  Medium: 5  Low: 3
  Fixed: 4  Outstanding: 8

SINCE LAST SCAN: +2 new files, 14 changed lines
  --> Run /appsec:run to check changes

TOP PRIORITY:
  1. [CRIT] SQL injection in src/db/queries.ts:45
  2. [HIGH] Missing auth on POST /api/export
  3. [HIGH] Hardcoded AWS key in config/deploy.sh

MODEL: 14 components, 22 data flows, 5 trust boundaries
  --> 3 components added since last model update
  --> Run /appsec:model --diff to update

=====================================================
```

No fake compliance percentages. Just facts.

---

## Cross-Cutting Filters

Every tool supports:

```
--scope changed|staged|branch|file:<path>|path:<dir>|full
--severity critical|high|medium|low    Minimum severity to report
--depth quick|standard|deep|expert     Analysis thoroughness
--format text|json|sarif|md            Output format
--fix                                  Chain into /appsec:fix
--quiet                                Findings only, no explanation
--explain                              Add contextual explanations to each finding
--only A01,A03                         Run specific categories (framework tools)
--persona all|insider|apt|...          Select red team personas (expert mode)
```

---

## Hook System

```yaml
# .appsec/config.yaml
hooks:

  # Plan approved --> review the plan (always on)
  on_plan_approved:
    tool: review-plan
    gate: soft

  # Code written --> quick scan of changed file (opt-in)
  on_code_written:
    tool: run
    depth: quick
    scope: changed-file
    gate: none
    debounce: 30s
    enabled: false

  # Any file write --> secret detection (always on, hard gate)
  on_file_written:
    tool: secrets
    scope: changed-file
    gate: hard

  # Pre-commit --> scan staged files (opt-in)
  on_pre_commit:
    tool: run
    depth: standard
    scope: staged
    gate: soft
    enabled: false
```

The secret detection gate is the one hard gate. Committing a secret is both common and catastrophic for solo devs. Everything else is soft or advisory.

---

## State & Persistence

```
.appsec/
+-- config.yaml
+-- findings/
|   +-- by-tool/
|   |   +-- injection.json
|   |   +-- spoofing.json
|   |   +-- secrets.json
|   |   +-- ...                  # One file per tool
|   +-- aggregate.json           # Deduplicated, all tools combined
|   +-- accepted.json            # Developer-accepted risks
|   +-- history/
|       +-- 2024-02-14.json
+-- model/
|   +-- components.json
|   +-- data-flows.json
|   +-- attack-surface.json
|   +-- diagrams/
|       +-- architecture.mmd
+-- reports/
|   +-- latest.md
+-- scanners/
    +-- detected.json
```

`.appsec/findings/` in `.gitignore` by default (contains paths, potential security info). `.appsec/model/` is committed (architecture is shareable). User chooses.

---

## Framework Mappings

```
/appsec:owasp runs:
  A01 --> /appsec:access-control
  A02 --> /appsec:crypto
  A03 --> /appsec:injection
  A04 --> /appsec:insecure-design
  A05 --> /appsec:misconfig
  A06 --> /appsec:outdated-deps
  A07 --> /appsec:auth
  A08 --> /appsec:integrity
  A09 --> /appsec:logging
  A10 --> /appsec:ssrf

/appsec:stride runs:
  S --> /appsec:spoofing
  T --> /appsec:tampering
  R --> /appsec:repudiation
  I --> /appsec:info-disclosure
  D --> /appsec:dos
  E --> /appsec:privilege-escalation

/appsec:pasta runs (7 stages sequentially, each a subagent):
  Stage 1 --> /appsec:pasta-objectives
  Stage 2 --> /appsec:pasta-scope
  Stage 3 --> /appsec:pasta-decompose
  Stage 4 --> /appsec:pasta-threats
  Stage 5 --> /appsec:pasta-vulns
  Stage 6 --> /appsec:pasta-attack-sim
  Stage 7 --> /appsec:pasta-risk

/appsec:linddun runs:
  L --> /appsec:linking
  I --> /appsec:identifying
  N --> /appsec:non-repudiation-privacy
  D --> /appsec:detecting
  D --> /appsec:data-disclosure
  U --> /appsec:unawareness
  N --> /appsec:non-compliance

/appsec:mitre runs:
  --> takes findings from any other tool
  --> maps to ATT&CK tactics, techniques, and procedures
  --> cross-references with known threat actor behavior

/appsec:run runs:
  --> auto-selects from all of the above based on project context
  --> plus always: secrets, outdated-deps, attack-surface
  --> if --depth expert: spawns red team personas
```

---

## Agent Summary

| Agent type | Count | Runs when | Purpose |
|-----------|-------|-----------|---------|
| OWASP analysis agents | Up to 10 | standard+ | One per OWASP Top 10 category |
| STRIDE analysis agents | Up to 6 | standard+ | One per STRIDE category |
| PASTA stage agents | 7 | on /appsec:pasta | Sequential, each stage feeds the next |
| LINDDUN privacy agents | Up to 7 | standard+ | One per LINDDUN category |
| MITRE mapping agent | 1 | standard+ | Maps findings to ATT&CK TTPs |
| Scanner agents | 1 per tool | always | Run external scanners in parallel |
| Consolidator | 1 | always | Merge, dedup, DREAD score, rank |
| Red Team: Script Kiddie | 1 | expert | What's easy to find with automated tools? |
| Red Team: Hacktivist | 1 | expert | What can be leaked or defaced? |
| Red Team: Insider | 1 | expert | Privilege escalation with domain knowledge |
| Red Team: Organized Crime | 1 | expert | Financial data, credentials, ransomware paths |
| Red Team: Supply Chain | 1 | expert | Dependency compromise blast radius |
| Red Team: Nation State | 1 | expert (opt-in) | APT persistence, multi-step chains, lateral movement |
| Plan reviewer | 1 | on plan approval | Analyze intent before code exists |
| Start assessor | 1 | on /appsec:start | Detect stack, data sensitivity, recommend tools |
| Full audit orchestrator | 1 | on /appsec:full-audit | Launch all agents, assemble report |

Max parallel agents at any time: ~10 (one framework batch at a time).
Red team agents run in parallel after analysis completes (~6 agents).
Full audit runs all batches sequentially, agents within each batch in parallel.

---

## Usage Examples

```bash
# First time on a project? Start here.
/appsec:start

# Quick check on what I just changed
/appsec:run

# Check a specific file thoroughly
/appsec:run --scope file:src/auth/login.ts --depth deep

# Full OWASP on my API directory
/appsec:owasp --scope path:src/api/

# Just check for injection in staged files before commit
/appsec:injection --scope staged

# Expert mode with red team on the whole branch before PR
/appsec:run --scope branch --depth expert

# Red team my auth system specifically
/appsec:stride --scope path:src/auth/ --depth expert

# Quick secrets check on everything
/appsec:secrets --scope full

# Check one specific thing after a fix
/appsec:verify INJ-001

# Fix everything critical
/appsec:run --severity critical --fix

# Generate report for the repo
/appsec:report --format md

# Full PASTA analysis (business-context + technical)
/appsec:pasta --scope full --depth deep

# Privacy check before handling PII
/appsec:linddun --scope path:src/user-data/

# Just check GDPR compliance
/appsec:non-compliance --scope full

# Map all findings to MITRE ATT&CK
/appsec:mitre

# Red team with specific persona
/appsec:run --depth expert --persona insider
/appsec:run --depth expert --persona apt

# Red team all personas on auth system
/appsec:run --scope path:src/auth/ --depth expert --persona all

# Supply chain risk check on dependencies
/appsec:run --depth expert --persona supply-chain

# Full exhaustive audit with dated report
/appsec:full-audit

# Full audit, skip the slow parts
/appsec:full-audit --skip-redteam --skip-frameworks pasta
```

---

## What This Does NOT Do

- Generate fake compliance percentages
- Pretend Claude analysis equals a SAST scanner
- Block the developer without an override path (except secrets)
- Replace actual penetration testing
- Claim SOC2/PCI-DSS/HIPAA coverage from an LLM scan
