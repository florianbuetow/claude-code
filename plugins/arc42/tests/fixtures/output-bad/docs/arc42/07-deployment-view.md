---
arc42_section: "07"
title: "Deployment View"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 7. Deployment View

<!-- arc42-meta section:07 provenance:derived confidence:high -->

## Infrastructure

```mermaid
graph TD
  subgraph Docker Host
    API[task-api container :3000]
    PG[postgres container :5432]
  end
  Client -->|HTTPS| API
  API -->|SQL| PG
```

| Artifact | Source | Notes |
|---|---|---|
| task-api image | `Dockerfile` | Node.js 18 alpine, port 3000 |
| postgres | official image | PostgreSQL 15 |

<!-- claim:deploy-docker -->
The deployment topology is derived from the `Dockerfile` in the repository root.
The base image `node:18-alpine` and `EXPOSE 3000` are present in the Dockerfile.
