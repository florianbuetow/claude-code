---
name: pasta-vulns
description: >
  This skill should be used when the user asks to "analyze vulnerabilities",
  "find security weaknesses", "map CWEs", "run vulnerability analysis", or is
  running PASTA stage 5. Also triggers when the user asks about SAST, DAST,
  dependency scanning, or CWE mapping in a threat modeling context. Part of the
  PASTA threat modeling methodology (Stage 5 of 7).
---

# PASTA Stage 5: Vulnerability Analysis

Identify specific weaknesses in code and configuration that could be exploited by
Stage 4 threats. This is the core code analysis stage of PASTA. Map each finding
to CWE identifiers and correlate with the threat catalog.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 5 Behavior |
|------|------------------|
| `--scope` | Default `changed`. Analyzes source code, configs, and infrastructure files. |
| `--depth quick` | Scanners + grep patterns only, no manual code review. |
| `--depth standard` | Full code read, local data-flow analysis, CWE mapping. |
| `--depth deep` | Standard + cross-file taint analysis, entry-to-sink tracing, dependency CVE scan. |
| `--depth expert` | Deep + exploitability scoring, proof-of-concept path assessment. |
| `--severity` | Filter output by severity. |
| `--fix` | Generate fix suggestions for each vulnerability found. |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 5 section. PASTA is SEQUENTIAL.
Stage 5 consumes Stages 1-4 output and feeds Stage 6.

## Prerequisites

**Required**: Stage 4 output -- threat catalog with MITRE ATT&CK mappings and
threat-to-component mapping. Also needs: entry points (Stage 2), components and
trust boundaries (Stage 3), business-critical assets (Stage 1). If unavailable,
warn and assume.

## Workflow

### Step 1: Determine Scope

Parse `--scope` flag (default: `changed`). Filter to code and config file types.
Prioritize files in components targeted by Stage 4 threats.

### Step 2: Check for Scanners

| Scanner | Detect | Coverage |
|---------|--------|----------|
| semgrep | `which semgrep` | Injection, auth, crypto, SSRF, XSS |
| bandit | `which bandit` | Python: injection, crypto, subprocess |
| gosec | `which gosec` | Go: injection, crypto, file handling |
| brakeman | `which brakeman` | Rails: injection, XSS, mass assignment |
| npm audit | `which npm` | Node.js dependency vulnerabilities |
| trivy | `which trivy` | Container and dependency vulnerabilities |
| gitleaks | `which gitleaks` | Secrets and credentials in code |

### Step 3: Run Scanners

Run available scanners, normalize output to `../../shared/schemas/findings.md`.

### Step 4: Manual Code Analysis

1. **Trace data flows**: User input from entry points through components to sinks.
2. **Check sanitization**: Validation, encoding, parameterization between source and sink.
3. **Review auth/authz**: Authentication enforcement and authorization consistency.
4. **Check crypto**: Secure algorithms, key management, TLS enforcement.
5. **Review configs**: Default credentials, debug modes, security headers.
6. **Check secrets**: Hardcoded credentials, API keys, tokens in source.

### Step 5: Correlate with Threats

Map each vulnerability to Stage 4 threat(s) it enables: which actor exploits it,
which ATT&CK technique it supports, which business asset it endangers.

### Step 6: Assess Exploitability

Evaluate: attack complexity, prerequisite access, mitigating controls, and
chaining potential with other vulnerabilities.

## Analysis Checklist

1. Are parameterized queries used everywhere, or are there dynamic query paths?
2. Are there deserialization points accepting untrusted input?
3. Do all endpoints enforce authentication and authorization?
4. Are secrets hardcoded or in configuration files within the repository?
5. Are input validation and output encoding applied consistently?
6. Are cryptographic algorithms and key lengths secure and current?
7. Are dependencies up to date with no known CVEs?
8. Are security headers configured (CSP, HSTS, X-Frame-Options)?

## Output Format

Stage 5 produces a **Vulnerability Inventory with CWE Mappings**. ID prefix: **PASTA** (e.g., `PASTA-001`).

Each finding includes: id, title, severity, location (file, line, function, snippet),
description, impact, fix, and references (CWE, MITRE ATT&CK, OWASP).

```
## PASTA Stage 5: Vulnerability Analysis

### Vulnerability Inventory
| ID | Vulnerability | CWE | Severity | Component | Enables Threat |
|----|--------------|-----|----------|-----------|---------------|
| PASTA-001 | SQL injection in search | CWE-89 | Critical | C-02 API | T-01 |
| PASTA-002 | Missing auth on export | CWE-862 | High | C-04 Admin | T-03 |

### Vulnerability-Threat Correlation
| Vulnerability | Threats Enabled | Complexity | Existing Controls |
|--------------|----------------|------------|-------------------|
| PASTA-001 | T-01, T-05 | Low | None |

### Scanner Coverage
| Scanner | Status | Findings |
|---------|--------|----------|
| semgrep | Available / Not found | N findings |
```

Findings follow `../../shared/schemas/findings.md` with:
- `references.cwe`: CWE identifier, `references.mitre_attck`: linked technique, `references.owasp`: OWASP category
- `metadata.tool`: `"pasta-vulns"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-5"`

## Next Stage

**Stage 6: Attack Simulation** (`pasta-attack-sim`). Pass the Vulnerability
Inventory and threat correlations. Stage 6 constructs exploit chains and scores
each attack scenario by exploitability and impact.
