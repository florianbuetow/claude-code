# Threat Modeling Research: Frameworks, Methodologies, and Tooling

Research compiled for the claude-threatmodel plugin. Organized by category with actionable implementation ideas for Claude Code plugin tools and agents.

---

## 1. Threat Modeling Frameworks Beyond STRIDE and OWASP Top 10

### PASTA (Process for Attack Simulation and Threat Analysis)

**What it is**: A seven-stage, risk-centric threat modeling methodology that aligns business objectives with technical requirements and attack patterns. The stages are: (1) Define objectives, (2) Define technical scope, (3) Application decomposition, (4) Threat analysis, (5) Vulnerability analysis, (6) Attack modeling/simulation, (7) Risk and impact analysis.

**Best used for**: Applications where business risk alignment matters most. PASTA is attacker-centric and produces actionable threat intelligence by simulating real attack scenarios against business-critical assets. Ideal for organizations that need threat models tied to business impact and ROI justification.

**Plugin implementation ideas**:
- `/threatmodel:pasta` -- A guided workflow that walks through all 7 stages
- Stage 1-2 could auto-extract from project README, package.json, and architecture docs
- Stage 3 maps directly to the existing asset discovery in `/threatmodel:full`
- Stages 5-6 align with the red team agents in expert mode
- Stage 7 could produce business-impact-weighted severity scores

### LINDDUN (Linkability, Identifiability, Non-repudiation, Detectability, Disclosure of information, Unawareness, Non-compliance)

**What it is**: A privacy-focused threat modeling framework developed at KU Leuven. Each letter represents a privacy threat category. It systematically identifies privacy threats in system architectures using Data Flow Diagrams, similar to STRIDE but focused entirely on privacy properties rather than security properties.

**Best used for**: Systems handling personal data, GDPR compliance, healthcare applications, any application where privacy-by-design is required. Complements STRIDE since STRIDE focuses on security while LINDDUN focuses on privacy.

