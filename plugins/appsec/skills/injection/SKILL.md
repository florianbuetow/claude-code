---
name: injection
description: >
  This skill should be used when the user asks to "check for injection",
  "analyze SQL injection", "find injection vulnerabilities", "check for
  command injection", "find NoSQL injection", "check for LDAP injection",
  or mentions "injection" in a security context. Maps to OWASP Top 10
  2021 A03:2021 - Injection.
---

# Injection Analysis (OWASP A03:2021)

Analyze source code for injection vulnerabilities where user-supplied data flows
into interpreters without proper validation, sanitization, or parameterization.
This is the most code-scannable OWASP category -- most injection patterns leave
clear syntactic fingerprints in source code.

## Supported Flags

Read `shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key behaviors:

| Flag | Injection-Specific Behavior |
|------|-----------------------------|
| `--scope` | Default `changed`. Injection analysis focuses on files containing database queries, system calls, LDAP operations, and eval constructs. |
| `--depth quick` | Scanners + Grep patterns only, no data-flow tracing. |
| `--depth standard` | Full code read of scoped files, local data-flow analysis within each file. |
| `--depth deep` | Trace user input from HTTP entry points through call chains to sinks. Cross-file taint analysis. |
| `--depth expert` | Deep + red team simulation: craft proof-of-concept payloads, DREAD scoring. |
| `--severity` | Filter output. Injection findings are typically `critical` or `high`. |
| `--fix` | Generate parameterized replacements for each finding. |

## Framework Context

**OWASP A03:2021 - Injection**

User-supplied data is not validated, filtered, or sanitized by the application.
Dynamic queries or commands are constructed using string concatenation or
interpolation with hostile data. Common injection types:

- **SQL Injection** (CWE-89): Unsanitized input in SQL queries
- **NoSQL Injection** (CWE-943): Unsanitized input in MongoDB/NoSQL queries
- **OS Command Injection** (CWE-78): User input passed to system shell commands
- **LDAP Injection** (CWE-90): Unsanitized input in LDAP queries
- **Expression Language Injection** (CWE-917): User input in EL/template engines
- **ORM Injection** (CWE-89): Raw queries or unsafe ORM usage with user input

**STRIDE Mapping**: Tampering, Information Disclosure, Elevation of Privilege

## Detection Patterns

Read `references/detection-patterns.md` for the full pattern catalog with
language-specific examples, regex heuristics, and false positive guidance.

**Pattern Summary**:
1. String concatenation in SQL queries
2. Template string / f-string SQL construction
3. Raw ORM queries with user input
4. `os.system` / `exec` / `subprocess` with user input
5. `eval()` / `Function()` with user input
6. LDAP query string construction with user input

## Workflow

### Step 1: Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Filter to relevant file types: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`,
   `.go`, `.rb`, `.php`, `.cs`, `.rs`, `.kt`, `.scala`, `.sql`, `.graphql`.
4. Prioritize files containing: database query patterns, HTTP handler functions,
   system call imports, LDAP library usage, eval/exec constructs.

### Step 2: Check for Scanners

Detect available scanners in priority order:

| Scanner | Detect | Injection Coverage |
|---------|--------|--------------------|
| semgrep | `which semgrep` | SQL, NoSQL, OS command, LDAP, EL, ORM -- broadest coverage |
| bandit | `which bandit` | Python: eval, exec, SQL, subprocess, pickle |
| gosec | `which gosec` | Go: SQL injection, command injection |
| brakeman | `which brakeman` | Rails: SQL injection, command injection, mass assignment |
| spotbugs | Maven/Gradle plugin | Java: SQL injection, command injection, XXE, LDAP |

Record which scanners are available and which are missing. If none are available,
note: "No scanner available -- findings based on code pattern analysis only."

### Step 3: Run Scanners

For each available scanner, run against the scoped files:

```
semgrep scan --config auto --json --quiet <target>
bandit -r <target> -f json -q
gosec -fmt json ./...
```

Normalize scanner output to the findings schema (see `shared/schemas/findings.md`).
Use the severity mapping from `shared/schemas/scanners.md`.

### Step 4: Claude Analysis

Read each scoped file and analyze for injection patterns not caught by scanners:

1. **Identify sinks**: Database query functions, system calls, LDAP operations,
   eval/exec, template engines.
2. **Trace sources**: HTTP request parameters, form data, URL path segments,
   headers, cookies, file uploads, environment variables from user input.
