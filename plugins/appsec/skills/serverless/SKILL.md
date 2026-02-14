---
name: serverless
description: >
  This skill should be used when the user asks to "check serverless security",
  "audit Lambda functions", "analyze cloud function permissions", "check IAM
  policies", "find serverless vulnerabilities", or mentions "serverless",
  "Lambda", "Cloud Functions", "Azure Functions", "IAM policy", "event
  injection", "overprivileged", or "/tmp reuse" in a security context.
---

# Serverless Security (SRVLS)

Analyze serverless applications for security vulnerabilities including
overprivileged IAM policies, event data injection, secrets stored in plain-text
environment variables, /tmp directory data reuse between invocations, excessive
timeout configuration, and missing concurrency limits. Serverless architectures
introduce unique attack surfaces where each function is an independent entry
point with its own trust boundary.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks function configuration
- `--depth deep` traces event flow across function triggers and IAM policy chains
- `--severity` filters output (serverless issues are often `high` or `critical`)

## Framework Context

Key CWEs in scope:
- CWE-250: Execution with Unnecessary Privileges (overprivileged IAM)
- CWE-94: Improper Control of Generation of Code (event injection)
- CWE-312: Cleartext Storage of Sensitive Information (secrets in env)
- CWE-377: Insecure Temporary File (/tmp reuse)
- CWE-400: Uncontrolled Resource Consumption (timeout, concurrency)

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain serverless logic:

- Function handlers (`**/handlers/**`, `**/functions/**`, `**/lambdas/**`)
- Infrastructure as Code (`**/serverless.yml`, `**/template.yaml`, `**/*.tf`)
- IAM policies (`**/iam/**`, `**/policies/**`, `**/roles/**`)
- Function configuration (`**/function.json`, `**/host.json`)
- Event sources (`**/events/**`, `**/triggers/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for code patterns
2. `checkov` -- IaC scanner for serverless misconfigurations
3. `tfsec` -- Terraform-specific security scanner

Record which scanners are available and which are missing.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting serverless:
```
semgrep scan --config auto --json --quiet <target>
```

If checkov is available, run for IaC:
```
checkov -d <target> -o json --quiet
```

Filter results to serverless-relevant rules. Normalize output to the
findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **IAM policy audit**: Parse IAM policies (SAM, Serverless Framework,
   Terraform) and flag `Action: *`, `Resource: *`, or overly broad permissions.
2. **Event injection**: Find event data (API Gateway, SQS, S3, SNS) used
   in SQL, shell commands, or file paths without sanitization.
3. **Secrets in environment**: Check for secrets in plaintext environment
   variable definitions in IaC templates.
4. **/tmp reuse**: Find code that writes sensitive data to `/tmp` without
   cleanup, which persists between warm invocations.
5. **Timeout configuration**: Check for excessive timeouts that increase the
   cost and blast radius of denial-of-service attacks.
6. **Concurrency limits**: Verify reserved concurrency is configured to
   prevent a single function from consuming all account capacity.

When `--depth deep`, additionally trace:
- Cross-function event flows and trust boundaries
- IAM role assumption chains
- VPC configuration and network isolation

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `SRVLS` prefix
(e.g., `SRVLS-001`, `SRVLS-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Blast radius (what the overprivileged function can access)
- Concrete fix with diff when possible
- CWE references

## What to Look For

These are the high-signal patterns specific to serverless security. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **Overprivileged IAM policies** -- Functions with `Action: *` or
   `Resource: *` that violate the principle of least privilege.

2. **Event data injection** -- Untrusted event data (HTTP body, S3 key, SNS
   message) used in SQL queries, shell commands, or file paths.

3. **Secrets in plain-text env vars** -- API keys, database passwords, and
   tokens defined as plain-text environment variables in IaC templates.

4. **/tmp directory reuse** -- Sensitive data written to `/tmp` persists across
   warm invocations and may be accessible to subsequent executions.

5. **Excessive function timeout** -- Timeouts set to the maximum (15 minutes
   for Lambda) when the function's task requires seconds.

6. **Missing concurrency limit** -- No reserved concurrency, allowing a
   triggered flood to exhaust the account's concurrent execution quota.

7. **Missing VPC configuration** -- Functions accessing internal resources
   without VPC attachment, or VPC-attached functions without security groups.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | Event injection, code patterns | `semgrep scan --config auto --json --quiet <target>` |
| checkov | IAM policies, IaC misconfig | `checkov -d <target> -o json --quiet` |
| tfsec | Terraform IAM, Lambda config | `tfsec <target> --format json` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find IAM policies, event handling, environment variable definitions, and
/tmp usage. Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `SRVLS` (e.g., `SRVLS-001`)
- **metadata.tool**: `serverless`
- **metadata.framework**: `specialized`
- **metadata.category**: `SRVLS`
- **references.cwe**: `CWE-250`, `CWE-94`, `CWE-312`
- **references.owasp**: `A05:2021` (Security Misconfiguration)
- **references.stride**: `E` (Elevation of Privilege) or `T` (Tampering)

Severity guidance for this category:
- **critical**: IAM `Action: *` on `Resource: *`, event injection leading to RCE
- **high**: Overly broad IAM permissions, secrets in plain-text env vars, event injection in SQL
- **medium**: /tmp reuse with sensitive data, excessive timeout, missing concurrency limit
- **low**: Slightly overprivileged IAM that follows a known pattern, informational misconfigs
