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
