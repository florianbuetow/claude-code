---
name: attack-surface
description: >
  This skill should be used when the user asks to "map attack surface",
  "list entry points", "inventory API endpoints", "find all inputs",
  "enumerate routes", "discover exposed endpoints", or "map external
  interfaces". Also triggers when the user asks about exposed APIs,
  form handlers, file upload endpoints, WebSocket handlers, CLI argument
  parsers, or wants to understand where external data enters the system.
---

# Attack Surface Mapping

Discover and inventory every entry point where external data enters the
application. Produces a ranked catalog of all routes, APIs, input handlers,
and external interfaces organized by exposure level and trust boundary.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Attack Surface Behavior |
|------|------------------------|
| `--scope` | Default `full`. Attack surface mapping benefits from whole-codebase visibility. Narrow scopes produce partial inventories with a warning. |
| `--depth quick` | Framework route extraction only (Grep for route decorators and definitions). |
| `--depth standard` | Route extraction + read handlers to classify input types and auth requirements. |
| `--depth deep` | Standard + trace each entry point to internal sinks, map trust boundary crossings. |
| `--depth expert` | Deep + rank by exploitability, identify shadow/undocumented endpoints, DREAD scoring. |
| `--severity` | Not directly applicable. Used to filter the exposure ranking in output. |
| `--format` | Default `text`. Use `json` for machine-readable inventory, `md` for wiki export. |

## Workflow

### Step 1: Determine Scope

1. Parse `--scope` flag. Default to `full` for this skill (attack surface requires broad visibility).
2. Resolve to a concrete file list.
3. Prioritize discovery in: route files, controller directories, API definitions, middleware,
   OpenAPI/Swagger specs, GraphQL schemas, gRPC proto files, CLI entry points, WebSocket handlers.

### Step 2: Discover Framework and Language

Identify the application framework(s) to determine route registration patterns:

| Framework | Route Pattern |
|-----------|--------------|
| Express/Koa/Fastify | `app.get()`, `router.post()`, `fastify.route()` |
| Django | `urlpatterns`, `path()`, `re_path()`, `@api_view` |
| Flask | `@app.route()`, `@blueprint.route()` |
| Spring | `@GetMapping`, `@PostMapping`, `@RequestMapping` |
| Rails | `routes.rb`, `resources :`, `get '/'` |
| Next.js/Nuxt | `pages/` and `app/` directory conventions, `route.ts` |
| ASP.NET | `[HttpGet]`, `[Route]`, `MapGet()`, `MapPost()` |
| Go net/http | `http.HandleFunc()`, `mux.Handle()`, gorilla/chi patterns |
| FastAPI | `@app.get()`, `@router.post()` |
| gRPC | `.proto` service definitions, generated server stubs |
| GraphQL | Schema definitions, resolver registrations |

### Step 3: Extract Entry Points

For each framework detected, systematically extract all entry points:

1. **HTTP Routes**: Method, path, handler function, middleware chain.
2. **API Endpoints**: REST, GraphQL queries/mutations, gRPC services.
3. **Form Handlers**: HTML form action targets, multipart upload handlers.
4. **File Upload Endpoints**: Endpoints accepting file data, storage destinations.
5. **WebSocket Handlers**: Connection endpoints, message handlers.
6. **CLI Arguments**: Argument parsers (`argparse`, `commander`, `cobra`, `clap`).
7. **Message Queue Consumers**: Kafka/RabbitMQ/SQS message handlers.
8. **Scheduled Tasks**: Cron jobs, scheduled functions that process external data.
9. **Webhook Receivers**: Endpoints accepting callbacks from external services.
10. **Server-Sent Events**: SSE endpoints, streaming responses.

### Step 4: Classify Each Entry Point

For every discovered entry point, determine:

1. **Authentication**: None, API key, session, JWT, OAuth, mTLS, or unknown.
2. **Authorization**: None, role-based, attribute-based, or unknown.
3. **Input Types**: Query params, path params, headers, body (JSON/XML/form), files, cookies.
4. **Validation**: Present (with details) or absent.
5. **Rate Limiting**: Present or absent.
6. **Network Exposure**: Internet-facing, internal network, localhost only.
7. **Protocol**: HTTP, HTTPS, WebSocket, gRPC, raw TCP, message queue.

### Step 5: Rank by Exposure

Assign an exposure level to each entry point:

| Level | Criteria |
|-------|----------|
| **CRITICAL** | Internet-facing, no authentication, accepts user input, interacts with sensitive data or system resources |
| **HIGH** | Internet-facing with authentication but handling sensitive data, or unauthenticated endpoints with limited input validation |
| **MEDIUM** | Authenticated endpoints with proper validation, or internal endpoints with no authentication |
| **LOW** | Internal endpoints with authentication, limited input surface, or read-only operations on non-sensitive data |

At `--depth deep` and `--depth expert`, trace each HIGH/CRITICAL entry point
inward to identify what sinks they reach (databases, file system, external
services, system commands).

### Step 6: Identify Shadow Endpoints

At `--depth expert`, look for:

- Debug/admin routes not behind auth middleware (e.g., `/debug`, `/admin`, `/metrics`, `/health` exposing internals).
- Routes registered dynamically or via reflection that don't appear in static route lists.
- Endpoints in test/staging configuration that may be active in production.
- API versions that are deprecated but still routed.
- OpenAPI/Swagger UI exposed without authentication.

### Step 7: Report

Output the attack surface inventory.

## Output Format

This skill produces an **inventory**, not vulnerability findings. However, when
entry points have clearly missing security controls (no auth on sensitive
endpoints), emit findings using the standard schema from `../../shared/schemas/findings.md`.

Finding ID prefix: **SURF** (e.g., `SURF-001`).

### Inventory Table

```
## Attack Surface Inventory

### Summary
- Total entry points: N
- Internet-facing: N (N unauthenticated)
- Internal: N
- Exposure: N CRITICAL, N HIGH, N MEDIUM, N LOW

### Entry Points by Exposure

| # | Method | Path | Auth | Input Types | Validation | Rate Limit | Exposure |
|---|--------|------|------|-------------|------------|------------|----------|
| 1 | POST | /api/v1/users | None | JSON body | None | No | CRITICAL |
| 2 | GET | /api/v1/users/:id | JWT | Path param | Partial | Yes | MEDIUM |
| ... |

### Trust Boundary Map (--depth deep)
[Mermaid diagram showing entry points grouped by trust boundary]

### Shadow Endpoints (--depth expert)
[Undocumented or debug endpoints discovered]

### Findings
[Standard findings for missing security controls on entry points]
```

Findings follow `../../shared/schemas/findings.md` with:
- `metadata.tool`: `"attack-surface"`
- `metadata.framework`: depends on invoking context (or `null` if standalone)
- `references.cwe`: `CWE-16` (Configuration), `CWE-306` (Missing Authentication)

## Pragmatism Notes

- Health check endpoints (`/health`, `/ready`) without auth are normal in container orchestration.
  Only flag if they expose sensitive internal state.
- Internal APIs behind a service mesh or VPN still warrant inventory but at lower exposure.
- CLI tools that only run locally have minimal attack surface unless they parse untrusted files.
- Static file serving endpoints are low priority unless directory traversal is possible.
