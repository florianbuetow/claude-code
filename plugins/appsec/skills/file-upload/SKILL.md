---
name: file-upload
description: >
  This skill should be used when the user asks to "check file upload security",
  "analyze upload validation", "find upload vulnerabilities", "check for zip
  slip", "audit file upload handling", or mentions "file upload", "upload
  validation", "content-type check", "magic bytes", "zip slip", or "path
  traversal in upload" in a security context.
---

# File Upload Security (UPLD)

Analyze source code for file upload vulnerabilities including client-only
validation, missing content-type verification, no magic byte checking, path
traversal in filenames, upload to webroot with execution, and zip slip
(archive extraction path traversal). Insecure file uploads can lead to remote
code execution, denial of service, and data exfiltration.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks upload handlers
- `--depth deep` traces file paths from upload through storage to serving
- `--severity` filters output (upload issues are often `critical` or `high`)

## Framework Context

Key CWEs in scope:
- CWE-434: Unrestricted Upload of File with Dangerous Type
- CWE-22: Improper Limitation of a Pathname to a Restricted Directory
- CWE-79: Cross-Site Scripting (via uploaded HTML/SVG)
- CWE-400: Uncontrolled Resource Consumption (via file size)
- CWE-611: Improper Restriction of XML External Entity Reference (via uploaded XML)

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain upload logic:

- Upload handlers (`**/upload/**`, `**/uploads/**`, `**/attachments/**`)
- File processing (`**/files/**`, `**/media/**`, `**/storage/**`)
- Multipart form handling (`**/middleware/**`, `**/controllers/**`)
- Archive extraction (`**/extract/**`, `**/unzip/**`, `**/import/**`)
- Frontend validation (`**/components/**`, `**/views/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for upload patterns
2. `bandit` -- Python file handling issues
3. `brakeman` -- Rails file upload vulnerabilities

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting upload security:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching file upload, path traversal, and content-type
patterns. Normalize output to the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **Client-only validation**: Find client-side file type checks (HTML `accept`
   attribute, JavaScript validation) without corresponding server-side checks.
2. **Content-type verification**: Check upload handlers verify Content-Type
   against an allowlist and do not trust the client-provided value alone.
3. **Magic byte validation**: Verify upload handlers check file magic bytes
   (file signatures) to confirm the file type matches the claimed type.
4. **Path traversal in filename**: Find places where the original filename is
   used in file path construction without sanitization.
5. **Upload to webroot**: Check whether uploaded files are stored in
   web-accessible directories where they could be executed.
6. **Archive extraction**: Find zip/tar extraction code and verify paths are
   validated to prevent directory traversal (zip slip).

When `--depth deep`, additionally trace:
- Full file path from upload to storage to serving
- File serving configuration (static file handlers, CDN configuration)
- Archive extraction to final storage location

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `UPLD` prefix
(e.g., `UPLD-001`, `UPLD-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Attack scenario (what malicious file could achieve)
- Concrete fix with diff when possible
- CWE and OWASP references

## What to Look For

These are the high-signal patterns specific to file upload security. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **Client-only file type validation** -- HTML `accept` attribute or JavaScript
   checks without server-side enforcement.

2. **Missing content-type verification** -- Upload handler accepts any file
   type or trusts the client-provided Content-Type header.

3. **No magic byte validation** -- File type determined solely by extension
   or Content-Type, not by reading the file header bytes.

4. **Path traversal in filename** -- Original filename used in path construction
   (e.g., `../../../etc/passwd`) without sanitization.

5. **Upload to executable directory** -- Files stored in webroot where a server
   could execute uploaded scripts (`.php`, `.jsp`, `.py`).

6. **Zip slip vulnerability** -- Archive extraction writes files outside the
   intended directory via `../` entries in archive member paths.

7. **Missing file size limit** -- No server-side limit on upload size, enabling
   denial of service via large files.

8. **Dangerous file types allowed** -- No blocklist for executable file types
   (`.exe`, `.sh`, `.php`, `.jsp`, `.py`).

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | Path traversal, unrestricted upload, zip slip | `semgrep scan --config auto --json --quiet <target>` |
| bandit | Python file handling, path traversal | `bandit -r <target> -f json -q` |
| brakeman | Rails file upload, content type | `brakeman -q -f json -o /dev/stdout` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find upload handlers, filename usage, archive extraction, and content-type
checks. Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `UPLD` (e.g., `UPLD-001`)
- **metadata.tool**: `file-upload`
- **metadata.framework**: `specialized`
- **metadata.category**: `UPLD`
- **references.cwe**: `CWE-434`, `CWE-22`
- **references.owasp**: `A04:2021` (Insecure Design)
- **references.stride**: `T` (Tampering) or `E` (Elevation of Privilege)

Severity guidance for this category:
- **critical**: Upload to webroot with execution, zip slip to sensitive directories, no validation at all
- **high**: Missing server-side type validation, path traversal in filename, dangerous types allowed
- **medium**: Client-only validation, missing magic bytes check, no file size limit
- **low**: Overly permissive allowlist, missing secondary validation layer
