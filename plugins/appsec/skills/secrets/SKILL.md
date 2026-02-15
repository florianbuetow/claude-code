---
name: secrets
description: >
  This skill should be used when the user asks to "check for secrets",
  "find hardcoded credentials", "scan for API keys", "detect leaked tokens",
  "find passwords in code", "check for committed .env files", "scan for
  private keys", or mentions "secrets", "credentials", "API keys", or
  "leaked tokens" in a security context. Also triggers for git history
  secret scanning and high-entropy string detection.
---

# Secrets Detection (SEC)

Analyze source code, configuration files, and git history for hardcoded
credentials, API keys, tokens, private keys, and other sensitive material
that should never appear in version control. Secrets in code are among the
most immediately exploitable vulnerabilities -- a single leaked API key can
lead to full account compromise within minutes.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key behaviors:

| Flag | Secrets-Specific Behavior |
|------|--------------------------|
| `--scope` | Default `changed`. Secrets analysis scans all file types including config, YAML, JSON, .env, scripts, and source code. |
| `--depth quick` | Scanners only (gitleaks/trufflehog), no manual pattern analysis. |
| `--depth standard` | Full file read of scoped files + Grep heuristics for patterns scanners miss. |
| `--depth deep` | Standard + scan git history for previously committed and removed secrets. |
| `--depth expert` | Deep + verify whether detected secrets are still active/valid, DREAD scoring. |
| `--severity` | Filter output. Most secrets findings are `critical` or `high`. |
| `--fix` | Generate remediation: remove secret, add to .gitignore, rotate credential. |

## Detection Patterns

Read `references/detection-patterns.md` for the full pattern catalog with
language-specific examples, regex heuristics, and false positive guidance.

**Pattern Summary**:
1. API keys and tokens hardcoded in source code
2. Passwords and credentials in configuration files
3. .env files committed to version control
4. Private keys (RSA, EC, PGP) in repository
5. Database connection strings with embedded credentials
6. High-entropy strings matching secret patterns

## Workflow

### Step 1: Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Include ALL file types -- secrets can appear anywhere: `.py`, `.js`, `.ts`,
   `.java`, `.go`, `.env`, `.yml`, `.yaml`, `.json`, `.xml`, `.toml`, `.ini`,
   `.cfg`, `.conf`, `.properties`, `.tf`, `.tfvars`, `.sh`, `.bash`, `.zsh`,
   `.dockerfile`, `docker-compose.*`, `*.pem`, `*.key`.
4. Check for `.gitignore` coverage of sensitive file patterns.

### Step 2: Check for Scanners

Detect available scanners in priority order:

| Scanner | Detect | Secrets Coverage |
|---------|--------|-----------------|
| gitleaks | `which gitleaks` | 150+ secret patterns, git history scanning, custom rules |
| trufflehog | `which trufflehog` | 700+ credential detectors, live verification of found secrets |
| trivy | `which trivy` | Secrets detection as part of broader filesystem scan |

Record which scanners are available and which are missing. If none are available,
note: "No scanner available -- findings based on code pattern analysis only."

### Step 3: Run Scanners

For each available scanner, run against the scoped files:

```
gitleaks detect --source <target> --report-format json --report-path /dev/stdout --no-banner
trufflehog filesystem --json <target>
```

At `--depth deep`, also scan git history:

```
gitleaks detect --source <target> --report-format json --report-path /dev/stdout --no-banner --log-opts="--all"
trufflehog git --json file://<target>
```

Normalize scanner output to the findings schema (see `../../shared/schemas/findings.md`).
Use the severity mapping from `../../shared/schemas/scanners.md`.

### Step 4: Claude Analysis

Read each scoped file and analyze for secret patterns not caught by scanners:

1. **Identify secret-like values**: Look for strings matching API key formats,
   base64-encoded credentials, high-entropy strings in assignment contexts.
2. **Check context**: Is the value in a variable named `key`, `secret`, `token`,
   `password`, `credential`, `api_key`, or similar?
3. **Verify not placeholder**: Exclude values like `YOUR_API_KEY_HERE`,
   `changeme`, `xxx`, `dummy`, `test`, `example`, `placeholder`.
