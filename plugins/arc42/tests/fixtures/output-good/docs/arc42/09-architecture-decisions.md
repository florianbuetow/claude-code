---
arc42_section: "09"
title: "Architecture Decisions"
source_commit: "abc1234def5678"
generated_at: "2025-01-15T10:00:00Z"
arc42_kb_version: "1.0.0"
upstream_hash: "deadbeef01234567"
---

# 9. Architecture Decisions

<!-- arc42-meta section:09 provenance:derived confidence:medium -->

## ADR-001: Express.js as web framework

**Status:** Accepted (inferred)

**Context:** A Node.js server is needed to expose a REST API.

**Decision:** Use Express.js as the HTTP framework.

**Consequences:** Simple routing; middleware ecosystem available.

<!-- claim:adr-express -->
Express.js is listed as a dependency in `package.json` and its routing patterns
are used throughout `src/index.js`.

## ADR-002: PostgreSQL as database

**Status:** Accepted (inferred)

**Context:** Persistent storage is required for tasks.

**Decision:** Use PostgreSQL.

**Consequences:** Relational integrity; SQL queries in `src/db.js`.

<!-- claim:adr-postgres -->
The `pg` npm package appears in `package.json` and connection code is in `src/db.js`.
