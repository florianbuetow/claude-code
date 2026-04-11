# Task Category Reference

The 30 task categories used by `maptasks`. Each category has a precise definition, primary/runner-up model, confidence level, evidence source, and selection criteria. Use this to ground every routing decision.

**Confidence levels:**
- **High** = multiple independent practitioner reports agree
- **Medium** = 2–3 consistent reports or one rigorous comparison
- **Low** = limited data or conflicting reports

---

## Planning & Architecture

### #1 — Architecture / system design
**Definition:** High-level design decisions: component boundaries, data flow, layering, integration topology.
**Primary:** Claude Opus 4.6 (High)
**Runner-up:** GPT-5.4 Pro (Medium)
**Avoid:** —
**Why Opus:** Maps interdependencies before proposing changes. Acts like a "disciplined senior engineer who reads the blueprint before picking up a tool". Sonnet loses dependency chains in 15+ file contexts.
**Use Opus when:** new system, redesign of existing module, or any decision that constrains future work.

### #2 — Task decomposition / planning
**Definition:** Breaking a feature into ordered, scoped subtasks; sequencing work; identifying parallelism.
**Primary:** Claude Opus 4.6 (Medium)
**Runner-up:** GPT-5.4 (Medium)
**Why Opus:** Reaches optimal solutions in ~4 iterations vs ~10 for Sonnet — cuts orchestration overhead by 60%.

### #3 — Tech-stack / tradeoff analysis
**Definition:** Comparing libraries, frameworks, or approaches; producing a recommendation with tradeoffs.
**Primary:** Claude Opus 4.6 (Low)
**Runner-up:** GPT-5.2 (Low)
**Why Opus:** Produces "review comments that sound like they came from a thoughtful senior developer" on tradeoff analysis.

### #4 — Spec writing (business → technical)
**Definition:** Turning vague requirements or business asks into a concrete technical spec.
**Primary:** Claude Opus 4.6 (Medium)
**Runner-up:** Claude Sonnet 4.6 (Low)
**Avoid:** Cursor Composer-2 (interprets and proceeds without clarification)
**Why Opus:** Asks for clarification on ambiguity. Better understands business intent — GPT-5 "writes syntactically correct code but misses underlying business rules".

---

## Specification & Contract Work

### #5 — API contract design (OpenAPI / protobuf)
**Definition:** Designing or formalizing service contracts in a machine-readable schema.
**Primary:** Claude Sonnet 4.6 (Medium)
**Runner-up:** GPT-5.4 (Medium)
**Why Sonnet:** Structured output and instruction following rated highest by ~70% of developers surveyed. For schema *enforcement*, escalate to GPT-5.4 strict mode.

### #6 — Database schema design
**Definition:** Designing tables, indexes, constraints, migrations.
**Primary:** Claude Sonnet 4.6 (Low)
**Runner-up:** Gemini 2.5 Pro (Low)
**Why Sonnet:** Limited direct comparisons but Sonnet's structural translation quality dominates this category.

---

## Code Generation

### #7 — Greenfield feature implementation
**Definition:** Writing new features from scratch in an existing codebase, well-scoped (<500 lines).
**Primary:** Claude Sonnet 4.6 (High)
**Runner-up:** GPT-5.4 (High)
**Why Sonnet:** "Gets things right on the first try more often"; ~80% one-shot success rate. GPT-5.4 generates faster for tighter iteration loops — pick based on whether you optimize for first-try correctness or iteration speed.

### #8 — Boilerplate / scaffolding
**Definition:** Pattern-following code: file skeletons, repetitive class structures, CRUD scaffolds.
**Primary:** Claude Haiku 4.5 (Medium)
**Runner-up:** GPT-5.4 nano (Medium)
**Avoid:** Claude Opus 4.6 (10x+ cost waste)
**Why Haiku:** Cheapest option that works. Pattern-following is exactly its sweet spot.

### #9 — Algorithm implementation
**Definition:** Implementing a known or specified algorithm correctly, with attention to micro-optimizations.
**Primary:** Claude Opus 4.6 (Medium)
**Runner-up:** GPT-5.3-Codex (Medium)
**Why Opus:** Both score A in head-to-head, but Codex catches micro-optimizations Opus misses (list vs string concat). Use Codex when performance matters most.

### #10 — Frontend components (React, Vue, CSS)
**Definition:** UI components, styling, interactive elements, layout.
**Primary:** Gemini 3.1 Pro (Medium)
**Runner-up:** Claude Sonnet 4.6 (High), Gemini 3 Flash (Medium, budget)
**Avoid:** GPT-5.3-Codex (documented as "weaker output on frontend tasks")
**Why Gemini 3.1 Pro:** All three research synthesis reports name it the frontend/UI champion — "vibe coding" leader, animated SVGs, 3D experiences, "made the frontend 10x better in 15 minutes." Sonnet remains the mid-tier default with high first-try success. Gemini 3 Flash is the budget option (78% SWE-bench at $0.50/MTok, adopted by JetBrains/Replit/Warp). Note: Gemini 3.1 Pro is flagship tier — use Sonnet when cost-optimized.

