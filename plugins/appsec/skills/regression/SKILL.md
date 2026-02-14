---
name: regression
description: >
  This skill should be used when the user asks to "check for regressions",
  "verify fixes still hold", "regression test security", "check for
  reintroduced vulnerabilities", "security regression check", or "verify
  no old bugs returned". Also triggers when the user wants to confirm
  that previously fixed vulnerabilities have not been reintroduced by
  recent code changes.
---

# Security Regression Detection

Verify that previously fixed vulnerabilities have not been reintroduced.
Reads the fix history from `.appsec/fixed-history.json`, checks
whether vulnerable patterns have returned or fixes have been removed, and
reports any regressions. Designed to run as a gate check before merges or
releases.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Regression Behavior |
|------|-------------------|
| `--scope` | Default `branch`. Checks regressions in all files changed on the current branch. Use `changed` for working tree only, `full` for all historical fixes. |
| `--depth quick` | Pattern match only: check if the exact vulnerable code snippet reappears. |
| `--depth standard` | Pattern match + semantic analysis: check if equivalent vulnerable patterns exist even if code changed. |
| `--depth deep` | Standard + trace data flows to verify fix integrity across refactored code. |
| `--depth expert` | Deep + attempt to bypass each fix with variant inputs and alternate code paths. |
| `--severity` | Only check regressions for findings at or above this severity. |
| `--format` | Default `text`. Use `json` for CI pipeline integration. |

## Workflow

### Step 1: Load Fix History

Read `.appsec/fixed-history.json`. This file contains all findings that have been verified as fixed by `/appsec:verify`. Each entry includes:

1. **Original finding**: Full finding object (ID, CWE, severity, location, description).
2. **Vulnerable snippet**: The original vulnerable code pattern.
3. **Fix applied**: The diff that resolved the vulnerability.
4. **Fixed location**: The file and line where the fix was applied.
5. **Verified timestamp**: When the fix was confirmed.

If the file does not exist or is empty, inform the user that no fix history is available and suggest running `/appsec:verify` on resolved findings to build the history.

### Step 2: Determine Check Scope

Resolve which files to check for regressions:

1. **Branch scope** (default): All files changed on the current branch vs main. Most useful for PR checks.
2. **Changed scope**: Only files with uncommitted changes. Useful during development.
3. **Full scope**: Check every file referenced in fix history. Most thorough, for release gates.

Intersect the scope file list with files referenced in fix history. Only check files that both (a) have historical fixes and (b) fall within scope. If scope includes files without fix history, skip them silently.

### Step 3: Check for Pattern Reintroduction

For each historical fix in scope, check whether the vulnerability has returned:

#### Quick Depth: Literal Pattern Match

1. Extract the original `vulnerable snippet` from the fix history.
2. Search for that exact snippet (or near-exact with whitespace normalization) in the current file.
3. If found at any location in the file, flag as potential regression.

#### Standard Depth: Semantic Analysis

1. Read the current code at and around the original fix location.
2. Analyze whether the fix is still intact:
   - Is the parameterized query still parameterized, or has someone reverted to string interpolation?
   - Is the auth middleware still in the middleware chain?
   - Is the input validation still present and applied before the dangerous operation?
3. Look for semantically equivalent vulnerable patterns even if the code has been refactored:
   - Same CWE pattern in different syntax.
   - Same vulnerability in a new function that handles similar input.
   - Copy-pasted code that duplicated the pre-fix version.

#### Deep Depth: Data Flow Verification

1. Trace the data flow from input to sink for each historical finding.
2. Verify that the fix (sanitization, validation, parameterization) is still in the path.
3. Check for new code paths that bypass the fix:
   - New routes that reach the same sink without the middleware.
   - Refactored code that calls the dangerous function directly.
   - New caller of a function that previously had the vulnerability.

#### Expert Depth: Fix Bypass Analysis

1. For each historical fix, attempt to construct a scenario where the fix is ineffective:
   - Input encoding that evades the validation.
   - Type confusion that bypasses the check.
   - Race condition that circumvents the guard.
2. Check if the fix's assumptions still hold given code changes.

### Step 4: Classify Results

For each historical fix checked, assign a status:

| Status | Meaning |
|--------|---------|
| **HOLDING** | Fix is intact. No regression detected. |
| **REGRESSION** | Vulnerable pattern has returned. The fix was reverted, removed, or bypassed. |
| **DEGRADED** | Fix is partially intact but weakened (e.g., validation is present but less strict). |
| **RELOCATED** | The fixed code was moved. Fix may be intact at new location but needs verification. |
| **INCONCLUSIVE** | Code changed significantly. Cannot determine if fix is still effective. Manual review needed. |

### Step 5: Report

Output the regression check results:

```
## Security Regression Report

### Summary
- Historical fixes checked: N
- Holding: N
- Regressions found: N
- Degraded: N
- Relocated: N
- Inconclusive: N

### Regressions

#### REGRESSION: INJ-001 - SQL injection in user lookup
**Original fix**: Parameterized query in src/db/queries.ts:45
**Current state**: String interpolation reintroduced at src/db/queries.ts:52
**Introduced by**: <commit hash if determinable>
**Severity**: CRITICAL -- This was a verified fix that has been undone.
**Action**: Re-apply parameterized query. Run `/appsec:fix INJ-001`.

#### DEGRADED: AC-003 - Missing rate limiting on login
**Original fix**: Added express-rate-limit middleware at 5 req/min
**Current state**: Rate limit increased to 1000 req/min (effectively disabled)
**Action**: Review rate limit configuration. 1000 req/min does not prevent brute force.

### Holding
- CRYPT-002: Weak hashing replaced with bcrypt -- Still intact
- AUTH-005: JWT validation added -- Still intact
- SSRF-001: URL allowlist implemented -- Still intact

### Inconclusive
- INJ-004: Code significantly refactored. Manual review recommended.
```

### Step 6: Emit Findings for Regressions

For each REGRESSION and DEGRADED result, emit a formal finding using `../../shared/schemas/findings.md`:

- Copy the original finding's details (CWE, severity, description).
- Update the location to the current file and line.
- Add `metadata.regression: true` to indicate this is a reintroduced vulnerability.
- Severity for regressions should be at least as high as the original, since this was a known and previously fixed issue.

Save regression findings to `.appsec/findings.json` with status `regression`.

## Output Format

Findings follow `../../shared/schemas/findings.md`.

Finding ID prefix: **REG** (e.g., `REG-001`).

- `metadata.tool`: `"regression"`
- `metadata.original_finding`: Reference to the original finding ID.

## Pragmatism Notes

- Not every code change near a fix location is a regression. Only flag when the actual vulnerability pattern returns.
- File renames and moves are common. Track by function name and pattern, not just file:line.
- If a fix was replaced with a better fix (e.g., switched from manual escaping to parameterized queries), that is HOLDING, not REGRESSION.
- Regressions in CRITICAL/HIGH findings should be treated as blocking for merge/release gates.
- When running in CI (detected by `--format json`), exit with a non-zero status indicator if regressions are found.
- If fix history is sparse (few entries), suggest the user build it up by running `/appsec:verify` on completed fixes.
