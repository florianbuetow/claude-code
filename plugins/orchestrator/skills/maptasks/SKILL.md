---
name: maptasks
description: Use when you have a specified engineering task or task list and need to decide which AI model should handle each work unit — routes tasks across Claude Opus/Sonnet/Haiku, GPT-5.4 family, GPT-5.3-Codex, and Gemini 2.5/3 with per-unit category, evidence-based rationale, context briefing, and failure-mode warnings. Also checks whether the task is broken down enough and proposes finer decomposition before routing.
---

# maptasks — Route Engineering Work to the Right Model

## Overview

Given a specified engineering task (or set of tasks), produce a **routing plan** that:

1. Checks whether the task is broken down enough to route. If not, proposes a finer breakdown first.
2. Categorizes each leaf work unit using a 30-category task taxonomy.
3. Assigns each unit to the best-suited model based on practitioner evidence (April 2026).
4. Explains *why* this model is best for *this* category — citing the rule or evidence.
5. Specifies the **context briefing** each model needs to do its job.
6. Flags model-specific failure modes to watch for.

The skill is evidence-driven, not vibes-driven. Every recommendation traces to a category lookup or a numbered decision rule.

### The Three-Tier Strategy (always implicit)

Every routing plan should distribute work across three tiers in roughly these proportions:

| Tier | Share of work | Models |
|---|---|---|
| **Flagship reasoning** | 5–10% | Opus 4.6, GPT-5.4 Pro, Gemini 3.1 Pro |
| **Balanced mid-tier** | 40–50% | Sonnet 4.6, GPT-5.4, GPT-5.3-Codex, Gemini 2.5 Pro |
| **Cheap / fast** | 30–40% | Haiku 4.5, GPT-5.4 mini/nano, Gemini 3 Flash |

A routing plan that uses only one tier (all Opus, or all Sonnet) is almost always wrong. The two failure modes to avoid:

1. **Verbose model on shallow task** → cache thrashing, quota exhaustion (Opus on boilerplate).
2. **Speed model on hard reasoning** → "fast failure" — race conditions and memory leaks discovered after merge.

The skill prevents both by forcing each unit through category lookup → tier check → model selection.

## When to Use

- You have a fully or partially specified task and are about to execute it with AI assistance.
- You want to assemble a multi-model team (e.g. Architect + Implementer + Reviewer).
- You're choosing between two or more models for a specific piece of work and want the comparison.
- You want a routing plan *before* spinning up subagents or parallel sessions.
- You want to know whether a task description is decomposed enough to be routable at all.

**Do NOT use this skill for:**
- Picking a chat model for casual conversation.
- Reviewing the quality of code (use `kiss`, `solid-principles`, `beyond-solid-principles`).
- Estimating timelines or effort in person-hours.

## Inputs

The user provides one of:

1. A task description (e.g. "Implement OAuth2 login with Google, update schema, add tests, update docs").
2. A pre-broken-down task list (markdown or bullets).
3. A spec / PRD / GitHub issue / file path.

If anything critical is missing, ask for it before routing:

- **Scope**: How many files? What's the language/framework/stack?
- **Constraints**: Privacy (can data leave your infra?), ecosystem (Google/JVM/.NET), latency.
- **Cost posture**: cost-optimized, balanced, or quality-first?
- **Done criteria**: How will you know each unit is finished?

If the user describes a team type or role context (solo MVP dev, senior in production codebase, frontend startup, backend team, migration team, docs team, agentic CLI workflow, privacy-constrained/air-gapped), pre-load the matching default stack from `references/rules.md` Part 3 — Persona-Based Routing Scenarios — and use it as the starting policy before applying category lookups.

## Workflow

```
1. INGEST          → Read task / spec. Identify scope and constraints.
2. SUFFICIENCY     → Run Breakdown Sufficiency Check on each unit.
3. DECOMPOSE       → If any unit fails, propose finer breakdown BEFORE routing.
4. CATEGORIZE      → Map each leaf unit to one of the 30 task categories.
5. SELECT          → Apply category lookup, then decision rules to pick a model.
6. BRIEF           → Build the context briefing for each unit.
7. EMIT            → Output the routing plan in the standard format.
```

### Step 2: Breakdown Sufficiency Check

A work unit is **routable** only if all five hold:

