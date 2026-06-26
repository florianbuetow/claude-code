---
arc42_section: "05"
title: "Building Block View"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 5. Building Block View

<!-- arc42-meta section:05 provenance:derived confidence:high -->

## Level 1: Whitebox System

```mermaid
graph TD
  Router[Express Router] --> TaskHandler[Task Handler]
  TaskHandler --> TaskRepo[Task Repository]
  TaskRepo --> DB[(PostgreSQL)]
```

## Components

| Block | Source | Responsibility |
|---|---|---|
| Express Router | `src/index.js` | HTTP routing |
| Task Handler | `src/handlers/tasks.js` | Request validation + response |
| Task Repository | `src/db.js` | SQL queries |

<!-- claim:block-router -->
The router is defined in `src/index.js`; it delegates to handler functions.
