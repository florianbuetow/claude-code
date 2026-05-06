# Theme Taxonomy for Documentation Index

Canonical ordering for the thematic table of contents, modeled after a well-structured technical book. Documents are classified into themes based on path components, filenames, and first-level headings.

## Theme Order

1. **Introduction** — Project overview, vision, mission
2. **Getting Started** — Quickstart guides, installation, setup, onboarding
3. **Concepts** — Core concepts, glossaries, mental models, architecture overview
4. **Architecture** — System design, data flow, component diagrams, ADRs
5. **Development** — Coding conventions, workflows, branching strategy, CI/CD
6. **API & Reference** — API docs, schemas, configuration reference, CLI reference
7. **Testing** — Test strategy, test plans, coverage, fixtures
8. **Security** — Security policies, threat models, compliance, audits
9. **Operations** — Deployment, monitoring, runbooks, incident response
10. **Contributing** — Contribution guidelines, code of conduct, PR templates
11. **Appendix** — Changelogs, license, third-party notices, migration guides

## Classification Signals

### Path-Based Signals

| Path Pattern | Theme |
|---|---|
| `docs/getting-started/*`, `docs/quickstart/*` | Getting Started |
| `docs/architecture/*`, `docs/adr/*`, `docs/design/*` | Architecture |
| `docs/api/*`, `docs/reference/*`, `docs/schema/*` | API & Reference |
| `docs/security/*`, `docs/compliance/*` | Security |
| `docs/ops/*`, `docs/deploy/*`, `docs/runbook/*` | Operations |
| `docs/dev/*`, `docs/development/*`, `docs/workflow/*` | Development |
| `docs/testing/*`, `docs/test/*` | Testing |
| `docs/concepts/*`, `docs/glossary/*` | Concepts |

### Filename-Based Signals

| Filename Pattern | Theme |
|---|---|
| `README.md` (root) | Introduction |
| `QUICKSTART.md`, `GETTING_STARTED.md` | Getting Started |
| `ARCHITECTURE.md`, `DESIGN.md`, `ADR-*.md` | Architecture |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | Contributing |
| `SECURITY.md`, `THREAT_MODEL.md` | Security |
| `CHANGELOG.md`, `CHANGES.md` | Appendix |
| `LICENSE.md`, `NOTICE.md` | Appendix |
| `MIGRATION.md`, `UPGRADE.md` | Appendix |
| `API.md`, `REFERENCE.md`, `SCHEMA.md` | API & Reference |
| `TESTING.md`, `TEST_PLAN.md` | Testing |
| `DEPLOY.md`, `RUNBOOK.md`, `OPS.md` | Operations |

### Heading-Based Signals (H1/H2)

When path and filename are ambiguous, classify by scanning the first H1 or H2:

- Keywords like "install", "setup", "getting started" → Getting Started
- Keywords like "architecture", "design", "system", "component" → Architecture
- Keywords like "api", "endpoint", "schema", "reference" → API & Reference
- Keywords like "test", "coverage", "fixture" → Testing
- Keywords like "security", "vulnerability", "threat" → Security
- Keywords like "deploy", "monitor", "incident", "runbook" → Operations
- Keywords like "contributing", "pull request", "code of conduct" → Contributing

### Fallback

Documents that match no signal go into **Appendix** with a note suggesting manual classification.

## Within-Theme Ordering

Within each theme, order documents:

1. Overview/index files first (e.g., `README.md` within a subdirectory)
2. Then alphabetically by filename