3. **Check sanitization**: Is there parameterization, input validation,
   allowlisting, or escaping between source and sink?
4. **Assess context**: Is the code reachable from an external entry point?
   Is there framework-level protection (e.g., Django ORM, prepared statements)?
5. **Deduplicate**: Merge Claude findings with scanner findings. If both found
   the same issue, keep the scanner finding and add Claude's context.

At `--depth deep` or `--depth expert`, trace data flow across files:
- Follow function calls from HTTP handlers to database/system call sites.
- Check middleware and interceptors for global sanitization.
- Map the full taint path: source -> transforms -> sink.

### Step 5: Report

Output findings using the format from `shared/schemas/findings.md`.

Each finding must include:
- **id**: `INJ-001`, `INJ-002`, etc.
- **title**: Concise description of the injection type and location.
- **severity**: Based on exploitability, authentication requirements, and impact.
- **location**: File, line, function, and vulnerable code snippet.
- **description**: What is vulnerable and why.
- **impact**: What an attacker can achieve.
- **fix**: Parameterized/safe replacement code.
- **references**: CWE, OWASP A03:2021, STRIDE mapping.

## What to Look For

These are the primary injection patterns to detect. Each has detailed examples
and regex heuristics in `references/detection-patterns.md`.

1. **String concatenation in SQL**: `"SELECT * FROM users WHERE id = " + userId`
2. **Template literals in SQL**: `` `SELECT * FROM users WHERE id = ${userId}` ``
3. **F-strings / format strings in SQL**: `f"SELECT * FROM users WHERE id = {user_id}"`
4. **Raw ORM queries**: `Model.objects.raw(user_input)`, `sequelize.query(userInput)`
5. **OS command construction**: `os.system("ping " + host)`, `exec("ls " + dir)`
6. **subprocess with shell=True**: `subprocess.call(cmd, shell=True)` where `cmd` includes user input
7. **eval/exec with user input**: `eval(request.body)`, `new Function(userCode)()`
8. **LDAP filter construction**: `"(uid=" + username + ")"` without escaping
9. **NoSQL operator injection**: `db.users.find({username: req.body.username})` where body can contain `$gt`, `$ne`
10. **Stored procedures with concatenation**: Dynamic SQL inside stored procedures

## Scanner Integration

**Primary**: semgrep (broadest injection coverage across languages)
**Language-specific**: bandit (Python), gosec (Go), brakeman (Rails), spotbugs (Java)
**Fallback**: Grep regex patterns from `references/detection-patterns.md`

When scanners are available, run them first and use Claude analysis to:
- Validate scanner findings (reduce false positives).
- Find injection patterns scanners miss (complex data flows, indirect concatenation).
- Provide fix suggestions with parameterized replacements.

When no scanners are available, Claude performs full pattern-based analysis using
the Grep heuristics from `references/detection-patterns.md` and contextual code
reading. Report these findings with `confidence: medium`.

## Output Format

Use finding ID prefix **INJ** (e.g., `INJ-001`, `INJ-002`).

All findings follow the schema in `shared/schemas/findings.md` with:
- `references.owasp`: `"A03:2021"`
- `references.stride`: `"T"` (Tampering), `"I"` (Info Disclosure), or `"E"` (Elevation of Privilege)
- `metadata.tool`: `"injection"`
- `metadata.framework`: `"owasp"`
- `metadata.category`: `"A03"`

**CWE Mapping by Injection Type**:

| Injection Type | CWE | Typical Severity |
|---------------|-----|-----------------|
| SQL Injection | CWE-89 | critical |
| OS Command Injection | CWE-78 | critical |
| NoSQL Injection | CWE-943 | high |
| LDAP Injection | CWE-90 | high |
| Expression Language Injection | CWE-917 | high |
| ORM Injection (raw queries) | CWE-89 | high |
| eval/exec Injection | CWE-95 | critical |

### Summary Table

After all findings, output a summary:

```
| Injection Type | Critical | High | Medium | Low |
|---------------|----------|------|--------|-----|
| SQL            |          |      |        |     |
| OS Command     |          |      |        |     |
| NoSQL          |          |      |        |     |
| eval/exec      |          |      |        |     |
| LDAP           |          |      |        |     |
| ORM            |          |      |        |     |
```

Followed by: top 3 priorities, scanner coverage notes, and overall assessment.
