---
name: fix
description: >
  This skill should be used when the user asks to "fix security finding",
  "fix vulnerability", "generate security fix", "appsec fix", "patch
  vulnerability", "remediate finding", or "apply security patch". Also
  triggers when the user references a finding ID (e.g., INJ-001) and asks
  for a fix, or points to a file:line and asks to fix the security issue
  there.
---

# Security Fix Generation

Generate concrete, production-ready code fixes for security findings. This
is not an advisory skill -- it produces actual code changes that resolve
vulnerabilities and offers to apply them via the Edit tool.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Fix Behavior |
|------|-------------|
| `--scope` | Identifies which findings to fix. `file:<path>` fixes findings in that file. Default: all unfixed findings in `--scope changed`. |
| `--depth quick` | Generate minimal fix (single-line change, no refactoring). |
| `--depth standard` | Fix with surrounding improvements (add validation, improve error handling). |
| `--depth deep` | Standard + refactor surrounding code to prevent similar issues, add defensive checks. |
| `--depth expert` | Deep + generate regression test, add security comments, update related code paths. |
| `--severity` | Only fix findings at or above this severity. |
| `--format` | Default `text`. Use `json` to output fix objects matching findings schema. |

## Workflow

### Step 1: Identify Target Finding

Resolve what to fix from user input. Accept any of these forms:

1. **Finding ID**: e.g., `INJ-001`. Read from `.appsec/findings.json` to load the finding.
2. **File and line**: e.g., `src/db/queries.ts:45`. Scan findings for a match, or analyze the location directly.
3. **Description**: e.g., "the SQL injection in the user lookup". Search findings by title/description.
4. **Batch mode**: No specific target means fix all findings in scope, ordered by severity (critical first).

If no findings exist in `.appsec/findings.json`, analyze the target location directly to identify the vulnerability before generating a fix.

### Step 2: Understand the Vulnerability

For each finding to fix:

1. **Read the finding record** (if it exists): severity, CWE, description, location, snippet.
2. **Read the vulnerable code**: Use the Read tool to load the file. Read at least 30 lines of surrounding context.
3. **Identify the root cause**: What specific coding pattern causes the vulnerability?
4. **Identify constraints**: What does the code need to do? What are the inputs/outputs? What framework/library is in use?
5. **Check for existing mitigations**: Is there partial validation? A security library already imported? Framework-level protection available?

### Step 3: Select Fix Strategy

Choose the most appropriate fix strategy based on the vulnerability type:

| Vulnerability | Preferred Fix Strategy |
|--------------|----------------------|
| SQL Injection (CWE-89) | Parameterized queries / prepared statements |
| XSS (CWE-79) | Context-aware output encoding, CSP headers |
| Command Injection (CWE-78) | Allowlist validation, avoid shell execution, use library APIs |
| Path Traversal (CWE-22) | Canonicalize + validate against base directory |
| SSRF (CWE-918) | URL allowlist, disable redirects, validate scheme/host |
| Insecure Deserialization (CWE-502) | Type-safe deserialization, allowlisted classes |
| Hardcoded Secrets (CWE-798) | Environment variables or secret manager references |
| Missing Auth (CWE-306) | Add authentication middleware/decorator |
| Broken Access Control (CWE-862) | Add authorization check before resource access |
| Weak Crypto (CWE-327) | Replace with current recommended algorithm |
| Open Redirect (CWE-601) | Validate redirect target against allowlist |
| Race Condition (CWE-362) | Add locking, use atomic operations |

### Step 4: Generate the Fix

Produce a concrete code change:

1. **Write the actual fixed code.** Not pseudocode, not advice -- real code that compiles/runs.
2. **Match the existing code style**: indentation, naming conventions, import style, error handling patterns.
3. **Use framework-idiomatic solutions**: If Express, use Express middleware. If Django, use Django's ORM parameterization. If React, use React's built-in XSS protection.
4. **Minimize blast radius**: Change only what is necessary. Do not refactor unrelated code (unless `--depth deep` or `expert`).
5. **Add imports** if the fix requires new dependencies. Note if a package install is needed.
6. **Preserve functionality**: The fix must not break the code's intended behavior.

### Step 5: Validate the Fix

Before presenting:

1. **Syntax check**: Ensure the generated code is syntactically valid.
2. **Completeness check**: Does the fix fully resolve the finding, or is it partial?
3. **Side effect check**: Could the fix break other functionality? Flag if so.
4. **Regression check**: Could the fix introduce a new vulnerability? (e.g., overly permissive allowlist).

### Step 6: Present and Apply

Present the fix to the user:

```
## Fix: <Finding ID> - <Title>

**Severity**: <severity> | **CWE**: <CWE-ID> | **File**: <path>

### Root Cause
<1-2 sentence explanation>

### Fix
<description of what the fix does>

```diff
- <old code>
+ <new code>
```

### Additional Changes (if any)
- New import: `<import statement>`
- New dependency: `<package>` (run `<install command>`)
```

Then ask: "Apply this fix?" If the user confirms (or `--fix` flag was passed from a parent skill), use the Edit tool to apply the change.

### Step 7: Update Finding Record

After applying a fix:

1. Update the finding in `.appsec/findings.json` with status `fix-applied`.
2. Add `fix.applied_at` timestamp and `fix.diff` with the actual change made.
3. Inform the user to run `/appsec:verify` to confirm the fix resolves the issue.

## Output Format

Findings follow `../../shared/schemas/findings.md`. When outputting fixes:

- `fix.summary`: One-line description of the fix.
- `fix.diff`: Unified diff of the change.
- `metadata.tool`: `"fix"`

Finding ID prefix: **FIX** (e.g., `FIX-001`) for new findings discovered during fix analysis. Fixes to existing findings retain the original finding ID.

## Pragmatism Notes

- Prefer the simplest correct fix. A one-line parameterized query beats a custom sanitization function.
- If a framework provides a built-in security mechanism, use it rather than hand-rolling.
- When multiple fix strategies exist, prefer the one already used elsewhere in the codebase for consistency.
- If the fix requires an architectural change beyond a single file, describe the full change but only apply the immediate file-level fix. Note the broader change needed.
- Never generate fixes that simply suppress warnings or disable security features.
- If unsure about a fix's correctness, present it with caveats rather than applying silently.
