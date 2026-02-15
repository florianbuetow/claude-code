# appsec

Comprehensive application security toolbox for Claude Code.

62 skills across 8 security frameworks, 6 red team attacker personas, 18 detection pattern references, and interactive security education.

## Installation

```bash
claude plugin marketplace add florianbuetow/claude-code
claude plugin install appsec
```

<details>
<summary>Manual / Development Installation</summary>

```bash
git clone https://github.com/florianbuetow/claude-code.git
cd claude-code
claude --plugin-dir ./plugins/appsec
```

</details>

## What's Included

### Security Frameworks (8)

| Framework | Skills | What It Covers |
|-----------|--------|----------------|
| OWASP Top 10 (2021) | 10 individual + dispatcher | Web application vulnerabilities (A01–A10) |
| STRIDE | 6 individual + dispatcher | Threat categories: Spoofing, Tampering, Repudiation, Info Disclosure, DoS, Privilege Escalation |
| PASTA | 7 individual + dispatcher | 7-stage threat modeling methodology (sequential) |
| LINDDUN | 7 individual + dispatcher | Privacy threats: Linking, Identifying, Non-repudiation, Detecting, Data Disclosure, Unawareness, Non-compliance |
| MITRE ATT&CK | mapping skill | Maps findings to adversary tactics and techniques |
| SANS/CWE Top 25 | mapping skill | Top 25 most dangerous software weaknesses |
| OWASP API Top 10 | `/appsec:api` | API-specific security risks |
| DREAD | scoring model | Risk scoring across all findings (Damage, Reproducibility, Exploitability, Affected Users, Discoverability) |

### Red Team Agents (7)

Six attacker personas simulate real-world adversaries at `--depth expert`:

| Agent | Persona | Focus |
|-------|---------|-------|
| script-kiddie | Low-skill opportunist | Known CVEs, default credentials, exposed admin panels |
| hacktivist | Ideological attacker | Data leaks, defacement, DDoS vectors |
| insider | Malicious authenticated user | Privilege escalation, data exfiltration, audit log evasion |
| organized-crime | Professional criminal | Payment data, PII harvesting, ransomware entry points |
| supply-chain | Dependency compromiser | Build pipeline, lockfile manipulation, typosquatting |
| nation-state | Advanced persistent threat | Multi-step attack chains, persistence mechanisms, stealth |
| **consolidator** | — | Merges, deduplicates, and ranks findings from all agents |

### Skills by Category (62 total)

**Orchestration & Core** — `/appsec:start`, `/appsec:run`, `/appsec:status`, `/appsec:config`, `/appsec:secrets`, `/appsec:review-plan`

**Framework Dispatchers** — `/appsec:owasp`, `/appsec:stride`, `/appsec:pasta`, `/appsec:linddun`, `/appsec:sans25`, `/appsec:mitre`

**OWASP Top 10 Individual** — `/appsec:access-control` (A01), `/appsec:crypto` (A02), `/appsec:injection` (A03), `/appsec:insecure-design` (A04), `/appsec:misconfig` (A05), `/appsec:outdated-deps` (A06), `/appsec:auth` (A07), `/appsec:integrity` (A08), `/appsec:logging` (A09), `/appsec:ssrf` (A10)

**STRIDE Individual** — `/appsec:spoofing`, `/appsec:tampering`, `/appsec:repudiation`, `/appsec:info-disclosure`, `/appsec:dos`, `/appsec:privilege-escalation`

**PASTA Individual** — `/appsec:pasta-objectives` (Stage 1), `/appsec:pasta-scope` (Stage 2), `/appsec:pasta-decompose` (Stage 3), `/appsec:pasta-threats` (Stage 4), `/appsec:pasta-vulns` (Stage 5), `/appsec:pasta-attack-sim` (Stage 6), `/appsec:pasta-risk` (Stage 7)

**LINDDUN Individual** — `/appsec:linking`, `/appsec:identifying`, `/appsec:non-repudiation-privacy`, `/appsec:detecting`, `/appsec:data-disclosure`, `/appsec:unawareness`, `/appsec:non-compliance`

**Specialized** — `/appsec:race-conditions`, `/appsec:file-upload`, `/appsec:graphql`, `/appsec:websocket`, `/appsec:serverless`, `/appsec:api`, `/appsec:business-logic`, `/appsec:fuzz`, `/appsec:model`, `/appsec:attack-surface`, `/appsec:data-flows`, `/appsec:regression`

**Guide & Remediation** — `/appsec:fix`, `/appsec:harden`, `/appsec:verify`, `/appsec:report`, `/appsec:full-audit`

**Education** — `/appsec:explain`, `/appsec:learn`, `/appsec:glossary`

## Quick Start

```
/appsec:start              # Assess your codebase and get recommendations
/appsec:run                # Smart orchestrator — picks the right tools for you
/appsec:owasp              # Run all OWASP Top 10 checks
/appsec:stride             # Run full STRIDE threat analysis
/appsec:full-audit         # Exhaustive audit with dated report
```

### Common Flags

All skills support:

```
--scope changed|staged|branch|file:<path>|path:<dir>|module:<name>|plan|full
--severity critical|high|medium|low
--depth quick|standard|deep|expert
--format text|json|sarif|md
--fix          Generate code fixes
--quiet        Minimal output
--explain      Add educational context
```

### Depth Modes

| Mode | What Happens |
|------|-------------|
| `quick` | Fast scan, scanner-only where available |
| `standard` | Scanner + Claude analysis (default) |
| `deep` | Thorough multi-framework analysis |
| `expert` | Everything above + red team agent simulation with DREAD scoring |

## Hooks

The plugin includes a `PostToolUse` hook that automatically triggers a security review when you approve a plan (`ExitPlanMode`) and checks for hardcoded secrets when files are written or edited.

## Scanner Integration

Skills automatically detect and use installed scanners when available, falling back to Claude analysis when not. Supported scanners include semgrep, bandit, gitleaks, trufflehog, trivy, npm audit, and more. Run `/appsec:status` to see which scanners are detected in your environment.

## License

[MIT](LICENSE)