| # | Criterion | Failing example |
|---|---|---|
| 1 | Belongs to exactly **one** task category | "Implement and test" — split |
| 2 | Requires exactly **one** model tier | "Plan and write docs" mixes flagship + mid — split |
| 3 | Produces a **single artifact** (one file, one plan, one review) | "Build OAuth flow" — split |
| 4 | Fits in **one context budget** (no mid-task re-injection) | "Migrate the whole repo" — chunk by module |
| 5 | Has **measurable done criteria** | "Make it better" — define done |

If any criterion fails, **propose a finer breakdown before routing**. Don't route an under-decomposed unit; you'll just push the routing problem onto the model.

### Step 5: Selecting the Model

1. **Category lookup** (Quick Reference table below) gives you a primary + runner-up.
2. **Apply decision rules** (Rules section below) to resolve ties or special cases.
3. **Check constraints**: privacy → local model; ecosystem → Gemini for Google stack; long context → Gemini 2.5 Pro.
4. **Sanity check**: cite the category number AND the rule number in the rationale.

## Model Roster

| Model | Tier | Sweet Spot | Context (usable) | $/M in | $/M out |
|---|---|---|---|---|---|
| **Claude Opus 4.6** | Flagship | Architecture, multi-file refactor, complex debug (race / cross-boundary), security audit, 7h+ autonomous | 1M (~400K reliable) | $5 | $25 |
| **GPT-5.4 Pro** | Flagship | Computer use (75% OSWorld), mid-task steering, native tool chaining | 1M | $30 | $180 |
| **Gemini 3.1 Pro** | Flagship | Frontier reasoning, frontend/UI, Google ecosystem (Go/Dart/Flutter/Angular) | 1M+ | $2-4 | $12-18 |
| **Claude Sonnet 4.6** | Mid | The 80% model: daily features, bug fixes, tests, docs, API/SQL design, frontend components | 1M (~400K reliable) | $3 | $15 |
| **GPT-5.4** | Mid | Structured output (~100% strict), tool/function calling, greenfield iteration | 1.05M | $2.50 | $15 |
| **GPT-5.3-Codex** | Mid | Terminal/DevOps/IaC (77.3% Terminal-Bench), code review, long-horizon autonomous (25h) | 400K | $2.50 | $15 |
| **Gemini 2.5 Pro** | Mid | Long-context analysis, whole-codebase summarization, data analysis, R workflows | 1-2M | $1.25 | $10 |
| **Claude Haiku 4.5** | Fast | Sub-agent workhorse, classification, boilerplate, strict JSON adherence | 200K | $0.80 | $5 |
| **GPT-5.4 mini** | Fast | Routine code, sub-agent, "almost indistinguishable from full" on simple tasks | 400K | $0.75 | $4.50 |
| **GPT-5.4 nano** | Fast | Classification, extraction, guardrails, high-volume pipelines | 400K | $0.20 | $1.25 |
| **Gemini 3 Flash** | Fast | Cost king for coding (78% SWE-bench at $0.50/MTok), default in JetBrains/Replit/Warp | 1M | $0.50 | $3 |
| **Codex-Spark** | Speed | Rapid prototyping drafter (1,000+ tok/s, 15x faster than Codex). Pair with Opus reviewer (Pattern B) | varies | varies | varies |
| **Qwen3-Coder-Next** | Local | Privacy-bound or offline coding (consumer hardware), Apache 2.0 | 128K | free | free |
| **Gemma 4** | Local | Local function calling, structured output, RAG (Apache 2.0) | varies | free | free |

Full profiles, weaknesses, and failure modes → `references/models.md`.

### Context Decay (the "1M Token Myth")

Advertised context windows ≠ usable context. Empirical retrieval accuracy:

| Model | 256K accuracy | 1M accuracy | Decay rate | Practical max |
|---|---|---|---|---|
| **Claude 4.6 Opus** | 92.1% | 78.3% | **15%** | ~400K reliable |
| **GPT-5.4** | 79.5% | 36.6% | **54%** | ~7,500 LoC reliable |
| **Gemini 3.1 Pro** | 35.0% | 25.9% | 26% | ~15,000 LoC (no cross-file reasoning) |

**Routing implication:** Long-context jobs should be routed by *task type*, not by raw window size:
- **Retrieval / summarization >200K** → Gemini 2.5 Pro (1–2M, generous free tier)
- **Cross-file reasoning >200K** → Claude Opus 4.6, but chunk to stay under 400K
- **Whole-codebase analysis with no precision needed** → Gemini 2.5 Pro
- **Anything past Opus 400K threshold** → switch to Gemini 2.5 Pro for that sub-task

