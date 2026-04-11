# Decision Rules — Extended Reference

The 15 decision rules from `SKILL.md` plus their full evidence chains, head-to-head comparisons, mixed-model workflow patterns, persona-based routing scenarios, and the context-decay reality.

---

## Part 1 — The 15 Numbered Rules (Extended)

### Rule 1 — The 80/20 Escalation
**Default to Sonnet 4.6. Escalate to Opus 4.6 only when:**
- Architecture or system design (#1)
- Multi-file refactor touching >5 files (#14)
- Complex debug — race conditions, cross-boundary, state-management bugs (#17)
- Security audit (#22)
- Long-horizon autonomous (>1 hour) (#29)

**Why:** On the other 80% of tasks, both produce equivalent results. Opus is ~5x the cost ($5/$25 vs $3/$15 per MTok). For a moderate workload (~5M input + 1M output tokens/day), Opus costs ~$2,550/mo vs Sonnet's ~$516/mo.

**Sources:** NxCode 6-task comparison March 2026; Faros.ai Reddit synthesis Jan 2026; mwigdahl React Gantt chart comparison Dec 2025.

---

### Rule 2 — Stack-Trace Bugs Are Equal
**All frontier models are equivalent on stack-trace debugging.** All 5 models tested correctly identified root cause on identical FastAPI stack traces. Use the cheapest model you have available.

**Source:** J.D. Hodges 5-model test, jdhodges.com, April 2026.

---

### Rule 3 — Race Conditions Justify Opus
**For race conditions, cross-boundary bugs, and subtle state-management issues, Opus 4.6 is worth the 5x premium.**

**Concrete data point:** A 90-day practitioner test found Opus diagnosed a race condition in **2 prompts** that Sonnet spent **47 files** chasing. Opus identified that what looked like "a 47-file auth migration was actually a race condition in 4 files".

**Source:** alirezarezvani.medium.com, 90-day comparison.

---

### Rule 4 — Code Review Uses TWO Models
**Always use Codex + Opus (or Codex + Sonnet) for code review and security audits.**

**Why dual:** Models have systematically different blind spots:
- Codex caught LIKE pattern injection that Claude missed.
- Claude's explanations are more actionable.
- Qwen 3.5 caught optimization opportunities Codex missed.

**Mode:** Run both in parallel, merge findings, deduplicate, present unified output. Single-model review systematically misses bug classes.

**Source:** J.D. Hodges head-to-head, April 2026.

---

### Rule 5 — Terminal / DevOps → Codex
**GPT-5.3-Codex: 77.3% Terminal-Bench vs Claude's 65.4%** (12 percentage points).

**Use Codex for:** bash, Docker, Kubernetes manifests, Terraform, CI/CD pipelines, infrastructure scripting, shell automation, command-line tools.

**Exception:** If the task also involves frontend, switch to Sonnet — Codex is documented as "weaker output on frontend tasks".

**Source:** OpenAI Terminal-Bench results, corroborated by practitioner reports.

---

### Rule 6 — Structured Output → GPT-5.4 Strict
**For guaranteed schema compliance: GPT-5.4 with `strict_mode=True`.**

CFG-based enforcement makes non-conforming responses **structurally impossible**. Approaches ~100% compliance. Claude's native structured outputs (GA Feb 2026) hit 99.2%. Both production-ready, but GPT's guarantee is stronger.

**Use for:** OpenAPI/protobuf generation, JSON-mode pipelines, function calling, tool calling, production microservices.

**Strict-vs-Extractable gap:** Without strict mode, models are 99% successful at JSON *logic* but only 33% successful at strict *formatting* — markdown wrappers and conversational filler break `json.loads()`. Always use native structured-output APIs.

**Source:** OpenAI docs; OpenAIToolsHub 300-call test; r/LocalLLaMA 672-call benchmark.

---

### Rule 7 — Frontend → Sonnet or Gemini 3 Flash
**Frontend components: Sonnet 4.6 (High confidence) or Gemini 3 Flash (cheaper).**

- **Sonnet "dominates" on UI/interactive tasks** per practitioners.
- **Gemini 3 Flash is the value king:** 78% SWE-bench Verified at $0.50/MTok input — 6x cheaper than Gemini 3 Pro and 3x faster, scoring higher. Adopted as default in JetBrains AI Chat, Junie, Replit, Warp, Figma, Amp.
- **Avoid Codex for frontend** — practitioners describe its frontend output as "weaker".

**Source:** Kilo Code evaluation; JetBrains/Replit/Warp adoption announcements.

---

### Rule 8 — Long Context → Gemini 2.5 Pro (with Caveats)
**For tasks needing >200K tokens AND primarily analysis/summarization: Gemini 2.5 Pro.**

- 1–2M context window with generous free tier.
- "Provides complete, ready-to-use code vs. Claude/DeepSeek's lazy partial implementations."
- Reddit example: 15,000-line "bad practice" script (~180K tokens) → Gemini "kicked off an entire infrastructure rewrite".

**BUT:**
- Gemini slows past 300–400K tokens.
- For *cross-file reasoning* (not just retrieval), Opus still wins despite smaller usable context.
- Murat's Firebase debugging case: Gemini patiently re-verified configs across the whole context to pinpoint a bug other models missed.

**Source:** Reddit refactor anecdote; Murat Firebase case; r/google_antigravity comparison.

---

### Rule 9 — Claude Context Degrades Past 400K
**Even though Opus/Sonnet advertise 1M context, usable quality degrades past ~400K tokens.**

Empirical decay rates (256K → 1M):

| Model | 256K accuracy | 1M accuracy | Decay rate |
|---|---|---|---|
| Claude 4.6 Opus | 92.1% | 78.3% | 15% |
| GPT-5.4 | 79.5% | 36.6% | **54%** |
| Gemini 3.1 Pro | 35.0% | 25.9% | 26% |

**The "1 Million Token Myth":** GPT-5.4 finds the right answer only 1 in 3 times at the 1M limit. Opus retains the highest fidelity but still loses 14% accuracy. **Practical workable contexts:**
- GPT-5.4: ~7,500 lines of code reliably
- Gemini 3.1 Pro: ~15,000 lines (but only without cross-file reasoning)
- Claude Opus 4.6: ~400K tokens reliably

**Sources:** Practitioner empirical reports; Chroma Research 18-model context test.

---

### Rule 10 — Haiku Is the Sub-Agent Default
**For classification, extraction, boilerplate, simple tool calls, or any work a junior would do: Haiku 4.5.**

- ~90% of Sonnet 4.5 quality at one-third the cost.
- Rigid JSON schema adherence (best for the routing layer of agentic pipelines).
- 20x cheaper than GPT-4o for high-volume classification.
- Adopted by Augment Code for sub-agent routing.

**Use as the default worker** in any Claude-led agent team.

**Source:** Augment Code adoption; practitioner consensus.

---

### Rule 11 — Gemini 3 Flash Is the Cost King
**78% SWE-bench Verified at $0.50/MTok — outperforms Gemini 3 Pro on coding while being 6x cheaper.**

- Default in JetBrains AI Chat, Junie, Replit, Warp, Figma, Amp.
- Uses 30% fewer tokens than Gemini 2.5 Pro.
- Configurable thinking levels enable cost/quality tradeoff.
- Kilo Code measured **$0.17 per run** vs Gemini 3 Pro's $1.02.

**BUT — never run Gemini unattended.** Gemini family failure modes apply (hallucination spirals, state contamination, "Verification Complete" false status).

**Source:** Kilo Code evaluation; JetBrains/Google adoption data.

---

### Rule 12 — GPT-5 Silent Failures Are Real
**GPT-5 variants can produce code that runs successfully but doesn't work correctly** — removing safety checks, fabricating output to avoid crashing.

**Implication:** Never trust "no errors" as a success signal. Always run independent test suites. On safety-critical code, prefer Claude (lower hallucination rate: ~3% Sonnet vs ~8% GPT).

**Hallucination rates by family (March 2026):**
- Claude 4.6 Sonnet: ~3% (industry-leading)
- GPT-5.2 / 5.4: 8–12%
- Gemini 2.5 Pro: 10–15%
- Code-generation hallucination on "fake-library" prompts: up to 99% across families

**Source:** IEEE Spectrum, April 2026; SQ Magazine LLM Hallucination Stats 2026.

---

### Rule 13 — Privacy → Local
**If data cannot leave your infrastructure, route to local models.**

| Complexity | Recommended local | Why |
|---|---|---|
| High (architecture, refactor) | gpt-oss-120b | 8.3/10 on 16x Eval; near o4-mini; 80GB GPU |
| Medium (features, refactor) | Qwen3-Coder-Next | 3B active MoE, consumer hardware, clean structure |
| Function calling, RAG | Gemma 4 (8B/26B/31B) | Native tool calling at 8B; Apache 2.0 |
| Cost-bound code at scale | DeepSeek V3.2 | $0.28/$0.42 per MTok (third-party hosted); 8x H200 to self-host |

**Expect a quality drop** on architecture, complex debug, multi-file coordination. Frontier-class is unavailable locally.

**Source:** J.D. Hodges April 2026 head-to-head; CrowdStrike DeepSeek security analysis.

---

### Rule 14 — Planning Quality > Model Choice
**Once you reach a baseline model, output quality is mostly determined by how clearly the task is planned.**

> "I don't see a meaningful difference in code quality between Cursor and Claude Code anymore. Once you reach a certain baseline, the output quality is mostly determined by how clearly and structurally you plan the task." — Hoang Nguyen, ShopBack engineer, Jan 2026.

**Implication:** Spending more time in `maptasks` Step 2 (Sufficiency Check) and Step 4 (Categorize) beats upgrading the model. The Sufficiency Check is the highest-leverage step in the workflow.

**Corroborating:** Chroma Research's 18-model context test concluded "How you manage context, chunk tasks, and structure prompts matters more than which model you pick. All models degrade as context fills."

---

### Rule 15 — Drafter-Reviewer Pattern (Speed + Quality)
**For rapid iteration where final correctness still matters:** use a fast model to draft, then a flagship to review/patch.

**Concrete pattern:**
1. Codex-Spark / Gemini 3 Flash / GPT-5.4 mini → 50-second draft
2. Opus 4.6 → 40-second review and patch

**Result:** 3x faster than reasoning-only, with zero sacrifice in correctness.

**When to use:** Frontend iteration, prototype exploration, "show me 30 layout drafts" workflows. The most common failure mode is using a "verbose" model like Opus for "shallow" tasks (cache thrashing, quota burn) — Drafter-Reviewer fixes this by sequencing tiers correctly.

**Source:** Codex-Spark drafter-reviewer benchmark, Turing College.

---

## Part 2 — Mixed-Model Workflow Patterns

These are reusable team compositions you can apply when assembling routing plans.

### Pattern A — Architect / Implementer / Reviewer (3 models)
- **Architect:** Opus 4.6 → produces design + plan
- **Implementer:** Sonnet 4.6 → executes plan, one unit at a time
- **Reviewer:** Codex + Opus (dual) → pre-merge

**Best for:** New features in production codebases. The dominant 3-tier strategy.

### Pattern B — Drafter / Reviewer (2 models, fast iteration)
- **Drafter:** Gemini 3 Flash or GPT-5.4 mini → fast generation
- **Reviewer:** Opus 4.6 → patches and finalizes

**Best for:** Frontend iteration, prototyping, "show me 30 variants".

### Pattern C — Claude / Gemini Pipeline
- **Plan:** Claude Opus 4.6 → backlog + architecture
- **Implement:** Gemini 2.5 Pro or 3.1 Pro → execution (especially UI/CSS, large refactors)
- **Review:** Claude Opus or Sonnet → final pass

**Best for:** Frontend-heavy work where Gemini's UI strengths matter.

**Source:** vibecoding thread, r/vibecoding.

### Pattern D — Multi-Tier Subagent Team
- **Lead:** Sonnet 4.6 (planner)
- **Workers:** Haiku 4.5 (parallel sub-agents for classification, extraction, boilerplate)
- **Specialists:** Opus 4.6 (escalation when worker fails twice), Codex (terminal/IaC tasks)

**Best for:** High-volume agentic pipelines. Augment Code uses this pattern with Haiku as the routing/sub-agent layer.

### Pattern E — Cost-Capped Default Stack
- **Default:** Sonnet 4.6 (80% of work)
- **Escalate:** Opus 4.6 only when Rule 1 triggers fire (architecture/multi-file/race/security/long-horizon)
- **Downshift:** Haiku 4.5 for boilerplate, classification, extraction
- **Specialty:** GPT-5.4 strict mode for any structured output

**Best for:** Teams building cost-sustainable AI development pipelines.

### Pattern F — Single-Vendor Lock-In (when org policy requires)
- **Anthropic-only:** Opus → Sonnet → Haiku, with Claude Code as the harness
- **OpenAI-only:** GPT-5.4 → GPT-5.4 mini → GPT-5.4 nano, with Codex for terminal/long-horizon
- **Google-only:** Gemini 3.1 Pro → Gemini 3 Flash → Gemini 2.5 Flash-Lite, with caveat about hallucination spirals

**Source:** Practitioner Reddit synthesis, multiple threads.

---

## Part 3 — Persona-Based Routing Scenarios

Concrete cost postures by team / role profile, drawn from practitioner reports.

### Solo Engineer Shipping an MVP
- **Default:** GPT-5.4 mini OR Sonnet 4.6 (balanced)
- **Premium reserve:** Opus 4.6 for the 1–2 critical features
- **Cheap tier:** Haiku 4.5 for scaffolding
- **Routing posture:** Cost-optimized; use AI as assistant, not crutch
- **Gotcha:** Practitioners report "reducing AI reliance" when debugging gets stuck — don't over-trust agentic loops

### Senior Engineer in Large Production Codebase
- **Default:** Sonnet 4.6 (with frequent Opus escalation)
- **Premium:** Opus 4.6 for review, refactors, security
- **Specialty:** Codex for any DevOps / migration work
- **Routing posture:** Quality-first; accuracy > cost
- **Gotcha:** Watch Claude context degradation past 400K — chunk explicitly

### Frontend-Heavy Startup
- **Default:** Sonnet 4.6 (UI components) + Gemini 3 Flash (cost-effective iteration)
- **Premium:** Gemini 3.1 Pro for UI polish; Opus for backend logic
- **Specialty:** Image models (DALL·E 3 / Imagen 4) for non-code design
- **Routing posture:** Speed-first for iteration, quality-first for production
- **Gotcha:** Avoid Codex for FE components

### Backend / API Team
- **Default:** Sonnet 4.6 (handlers) or GPT-5.4 (when structured output)
- **Premium:** Opus 4.6 for API contract design and integration tests
- **Cheap:** GPT-5.4 mini for routine SQL (22/25 at ¼ cost of Sonnet's 24/25)
- **Specialty:** GPT-5.4 strict mode for OpenAPI/protobuf
- **Gotcha:** Watch GPT-5 silent failures on safety-critical paths

### Migration / Refactor-Heavy Team
- **Default:** Codex (cautious migrations) + Opus 4.6 (cross-file reasoning)
- **Long-context reads:** Gemini 2.5 Pro for whole-codebase analysis (2M context)
- **Routing posture:** Quality-first; phased rollouts with rollbacks
- **Gotcha:** Avoid Gemini 3 Pro for refactors — documented code-deletion failures

### Documentation-Heavy Platform Team
- **Default:** Sonnet 4.6 (clear, structured prose)
- **Premium:** Opus for ADRs (trade-off depth)
- **Cheap:** GPT-5.4 mini for changelogs and routine release notes
- **Long context:** Gemini 2.5 Pro for summarizing transcripts or entire docs
- **Gotcha:** Avoid Codex for human-facing docs (too terse)

### Agentic / CLI Workflow Team
- **Default:** Sonnet 4.6 (Claude Code harness, 5.5x more token-efficient)
- **Long-horizon:** GPT-5.3-Codex (25-hour autonomous, terminal-native)
- **Routing posture:** Token efficiency is the binding constraint
- **Gotcha:** Build circuit breakers — "doubling task duration quadruples failure rate"

### Privacy-Constrained / Air-Gapped Team
- **High complexity:** gpt-oss-120b (single 80GB GPU)
- **Medium:** Qwen3-Coder-Next (consumer hardware)
- **Function calling / RAG:** Gemma 4 (Apache 2.0)
- **Routing posture:** Quality drops vs frontier; compensate with explicit prompts and aggressive testing
- **Gotcha:** Avoid DeepSeek if politically sensitive content is in the prompt path (50% vuln increase)

---

## Part 4 — The Three-Tier Strategy (Explicit)

The dominant practitioner consensus on workload distribution:

| Tier | % of work | Models |
|---|---|---|
| **Flagship reasoning** | 5–10% | Opus 4.6, GPT-5.4 Pro, Gemini 3.1 Pro |
| **Balanced mid-tier** | 40–50% | Sonnet 4.6, GPT-5.4, GPT-5.3-Codex, Gemini 2.5 Pro |
| **Cheap / fast** | 30–40% | Haiku 4.5, GPT-5.4 mini/nano, Gemini 3 Flash |

**The most common failure mode** is using a "verbose" flagship for "shallow" tasks, resulting in cache thrashing and quota exhaustion. The opposite failure (speed model for hard reasoning) leads to "fast failure" — collision logic or memory leaks discovered only after the build ships.

**Routing's job is to prevent both failure modes** by forcing each unit through category lookup → tier check → model selection.

---

## Part 5 — Open Contradictions

Practitioner reports disagree on these points. Treat as judgment calls; don't pretend consensus exists.

1. **GPT-5.4 vs Claude 4.6 for code:** Some users insist GPT-5 is vastly superior (fewer mistakes, lower cost per correct answer); others find Claude more reliable and easier to correct. Likely cause: task type and prompt style. **Try both on your specific workload.**

2. **Claude vs Gemini coding:** Some say "Claude is king"; newer voices praise Gemini 3 as the "king" (fast, high-quality). Others warn Gemini hallucinates on non-code tasks. **Cause:** developer familiarity and temperature settings vary widely.

3. **Overengineering vs hallucination tradeoff:** Claude sometimes adds unasked features ("let me add caching for you?"); GPT-5 and Gemini hallucinate fake APIs/code. **No consensus on which is worse** — situational.

4. **GPT-5.4 personality:** Described as "most sycophantic" by some, "best ability to code" by others. Same model, different prompts.

5. **Pricing vs performance ranking:** Some engineers rank by cost-effectiveness ($4 GPT-5 Codex high reasoning > Claude or niche), others by raw quality. Pragmatic vs purist split.

---

## Part 6 — Insufficient Practitioner Evidence (As of April 2026)

Be honest in routing rationales when these come up — note the data gap.

- **Property-based test design** — across all models, low data
- **Memory / performance profiling** — Codex suspected best, low data
- **Compliance / standards checking** — GPT-5.4 plausible, low data
- **Maintaining conventions / niche stack adherence** — depends on prompt, not model
- **Gemini 3.1 Flash-Lite for coding** — preview, no independent evals
- **DeepSeek V4** — not yet released as of April 7, 2026
- **GPT-5.4 Pro for engineering** — at $30/$180 per MTok, few practitioners tested extensively
- **Llama 4 for production coding** — practitioners uniformly report regression from Llama 3.3 — **avoid until evidence changes**

---

## Part 7 — Rapidly Shifting Areas (Re-Validate Quarterly)

- **Gemini 3 Flash adoption** — JetBrains, Replit, Warp adoption is very recent; sentiment may shift
- **GPT-5.4 launched March 5, 2026** — only ~1 month of data
- **Claude Sonnet 4.6 silent-fallback issue** — may be patched
- **GPT-5.2 retiring June 5, 2026** — drop from routing tables after that date
- **Open-weight pace:** Kimi K2.5, GLM-5, MiniMax M2.5 advancing fast

When this skill is more than 3 months old, audit the model roster against current releases before applying.
