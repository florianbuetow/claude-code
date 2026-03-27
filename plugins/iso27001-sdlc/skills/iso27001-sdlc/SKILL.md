---
name: iso27001-sdlc
description: >
  Scan a software repository for ISO 27001:2022 compliance of its software development controls.
  Produces a per-control compliance report covering Annex A controls 8.4, 8.25–8.33
  (source code access, secure SDLC, application security requirements, secure architecture,
  secure coding, security testing, outsourced development, environment separation, change
  management, and test data). Use this skill whenever a user mentions ISO 27001, ISMS compliance,
  security audit readiness, Annex A controls, secure SDLC compliance, or wants to check whether
  their codebase meets information security standards. Also trigger when the user asks about
  audit preparation for software development, security control gaps, or compliance posture
  of a repository — even if they don't mention ISO 27001 by name but describe wanting to verify
  security practices against a standard.
---

# ISO 27001:2022 Software Development Compliance Scanner

Scans a repository and produces a compliance gap report against the
ISO 27001:2022 Annex A software development controls (8.4, 8.25–8.33).

## Before you start

Read `references/controls.md` — it contains the per-control scoring rules,
example fix suggestions, and the mapping from evidence to status.

## Architecture: two-phase scan → score

The skill separates evidence collection (deterministic) from compliance
scoring (judgment-based). This eliminates inconsistency where the same file
gets assessed differently for different controls.

**Phase 1 — Scan** runs `scripts/scan_repo.py` to collect all file evidence
into a single JSON structure. This is the only phase that touches the filesystem.

**Phase 2 — Score** reads the JSON evidence and applies the scoring rules from
`references/controls.md` to produce the markdown report. Evidence is mapped to
controls, not re-discovered per control.

## Phase 1: Collect evidence

Run the scanning script:

```bash
python /path/to/skill/scripts/scan_repo.py /path/to/repo --output /tmp/iso27001-evidence.json
```

The script indexes the entire repo and produces structured evidence covering:
file pattern matches, linter configs, security analysis tools, faker/synthetic
data libraries, hardcoded secret patterns, .gitignore checks, CI/CD config
analysis, ADR security content, security test files, language/container/IaC
detection, and monorepo detection.

Review the scan summary printed to stderr. If the repo is a monorepo (the
script detects this), see the Monorepo Handling section below before proceeding.

If the script fails or the repo is not locally available, fall back to manual
scanning: use `find`, `grep`, and `cat` to collect the same evidence described
in `references/controls.md`. The script is a convenience, not a hard dependency.

## Phase 2: Score and report

Read the evidence JSON produced by Phase 1. For each of the 10 core controls
(8.4, 8.25, 8.26, 8.27, 8.28, 8.29, 8.30, 8.31, 8.32, 8.33), apply the
scoring rules in `references/controls.md`.

The evidence JSON maps to controls like this:

| Evidence key | Used by controls |
|---|---|
| `file_evidence.codeowners` | 8.4, 8.32 |
| `file_evidence.pr_template`, `pr_template_security` | 8.25, 8.32 |
| `file_evidence.issue_template` | 8.25, 8.26 |
| `file_evidence.security_policy` | 8.25 |
| `architecture_security`, `adr_findings` | 8.27 |
| `file_evidence.threat_model` | 8.27 |
| `linter_evidence`, `security_analysis` | 8.28 |
| `secrets_findings`, `env_gitignore` | 8.28 |
| `file_evidence.lockfiles`, `file_evidence.dependency_scanning_config` | 8.28 |
| `ci_evidence.security_jobs` | 8.25, 8.28, 8.29 |
| `security_test_files` | 8.29 |
| `file_evidence.env_specific_configs`, `file_evidence.env_dirs` | 8.31 |
| `file_evidence.changelog`, `file_evidence.commitlint_config` | 8.32 |
| `faker_evidence`, `file_evidence.test_fixtures_dirs` | 8.33 |

When a single piece of evidence is relevant to multiple controls, reference
it consistently — do not re-assess or describe it differently in each section.
Example: if CI has CodeQL configured, that's SAST evidence for 8.29, a
security gate for 8.25, and supporting evidence for 8.28. State the fact once,
reference it in each control.

After scoring core controls, do a lighter pass on supporting controls
(5.8, 8.7, 8.8, 8.9, 8.16) — present if found, flag if absent, but don't
fail the report over them.

### Handling absent infrastructure

If no CI/CD configuration is found, do not attempt CI-related checks.
Instead flag CI/CD as an analysis gap and include this guidance:

> ISO 27001:2022 expects automated security controls integrated into the
> build and deployment pipeline: static analysis (SAST), dependency scanning
> (SCA), and approval gates before production deployment. Without CI/CD
> configuration in the repository, these controls cannot be verified. The
> organization should document its CI/CD approach and ensure security scans
> are mandatory pipeline stages.

The same principle applies to any absent infrastructure — flag the gap,
explain the ISO requirement, move on.

## Report format

Produce a single markdown report. Use this structure:

