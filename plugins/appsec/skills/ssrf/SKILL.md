---
name: ssrf
description: >
  This skill should be used when the user asks to "check for SSRF",
  "analyze server-side request forgery", "find URL fetching vulnerabilities",
  "check for internal network access", or mentions "SSRF", "URL fetching",
  "cloud metadata", "169.254.169.254", or "request forgery" in a security context.
  Maps to OWASP Top 10 2021 A10: Server-Side Request Forgery.
---

# Server-Side Request Forgery (A10:2021)

Analyze source code for server-side request forgery vulnerabilities including URL
fetching from user input, missing URL validation, internal network access, redirect
following, DNS rebinding, and cloud metadata endpoint access. SSRF is especially
critical in cloud environments where metadata endpoints expose credentials and
instance configuration.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks URL fetch calls for user-controlled input
- `--depth deep` traces URL input from request parameters through all transformations to fetch calls
- `--severity` filters output (SSRF to cloud metadata is `critical`, general SSRF is `high`)

## Framework Context

Read `../../shared/frameworks/owasp-top10-2021.md`, section **A10:2021 - Server-Side
Request Forgery (SSRF)**, for the full category description, common vulnerabilities,
and prevention guidance.

Key CWEs in scope:
- CWE-918: Server-Side Request Forgery (SSRF)
- CWE-441: Unintended Proxy or Intermediary
- CWE-601: URL Redirection to Untrusted Site (open redirect enabling SSRF chains)

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain outbound HTTP request logic:

- HTTP client usage (`**/http/**`, `**/client/**`, `**/fetch/**`, `**/request/**`)
- Webhook and callback handlers (`**/webhooks/**`, `**/callbacks/**`)
- Proxy and gateway code (`**/proxy/**`, `**/gateway/**`)
- Integration modules (`**/integrations/**`, `**/connectors/**`, `**/services/**`)
- File import/upload handlers (`**/upload/**`, `**/import/**`)
- URL preview or unfurling code (`**/preview/**`, `**/unfurl/**`, `**/embed/**`)
- PDF generation and screenshot services (`**/pdf/**`, `**/screenshot/**`, `**/render/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for SSRF patterns (taint analysis for URL flow)
2. `bandit` -- Python-specific request patterns
3. `gosec` -- Go HTTP client patterns

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting SSRF:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching SSRF, URL fetching, and request forgery patterns.
Normalize output to the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **URL from user input**: Find HTTP client calls (fetch, requests, http.get, etc.)
   and trace whether the URL or any URL component originates from user input
   (query params, request body, headers, path params).
2. **URL scheme validation**: Check that URL schemes are restricted to `http://` and
   `https://` only, blocking `file://`, `gopher://`, `dict://`, `ftp://`, and other
   dangerous schemes.
3. **Internal IP blocking**: Verify that URLs are validated against internal/private IP
   ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16,
   0.0.0.0, ::1, fd00::/8) before making requests.
4. **Cloud metadata protection**: Check for blocking of cloud metadata endpoints
   (169.254.169.254, metadata.google.internal, 169.254.170.2) and IMDSv2 enforcement
   on AWS.
5. **Redirect handling**: Verify that HTTP redirects are either disabled or validated
   at each hop to prevent redirect-based SSRF bypass.
6. **DNS rebinding**: Check if DNS resolution and connection happen atomically or if
   there is a TOCTOU gap where a hostname could resolve to a safe IP during validation
   but a private IP during the actual request.

When `--depth deep`, additionally trace:
- Complete data flow from request parameter to HTTP client call
- URL construction through string concatenation, template rendering, or URL builder APIs
- Indirect SSRF via PDF generators, screenshot services, SVG/XML processors, or webhook URLs

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `SSRF` prefix
(e.g., `SSRF-001`, `SSRF-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Impact description specific to the SSRF scenario (cloud metadata, internal scanning, data exfiltration)
- Concrete fix with diff when possible
- CWE and OWASP references

## What to Look For

These are the high-signal patterns specific to server-side request forgery. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **URL from user input passed to HTTP client** -- Any HTTP request function
   (fetch, requests.get, http.Get, HttpClient) called with a URL that originates
   from user-controlled input without validation.

2. **Missing URL scheme whitelist** -- URL validation that does not restrict the
   scheme to http/https, allowing file://, gopher://, or other dangerous protocols.

3. **No blocking of internal IP ranges** -- Outbound requests to user-supplied URLs
   without checking the resolved IP against private/reserved ranges, enabling
   internal network scanning and service access.

4. **Cloud metadata endpoint accessible** -- No specific blocking of 169.254.169.254
   (AWS/Azure/GCP metadata), metadata.google.internal, or 169.254.170.2 (ECS task
   metadata), allowing credential theft from cloud environments.

5. **Redirect following on user-supplied URLs** -- HTTP client configured to follow
   redirects when fetching user-supplied URLs, enabling attackers to bypass URL
   validation by redirecting from an allowed domain to an internal target.

6. **DNS rebinding vulnerability** -- URL validation resolves the hostname to check
   the IP, but the actual HTTP request resolves it again, allowing a DNS record
   with a short TTL to return a different (internal) IP on the second resolution.

7. **Indirect SSRF via document processors** -- PDF generators (wkhtmltopdf, Puppeteer),
   SVG renderers, XML parsers (XXE), or webhook registration endpoints that fetch
   URLs without SSRF protection.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | URL from user input, taint tracking through request calls | `semgrep scan --config auto --json --quiet <target>` |
| bandit | Python requests/urllib with user input | `bandit -r <target> -f json -q` |
| gosec | Go net/http with user input | `gosec -fmt json ./...` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find HTTP client calls, URL construction from user input, and missing validation.
Report findings with `confidence: medium`.

Relevant semgrep rule categories:
- `python.requests.security.ssrf.*`
- `python.urllib.security.audit.ssrf.*`
- `javascript.fetch.security.ssrf.*`
- `java.net.security.audit.ssrf.*`
- `go.net.security.audit.ssrf.*`

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `SSRF` (e.g., `SSRF-001`)
- **metadata.tool**: `ssrf`
- **metadata.framework**: `owasp`
- **metadata.category**: `A10`
- **references.owasp**: `A10:2021`
- **references.stride**: `I` (Information Disclosure) or `E` (Elevation of Privilege)

Severity guidance for this category:
- **critical**: SSRF to cloud metadata endpoint (169.254.169.254), unauthenticated endpoint with no URL validation
- **high**: SSRF to internal network with no IP range blocking, redirect following enabled on user URLs
- **medium**: Partial URL validation (scheme checked but IP not validated), DNS rebinding possible
- **low**: SSRF risk in internal-only service not exposed to external users, URL construction from partially controlled input
