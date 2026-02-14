---
name: verify
description: >
  This skill should be used when the user asks to "verify fix", "confirm
  fix", "check if vulnerability is fixed", "validate remediation",
  "recheck finding", or "test if patch works". Also triggers when the user
  has applied a security fix and wants confirmation that the vulnerability
  is actually resolved, or when referencing a finding ID and asking if it
  is still present.
---

# Fix Verification

Confirm that a security fix actually resolves the reported vulnerability.
Re-runs the specific check -- scanner rule or Claude analysis -- that
originally detected the issue. Outputs a clear verdict: FIXED or STILL
VULNERABLE with explanation. Updates the finding record in `.appsec/findings/`.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Verify Behavior |
|------|----------------|
| `--scope` | Identifies which findings to verify. Default: all findings with status `fix-applied` in scope. |
| `--depth quick` | Check only the exact location referenced in the finding. |
| `--depth standard` | Check the location + immediate callers and related code paths. |
| `--depth deep` | Standard + verify no variant of the vulnerability was introduced nearby. |
| `--depth expert` | Deep + attempt to construct a proof-of-concept that bypasses the fix. |
| `--severity` | Only verify findings at or above this severity. |
| `--format` | Default `text`. Use `json` for structured verification results. |

## Workflow

### Step 1: Identify Findings to Verify

Resolve which findings need verification:

1. **By finding ID**: User provides e.g., `INJ-001`. Load from `.appsec/findings/`.
2. **By status**: Find all findings with status `fix-applied` that have not yet been verified.
3. **By scope**: Find all findings whose `location.file` falls within the resolved scope.
4. **All pending**: If no specific target, verify all `fix-applied` findings.

If no findings match, inform the user. If findings exist but none have `fix-applied` status, suggest running `/appsec:fix` first.

### Step 2: Load Finding Context

For each finding to verify:

1. **Read the finding record**: Original vulnerability details, CWE, location, snippet.
2. **Read the fix record**: What was changed (the diff), when it was applied.
3. **Read the current code**: Load the file at the finding's location using the Read tool.
4. **Determine the original detection method**: Was it found by a scanner (check `scanner.name`) or by Claude analysis?

### Step 3: Re-Run Detection

Apply the same detection method that found the original vulnerability:

#### Scanner-Detected Findings

If `scanner.name` is present and the scanner is available:

1. Run the specific scanner rule against the fixed file.
2. If the scanner no longer reports the finding at that location, mark as FIXED.
3. If the scanner still reports, mark as STILL VULNERABLE with scanner output.

#### Claude-Detected Findings

If the finding was detected by Claude analysis (no scanner, or scanner not available):

1. Re-read the code at the finding location with full context.
2. Apply the same analysis that detected the original vulnerability:
   - Is the vulnerable pattern still present?
   - Is user input still reaching the dangerous sink without sanitization?
   - Is the missing security control still missing?
3. Check that the fix is correct and complete:
   - Does the fix use the right mitigation for this vulnerability type?
   - Are there edge cases the fix misses (e.g., alternate code paths, encoding bypasses)?
   - Is the fix applied to all instances of the pattern, not just one?

### Step 4: Check for Fix Bypasses

At `--depth deep` and above, look for ways the fix might be circumvented:

1. **Alternate code paths**: Is there another route to the same sink that bypasses the fix?
2. **Encoding bypasses**: Can the input be encoded to evade the validation (double encoding, unicode, null bytes)?
3. **Type confusion**: Can the input type be changed to bypass validation (array instead of string)?
4. **Race conditions**: Can the check be bypassed via TOCTOU?
5. **Partial fix**: Does the fix cover all variants of the vulnerability?

### Step 5: Render Verdict

For each finding, output one of two verdicts:

#### FIXED

```
## FIXED: <Finding ID> - <Title>

**Status**: FIXED
**Verified at**: <timestamp>
**Method**: <scanner re-run | code analysis>

The vulnerability at `<file>:<line>` has been resolved.

**What changed**: <1-2 sentence summary of the fix>
**Confidence**: <high|medium> -- <why>
```

#### STILL VULNERABLE

```
## STILL VULNERABLE: <Finding ID> - <Title>

**Status**: STILL VULNERABLE
**Verified at**: <timestamp>
**Method**: <scanner re-run | code analysis>

The vulnerability at `<file>:<line>` has NOT been resolved.

**Reason**: <specific explanation of why the fix is insufficient>
**Remaining issue**: <what still needs to change>
**Suggestion**: <concrete next step to actually fix it>
```

### Step 6: Update Finding Records

Update each finding in `.appsec/findings/`:

- **FIXED**: Set status to `verified-fixed`. Add `verified_at` timestamp and `verification.method`.
- **STILL VULNERABLE**: Set status to `fix-failed`. Add `verification.reason` explaining why. Preserve the original finding so `/appsec:fix` can be re-run.

Copy verified-fixed findings to `.appsec/findings/fixed-history.json` for regression tracking (used by `/appsec:regression`).

### Step 7: Summary

After verifying all targeted findings, output a summary:

```
## Verification Summary

| Finding | Status | Confidence |
|---------|--------|------------|
| INJ-001 | FIXED | High |
| AC-003  | STILL VULNERABLE | High |

Verified: N/M findings fixed. N still require remediation.
```

## Output Format

Verification results reference the original finding but add verification metadata.

- `metadata.tool`: `"verify"`
- Original finding ID is preserved (not re-prefixed).

Finding ID prefix: **VER** (e.g., `VER-001`) only for new issues discovered during verification (e.g., the fix introduced a different vulnerability).

Findings follow `../../shared/schemas/findings.md`.

## Pragmatism Notes

- A finding is FIXED when the specific vulnerable pattern is resolved. Do not fail verification because of unrelated issues in the same file.
- Scanner re-runs are the strongest evidence. If the scanner that originally detected the issue no longer flags it, that is high-confidence FIXED.
- Claude analysis verification is medium-confidence by default. Note this in the output.
- If the fix moved the vulnerable code rather than resolving it, mark as STILL VULNERABLE and note the new location.
- If the entire function or file was deleted, verify the functionality was actually removed and not relocated. If truly removed, mark as FIXED.
- Do not penalize fixes that use a different mitigation strategy than suggested, as long as the vulnerability is resolved.
