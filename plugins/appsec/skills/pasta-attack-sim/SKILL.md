---
name: pasta-attack-sim
description: >
  This skill should be used when the user asks to "simulate attacks",
  "build attack trees", "model exploit chains", "score exploitability", or is
  running PASTA stage 6. Also triggers when the user asks about attack scenarios,
  red team simulation, DREAD scoring, or detection gap analysis in a threat
  modeling context. Part of the PASTA threat modeling methodology (Stage 6 of 7).
---

# PASTA Stage 6: Attack Simulation

Simulate realistic exploit chains by combining Stage 4 threats with Stage 5
vulnerabilities. Score each scenario by exploitability and impact, and assess
whether existing controls detect or prevent each chain.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 6 Behavior |
|------|------------------|
| `--scope` | Inherits from prior stages. Uses vulnerability inventory and threat catalog, not raw source. |
| `--depth quick` | Top 3 most critical exploit chains only, basic scoring. |
| `--depth standard` | Full attack trees for all high/critical pairs, DREAD scoring. |
| `--depth deep` | Standard + detection gap analysis, control bypass assessment, multi-stage pivots. |
| `--depth expert` | Deep + red team persona simulation with step-by-step exploit narratives. |
| `--severity` | Filter to attack scenarios above the specified impact level. |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 6 section. PASTA is SEQUENTIAL.
Stage 6 consumes Stages 1-5 output and feeds Stage 7.

## Prerequisites

**Required**: Stage 5 output -- vulnerability inventory with CWE mappings and
vulnerability-threat correlations. Also needs: business assets (Stage 1), entry
points (Stage 2), components and trust boundaries (Stage 3), threat catalog
(Stage 4). If unavailable, warn and assume.

## Workflow

### Step 1: Identify Attack Pairs

Combine threats with vulnerabilities. Prioritize pairs targeting business-critical
assets. Discard pairs fully mitigated by existing controls.

### Step 2: Construct Exploit Chains

For each high-priority pair, build multi-step scenarios covering: entry point,
exploitation, lateral movement, privilege escalation, objective reached, and
exfiltration/impact. Construct attack trees showing alternate paths:

```
Goal: [Business-critical asset]
  OR
  +-- Path A: [Entry point] -> [Vuln-1] -> [Pivot] -> [Target]
  +-- Path B: [Entry point] -> [Vuln-2] -> [Escalation] -> [Target]
```

### Step 3: Score Exploitability (DREAD)

| Factor | Criteria |
|--------|----------|
| **Damage** | 10 = full compromise, 1 = minor info leak |
| **Reproducibility** | 10 = every time, 1 = race condition |
| **Exploitability** | 10 = script kiddie, 1 = nation-state |
| **Affected Users** | 10 = all users, 1 = single user |
| **Discoverability** | 10 = publicly known, 1 = insider knowledge |

DREAD Score = Average of all five factors (0-10).

### Step 4: Assess Detection Gaps

For each chain: is exploitation logged? Would alerts fire? Would WAF/IDS block
it? Is rate limiting effective? Would post-exploitation behavior be detected?

### Step 5: Identify Control Bypasses

For each security control: can it be bypassed via alternative paths? Does it
cover all entry points? Are there timing windows? Can the attacker degrade it?

### Step 6: Rank Attack Scenarios

Order by: DREAD score, business impact, attack complexity (simpler = higher),
detection coverage (undetectable = higher).

## Analysis Checklist

1. Can low-severity vulns chain into high-impact exploits?
2. What is the shortest path from internet to most sensitive data?
3. Would current logging detect this attack in progress?
4. What skill level and tooling is required per path?
5. Are there paths that bypass all existing controls?
6. Can a single compromised credential yield full system access?
7. Are there TOCTOU windows exploitable in chains?
8. What is the blast radius of the most likely attack?

## Output Format

Stage 6 produces **Attack Scenarios with Exploit Chains**. ID prefix: **PASTA** (e.g., `PASTA-ATK-001`).

```
## PASTA Stage 6: Attack Simulation

### ATK-001: [Scenario Name]
**Target**: [Asset] | **Actor**: [Profile] | **DREAD**: X.X
**Chain**: Entry point -> Vuln exploited -> Access gained -> Pivot -> Objective
| Damage | Reproducibility | Exploitability | Affected Users | Discoverability | Score |
|--------|----------------|---------------|---------------|----------------|-------|
| X | X | X | X | X | X.X |
**Detection**: Logging [Y/N], Alerting [Y/N], WAF [Y/N]
**Gaps**: [Missing controls]

### Attack Scenario Summary
| ID | Scenario | DREAD | Target Asset | Complexity | Detected |
|----|----------|-------|-------------|------------|----------|
| ATK-001 | ... | X.X | ... | Low/Med/High | Yes/No |

### Detection Gap Summary
| Gap | Scenarios Affected | Recommendation |
|-----|-------------------|----------------|
```

Findings follow `../../shared/schemas/findings.md` with:
- `dread`: Full DREAD scoring object
- `references.mitre_attck`: technique IDs, `references.cwe`: exploited CWE IDs
- `metadata.tool`: `"pasta-attack-sim"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-6"`

## Next Stage

**Stage 7: Risk & Impact Analysis** (`pasta-risk`). Pass attack scenarios, DREAD
scores, and detection gaps. Stage 7 combines technical exploitability with Stage 1
business impact to produce risk-weighted scores and a remediation roadmap.
