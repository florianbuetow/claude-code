---
name: logging
description: >
  This skill should be used when the user asks to "check for logging issues",
  "analyze security logging", "find missing audit logs", "check for log injection",
  "audit monitoring configuration", or mentions "logging", "audit trail",
  "log injection", "monitoring", or "alerting" in a security context.
  Maps to OWASP Top 10 2021 A09: Security Logging and Monitoring Failures.
---

# Security Logging and Monitoring Failures (A09:2021)

Analyze source code for security logging and monitoring failures including missing
audit logging for security events, sensitive data in logs, log injection, absence
of alerting on failures, logs only stored locally, and missing tamper protection.

This is the most architectural OWASP category. Scanners provide minimal coverage
for logging failures, so Claude's analysis of code patterns, logging configuration,
and event coverage is the primary value of this skill.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks logging around security-critical operations
- `--depth deep` traces security event flows to verify each produces an audit log entry
- `--severity` filters output (logging gaps are often `medium`, sensitive data in logs is `high`)

## Framework Context

Read `../../shared/frameworks/owasp-top10-2021.md`, section **A09:2021 - Security
Logging and Monitoring Failures**, for the full category description, common
vulnerabilities, and prevention guidance.

Key CWEs in scope:
- CWE-117: Improper Output Neutralization for Logs (log injection)
- CWE-223: Omission of Security-Relevant Information
- CWE-532: Insertion of Sensitive Information into Log File
- CWE-778: Insufficient Logging
- CWE-779: Logging of Excessive Data

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain logging logic or security-critical operations:

- Authentication modules (`**/auth/**`, `**/login/**`, `**/session/**`)
- Access control and authorization (`**/middleware/**`, `**/guards/**`, `**/policies/**`)
- Logging configuration (`**/logging/**`, `**/logger/**`, `**/*log*config*`)
- Error handlers (`**/errors/**`, `**/exceptions/**`, `**/handlers/**`)
- Route/controller definitions (`**/routes/**`, `**/controllers/**`, `**/api/**`)
- Configuration files (`**/config/**`, `*.yaml`, `*.toml`, `*.ini`, `*.env*`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- can detect some log injection and sensitive data in logs
2. `bandit` -- Python-specific logging issues (e.g., sensitive data in debug logs)

Record which scanners are available and which are missing.
Note: scanner coverage for logging failures is limited. Claude analysis is the
primary detection mechanism for this category.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting logging patterns:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching log injection, sensitive data exposure in logs,
and logging configuration issues. Normalize output to the findings schema.

### 4. Claude Code Analysis

This is the primary analysis step for logging failures. Perform manual code analysis:

1. **Authentication event logging**: Find login, logout, failed login, password reset,
   and MFA flows. Verify each produces an audit log entry with user identity, timestamp,
   IP address, and outcome (success/failure).
2. **Access control failure logging**: Find authorization checks and verify that denied
   access attempts are logged with sufficient detail for investigation.
3. **Sensitive data in logs**: Grep for log statements and check that passwords, tokens,
   API keys, credit card numbers, SSNs, and other PII are not logged.
4. **Log injection**: Find log statements that include user-controlled input and verify
   the input is sanitized or the logging framework handles neutralization.
5. **Error handling**: Find catch/except blocks and verify they log the error rather
   than swallowing it silently.
6. **Logging configuration**: Check for centralized logging setup, structured log format,
   log level configuration, and whether logs are sent to a remote destination.
7. **Tamper protection**: For high-value audit trails, check for integrity controls
   (append-only storage, checksums, write-once destinations).

When `--depth deep`, additionally trace:
- Complete authentication flow from entry to audit log
- Exception propagation chains to verify no errors are silently dropped
- Logging pipeline from application code to destination (local file, remote service, SIEM)

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `LOG` prefix
(e.g., `LOG-001`, `LOG-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Impact description specific to the logging failure
- Concrete fix with diff when possible
- CWE and OWASP references

## What to Look For

These are the high-signal patterns specific to logging and monitoring failures. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **Missing authentication event logging** -- Login, failed login, logout, password
   reset, and MFA events that produce no audit log entry.

2. **Sensitive data in log statements** -- Passwords, tokens, API keys, credit card
   numbers, or PII written to logs, especially at DEBUG or INFO level.

3. **Log injection via user input** -- User-controlled strings passed directly into
   log format strings without sanitization, enabling log forgery or CRLF injection.

4. **Missing access control failure logging** -- Authorization denials that are not
   logged, making it impossible to detect brute-force or enumeration attacks.

5. **Silent error swallowing** -- Catch/except blocks with `pass`, empty bodies, or
   comments like "ignore" that discard errors without logging.

6. **No centralized logging configuration** -- Logging set up ad-hoc per file with
   no consistent format, level, or destination configuration.

7. **Logs stored only locally** -- Log output goes to local files or stdout with no
   forwarding to a centralized log management system.

8. **Missing alerting configuration** -- No evidence of alerting thresholds for
   security-critical events (repeated failed logins, privilege escalation attempts).

9. **Excessive logging of request/response bodies** -- Logging full HTTP bodies that
   may contain sensitive data without redaction.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | Log injection, sensitive data in debug logs | `semgrep scan --config auto --json --quiet <target>` |
| bandit | Python logging of sensitive data | `bandit -r <target> -f json -q` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find log statements with user input interpolation, catch blocks without logging,
authentication functions without log calls, and sensitive data patterns in log arguments.
Report findings with `confidence: medium`.

Scanner coverage for this category is inherently limited. Most logging failures are
architectural gaps (missing logging) rather than code-level bugs (present but incorrect
code), making Claude analysis the primary detection mechanism.

Relevant semgrep rule categories:
- `python.lang.security.audit.logging.*`
- `javascript.express.security.audit.logging.*`
- `java.lang.security.audit.logging.*`
- `generic.logging.security.*`

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `LOG` (e.g., `LOG-001`)
- **metadata.tool**: `logging`
- **metadata.framework**: `owasp`
- **metadata.category**: `A09`
- **references.owasp**: `A09:2021`
- **references.stride**: `R` (Repudiation)

Severity guidance for this category:
- **critical**: Sensitive data (passwords, tokens) logged in plaintext in production
- **high**: No audit logging for authentication events, log injection enabling log forgery
- **medium**: Silent error swallowing in security-critical paths, logs only stored locally
- **low**: Inconsistent log format, missing structured logging, minor gaps in non-critical logging
