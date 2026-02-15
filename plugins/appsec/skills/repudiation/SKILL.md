---
name: repudiation
description: >
  This skill should be used when the user asks to "check for repudiation",
  "analyze audit logging", "find logging gaps", or mentions "repudiation"
  or "non-repudiation" in a security context. Maps to STRIDE category R.
---

# Repudiation Analysis

Analyze source code for repudiation threats where users can deny having performed actions due to insufficient logging and evidence. Maps to **STRIDE R** -- violations of the **Non-repudiation** security property.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full flag specification. This skill supports all cross-cutting flags including `--scope`, `--depth`, `--severity`, `--format`, `--fix`, `--quiet`, and `--explain`.

## Framework Context

Read [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md), specifically the **R - Repudiation** section, for the threat model backing this analysis. Key concerns: missing audit logs, log tampering, log injection, insufficient logging detail, log deletion.

## Workflow

### 1. Determine Scope

Parse flags and resolve the target file list per the flags spec. Prioritize files containing security-critical operations:

- Authentication handlers (login, logout, password reset, MFA enrollment)
- Payment processing and financial transaction handlers
- Admin actions and user management endpoints
- Data modification endpoints (create, update, delete on sensitive resources)
- Access control decision points (grant/deny/escalate)
- File upload and download handlers
- The logging infrastructure itself (logger configuration, log sinks, formatters)

### 2. Analyze for Repudiation Threats

For each in-scope file, apply the Analysis Checklist below. At `--depth standard`, check each file for logging around critical actions. At `--depth deep`, trace the full lifecycle of security events to confirm they are captured end-to-end with sufficient detail, and verify log shipping and tamper protection.

### 3. Report Findings

Output findings per [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md) using the `REPUD` ID prefix (e.g., `REPUD-001`). Set `references.stride` to `"R"` on every finding.

## Analysis Checklist

Work through these questions against the scoped code. Each "yes" may produce a finding.

1. **Missing audit logs on auth events** -- Are login successes, login failures, logout, password changes, and MFA events logged with user identity and timestamp? Search for auth handlers that lack logging calls. Auth failures are especially critical -- they indicate attack attempts.
2. **Unlogged data modifications** -- Are CREATE, UPDATE, and DELETE operations on sensitive data logged? Check ORM hooks, repository methods, and direct database calls for audit trail gaps. Look for model lifecycle callbacks (e.g., `after_save`, `post_save`) that should emit audit events but are absent.
3. **Missing actor identity in logs** -- Do log entries include who performed the action (user ID, session ID, IP address), or do they only record what happened? Search for `log.info`, `logger.warn` calls near critical operations and check if user context is passed as structured metadata.
4. **Log injection vulnerability** -- Can user input be written into log entries unsanitized? Look for user-controlled strings (usernames, query params, form data) passed directly into log formatters, which could inject fake log entries, break log parsing, or enable CRLF injection. Check: `logger.info(f"User {username}")` without sanitization.
5. **Log tampering exposure** -- Are logs written to locations the application can also delete or modify? Check if log files are stored in application-writable directories without append-only flags (`chattr +a`), write-once storage, or external forwarding to a SIEM/log aggregator.
6. **Missing failure logging** -- Are authorization denials, validation failures, rate limit hits, and error conditions logged? Look for `catch` blocks, `403`/`401` responses, and validation rejection paths that silently discard the event without recording what was attempted and by whom.
7. **No transaction evidence** -- Do financial or legally significant operations produce tamper-evident records? Check for digital signatures, sequence numbers, or immutable audit entries on payment, consent, or contract events. Are transaction IDs generated server-side and logged?
8. **Timestamp integrity** -- Are log timestamps generated server-side from a trusted clock, or can clients supply their own? Look for client-provided timestamps accepted without validation on audit records. Check for NTP configuration or trusted time sources in infrastructure code.
9. **Insufficient log detail** -- Do logs capture enough context for forensic reconstruction? Check for: before/after values on updates, affected resource IDs, request metadata (IP, user agent, request ID). Sparse `"action completed"` entries without context are a forensic gap.
10. **Missing centralized aggregation** -- Are logs only stored locally on application servers where they can be lost during incidents or rotation? Check for log shipping configuration to external systems: SIEM, ELK, CloudWatch, Datadog, Splunk, or equivalent.
11. **Log retention policy gaps** -- Is there a defined retention period, or could logs be rotated away before they are needed for incident response? Check log rotation config (`logrotate`, `maxFiles`, `maxSize`) and whether retention aligns with compliance requirements.
12. **Selective logging gaps** -- Are some code paths logged while equivalent paths are not? For example, if `createUser` logs but `deleteUser` does not, or if admin actions are logged but equivalent API actions are not. Look for asymmetric coverage across related handlers.

