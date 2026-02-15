---
name: tampering
description: >
  This skill should be used when the user asks to "check for tampering",
  "analyze data integrity risks", "find injection vulnerabilities", or
  mentions "tampering" in a security context. Maps to STRIDE category T.
---

# Tampering with Data Analysis

Analyze source code for tampering threats where attackers can modify data, code, or configuration without detection. Maps to **STRIDE T** -- violations of the **Integrity** security property.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full flag specification. This skill supports all cross-cutting flags including `--scope`, `--depth`, `--severity`, `--format`, `--fix`, `--quiet`, and `--explain`.

## Framework Context

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md), specifically the **T - Tampering with Data** section, for the threat model backing this analysis. Key concerns: SQL injection, parameter tampering, man-in-the-middle, file modification, configuration tampering, code injection.

## Workflow

### 1. Determine Scope

Parse flags and resolve the target file list per the flags spec. Filter to files likely relevant to data handling:

- Database query builders and ORM usage
- API request handlers and form processors
- File upload and file write operations
- Configuration loaders and environment parsers
- Serialization/deserialization logic
- Template rendering engines
- Webhook receivers and inter-service message handlers
- Package manifests and lock files (for supply chain integrity)

### 2. Analyze for Tampering Threats

For each in-scope file, apply the Analysis Checklist below. At `--depth standard`, read each file and trace user input to data operations. At `--depth deep`, follow input across file boundaries through function calls, imports, and middleware chains to find indirect injection paths.

### 3. Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) using the `TAMP` ID prefix (e.g., `TAMP-001`). Set `references.stride` to `"T"` on every finding.

## Analysis Checklist

Work through these questions against the scoped code. Each "yes" may produce a finding.

1. **SQL injection** -- Is user input concatenated or interpolated into SQL strings? Search for string formatting in query construction: f-strings, `+` concatenation, `format()`, template literals near `SELECT`, `INSERT`, `UPDATE`, `DELETE`. Even ORM raw query methods are vulnerable if they interpolate user input.
2. **Command injection** -- Is user input passed to shell execution functions? Look for `os.system`, `subprocess.call` with `shell=True`, `exec()`, `child_process.exec`, backtick execution with unsanitized input. Check if arguments are passed as arrays (safe) vs. strings (unsafe).
3. **NoSQL injection** -- Are user-controlled objects passed directly into MongoDB/NoSQL query operators? Look for `$gt`, `$ne`, `$where`, `$regex` coming from request bodies without schema validation or type enforcement.
4. **Parameter tampering** -- Are hidden form fields, cookies, or URL parameters trusted without server-side validation? Check if price, role, user ID, quantity, or discount values from the client are used directly in business logic without re-derivation from server state.
5. **Missing integrity checks** -- Are downloaded files, API responses, or inter-service messages consumed without HMAC, signature, or checksum verification? Look for `fetch`, `requests.get`, file reads where the content is used without hash validation. Check webhook handlers for missing signature verification.
6. **Unsafe deserialization** -- Is untrusted data deserialized with `pickle.loads`, `yaml.load` (without SafeLoader), `unserialize()`, `ObjectInputStream`, `Marshal.load`, or `eval(JSON)`? These can lead to remote code execution.
7. **Path traversal for writes** -- Can user input influence file write paths? Look for `../` or unvalidated path components in file creation, upload handling, or log file naming. Check if `os.path.realpath` or equivalent canonicalization is applied before writing.
8. **Missing CSRF protection** -- Do state-changing endpoints (POST/PUT/DELETE) lack CSRF token validation? Check for absence of CSRF middleware, `@csrf_exempt` on sensitive endpoints, or token verification gaps in form handlers.
9. **Configuration injection** -- Can environment variables, config files, or feature flags be modified through application inputs? Look for dynamic config loading from user-influenced sources, admin panels that write config without integrity checks.
10. **Template injection** -- Is user input rendered in server-side templates without escaping? Search for `render_template_string`, Jinja2 with `autoescape=False`, `eval` in template contexts, Handlebars triple-stash `{{{`, or Twig raw filters on user data.
11. **Header injection** -- Can user input be injected into HTTP response headers? Look for `setHeader`, `res.header`, `response.headers` where values come from request parameters, enabling response splitting or cookie injection.
12. **Prototype pollution** -- In JavaScript, are user-controlled objects merged unsafely? Look for `Object.assign({}, userInput)`, `_.merge`, `_.defaultsDeep`, or spread operators on untrusted data that could set `__proto__` or `constructor.prototype`.

