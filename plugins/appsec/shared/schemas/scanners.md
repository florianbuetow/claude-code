# Scanner Detection Patterns

Reference for detecting and integrating external security scanners. Skills read this to determine which scanners are available and how to invoke them.

## Scanner Registry

### Multi-Language Scanners

#### semgrep
- **Detect**: `which semgrep` or `semgrep --version`
- **Languages**: 30+ (Python, JS/TS, Java, Go, Ruby, C, C++, PHP, Rust, etc.)
- **Run**: `semgrep scan --config auto --json --quiet <target>`
- **Output**: JSON with findings array
- **SARIF**: `semgrep scan --config auto --sarif --quiet <target>`
- **Best for**: Pattern-based SAST, custom rules, taint analysis
- **Covers**: Injection, XSS, SSRF, misconfig, auth issues, crypto misuse
- **OWASP mapping**: A01-A10 (broad coverage)

### Language-Specific Scanners

#### bandit (Python)
- **Detect**: `which bandit` or `bandit --version`
- **Run**: `bandit -r <target> -f json -q`
- **Output**: JSON with results array
- **Best for**: Python-specific security issues
- **Covers**: eval/exec, pickle, SQL injection, weak crypto, hardcoded passwords, temp files
- **OWASP mapping**: A02, A03, A05, A07

#### gosec (Go)
- **Detect**: `which gosec` or `gosec --version`
- **Run**: `gosec -fmt json ./...` (from module root)
- **Output**: JSON with Issues array
- **Best for**: Go-specific security patterns
- **Covers**: SQL injection, command injection, hardcoded creds, weak crypto, TLS config
- **OWASP mapping**: A02, A03, A05, A07

#### brakeman (Ruby/Rails)
- **Detect**: `which brakeman` or `brakeman --version`
- **Run**: `brakeman -q -f json -o /dev/stdout`
- **Output**: JSON with warnings array
- **Best for**: Rails-specific vulnerabilities
- **Covers**: Mass assignment, SQL injection, XSS in ERB, unsafe redirects
- **OWASP mapping**: A01, A03, A05, A07

#### cargo-audit (Rust)
- **Detect**: `which cargo-audit` or `cargo audit --version`
- **Run**: `cargo audit --json`
- **Output**: JSON with vulnerabilities
- **Best for**: Known CVEs in Rust dependencies
- **OWASP mapping**: A06

#### phpstan (PHP)
- **Detect**: `which phpstan` or `vendor/bin/phpstan --version`
- **Run**: `phpstan analyse --error-format=json <target>`
- **Output**: JSON with errors
- **Best for**: PHP static analysis with security extensions
- **OWASP mapping**: A03, A05

#### spotbugs (Java)
- **Detect**: Check for `spotbugs` binary or Maven/Gradle plugin
- **Run**: Via Maven: `mvn spotbugs:check` or Gradle: `gradle spotbugsMain`
- **Output**: XML with BugInstance elements
- **Best for**: Java bytecode analysis with Find Security Bugs plugin
- **Covers**: Injection, XXE, SSRF, deserialization, weak crypto
- **OWASP mapping**: A01-A10 (with security plugin)

### Dependency Scanners

#### npm audit (Node.js)
- **Detect**: `which npm` (built-in)
- **Run**: `npm audit --json`
- **Output**: JSON with advisories
- **Best for**: Known CVEs in npm dependencies
- **OWASP mapping**: A06

#### pip-audit (Python)
- **Detect**: `which pip-audit`
- **Run**: `pip-audit --format json`
- **Output**: JSON with vulnerabilities
- **Best for**: Known CVEs in Python packages
- **OWASP mapping**: A06

#### trivy (Universal)
- **Detect**: `which trivy` or `trivy --version`
- **Run (filesystem)**: `trivy fs --format json <target>`
- **Run (container)**: `trivy image --format json <image>`
- **Output**: JSON with Results array
- **Best for**: Vulnerabilities, misconfigs, secrets, licenses in containers, filesystems, IaC
- **OWASP mapping**: A05, A06, A08

#### osv-scanner (Universal)
- **Detect**: `which osv-scanner`
- **Run**: `osv-scanner --format json -r <target>`
- **Output**: JSON with results
- **Best for**: OSV database lookups across all ecosystems
- **OWASP mapping**: A06

