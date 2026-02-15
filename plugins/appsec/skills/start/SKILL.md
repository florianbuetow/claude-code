---
name: start
description: >
  This skill should be used when the user asks to "start security analysis",
  "assess security", "which security tools should I use", "appsec start",
  "what should I scan", "security assessment", or invokes /appsec:start.
  Assesses the project's tech stack, data sensitivity, architecture, and
  installed scanners, then recommends which /appsec:* tools to run in
  priority order with rationale.
---

# AppSec Start -- Project Assessment

The entry point for any codebase. Detects what the project is, what data it
handles, what scanners are available, and recommends exactly which `/appsec:*`
tools are relevant, in what order, and why.

This skill runs entirely in the main agent context. It does NOT dispatch
subagents. It produces a recommendation, not findings.

## Supported Flags

This skill accepts a subset of cross-cutting flags. Read
[`../../shared/schemas/flags.md`](../../shared/schemas/flags.md) for the full
specification.

| Flag | Behavior |
|------|----------|
| `--scope` | Ignored. Start always assesses the full project. |
| `--format text` | Human-readable ASCII output (default). |
| `--format json` | Structured JSON assessment. |
| `--format md` | Markdown report. |
| `--quiet` | Suppress explanations, output tool list only. |

## Workflow

Execute all 6 steps sequentially in the main agent context. Use Glob, Grep,
Read, and Bash tools to gather evidence. Do NOT guess -- only report what
you find.

### Step 1: Detect Tech Stack

Read project manifests to determine languages, frameworks, databases, and
infrastructure. Check for each of these files using Glob:

| File Pattern | Reveals |
|-------------|---------|
| `package.json` | Node.js, npm dependencies, scripts |
| `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` | Dependency lockfiles |
| `requirements.txt`, `Pipfile`, `pyproject.toml`, `setup.py` | Python |
| `go.mod`, `go.sum` | Go |
| `Cargo.toml`, `Cargo.lock` | Rust |
| `Gemfile`, `Gemfile.lock` | Ruby |
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java/Kotlin |
| `*.csproj`, `*.sln` | .NET/C# |
| `composer.json` | PHP |
| `Dockerfile`, `docker-compose.yml`, `docker-compose.yaml` | Containers |
| `serverless.yml`, `serverless.yaml`, `serverless.ts` | Serverless |
| `terraform/*.tf`, `**/*.tf` | Terraform IaC |
| `*.yaml` in `.github/workflows/` | GitHub Actions CI/CD |
| `.gitlab-ci.yml` | GitLab CI/CD |
| `Jenkinsfile` | Jenkins CI/CD |
| `.circleci/config.yml` | CircleCI |

Read each found manifest to extract framework names, database drivers,
and notable dependencies. Build a concise stack summary.

### Step 2: Detect Data Sensitivity

Scan the codebase for patterns indicating sensitive data handling. Use Grep
with these patterns:

**PII indicators:**
- User model fields: `email`, `phone`, `address`, `ssn`, `date_of_birth`,
  `social_security`, `national_id`, `passport`
- GDPR patterns: `consent`, `gdpr`, `data_subject`, `right_to_forget`,
  `data_protection`

**Financial indicators:**
- Payment integrations: `stripe`, `paypal`, `braintree`, `adyen`, `square`
- Card patterns: `card_number`, `cvv`, `credit_card`, `payment_method`
- Transaction models: `transaction`, `invoice`, `billing`, `subscription`

**Health data indicators:**
- HIPAA terms: `hipaa`, `phi`, `protected_health`, `medical_record`,
  `diagnosis`, `patient`

**Auth mechanism indicators:**
- JWT: `jsonwebtoken`, `jwt`, `jose`
- OAuth: `oauth`, `passport`, `openid`
- Session: `express-session`, `cookie-session`, `session_store`
- Password storage: `bcrypt`, `argon2`, `scrypt`, `pbkdf2`

Classify data sensitivity as: **None detected**, **PII**, **Financial**,
**Health/PHI**, or combinations.

### Step 3: Detect Architecture Patterns

Determine the application type by scanning for these indicators:

| Pattern | Indicator Files / Code |
|---------|----------------------|
| API-only backend | Route handlers without template/view rendering, OpenAPI/Swagger spec |
| Full-stack | Template engines (EJS, Pug, Jinja, ERB), React/Vue/Angular alongside API |
| GraphQL | `.graphql` files, `graphql` in dependencies, schema definitions |
| WebSocket | `ws`, `socket.io`, `websocket` in dependencies or code |
| Serverless | `serverless.yml`, Lambda handlers, Cloud Functions |
| Microservices | Multiple `Dockerfile`s, service mesh config, multiple `package.json`s |
| Monolith | Single deployment unit, single database connection |
| Business logic heavy | Payment processing, e-commerce models, fintech calculations |
| Many dependencies | 100+ entries in lockfile |
| CI/CD present | `.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile` |