```markdown
# ISO 27001:2022 Software Development Compliance Report

**Repository:** <name>
**Scan date:** <date>
**Languages/frameworks:** <detected>
**CI/CD system:** <detected or "None detected">
**Repository type:** <single project / monorepo with N sub-projects>

## Executive Summary

<Lead with the highest-risk gap. State overall posture. Name the #1 priority action.>

**Overall posture:** <STRONG / MODERATE / WEAK / CRITICAL GAPS>

| Status | Count |
|--------|-------|
| PASS | X |
| WARNING | X |
| FAIL | X |
| MANUAL REVIEW NEEDED | X |
| NOT APPLICABLE | X |

## Detailed Findings

### 8.X — <Control Name>

**Status:** PASS / FAIL / WARNING / NOT APPLICABLE / MANUAL REVIEW NEEDED

**What this control requires:**
<1-2 sentences from the control intent in controls.md>

**Evidence found:**
- <file path or config with brief description>

**Gaps identified:**
- <what is missing>

**Recommended actions:**
- <concrete fix suggestion from controls.md>
- <if templates would help: "A template for <X> can be generated on request.">

---

[repeat for each of the 10 controls]

## Supporting Controls

| Control | Status | Notes |
|---------|--------|-------|
| 5.8 — Info security in project mgmt | ... | ... |
| 8.8 — Vulnerability management | ... | ... |
| ... | ... | ... |

## Next Steps

<Top 3-5 prioritized actions. Be specific: "Add a .bandit config for Python
SAST" not "improve security testing.">

## Appendix: Analysis Limitations

<What the scan could not verify: platform-level access controls, process
adherence, training records, contractual controls, etc.>
```

Keep the report concise. For large repos, summarize evidence per control
(e.g., "14 workflow files found, 3 contain security scanning stages")
rather than listing every file. Only list individual files when they're
notable (secrets found, key configs present/absent).

## Example control output

This example shows the expected quality bar for a single control finding:

```markdown
### 8.28 — Secure Coding

**Status:** WARNING

**What this control requires:**
Apply secure coding principles to prevent common vulnerabilities. Enforce
coding standards, use static analysis, manage dependencies securely, and
prevent hardcoded secrets.

**Evidence found:**
- `.eslintrc.json` — ESLint configured but no security plugin (`eslint-plugin-security` absent)
- `package-lock.json` — dependency lock file present
- `.github/dependabot.yml` — automated dependency updates configured
- `.env` in `.gitignore` — environment files properly excluded
- `.env.example` — environment variable documentation present

**Gaps identified:**
- No security-focused static analysis tool configured (no Semgrep, Bandit, or equivalent)
- No secrets scanning configured (no Gitleaks, GitGuardian, or detect-secrets)
- No secure coding standards document found in repository
- 2 potential hardcoded secrets detected:
  - `src/config/api.ts:14` — Generic API Key assignment
  - `scripts/deploy.sh:8` — Connection string with credentials

**Recommended actions:**
- Add `eslint-plugin-security` to ESLint config and enable recommended rules
- Add Gitleaks with a `.gitleaks.toml` config; integrate into CI as a pre-commit hook and pipeline stage
- Rotate the credentials found in `src/config/api.ts` and `scripts/deploy.sh`; move them to environment variables or a secrets manager
- Create a secure coding standards document covering OWASP Top 10 mitigations for your stack. A template can be generated on request.
```

## Monorepo handling

When the scan detects a monorepo (`monorepo.is_monorepo: true`):

1. **Produce one aggregate report**, not one per sub-project. The ISMS scope
   is the organization's development practices, not individual packages.

2. **Note sub-project count and structure** in the report header.

3. **For controls that vary by sub-project** (e.g., different languages have
   different linter configs), summarize coverage:
   "8 of 12 sub-projects have language-appropriate linter configs. Missing:
   packages/auth, packages/billing, packages/legacy, packages/scripts."

4. **CI/CD is typically shared** in monorepos. Assess the root-level CI config
   and note if sub-projects have additional CI configurations.

5. **Flag monorepo-specific risks**: shared dependency lock files that may
   mask per-package vulnerabilities, inconsistent security tooling across
   sub-projects, and the need for CODEOWNERS to cover all sub-project paths.

## After the report

Offer follow-up actions:
- "I can generate template files for any of the missing documents or
  configurations — just tell me which ones."
- "I can do a deeper scan of specific areas if you want more detail on
  any control."
- "I can inspect specific CI workflow files or config files in detail."

Do NOT generate template files unless the user explicitly asks for specific ones.

## Key principles

- **Evidence-based:** every finding references a concrete file path or absence.
  Never assert compliance without evidence.
- **Conservative:** when in doubt, flag as WARNING or MANUAL REVIEW NEEDED.
  False assurance is worse than a false alarm.
- **Actionable:** every gap has a concrete fix suggestion (see examples in
  controls.md). "Improve your security" is not actionable.
- **Scope-honest:** be explicit about what a repo scan can and cannot verify.
  Many controls are process/organizational.
- **Consistent:** evidence is collected once, referenced everywhere. The same
  file never gets contradictory assessments across controls.
- **Proportional:** report length scales to findings, not repo size. Summarize
  when evidence is repetitive.
