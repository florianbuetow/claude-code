---
name: outdated-deps
description: >
  This skill should be used when the user asks to "check for vulnerable dependencies",
  "audit dependencies", "find outdated packages", "scan for CVEs", "check for
  typosquatting", or mentions "vulnerable components", "outdated dependencies", or
  "supply chain" in a security context. Maps to OWASP Top 10 2021 A06: Vulnerable
  and Outdated Components.
---

# Vulnerable and Outdated Components Analysis

Analyze project dependencies for known vulnerabilities (CVEs), abandoned packages,
unpinned versions, typosquatting risks, and excessive transitive dependency chains.
This skill heavily relies on external scanners for CVE detection and uses Claude
analysis for configuration hygiene, supply chain risks, and contextual assessment.

## Supported Flags

Read [`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for full flag
documentation. This skill supports all cross-cutting flags.

Key flags for this skill:

| Flag | Effect |
|------|--------|
| `--scope <value>` | Target scope (default: `changed`). `module:` and `full` are common for dependency audits. |
| `--depth <value>` | Analysis depth (default: `standard`). `deep` traces transitive dependency trees. |
| `--severity <value>` | Minimum severity to report (default: all). |
| `--format <value>` | Output format: `text`, `json`, `sarif`, `md`. |
| `--fix` | Generate dependency update commands or patches for each finding. |
| `--explain` | Add CVE details, exploit context, and learning material to each finding. |

## Framework Context

**OWASP Top 10 2021 -- A06: Vulnerable and Outdated Components**

Applications are vulnerable when they use components with known vulnerabilities,
do not track component versions, do not scan for vulnerabilities regularly, do not
fix or upgrade underlying platforms in a timely fashion, or do not test compatibility
of updated libraries.

**CWE Mappings**:
- CWE-1035: Using Software with Known Vulnerabilities (OWASP Top 10 specific)
- CWE-1104: Use of Unmaintained Third-Party Components
- CWE-937: Using Components with Known Vulnerabilities

**STRIDE Mapping**: All categories -- the impact depends on the specific vulnerability
in the component. A vulnerable serialization library maps to Tampering and Elevation of
Privilege; a vulnerable TLS library maps to Information Disclosure.

## Detection Patterns

Read [`references/detection-patterns.md`](references/detection-patterns.md) before
running analysis. It contains Grep regex patterns for manifest file issues, lockfile
analysis, and supply chain risk indicators.

## Workflow

### Step 1 -- Determine Scope

1. Parse `--scope` flag (default: `changed`).
2. Resolve to a concrete file list.
3. Identify dependency manifests and lockfiles in scope:
   - **Node.js**: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Python**: `requirements.txt`, `requirements*.txt`, `Pipfile`, `Pipfile.lock`, `pyproject.toml`, `poetry.lock`, `setup.py`, `setup.cfg`
   - **Go**: `go.mod`, `go.sum`
   - **Rust**: `Cargo.toml`, `Cargo.lock`
   - **Java**: `pom.xml`, `build.gradle`, `build.gradle.kts`, `gradle.lockfile`
   - **Ruby**: `Gemfile`, `Gemfile.lock`
   - **PHP**: `composer.json`, `composer.lock`
   - **.NET**: `*.csproj`, `packages.config`, `Directory.Packages.props`
   - **Container**: `Dockerfile`, `docker-compose*.yml`
4. If `--scope changed` returns no manifest files, expand to `--scope module:<auto>`
   to find the nearest manifest.

### Step 2 -- Check for Scanners

Detect available scanners in priority order:

| Scanner | Detect | Ecosystem | Best For |
|---------|--------|-----------|----------|
| npm audit | `which npm` | Node.js | Built-in CVE scanning for npm packages |
| pip-audit | `which pip-audit` | Python | CVE scanning for Python packages |
| trivy | `which trivy` | Universal | Multi-ecosystem CVE + license scanning |
| osv-scanner | `which osv-scanner` | Universal | OSV database lookups across all ecosystems |
| cargo-audit | `which cargo-audit` | Rust | CVE scanning for Rust crates |

**This skill depends heavily on scanners.** If no scanners are available, warn the
user prominently and recommend installing at least one. Claude analysis alone cannot
reliably detect known CVEs -- it can only check configuration hygiene and supply chain
indicators.

### Step 3 -- Run Available Scanners

For each detected scanner relevant to the project ecosystem, run against the scoped
manifests:

- **npm audit**: `npm audit --json` (from package.json directory)
- **pip-audit**: `pip-audit --format json` (from requirements.txt or pyproject.toml directory)
- **trivy**: `trivy fs --format json --scanners vuln <target>`
- **osv-scanner**: `osv-scanner --format json -r <target>`
- **cargo-audit**: `cargo audit --json` (from Cargo.toml directory)

Normalize scanner output to the findings schema per
[`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md).