### Step 4: Detect Installed Scanners

Check PATH for known scanner binaries using Bash `which` commands. Run
these checks in parallel:

```
which semgrep
which bandit
which gosec
which brakeman
which cargo-audit
which gitleaks
which trufflehog
which trivy
which osv-scanner
which checkov
which tfsec
which kics
which npm    (for npm audit)
which pip-audit
```

Read [`../../shared/schemas/scanners.md`](../../shared/schemas/scanners.md)
for the full scanner registry and detection patterns.

Mark each as detected or not. For language-specific scanners, only report
relevance if the language is in the detected stack.

### Step 5: Check Existing Security Configs

Scan for security configurations already in place:

| Config | What to Check |
|--------|--------------|
| ESLint security | `.eslintrc*` files for `eslint-plugin-security` or security rules |
| CSP headers | `Content-Security-Policy` in middleware, meta tags, or config |
| CORS config | `cors()` middleware config, `Access-Control-Allow-Origin` settings |
| Rate limiting | `express-rate-limit`, `bottleneck`, rate limit middleware |
| Helmet/headers | `helmet` in dependencies, security header middleware |
| Input validation | `joi`, `zod`, `yup`, `class-validator`, `express-validator` |
| `.gitignore` | Whether `.env`, secrets, and keys are excluded |
| Dependabot | `.github/dependabot.yml` for automated dependency updates |

Note what is present and what is missing. This informs recommendations.

### Step 6: Output Tailored Recommendation

Based on all detected signals, produce a prioritized list of `/appsec:*`
tools to run, with rationale for each.

**Priority rules:**
1. `/appsec:secrets --scope full` is ALWAYS priority 1. Committed secrets
   are the most common and most damaging solo dev mistake.
2. Tools matching detected data sensitivity rank higher (financial data
   detected -> prioritize `business-logic`, `race-conditions`).
3. Tools matching detected architecture rank higher (GraphQL detected ->
   include `graphql`).
4. Tools with no relevant attack surface in this project go to the SKIP list.
5. Include the "why" for each recommendation -- reference specific files or
   patterns found.

## Output Format

### Text Format (default)

```
=====================================================
          APPSEC START -- Project Assessment
=====================================================

PROJECT: <project name from package.json or directory>
STACK: <languages, frameworks, databases, infra>
DATA: <data sensitivity classifications>
SCANNERS: <scanner> Y/N  <scanner> Y/N  ...

RECOMMENDED TOOLS (priority order):

  1. /appsec:secrets --scope full
     WHY: <rationale referencing specific findings>

  2. /appsec:<tool> --scope <recommended scope>
     WHY: <rationale referencing specific findings>

  ...

SKIP (not relevant for this project):
  - /appsec:<tool> (<reason>)
  - ...

EXISTING SECURITY:
  - <config found> -- <status>
  - ...

QUICK START:
  /appsec:run                    # Run top priorities automatically
  /appsec:run --depth deep       # Thorough analysis
  /appsec:run --depth expert     # + Red team simulation
  /appsec:full-audit             # Everything, with dated report

=====================================================
```

### JSON Format

```json
{
  "project": "<name>",
  "stack": { "languages": [], "frameworks": [], "databases": [], "infra": [] },
  "data_sensitivity": [],
  "architecture": [],
  "scanners": { "<name>": true|false },
  "existing_security": { "<config>": true|false },
  "recommended_tools": [
    { "rank": 1, "tool": "secrets", "scope": "full", "rationale": "..." }
  ],
  "skip": [
    { "tool": "graphql", "reason": "No GraphQL schema found" }
  ]
}
```

## Caching

After assessment, write the results to `.appsec/start-assessment.json` so
that `/appsec:run` can reuse the detection results without re-scanning.
Include a timestamp so stale results can be detected (older than 24 hours
or if `package.json` / manifest mtime has changed).

## Follow-Up Prompt

After presenting the assessment, suggest:

```
Ready to scan? Run one of:
  /appsec:run                    Run recommended tools automatically
  /appsec:<top-priority-tool>    Start with the highest priority
  /appsec:full-audit             Exhaustive audit with dated report
```
