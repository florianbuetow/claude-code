---
arc42_section: "12"
title: "Glossary"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 12. Glossary

<!-- arc42-meta section:12 provenance:derived confidence:medium -->

| Term | Definition |
|---|---|
| Task | A unit of work with a title, description, due date, and completion status |
| REST | Representational State Transfer; the API style used by this system |
| CRUD | Create, Read, Update, Delete; the four basic data operations |
| JWT | JSON Web Token; a common stateless authentication mechanism (not yet implemented) |
| ADR | Architecture Decision Record; a document capturing an architectural decision |

<!-- claim:glossary-task -->
The `Task` entity is defined by the SQL schema in `src/db.js` (`CREATE TABLE tasks`).
