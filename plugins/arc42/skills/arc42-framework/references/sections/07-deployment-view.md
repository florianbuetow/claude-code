# Section 7 — Deployment View

Source: 07-deployment-view/index.md

## Intent
Maps software artifacts onto the physical or virtual infrastructure that executes them, capturing environments, distribution topologies, and the reasoning behind infrastructure choices. This section becomes especially important when the system runs across multiple hosts, containers, or geographic locations — where the infrastructure itself shapes architectural decisions.

## Evidence tier
code-derivable

## What to look for in the repo
- Docker Compose files, Kubernetes manifests, Helm charts, or Terraform/Pulumi configurations
- CI/CD pipeline definitions naming deployment targets (dev, staging, production, regions)
- Infrastructure-as-code specifying compute, network, and storage resources
- Environment-specific configuration files (`.env.production`, `values-prod.yaml`, region config)
- Monitoring and logging endpoint configurations that reveal where services actually run

## Output template

### 7.1 Infrastructure Level 1

High-level topology showing where the system runs: environments, compute nodes, network zones, and how software components map onto those nodes.

*<insert infrastructure overview diagram>*

**Motivation:** *<why this topology was chosen — cost, latency, compliance, availability>*

**Quality / performance characteristics:** *<targets this layout is designed to meet>*

**Artifact-to-node mapping:**

| Software Component | Infrastructure Node | Notes |
|--------------------|---------------------|-|
|  |  |  |

### 7.2 Infrastructure Level 2

Zoomed-in view of individual infrastructure elements from Level 1 that warrant further detail (e.g., internal structure of a Kubernetes cluster, a VPC, or a CDN configuration).

#### 7.2.1 `<Infrastructure Element>`

*<diagram and explanation>*

#### 7.2.n `<Infrastructure Element>`

*<diagram and explanation>*

## Diagrams
- Mermaid `graph TB` for the Level 1 deployment topology
- UML deployment diagram notation for more complex nested infrastructure

## Lint (this section)
- T07-* (all runtime environments documented; artifact-to-node mapping present; Level 1 is consistent with §3.2 technical context)

## Depends on
- §3.2 (technical context defines the outer infrastructure boundary that this section zooms into)
- §5 (components assigned to nodes here must exist in the building block view)
