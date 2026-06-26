---
arc42_section: "03"
title: "System Scope and Context"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 3. System Scope and Context

<!-- arc42-meta section:03 provenance:derived confidence:high -->

## 3.1 Business Context

The task-list API interacts with the following external systems:

| Neighbour | Direction | Interface |
|---|---|---|
| HTTP Client (browser/mobile) | in | REST/JSON over HTTPS |
| PostgreSQL | out | TCP/5432, SQL |

## 3.2 Technical Context

```mermaid
graph LR
  Client -->|HTTPS REST| API[Task API]
  API -->|SQL| DB[(PostgreSQL)]
```

<!-- claim:context-db -->
The only persistent store is PostgreSQL, inferred from `src/db.js`.
