---
name: privilege-escalation
description: >
  This skill should be used when the user asks to "check for privilege escalation",
  "analyze authorization risks", "find access control vulnerabilities", or mentions
  "elevation of privilege" in a security context. Maps to STRIDE category E.
---

# Elevation of Privilege Analysis

Analyze source code for privilege escalation threats where attackers can gain unauthorized capabilities or access. Maps to **STRIDE E** -- violations of the **Authorization** security property.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full flag specification. This skill supports all cross-cutting flags including `--scope`, `--depth`, `--severity`, `--format`, `--fix`, `--quiet`, and `--explain`.

## Framework Context

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md), specifically the **E - Elevation of Privilege** section, for the threat model backing this analysis. Key concerns: broken access control (IDOR), missing function-level access control, JWT manipulation, role confusion, privilege escalation.

## Workflow

### 1. Determine Scope

Parse flags and resolve the target file list per the flags spec. Filter to files implementing authorization:

- Route handlers with role checks and permission guards
- Authorization middleware and policy enforcement points
- RBAC/ABAC implementations and permission models
- Admin endpoints and administrative interfaces
- User management (create, update roles, delete accounts)
- Object ownership checks and tenant isolation logic
- API controllers and GraphQL resolvers with access control
- Infrastructure-as-code defining IAM roles and security groups

### 2. Analyze for Privilege Escalation Threats

For each in-scope file, apply the Analysis Checklist below. At `--depth standard`, examine authorization logic in each file. At `--depth deep`, map the full authorization architecture: who can access what, where checks are enforced, where gaps exist between routes, and whether authorization is consistently applied at every layer.

### 3. Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) using the `PRIV` ID prefix (e.g., `PRIV-001`). Set `references.stride` to `"E"` on every finding.

## Analysis Checklist

Work through these questions against the scoped code. Each "yes" may produce a finding.

1. **Missing function-level access control** -- Are admin or privileged endpoints accessible without role verification? Compare route definitions: if some routes check `isAdmin`, `requireRole('admin')`, or `@permission_required`, identify sibling routes that should but do not have equivalent guards. Map all endpoints and flag gaps in the authorization layer.
2. **Insecure direct object references (IDOR)** -- Do endpoints use user-supplied IDs to fetch resources without verifying ownership? Look for `findById(req.params.id)`, `getRecord(id)` where the result is not checked against the requesting user's permissions or tenant. Test: can user A access user B's resources by changing the ID?
3. **JWT claim manipulation** -- Are JWT role or permission claims trusted without server-side verification? Check if role-based decisions use claims from the token payload without cross-referencing a server-side authority (database, LDAP). Look for `jwt.decode` without verify, or role checks solely from token claims.
4. **Client-side authorization** -- Are access control decisions made only in frontend code (React/Vue/Angular component guards, route guards) without corresponding server-side enforcement on the API endpoints they call? Search for `role`, `isAdmin`, `canAccess` in frontend code and verify equivalent checks exist server-side.
5. **Mass assignment to role fields** -- Can users set their own role, `isAdmin`, `permissions`, or `group` fields through API requests? Look for ORM `.create(req.body)` or `.update(req.body)` without excluding privilege-related fields. Check for `attr_accessible`, `fillable`, `$guarded`, or DTO validation that strips role fields.
6. **Default admin accounts** -- Are there hardcoded admin users created in seed scripts, migrations, or initialization code with well-known credentials? Look for `role: 'admin'` combined with `password:` in seed data. Check if these are gated behind environment checks (`if NODE_ENV === 'development'`).
7. **Horizontal privilege escalation** -- Can users access other users' resources by manipulating IDs? Check if resource queries include ownership filters (`WHERE user_id = ?` or `WHERE org_id = ?`) or if they rely solely on the resource ID from the request. Multi-tenant applications must enforce tenant isolation on every query.
8. **Trust boundary violations** -- Are internal-only services or endpoints accessible from external networks? Look for admin APIs without network-level restrictions, internal microservice calls that accept external requests, or debug/management ports exposed without authentication.
9. **Broken role hierarchy** -- Is the role hierarchy enforced consistently? Check if `editor` can perform `admin` actions, or if role inheritance has gaps. Look for permission checks using string comparison (`if role === 'admin'`) instead of hierarchical evaluation that accounts for role inheritance.
10. **Missing deny-by-default** -- Does the authorization system default to allow when no explicit rule matches? Check middleware ordering: is there a catch-all deny at the end, or do unmatched routes pass through without authorization? Look for `next()` called unconditionally in auth middleware.
11. **Path parameter manipulation** -- Can URL path parameters be manipulated to bypass route-level authorization? For example, accessing `/api/admin/../user/settings` to bypass admin-only middleware, or using URL encoding tricks to evade path-based access rules.
12. **Scope/permission creep in tokens** -- Are OAuth scopes or API key permissions overly broad? Check if tokens are issued with `scope: *`, full permissions, or if fine-grained scopes are available but not enforced. Look for scope validation at the endpoint level, not just at token issuance.

