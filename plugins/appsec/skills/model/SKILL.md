---
name: model
description: >
  This skill should be used when the user asks to "create threat model",
  "threat model architecture", "map security architecture", "build threat
  model", "STRIDE analysis", "data flow diagram", "DFD security", or
  "attack tree analysis". Also triggers when the user wants a systematic
  identification of threats against the application architecture, trust
  boundaries, data flows, or component interactions.
---

# Threat Modeling

Full architecture-level threat modeling with automated discovery, data flow
mapping, STRIDE-per-component analysis, and attack tree generation. Produces
persistent, incremental threat models stored in `.appsec/model/` that evolve
as the codebase changes.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Model Behavior |
|------|---------------|
| `--scope` | Default `full`. Threat models benefit from whole-system visibility. Narrow scopes produce partial models with a warning. |
| `--depth quick` | Component inventory and trust boundary identification only. |
| `--depth standard` | Full threat model: components, data flows, STRIDE analysis, mitigations. |
| `--depth deep` | Standard + attack trees, cross-component threat chains, external dependency threats. |
| `--depth expert` | Deep + DREAD scoring, attack simulation narratives, compliance mapping. |
| `--severity` | Filter reported threats by severity in output. |
| `--format` | Default `md`. Use `json` for structured model data. |
| `--diff` | Incremental mode: only analyze changes since last model. Compare against `.appsec/model/current.json`. |

## Workflow

### Step 1: Discovery

Automatically discover the application architecture by analyzing the codebase:

#### Component Discovery

Identify all significant components:

1. **Services**: Separate processes, microservices (from docker-compose, k8s manifests, service configs).
2. **APIs**: REST controllers, GraphQL resolvers, gRPC services.
3. **Data stores**: Databases, caches, file storage, message queues.
4. **External dependencies**: Third-party APIs, SaaS integrations, CDNs, auth providers.
5. **Background workers**: Job processors, cron tasks, event consumers.
6. **Client applications**: Web frontends, mobile apps, CLI tools.
7. **Infrastructure**: Load balancers, reverse proxies, API gateways (from config files).

#### Trust Boundary Discovery

Identify boundaries where trust levels change:

1. **Network boundaries**: Internet to DMZ, DMZ to internal, internal to database tier.
2. **Authentication boundaries**: Public vs authenticated, user vs admin.
3. **Process boundaries**: Between services, between containers.
4. **Data classification boundaries**: Where PII/secrets move between storage/transit.

### Step 2: Data Flow Mapping

Generate Mermaid data flow diagrams (DFDs) at two levels:

Generate Mermaid DFDs at two levels: Level 0 (system context -- actors, application, external systems) and Level 1 (component detail with trust boundary subgraphs showing internal services, data stores, and message queues).

Annotate each data flow with:
- Protocol (HTTPS, gRPC, TCP, etc.)
- Authentication method
- Data classification (public, internal, confidential, restricted)
- Encryption status (in transit, at rest)

### Step 3: STRIDE-per-Component Analysis

Apply STRIDE to each component and data flow:

| STRIDE | Question |
|--------|----------|
| **S**poofing | Can an attacker impersonate this component or a user of it? |
| **T**ampering | Can data in transit or at rest be modified without detection? |
| **R**epudiation | Can actions be performed without an audit trail? |
| **I**nformation Disclosure | Can sensitive data leak from this component? |
| **D**enial of Service | Can this component be made unavailable? |
| **E**levation of Privilege | Can an attacker gain higher access through this component? |

For each component, generate a threat table:

For each component, produce a table with columns: #, STRIDE category, Threat description, Severity, Mitigation, Status (Mitigated/Partial/Gap/Accepted).

### Step 4: Attack Tree Generation

At `--depth deep` and above, generate attack trees for high-value targets:

For each high-value target (e.g., "Exfiltrate User PII"), produce a numbered attack tree with branches for direct access, application-layer attacks, and infrastructure attacks. Each leaf node references severity and mitigation status from the STRIDE analysis.

### Step 5: Identify Mitigations and Gaps

For each threat identified:

1. **Check if mitigated**: Search the codebase for security controls that address the threat.
2. **Assess mitigation quality**: Is the control properly implemented? Complete? Tested?
3. **Mark status**:
   - `Mitigated`: Security control exists and is properly implemented.
   - `Partial`: Control exists but is incomplete or has known weaknesses.
   - `Gap`: No mitigation found. This becomes a finding.
   - `Accepted`: Risk acknowledged and accepted (noted in threat model).

### Step 6: Incremental Mode (--diff)

When `--diff` flag is set:

1. Load the previous model from `.appsec/model/current.json`.
2. Detect changes:
   - New components added.
   - Components removed.
   - Data flows added or changed.
   - Trust boundaries modified.
3. Run STRIDE analysis only on new/changed components and flows.
4. Merge results into the existing model.
5. Highlight what changed in the output.

Output a changelog showing NEW, CHANGED, and REMOVED components with threat counts for each.

### Step 7: Persist Model

Save the threat model to `.appsec/model/`:

| File | Contents |
|------|----------|
| `current.json` | Full structured model (components, flows, threats, mitigations) |
| `threat-model.md` | Human-readable report with Mermaid diagrams |
| `dfd-level0.mmd` | Level 0 Mermaid DFD source |
| `dfd-level1.mmd` | Level 1 Mermaid DFD source |
| `attack-trees.md` | Attack tree documentation |
| `history/<timestamp>.json` | Snapshot for diffing (incremental mode) |

### Step 8: Emit Findings for Gaps

For each threat with status `Gap`, emit a finding using `../../shared/schemas/findings.md`:

- Map STRIDE category to the appropriate `references.stride` value.
- Severity based on threat analysis (impact and likelihood).
- Location points to the component/file most relevant to the gap.

## Output Format

Findings follow `../../shared/schemas/findings.md`.

Finding ID prefix: **TM** (e.g., `TM-001`).

- `metadata.tool`: `"model"`
- `metadata.framework`: `"stride"` (or specific framework if used)
- `references.stride`: The STRIDE category letter

## Pragmatism Notes

- Threat models are living documents. Encourage incremental updates (`--diff`) rather than full rebuilds.
- Not every theoretical threat warrants a finding. Focus on threats that are plausible given the application's deployment context.
- A microservice behind a service mesh has different threats than an internet-facing monolith. Adjust analysis accordingly.
- Component discovery is heuristic. Label the model as based on code analysis, not authoritative architecture documentation.
- DFDs should be useful, not exhaustive. Omit trivial flows (e.g., logging to stdout) unless they carry sensitive data.
- If the codebase is a library (not a deployed application), model threats to consumers of the library rather than infrastructure threats.
- STRIDE is the default framework. If the user requests PASTA, LINDDUN, or another framework, defer to those specialized skills.