### Mixed-Model Workflow Patterns

When more than one model collaborates on a task, use a named pattern. Full descriptions in `references/rules.md` Part 2.

| Pattern | Composition | Best for |
|---|---|---|
| **A. Architect / Implementer / Reviewer** | Opus → Sonnet → (Codex+Opus dual review) | New features in production codebases (the dominant 3-tier strategy) |
| **B. Drafter / Reviewer** | Gemini 3 Flash or Codex-Spark or GPT-5.4 mini → Opus 4.6 patch | Frontend iteration, prototyping, "show me 30 variants" — 3x faster than reasoning-only with no correctness loss |
| **C. Claude / Gemini Pipeline** | Opus plan → Gemini 2.5/3 implement → Opus review | Frontend-heavy work where Gemini's UI strengths matter |
| **D. Multi-Tier Subagent Team** | Sonnet lead + Haiku workers + Opus/Codex specialists | High-volume agentic pipelines (Augment Code style) |
| **E. Cost-Capped Default Stack** | Sonnet default + Opus escalation + Haiku downshift + GPT-5.4 strict for structured output | Sustainable production AI workflows |
| **F. Single-Vendor Lock-In** | Opus→Sonnet→Haiku OR GPT-5.4→mini→nano OR Gemini 3.1→Flash→Flash-Lite | Org policy / billing simplification |

When a unit's rationale invokes a pattern, name it explicitly: "Pattern A — Architect/Implementer/Reviewer".

## Task Categories (Quick Reference)

| # | Category | Primary | Runner-up | Avoid |
|---|---|---|---|---|
| 1 | Architecture / system design | **Opus 4.6** | GPT-5.4 Pro | — |
| 2 | Task decomposition / planning | **Opus 4.6** | GPT-5.4 | Haiku |
| 3 | Tech-stack / tradeoff analysis | **Opus 4.6** | GPT-5.2 | — |
| 4 | Spec writing (business → tech) | **Opus 4.6** | Sonnet 4.6 | Cursor Composer-2 |
| 5 | API contract design (OpenAPI/protobuf) | **Sonnet 4.6** | GPT-5.4 | — |
| 6 | Database schema design | **Sonnet 4.6** | Gemini 2.5 Pro | — |
| 7 | Greenfield feature implementation | **Sonnet 4.6** | GPT-5.4 | — |
| 8 | Boilerplate / scaffolding | **Haiku 4.5** | GPT-5.4 nano | Opus (10x cost waste) |
| 9 | Algorithm implementation | **Opus 4.6** | Codex | — |
| 10 | Frontend components (React/Vue/CSS) | **Gemini 3.1 Pro** | Sonnet 4.6, Gemini 3 Flash (budget) | Codex (weak on FE) |
| 11 | Backend service / REST endpoints | **Sonnet 4.6** | GPT-5.4 | — |
| 12 | Infrastructure-as-code / terminal | **GPT-5.3-Codex** | Sonnet 4.6 | — |
| 13 | One-shot script (bash, python) | **Sonnet 4.6** | Gemini 3 Flash | — |
| 14 | Refactoring (cross-file) | **Opus 4.6** | GPT-5.2-Codex | — |
| 15 | Dependency upgrade / migration | **GPT-5.2-Codex** | Opus 4.6 | — |
| 16 | Stack-trace bug fix | **Any frontier** (cheapest) | — | — |
| 17 | Complex debug (race / cross-boundary) | **Opus 4.6** | GPT-5.4 | — |
| 18 | Performance optimization | **GPT-5.3-Codex** | Opus 4.6 | — |
| 19 | Unit test generation | **Sonnet 4.6** | Gemini 2.5 Pro | — |
| 20 | Integration / edge-case test design | **Opus 4.6** | Codex | — |
| 21 | Code review | **Codex + Opus (dual)** | — | Single-model review |
| 22 | Security audit | **Opus + Codex (dual)** | — | GPT-4o (10% clean rate) |
| 23 | Code docs / README | **Sonnet 4.6** | GPT-5.4 | Codex (too terse) |
| 24 | ADR / trade-off documentation | **Opus 4.6** | GPT-5.2 | — |
| 25 | Structured output / function calling | **GPT-5.4 strict** | Sonnet 4.6 | — |
| 26 | Long-context analysis (>200K) | **Gemini 2.5 Pro** | Opus 4.6 | Haiku |
| 27 | SQL generation | **Sonnet 4.6** (24/25) | GPT-5.4 mini (22/25, ¼ cost) | Codex (slow, 21/25) |
| 28 | Classification / extraction | **GPT-5.4 nano** | Haiku 4.5 | Opus |
| 29 | Long-horizon autonomous (>1h) | **Opus** (general) / **Codex** (terminal) | — | Gemini (spiral risk) |
| 30 | Data analysis / ETL | **Gemini 2.5 Pro** | Sonnet 4.6 | — |