## Pragmatism Notes

- Single-user applications or personal tools may not have authorization at all, and that is fine. Only flag missing authz when the application clearly has multiple user roles or multi-tenancy.
- IDOR findings require understanding the data model. Not every `findById(req.params.id)` is an IDOR -- some resources are intentionally public (e.g., blog posts, product listings). Focus on resources that contain user-private data.
- Client-side route guards are expected for UX (hiding admin buttons from regular users) but are not security controls. Only flag when the corresponding server-side check is missing.
- Mass assignment protections vary by framework. Before reporting, check if the framework has built-in protection (Rails strong params, Django ModelForm, NestJS DTOs with class-validator). Flag only when protection is absent or misconfigured.
- Role hierarchies are application-specific. A flat role model (`admin` / `user`) is not a finding. Flag only when the code shows evidence of an intended hierarchy that is inconsistently enforced.

## What to Look For

Concrete code patterns and grep heuristics to surface privilege escalation risks:

- **Unprotected admin routes**: Routes containing `/admin`, `/manage`, `/internal`, `/dashboard`, `/settings` without auth middleware. Compare middleware chains between admin and public routes. Grep: `(admin|manage|internal|dashboard)` in route definitions.
- **Direct ID lookups without ownership**: `Model.findById(req.params.id)` or `db.query("SELECT ... WHERE id = $1", [req.params.id])` without a `user_id` or `org_id` filter joined to the session user. Grep: `findById\s*\(\s*req\.(params|query)|WHERE id\s*=` without ownership clause.
- **Role from client**: `req.body.role`, `request.data['is_admin']`, `params[:role]` used in user creation or update without stripping. Also `req.user.role` derived solely from JWT without server-side lookup. Grep: `req\.(body|query|params)\.(role|isAdmin|is_admin|permissions|group)`.
- **Missing middleware on routes**: Routes registered after auth middleware is applied vs. routes registered before (ordering bug). Check for `app.use(authMiddleware)` placement relative to route definitions. Grep: `app\.(get|post|put|delete|use)\s*\(` to map registration order.
- **Wildcard permissions**: `permission: '*'`, `role: 'superadmin'` granted broadly, `if (user.role) { allow }` checking role existence rather than specific role value. Grep: `permission.*\*|role.*super|if\s*\(\s*user\.(role|admin)`.
- **Unsafe defaults**: `authorized: true` as default, `access: 'public'` on sensitive resources, missing `else deny` in conditional authorization. Grep: `authorized.*true|access.*public|default.*allow`.
- **Privilege fields in mass assignment**: `.create(req.body)`, `Object.assign(user, req.body)`, `**request.data` without `exclude_fields` or `pick` for role/permission attributes. Grep: `\.create\(\s*req\.body|Object\.assign\(.*req\.body|\.update\(\s*\{.*\.\.\.req`.
- **Inconsistent checks**: Some endpoints for a resource check permissions while sibling endpoints for the same resource do not. Search for the resource name across handlers and compare auth patterns. Flag asymmetric coverage.

## Output Format

Each finding must conform to [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

```
id:          PRIV-<NNN>
severity:    critical | high | medium | low
confidence:  high | medium | low
location:    file, line, function, snippet
description: What the privilege escalation path is and how it can be exploited
impact:      What unauthorized capabilities an attacker gains
fix:         Concrete remediation with diff when possible
references:
  stride: "E"
  cwe:    CWE-269 (Improper Privilege Mgmt), CWE-639 (IDOR), or relevant CWE
metadata:
  tool:      privilege-escalation
  framework: stride
  category:  E
```

### Severity Guidelines for Elevation of Privilege

| Severity | Criteria |
|----------|----------|
| `critical` | Admin endpoints without auth, mass assignment allowing role escalation to admin, IDOR on sensitive resources (financial data, PII, other users' accounts) |
| `high` | Missing function-level access control on data modification endpoints, JWT role trust without server-side verification, broken tenant isolation |
| `medium` | Horizontal privilege escalation on non-sensitive resources, client-only authorization, inconsistent permission checks across sibling endpoints |
| `low` | Default admin in dev seeds, overly broad wildcard permissions in non-production config, missing deny-by-default on low-impact routes |

### Common CWE References

| CWE | Description |
|-----|-------------|
| CWE-269 | Improper Privilege Management |
| CWE-639 | Authorization Bypass Through User-Controlled Key (IDOR) |
| CWE-862 | Missing Authorization |
| CWE-863 | Incorrect Authorization |
| CWE-285 | Improper Authorization |
| CWE-915 | Improperly Controlled Modification of Dynamically-Determined Object Attributes (Mass Assignment) |
| CWE-284 | Improper Access Control |