## Pragmatism Notes

- Small internal tools and prototypes may not need comprehensive audit logging. Scale expectations to the application's threat model and regulatory context.
- The presence of a logging framework does not mean critical actions are logged. Verify that security-relevant events specifically have log calls, not just general application logging.
- Log injection severity depends on the log consumer. If logs feed a SIEM with automated alerting, injecting fake entries is high severity. If logs are only read by humans in text files, it is medium.
- Centralized log aggregation is an infrastructure concern. If the codebase is application-only with no infrastructure code, note the gap but do not rate it above `low`.
- Distinguish between application logs (general debugging) and audit logs (security evidence). The absence of audit-specific infrastructure is a stronger finding than missing debug logs.

## What to Look For

Concrete code patterns and grep heuristics to surface repudiation risks:

- **Auth handlers without logging**: Functions matching `login`, `authenticate`, `signIn`, `register`, `resetPassword`, `changePassword` that do not contain calls to `log`, `logger`, `audit`, `emit`, or `track`. Grep: `(login|signIn|authenticate|register)` then verify adjacent logging.
- **CRUD without audit**: Database operations (`save()`, `.create(`, `.update(`, `.delete(`, `INSERT`, `UPDATE`, `DELETE`) in handlers with no adjacent logging call within 5-10 lines. Grep: `\.(save|create|update|delete|destroy)\(` and check surrounding context.
- **Raw user input in logs**: `logger.info(f"User {username}")`, `console.log(req.body)`, `log.info("Query: " + userInput)` -- any pattern where unsanitized input flows into log formatting. Grep: `log\w*\.(info|warn|error|debug)\(.*req\.(body|params|query|headers)`.
- **Catch blocks that swallow**: `except Exception: pass`, `catch (e) {}`, `catch (e) { return; }`, `.catch(() => {})` -- error handlers with no logging. Grep: `catch.*\{\s*\}|except.*:\s*pass`.
- **Local-only log config**: Log configuration writing only to `file://`, `./logs/`, or stdout without forwarding. Absence of log shipping libraries (`winston-transport`, `fluent-logger`, `logstash`, `sentry`, `@google-cloud/logging`).
- **Missing before/after values**: Update operations that log `"record updated"` without capturing the previous and new state. Check for absence of `old_value`, `previous`, `before`, `diff` in log payloads near update handlers.
- **No request correlation**: Absence of request ID or correlation ID in logs, making it impossible to trace a single user action across multiple log entries. Search for `requestId`, `correlationId`, `traceId`, `x-request-id` in logging middleware.

## Output Format

Each finding must conform to [`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

```
id:          REPUD-<NNN>
severity:    critical | high | medium | low
confidence:  high | medium | low
location:    file, line, function, snippet
description: What the repudiation risk is and what actions can be denied
impact:      What accountability is lost and what forensic gaps result
fix:         Concrete remediation with diff when possible
references:
  stride: "R"
  cwe:    CWE-778 (Insufficient Logging), CWE-117 (Log Injection), or relevant CWE
metadata:
  tool:      repudiation
  framework: stride
  category:  R
```

### Severity Guidelines for Repudiation

| Severity | Criteria |
|----------|----------|
| `critical` | No audit logging on financial transactions or authentication events, log injection enabling forged audit entries |
| `high` | Missing logging on data modification endpoints, log files writable/deletable by application without tamper protection |
| `medium` | Insufficient detail in audit logs (missing actor/resource IDs), swallowed exceptions on security-relevant paths |
| `low` | Local-only log storage without forwarding, missing before/after values on low-impact updates, no request correlation IDs |

### Common CWE References

| CWE | Description |
|-----|-------------|
| CWE-778 | Insufficient Logging |
| CWE-117 | Improper Output Neutralization for Logs (Log Injection) |
| CWE-223 | Omission of Security-Relevant Information |
| CWE-532 | Insertion of Sensitive Info into Log File |
| CWE-779 | Logging of Excessive Data |
| CWE-770 | Allocation of Resources Without Limits (log storage) |
| CWE-393 | Return of Wrong Status Code (masking failures) |
