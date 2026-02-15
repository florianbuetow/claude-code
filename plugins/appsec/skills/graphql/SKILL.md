---
name: graphql
description: >
  This skill should be used when the user asks to "check GraphQL security",
  "analyze GraphQL endpoint", "find GraphQL vulnerabilities", "audit GraphQL
  schema", "check for introspection", "analyze query depth", or mentions
  "GraphQL", "introspection", "query depth limit", "query complexity",
  "GraphQL batching", "alias abuse", or "per-field authorization" in a
  security context.
---

# GraphQL Security (GQL)

Analyze GraphQL APIs for security vulnerabilities including introspection
enabled in production, missing query depth limits, no complexity analysis,
batching abuse, alias-based denial of service, and missing per-field
authorization. GraphQL's flexibility makes it a rich attack surface when
default configurations are deployed to production without hardening.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks GraphQL configuration
- `--depth deep` traces resolvers to data sources and maps authorization coverage
- `--severity` filters output (GraphQL issues range from `medium` to `critical`)

## Framework Context

Key CWEs in scope:
- CWE-200: Exposure of Sensitive Information (introspection)
- CWE-400: Uncontrolled Resource Consumption (depth/complexity)
- CWE-862: Missing Authorization (per-field auth)
- CWE-770: Allocation of Resources Without Limits (batching)
- CWE-284: Improper Access Control

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain GraphQL logic:

- Schema definitions (`**/*.graphql`, `**/schema.*`, `**/typeDefs*`)
- Resolver implementations (`**/resolvers/**`, `**/graphql/**`)
- GraphQL server configuration (`**/server.*`, `**/app.*`, `**/index.*`)
- Middleware and plugins (`**/middleware/**`, `**/plugins/**`)
- Authorization directives (`**/directives/**`, `**/guards/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for GraphQL patterns
2. `graphql-cop` -- specialized GraphQL security auditor (if available)

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting GraphQL:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching GraphQL security patterns. Normalize output
to the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **Introspection check**: Find GraphQL server configuration and verify
   introspection is disabled in production environments.
2. **Depth limiting**: Check for depth limiting middleware (graphql-depth-limit,
   @graphql-tools/utils, custom validation rules).
3. **Complexity analysis**: Verify query complexity is calculated and limited
   before execution (graphql-query-complexity, cost analysis).
4. **Batching controls**: Check whether query batching is enabled and if
   there are limits on the number of operations per request.
5. **Alias abuse**: Verify aliases are counted toward rate limiting and
   complexity calculations.
6. **Per-field authorization**: Trace resolvers for sensitive fields and verify
   each checks the requesting user's permissions.

When `--depth deep`, additionally trace:
- Full resolver chain from query to data source
- Authorization directive/guard coverage across all types and fields
- Subscription authentication and authorization

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `GQL` prefix
(e.g., `GQL-001`, `GQL-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Exploit scenario (example malicious query when applicable)
- Concrete fix with diff when possible
- CWE references

## What to Look For

These are the high-signal patterns specific to GraphQL security. Each maps
to a detection pattern in `references/detection-patterns.md`.

1. **Introspection enabled in production** -- `__schema` and `__type` queries
   are accessible, revealing the entire API schema to attackers.

2. **No query depth limit** -- Deeply nested queries can exhaust server resources
   (e.g., `user { friends { friends { friends { ... } } } }`).

3. **No query complexity limit** -- Expensive queries with many fields or
   computed values can cause denial of service.

4. **Batching abuse** -- Multiple queries in a single request bypass per-request
   rate limiting and can brute-force authentication.

5. **Alias-based denial of service** -- Using aliases to repeat expensive
   fields/resolvers many times in a single query.

6. **Missing per-field authorization** -- Sensitive fields (email, SSN, balance)
   exposed to any authenticated user without field-level access checks.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | Introspection, missing auth directives | `semgrep scan --config auto --json --quiet <target>` |
| graphql-cop | Introspection, depth, batching, aliases | `graphql-cop -t <endpoint>` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find GraphQL server configuration, depth/complexity middleware, resolver
authorization, and batching settings. Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `GQL` (e.g., `GQL-001`)
- **metadata.tool**: `graphql`
- **metadata.framework**: `specialized`
- **metadata.category**: `GQL`
- **references.cwe**: `CWE-200`, `CWE-400`, `CWE-862`
- **references.owasp**: `A05:2021` (Security Misconfiguration)
- **references.stride**: `I` (Information Disclosure) or `D` (Denial of Service)

Severity guidance for this category:
- **critical**: Missing per-field auth on sensitive data, introspection exposing internal schemas
- **high**: No depth or complexity limits, batching with no limits on auth endpoints
- **medium**: Introspection enabled in prod (non-sensitive schema), alias abuse possible
- **low**: Overly permissive but rate-limited batching, minor information disclosure