### #11 — Backend service / REST endpoints
**Definition:** Server logic, route handlers, validation, DB queries, business logic.
**Primary:** Claude Sonnet 4.6 (High)
**Runner-up:** GPT-5.4 (High)
**Why Sonnet:** "Generated route handler, validation schema, DB query with proper joins — worked on first try" per practitioner testing. Both produce working REST endpoints first try.

### #12 — Infrastructure-as-code / terminal
**Definition:** Terraform, Kubernetes manifests, Docker, bash scripts, CI/CD pipelines, shell automation.
**Primary:** GPT-5.3-Codex (Medium)
**Runner-up:** Claude Sonnet 4.6 (Medium)
**Why Codex:** 77.3% Terminal-Bench vs Claude's 65.4%. Terminal-native strength is the dominant factor.

### #13 — One-shot script (bash, Python)
**Definition:** Single-purpose, small (<200 lines), self-contained scripts.
**Primary:** Claude Sonnet 4.6 (High)
**Runner-up:** Gemini 3 Flash (Medium)
**Why Sonnet:** All frontier models handle simple scripts well; Sonnet's one-shot rate is "about 4 in 5" per practitioner testing.

---

## Code Modification

### #14 — Refactoring (cross-file)
**Definition:** Restructuring code that spans multiple files; preserving behavior.
**Primary:** Claude Opus 4.6 (High)
**Runner-up:** GPT-5.2-Codex (Medium)
**Avoid:** —
**Why Opus:** Tracks type dependencies across module boundaries. Critical for refactors that touch >5 files.

### #15 — Dependency upgrade / migration
**Definition:** Library version upgrades, framework migrations, breaking-change handling.
**Primary:** GPT-5.2-Codex (Medium)
**Runner-up:** Claude Opus 4.6 (Medium)
**Why Codex:** "Touches the minimum necessary" — cautious approach reduces risk in large repos. Use Opus when migration also needs deep architectural reasoning.

---

## Debugging

### #16 — Stack-trace bug fix
**Definition:** Bug with a clear error trace, identifiable root cause within a single file or module.
**Primary:** Any frontier model (use cheapest)
**Why:** "All 5 models correctly identified root cause" in head-to-head testing. Don't pay 5x more for the same fix.

### #17 — Complex debug (race condition / cross-boundary)
**Definition:** Bugs spanning components, async issues, state-management bugs, intermittent failures.
**Primary:** Claude Opus 4.6 (High)
**Runner-up:** GPT-5.4 (Medium)
**Why Opus:** Excels at "race conditions, cross-boundary bugs, subtle state management". 90-day test: Opus diagnosed a race in 2 prompts that Sonnet spent 47 files chasing.

### #18 — Performance optimization
**Definition:** Improving runtime, memory, or throughput without changing behavior.
**Primary:** GPT-5.3-Codex (Medium)
**Runner-up:** Claude Opus 4.6 (Medium)
**Why Codex:** Adds micro-optimizations others miss in head-to-head. Terminal-native strength suggests advantage on profiling work.

---

## Testing

### #19 — Unit test generation
**Definition:** Tests for individual functions, classes, or modules in isolation.
**Primary:** Claude Sonnet 4.6 (High)
**Runner-up:** Gemini 2.5 Pro (Medium)
**Why Sonnet:** "Test writing is one of Sonnet's strongest areas" per NxCode. Opus adds edge cases but rarely worth the 5x premium. Note universal failure: ~40% mutation kill rate across all models.

### #20 — Integration / edge-case test design
**Definition:** End-to-end tests, edge cases, contract tests across boundaries.
**Primary:** Claude Opus 4.6 (Medium)
**Runner-up:** GPT-5.3-Codex (Medium)
**Why Opus:** Caught "webhook replay attacks and partial refund arithmetic rounding" edge cases others missed. Codex catches race conditions and logical errors Claude misses — consider dual-model for high-stakes integration tests.

---

## Review & Quality

### #21 — Code review
**Definition:** Reviewing code diffs for bugs, style, correctness, security.
**Primary:** **Codex + Opus (DUAL)**
**Why dual:** Different blind spots — Codex caught LIKE injection that Claude missed; Claude's explanations are more actionable. Single-model review systematically misses bug classes.
**Mode:** Run both, merge findings, deduplicate.

