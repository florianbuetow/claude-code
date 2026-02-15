---
name: pasta-risk
description: >
  This skill should be used when the user asks to "calculate risk scores",
  "prioritize mitigations", "generate remediation roadmap", "analyze business
  impact", or is running PASTA stage 7. Also triggers when the user asks about
  risk-weighted findings, compliance gap analysis, or executive security summary
  in a threat modeling context. Part of the PASTA threat modeling methodology
  (Stage 7 of 7).
---

# PASTA Stage 7: Risk & Impact Analysis

Produce business-weighted risk scores by combining Stage 6 exploitability with
Stage 1 business impact. Deliver a prioritized remediation roadmap balancing risk
reduction against effort. This is the final PASTA stage.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 7 Behavior |
|------|------------------|
| `--scope` | Inherits from prior stages. Synthesizes all prior outputs. |
| `--depth quick` | Top 5 risk-ranked findings with one-line mitigations only. |
| `--depth standard` | Full risk scoring, mitigation roadmap, and compliance mapping. |
| `--depth deep` | Standard + residual risk assessment, systemic issues, cost-benefit per mitigation. |
| `--depth expert` | Deep + executive summary, quantified risk, formal compliance gap report. |
| `--severity` | Filter final output to findings at or above the threshold. |
| `--format md` | Standalone markdown report for stakeholder distribution. |
| `--fix` | Chain into fix mode for highest-priority findings. |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 7 section. PASTA is SEQUENTIAL.
Stage 7 consumes all prior stage outputs to produce the final deliverable.

## Prerequisites

**Required**: Stage 6 output -- attack scenarios, DREAD scores, detection gaps.
Also needs: business assets and compliance (Stage 1), entry points (Stage 2),
components (Stage 3), threats (Stage 4), vulnerabilities (Stage 5). If
unavailable, warn and assume.

## Workflow

### Step 1: Calculate Business-Weighted Risk

Risk Score = Exploitability (DREAD, 1-10) x Business Impact (1-10).

| Impact Level | Score | Criteria |
|-------------|-------|----------|
| Critical | 9-10 | Regulatory breach, massive financial loss, existential threat |
| High | 7-8 | Significant data breach, major outage, legal liability |
| Medium | 4-6 | Limited exposure, partial degradation, reputational harm |
| Low | 1-3 | Minor disclosure, negligible business effect |

### Step 2: Rank Findings

Order by composite risk score (descending). Break ties by: compliance implications,
attack complexity (simpler ranks higher), detection coverage (undetectable ranks higher).

### Step 3: Propose Mitigations

| Effort | Definition | Timeline |
|--------|-----------|----------|
| **Quick win** | Single file change, config update, dependency bump | Same day |
| **Short-term** | Targeted code changes, new middleware or control | 1-2 sprints |
| **Long-term** | Architectural change, new service, framework migration | Quarterly |

Prioritize by risk-reduction-per-effort. Identify mitigations resolving multiple findings.

### Step 4: Map to Compliance

Cross-reference with Stage 1 compliance requirements: which findings violate
regulatory controls, which would be flagged in audit, mandated timelines,
documentation needed.

### Step 5: Assess Residual Risk

After proposed mitigations: what risk remains, what needs formal acceptance,
what compensating controls exist, what monitoring is needed.

### Step 6: Executive Summary

Non-technical summary: overall posture, top 3 immediate actions, phased effort
estimate, compliance status and regulatory exposure.

## Analysis Checklist

1. Which findings, if exploited, would cause the greatest business harm?
2. Which mitigations give the highest risk reduction for lowest effort?
3. Are there findings violating regulatory requirements needing immediate remediation?
4. What residual risk remains after all proposed mitigations?
5. Are there systemic issues that, if fixed, resolve multiple findings?
6. What is the total estimated effort for all recommended mitigations?
7. Should any findings be formally accepted rather than fixed?
8. What ongoing monitoring is needed after remediation?

## Output Format

Stage 7 produces the **Final PASTA Report**. ID prefix: **PASTA** (e.g., `PASTA-001`).

```
## PASTA Stage 7: Risk & Impact Analysis

### Executive Summary
**Risk Posture**: [Critical / High / Moderate / Low]
[2-3 sentence summary]
**Immediate Actions**: [N] | **Total Findings**: [N] (X critical, Y high, Z medium)
**Effort**: [quick wins: N, short-term: N, long-term: N]

### Risk-Ranked Findings
| Rank | ID | Finding | Risk Score | Exploitability | Business Impact | Effort |
|------|-------|---------|-----------|---------------|----------------|--------|
| 1 | PASTA-001 | SQL injection in search | 81 | 9.0 | 9 (breach) | Quick win |

### Remediation Roadmap
#### Quick Wins (Immediate)
| Finding | Mitigation | Risk Reduction | Effort |
|---------|-----------|---------------|--------|

#### Short-Term (1-2 Sprints)
| Finding | Mitigation | Risk Reduction | Effort |
|---------|-----------|---------------|--------|

#### Long-Term (Quarterly)
| Finding | Mitigation | Risk Reduction | Effort |
|---------|-----------|---------------|--------|

### Compliance Gaps
| Regulation | Requirement | Finding | Status | Deadline |
|-----------|------------|---------|--------|----------|

### Residual Risk
| Risk | After Mitigation | Compensating Controls | Accepted |
|------|-----------------|----------------------|----------|
```

Findings follow `../../shared/schemas/findings.md` with:
- `dread`: DREAD scoring from Stage 6
- `references.cwe`: from Stage 5, `references.owasp`: OWASP mapping, `references.mitre_attck`: from Stage 4
- `metadata.tool`: `"pasta-risk"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-7"`

## Completion

This is the final PASTA stage. The output is the complete threat model deliverable:
actionable, prioritized, and tied to business value. Track remediation progress
and schedule periodic reassessment as the application evolves.
