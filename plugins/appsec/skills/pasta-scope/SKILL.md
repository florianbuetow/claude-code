---
name: pasta-scope
description: >
  This skill should be used when the user asks to "define technical scope",
  "map attack surface", "identify entry points", "build a data flow diagram",
  or is running PASTA stage 2. Also triggers when the user asks about DFDs,
  network boundaries, external dependencies, or deployment topology in a
  threat modeling context. Part of the PASTA threat modeling methodology
  (Stage 2 of 7).
---

# PASTA Stage 2: Define Technical Scope

Map the technical boundaries of the system -- architecture, protocols, entry
points, and attack surface. Build data flow diagrams (DFDs) showing how data
moves through the system and where trust boundaries exist.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 2 Behavior |
|------|------------------|
| `--scope` | Default `changed`. Scans routes, API specs, Dockerfiles, IaC, and network configs. |
| `--depth quick` | Entry points from route definitions and API specs only. |
| `--depth standard` | Full entry point scan + dependency catalog + protocol identification. |
| `--depth deep` | Standard + infrastructure analysis (Docker, K8s, Terraform) + network boundary mapping. |
| `--depth expert` | Deep + complete DFD with trust levels annotated on every data flow. |
| `--severity` | Not applicable at this stage. |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 2 section. PASTA is SEQUENTIAL.
Stage 2 consumes Stage 1 output and feeds Stage 3.

## Prerequisites

**Required**: Stage 1 output -- business-critical assets, compliance requirements,
and risk tolerance thresholds. If unavailable, warn and proceed with assumptions.

## Workflow

### Step 1: Determine Scope

Parse `--scope` flag (default: `changed`). Prioritize: route files, controllers,
API gateway configs, Dockerfiles, `docker-compose.yml`, K8s manifests, Terraform,
nginx configs, OpenAPI/Swagger specs, GraphQL schemas.

### Step 2: Enumerate Entry Points

Scan for all data ingress paths:
1. **HTTP/REST**: Express routes, FastAPI paths, Spring `@RequestMapping`, Django URLs.
2. **GraphQL**: Schemas, resolvers, mutations, subscriptions.
3. **WebSocket**: Socket.io handlers, WS endpoints.
4. **Message queues**: RabbitMQ, Kafka, SQS, Redis pub/sub consumers.
5. **File uploads**: Multipart handlers, S3 presigned URLs.
6. **Webhooks**: Incoming receivers from third-party services.
7. **CLI/Scheduled**: Admin consoles, cron tasks, Lambda triggers, workers.

### Step 3: Map External Dependencies

Catalog outbound connections: third-party APIs (payment, auth, email), databases,
caches (Redis, Memcached), cloud services (S3, SQS, Pub/Sub), and package
dependencies from manifest files.

### Step 4: Identify Network Boundaries

1. Internet-facing vs. internal services.
2. Network segmentation (VPCs, security groups, firewalls).
3. Container orchestration (Docker networks, K8s namespaces, service meshes).
4. CDN/proxy layers (Cloudflare, nginx, API gateways, load balancers).
5. Legacy/deprecated endpoints still reachable.

### Step 5: Build Data Flow Diagram

Construct a textual DFD: external entities, processes, data stores, data flows
with protocol labels, and trust boundary lines.

## Analysis Checklist

1. What are all the ways data enters and exits this system?
2. Which components are internet-facing vs. internal-only?
3. What third-party services does the application depend on?
4. What protocols and ports are exposed?
5. Are there deprecated endpoints still reachable?
6. What is the deployment topology (monolith, microservices, serverless)?
7. Are there admin or debug endpoints exposed in production?
8. What authentication mechanisms protect each entry point?

## Output Format

Stage 2 produces a **Technical Scope Document** with DFD. ID prefix: **PASTA** (e.g., `PASTA-S2-001`).

```
## PASTA Stage 2: Technical Scope

### Technology Stack
| Layer | Technology | Version |
|-------|-----------|---------|
| Language / Framework / Database / Cache / Deployment | ... | ... |

### Entry Points
| ID | Type | Path/Handler | Auth Required | Protocol |
|----|------|-------------|---------------|----------|
| EP-01 | REST API | POST /api/users | No | HTTPS |
| EP-02 | WebSocket | /ws/chat | Yes (JWT) | WSS |

### External Dependencies
| Service | Purpose | Data Exchanged | Protocol |
|---------|---------|---------------|----------|
| Stripe | Payments | Card tokens | HTTPS |

### Data Flow Diagram
User --> [API Gateway] --> [Auth] --> [App Server] --> [Database]
Trust Boundaries:
- Internet | DMZ: User to API Gateway
- DMZ | Internal: API Gateway to App Server
- App | Data: App Server to Database

### Attack Surface Summary
| Surface | Entry Points | Internet-Facing | Auth Required |
|---------|-------------|-----------------|---------------|
| REST API | N | Yes | Mixed |
```

Findings follow `../../shared/schemas/findings.md` with:
- `metadata.tool`: `"pasta-scope"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-2"`

## Next Stage

**Stage 3: Application Decomposition** (`pasta-decompose`). Pass entry points,
DFD, dependencies, and network boundaries. Stage 3 decomposes into components,
maps trust boundaries, and catalogs roles and permissions.
