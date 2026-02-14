---
name: pasta-objectives
description: >
  This skill should be used when the user asks to "define business objectives",
  "identify business-critical assets", "determine risk appetite", or is running
  PASTA stage 1. Also triggers when the user asks about compliance requirements,
  acceptable risk thresholds, or business impact analysis in a threat modeling
  context. Part of the PASTA threat modeling methodology (Stage 1 of 7).
---

# PASTA Stage 1: Define Business Objectives

Establish what the application protects, why it matters, and what business impact
a compromise would have. This stage anchors the entire PASTA threat model to real
business value so that subsequent stages prioritize by actual organizational impact.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 1 Behavior |
|------|------------------|
| `--scope` | Default `changed`. Scans configs, docs, schemas, and API contracts to infer business purpose. |
| `--depth quick` | Business purpose from project metadata only. |
| `--depth standard` | Full analysis of configs, schemas, and code to infer objectives, compliance, and risk thresholds. |
| `--depth deep` | Standard + trace payment flows, PII handling, and regulatory indicators across the codebase. |
| `--depth expert` | Deep + formal risk tolerance matrix with quantified impact categories. |
| `--severity` | Not applicable at this stage (no vulnerability findings produced). |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 1 section. PASTA is SEQUENTIAL.
Stage 1 output feeds Stage 2. Do not skip this stage.

## Prerequisites

None. This is the first stage. The analyst needs access to the application source
code, configuration files, and any available documentation.

## Workflow

### Step 1: Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Prioritize: `README`, `package.json`, `pom.xml`, `.env.example`, database
   migrations, API routes, OpenAPI specs, Terraform/CloudFormation, `docs/`.

### Step 2: Identify Business Purpose

1. **Core function**: What does this application do? (e-commerce, SaaS, API, etc.)
2. **Users**: Who uses it? Customers, employees, partners, public?
3. **Data handled**: PII, financial, health, credentials, intellectual property?
4. **Revenue impact**: Directly revenue-generating or supporting?

### Step 3: Identify Compliance Requirements

Scan for indicators: PCI-DSS (payment processing, Stripe), HIPAA (health data,
FHIR), GDPR/CCPA (EU data, consent, deletion endpoints), SOX (audit trails),
SOC 2 (multi-tenant SaaS, data isolation).

### Step 4: Define Risk Appetite

1. **Acceptable downtime**: SLA requirements.
2. **Data sensitivity**: Classify as public, internal, confidential, restricted.
3. **Blast radius**: Systems and users affected if compromised.
4. **Recovery cost**: Data loss vs. data exposure trade-offs.

### Step 5: Document Business Context

Produce the Stage 1 output document that feeds Stage 2.

## Analysis Checklist

1. What is the worst business outcome if this application is fully compromised?
2. What data, if exposed, would trigger regulatory notification requirements?
3. What is the acceptable downtime for this service?
4. Which business processes depend on this application's integrity?
5. Who are the stakeholders impacted by a breach?
6. Does the application handle payments, PII, health data, or other regulated data?
7. Is this application internet-facing, internal, or both?
8. What is the risk appetite -- startup-aggressive or enterprise-conservative?

## Output Format

Stage 1 produces a **Business Context Document**. ID prefix: **PASTA** (e.g., `PASTA-S1-001`).

```
## PASTA Stage 1: Business Objectives

### Application Purpose
[1-2 sentence summary of what the application does and why it matters]

### Business-Critical Assets
| Asset | Type | Sensitivity | Impact if Compromised |
|-------|------|-------------|----------------------|
| ... | Data / Process / System | Public / Internal / Confidential / Restricted | ... |

### Compliance Requirements
| Regulation | Applicable | Evidence | Key Requirements |
|-----------|-----------|----------|-----------------|
| PCI-DSS | Yes/No/Unknown | [files/patterns] | [controls] |
| HIPAA / GDPR / SOX | ... | ... | ... |

### Risk Tolerance
| Category | Tolerance | Justification |
|----------|-----------|---------------|
| Downtime | [hours/minutes] | [SLA evidence] |
| Data exposure | [severity] | [data classification] |
| Financial loss | [threshold] | [revenue model] |

### Assumptions
[List assumptions made when business context was ambiguous]
```

Findings follow `../../shared/schemas/findings.md` with:
- `metadata.tool`: `"pasta-objectives"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-1"`

## Next Stage

**Stage 2: Define Technical Scope** (`pasta-scope`). Pass the Business Context
Document. Stage 2 maps the attack surface and builds DFDs focused on the assets
and processes identified here.
