# ISO 27001:2022 Annex A — Control Scoring Rules

This reference defines how to score each control based on the evidence JSON
produced by `scripts/scan_repo.py`. Each control section lists:

- **Evidence keys** — which JSON fields to check
- **Scoring rules** — how to map evidence to PASS / FAIL / WARNING / MANUAL REVIEW NEEDED / NOT APPLICABLE
- **Gap flags** — things that cannot be verified from a repo and need manual review
- **Example fix suggestions** — concrete, copy-pasteable recommendations for common gaps

## Table of Contents

1. [8.4 — Access to Source Code](#84--access-to-source-code)
2. [8.25 — Secure Development Life Cycle](#825--secure-development-life-cycle)
3. [8.26 — Application Security Requirements](#826--application-security-requirements)
4. [8.27 — Secure Architecture and Engineering](#827--secure-architecture-and-engineering)
5. [8.28 — Secure Coding](#828--secure-coding)
6. [8.29 — Security Testing in Development and Acceptance](#829--security-testing-in-development-and-acceptance)
7. [8.30 — Outsourced Development](#830--outsourced-development)
8. [8.31 — Separation of Environments](#831--separation-of-environments)
9. [8.32 — Change Management](#832--change-management)
10. [8.33 — Test Information and Data](#833--test-information-and-data)
11. [Supporting Controls](#supporting-controls)
12. [Overall Posture Scoring](#overall-posture-scoring)

---

## 8.4 — Access to Source Code

**Control intent:** Prevent unauthorized access to and modification of source
code. Protect confidentiality, integrity, and intellectual property.

### Evidence keys

- `file_evidence.codeowners`
- `file_evidence.branch_protection_config`
- `file_evidence.signed_commits_config`
- `file_evidence.contributing`

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| CODEOWNERS | `codeowners` non-empty | Present | — | Absent |
| Branch protection | `branch_protection_config` non-empty | Config found | Only mentioned in CONTRIBUTING.md | MANUAL REVIEW NEEDED (typically platform-level) |
| Signed commits | `signed_commits_config` non-empty | Configured | Absent (nice-to-have) | — |
| Contributing guide | `contributing` non-empty | Present with access policies | Present without access policies | Absent |

**Overall 8.4 status:**
- PASS if CODEOWNERS present AND contributing guide exists
- WARNING if one of the two is missing
- MANUAL REVIEW NEEDED if neither found (branch protection is almost always
  platform-level; its absence from the repo does not mean it's absent)

### Gap flags

An auditor will want to verify these items, which live outside the repo:
- Platform-level access controls: roles, permissions, SSO/MFA enforcement
- Periodic access reviews (quarterly or on role change)
- Audit logging of repository access and administrative actions

### Example fix suggestions

- **Missing CODEOWNERS:** "Add a `CODEOWNERS` file to the repository root mapping
  directories to responsible teams. Example: `* @org/platform-team` with more
  specific paths for sensitive areas like `infra/ @org/security-team`."
- **Missing contributing guide:** "Create a `CONTRIBUTING.md` covering: who can
  request repo access, required review approvals before merge, and branch
  naming conventions. A template can be generated on request."

---

## 8.25 — Secure Development Life Cycle

**Control intent:** Rules for secure development must be defined and applied
across all SDLC phases — from requirements through deployment and maintenance.

### Evidence keys

- `file_evidence.pr_template` + `pr_template_security`
- `file_evidence.issue_template`
- `file_evidence.security_policy`
- `ci_evidence.security_jobs`
- `ci_evidence.gate_indicators`

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| PR template with security | `pr_template` non-empty AND `pr_template_security` has findings | Template + security section | Template exists, no security content | No PR template |
| Issue templates | `issue_template` non-empty | Present | — | Absent (lower severity) |
| SDLC/security policy doc | `security_policy` non-empty | Dedicated doc found | Security mentioned in README only | No security docs |
| CI security gates | `ci_evidence.security_jobs` non-empty | Security jobs that block | Security jobs but non-blocking | CI exists, no security jobs |

**Overall 8.25 status:**
- PASS if security policy doc exists AND CI has blocking security jobs AND PR template has security section
- WARNING if two of three present
- FAIL if security policy doc missing AND no CI security jobs
- If no CI detected at all: flag as analysis gap (see SKILL.md guidance), score remaining checks only

### Gap flags

- Developer security training records (attendance, completion, frequency)
- SDLC metrics (security defect rates, mean time to remediate)
- Management review evidence of SDLC effectiveness

### Example fix suggestions

- **Missing security policy:** "Create a `SECURITY.md` or `docs/secure-development-policy.md`
  covering: SDLC phases with mapped security activities, mandatory security
  gates (review before merge, security tests before release), roles and
  responsibilities for security decisions. A template can be generated on request."
- **PR template without security:** "Add a 'Security Considerations' section to
  your PR template with checkboxes: '- [ ] No new secrets/credentials introduced',
  '- [ ] Input validation added for new endpoints', '- [ ] Security implications
  reviewed'. A template can be generated on request."
- **No CI security jobs:** "Add a security scanning stage to your CI pipeline.
  Minimum: SAST (e.g., CodeQL or Semgrep) and dependency scanning (e.g., `npm audit`
  or Snyk) as required checks that block merge on critical findings."

---

## 8.26 — Application Security Requirements

**Control intent:** Security requirements must be identified, specified, and
approved during analysis and design — not discovered during testing.

### Evidence keys

- `file_evidence.issue_template`
- `pr_template_security` (for security acceptance criteria in PRs)
- `adr_findings` (for security decisions in design docs)
- `file_evidence.secure_coding_docs` (may contain requirements checklists)

### Scoring rules

| Check | Evidence | PASS | WARNING |
|-------|----------|------|---------|
| Security in issue templates | `issue_template` exists with security fields | Templates include security fields | Templates exist without security fields, or no templates |
| Security requirements docs | Any doc matching `*security-requirements*`, `*nfr*`, or ADRs with security content | Dedicated requirements checklist found | Only informal references |
| Security in design decisions | `adr_findings` contains entries with `has_security_content: true` | ADRs address security | ADRs exist but don't mention security |

**Overall 8.26 status:**
- PASS if issue templates include security fields OR a dedicated security requirements doc exists
- WARNING if only informal security references found
- MANUAL REVIEW NEEDED if no evidence (security requirements typically live in ticketing tools)

### Gap flags

- Actual per-feature security requirements are in Jira/Linear/etc., not the repo
- Approval workflows for security requirements (who signs off) are process-level
- Third-party/SaaS security assessments are procurement artifacts

### Example fix suggestions

- **No security in issue templates:** "Add a 'Security Impact' section to issue
  templates with fields: data classification (public/internal/confidential),
  authentication/authorization changes (yes/no), new external integrations (yes/no).
  A template can be generated on request."
- **No security requirements checklist:** "Create a `docs/security-requirements-checklist.md`
  with standard categories: authentication, authorization, session management,
  input validation, data encryption, audit logging, privacy/regulatory requirements.
  Teams reference this when writing feature specs. A template can be generated on request."

---

## 8.27 — Secure Architecture and Engineering

**Control intent:** System architectures must incorporate security principles
(least privilege, defence in depth, fail-secure, zero trust). Threat modelling
should inform design decisions.

### Evidence keys

- `file_evidence.architecture_docs_dirs` + `file_evidence.architecture_docs_files`
- `architecture_security`
- `file_evidence.threat_model`
- `adr_findings`

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| Architecture docs | `architecture_docs_dirs` or `architecture_docs_files` non-empty | Docs found | — | No architecture docs |
| Security in architecture | `architecture_security` has findings with security keywords | Security content present | Docs exist, no security content | — |
| Threat models | `threat_model` non-empty | Threat model docs found | Absent (significant gap) | — |
| Security in ADRs | `adr_findings` has entries with `has_security_content: true` | Some ADRs address security | ADRs exist, none mention security | — |

**Overall 8.27 status:**
- PASS if architecture docs with security content exist AND (threat model OR security-focused ADRs found)
- WARNING if architecture docs exist but lack security content, or no threat models
- FAIL if no architecture documentation at all

### Gap flags

- Architecture review meeting records
- Whether threat modelling is performed regularly (process question)
- Design review checklists and sign-off records

### Example fix suggestions

- **No architecture docs:** "Create a `docs/architecture/` directory with at least:
  a system overview diagram, component descriptions, and data flow documentation.
  Include a 'Security Architecture' section covering trust boundaries, network
  zoning, encryption approach, and authentication/authorization model."
- **No threat model:** "Create a threat model for your system using STRIDE methodology.
  Document it in `docs/security/threat-model.md` covering: system boundaries,
  identified threats per component, chosen mitigations, and residual risks.
  Track mitigations as backlog items. A template can be generated on request."
- **Architecture docs lack security content:** "Add security considerations to existing
  architecture docs: trust boundaries in diagrams, encryption at rest/in transit
  decisions, least-privilege access patterns, and fail-secure defaults."

---

## 8.28 — Secure Coding

**Control intent:** Apply secure coding principles to prevent common
vulnerabilities. This is the most technically verifiable control.

### Evidence keys

- `linter_evidence` (per-language linter configs)
- `security_analysis` (security-specific SAST tools)
- `file_evidence.secrets_scanning_config`
- `secrets_findings` (hardcoded secrets detected)
- `env_gitignore` (.env handling)
- `file_evidence.env_example`
- `file_evidence.lockfiles`
- `file_evidence.dependency_scanning_config`
- `file_evidence.pre_commit`
- `file_evidence.secure_coding_docs`
- `repo_context.languages` (to determine which linters are expected)

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| Linter config | Any non-empty entry in `linter_evidence` matching detected languages | Language-appropriate linter found | Only formatting tools (prettier/editorconfig) | No linting at all |
| Security SAST | Any non-empty entry in `security_analysis` | Security-focused tool configured | — | No security analysis tools |
| Secrets scanning | `secrets_scanning_config` non-empty | Scanning configured | — | No secrets scanning |
| Hardcoded secrets | `secrets_findings` empty | No secrets found | — | Secrets detected (list files + lines) |
| .env handling | `env_gitignore.env_ignored` is true | .env in .gitignore | .env files committed | .gitignore missing or .env not excluded |
| Dependency locks | `lockfiles` non-empty | Lock files present | — | No lock files |
| Dependency scanning | `dependency_scanning_config` non-empty | Auto-updates configured | — | No dependency scanning |
| Coding standards doc | `secure_coding_docs` non-empty | Doc found | — | Absent |

**Overall 8.28 status:**
- PASS if linters present AND no hardcoded secrets AND lock files present AND (security SAST OR secrets scanning configured)
- WARNING if linters present but no security-specific tools, or minor gaps
- FAIL if hardcoded secrets found, or no linting AND no security analysis at all

**Language-specific linter expectations** (use `repo_context.languages`):

| Language | Expected linter | Security-specific tool |
|----------|----------------|----------------------|
| Python | ruff, flake8, pylint | bandit, semgrep |
| JavaScript/TypeScript | eslint, biome | eslint-plugin-security, semgrep |
| Java/Kotlin | checkstyle, spotbugs | spotbugs + find-sec-bugs, semgrep |
| Go | golangci-lint | gosec (often via golangci-lint), semgrep |
| Ruby | rubocop | brakeman |
| Rust | clippy | cargo-audit (dependency), semgrep |
| PHP | phpstan, phpcs | psalm (taint analysis), semgrep |
| C/C++ | clang-tidy | clang-tidy security checks, semgrep |
| Scala | scalafmt, scalafix | scalafix security rules |
| Swift | swiftlint | semgrep |
| Elixir | credo | sobelow |
| C# | Roslyn analyzers | SecurityCodeScan, semgrep |
| Dart | analysis_options.yaml | dart analyze (built-in) |

### Gap flags

- Code review records (PR/MR comments and approvals) are platform-level
- Developer secure coding training records

### Example fix suggestions

- **No security SAST (Python):** "Add a `.bandit` config or add `[tool.bandit]`
  to `pyproject.toml`. Integrate into CI: `bandit -r src/ -f json`. For broader
  coverage, add Semgrep with `semgrep scan --config=auto`."
- **No security SAST (JavaScript):** "Install `eslint-plugin-security`:
  `npm install --save-dev eslint-plugin-security` and add `plugin:security/recommended`
  to your ESLint extends. For deeper analysis, add Semgrep to CI."
- **No secrets scanning:** "Add Gitleaks: create `.gitleaks.toml` (start with the
  default config), add a pre-commit hook via `.pre-commit-config.yaml`, and add
  a CI step: `gitleaks detect --source . --verbose`. A config template can be
  generated on request."
- **Hardcoded secrets found:** "IMMEDIATE ACTION: Rotate all detected credentials.
  Move secrets to environment variables or a secrets manager (AWS Secrets Manager,
  HashiCorp Vault, Doppler). Add `.env` to `.gitignore`. Consider running
  `git filter-branch` or BFG Repo-Cleaner to remove secrets from git history."
- **No lock files:** "Commit your dependency lock file (`package-lock.json`,
  `poetry.lock`, `Cargo.lock`, etc.) to ensure reproducible builds and prevent
  supply chain attacks via dependency confusion."
- **No dependency scanning:** "Add Dependabot (`.github/dependabot.yml`) or
  Renovate (`renovate.json`) for automated dependency update PRs. Configure
  security-only updates at minimum. A config template can be generated on request."

---

## 8.29 — Security Testing in Development and Acceptance

**Control intent:** Security testing must verify that requirements are met and
vulnerabilities are identified before go-live.

### Evidence keys

- `ci_evidence.security_jobs` (SAST, DAST, SCA tool names found in CI)
- `ci_evidence.config_files` (CI files to reference)
- `security_test_files` (test files with security-related names)
- `file_evidence.codeql_config`
- `file_evidence.semgrep_config`
- `file_evidence.sonar_config`
- `repo_context.containers` (for container scanning relevance)

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| SAST in CI | `security_jobs` contains SAST tools (codeql, semgrep, bandit, brakeman, sonar, etc.) | SAST integrated | — | CI exists, no SAST |
| DAST | `security_jobs` contains DAST tools (zap, dastardly, nuclei) | DAST integrated | DAST mentioned in docs only | MANUAL REVIEW NEEDED (often external) |
| SCA/dependency scanning | `security_jobs` contains SCA tools (snyk, trivy, npm audit, etc.) | SCA in CI | Only Dependabot/Renovate (alerts, not blocking) | CI exists, no SCA |
| Container scanning | If `containers.dockerfile` is true: `security_jobs` contains container tools | Scanning found | — | Containers used, no scanning |
| Security test files | `security_test_files` non-empty | Dedicated security tests exist | Absent | — |

**Overall 8.29 status:**
- PASS if SAST in CI AND SCA in CI AND (container scanning OR no containers)
- WARNING if only one of SAST/SCA present, or security tools configured but non-blocking
- FAIL if CI exists but has no security testing at all
- NOT APPLICABLE for CI checks if no CI detected (flag as gap)

### Gap flags

- Penetration test reports and schedules (external firms, not in repo)
- Security acceptance criteria in release checklists
- DAST may run in a separate environment not reflected in repo CI

### Example fix suggestions

- **No SAST in CI (GitHub Actions):** "Add CodeQL analysis:
  `.github/workflows/codeql.yml` with `uses: github/codeql-action/analyze@v3`.
  Or add Semgrep: `uses: returntocorp/semgrep-action@v1`. Set as a required
  status check to block PRs with critical findings."
- **No SCA in CI:** "Add dependency review to CI. GitHub Actions:
  `uses: actions/dependency-review-action@v4` on pull_request events. Or add
  `npx audit-ci --critical` / `pip-audit` / `cargo audit` as a CI step."
- **No container scanning:** "Add Trivy to CI: `trivy image --exit-code 1
  --severity CRITICAL,HIGH <image>` as a post-build step. Or use Grype:
  `grype <image> --fail-on high`."
- **No security tests:** "Create dedicated security test files covering:
  authentication bypass attempts, authorization boundary tests, input validation
  edge cases, and session management. Name them clearly
  (e.g., `test_security_auth.py`, `auth.security.test.ts`)."

---

## 8.30 — Outsourced Development

**Control intent:** When development is outsourced, security requirements and
oversight must be contractually defined and enforced.

### Evidence keys

- `file_evidence.contributing` (may contain third-party policies)

### Scoring rules

This control is almost entirely process/contractual. Limited repo checks:

- PASS if CONTRIBUTING.md contains explicit third-party contributor policies
  (external review requirements, access scope limitations)
- MANUAL REVIEW NEEDED in most cases

**Overall 8.30 status:** Usually MANUAL REVIEW NEEDED or NOT APPLICABLE
(for teams with no outsourced development).

### Gap flags

This is the most process-heavy control. Auditors want:
- Contracts with security clauses (secure coding, vulnerability disclosure,
  confidentiality, right to audit)
- Supplier security assessment records
- External developer access provisioning/deprovisioning records
- Evidence that outsourced code meets same review/test standards as internal code

### Example fix suggestions

- **No third-party policies:** "If you use external contributors or contractors,
  add a 'Third-Party Contributors' section to CONTRIBUTING.md covering: access
  scope limitations, mandatory code review by internal team members, NDA/security
  requirements, and offboarding procedures."
- **General guidance:** "Document your supplier security requirements in a
  `docs/supplier-security-policy.md`. Include: minimum security certifications,
  required secure coding practices, vulnerability disclosure SLA, and audit rights.
  A template can be generated on request."

---

## 8.31 — Separation of Environments

**Control intent:** Development, test, and production environments must be
separated to prevent unauthorized changes and test activities affecting production.

### Evidence keys

- `file_evidence.env_specific_configs`
- `file_evidence.env_dirs`
- `file_evidence.k8s_envs`
- `file_evidence.terraform_envs`
- `file_evidence.docker_compose_envs`
- `repo_context.iac` (IaC presence)
- `ci_evidence.deployment_stages`

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| Environment configs | Any of `env_specific_configs`, `env_dirs`, `k8s_envs`, `terraform_envs`, `docker_compose_envs` non-empty | Clear env separation | Only 2 environments (dev+prod, no staging) | No environment separation visible |
| IaC env separation | `terraform_envs` or `k8s_envs` shows per-env structure | Per-env IaC | — | NOT APPLICABLE if no IaC |
| Deployment pipeline | `ci_evidence.deployment_stages` non-empty | Deploy stages exist | — | No deployment pipeline |

**Overall 8.31 status:**
- PASS if environment-specific configs show 3+ environments (dev/test/staging/prod)
- WARNING if only 2 environments visible, or environment separation unclear
- FAIL if no environment separation found at all
- Consider that environment separation may be managed entirely outside the repo
  (cloud console, platform settings) — flag if nothing found but don't
  assume non-compliance

### Gap flags

- Actual network/account separation (VPCs, cloud accounts) is infrastructure-level
- Access control per environment (who can access prod) is platform-level
- Rules about production data in lower environments are policy

### Example fix suggestions

- **No environment separation visible:** "Define environment-specific configuration
  files: `.env.development`, `.env.staging`, `.env.production` (with `.env.example`
  documenting required variables). For IaC, create `environments/dev/`,
  `environments/staging/`, `environments/prod/` with separate variable files."
- **Only dev+prod, no staging:** "Add a staging environment that mirrors production
  configuration. This provides a pre-production validation step. For Terraform,
  add `environments/staging/terraform.tfvars`. For Docker Compose,
  add `docker-compose.staging.yml`."
- **No deployment pipeline:** "Create a CI/CD deployment pipeline with environment
  promotion: build → deploy to dev (auto) → deploy to staging (auto) → deploy to
  prod (manual approval required). This enforces the separation in practice."

---

## 8.32 — Change Management

**Control intent:** Changes to systems and applications must be formally
controlled — submitted, assessed (including security impact), approved,
tested, and documented.

### Evidence keys

- `file_evidence.codeowners` (cross-referenced from 8.4)
- `file_evidence.pr_template` (cross-referenced from 8.25)
- `file_evidence.changelog`
- `file_evidence.commitlint_config`
- `file_evidence.runbooks`
- `ci_evidence.gate_indicators`
- `ci_evidence.deployment_stages`

### Scoring rules

| Check | Evidence | PASS | WARNING | FAIL |
|-------|----------|------|---------|------|
| Review enforcement | `codeowners` + `pr_template` present | Both present | One present | Neither |
| Change documentation | `changelog` non-empty | Changelog maintained | — | No changelog |
| Commit conventions | `commitlint_config` non-empty | Configured | — | Absent (lower severity) |
| Rollback capability | `runbooks` non-empty OR IaC present (`repo_context.iac`) | Runbooks or IaC-based rollback | — | No rollback procedures |
| Deployment gates | `ci_evidence.gate_indicators` non-empty | Approval gates in CI | Deployment exists, no gates | No deployment pipeline |

**Overall 8.32 status:**
- PASS if review enforcement + changelog + (rollback OR IaC) + deployment gates
- WARNING if most present but one area missing
- FAIL if no review enforcement AND no changelog AND no deployment pipeline

### Gap flags

- Change Advisory Board (CAB) or approval workflows in ticketing systems
- Emergency change procedures
- Change impact assessments (including security impact)

### Example fix suggestions

- **No changelog:** "Add a `CHANGELOG.md` following Keep a Changelog format
  (keepachangelog.com). Automate with conventional commits + a tool like
  `standard-version` or `release-please`."
- **No commit conventions:** "Add commitlint: `npm install --save-dev
  @commitlint/cli @commitlint/config-conventional` and create
  `commitlint.config.js` with `extends: ['@commitlint/config-conventional']`.
  Add as a commit-msg hook via Husky or pre-commit."
- **No rollback procedures:** "Create `docs/runbooks/rollback.md` documenting:
  how to revert a deployment, database migration rollback steps, and who to
  contact during a failed release. For IaC-based deployments, document the
  `terraform plan` → `terraform apply` → rollback workflow."
- **No deployment gates:** "Add manual approval gates for production deployments.
  GitHub Actions: use `environment: production` with required reviewers.
  GitLab: use `when: manual` on the production deploy stage."

---

## 8.33 — Test Information and Data

**Control intent:** Test data must be appropriately protected. Prefer
synthetic/anonymized data over production data in test environments.

### Evidence keys

- `file_evidence.test_fixtures_dirs`
- `faker_evidence` (per-ecosystem synthetic data library detection)
- `secrets_findings` (may catch credentials in test data)

### Scoring rules

| Check | Evidence | PASS | WARNING |
|-------|----------|------|---------|
| Synthetic data tooling | Any non-empty entry in `faker_evidence` | Faker/factory libraries in use | Test fixtures exist but no synthetic data tooling |
| Test fixtures | `test_fixtures_dirs` non-empty | Test data structured | — |

**Overall 8.33 status:**
- PASS if synthetic data libraries found in dependencies
- WARNING if test fixtures exist but no faker/factory tooling (suggests
  possible use of static or real data)
- MANUAL REVIEW NEEDED if no test data evidence at all

### Gap flags

- Policies on production data usage in test environments
- Data masking/anonymization procedures when prod data is unavoidable
- Test data retention and cleanup procedures

### Example fix suggestions

- **No synthetic data tooling (Python):** "Add `faker` and `factory_boy` to
  dev dependencies. Use factories to generate test data instead of hardcoded
  fixtures. Example: `factory.Faker('email')` instead of literal email addresses."
- **No synthetic data tooling (JavaScript):** "Add `@faker-js/faker` to devDependencies.
  Use `faker.person.fullName()`, `faker.internet.email()` etc. in test setup
  instead of hardcoded values that might resemble real data."
- **Static test fixtures without faker:** "Review test fixture files for any
  data that resembles real personal information. Replace with obviously fake
  data (e.g., `test@example.com`, `555-0100`) or integrate a faker library
  for dynamic generation."

---

## Supporting Controls

These receive lighter assessment. Check for evidence, note if found, flag if absent.
Do not assign FAIL for these — use only PASS / WARNING / NOT APPLICABLE.

### 5.8 — Information Security in Project Management

- **Check:** `file_evidence.issue_template` for security sections,
  `pr_template_security` for security considerations
- **PASS** if project templates include security fields
- **WARNING** if no security in project management artifacts

### 8.7 — Protection Against Malware

- **Check:** Container base image policies (pinned versions in Dockerfiles),
  build server hardening documentation
- Primarily organizational — usually WARNING or NOT APPLICABLE from repo evidence

### 8.8 — Management of Technical Vulnerabilities

- **Check:** `file_evidence.dependency_scanning_config` (Dependabot/Renovate),
  `file_evidence.security_txt`
- **PASS** if dependency update automation configured AND security.txt present
- **WARNING** if only one present

### 8.9 — Configuration Management

- **Check:** `repo_context.iac`, `file_evidence.editorconfig`,
  `file_evidence.gitops_configs`
- **PASS** if IaC present with managed configurations
- **WARNING** if no IaC or configuration baselines

### 8.16 — Monitoring Activities

- **Check:** `file_evidence.monitoring_configs`, logging library usage in
  dependency manifests
- **PASS** if monitoring/alerting configuration found
- **WARNING** if no monitoring evidence in repo

---

## Overall Posture Scoring

After scoring all 10 core controls, determine overall posture:

- **STRONG** — No FAILs, at most 2 WARNINGs among core controls
- **MODERATE** — No more than 2 FAILs, rest are PASS/WARNING/MANUAL REVIEW
- **WEAK** — 3-4 FAILs or widespread WARNINGs across most controls
- **CRITICAL GAPS** — 5+ FAILs, or all three of these core controls failing:
  8.25 (Secure SDLC), 8.28 (Secure Coding), 8.29 (Security Testing)

MANUAL REVIEW NEEDED and NOT APPLICABLE do not count against the posture —
they indicate scope limitations, not failures.

When reporting overall posture, lead with the most impactful gap. A single
FAIL on 8.28 with hardcoded secrets in production code is more urgent than
three WARNINGs about missing documentation.
