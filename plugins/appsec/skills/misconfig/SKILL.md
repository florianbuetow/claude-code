---
name: misconfig
description: >
  This skill should be used when the user asks to "check for misconfigurations",
  "analyze security headers", "find misconfigured settings", "check CORS policy",
  "find debug mode", "audit server configuration", or mentions "misconfiguration"
  in a security context. Maps to OWASP Top 10 2021 A05: Security Misconfiguration.
---

# Security Misconfiguration Analysis

Analyze application and infrastructure configuration for security misconfigurations
that could expose the system to attack. Covers missing security headers, debug modes
left enabled, overly permissive CORS, default credentials, verbose error handling,
unnecessary features, and directory listing.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

Key flags for this skill:

| Flag | Effect |
|------|--------|
| `--scope <value>` | Target scope (default: `changed`). Config-heavy scopes like `path:` and `full` are common. |
| `--depth <value>` | Analysis depth (default: `standard`). `deep` traces config inheritance chains. |
| `--severity <value>` | Minimum severity to report (default: all). |
| `--format <value>` | Output format: `text`, `json`, `sarif`, `md`. |
| `--fix` | Generate remediation patches for each finding. |
| `--explain` | Add OWASP context and learning material to each finding. |

## Framework Context

**OWASP Top 10 2021 -- A05: Security Misconfiguration**

Security misconfiguration is the most commonly seen issue. This is commonly a result
of insecure default configurations, incomplete or ad hoc configurations, open cloud
storage, misconfigured HTTP headers, unnecessary HTTP methods, permissive CORS,
and verbose error messages containing sensitive information.

**CWE Mappings**:
- CWE-16: Configuration
- CWE-2: Environment
- CWE-388: Error Handling
- CWE-497: Exposure of System Data to an Unauthorized Control Sphere
- CWE-611: Improper Restriction of XML External Entity Reference
- CWE-614: Sensitive Cookie in HTTPS Session Without 'Secure' Attribute
- CWE-756: Missing Custom Error Page
- CWE-942: Permissive Cross-domain Policy with Untrusted Domains

**STRIDE Mapping**: All categories -- misconfigurations can enable spoofing, tampering,
information disclosure, denial of service, and elevation of privilege.

## Detection Patterns

Read [`references/detection-patterns.md`](references/detection-patterns.md) before
running analysis. It contains Grep regex patterns, language-specific examples, scanner
coverage, and false positive guidance for each detection category.

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to configuration-relevant files:
   - Application config: `*.yaml`, `*.yml`, `*.toml`, `*.ini`, `*.cfg`, `*.conf`, `*.json`, `*.properties`, `*.env`, `*.env.*`
   - Server config: `nginx.conf`, `httpd.conf`, `apache2.conf`, `Caddyfile`, `traefik.yml`
   - Framework config: `settings.py`, `config/*.rb`, `application.properties`, `next.config.*`, `nuxt.config.*`
   - IaC: `*.tf`, `*.hcl`, `Dockerfile`, `docker-compose*.yml`, `*.k8s.yml`, `k8s/*.yaml`
   - CI/CD: `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/config.yml`
   - Source files that set headers or configure middleware
4. Also include source files that import/configure security middleware or set HTTP headers.

### Step 2 -- Check for Scanners

Detect available scanners in priority order:

| Scanner | Detect | Best For |
|---------|--------|----------|
| checkov | `which checkov` | IaC misconfigurations (Terraform, K8s, Docker) |
| tfsec | `which tfsec` | Terraform-specific security |
| kics | `which kics` | Multi-IaC scanning |
| trivy | `which trivy` | Filesystem misconfigs, Dockerfiles, K8s |
| semgrep | `which semgrep` | Code-level misconfiguration patterns |

If no scanners are found, proceed with Claude analysis only and note this in output.

### Step 3 -- Run Available Scanners

For each detected scanner, run against the scoped files:

- **checkov**: `checkov -d <target> -o json --quiet`
- **tfsec**: `tfsec <target> --format json`
- **kics**: `kics scan -p <target> --type json`
- **trivy**: `trivy fs --format json --scanners misconfig <target>`
- **semgrep**: `semgrep scan --config auto --json --quiet <target>`

Normalize scanner output to the findings schema per
[`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md).

### Step 4 -- Claude Analysis

Using Grep and Read, search for patterns from `references/detection-patterns.md`.
For each match:

1. Read surrounding context (10-20 lines) to determine if the pattern is a true finding.
2. Check for compensating controls (e.g., a reverse proxy may set headers upstream).
3. Determine if the configuration is for production or development.
4. Assign severity based on the criteria in detection-patterns.md.
5. Avoid duplicating scanner findings -- deduplicate by file and line.

### Step 5 -- Report Findings

Output findings using the schema from
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

Use the **MSCFG** prefix for finding IDs (e.g., `MSCFG-001`, `MSCFG-002`).

## What to Look For

1. **Debug mode enabled in production** -- `DEBUG=True`, `NODE_ENV=development`,
   `FLASK_DEBUG=1`, `RAILS_ENV=development` in production-bound configs.
2. **Missing security headers** -- No Content-Security-Policy, X-Frame-Options,
   Strict-Transport-Security, X-Content-Type-Options, Permissions-Policy, or
   Referrer-Policy in HTTP responses.
3. **CORS wildcard or overly permissive origins** -- `Access-Control-Allow-Origin: *`
   or reflecting arbitrary Origin headers without validation.
4. **Default credentials** -- Unchanged admin/admin, root/root, or well-known default
   passwords in configuration files.
5. **Verbose error handling** -- Stack traces, internal paths, database details, or
   framework version numbers exposed to end users in error responses.
6. **Unnecessary features enabled** -- Directory listing, HTTP TRACE/TRACK methods,
   admin panels exposed without authentication, phpinfo() pages.
7. **Insecure cookie attributes** -- Missing Secure, HttpOnly, or SameSite flags on
   session or authentication cookies.
8. **Permissive file permissions** -- World-readable secrets, 777 permissions on
   sensitive directories, overly broad IAM policies.
9. **TLS/SSL misconfiguration** -- Weak cipher suites, outdated TLS versions (< 1.2),
   self-signed certificates in production, missing HSTS.
10. **Missing rate limiting** -- No rate limiting on authentication endpoints, API
    routes, or form submissions.

## Scanner Integration

See [`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md) for full scanner
invocation details. This skill primarily uses:

| Scanner | What It Catches |
|---------|----------------|
| checkov | IaC misconfigurations: open security groups, missing encryption, public S3 buckets |
| tfsec | Terraform-specific: missing tags, public subnets, insecure defaults |
| kics | Multi-IaC: Docker, K8s, Terraform, CloudFormation misconfigurations |
| trivy | Dockerfile and K8s manifest misconfigurations, misconfigured filesystem |
| semgrep | Code patterns: missing headers, debug flags, insecure cookie settings |

When scanners are unavailable, Claude falls back to Grep-based detection using the
patterns in `references/detection-patterns.md` and reports findings with
`confidence: medium`.

## Output Format

All findings use the schema defined in
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

**ID Prefix**: `MSCFG` (e.g., `MSCFG-001`)

**References for each finding**:
- `references.owasp`: `A05:2021`
- `references.cwe`: Appropriate CWE from the list above
- `references.stride`: Relevant STRIDE category
- `metadata.tool`: `misconfig`
- `metadata.framework`: `owasp`
- `metadata.category`: `A05`

**Summary table** after all findings:

```
| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |
```

Followed by top 3 priorities and an overall assessment paragraph.
