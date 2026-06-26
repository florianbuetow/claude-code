---
arc42_section: "02"
title: "Architecture Constraints"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 2. Architecture Constraints

<!-- arc42-meta section:02 provenance:derived confidence:high -->

| Constraint | Background |
|---|---|
| Node.js runtime | Inferred from `package.json` engine field |
| Docker deployment | Dockerfile present in root |
| PostgreSQL database | Referenced in `src/db.js` connection string |
| REST API | Express routes define HTTP endpoints |

<!-- claim:constraint-node -->
The runtime is constrained to Node.js ≥18 as specified in `package.json`.
