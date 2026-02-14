---
name: integrity
description: >
  This skill should be used when the user asks to "check for integrity issues",
  "analyze deserialization", "find supply chain vulnerabilities", "review CI/CD
  security", "check SRI", or mentions "deserialization", "integrity", "pipeline
  security", "code signing", or "supply chain" in a security context. Maps to
  OWASP Top 10 2021 A08: Software and Data Integrity Failures.
---

# Software and Data Integrity Failures

Analyze source code, CI/CD configurations, and dependency manifests for integrity
violations. Detect insecure deserialization, unverified auto-updates, missing
subresource integrity, CI/CD pipeline injection, and untrusted dependency sources.
Produce actionable findings with severity ratings, code locations, and concrete
remediation steps.

## Supported Flags

All flags from `shared/schemas/flags.md` are supported:

| Flag | Relevant Behavior |
|------|-------------------|
| `--scope <value>` | Determines which files to analyze (default: `changed`) |
| `--depth <value>` | `quick`: pattern scan only. `standard`: full read + analysis. `deep`: trace data flows and dependency chains cross-file. `expert`: red team simulation with DREAD scoring |
| `--severity <value>` | Filter findings by minimum severity |
| `--format <value>` | Output format: `text`, `json`, `sarif`, `md` |
| `--fix` | Chain into remediation after analysis |
| `--quiet` | Findings only, no explanations |
| `--explain` | Add learning context to each finding |

## Framework Context

**OWASP Top 10 2021 - A08: Software and Data Integrity Failures**

Code and infrastructure that does not protect against integrity violations. This
category covers a broad set of concerns around trusting the provenance and
authenticity of software, data, and infrastructure:

- Relying on plugins, libraries, or modules from untrusted sources, repositories, or CDNs
- Insecure CI/CD pipelines that allow unauthorized code or configuration changes
- Auto-update functionality that downloads and applies updates without integrity verification
- Insecure deserialization where untrusted data is deserialized into objects, enabling
  remote code execution, replay attacks, injection, or privilege escalation

**STRIDE Mapping**: Tampering, Elevation of Privilege

**CWE References**: CWE-502 (Deserialization of Untrusted Data), CWE-829 (Inclusion of
Functionality from Untrusted Control Sphere), CWE-494 (Download of Code Without Integrity
Check), CWE-915 (Improperly Controlled Modification of Dynamically-Determined Object
Attributes), CWE-353 (Missing Support for Integrity Check)

## Detection Patterns

Read [`references/detection-patterns.md`](references/detection-patterns.md) before
performing analysis. It contains detailed Grep heuristics, language-specific code
examples, scanner coverage, and false positive guidance for each vulnerability pattern.

## Workflow

### 1. Determine Scope

Parse `--scope` flag and resolve to a concrete file list:

1. Apply scope resolution per `shared/schemas/flags.md`.
2. Filter to files relevant to integrity:
   - Serialization/deserialization code (data processing, API handlers)
   - CI/CD configuration files (`.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`,
     `.circleci/config.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`)
   - Dependency manifests and lockfiles (`package.json`, `package-lock.json`, `yarn.lock`,
     `requirements.txt`, `Pipfile.lock`, `go.sum`, `Cargo.lock`, `pom.xml`, `build.gradle`)
   - HTML files with CDN script/link tags
   - Update/installer scripts and auto-update mechanisms
   - Pre/post-install hooks in package configurations
   - Dockerfile and container build configurations
3. Include infrastructure-as-code files that reference external resources or images.

### 2. Check for Scanners

Detect available scanners in order of preference:

| Scanner | Detect | Relevant Rules |
|---------|--------|----------------|
| semgrep | `which semgrep` | Insecure deserialization, unsafe YAML/pickle loading |
| trivy | `which trivy` | Dependency vulnerabilities, misconfigurations, secret detection |
| osv-scanner | `which osv-scanner` | Known vulnerabilities in dependencies across ecosystems |
| checkov | `which checkov` | CI/CD misconfigurations, IaC integrity issues |
| bandit | `which bandit` | Python-specific: pickle, yaml, marshal (B301, B506) |

If no scanner is available, proceed with Claude analysis using Grep patterns from
`references/detection-patterns.md`. Note in output: "No scanner available -- findings
based on code pattern analysis only."

### 3. Run Scanners

For each available scanner:

1. Execute against the scoped file list.
2. Parse JSON output.
3. Filter to integrity-related rules only.
4. Normalize findings to the schema in `shared/schemas/findings.md`.
5. Set `scanner.confirmed: true` for scanner-detected findings.

### 4. Claude Analysis

Regardless of scanner availability, perform manual code analysis:

