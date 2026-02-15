---
name: sans25
description: >
  This skill should be used when the user asks to "check CWE Top 25",
  "run SANS analysis", "check for common weaknesses", or mentions
  "CWE" or "SANS Top 25" in a security context. Checks code against
  the SANS/CWE Top 25 Most Dangerous Software Weaknesses.
---

# SANS/CWE Top 25 Dispatcher

Analyze scoped code directly against the SANS/CWE Top 25 Most Dangerous
Software Weaknesses (2024). Unlike the OWASP and STRIDE dispatchers, this
skill does NOT dispatch individual subagents per category. Instead it reads
the full framework reference, determines which CWEs are relevant to the
scoped code based on languages and patterns, checks each applicable CWE
directly, groups findings by CWE category, and cross-references with OWASP
and STRIDE mappings.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the
full flag specification. This dispatcher supports all cross-cutting flags.

| Flag | Dispatcher-Specific Behavior |
|------|------------------------------|
| `--scope` | Determines which files to analyze. Default `changed`. |
| `--depth` | Controls analysis thoroughness. Default `standard`. |
| `--severity` | Applied after analysis to filter output. |
| `--format` | Applied to final output. |
| `--only CWE-89,CWE-79` | Check only the listed CWEs. Accepts comma-separated CWE identifiers (e.g., `CWE-89`, `CWE-787`, `CWE-22`). Unlisted CWEs are skipped entirely. |
| `--fix` | Produce fix suggestions inline for each finding. |
| `--quiet` | Findings only, suppress explanations. |
| `--explain` | Add learning material per finding. |

## Framework Reference

Read [`../../shared/frameworks/sans-cwe-top25.md`](../../shared/frameworks/sans-cwe-top25.md)
for the full SANS/CWE Top 25 specification including weakness descriptions,
code-level indicators, severity ratings, and cross-framework mapping tables.

## Workflow

### Step 1: Resolve Scope

Parse the `--scope` flag and resolve to a concrete file list. Use Git
commands or Glob as appropriate for the scope type. Record the resolved
file list for use in subsequent steps.

### Step 2: Detect Languages and Technology Stack

Scan the scoped files to identify:
- **Languages**: file extensions (`.c`, `.cpp`, `.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`, `.php`, `.rs`, etc.)
- **Frameworks**: imports and config files (Express, Django, Flask, Spring, Rails, ASP.NET, etc.)
- **Data layer**: database libraries, ORM usage, raw query patterns
- **Infrastructure**: Dockerfiles, deployment manifests, CI/CD config

This determines which CWEs are applicable. Record a `language_profile`
summarizing what was detected.

### Step 3: Determine Applicable CWEs

Using the `language_profile`, filter the 25 CWEs to those relevant for this
codebase. Each CWE category has language-specific applicability:

| Category | CWEs | Applicable When |
|----------|------|-----------------|
| Memory Safety | CWE-787, CWE-125, CWE-416, CWE-476, CWE-190, CWE-119 | C, C++, Rust (unsafe blocks), or any code with FFI/native bindings |
| Injection | CWE-79, CWE-89, CWE-78, CWE-94, CWE-77 | Any language with user input handling, database queries, shell execution, or template rendering |
| Auth/AuthZ | CWE-862, CWE-863, CWE-306, CWE-287 | Any code with authentication, authorization, session management, or API endpoints |
| Data Handling | CWE-20, CWE-22, CWE-502, CWE-918, CWE-352, CWE-434, CWE-362 | Any code handling user input, files, URLs, serialization, or concurrent access |
| Configuration | CWE-798, CWE-276, CWE-269 | Any code with credentials, permissions, privilege management, or deployment config |

If `--only` is specified, skip the relevance check and analyze only the
listed CWEs.

**Memory safety skip rule**: If no C, C++, Rust, or native binding code
is present, skip the entire Memory Safety category and record the skip
reason. Do NOT report memory safety CWEs for pure Python, JavaScript,
Java, Go, or Ruby codebases.

### Step 4: Analyze Each Applicable CWE

For each applicable CWE, read its section in `sans-cwe-top25.md` and check
the scoped code against the documented code-level indicators.

For each CWE, perform the following:

1. **Pattern scan**: Use Grep to search for the code-level indicators
   listed in the framework reference. For example, for CWE-89 (SQL
   Injection), search for string concatenation in SQL queries, `f"SELECT`,
   raw query methods, and dynamic table/column names.

2. **Context analysis**: Read the surrounding code for each pattern match.
   Determine whether the match is a true positive or a false positive.
   Consider:
   - Is user input actually reaching this code path?
   - Are there existing mitigations (parameterized queries, input validation, encoding)?
   - Is the pattern in test code, comments, or dead code?

3. **Severity assessment**: Assign severity based on the CWE's documented
   severity rating, adjusted for context:
   - Upgrade if the code is in a critical path (auth, payment, PII handling).
   - Downgrade if existing mitigations partially address the weakness.