## Pragmatism Notes

- Not every string concatenation near SQL is injection. Check if the concatenated value is a constant, an enum, or derived from trusted server-side logic. Only flag when user input reaches the query.
- CSRF protection is less relevant for pure JSON APIs consumed by SPAs with token-based auth (Bearer tokens are not automatically attached like cookies). Focus CSRF findings on cookie-authenticated form submissions.
- Prototype pollution is JavaScript-specific. Skip this check for other language ecosystems.
- Mass assignment findings require checking the ORM's built-in protections. Many modern frameworks (Rails strong params, Django forms, Pydantic models) have allowlisting built in.

## What to Look For

Concrete code patterns and grep heuristics to surface tampering risks:

- **String-built queries**: `f"SELECT`, `"SELECT * FROM " +`, `query = "...${`, `.format(` adjacent to SQL keywords, `execute(f"`, `.query("..."+`. Grep: `(execute|query|prepare)\s*\(\s*(f['"]|['"].*\+|.*format)`.
- **Shell execution with input**: `os.system(`, `subprocess.call(.*shell=True`, `exec(`, `child_process.exec(`, `Runtime.getRuntime().exec(`. Grep: `(system|exec|popen|spawn)\s*\(`.
- **Unsafe deserialization**: `pickle.loads`, `yaml.load(` without `Loader=SafeLoader`, `unserialize(`, `readObject(`, `eval(.*JSON`, `Marshal.load`. Grep: `(pickle\.loads|yaml\.load|unserialize|readObject|Marshal\.load)`.
- **Missing parameterization**: Database calls using string concatenation instead of `?`, `$1`, or `%s` placeholders with parameter tuples/arrays.
- **No CSRF middleware**: State-changing routes without `csrf_protect`, `csurf`, `@csrf_exempt` on sensitive endpoints, missing `X-CSRF-Token` header checks. Grep: `csrf_exempt|csrf.*disable`.
- **Unvalidated file paths**: `os.path.join(base, user_input)` without `os.path.commonprefix` or realpath validation, `path.resolve` without containment check, `..` not stripped from upload filenames.
- **Direct object use from request**: `req.body` or `request.json` passed directly to ORM `.create()` or `.update()` without allowlist filtering (mass assignment risk). Grep: `\.create\(\s*req\.body|\.update\(\s*req\.body`.
- **Prototype pollution vectors**: `_.merge(`, `_.defaultsDeep(`, `Object.assign(.*req` with untrusted input. Grep: `(merge|assign|extend)\s*\(.*req\.(body|query|params)`.

## Output Format

Each finding must conform to [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

```
id:          TAMP-<NNN>
severity:    critical | high | medium | low
confidence:  high | medium | low
location:    file, line, function, snippet
description: What the tampering risk is and how it could be exploited
impact:      What an attacker can modify or corrupt
fix:         Concrete remediation with diff when possible
references:
  stride: "T"
  cwe:    CWE-89 (SQLi), CWE-78 (OS Command Injection), CWE-352 (CSRF), or relevant CWE
metadata:
  tool:      tampering
  framework: stride
  category:  T
```

### Severity Guidelines for Tampering

| Severity | Criteria |
|----------|----------|
| `critical` | SQL/command/template injection with direct user input, unsafe deserialization of untrusted data, RCE via prototype pollution |
| `high` | NoSQL injection, path traversal on write operations, mass assignment without field allowlist, missing webhook signature verification |
| `medium` | Missing CSRF on state-changing endpoints, configuration values from unvalidated sources, header injection |
| `low` | Missing integrity checks on non-critical file downloads, parameter tampering on low-impact fields, autoescape disabled on safe content |

### Common CWE References

| CWE | Description |
|-----|-------------|
| CWE-89  | SQL Injection |
| CWE-78  | OS Command Injection |
| CWE-94  | Code Injection |
| CWE-352 | Cross-Site Request Forgery |
| CWE-502 | Deserialization of Untrusted Data |
| CWE-22  | Path Traversal |
| CWE-1321 | Prototype Pollution |
| CWE-113 | HTTP Response Splitting |
