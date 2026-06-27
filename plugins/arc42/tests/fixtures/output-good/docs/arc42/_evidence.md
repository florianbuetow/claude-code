# Evidence Index

This file maps every `<!-- claim:… -->` anchor to its source evidence.

| Claim | File | Evidence |
|---|---|---|
| req-crud | 01-introduction-and-goals.md | `src/index.js` routes: GET/POST/PUT/DELETE `/tasks` |
| constraint-node | 02-architecture-constraints.md | `package.json` `"engines": {"node": ">=18"}` |
| context-db | 03-system-scope-and-context.md | `src/db.js` `new Pool({...})` PostgreSQL connection |
| strategy-monolith | 04-solution-strategy.md | Single `Dockerfile`, single `src/` tree, no docker-compose |
| block-router | 05-building-block-view.md | `src/index.js` `app.use('/tasks', taskRouter)` |
| runtime-create | 06-runtime-view.md | `src/handlers/tasks.js` `router.post('/', ...)` |
| deploy-docker | 07-deployment-view.md | `Dockerfile` `FROM node:18-alpine` + `EXPOSE 3000` |
| concept-error-handling | 08-crosscutting-concepts.md | `src/handlers/tasks.js` try/catch blocks |
| adr-express | 09-architecture-decisions.md | `package.json` `"express": "^4.18.0"` |
| adr-postgres | 09-architecture-decisions.md | `package.json` `"pg": "^8.11.0"` |
| quality-eslint | 10-quality-requirements.md | `.eslintrc.json` present at repo root |
| risk-no-auth | 11-risks-and-technical-debts.md | No `app.use(auth...)` in `src/index.js` |
| risk-no-tests | 11-risks-and-technical-debts.md | No `test` script in `package.json`, no `test/` dir |
| glossary-task | 12-glossary.md | `src/db.js` `CREATE TABLE tasks (...)` |