4. **Create finding**: For each confirmed weakness, create a finding
   object following the schema in `shared/schemas/findings.md`. Set:
   - `id`: `CWE<NNN>-<SEQ>` (e.g., `CWE89-001`, `CWE787-002`)
   - `references.cwe`: The CWE identifier
   - `references.sans_cwe25`: The rank (1-25)
   - `metadata.framework`: `"sans25"`
   - `metadata.category`: The CWE category group (e.g., `"injection"`, `"memory-safety"`, `"auth"`, `"data-handling"`, `"config"`)

If `--depth deep` or `--depth expert`, additionally:
- Trace data flows from user input to the vulnerable code point.
- Follow imports and cross-file calls to confirm reachability.
- Check for defense-in-depth layers that might mitigate the weakness.

### Step 5: Group Findings by Category

Organize confirmed findings into the five CWE category groups:

| Group | ID | CWEs Covered |
|-------|----|-------------|
| Memory Safety | `memory-safety` | CWE-787, CWE-125, CWE-416, CWE-476, CWE-190, CWE-119 |
| Injection | `injection` | CWE-79, CWE-89, CWE-78, CWE-94, CWE-77 |
| Auth/AuthZ | `auth` | CWE-862, CWE-863, CWE-306, CWE-287 |
| Data Handling | `data-handling` | CWE-20, CWE-22, CWE-502, CWE-918, CWE-352, CWE-434, CWE-362 |
| Configuration | `config` | CWE-798, CWE-276, CWE-269 |

Within each group, sort findings by CWE rank (lower rank = more dangerous).

### Step 6: Cross-Reference with Other Frameworks

For each finding, populate cross-framework references using the mapping
table in `sans-cwe-top25.md`:

- `references.owasp`: Map to the OWASP Top 10 category (e.g., CWE-89 maps to `A03:2021`).
- `references.stride`: Map to STRIDE category letters (e.g., CWE-89 maps to `T, I, E`).
- `references.mitre_attck`: Map to ATT&CK technique IDs (e.g., CWE-89 maps to `T1190, T1059`).

Use the "Cross-Framework Mapping Table" section in the framework reference
as the authoritative source for these mappings.

### Step 7: Deduplicate

Two findings are duplicates if they share the same `location.file` AND
`location.line` (or overlapping line ranges) AND refer to the same or
parent/child CWE. When duplicates exist:
- Keep the finding with the higher-ranked CWE (lower rank number).
- Merge CWE references into the retained finding.
- Note the duplicate in the retained finding's description.

### Step 8: Rank and Filter

Sort all findings: critical > high > medium > low. Within the same
severity, sort by CWE rank (lower rank first), then by confidence
(high > medium > low).

Apply the `--severity` filter to exclude findings below the threshold.

### Step 9: Produce Output

Wrap findings in the aggregate output format from `shared/schemas/findings.md`:

```json
{
  "tool": "sans25",
  "scope": "{SCOPE}",
  "depth": "{DEPTH}",
  "language_profile": ["python", "javascript"],
  "categories_checked": ["injection", "auth", "data-handling", "config"],
  "categories_skipped": ["memory-safety"],
  "skip_reason": "No C/C++/Rust or native bindings detected",
  "total_findings": 7,
  "by_severity": { "critical": 2, "high": 3, "medium": 1, "low": 1 },
  "by_cwe_group": {
    "injection": 3,
    "auth": 2,
    "data-handling": 1,
    "config": 1
  },
  "findings": [ ... ]
}
```

### Step 10: Present Results

Output the report in the requested `--format`. Include:

- **Language profile**: detected languages and technologies.
- **Coverage table**: which CWE groups were checked and which were skipped (with reasons).
- **CWE group breakdown**: finding count per group.
- **Severity breakdown**: count by critical/high/medium/low.
- **Findings list**: in severity order, grouped by CWE category.
- **Cross-framework summary**: for each finding, show the OWASP, STRIDE,
  and ATT&CK mappings so the finding can be located in other framework
  reports.

## Expert Mode

If `--depth expert` is set, after the main analysis:

1. Read [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md)
   for DREAD scoring criteria. Assign a DREAD score to each finding.

2. Identify CWE chains -- combinations of weaknesses that amplify each
   other. For example:
   - CWE-20 (Improper Input Validation) + CWE-89 (SQL Injection): missing
     validation enables injection.
   - CWE-306 (Missing Authentication) + CWE-862 (Missing Authorization):
     unauthenticated access to unprotected resources.
   - CWE-798 (Hard-coded Credentials) + CWE-287 (Improper Authentication):
     attacker uses leaked credentials to bypass auth.

3. For each chain, describe the combined attack scenario and assign an
   aggregate severity reflecting the chained impact.

4. Append chain findings with prefix `CHAIN` and `metadata.tool` set to
   `"cwe-chain"`.
