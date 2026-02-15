---
name: pasta-threats
description: >
  This skill should be used when the user asks to "analyze threats",
  "identify threat actors", "map attack vectors", "cross-reference MITRE ATT&CK",
  or is running PASTA stage 4. Also triggers when the user asks about adversary
  tactics, supply chain threats, or threat intelligence in a threat modeling
  context. Part of the PASTA threat modeling methodology (Stage 4 of 7).
---

# PASTA Stage 4: Threat Analysis

Identify threats using real-world intelligence, attack patterns, and adversary
tactics. Cross-reference with MITRE ATT&CK to ground analysis in actual attacker
behavior. Map threats to the components and trust boundaries from Stage 3.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 4 Behavior |
|------|------------------|
| `--scope` | Inherits from prior stages. Focuses on components and entry points from Stages 2-3. |
| `--depth quick` | Top 5 most likely threats based on technology stack only. |
| `--depth standard` | Full threat catalog with MITRE ATT&CK mappings for all components. |
| `--depth deep` | Standard + attack tree construction, supply chain analysis, insider threat modeling. |
| `--depth expert` | Deep + adversary persona simulation with detailed TTPs per actor profile. |
| `--severity` | Filter threats by estimated impact level. |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 4 section. PASTA is SEQUENTIAL.
Stage 4 consumes Stages 1-3 output and feeds Stage 5.

## Prerequisites

**Required**: Stage 3 output -- component inventory, role-permission matrix, data
classification, trust boundaries. Also needs: business-critical assets (Stage 1),
entry points and attack surface (Stage 2). If unavailable, warn and assume.

## Workflow

### Step 1: Profile Threat Actors

1. **Opportunistic external**: Automated scanners, credential stuffing. Targets known CVEs.
2. **Targeted external**: Researched attack on business logic, custom vulns.
3. **Malicious insider**: Legitimate access, targets escalation and exfiltration.
4. **Supply chain**: Compromised dependency or build pipeline.
5. **APT/nation-state**: Significant resources, targets IP and infrastructure.

### Step 2: Map MITRE ATT&CK Techniques

| Technique | Name | Relevance |
|-----------|------|-----------|
| T1190 | Exploit Public-Facing App | Internet-facing endpoints |
| T1059 | Command/Scripting Interpreter | Server-side execution paths |
| T1078 | Valid Accounts | Authentication mechanisms |
| T1098 | Account Manipulation | User/role management |
| T1134 | Access Token Manipulation | JWT/session handling |
| T1552 | Unsecured Credentials | Secrets in config files |
| T1210 | Exploit Remote Services | Service-to-service calls |
| T1195 | Supply Chain Compromise | Third-party dependencies |

### Step 3: Identify Attack Patterns

For each component: review stack-specific attack history, map patterns to entry
points, assess feasibility given controls, and identify cross-component chains.

### Step 4: Analyze Supply Chain

Check dependency manifests for count, known CVEs (via SCA tooling), undermaintained
packages, typosquatting risk, and CI/CD pipeline security.

### Step 5: Build Threat-to-Component Matrix

Map each threat to target component(s), exploited entry point(s), and endangered
business asset(s).

## Analysis Checklist

1. What MITRE ATT&CK techniques are most relevant to this stack?
2. What attacks are commonly seen against similar applications?
3. What would a motivated insider with legitimate access attempt?
4. Which dependencies have known CVEs or are poorly maintained?
5. What chains could pivot from low-privilege entry to high-value assets?
6. Are there public exploits for the framework versions in use?
7. Which threat actors are most likely to target this application type?
8. Are there seasonal or event-driven threat patterns relevant here?

## Output Format

Stage 4 produces a **Threat Catalog**. ID prefix: **PASTA** (e.g., `PASTA-S4-001`).

```
## PASTA Stage 4: Threat Analysis

### Threat Actor Profiles
| Actor | Motivation | Capability | Likely Targets | Likelihood |
|-------|-----------|-----------|---------------|------------|
| Opportunistic | Financial gain | Low-Med | Known CVEs, weak auth | High |
| Targeted | Data theft | Med-High | Business logic, APIs | Medium |
| Insider | Revenge/profit | High | Data exfil, backdoors | Low-Med |
| Supply chain | Broad compromise | Medium | Dependencies, CI/CD | Low |

### Threat Catalog
| ID | Threat | MITRE ATT&CK | Component | Asset | Likelihood |
|----|--------|-------------|-----------|-------|------------|
| T-01 | SQL injection via search | T1190 | C-02 API | User DB | High |
| T-02 | Credential stuffing | T1078 | C-01 Auth | Accounts | High |

### Attack Trees (--depth deep+)
Goal: Access customer payment data
  OR
  +-- Exploit SQL injection -> extract tokens -> impersonate admin
  +-- Credential stuff admin login -> access /admin/export
  +-- Compromise npm dependency -> backdoor payment module

### Supply Chain Assessment
| Dependency | Risk | CVEs Known | Maintainer Status |
|-----------|------|-----------|------------------|
```

Findings follow `../../shared/schemas/findings.md` with:
- `references.mitre_attck`: Technique ID (e.g., `"T1190"`)
- `metadata.tool`: `"pasta-threats"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-4"`

## Next Stage

**Stage 5: Vulnerability Analysis** (`pasta-vulns`). Pass the Threat Catalog and
MITRE ATT&CK mappings. Stage 5 analyzes code for specific vulnerabilities that
enable the threats identified here.
