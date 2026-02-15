# PASTA Threat Modeling Framework

## Overview

PASTA (Process for Attack Simulation and Threat Analysis) is a 7-stage, risk-centric threat modeling methodology that aligns business objectives with technical requirements and attack simulation. Unlike STRIDE, which categorizes threats by type, PASTA follows a sequential process that moves from high-level business context down to concrete attack scenarios and risk-weighted mitigations.

**When to use PASTA**: Use PASTA when the analysis requires business context, when you need to prioritize findings by real-world exploitability, or when the system under review has complex risk trade-offs. PASTA is especially valuable for applications that handle financial transactions, regulated data, or critical infrastructure.

**Key differentiator**: PASTA is the ONLY framework dispatched SEQUENTIALLY. Each stage feeds the next. Do not skip stages or run them in parallel. The output of Stage 1 constrains Stage 2, Stage 2 constrains Stage 3, and so on through Stage 7.

---

## Stage 1: Define Business Objectives

**Description**: Establish what the application protects, why it matters, and what business impact a compromise would have. This stage ensures the entire threat model stays anchored to real business value.

**Key Activities**:
- Identify the application's core business purpose
- Enumerate critical business processes the application supports
- Define risk appetite and tolerance thresholds
- Identify regulatory and compliance requirements (PCI-DSS, HIPAA, SOX, GDPR)
- Establish business impact categories (financial, reputational, legal, operational)

**Outputs**:
- Business context statement
- Risk tolerance matrix
- Compliance requirement checklist
- Prioritized list of business-critical assets

**Questions to Ask**:
- What is the worst business outcome if this application is compromised?
- What data, if exposed, would trigger regulatory notification requirements?
- What is the acceptable downtime for this service?
- Which business processes depend on this application's integrity?
- Who are the stakeholders that would be impacted by a breach?

**How Claude Should Approach This Stage**:
When analyzing code, infer business objectives from configuration files, database schemas, API contracts, and documentation. Look for payment processing, PII handling, authentication flows, and admin interfaces to determine what the application protects. Flag when business context is ambiguous and state assumptions explicitly.

---

## Stage 2: Define Technical Scope

**Description**: Map the technical boundaries of the system, including architecture, infrastructure, protocols, and the attack surface visible to external and internal actors.

**Key Activities**:
- Enumerate all entry points (APIs, web forms, file uploads, message queues, webhooks)
- Identify network boundaries and deployment topology
- Catalog protocols in use (HTTP/HTTPS, gRPC, WebSocket, MQTT, AMQP)
- Map external dependencies (third-party APIs, SaaS integrations, CDNs)
- Document technology stack (languages, frameworks, databases, caches)

**Outputs**:
- Attack surface inventory
- Network and deployment diagram (or textual equivalent)
- Technology stack inventory
- Data flow diagram (DFD) Level 0 and Level 1

**Questions to Ask**:
- What are all the ways data enters and exits this system?
- Which components are internet-facing vs. internal-only?
- What third-party services does the application depend on?
- What protocols and ports are exposed?
- Are there any legacy components or deprecated endpoints still reachable?

**How Claude Should Approach This Stage**:
Scan for route definitions, controller files, API gateway configurations, Dockerfiles, Kubernetes manifests, and infrastructure-as-code files. Build a mental model of entry points from `@RequestMapping`, Express routes, FastAPI paths, or equivalent. Identify database connection strings, external API calls, and message broker configurations to map data flows.

---

## Stage 3: Application Decomposition

**Description**: Break the application into its constituent components and analyze trust boundaries, user roles, privilege levels, and data sensitivity at each layer.

**Key Activities**:
- Decompose the application into functional components (auth, payment, messaging, admin)
- Identify all user roles and their permission boundaries
- Map trust boundaries between components
- Classify data by sensitivity (public, internal, confidential, restricted)
- Document authentication and authorization mechanisms per component
- Identify shared resources and cross-component dependencies

**Outputs**:
- Component inventory with trust levels
- Role-permission matrix
- Data classification table
- Trust boundary diagram
- Authentication/authorization flow documentation

**Questions to Ask**:
- What trust boundaries does data cross between components?
- Which components run with elevated privileges?
- How are service-to-service calls authenticated?
- Where does data sensitivity change (encryption, masking, aggregation)?
- Are there shared databases or caches across trust boundaries?

**How Claude Should Approach This Stage**:
Examine middleware, decorators, and interceptors for authorization logic. Look for role definitions, permission enums, and policy files. Trace how requests flow through middleware chains. Identify where privilege escalation boundaries exist (user to admin, service to service). Map database schemas to understand data relationships and sensitivity.

---

## Stage 4: Threat Analysis

**Description**: Identify threats using real-world intelligence, attack patterns, and adversary tactics. Cross-reference with known threat databases to ground the analysis in actual attacker behavior.