**The 7 categories**:
- **L**inkability -- Can an attacker link two or more items of interest (actions, identities, data)?
- **I**dentifiability -- Can an attacker identify a subject from a data set?
- **N**on-repudiation -- Can a user deny an action? (Inverse of STRIDE's Repudiation -- here, non-repudiation is the threat to privacy)
- **D**etectability -- Can an attacker determine whether an item of interest exists?
- **D**isclosure of information -- Can an attacker learn the content of data?
- **U**nawareness -- Is the user unaware of data collection, processing, or sharing?
- **N**on-compliance -- Does the system fail to comply with privacy regulations and policies?

**Plugin implementation ideas**:
- `/threatmodel:privacy` or `/threatmodel:linddun` -- Privacy-specific threat analysis
- Auto-detect PII fields in code (email, phone, address, SSN patterns, date of birth)
- Check for data minimization (are you collecting more than needed?)
- Check for consent mechanisms (cookie banners, opt-in/opt-out)
- Check for data retention policies and deletion capabilities (right to be forgotten)
- Map findings to GDPR articles automatically
- Scan for tracking pixels, analytics SDKs, third-party data sharing

### VAST (Visual, Agile, and Simple Threat modeling)

**What it is**: A scalable threat modeling approach designed for enterprise DevOps and Agile environments. Uses two model types: Application Threat Models (based on process flow diagrams) and Operational Threat Models (based on DFDs from the attacker's perspective). Designed to integrate into CI/CD and be automatable.

**Best used for**: Organizations that need threat modeling at scale, integrated into Agile sprints and CI/CD pipelines. VAST emphasizes automation and repeatability over manual analysis.

**Plugin implementation ideas**:
- Auto-generate application threat models from code structure on every PR
- `/threatmodel:run` already aligns with VAST's philosophy of automated, integrated threat modeling
- Operational threat model generation from infrastructure-as-code (Terraform, CloudFormation, K8s manifests)
- Sprint-scoped threat assessments that only analyze changes in the current sprint/branch

### Attack Trees

**What it is**: A formal, hierarchical methodology for analyzing threats. The root node represents the attacker's goal (e.g., "steal user credentials"). Child nodes represent ways to achieve that goal, broken into sub-goals using AND/OR logic. Leaves represent concrete attack steps. Originally proposed by Bruce Schneier.

**Best used for**: Deep analysis of specific, high-value attack scenarios. Excellent for communicating complex attack paths to stakeholders. Can be annotated with cost, difficulty, likelihood, and detection probability.

**Plugin implementation ideas**:
- Already partially implemented in the red team agent concept (attack path chaining)
- Generate Mermaid diagrams of attack trees from findings
- `/threatmodel:attack-tree <goal>` -- Build an attack tree for a specific goal like "exfiltrate user data" or "gain admin access"
- Annotate tree nodes with difficulty (from code analysis) and detection likelihood (from logging analysis)
- Allow interactive exploration: "expand this node" to get deeper analysis

### DREAD (Damage, Reproducibility, Exploitability, Affected Users, Discoverability)

**What it is**: A risk rating model (formerly used by Microsoft, now largely deprecated in favor of CVSS and bug bars). Each category is scored 1-10, producing an overall risk score. Provides a quick, semi-quantitative way to prioritize threats.

**The 5 factors**:
- **D**amage potential -- How much damage if exploited? (0 = nothing, 10 = complete system compromise)
- **R**eproducibility -- How easy to reproduce? (0 = nearly impossible, 10 = always works)
- **E**xploitability -- How much expertise/tooling needed? (0 = advanced, 10 = no skill needed)
- **A**ffected users -- What percentage of users affected? (0 = none, 10 = all users)
- **D**iscoverability -- How easy to find? (0 = requires source code access, 10 = visible in browser)

**Best used for**: Quick risk prioritization when you need a simple scoring model. Useful for comparing relative severity of findings. Criticized for subjectivity but still practical for rapid triage.

**Plugin implementation ideas**:
- Use DREAD as an alternative/supplementary scoring system alongside the existing Likelihood x Impact matrix
- LLM can estimate DREAD scores for each finding based on code context
- `/threatmodel:run --scoring dread` to use DREAD-based prioritization
- Compare DREAD scores with CVSS scores when scanner data is available

### MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge)

**What it is**: A globally-accessible knowledge base of adversary tactics and techniques based on real-world observations. Organized as a matrix: 14 tactics (columns) representing adversary goals (Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact, Reconnaissance, Resource Development) and hundreds of techniques/sub-techniques (rows) representing how those goals are achieved.

**Best used for**: Understanding real-world attacker behavior. Mapping defenses to known attack patterns. Red team/blue team exercises. Threat intelligence. Gap analysis (which ATT&CK techniques are you defended against?).

**Plugin implementation ideas**:
- Map findings to ATT&CK technique IDs (e.g., T1190 Exploit Public-Facing Application, T1078 Valid Accounts)
- `/threatmodel:attck-coverage` -- Analyze which ATT&CK techniques your application is defended against
- Use ATT&CK for red team agent prompting: "You are an attacker using technique T1078 (Valid Accounts). Given this codebase..."
- Generate ATT&CK Navigator layer JSON for visualization
- Cross-reference with ATT&CK's software entries (known malware and tools)
- Focus on ATT&CK for Cloud (covering AWS, Azure, GCP-specific techniques) and ATT&CK for Containers

### OCTAVE (Operationally Critical Threat, Asset, and Vulnerability Evaluation)

**What it is**: A risk-based strategic assessment framework developed by Carnegie Mellon's CERT. Focuses on organizational risk rather than technical vulnerabilities. Three variants: OCTAVE (large orgs), OCTAVE-S (small orgs), OCTAVE Allegro (streamlined, asset-focused).

**Best used for**: Organization-level risk assessment where you need to tie security to business objectives and operational risk tolerance. Less granular than STRIDE for code-level analysis but useful for prioritizing what to protect.

**Plugin implementation ideas**:
- Could inform the business-impact weighting in risk scoring
- Help classify assets by criticality (which services handle the most valuable data?)

### Trike

**What it is**: An open-source threat modeling methodology that uses a requirements-focused approach. Builds a requirements model (what actors can do to what assets in what states), then enumerates threats as violations of those requirements. Uses an actor-asset-action matrix.

**Best used for**: Systems where you have clear CRUD requirements per role. Produces very precise authorization models.

**Plugin implementation ideas**:
- Auto-generate actor-asset-action matrices from route definitions and RBAC configurations
- Compare the matrix against actual code to find authorization gaps

---

## 2. Red Team Roles and Specializations

The existing plugin defines three red team agents (Attacker, Insider, Data Thief). Here is a comprehensive taxonomy of red team specializations that could be implemented as additional agents.

### Network Attacker / Infrastructure Specialist

**Focus**: External network attack surface. Port scanning, service enumeration, network protocol exploitation, firewall bypass, DNS attacks, network segmentation testing.

**Code-level relevance**:
- Exposed ports in Docker/docker-compose configurations
- Network policies in Kubernetes manifests
- Firewall rules in Terraform/CloudFormation
- Service mesh configurations (Istio, Linkerd)
- TLS configuration and certificate management
- DNS configuration and subdomain enumeration

**Agent prompt concept**: "You are a network penetration tester examining this application's infrastructure configuration. Identify exposed services, missing network segmentation, weak TLS configurations, and potential lateral movement paths."

### Social Engineer

**Focus**: Human-factor attacks. Phishing, pretexting, baiting, tailgating. In code context: UI/UX patterns that facilitate phishing, misleading error messages, unsafe URL handling.

**Code-level relevance**:
- Open redirect vulnerabilities (attacker-controlled redirect URLs)
- Email template injection (can attacker control email content?)
- URL display patterns (does the UI show the full URL or just display text?)
- OAuth/SSO callback URL validation
- Password reset flow abuse
- Account enumeration via error messages ("no account with that email" vs "invalid credentials")
- Homograph/IDN domain attacks in URL validation

**Agent prompt concept**: "You are a social engineer analyzing this application. Find ways an attacker could abuse the application's features to trick users -- open redirects, phishing-friendly error messages, account enumeration, or abusable email/notification features."

### Insider Threat Specialist

**Focus**: Malicious or compromised authenticated users. Already partially covered by the Insider agent. Extended focus: database access, logging bypass, data export abuse, API key theft.

**Extended code-level relevance**:
- Bulk export/download endpoints without rate limits or audit logs
- Admin panels accessible from the public internet
- Shared service accounts or API keys
- Database connection strings with overprivileged credentials
- Missing audit trails for data access (not just modifications)
- Ability to disable logging or alerting
- Backdoor detection in code (hidden routes, debug endpoints, test credentials in production)

### Supply Chain Attacker

**Focus**: Attacking the software supply chain. Dependency confusion, typosquatting, compromised packages, malicious build scripts, CI/CD pipeline attacks.

**Code-level relevance**:
- Dependency manifests (package.json, requirements.txt, go.mod, Cargo.toml, Gemfile)
- Lockfile integrity (is the lockfile committed? can it be tampered with?)
- Pre/post-install scripts in npm packages
- GitHub Actions workflow injection (untrusted input in `run:` blocks)
- Docker base image provenance (using `:latest` tags, unverified images)
- Build script analysis (Makefile, webpack configs, build.gradle)
- Dependency pinning (exact versions vs ranges)
- Registry configuration (private registries, scoped packages)
- SLSA (Supply-chain Levels for Software Artifacts) compliance

**Agent prompt concept**: "You are a supply chain attacker. Analyze this project's dependency manifests, build scripts, and CI/CD configuration. Find opportunities for dependency confusion, typosquatting, or build pipeline injection."

**Plugin implementation ideas**:
- `/threatmodel:supply-chain` -- Dedicated supply chain analysis
- Check for dependency confusion (public package with same name as internal)
- Analyze GitHub Actions for injection vulnerabilities
- Verify lockfile integrity and pinning strategy
- Check Docker base images for known vulnerabilities and provenance

### API Specialist

**Focus**: API-specific attacks. REST, GraphQL, gRPC, WebSocket vulnerabilities. BOLA (Broken Object Level Authorization), BFLA (Broken Function Level Authorization), mass assignment, excessive data exposure.

**Code-level relevance**:
- API route definitions and middleware chains
- GraphQL schema (introspection enabled? query depth limits? complexity limits?)
- OpenAPI/Swagger specifications vs actual implementation
- Rate limiting configuration
- API versioning and deprecation
- Mass assignment protection (which fields are assignable?)
- Response filtering (are you returning entire DB objects?)
- CORS configuration
- API key management and rotation

**Maps to OWASP API Security Top 10 (2023)**:
- API1: Broken Object Level Authorization
- API2: Broken Authentication
- API3: Broken Object Property Level Authorization
- API4: Unrestricted Resource Consumption
- API5: Broken Function Level Authorization
- API6: Unrestricted Access to Sensitive Business Flows
- API7: Server Side Request Forgery
- API8: Security Misconfiguration
- API9: Improper Inventory Management
- API10: Unsafe Consumption of APIs

**Plugin implementation ideas**:
- `/threatmodel:api` -- Dedicated API security analysis using OWASP API Top 10
- Auto-discover API endpoints from code (Express routes, FastAPI decorators, Spring annotations)
- Analyze GraphQL schemas for depth/complexity attack vectors
- Check for BOLA by analyzing authorization middleware on each endpoint
- Verify rate limiting on all public endpoints

### Cloud Security Specialist

**Focus**: Cloud-specific misconfigurations and attack vectors. IAM policy analysis, storage bucket permissions, serverless function security, cloud network security groups.

**Code-level relevance**:
- Terraform/CloudFormation/Pulumi configurations
- IAM policies (overprivileged roles, wildcard permissions)
- S3/GCS/Azure Blob storage ACLs and policies
- Security group rules (0.0.0.0/0 ingress)
- Lambda/Cloud Functions environment variables (secrets in plaintext)
- KMS key policies
- CloudTrail/audit logging configuration
- VPC configuration and network ACLs

**Agent prompt concept**: "You are a cloud security specialist. Analyze this infrastructure-as-code for misconfigurations: overprivileged IAM, public storage buckets, missing encryption, weak network controls, and missing audit logging."

**Plugin implementation ideas**:
- `/threatmodel:cloud` or `/threatmodel:iac` -- Infrastructure-as-Code security analysis
- Integrates with Checkov, tfsec, KICS for real scanning
- Claude analyzes IAM policy semantics (what can this role actually do?)
- Check for CIS Benchmark compliance for AWS/Azure/GCP

### Mobile Application Specialist

**Focus**: Mobile-specific attack vectors. Insecure data storage, certificate pinning, binary protections, inter-process communication.

**Code-level relevance**:
- Insecure data storage (SharedPreferences, UserDefaults without encryption)
- Missing certificate pinning
- Exported Android components (activities, services, broadcast receivers)
- iOS App Transport Security exceptions
- Hardcoded secrets in mobile binaries
- Deep link / Universal link validation
- WebView security configuration
- Biometric authentication implementation

### Cryptography Specialist

**Focus**: Cryptographic implementation flaws. Weak algorithms, improper key management, random number generation issues, protocol-level vulnerabilities.

**Code-level relevance**:
- Use of deprecated algorithms (MD5, SHA1 for security, DES, RC4)
- ECB mode usage (should be CBC, GCM, or ChaCha20-Poly1305)
- Hardcoded encryption keys or IVs
- Insufficient key lengths (RSA < 2048, AES < 128)
- Custom crypto implementations (should use established libraries)
- Random number generation (Math.random() for security purposes)
- Password hashing (plain SHA256 instead of bcrypt/Argon2/scrypt)
- TLS configuration (protocol versions, cipher suites)
- JWT algorithm confusion (accepting `none`, RS256 vs HS256 confusion)

**Agent prompt concept**: "You are a cryptography specialist. Analyze all cryptographic usage in this codebase. Find weak algorithms, improper key management, predictable randomness, and protocol-level issues."

**Plugin implementation ideas**:
- `/threatmodel:crypto` already exists in the OWASP A02 mapping
- Extend with deep cryptographic analysis: algorithm inventory, key management audit, protocol analysis

---

## 3. Open Source SAST and Security Scanning Tools

### Multi-Language / Universal Scanners

**Semgrep**
- **Languages**: 30+ (Python, JavaScript/TypeScript, Java, Go, Ruby, C, C++, PHP, Rust, and more)
- **What it does best**: Pattern-based static analysis with a simple rule syntax. Supports custom rules that are easy to write (YAML-based). Huge community rule registry (semgrep.dev/r). Excellent for enforcing organization-specific coding standards and security patterns. Fast, low false-positive rate.
- **Integration**: Already listed in the plugin. Should be the primary recommended scanner.
- **Key capability**: Taint analysis (tracking data from sources to sinks) in Pro version, basic pattern matching in OSS.

**CodeQL (GitHub)**
- **Languages**: C, C++, C#, Go, Java, JavaScript/TypeScript, Python, Ruby, Swift
- **What it does best**: Semantic code analysis using a query language. Treats code as data you can query. Extremely powerful for finding complex vulnerability patterns that require understanding data flow across functions and files. Built into GitHub Advanced Security.
- **Integration**: Best for CI/CD integration via GitHub Actions. Produces SARIF output. Query packs available for common vulnerability types.
- **Key capability**: Deep inter-procedural data flow analysis. Can find vulnerabilities that span multiple files and function calls.

**SonarQube (Community Edition)**
- **Languages**: 30+ languages
- **What it does best**: Comprehensive code quality and security analysis. Tracks security hotspots, technical debt, code smells, and vulnerabilities. Good for ongoing monitoring with a dashboard. Community edition is free and open source.
- **Integration**: Self-hosted server with CI/CD plugins. Good for organizations wanting a central security dashboard.

### Language-Specific Scanners

**Bandit (Python)**
- **What it does best**: Python-specific security linter. Finds common security issues in Python code: use of `eval()`, `exec()`, `pickle`, SQL injection patterns, weak crypto, hardcoded passwords, insecure temp file creation.
- **Integration**: Already listed. Fast, pip-installable, good default rules. Produces SARIF output.

**gosec (Go)**
- **What it does best**: Go-specific security scanner. Finds SQL injection, command injection, hardcoded credentials, weak crypto, insecure TLS configurations, integer overflow, file path issues, and more.
- **Integration**: Already listed. Go module, integrates with `go vet`.

**Brakeman (Ruby/Rails)**
- **What it does best**: Rails-specific static analysis. Understands Rails conventions and finds Rails-specific vulnerabilities: mass assignment, SQL injection via ActiveRecord, XSS in ERB templates, unsafe redirects, file access issues.
- **Integration**: Already listed. Gem installation. Produces JSON and HTML output.

**SpotBugs + Find Security Bugs (Java)**
- **What it does best**: Bytecode-level analysis for Java. The Find Security Bugs plugin adds 150+ security-specific bug patterns: injection flaws, weak crypto, XXE, SSRF, deserialization, LDAP injection.
- **Integration**: Already listed (as spotbugs). Maven/Gradle plugin.

**PHPStan (PHP)**
- **What it does best**: PHP static analysis focused on finding bugs. With security-focused extensions, detects SQL injection, XSS, file inclusion, command injection.
- **Integration**: Already listed. Composer installation.

**cargo-audit (Rust)**
- **What it does best**: Audits Cargo.lock files for crates with known security vulnerabilities from the RustSec Advisory Database.
- **Integration**: Already listed. Cargo subcommand.

### Additional Scanners Not Yet Listed

**ESLint Security Plugins (JavaScript/TypeScript)**
- `eslint-plugin-security` -- Detects potential security hotspots in Node.js code
- `eslint-plugin-no-unsanitized` -- Mozilla's plugin for detecting unsafe DOM manipulation
- **Why add**: Most JS/TS projects already have ESLint configured. Zero-friction security scanning.

**Snyk Code (Free Tier)**
- **Languages**: JavaScript, TypeScript, Python, Java, C#, Go, Ruby, PHP, Swift, Kotlin
- **What it does best**: ML-powered SAST with high accuracy. Free tier covers up to 200 tests/month. Real-time IDE integration.
- **Integration**: CLI tool (`snyk code test`), produces SARIF.

**Grype + Syft (Anchore)**
- **What it does best**: Container image and SBOM vulnerability scanning. Syft generates SBOMs, Grype scans them for vulnerabilities. Alternative to Trivy for container scanning.
- **Integration**: CLI tools, produce JSON/SARIF output.

**njsscan (Node.js)**
- **What it does best**: Semantic analysis for Node.js security. Uses Semgrep under the hood with Node.js-specific rules. Covers Express, Koa, Hapi, Fastify.

**Bearer (Privacy/Data)**
- **What it does best**: Scans code for data security risks and privacy violations. Classifies sensitive data types found in code and checks for proper handling. Useful for GDPR/privacy compliance.
- **Integration**: CLI tool, SARIF output.

### Secrets Detection

**Gitleaks**
- **What it does best**: Scans git repos for hardcoded secrets and sensitive data. Scans entire git history. Customizable rules via TOML config. Fast.
- **Integration**: Already listed. Pre-commit hook support. Produces JSON output.

**TruffleHog**
- **What it does best**: High-signal secret detection with verification. Can actually verify if detected secrets are live/active (connects to APIs to check). Supports 700+ credential detectors. Scans git, S3, GCS, filesystems.
- **Integration**: Already listed. CLI tool. The verification feature is unique and valuable.

**detect-secrets (Yelp)**
- **What it does best**: Server-side, pre-commit-hook focused. Maintains a baseline of known secrets to prevent new ones. Good for incremental secret detection in CI.

### Infrastructure as Code (IaC) Scanners

**Checkov (Bridgecrew/Palo Alto)**
- **What it does best**: Scans Terraform, CloudFormation, Kubernetes, Docker, ARM templates, Serverless, Helm charts. 1000+ built-in policies. CIS Benchmark compliance checks. Supports custom policies in Python and YAML.
- **Integration**: Already listed. pip-installable. Produces SARIF, JSON, JUnit output.

**tfsec (Aqua Security)**
- **What it does best**: Terraform-specific security scanner. Fast, focused, well-maintained. Now merged into Trivy but still usable standalone. Good for Terraform-only shops.
- **Integration**: Already listed.

**KICS (Checkmarx)**
- **What it does best**: Multi-IaC scanner covering Terraform, CloudFormation, Ansible, Docker, Kubernetes, OpenAPI, and more. 2000+ queries. Unique in covering Ansible and OpenAPI specs.
- **Integration**: Already listed (as kics). Docker-based or binary.

**Trivy (Aqua Security)**
- **What it does best**: Swiss army knife. Scans container images, filesystems, git repos, Kubernetes, and IaC. Covers vulnerabilities, misconfigurations, secrets, and licenses. Increasingly the go-to all-in-one scanner.
- **Integration**: Already listed. Binary or Docker. Produces SARIF, JSON, table output.

### Dependency Scanning

**OSV-Scanner (Google)**
- **What it does best**: Scans dependency manifests and lockfiles against the OSV (Open Source Vulnerabilities) database. Covers all ecosystems. Maintained by Google.
- **Integration**: Already listed. Binary. JSON output.

**pip-audit (Python)**
- **What it does best**: Audits Python environments and requirements files against the PyPI Advisory Database and OSV.
- **Integration**: Already listed.

**npm audit (Node.js)**
- **What it does best**: Built into npm. Audits dependencies against the npm advisory database. Zero setup.
- **Integration**: Already listed.

### Plugin Implementation Ideas for Scanner Integration

- **Scanner auto-detection priority**: Trivy > Semgrep > language-specific (Bandit/gosec/etc.) > dependency scanners
- **Unified output normalization**: All scanner output should be normalized to a common finding format (SARIF-compatible)
- **Scanner recommendation engine**: Based on detected languages and file types, recommend which scanners to install
- **Parallel scanner execution**: Run all detected scanners simultaneously using background tasks
- **Smart deduplication**: When multiple scanners find the same issue, keep the most detailed finding and note scanner agreement

---

## 4. AI-Powered Security Analysis and Threat Modeling

### Current State of LLM-Powered Security (2025-2026)

**LLM-Assisted Vulnerability Detection**

Key approaches being used:
- **Code review augmentation**: LLMs analyze code diffs for security implications, understanding business logic context that SAST tools miss. This is exactly what the claude-threatmodel plugin does.
- **Vulnerability explanation and remediation**: LLMs explain vulnerabilities in context and generate specific, compilable fixes (not generic OWASP advice). Already planned in `/threatmodel:fix`.
- **False positive reduction**: LLMs triage scanner output, understanding whether a flagged pattern is actually exploitable in context. A key differentiator for LLM-based tools.

**LLM Red Teaming / Offensive Security**

Approaches:
- **Attack path reasoning**: Given a set of findings, LLMs reason about how an attacker would chain them together. More creative than rule-based attack graph tools. Already planned in expert mode.
- **Exploit generation assistance**: LLMs can draft proof-of-concept exploits for identified vulnerabilities, helping verify if an issue is actually exploitable.
- **Social engineering simulation**: LLMs craft realistic phishing emails or pretexting scenarios to test organizational resilience.
- **Fuzzing input generation**: LLMs generate intelligent fuzz inputs based on understanding of the code's input parsing logic, rather than purely random mutation.

**LLM-Assisted Threat Modeling**

Approaches:
- **Architecture understanding from code**: LLMs read code and infer architecture, data flows, trust boundaries without requiring manual diagramming. This is a major advantage over traditional threat modeling tools that require manual input.
- **Natural language threat descriptions**: Instead of requiring security expertise to interpret findings, LLMs explain threats in developer-friendly language.
- **Compliance mapping automation**: LLMs map technical findings to compliance framework requirements, understanding the semantic relationship rather than needing exact keyword matches.
- **Plan-time security review**: Reviewing implementation plans before code is written. This is the flagship feature of claude-threatmodel (`/threatmodel:review-plan`).

### Innovative Approaches to Explore

**1. Agentic Security Pipelines**

Multiple specialized LLM agents working together, each with a focused security domain. The claude-threatmodel architecture already embodies this with its subagent approach. Additional agent specializations to consider:

- **Dependency analyst agent**: Deeply analyzes each dependency for supply chain risk, not just known CVEs but maintenance status, contributor patterns, recent suspicious commits
- **Configuration auditor agent**: Specializes in analyzing configuration files across all layers (app config, Docker, K8s, CI/CD, cloud IaC)
- **API contract validator agent**: Compares OpenAPI specs against actual route implementations to find undocumented endpoints or spec drift
- **Regression detector agent**: Compares current findings against baseline to detect security regression

**2. Semantic Code Understanding for Security**

Going beyond pattern matching (what SAST does) to understanding what code *means*:

- **Intent analysis**: "This function is trying to do authentication" -- then check if it does it correctly
- **Data classification**: Automatically classify data types (PII, financial, health, credentials) based on variable names, database schemas, and usage patterns
- **Trust boundary inference**: Automatically identify where trust boundaries exist based on network calls, authentication middleware, input validation points
- **Business logic flaw detection**: Understand business rules from code and find logical flaws (e.g., "users can apply a discount code multiple times" or "race condition in payment processing")

**3. Continuous Security Posture Monitoring**

- **Drift detection**: Compare current threat model against baseline, alert on new attack surface
- **Security debt tracking**: Track unresolved findings over time, estimate effort to resolve
- **Trend analysis**: "Your injection risk has been increasing over the last 5 PRs"

**4. Interactive Threat Exploration**

- **Conversational threat modeling**: "What would happen if an attacker gained access to the database credentials?"
- **What-if analysis**: "If we add rate limiting here, which attack paths does that close?"
- **Guided remediation**: Walk the developer through fixing an issue step-by-step

**5. Security Knowledge Graph**

Build a knowledge graph of the application's security properties:
- Components, data flows, trust boundaries (architecture)
- Security controls (what exists)
- Threats (what could go wrong)
- Findings (what is wrong)
- Attack paths (how findings chain together)

This graph enables queries like:
- "What is the blast radius if this API key is compromised?"
- "Which components have no authentication?"
- "Show all paths from unauthenticated input to the database"

### Plugin Implementation Ideas

- **Phase 1 (current)**: Single-agent quick scan + full STRIDE analysis. Already implemented.
- **Phase 2 (planned in IDEA.md)**: Multi-agent parallel analysis with OWASP/STRIDE categories. Subagent consolidation. Red team agents.
- **Phase 3 (future)**: Knowledge graph persistence. Drift detection. Continuous monitoring. Interactive threat exploration. Additional frameworks (PASTA, LINDDUN, ATT&CK).

---

## 5. Compliance and Security Frameworks

### NIST Cybersecurity Framework (CSF) 2.0

**What it is**: A voluntary framework of standards, guidelines, and best practices. Organized into 6 core functions: Govern, Identify, Protect, Detect, Respond, Recover. Each function contains categories and subcategories with informative references.

**Code-level automatable checks**:
- **Identify**: Asset inventory (auto-discover components, services, data stores from code)
- **Protect**: Access control implementation verification, data encryption checks, input validation
- **Detect**: Logging and monitoring configuration, anomaly detection setup
- **Respond**: Error handling patterns, incident response configuration

**Plugin implementation ideas**:
- `/threatmodel:nist` -- Map findings to NIST CSF categories
- Auto-check Protect subcategories: PR.AC (Access Control), PR.DS (Data Security), PR.IP (Information Protection)

### CIS Controls (v8)

**What it is**: A prioritized set of 18 security controls (formerly 20). Organized into 3 Implementation Groups (IG1-IG3) based on organizational maturity. Extremely actionable and specific.

**Key controls automatable at code level**:
- **CIS 2**: Software Inventory -- Auto-generate SBOM from manifests
- **CIS 3**: Data Protection -- Encryption at rest and in transit checks
- **CIS 4**: Secure Configuration -- Hardening checks for frameworks, servers, containers
- **CIS 6**: Access Control Management -- RBAC implementation, least privilege checks
- **CIS 7**: Continuous Vulnerability Management -- Dependency scanning, SAST
- **CIS 12**: Network Infrastructure Management -- Network configuration in IaC
- **CIS 16**: Application Software Security -- All SAST checks, secure coding practices

**Plugin implementation ideas**:
- `/threatmodel:cis` -- Check CIS Controls applicable to the codebase
- Focus on Implementation Group 1 (essential, applicable to all organizations)
- Map existing OWASP/STRIDE findings to CIS Control IDs

### ISO 27001:2022

**What it is**: International standard for Information Security Management Systems (ISMS). Annex A contains 93 controls organized in 4 themes: Organizational, People, Physical, Technological.

**Code-level automatable checks (Annex A Technological Controls)**:
- A.8.3: Information access restriction (authorization checks in code)
- A.8.5: Secure authentication (password policies, MFA implementation)
- A.8.7: Protection against malware (input validation, file upload restrictions)
- A.8.9: Configuration management (secure defaults, hardening)
- A.8.12: Data leakage prevention (logging, data flow controls)
- A.8.24: Use of cryptography (algorithm and key management checks)
- A.8.25: Secure development lifecycle (this plugin itself contributes to this control)
- A.8.26: Application security requirements (threat modeling -- this plugin)
- A.8.28: Secure coding (SAST checks, secure coding patterns)

**Plugin implementation ideas**:
- Map findings to ISO 27001 Annex A control IDs
- Generate evidence artifacts for ISO audits (threat model documents, scan results)

### SOC 2 (Service Organization Control)

**What it is**: An auditing framework based on the Trust Services Criteria (TSC): Security, Availability, Processing Integrity, Confidentiality, Privacy. Relevant for SaaS companies and service providers.

**Code-level automatable checks**:
- **Security (CC)**: Access controls (CC6.1), system boundaries (CC6.6), change management (CC8.1)
- **Availability (A)**: Rate limiting, circuit breakers, health checks, redundancy
- **Processing Integrity (PI)**: Input validation, data integrity checks, error handling
- **Confidentiality (C)**: Encryption, data classification, access logging
- **Privacy (P)**: Consent mechanisms, data retention, deletion capabilities

**Plugin implementation ideas**:
- `/threatmodel:soc2` -- SOC 2 readiness check
- Focus on common criteria (CC) -- applicable to all SOC 2 reports
- Generate evidence documentation for auditors
- Check for logging of security-relevant events (CC7.2)
- Verify change management practices (CC8.1) -- git history analysis

### PCI-DSS (Payment Card Industry Data Security Standard) v4.0

**What it is**: Required for anyone who stores, processes, or transmits cardholder data. 12 requirements with detailed sub-requirements. v4.0 (effective March 2025) adds new requirements around customized approach, targeted risk analysis, and enhanced authentication.

**Code-level automatable checks**:
- **Req 2**: Secure configurations (no default passwords, unnecessary services)
- **Req 3**: Protect stored account data (encryption, key management, masking)
- **Req 4**: Encrypt transmission (TLS configuration checks)
- **Req 6**: Develop secure systems (SAST, dependency scanning, code review)
- **Req 7**: Restrict access (RBAC, least privilege)
- **Req 8**: Identify users and authenticate (MFA, password policies, session management)
- **Req 10**: Log and monitor (audit logging, log retention, integrity)

**Plugin implementation ideas**:
- `/threatmodel:pci` -- PCI-DSS compliance check (relevant checks only)
- Auto-detect if the application handles payment data (Stripe/PayPal/Braintree SDKs, credit card number patterns)
- Only activate PCI-relevant checks when payment processing is detected
- Check for PAN (Primary Account Number) storage/logging violations
- Verify strong cryptography for cardholder data

### HIPAA (Health Insurance Portability and Accountability Act)

**What it is**: US regulation protecting Protected Health Information (PHI). Covers administrative, physical, and technical safeguards. Relevant for healthcare applications and any system handling health data.

**Code-level automatable checks**:
- **Technical Safeguards**: Access control (unique user ID, emergency access, automatic logoff, encryption)
- **Audit controls**: Logging of PHI access and modifications
- **Integrity controls**: Data integrity checks, electronic signatures
- **Transmission security**: Encryption in transit, integrity controls

**Plugin implementation ideas**:
- `/threatmodel:hipaa` -- HIPAA technical safeguard checks
- Auto-detect if application handles health data (HL7/FHIR libraries, health-related data models)
- Check for PHI logging violations (PHI should never appear in logs)
- Verify encryption of PHI at rest and in transit
- Check for audit trail completeness on PHI access

### GDPR (General Data Protection Regulation)

**What it is**: EU regulation on data protection and privacy. Applies to any organization processing personal data of EU residents. Key principles: lawfulness, purpose limitation, data minimization, accuracy, storage limitation, integrity and confidentiality, accountability.

**Code-level automatable checks**:
- **Data minimization**: Are you collecting only necessary data? (check form fields vs database schema)
- **Right to erasure**: Is there a data deletion mechanism? (check for delete endpoints/functions)
- **Data portability**: Is there a data export mechanism? (check for export endpoints)
- **Consent management**: Is consent collected before data processing? (check for consent flows)
- **Privacy by design**: Data protection impact assessment artifacts
- **Data breach notification**: Incident response mechanisms, monitoring
- **Cross-border transfers**: Data residency checks in cloud configurations

**Plugin implementation ideas**:
- `/threatmodel:gdpr` or combine with `/threatmodel:privacy` (LINDDUN-based)
- Auto-detect PII fields and trace their data flows
- Check for data retention policies and automated deletion
- Verify consent mechanisms exist before data collection
- Check for Data Processing Agreement (DPA) requirements with third-party services

### Cross-Compliance Mapping

Many frameworks overlap. A single finding may map to multiple compliance requirements:

| Finding | OWASP | CIS | PCI-DSS | SOC 2 | ISO 27001 |
|---------|-------|-----|---------|-------|-----------|
| Missing input validation | A03 | 16.4 | 6.2.4 | CC6.1 | A.8.28 |
| Weak password policy | A07 | 6.2 | 8.3.6 | CC6.1 | A.8.5 |
| Missing encryption in transit | A02 | 3.10 | 4.2.1 | C1.1 | A.8.24 |
| Missing audit logging | A09 | 8.5 | 10.2.1 | CC7.2 | A.8.15 |
| Broken access control | A01 | 6.8 | 7.2.1 | CC6.1 | A.8.3 |

**Plugin implementation ideas**:
- `/threatmodel:compliance [--frameworks owasp,soc2,pci,hipaa,gdpr,nist,cis,iso27001]`
- Single scan, multiple compliance mappings
- Generate compliance evidence packages per framework
- Dashboard showing coverage across all selected frameworks

---

## 6. Prioritized Implementation Roadmap

Based on this research, here are the highest-impact additions to the claude-threatmodel plugin, organized by implementation priority.

### Immediate (Enhance existing tools)

1. **OWASP API Security Top 10 framework** -- New framework file + dedicated `/threatmodel:api` skill. APIs are the primary attack surface for modern applications.

2. **Supply chain analysis agent** -- `/threatmodel:supply-chain`. Dependency confusion, CI/CD security, lockfile integrity. High impact, relatively straightforward to implement.

3. **Additional red team agent: Social Engineer** -- Finds open redirects, account enumeration, phishing-friendly features. Extends the existing expert-mode red team.

4. **MITRE ATT&CK technique mapping** -- Add ATT&CK IDs to findings. Helps developers understand real-world attack context.

### Short-term (New frameworks and agents)

5. **LINDDUN privacy framework** -- `/threatmodel:privacy`. Privacy-by-design analysis. GDPR relevance makes this high-priority for any application handling EU user data.

6. **Cloud/IaC security agent** -- `/threatmodel:cloud`. Analyzes Terraform, CloudFormation, K8s, Docker for misconfigurations. Pairs with Checkov/tfsec/Trivy integration.

7. **Cross-compliance mapping** -- Single analysis, mapped to OWASP + SOC 2 + PCI-DSS + NIST CSF + CIS Controls. Generate compliance evidence packages.

8. **Cryptography specialist agent** -- Deep crypto analysis beyond OWASP A02. Algorithm inventory, key management audit, protocol analysis.

### Medium-term (Advanced capabilities)

9. **PASTA methodology integration** -- 7-stage guided workflow. Business-risk-aligned threat modeling for larger projects.

10. **Attack tree generation** -- Mermaid-based attack tree diagrams from findings. Interactive "expand this node" exploration.

11. **Security knowledge graph** -- Persistent graph of components, controls, threats, findings, attack paths. Enables sophisticated queries about blast radius and defense coverage.

12. **ATT&CK coverage analysis** -- `/threatmodel:attck-coverage`. Which ATT&CK techniques is the application defended against? Generate ATT&CK Navigator layers.

### Long-term (Ecosystem features)

13. **Continuous drift detection** -- Compare current state to baseline, alert on new attack surface from code changes.

14. **Interactive threat exploration** -- Conversational "what-if" analysis. "What happens if this API key leaks?"

15. **Scanner recommendation engine** -- Based on detected tech stack, suggest and optionally auto-install the most relevant security scanners.

16. **SBOM generation** -- Generate Software Bill of Materials in CycloneDX or SPDX format for supply chain transparency.

---

## 7. Key Architectural Principles

Based on this research, the following principles should guide all new additions:

1. **Use each tool for what it is good at**: Real scanners for pattern detection. LLMs for understanding intent, business logic, and architecture. Red team agents for reasoning about exploitability. Never pretend one can do the other's job.

2. **Compose, don't monolith**: Every tool works standalone. Framework tools orchestrate their categories. The orchestrator picks the right combination. Everything composes.

3. **Context efficiency**: Subagent architecture keeps the main conversation context clean. Only summaries flow back. This is critical for developer experience.

4. **Progressive depth**: Quick scans for rapid feedback. Deep analysis on demand. Expert mode for pre-release thorough review. Never force the developer to wait for analysis they did not ask for.

5. **Real severity, not noise**: Severity comes from actual exploitability, not pattern matches. LLMs can reason about whether a finding is actually dangerous in context.

6. **Framework-agnostic findings, framework-specific mapping**: Find the vulnerability once, map it to OWASP, STRIDE, NIST, SOC 2, PCI-DSS, ATT&CK, and any other framework simultaneously.

7. **No fake compliance**: Never generate compliance percentages from LLM analysis alone. Be honest about what was checked, what was not, and what requires human verification or real tooling.