Detailed criteria, edge cases, and confidence levels → `references/categories.md`.

## Decision Rules

These rules resolve ties and special cases. Apply them **after** the category lookup. Each cites the source evidence.

### Rule 1 — The 80/20 Escalation
> **Default to Sonnet 4.6. Escalate to Opus 4.6 only when** the unit involves architecture, multi-file refactor (>5 files), complex debug (race / cross-boundary), security audit, or long-horizon autonomous (>1h). Opus produces identical results to Sonnet on single-file work — paying 5x more is waste.
> *Source: NxCode 6-task comparison; Faros.ai Reddit synthesis.*

### Rule 2 — Stack-Trace Bugs Are Equal
> **All frontier models are equivalent on stack-trace debugging.** All 5 models tested correctly identified root cause on identical FastAPI traces. Use the cheapest you have access to. *Source: jdhodges.com 5-model test, April 2026.*

### Rule 3 — Race Conditions Justify Opus
> **Race conditions and cross-boundary bugs → Opus 4.6.** In a 90-day practitioner test, Opus diagnosed a race in 2 prompts that Sonnet spent 47 files chasing. The 5x premium is recouped on the first hard bug. *Source: alirezarezvani.medium.com 90-day comparison.*

### Rule 4 — Code Review Uses TWO Models
> **Always use Codex + Opus (or Codex + Sonnet) for code review and security audits.** Different models have different blind spots: Codex catches LIKE injection, race conditions, and logical errors that Claude misses; Claude's explanations are more actionable. Single-model review misses entire bug classes. *Source: J.D. Hodges head-to-head, April 2026.*

### Rule 5 — Terminal / DevOps → Codex
> **GPT-5.3-Codex: 77.3% Terminal-Bench vs Claude's 65.4%.** For bash, Docker, K8s, Terraform, CI/CD, infrastructure scripts: Codex wins. Exception: if the task also involves frontend, switch to Sonnet (Codex is documented as weak on FE). *Source: OpenAI Terminal-Bench, corroborated.*

### Rule 6 — Structured Output → GPT-5.4 Strict
> **Any task requiring guaranteed schema compliance (JSON, YAML, function calling) → GPT-5.4 with strict mode.** CFG-based enforcement makes non-conforming responses structurally impossible (~100%). Claude's native structured outputs hit 99.2%. For production microservices, GPT-5.4 is the safest bet. *Source: OpenAI docs; OpenAIToolsHub 300-call test.*

### Rule 7 — Frontend → Gemini 3.1 Pro, Sonnet, or Gemini 3 Flash
> **Frontend components: Gemini 3.1 Pro (flagship, "vibe coding" champion), Sonnet 4.6 (mid-tier default), or Gemini 3 Flash (budget).** GPT-5.3-Codex is documented as weak on frontend. Gemini 3 Flash is 6x cheaper than Gemini 3.0 Pro and scores higher on SWE-bench — adopted by JetBrains, Replit, Warp. *Source: Kilo Code evaluation; JetBrains adoption data; all three research synthesis reports name Gemini 3.1 Pro as the frontend leader.*

### Rule 8 — Long Context → Gemini 2.5 Pro
> **If the task needs >200K tokens AND is primarily analysis/summarization, route to Gemini 2.5 Pro.** Its 1–2M window with a generous free tier makes it ideal for "dump the whole codebase and ask". BUT: Gemini slows past 300–400K tokens, and Opus still wins for cross-file *reasoning* that requires precision. *Source: Reddit 15K-line refactor anecdote; Murat Firebase debugging case.*