### Secret Scanners

#### gitleaks
- **Detect**: `which gitleaks` or `gitleaks version`
- **Run (current files)**: `gitleaks detect --source <target> --report-format json --report-path /dev/stdout --no-banner`
- **Run (git history)**: `gitleaks detect --source <target> --report-format json --report-path /dev/stdout --no-banner --log-opts="--all"`
- **Output**: JSON array of findings
- **Best for**: Secrets in code and git history
- **Covers**: API keys, tokens, passwords, private keys, connection strings

#### trufflehog
- **Detect**: `which trufflehog` or `trufflehog --version`
- **Run**: `trufflehog filesystem --json <target>`
- **Run (git)**: `trufflehog git --json file://<target>`
- **Output**: JSON lines (one finding per line)
- **Best for**: High-signal secret detection with live verification
- **Covers**: 700+ credential detectors with optional verification

### IaC Scanners

#### checkov
- **Detect**: `which checkov` or `checkov --version`
- **Run**: `checkov -d <target> -o json --quiet`
- **Output**: JSON with passed/failed checks
- **Best for**: Terraform, CloudFormation, K8s, Docker, Helm
- **Covers**: CIS benchmarks, security misconfigurations
- **OWASP mapping**: A05

#### tfsec
- **Detect**: `which tfsec` or `tfsec --version`
- **Run**: `tfsec <target> --format json`
- **Output**: JSON with results
- **Best for**: Terraform-specific security scanning
- **OWASP mapping**: A05

#### kics
- **Detect**: `which kics` or `kics version`
- **Run**: `kics scan -p <target> --type json`
- **Output**: JSON with queries
- **Best for**: Multi-IaC scanning (Terraform, CloudFormation, Ansible, K8s, Docker, OpenAPI)
- **OWASP mapping**: A05

## Scanner Detection Flow

Skills should detect scanners in this order:

```
1. Check if scanner binary is on PATH: `which <binary>`
2. Check common install locations (node_modules/.bin, vendor/bin, etc.)
3. Check if Docker is available for containerized scanners
4. Cache results — don't re-detect on every invocation
```

## Scanner Selection by Skill

| Skill | Primary Scanners | Fallback |
|-------|-----------------|----------|
| secrets | gitleaks, trufflehog | Grep for high-entropy strings and key patterns |
| injection | semgrep, bandit, gosec | Grep for string interpolation in queries |
| access-control | semgrep | Claude analysis of route middleware |
| crypto | semgrep, bandit | Grep for weak algorithm names |
| outdated-deps | npm-audit, pip-audit, trivy, osv-scanner, cargo-audit | Read lockfiles, check known CVEs |
| misconfig | checkov, tfsec, kics, trivy | Claude analysis of config files |
| auth | semgrep | Claude analysis of auth flows |
| ssrf | semgrep | Grep for URL fetch patterns |
| integrity | trivy, osv-scanner | Claude analysis of CI/CD configs and dependency manifests |

## Output Normalization

When a skill runs a scanner, normalize the output to the findings schema defined in `findings.md`. Map scanner-specific severity levels:

| Scanner | Critical | High | Medium | Low |
|---------|----------|------|--------|-----|
| semgrep | ERROR | WARNING | WARNING | INFO |
| bandit | HIGH confidence + HIGH severity | HIGH severity | MEDIUM severity | LOW severity |
| gitleaks | — (all treated as HIGH) | default | — | — |
| trivy | CRITICAL | HIGH | MEDIUM | LOW |
| npm audit | critical | high | moderate | low |
| checkov | — | FAILED (high impact) | FAILED (medium impact) | FAILED (low impact) |

## Claude Fallback Patterns

When no scanner is available for a skill, Claude uses Grep and Read to find common vulnerability patterns. Each skill's detection-patterns.md contains the specific patterns to search for. The general approach:

1. Use Grep with regex patterns to find suspicious code constructs.
2. Read the surrounding code context to assess whether the pattern is actually vulnerable.
3. Report findings with `confidence: medium` (scanner confirmation would be `confidence: high`).
4. Always note in output: "No scanner available — findings based on code pattern analysis only."