### #22 — Security audit
**Definition:** Scanning code for vulnerabilities, auth flow review, threat modeling.
**Primary:** **Opus + Codex (DUAL)**
**Avoid:** GPT-4o (10% vulnerability-free outputs)
**Why dual:** Opus found 500+ unknown vulnerabilities in open-source code. Codex catches concrete injection patterns. Don't iterate — 37.6% increase in critical vulns after 5 iterations.

---

## Documentation

### #23 — Code docs / README / docstrings
**Definition:** Inline documentation, READMEs, onboarding guides, code explanations.
**Primary:** Claude Sonnet 4.6 (Medium)
**Runner-up:** GPT-5.4 (Medium)
**Avoid:** GPT-5.2-Codex (felt "too terse for documentation")
**Why Sonnet:** Natural prose, structured output, good tone for human readers.

### #24 — ADR / trade-off documentation
**Definition:** Architecture Decision Records — capturing the *why* behind a decision and its alternatives.
**Primary:** Claude Opus 4.6 (Medium)
**Runner-up:** GPT-5.2 (Low)
**Why Opus:** Better at capturing trade-off reasoning. ADRs need depth of analysis, not just prose.

---

## Structured Output & Tool Use

### #25 — Structured output / function calling
**Definition:** Producing JSON/YAML/XML output that must validate against a schema; calling tools/functions.
**Primary:** GPT-5.4 strict mode (High)
**Runner-up:** Claude Sonnet 4.6 (Medium)
**Why GPT-5.4:** CFG-based enforcement makes non-conforming responses structurally impossible (~100% schema compliance with strict mode). Claude's native structured outputs hit 99.2%. For production microservices, GPT-5.4 is the safest bet. Tool calling: "half the tool calling error rate" of alternatives.

---

## Long Context

### #26 — Long-context analysis (>200K tokens)
**Definition:** Summarizing, searching, or reasoning over very large inputs (whole codebases, big documents).
**Primary:** Gemini 2.5 Pro (High)
**Runner-up:** Claude Opus 4.6 (Medium)
**Avoid:** Claude Haiku (200K limit)
**Why Gemini:** 1–2M context with generous free tier. Murat's Firebase example: pinpointed an HTTPS bug that other models missed by keeping all context. Note: slows past 300–400K tokens. For *cross-file reasoning* (not just retrieval), Opus still wins despite smaller usable context.

---

## Specialized

### #27 — SQL generation
**Definition:** Writing SQL queries for analytics, ETL, or application use.
**Primary:** Claude Sonnet 4.6 (High) — 24/25 on Lothian SQL benchmark
**Runner-up:** GPT-5.4 mini (Medium) — 22/25 at ¼ cost
**Avoid:** GPT-5.3-Codex (slower, scored 21/25)
**Why Sonnet:** Best benchmark score. But cheaper alternatives at 22/25 may be sufficient for routine queries — check cost sensitivity.

### #28 — Classification / extraction
**Definition:** Tagging, categorization, named-entity extraction, information extraction from text.
**Primary:** GPT-5.4 nano (Medium) — $0.20/MTok
**Runner-up:** Claude Haiku 4.5 (Medium)
**Avoid:** Opus (vast cost waste)
**Why nano:** Best for high-volume classification, extraction, guardrails. Both nano and Haiku produce comparable quality on routine extraction.

### #29 — Long-horizon autonomous (>1h continuous)
**Definition:** Fire-and-forget agentic work that runs unattended for hours.
**Primary (general):** Claude Opus 4.6 — sustained 7-hour autonomous refactor (Rakuten)
**Primary (terminal/DevOps):** GPT-5.3-Codex — 25-hour coherent session documented
**Avoid:** Gemini 2.5 Pro (enters hallucination spirals when unattended)
**Why split:** Opus best for general planning + execution loops. Codex best when the work is terminal-bound. Always use circuit breakers (max iterations, time limits).

### #30 — Data analysis / ETL
**Definition:** Data transformation pipelines, exploratory analysis, summarization of datasets.
**Primary:** Gemini 2.5 Pro (Medium)
**Runner-up:** Claude Sonnet 4.6 (Medium)
**Why Gemini:** 1M context and free tier make it ideal for "dump the whole dataset and ask". Strong R / data-science workflow support.

---

## Categories Without Sufficient Practitioner Evidence

For these, fall back to category #7 (greenfield) or #11 (backend) and rely on decision rules:

- Property-based test design (across all models)
- Memory / performance profiling (GPT-5.3-Codex suspected best, low data)
- DevOps observability code
- Compliance / standards checking (GPT-5.4 plausible due to structured output)
- Maintaining conventions / niche stack adherence

When routing one of these, note in the rationale: "Limited practitioner data; defaulting to category X by analogy."