### Rule 9 — Claude Context Degrades Past 400K
> **Even though Opus/Sonnet advertise 1M context, usable quality degrades past ~400K tokens.** For tasks pushing the limit, chunk explicitly OR switch to Gemini 2.5 Pro for the analysis sub-task. *Source: practitioner reports, Chroma Research 18-model context test.*

### Rule 10 — Haiku Is the Sub-Agent Default
> **For classification, extraction, boilerplate, or any work a junior would do: Haiku 4.5.** ~90% of Sonnet 4.5 quality at one-third the cost, with rigid JSON adherence. Use as default worker in any Claude-led agent team. Adopted by Augment Code for sub-agent routing. *Source: Augment Code adoption; practitioner consensus.*

### Rule 11 — Gemini 3 Flash Is the Cost King
> **78% SWE-bench Verified at $0.50/MTok input.** Outperforms Gemini 3 Pro on coding while being 6x cheaper. Default in JetBrains AI Chat, Junie, Replit, Warp, Figma, Amp. BUT: still has Gemini failure modes (hallucination spirals, state contamination). Never run unattended. *Source: Kilo Code; Google adoption announcements.*

### Rule 12 — GPT-5 Silent Failures Are Real
> **GPT-5 variants can produce code that runs but is wrong** — removing safety checks, fabricating outputs to avoid crashes (IEEE Spectrum, April 2026). Never trust "no errors" as success. On safety-critical code, prefer Claude. Always run independent tests. *Source: IEEE Spectrum, April 2026.*

### Rule 13 — Privacy → Local
> **If data cannot leave your infrastructure, route to local models.** High complexity → gpt-oss-120b (single 80GB GPU). Medium → Qwen3-Coder-Next (3B active, consumer hardware). Function-calling/RAG → Gemma 4 (Apache 2.0, 8B). Frontier-class is unavailable locally; expect a quality drop on architecture and complex debug. *Source: J.D. Hodges April 2026 head-to-head.*

### Rule 14 — Planning Quality > Model Choice
> **Once you reach a baseline model, output quality is mostly determined by how clearly the task is planned.** Spending more time in Step 2 (Sufficiency Check) and Step 4 (Categorize) beats upgrading the model. *Source: ShopBack engineer Hoang Nguyen, Jan 2026.*

### Rule 15 — Drafter-Reviewer Pattern (Speed + Quality)
> **For rapid iteration where final correctness still matters:** use a fast model (Codex-Spark, Gemini 3 Flash, GPT-5.4 mini) to generate drafts, then a flagship (Opus 4.6) to review/patch. 3x faster than reasoning-only, with no correctness loss. Apply when iteration speed dominates. *Source: Codex-Spark drafter-reviewer benchmark.*

Extended rules with full source citations → `references/rules.md`.

## Output Format

Emit a markdown document with this structure:

```markdown
# Routing Plan: <Task Name>

## Breakdown Assessment
- Input was [sufficiently / insufficiently] decomposed.
- [If insufficient: list which units failed which Sufficiency criterion and the proposed finer breakdown.]

## Global Context
- **Scope:** <single/multi-file, files touched, languages, frameworks>
- **Constraints:** <privacy, ecosystem, latency, framework versions>
- **Cost posture:** <quality-first / balanced / cost-optimized>

## Work Units

### Unit 1: <short imperative name>
- **Category:** #<n> <category name>
- **Assigned model:** <primary> [+ <secondary> if dual-model pattern]
- **Rationale:** <2–4 sentences. Cite the category number AND the rule number. Explain the type of work and why this model is best for that type.>
- **Context briefing:**
  - *Files to read:* <explicit paths or globs>
  - *Prior outputs:* <which earlier units this depends on>
  - *Constraints:* <style, framework version, libs allowed/banned, conventions>
  - *Acceptance criteria:* <measurable done>
- **Failure modes to watch:** <2–3 model-specific risks from `references/models.md`>
- **Budget hint:** <rough token range if known>

### Unit 2: ...

## Execution Order
1. Unit 1 (entry point)
2. Units 2 & 3 (parallel after Unit 1)
3. ...

## Cost Summary
- Flagship calls: N
- Mid-tier calls: M
- Fast calls: K
- Rough envelope: <ballpark or "unknown — depends on token counts">
```

## Worked Example

**Input:**
> "Migrate the `/users` REST API from Express+Mongoose to Fastify+Prisma. Preserve endpoints and response shapes. Add tests. Update OpenAPI spec."

