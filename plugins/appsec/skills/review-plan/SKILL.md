---
name: review-plan
description: >
  This skill should be used when the user asks to "review plan for security",
  "check plan for security issues", "security review of implementation plan",
  "audit the plan for vulnerabilities", or "check my plan before coding".
  Also triggers when the user mentions security in the context of an
  implementation plan, architecture proposal, or design document before
  code has been written. This is the FLAGSHIP pre-code security skill --
  no other tool reviews plans at design time.
---

# Security Plan Review

Analyze an implementation plan before code exists. Identify security gaps,
implicit trust assumptions, missing threat considerations, and architectural
risks while changes are still cheap. This is the most cost-effective point
in the development lifecycle to catch security issues -- fixing a design flaw
before coding costs 10-100x less than fixing it in production.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Plan Review Behavior |
|------|---------------------|
| `--scope plan` | Default. Reads the implementation plan content. |
| `--scope file:<path>` | Review a plan written to a specific file. |
| `--depth quick` | Check for top 5 most common plan-level security gaps only. |
| `--depth standard` | Full security review against all checklist items. |
| `--depth deep` | Standard + trace data flows described in the plan, model trust boundaries. |
| `--depth expert` | Deep + STRIDE-per-component on the planned architecture, attack tree sketches. |
| `--format` | Default `text`. Use `md` for structured report with Mermaid diagrams. |

## Why This Skill Exists

Most security tools analyze code that already exists. By then, architectural
decisions are baked in and expensive to change. This skill shifts security left
to the plan phase where:

- Architecture can be restructured without rewriting code.
- Auth/authz models can be designed correctly from the start.
- Data flow paths can be secured before they're implemented.
- Third-party integration risks can be evaluated before dependencies are added.
- Compliance requirements can be built in rather than bolted on.

## Workflow

### Step 1: Obtain the Plan

1. If `--scope plan` (default): read the implementation plan from the current
   planning context. This is typically the plan approved via ExitPlanMode in
   Claude Code, or a plan provided by the user.
2. If `--scope file:<path>`: read the specified file.
3. If the user pastes or describes a plan inline, use that content directly.
4. If no plan is found, ask the user to provide or point to the plan.

### Step 2: Understand the Plan

Before reviewing for security, build a mental model:

1. **Goal**: What is being built or changed?
2. **Components**: What new components, services, or modules are planned?
3. **Data**: What data will be created, read, updated, or deleted?
4. **Users**: Who will interact with the new functionality?
5. **Dependencies**: What external services, libraries, or APIs will be used?
6. **Infrastructure**: What deployment targets, networks, or storage are involved?

### Step 3: Security Review Checklist

Work through every item. For each concern found, record it as a finding.

#### Authentication and Authorization
1. Does the plan specify who can access each new endpoint or feature?
2. Are there features that assume "only internal users" without enforcing it?
3. Is there a clear auth model (JWT, session, API key) or is auth unmentioned?
4. Are role/permission checks planned for sensitive operations?
5. If an admin panel or privileged feature is planned, how is access controlled?

#### Data Security
6. Does the plan identify what data is sensitive (PII, credentials, financial)?
7. Is encryption at rest and in transit addressed for sensitive data?
8. Are data retention and deletion requirements considered?
9. If user input is accepted, is validation and sanitization mentioned?
10. Are database queries planned with parameterization or ORM usage?

#### Trust Boundaries
11. Does the plan distinguish between trusted and untrusted inputs?
12. Are there service-to-service calls that assume mutual trust without verification?
13. If third-party APIs are called, is response validation planned?
14. Are webhook endpoints planned with signature verification?
15. Is there a clear boundary between public and authenticated functionality?

#### Architectural Risks
16. Does the plan introduce new attack surface (new endpoints, protocols, integrations)?
17. Are there single points of failure for security controls?
18. Is error handling mentioned, and does it avoid leaking sensitive information?
19. Are logging and monitoring planned for security-relevant operations?
20. If file uploads are planned, are size limits, type validation, and storage isolation mentioned?

#### Third-Party and Supply Chain
21. Are new dependencies being added? Are they well-maintained and audited?
22. Do planned third-party integrations require sharing sensitive data?
23. Is there a plan for handling third-party service outages or compromises?
24. Are API keys and secrets managed through environment variables or a vault?

#### Implicit Assumptions
25. What security assumptions does the plan make without stating them?
26. Does the plan assume network-level security that may not exist?
27. Are there race conditions possible in the planned operations?
28. Does the plan assume sequential execution where concurrent access is possible?
29. Are there "we'll add security later" gaps?

### Step 4: Risk Assessment

For each identified concern, assess:

1. **Likelihood**: How likely is this to be exploited if left unaddressed?
2. **Impact**: What is the worst-case outcome?
3. **Cost to fix now**: How much plan revision is needed?
4. **Cost to fix later**: How much code rewrite if caught post-implementation?

### Step 5: Generate Recommendations

For each concern, produce an actionable recommendation:

- **Concrete**: "Add JWT validation middleware to the /api/admin routes" not "consider authentication."
- **Proportional**: Match the recommendation to the application's risk profile.
- **Ordered**: Present recommendations in priority order (highest risk first).
- **Constructive**: Frame as improvements to the plan, not criticisms.

### Step 6: Report

Output the plan review with findings and recommendations.

## Output Format

Finding ID prefix: **PLAN** (e.g., `PLAN-001`).

```
## Security Plan Review

### Plan Summary
[1-2 sentence summary of what the plan proposes]

### Security Assessment: [PASS | CONCERNS | SIGNIFICANT GAPS]

### Findings

#### PLAN-001: [Title] -- Severity: HIGH
Category: [Auth | Data | Trust Boundary | Architecture | Supply Chain | Assumption]
Concern: [What is missing or risky in the plan]
Risk: [What could go wrong if this ships as-is]
Recommendation: [Specific change to the plan]
Cost to fix now: [Minimal | Moderate | Significant]
Cost to fix later: [Moderate | Significant | Architectural rewrite]

#### PLAN-002: ...

### Plan Strengths
[Security aspects the plan handles well -- acknowledge good design]

### Recommended Plan Additions
[Bullet list of specific items to add to the plan before coding begins]

### Trust Boundary Diagram (--depth deep)
[Mermaid diagram of planned architecture with trust boundaries marked]
```

Findings follow `../../shared/schemas/findings.md` with:
- `metadata.tool`: `"review-plan"`
- `metadata.framework`: depends on invoking context
- `metadata.category`: `"plan-review"`
- `references.cwe`: Most relevant CWE for the architectural weakness

### Severity Guidelines for Plan Findings

| Severity | Criteria |
|----------|----------|
| `critical` | Plan has no authentication model for sensitive features, stores credentials in plaintext by design, or exposes PII without encryption |
| `high` | Missing authorization checks on privileged operations, no input validation strategy, trust boundary violations in the architecture |
| `medium` | Incomplete error handling strategy, missing rate limiting, logging gaps for security events |
| `low` | Minor hardening opportunities, defense-in-depth suggestions, style and convention issues |

## Pragmatism Notes

- Plans are naturally incomplete. Don't flag every missing detail -- focus on
  security-relevant gaps that would be costly to fix after implementation.
- A plan for an internal CLI tool needs different security scrutiny than a
  public-facing API. Calibrate expectations to the threat model.
- Acknowledge what the plan does well. Pure criticism is demoralizing and less
  likely to be acted upon.
- When a plan says "we'll use standard auth" without specifics, flag it as
  needing clarification rather than assuming the worst.
- Plans for prototypes and MVPs may intentionally defer security. Note the
  deferred items but respect the stated intent.