4. **Check .gitignore**: Are `.env`, `*.pem`, `*.key`, `credentials.json`
   patterns in `.gitignore`? Flag missing patterns.
5. **Deduplicate**: Merge Claude findings with scanner findings.

At `--depth deep` or `--depth expert`:
- Trace secret usage across files to map exposure surface.
- Check if secrets are loaded from environment variables (good) vs hardcoded (bad).
- Verify secret rotation practices (key age, rotation infrastructure).

### Step 5: Report

Output findings using the format from `../../shared/schemas/findings.md`.

Each finding must include:
- **id**: `SEC-001`, `SEC-002`, etc.
- **title**: Secret type and location (e.g., "AWS access key in config.py").
- **severity**: Based on secret type, exposure scope, and verification status.
- **location**: File, line, and masked snippet (NEVER include the full secret).
- **description**: What type of secret was found and how it is exposed.
- **impact**: What an attacker can access with this secret.
- **fix**: Remove from code, add to .gitignore, rotate credential, use env vars.
- **references**: CWE-798, CWE-321, CWE-312.

**CRITICAL**: Never output the actual secret value in findings. Always mask
the middle portion: `AKIA****XMPL`.

## What to Look For

These are the primary secret patterns to detect. Each has detailed examples
and regex heuristics in `references/detection-patterns.md`.

1. **AWS access keys**: `AKIA[0-9A-Z]{16}` patterns in source code
2. **Generic API keys**: Long alphanumeric strings assigned to key/token variables
3. **Passwords in config**: `password = "..."`, `DB_PASSWORD`, connection strings
4. **Private keys**: `-----BEGIN RSA PRIVATE KEY-----` and similar PEM headers
5. **OAuth/JWT secrets**: Client secrets, signing keys, bearer tokens
6. **Cloud provider tokens**: GCP service account keys, Azure connection strings
7. **.env files committed**: Entire environment files with production secrets
8. **Git history secrets**: Secrets that were committed then "removed" but remain in history
9. **High-entropy strings**: Base64 or hex strings in suspicious contexts
10. **Connection strings**: Database URIs with embedded username:password

## Scanner Integration

**Primary**: gitleaks (fast, comprehensive pattern matching), trufflehog (live verification)
**Secondary**: trivy (secrets as part of broader scanning)
**Fallback**: Grep regex patterns from `references/detection-patterns.md`

When scanners are available, run them first and use Claude analysis to:
- Validate scanner findings (filter false positives like example values).
- Find secret patterns scanners miss (custom key formats, obfuscated secrets).
- Assess impact based on secret type and code context.

When no scanners are available, Claude performs full pattern-based analysis using
the Grep heuristics from `references/detection-patterns.md` and contextual code
reading. Report these findings with `confidence: medium`.

## Output Format

Use finding ID prefix **SEC** (e.g., `SEC-001`, `SEC-002`).

All findings follow the schema in `../../shared/schemas/findings.md` with:
- `references.cwe`: `"CWE-798"` (hardcoded credentials) or `"CWE-312"` (cleartext storage)
- `references.owasp`: `"A07:2021"` (Identification and Authentication Failures)
- `metadata.tool`: `"secrets"`
- `metadata.framework`: `"specialized"`
- `metadata.category`: `"SEC"`

**CWE Mapping by Secret Type**:

| Secret Type | CWE | Typical Severity |
|------------|-----|-----------------|
| Hardcoded password | CWE-798 | critical |
| API key in source | CWE-798 | critical |
| Private key committed | CWE-321 | critical |
| .env file committed | CWE-312 | high |
| Connection string with credentials | CWE-798 | critical |
| High-entropy string (unverified) | CWE-798 | medium |
| Missing .gitignore for secret files | CWE-312 | medium |

### Summary Table

After all findings, output a summary:

```
| Secret Type        | Critical | High | Medium | Low |
|--------------------|----------|------|--------|-----|
| API Keys/Tokens    |          |      |        |     |
| Passwords          |          |      |        |     |
| Private Keys       |          |      |        |     |
| Connection Strings |          |      |        |     |
| .env / Config      |          |      |        |     |
| Git History        |          |      |        |     |
```

Followed by: top 3 priorities, scanner coverage notes, rotation recommendations,
and overall assessment.