1. Read `references/detection-patterns.md` for the full pattern catalog.
2. Use Grep with the regex patterns to locate suspicious constructs.
3. Read surrounding code context (30-50 lines) to assess each match.
4. Trace data flows from untrusted sources to deserialization sinks.
5. At `--depth deep` or higher: follow imports, trace dependency chains, analyze
   CI/CD workflow trigger conditions and secret exposure, map update mechanisms
   end-to-end.
6. Deduplicate against scanner findings (same file + line = same finding).
7. Set `confidence: medium` for Claude-only findings, `confidence: high` when
   confirmed by a scanner.

### 5. Report Findings

Format output per `--format` flag. Each finding uses the schema from
`shared/schemas/findings.md` with these specifics:

- **ID prefix**: `INTEG` (e.g., `INTEG-001`, `INTEG-002`)
- **references.owasp**: `A08:2021`
- **references.stride**: `T` (Tampering) or `E` (Elevation of Privilege)
- **metadata.tool**: `integrity`
- **metadata.framework**: `owasp`
- **metadata.category**: `A08`

**Summary block** (appended after all findings):

```
## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |

**Scanners used**: [list or "none"]
**Scanners missing**: [list of recommended but unavailable]
**Top priorities**: [top 3 findings to fix first and why]
```

## What to Look For

These are the primary vulnerability patterns. See `references/detection-patterns.md`
for detailed regex patterns and code examples.

1. **Insecure deserialization** -- Using `pickle.loads`, `yaml.load` (without SafeLoader),
   Java `ObjectInputStream`, or `JSON.parse` on untrusted input to reconstruct objects
   that can execute arbitrary code.
2. **CI/CD pipeline injection** -- GitHub Actions or other CI workflows that interpolate
   untrusted input (PR titles, branch names, issue bodies) into `run:` blocks, enabling
   command injection in the build environment.
3. **CDN resources without SRI** -- Loading JavaScript or CSS from third-party CDNs
   without `integrity` attributes, allowing a compromised CDN to inject malicious code.
4. **Auto-update without verification** -- Download-and-execute update mechanisms that
   do not verify digital signatures or checksums before applying updates.
5. **Malicious pre/post-install scripts** -- Package configurations with install hooks
   that execute arbitrary code during `npm install`, `pip install`, or similar commands.
6. **Missing lockfile integrity** -- Dependency lockfiles absent from version control or
   containing no integrity hashes, allowing silent dependency substitution.
7. **Untrusted base images** -- Dockerfiles using unverified or untagged base images
   (e.g., `FROM node` instead of `FROM node:20-alpine@sha256:...`).
8. **Missing code signing** -- Release artifacts, packages, or binaries distributed
   without digital signatures.

## Scanner Integration

Refer to `shared/schemas/scanners.md` for full scanner details.

**Primary**: trivy (dependency vulnerabilities, misconfigurations), osv-scanner (cross-ecosystem CVEs)
**Secondary**: semgrep (deserialization patterns), bandit (Python pickle/YAML), checkov (CI/CD configs)
**Fallback**: Grep-based pattern matching from `references/detection-patterns.md` plus
Claude analysis of CI/CD configs and dependency manifests

When running as a subagent of the OWASP dispatcher, receive scope and flags from the
parent agent prompt. Do not re-parse user input.

## Output Format

All findings conform to the schema defined in `shared/schemas/findings.md`.

**ID prefix**: `INTEG` (registered in the ID Prefix Registry as OWASP A08)

Example finding:

```json
{
  "id": "INTEG-001",
  "title": "Unsafe pickle deserialization of user-uploaded data",
  "severity": "critical",
  "confidence": "high",
  "location": {
    "file": "src/api/import_handler.py",
    "line": 72,
    "function": "import_data",
    "snippet": "data = pickle.loads(request.files['upload'].read())"
  },
  "description": "User-uploaded file content is deserialized with pickle.loads, which can execute arbitrary Python code embedded in the pickle stream.",
  "impact": "An attacker can upload a crafted pickle file to achieve remote code execution on the server, potentially compromising the entire application and underlying infrastructure.",
  "fix": {
    "summary": "Replace pickle with a safe serialization format like JSON",
    "diff": "- data = pickle.loads(request.files['upload'].read())\n+ data = json.loads(request.files['upload'].read())"
  },
  "references": {
    "cwe": "CWE-502",
    "owasp": "A08:2021",
    "stride": "T",
    "mitre_attck": "T1059"
  },
  "scanner": {
    "name": "bandit",
    "rule": "B301",
    "confirmed": true
  },
  "metadata": {
    "tool": "integrity",
    "framework": "owasp",
    "category": "A08"
  }
}
```
