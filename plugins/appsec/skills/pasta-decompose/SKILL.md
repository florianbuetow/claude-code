---
name: pasta-decompose
description: >
  This skill should be used when the user asks to "decompose the application",
  "map trust boundaries", "identify components and roles", "catalog permissions",
  or is running PASTA stage 3. Also triggers when the user asks about role-based
  access control mapping, data classification, or service-to-service trust in a
  threat modeling context. Part of the PASTA threat modeling methodology
  (Stage 3 of 7).
---

# PASTA Stage 3: Application Decomposition

Break the application into its constituent components and analyze trust boundaries,
user roles, privilege levels, and data sensitivity at each layer. This produces
the component map that Stages 4-7 use to identify where threats and attacks focus.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. Key behaviors:

| Flag | Stage 3 Behavior |
|------|------------------|
| `--scope` | Default `changed`. Scans middleware, auth modules, role definitions, permission configs, database schemas. |
| `--depth quick` | Component inventory from project structure and imports only. |
| `--depth standard` | Full decomposition + role-permission matrix + data classification. |
| `--depth deep` | Standard + cross-component data flows, inter-service auth, shared resource access patterns. |
| `--depth expert` | Deep + formal trust boundary analysis with privilege escalation path mapping. |
| `--severity` | Not applicable at this stage. |

## Framework Context

Read `../../shared/frameworks/pasta.md`, Stage 3 section. PASTA is SEQUENTIAL.
Stage 3 consumes Stage 2 output and feeds Stage 4.

## Prerequisites

**Required**: Stage 2 output -- entry point inventory, DFD, technology stack, and
external dependencies. If unavailable, warn and proceed with assumptions.

## Workflow

### Step 1: Determine Scope

Parse `--scope` flag (default: `changed`). Prioritize: middleware, auth modules,
role/permission definitions, policy files (RBAC, ABAC, ACL), database schemas,
service definitions, module boundaries.

### Step 2: Identify Components

Decompose into functional units: authentication, authorization, core business
logic, data access layer, API layer, background processing, admin/management,
integration layer (third-party clients, webhooks), and infrastructure (logging,
caching, sessions).

### Step 3: Map Roles and Permissions

For each component: identify user roles (anonymous, authenticated, admin, service
account), permission model (RBAC/ABAC/ACL), enforcement location (middleware,
decorators, inline), default permissions, and permission gaps.

### Step 4: Map Trust Boundaries

Identify where trust levels change: external-to-app, unauthenticated-to-authenticated,
user-to-admin, service-to-service (mTLS, API keys, JWT), app-to-datastore, and
app-to-third-party.

### Step 5: Classify Data

For each data entity: **Public** (marketing, public APIs), **Internal** (analytics,
internal docs), **Confidential** (PII, credentials, tokens), **Restricted**
(payment data, health records, encryption keys).

### Step 6: Document Auth/Authz Flows

Trace end-to-end: credential validation, session/token issuance, per-request
permission checks, and bypass paths (debug endpoints, feature flags, test accounts).

## Analysis Checklist

1. What trust boundaries does data cross between components?
2. Which components run with elevated privileges?
3. How are service-to-service calls authenticated?
4. Where does data sensitivity change (encryption, masking, aggregation)?
5. Are there shared databases or caches across trust boundaries?
6. What is the default permission level for new users or services?
7. Are there components that lack authorization checks entirely?
8. Do admin interfaces share authentication with user-facing interfaces?

## Output Format

Stage 3 produces a **Component Inventory with Trust Boundaries**. ID prefix: **PASTA** (e.g., `PASTA-S3-001`).

```
## PASTA Stage 3: Application Decomposition

### Component Inventory
| ID | Component | Function | Trust Level | Auth Mechanism |
|----|-----------|----------|-------------|---------------|
| C-01 | Auth Service | Login, registration, JWT | High | N/A (is the auth) |
| C-02 | API Gateway | Request routing | Medium | JWT validation |
| C-03 | Payment Module | Charge processing | High | JWT + role check |

### Role-Permission Matrix
| Role | C-01 Auth | C-02 API | C-03 Payment | C-04 Admin |
|------|----------|---------|-------------|-----------|
| Anonymous | register, login | public endpoints | none | none |
| User | profile, logout | CRUD own data | pay, history | none |
| Admin | manage users | all endpoints | refunds | full access |

### Data Classification
| Data Entity | Classification | Components | Encrypted Rest/Transit |
|------------|---------------|------------|----------------------|
| Credentials | Restricted | Auth Service | Hashed / TLS |
| Payment tokens | Restricted | Payment | Yes / TLS |

### Trust Boundaries
| Boundary | From | To | Mechanism | Validated |
|----------|------|----|-----------|-----------|
| TB-01 | Internet | API Gateway | HTTPS | TLS |
| TB-02 | Gateway | Auth Service | Internal HTTP | JWT |

### Authorization Gaps
[Components or endpoints without proper authorization enforcement]
```

Findings follow `../../shared/schemas/findings.md` with:
- `metadata.tool`: `"pasta-decompose"`, `metadata.framework`: `"pasta"`, `metadata.category`: `"Stage-3"`

## Next Stage

**Stage 4: Threat Analysis** (`pasta-threats`). Pass the Component Inventory,
Role-Permission Matrix, Data Classification, and Trust Boundaries. Stage 4
cross-references with real-world threat intelligence to identify relevant threats.