**Output:**

```markdown
# Routing Plan: Express → Fastify+Prisma Migration for /users API

## Breakdown Assessment
Input was **insufficiently decomposed** — single sentence spans planning, schema, implementation, tests, docs across 3 model tiers. Failed Sufficiency criteria 1, 2, 3, 5. Proposed 8-unit breakdown below.

## Global Context
- **Scope:** Multi-file, TypeScript, Node backend, ~15 files in `src/routes/users/`.
- **Constraints:** Preserve API contract — no breaking changes to response shapes.
- **Cost posture:** Balanced.

## Work Units

### Unit 1: Migration plan + risk analysis
- **Category:** #15 Dependency upgrade / migration (also #2 planning)
- **Assigned model:** GPT-5.3-Codex (primary), Opus 4.6 (review)
- **Rationale:** Migration planning category — Codex's "touch the minimum necessary" approach reduces risk in large-repo upgrades (Rule 5). Opus reviews the plan for dependency-chain gaps (Rule 1: multi-file refactor escalation justified). The work type is sequencing-with-rollback, where conservative scoping matters more than cleverness.
- **Context briefing:**
  - *Files to read:* `src/routes/users/**/*.ts`, `src/models/User.ts`, `package.json`, `openapi.yaml`
  - *Prior outputs:* none (entry point)
  - *Constraints:* No endpoint removals; preserve response shapes; phased rollout.
  - *Acceptance criteria:* Phased plan with rollback points and risk-per-phase.
- **Failure modes:** Codex over-suggests scope ("Should I also do X?") — explicit "do not suggest extras"; Opus silent fallback to Sonnet under rate limit — verify model header.

### Unit 2: Prisma schema from Mongoose model
- **Category:** #6 Database schema design
- **Assigned model:** Sonnet 4.6
- **Rationale:** Single-artifact schema translation, well-scoped, single file. The 80/20 default applies (Rule 1) — Opus would produce identical output for this kind of structural translation.
- **Context briefing:**
  - *Files to read:* `src/models/User.ts`
  - *Prior outputs:* Unit 1 plan
  - *Constraints:* Prisma 5+, PostgreSQL target, preserve all indexes and unique constraints.
  - *Acceptance criteria:* `schema.prisma` compiles; index parity with source.
- **Failure modes:** Sonnet greenfield bias — may drop legacy constraints. Provide explicit "preserve all" instruction.

### Unit 3: Fastify route handlers (one per endpoint)
- **Category:** #11 Backend service / REST endpoints
- **Assigned model:** Sonnet 4.6
- **Rationale:** Standard REST handler implementation, where Sonnet has High-confidence first-try success. The work type is well-scoped translation between two REST frameworks, not novel logic.
- **Context briefing:**
  - *Files to read:* current Express handler, Prisma schema (Unit 2 output), OpenAPI contract.
  - *Prior outputs:* Units 1, 2.
  - *Constraints:* Preserve status codes, error shapes, query params; one handler per call.
  - *Acceptance criteria:* Existing integration tests still pass.
- **Failure modes:** Sonnet "haphazard multi-file changes" — constrain to one handler per call.

### Unit 4: Unit tests for each handler
- **Category:** #19 Unit test generation
- **Assigned model:** Sonnet 4.6
- **Rationale:** Test generation is Sonnet's strongest area. Opus would add marginal edge cases at 5x cost — not worth it for unit-level tests (Rule 1).
- **Context briefing:** Handler code (Unit 3), test framework config, existing test style guide.
- **Failure modes:** ~40% mutation kill rate across all models — don't trust generated tests as exhaustive coverage.

### Unit 5: Integration test for migration parity
- **Category:** #20 Integration / edge-case test design
- **Assigned model:** Opus 4.6
- **Rationale:** Cross-boundary coverage (request → handler → Prisma → DB) is exactly where Opus catches edge cases others miss ("webhook replay, partial refund rounding"). The work type is *contract verification across two stacks* — flagship reasoning earns its premium here.
- **Context briefing:** Both old and new routes, sample payloads, prior bug reports.
- **Failure modes:** Opus may suggest unrelated refactors — explicit negative constraint.

### Unit 6: OpenAPI spec update
- **Category:** #25 Structured output
- **Assigned model:** GPT-5.4 (strict mode)
- **Rationale:** OpenAPI is schema-bound output where strict mode guarantees validity (Rule 6). Claude could do this at 99.2% but GPT-5.4 strict is the production-safe choice.
- **Context briefing:** New handler signatures, old OpenAPI spec, target file path.
- **Failure modes:** GPT-5.4 loses long system-prompt constraints — keep prompt lean and re-inject schema.

### Unit 7: Security review of auth paths
- **Category:** #22 Security audit
- **Assigned model:** **Opus 4.6 + GPT-5.3-Codex** (dual)
- **Rationale:** Rule 4 — different blind spots. Opus catches auth-flow logic issues; Codex catches concrete injection and race vulnerabilities. Merge findings.
- **Context briefing:** All new handler files, schema, middleware.
- **Failure modes:** Iterating on security review worsens outcomes (37.6% increase in critical vulns after 5 iterations) — one-shot review, do not iterate.

### Unit 8: CHANGELOG and migration guide
- **Category:** #23 Code docs / README
- **Assigned model:** Sonnet 4.6
- **Rationale:** Natural prose, low cost; Codex would be too terse for migration guides.
- **Context briefing:** Diff summary, Units 1–7 outputs.
- **Failure modes:** — (routine task)

## Execution Order
1. Unit 1 (planning)
2. Unit 2 (schema) — after Unit 1
3. Units 3 & 4 (handlers + tests) — parallel per endpoint, after Unit 2
4. Units 5 & 6 (integration test + OpenAPI) — parallel after Unit 3
5. Unit 7 (security review) — after Unit 3 completes
6. Unit 8 (docs) — last

## Cost Summary
- Flagship calls (Opus): 1 review (Unit 1) + Unit 5 + Unit 7 → ~3
- Mid-tier calls (Sonnet/Codex/GPT-5.4): ~8
- Fast calls: 0
- Rough envelope: budget 4–8h of agentic developer time; flagship dominates token cost.
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Routing "implement feature X" to one model | Run Sufficiency Check first; break into plan → schema → impl → tests → review → docs |
| Using Opus for boilerplate | Rule 10: Haiku or GPT-5.4 nano. Opus is 10x cost waste here. |
| Single-model code review | Rule 4: dual-model is mandatory for review and security |
| Ignoring Claude context degradation past 400K | Rule 9: chunk explicitly or hand off to Gemini 2.5 Pro |
| Trusting "no errors" from GPT-5 as success | Rule 12: always run independent tests |
| Picking by vibes instead of category lookup | Category lookup first, decision rules second |
| Omitting failure-mode warnings in briefings | Include 2–3 per unit from `references/models.md` |
| Routing private code to API models | Rule 13: check privacy in Step 1; route to local (Qwen3 / Gemma 4) |
| Routing frontend to Codex | Codex is documented as weak on frontend; use Sonnet or Gemini 3 Flash |
| Rationale doesn't cite a category # or rule # | Not evidence-based — re-do |

## Red Flags — STOP and Re-Route

- **The same model is selected for every unit** → you're defaulting, not routing. Re-apply categories.
- **No rationale cites a category number or rule number** → not evidence-based.
- **Context briefing says "the whole repo"** → chunk it or use long-context model.
- **Any unit estimated >1h autonomous runtime without a circuit breaker** → add iteration limit and time cap.
- **Privacy constraint exists but model is API-hosted** → re-route to local.

## Data Freshness

This skill reflects practitioner evidence as of **April 2026**. The model landscape shifts monthly. Re-validate quarterly.

Models covered:
- Anthropic: Claude Opus 4.6 (Feb 5 2026), Sonnet 4.6 (Feb 17 2026), Haiku 4.5 (Oct 2025)
- OpenAI: GPT-5.4 / 5.4 Pro / 5.4 mini / 5.4 nano (Mar 5 2026), GPT-5.3-Codex, GPT-5.2-Codex (retiring Jun 5 2026), GPT-4.1
- Google: Gemini 3.1 Pro (Feb 19 2026), Gemini 3 Flash, Gemini 2.5 Pro/Flash/Flash-Lite
- Open-weight: Qwen3-Coder-Next, Gemma 4, gpt-oss-120b/20b, MiniMax M2.5

## References

- `references/models.md` — Full model profiles: pricing, context, sweet spots, weaknesses, failure modes.
- `references/categories.md` — All 30 task categories with confidence levels and edge cases.
- `references/rules.md` — Extended decision rules with full source citations.
