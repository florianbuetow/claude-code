---
arc42_section: "06"
title: "Runtime View"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 6. Runtime View

<!-- arc42-meta section:06 provenance:derived confidence:medium -->

## Scenario: Create Task

```mermaid
sequenceDiagram
  Client->>Router: POST /tasks
  Router->>TaskHandler: handle(req)
  TaskHandler->>TaskRepo: insert(task)
  TaskRepo->>DB: INSERT INTO tasks ...
  DB-->>TaskRepo: id
  TaskRepo-->>TaskHandler: {id, ...}
  TaskHandler-->>Client: 201 Created
```

<!-- claim:runtime-create -->
The create-task flow is inferred from the `POST /tasks` route handler in `src/handlers/tasks.js`.