**Key Activities**:
- Research relevant threat actors for this type of application
- Cross-reference with MITRE ATT&CK techniques applicable to the technology stack
- Identify historically exploited attack patterns for similar applications
- Map threats to the components and trust boundaries from Stage 3
- Consider both external attackers and malicious insiders
- Enumerate supply chain threats relevant to dependencies

**Outputs**:
- Threat catalog with MITRE ATT&CK mappings
- Threat actor profiles (external, insider, supply chain)
- Attack tree diagrams for high-value targets
- Threat-to-component mapping matrix

**Questions to Ask**:
- What MITRE ATT&CK techniques are most relevant to this stack?
- What attacks have been commonly seen against similar applications?
- What would a motivated insider with legitimate access attempt?
- Which dependencies have had recent CVEs?
- What attack chains could pivot from a low-privilege entry point to high-value assets?

**Common MITRE ATT&CK Mappings**:
- T1190: Exploit Public-Facing Application
- T1059: Command and Scripting Interpreter
- T1078: Valid Accounts
- T1098: Account Manipulation
- T1134: Access Token Manipulation
- T1552: Unsecured Credentials
- T1210: Exploitation of Remote Services

**How Claude Should Approach This Stage**:
Use findings from Stages 2 and 3 to focus threat identification. For each entry point and trust boundary, consider what known attack patterns apply. Prioritize threats that are realistic given the technology stack. Do not enumerate theoretical threats with no plausible attack path in the code under review.

---

## Stage 5: Vulnerability Analysis

**Description**: Identify specific weaknesses in the code and configuration that could be exploited by the threats identified in Stage 4. Map findings to CWE identifiers.

**Key Activities**:
- Perform static analysis of code for known vulnerability patterns
- Map identified weaknesses to CWE (Common Weakness Enumeration) entries
- Correlate vulnerabilities with threats from Stage 4
- Assess vulnerability exploitability (attack complexity, prerequisites)
- Check for known CVEs in dependencies (SCA)
- Review security configurations and hardening

**Outputs**:
- Vulnerability inventory with CWE mappings
- Vulnerability-to-threat correlation matrix
- Exploitability assessment per vulnerability
- Dependency vulnerability report

**Common CWE Mappings**:
- CWE-89: SQL Injection
- CWE-79: Cross-site Scripting (XSS)
- CWE-287: Improper Authentication
- CWE-862: Missing Authorization
- CWE-311: Missing Encryption of Sensitive Data
- CWE-502: Deserialization of Untrusted Data
- CWE-918: Server-Side Request Forgery (SSRF)
- CWE-78: OS Command Injection
- CWE-22: Path Traversal
- CWE-798: Use of Hard-coded Credentials

**Questions to Ask**:
- Does the code use parameterized queries everywhere, or are there dynamic query construction paths?
- Are there deserialization points that accept untrusted input?
- Do all endpoints enforce authentication and authorization checks?
- Are secrets hard-coded or stored in configuration files within the repository?
- Are input validation and output encoding applied consistently?

**How Claude Should Approach This Stage**:
This is the core code analysis stage. Trace data flows from entry points (Stage 2) through components (Stage 3) looking for the vulnerabilities that enable the threats (Stage 4). For each finding, assign a CWE identifier and note the specific file and line. Prioritize findings that directly enable threats from Stage 4 over theoretical weaknesses.

---

## Stage 6: Attack Simulation

**Description**: Simulate realistic exploit chains by combining the threats from Stage 4 with the vulnerabilities from Stage 5. Score each attack scenario by exploitability and impact.

**Key Activities**:
- Construct multi-step attack scenarios (exploit chains)
- Assess feasibility of each attack path (required access, complexity, tooling)
- Score exploitability using CVSS or DREAD
- Identify which attack paths lead to the business-critical assets from Stage 1
- Determine whether existing controls detect or prevent each attack chain
- Identify attack paths that bypass multiple layers of defense

**Outputs**:
- Attack scenario descriptions with step-by-step exploit chains
- Exploitability scores (CVSS base score or DREAD rating)
- Attack path diagrams showing entry point to target asset
- Detection gap analysis (which attacks evade current monitoring)

**Questions to Ask**:
- Can an unauthenticated attacker chain two low-severity vulnerabilities into a high-impact exploit?
- What is the shortest attack path from the internet to the most sensitive data?
- Would the current logging and alerting detect this attack in progress?
- What attacker skill level and tooling is required for each path?
- Are there attack paths that bypass all existing controls?

**How Claude Should Approach This Stage**:
Combine findings from Stages 4 and 5 into concrete attack narratives. For example: "An attacker exploits [CWE-89 in /api/search] to extract session tokens from the database, then uses a stolen admin token to access [/admin/export], bypassing the IP allowlist because the check only applies to the login endpoint." Score each chain and identify which ones reach the business-critical assets identified in Stage 1.

---

## Stage 7: Risk and Impact Analysis

**Description**: Produce business-weighted risk scores by combining the technical exploitability from Stage 6 with the business impact from Stage 1. Deliver prioritized, actionable mitigations.