**Important**: Run scanners from the correct working directory. Dependency scanners
require being in the project root or the directory containing the manifest file.

### Step 4 -- Claude Analysis

Even when scanners are available, Claude adds value by analyzing patterns that scanners
miss. Using Grep and Read, search for patterns from `references/detection-patterns.md`:

1. **Unpinned versions**: Check manifests for loose version constraints (`^`, `~`, `*`,
   `>=` without upper bound).
2. **Missing lockfiles**: Verify that each manifest has a corresponding lockfile committed.
3. **Abandoned packages**: Cross-reference package names with known abandoned or
   deprecated packages when recognizable.
4. **Typosquatting risks**: Look for package names that are one edit distance from
   popular packages.
5. **Excessive dependencies**: Flag manifests with unusually large dependency counts
   that increase attack surface.
6. **License compliance**: Note packages with restrictive or unknown licenses if detectable.

Merge Claude findings with scanner findings, deduplicating by package name and version.

### Step 5 -- Report Findings

Output findings using the schema from
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

Use the **DEP** prefix for finding IDs (e.g., `DEP-001`, `DEP-002`).

Group findings by category:
1. **Known CVEs** (from scanners) -- highest priority
2. **Unpinned versions** -- configuration hygiene
3. **Missing lockfiles** -- supply chain risk
4. **Abandoned packages** -- maintenance risk
5. **Typosquatting candidates** -- supply chain attack risk
6. **Excessive transitive dependencies** -- attack surface

## What to Look For

1. **Known CVEs in direct dependencies** -- Vulnerabilities with published CVE
   identifiers in packages the project directly depends on.
2. **Known CVEs in transitive dependencies** -- Vulnerabilities in packages pulled
   in indirectly through the dependency tree.
3. **Unpinned dependency versions** -- Version ranges that allow automatic updates
   to potentially vulnerable versions (`^`, `~`, `*`, `>=`).
4. **Missing lockfiles** -- Manifests without committed lockfiles mean builds are
   not reproducible and dependency resolution can vary.
5. **Abandoned or unmaintained packages** -- Dependencies with no updates in 2+ years,
   archived repositories, or known deprecation notices.
6. **Typosquatting candidates** -- Package names suspiciously similar to popular
   packages (e.g., `lodahs` vs `lodash`, `reqeusts` vs `requests`).
7. **Excessive transitive dependencies** -- A single direct dependency pulling in
   hundreds of transitive packages increases supply chain attack surface.
8. **Packages from untrusted registries** -- Dependencies sourced from non-default
   registries, private URLs, or git repositories without integrity checks.
9. **Outdated major versions** -- Running multiple major versions behind, even
   without known CVEs, increases the risk window for future disclosures.

## Scanner Integration

See [`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md) for full scanner
invocation details. This skill primarily uses:

| Scanner | What It Catches |
|---------|----------------|
| npm audit | Known CVEs in npm packages, severity ratings, fix availability |
| pip-audit | Known CVEs in Python packages via PyPI/OSV advisories |
| trivy | Multi-ecosystem CVEs, license issues, Dockerfile base image vulnerabilities |
| osv-scanner | OSV database matches across all ecosystems, including Go, Maven, PyPI, npm |
| cargo-audit | RustSec advisory database matches for Rust crates |

**Scanner availability is critical for this skill.** Without scanners, the skill can
only detect configuration-level issues (unpinned versions, missing lockfiles) but
cannot reliably identify known CVEs.

When scanners are unavailable:
1. Warn: "No dependency scanner available. CVE detection requires a scanner. Install
   one of: npm audit (built-in), pip-audit, trivy, osv-scanner."
2. Proceed with Claude-only analysis for configuration hygiene patterns.
3. Report findings with `confidence: low` for anything that would need scanner
   confirmation.

## Output Format

All findings use the schema defined in
[`../../shared/schemas/findings.md`](../../shared/schemas/findings.md).

**ID Prefix**: `DEP` (e.g., `DEP-001`)

**References for each finding**:
- `references.owasp`: `A06:2021`
- `references.cwe`: `CWE-1035` (known vulns) or `CWE-1104` (unmaintained)
- `references.stride`: Depends on the specific vulnerability
- `metadata.tool`: `outdated-deps`
- `metadata.framework`: `owasp`
- `metadata.category`: `A06`

For CVE findings, also include:
- `references.cve`: The CVE identifier (e.g., `CVE-2023-44270`)
- `fix.summary`: The fixed version or upgrade command

**Summary table** after all findings:

```
| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |

| Category                  | Count |
|---------------------------|-------|
| Known CVEs                | N     |
| Unpinned Versions         | N     |
| Missing Lockfiles         | N     |
| Abandoned Packages        | N     |
| Typosquatting Candidates  | N     |
| Excessive Dependencies    | N     |
```

Followed by:
- Top 3 priorities (usually the highest-severity CVEs)
- Recommended upgrade commands
- Overall dependency health assessment paragraph