**Key Activities**:
- Calculate risk scores: Risk = Likelihood x Business Impact
- Rank all findings by business-weighted risk
- Propose mitigations for each finding, ordered by risk reduction per effort
- Identify quick wins (low effort, high risk reduction)
- Map findings to compliance requirements from Stage 1
- Produce executive summary and detailed technical findings

**Outputs**:
- Risk-ranked finding list with business impact justification
- Mitigation roadmap with effort estimates (quick win / short-term / long-term)
- Compliance gap report
- Executive summary suitable for non-technical stakeholders
- Residual risk assessment after proposed mitigations

**Questions to Ask**:
- Which findings, if exploited, would cause the greatest business harm?
- Which mitigations provide the highest risk reduction for the lowest effort?
- Are there findings that violate regulatory requirements and need immediate remediation?
- What residual risk remains after all proposed mitigations are applied?
- Are there systemic issues (e.g., no input validation framework) that, if fixed, would resolve multiple findings?

**How Claude Should Approach This Stage**:
Tie every finding back to Stage 1 business objectives. A critical SQL injection in an internal admin tool used by 3 people may rank lower than a medium-severity IDOR in a customer-facing API serving millions. Present findings in descending risk order with clear, actionable mitigation steps. Distinguish between findings that need immediate fixes and those that can go into a backlog.

---

## Cross-Framework Mappings

### PASTA Stages to OWASP Top 10

| PASTA Stage | OWASP Top 10 Categories Addressed |
|---|---|
| Stage 1: Business Objectives | A04 Insecure Design (requirements phase) |
| Stage 2: Technical Scope | A05 Security Misconfiguration, A10 SSRF |
| Stage 3: Application Decomposition | A01 Broken Access Control, A04 Insecure Design |
| Stage 4: Threat Analysis | A06 Vulnerable Components, A08 Software Integrity |
| Stage 5: Vulnerability Analysis | A01-A10 (all, depending on findings) |
| Stage 6: Attack Simulation | A03 Injection, A07 Auth Failures, A08 Software Integrity |
| Stage 7: Risk & Impact | A09 Logging & Monitoring Failures |

### PASTA Stages to STRIDE

| PASTA Stage | STRIDE Categories Most Relevant |
|---|---|
| Stage 1: Business Objectives | (sets context for all categories) |
| Stage 2: Technical Scope | Denial of Service, Information Disclosure |
| Stage 3: Application Decomposition | Spoofing, Elevation of Privilege |
| Stage 4: Threat Analysis | All STRIDE categories |
| Stage 5: Vulnerability Analysis | All STRIDE categories |
| Stage 6: Attack Simulation | Tampering, Elevation of Privilege, Spoofing |
| Stage 7: Risk & Impact | (prioritizes across all categories) |

### PASTA Stages to CWE

| PASTA Stage | Relevant CWE Classes |
|---|---|
| Stage 2: Technical Scope | CWE-16 (Configuration), CWE-311 (Missing Encryption) |
| Stage 3: Application Decomposition | CWE-284 (Improper Access Control), CWE-269 (Improper Privilege Management) |
| Stage 4: Threat Analysis | CWE-1035 (MITRE Top 25) |
| Stage 5: Vulnerability Analysis | All relevant CWE entries |
| Stage 6: Attack Simulation | CWE-829 (Untrusted Functionality), CWE-20 (Improper Input Validation) |

---

## When to Use PASTA vs STRIDE vs OWASP

| Criterion | PASTA | STRIDE | OWASP Top 10 |
|---|---|---|---|
| **Focus** | Business risk | Threat categorization | Common vulnerabilities |
| **Approach** | Sequential, 7-stage process | Per-element threat enumeration | Checklist-based |
| **Best for** | Risk-prioritized analysis | Systematic threat identification | Quick vulnerability audit |
| **Requires** | Business context | Data flow diagram | Code access |
| **Output** | Risk-ranked mitigation roadmap | Threat catalog per component | Finding list by category |
| **Effort** | High (most thorough) | Medium | Low |
| **When to choose** | Regulated systems, complex business logic, executive reporting | New system design, architecture review | Fast scan, compliance check |

---

## Compliance Mapping Template

```json
{
  "framework": "PASTA",
  "stage": 7,
  "finding_id": "PASTA-001",
  "business_objective": "Protect customer payment data",
  "threat_id": "T1190",
  "vulnerability_cwe": "CWE-89",
  "attack_chain": ["SQL injection in /api/search", "Extract session tokens", "Admin panel access"],
  "risk_score": 22,
  "business_impact": "critical",
  "exploitability": "high",
  "compliance_requirements": ["PCI-DSS 6.5.1", "OWASP A03:2021"],
  "mitigations": [
    {"action": "Parameterize all queries in SearchController", "effort": "low", "risk_reduction": "high"},
    {"action": "Implement WAF rules for SQL injection patterns", "effort": "medium", "risk_reduction": "medium"}
  ],
  "residual_risk": "low"
}
```
