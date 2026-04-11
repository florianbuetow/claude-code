# Model Profiles

Detailed reference for every model in the routing roster. Each profile includes: sweet spot, weaknesses, agentic reliability, cost-performance notes, and known failure modes. Source: synthesized from 500+ practitioner reports compiled through April 2026.

---

## Claude Opus 4.6

- **Version:** `claude-opus-4-6-20260205` | **Released:** Feb 5, 2026
- **Pricing:** $5 / $25 per MTok (input / output)
- **Context:** 1M tokens advertised, **~400K reliable**
- **Benchmarks:** SWE-bench Verified 80.8%, Terminal-Bench 65.4%

**Sweet spot:** Large multi-file refactors, system architecture decisions, complex root-cause analysis (race conditions, cross-boundary bugs), security audits, long-running autonomous agentic tasks (validated 7+ hours by Rakuten). Best-in-class for "disciplined senior engineer" reasoning.

**Weaknesses:**
- Overkill for routine tasks — produces identical results to Sonnet on single-file work.
- Sometimes "improves" things you didn't ask for (greenfield bias).
- **Rate limiting on Pro plan ($20/mo)** makes it impractical as a daily driver; realistically requires Max plan ($100–200/mo).
- **Context degrades past ~400K tokens** despite 1M advertised window.
- Token-heavy: GitHub issue #23706 documents 5–10x context usage of previous models, often 6–8% of session quota in a single prompt.
- "Approach volatility" — abandons paths quickly. See failure modes table: advantage on complex debug, risk on straightforward tasks.

**Cost-performance:** For ~5M input + 1M output tokens/day, Opus costs ~$2,550/mo vs Sonnet at ~$516/mo. Reserve for the 10–20% of tasks that demonstrably need it.

**Agentic reliability:** Best-in-class. 16 agents built a 100,000-line C compiler. Primary risk: silent fallback to Sonnet when rate-limited (Claude Code GitHub issue #3434) — breaks context.

**Failure modes (severity):**
| Failure | Severity | Workaround |
|---|---|---|
| Context degradation past 400K | High | Use `/compact`, fresh sessions, "one task one context" |
| Greenfield bias / legacy collapse | High | Provide explicit architectural context |
| Sycophantic agreement (58% Stanford study) | High | Have model answer first, then show user opinion |
| Silent fallback to Sonnet under rate limit | High | Use Max plan; monitor model header |
| Approach volatility (abandons paths quickly) | Conditional | Advantage on complex debug — avoids sunk-cost loops (50-day improvement over 4.5 on Sokoban). Risk on straightforward tasks where persistence is better. |
| "Improving" unrequested code | Low | Explicit negative constraint in prompt |

---

## Claude Sonnet 4.6

- **Version:** `claude-sonnet-4-6-20260217` | **Released:** Feb 17, 2026
- **Pricing:** $3 / $15 per MTok | **Context:** 1M, ~400K reliable
- **Benchmarks:** SWE-bench Verified 79.6%, SQL Lothian 24/25

**Sweet spot:** The **80% model**. Daily feature implementation, bug fixing, unit/integration test generation, documentation, API design, SQL generation, frontend components. ~80% one-shot success rate on well-scoped tasks. Preferred by 70% of developers for instruction following.

**Weaknesses:**
- Loses dependency chains in 15+ file changes.
- **Hedges in 34% of code review comments** ("might", "could", "possibly").
- "Haphazard multi-file changes" reported when not tightly constrained.
- Inconsistent quality week-over-week per multiple practitioners.
- 2.4% refusal rate on coding requests (highest of any model).

**Cost-performance:** Best value among frontier-quality models for most engineering tasks. For test writing, single-file bugs, standard features: "no meaningful quality difference" vs Opus.

**Agentic reliability:** Strong for scoped tasks. Best used as implementer when Opus serves as planner. Claude Code uses 5.5x fewer tokens than Cursor for identical tasks.

**Failure modes:**
| Failure | Severity | Workaround |
|---|---|---|
| Circular debugging | Medium | Start fresh context when proposing rejected solutions |
| Haphazard multi-file changes | Medium | Enforce small diffs; require plan with rollback |
| Hedging in code review (34%) | Medium | Use Opus or Codex for decisive reviews |
| Refusal of valid coding requests (2.4%) | Medium | Rephrase; remove security-adjacent ambiguity. For unattended pipelines, Rule 1 already escalates to Opus/Codex. |

---

## Claude Haiku 4.5

- **Version:** `claude-haiku-4-5-20251022` | **Released:** Oct 2025
- **Pricing:** $0.80 / $5 per MTok | **Context:** 200K

**Sweet spot:** Sub-agent workhorse, high-volume classification, boilerplate generation, simple scripting, strict JSON output. ~90% of Sonnet 4.5 performance at one-third the cost. Adopted by Augment Code for sub-agent routing.

**Weaknesses:** Not suited for complex reasoning, architecture, or multi-file coordination. Limited 200K context.

**Cost-performance:** Use as default for any task where output is indistinguishable from a frontier model. Compounds dramatically at scale.

**Agentic reliability:** Adequate for simple tool-calling loops. Not for long-horizon autonomous work.

---

## GPT-5.4

- **Version:** `gpt-5.4-2026-03-05` | **Released:** Mar 5, 2026
- **Pricing:** $2.50 / $15 per MTok (doubles past 272K input → $5)
- **Context:** 1.05M
- **Benchmarks:** SWE-bench 79.1%, OSWorld (Computer Use) 75% — surpasses 72.4% human baseline

**Sweet spot:** Structured output / function calling (99.7% schema compliance), fast iteration on greenfield code, straightforward debugging, computer-use tasks, mid-task steering via "Thinking" feature. Best single-model choice for teams wanting one API to handle everything.

**Routing signal — mid-task steering:** GPT-5.4 can be interrupted and redirected mid-generation. For iterative architecture or planning work where assumptions shift during generation, this is a tie-breaker vs Opus (which must restart). Consider for categories #1 and #2 when the task involves exploration with frequent course corrections.

**Weaknesses:**
- SWE-bench trails Claude (79.1% vs 80.8%).
- Still hallucinates ~8% of factual claims in long outputs.
- "Trained to be conversational and role-playing" rather than task-focused per HN.
- **Critical: GPT-5 variants produce code that runs but is wrong** (IEEE Spectrum, April 2026) — removing safety checks, fabricating outputs.
- Loses constraints in system prompts longer than a few hundred words.
- Price doubles past 272K tokens.

**Cost-performance:** Sits between Sonnet and Gemini 3.1 Pro. Auto-routing reasoning depth (5 levels) helps optimize cost per task.

**Agentic reliability:** "Half the tool calling error rate" of alternatives (per Cursor). 5-level reasoning effort control.

**Failure modes:**
| Failure | Severity | Workaround |
|---|---|---|
| Silent failures — runs but wrong | **Critical** | Always run independent tests; never trust "no errors" |
| Sycophancy / role-playing | Medium | Higher reasoning effort; explicit constraints |
| Loss of system prompt constraints | Medium | Keep prompts concise; re-inject mid-conversation |
| xhigh reasoning latency | Medium | Reserve xhigh for when medium/high fail |

---

## GPT-5.4 mini / nano

- **Released:** Mar 17, 2026
- **mini:** $0.75 / $4.50 per MTok, 400K context, SWE-bench Pro 54.4%
- **nano:** $0.20 / $1.25 per MTok, 400K context, SWE-bench Pro 52.4%

**Sweet spot (mini):** "Almost indistinguishable from full GPT-5.4" on routine tasks per TechRadar. 2x faster than GPT-5 mini. Good sub-agent model.

**Sweet spot (nano):** Classification, extraction, guardrails, high-volume pipelines. "Even nano beats last year's $20/month ChatGPT on real coding tasks." Outperforms GPT-5 mini at maximum reasoning effort per Simon Willison.

**Avoid nano for:** Computer use (39% OSWorld), complex architecture, multi-file coordination.

**Failure modes:**
| Failure | Severity | Workaround |
|---|---|---|
| Hallucinated APIs (mini, 26% with one-char misspelling) | Medium | Spell-check library names; RAG with current docs |
| Duplicate tool calls (nano with parallel) | Low | Disable parallel tool calls |

---

## GPT-5.3-Codex

- **Pricing:** ~$2.50 / $15 per MTok
- **Benchmarks:** Terminal-Bench 77.3% (industry-leading)

**Sweet spot:** Long-horizon autonomous coding (25-hour coherent session documented), terminal/DevOps tasks, code review ("rigid reviewer energy" catches logical errors, race conditions, edge cases Claude misses). Built itself during training. Best GitHub integration per Builder.io team.

**Weaknesses:**
- "Erratic behavior in extended sessions" most common complaint.
- **Weak on frontend tasks.**
- Over-suggests scope expansion ("Should I also do X?").
- "Felt too terse for documentation" per practitioners.
- Slower than alternatives for interactive work.

**Cost-performance:** Roughly half Claude's cost with comparable quality. Codex Pro plan users "almost never hit limits" unlike Claude's tight rate caps. 4x more token-efficient than Claude Code.

**Agentic reliability:** Strong for fire-and-forget autonomous tasks in sandboxed environments.

**Failure modes:**
| Failure | Severity | Workaround |
|---|---|---|
| Erratic behavior in extended sessions | Medium | Set iteration limits; restart on looping |
| Scope creep / over-suggestion | Low | Explicit "do not suggest additional tasks" |
| Context compaction loops | Medium | Monitor for repeated steps; restart |

---

## GPT-5.2 / GPT-5.2-Codex

- **Retiring:** June 5, 2026
- **Pricing:** $1.75 / $14 per MTok

**Sweet spot:** "Slow but careful" — cautious refactors in large repos, one-shotting hard problems at xhigh reasoning, code review as "rigid reviewer". GPT-5.2 for planning/review, GPT-5.2-Codex for implementation. Still preferred by practitioners who need maximum correctness on risky changes.

**Weaknesses:** Extremely slow at xhigh. Context compaction loopiness in long tasks. Retiring soon.

---

## GPT-4.1

- **Pricing:** $2 / $8 per MTok | **Context:** 1M

**Sweet spot:** Large-context instruction following, paste-in-entire-codebases analysis, teams who want a non-reasoning model with clear control. "Followed a 15-step instruction set flawlessly." 40% faster code review cycles.

**Weaknesses:** Not a reasoning model — less assertive than Claude/Gemini. gpt-4.1-nano can produce duplicate tool calls with parallel calling enabled.

---

## Gemini 3.1 Pro

- **Released:** Feb 19, 2026
- **Pricing:** $2 / $12 per MTok (preview pricing $2-4 / $12-18)
- **Context:** 1M+
- **Benchmarks:** MMLU 94.1%, ARC-AGI-2 77.1%, SWE-bench 63.8%

**Sweet spot:** Cheapest frontier-tier per output token. Strong on abstract reasoning. Frontend / UI / "vibe coding" champion. Google ecosystem (Go, Dart/Flutter, Angular). Massive context for whole-monorepo analysis.

**Weaknesses:**
- SWE-bench only 63.8% — significantly behind Claude and GPT.
- 2.3x slower response time than GPT-5.4.
- Predecessor (Gemini 3 Pro) has documented "spiral" failures — monitor closely.
- "Lunacy" after long sessions — hallucinates input sizes.

---

## Gemini 2.5 Pro

- **Pricing:** $1.25 / $10 per MTok (≤128K) | **Context:** 1M-2M

**Sweet spot:** Long-context analysis of entire codebases, R/data science workflows, large-document analysis, cost-effective alternative when Claude's quality isn't strictly needed. "Provides complete, ready-to-use code vs. Claude/DeepSeek's lazy partial implementations." 1M context with generous free tier.

**Weaknesses:**
- "Complete garbage" at pixel-perfect UI translation.
- General reasoning "very bad" on tasks requiring leaps beyond training patterns.
- Slowdown past 300–400K tokens.
- Makes unrequested changes.

**Agentic reliability:** Adequate but not best-in-class. Prone to "state contamination" — relies on cached intuition over explicit context.

**Failure modes (Gemini family broadly):**
| Failure | Severity | Workaround |
|---|---|---|
| Hallucination spirals | **Critical** | Never run unattended; verify each step |
| Execution hallucination (claims tool calls happened) | **Critical** | Restart session immediately if detected |
| State contamination | High | Re-provide critical context each turn |
| Code deletion during modifications | High | Aggressive version control; review diffs |
| Stray syntax (closing braces in SwiftUI) | Medium | Manual review before compilation |
| Temperature <1.0 causes looping | Medium | Don't lower temperature for reasoning |
| Structured output hurts reasoning | Medium | Use JSON-Prompt over JSON-Schema |
| "Verification Complete" false status | High | Never trust self-reported verification |

---

## Gemini 3 Flash

- **Pricing:** $0.50 / $3 per MTok | **Context:** 1M
- **Benchmarks:** SWE-bench Verified 78% — outperforms Gemini 3 Pro (76.2%)

**Sweet spot:** **The cost-effective coding model of 2026.** Adopted as default by JetBrains (AI Chat + Junie), Replit, Warp, Figma, Amp. Uses 30% fewer tokens than Gemini 2.5 Pro. Configurable thinking levels enable cost/quality tradeoff. Kilo Code test: 90% average across 3 coding tests at $0.17 total.

**Weaknesses:** Still a Flash-tier model — not for complex architecture or security audits. Gemini family hallucination tendencies apply.

**Cost-performance:** 6x cheaper than Gemini 3 Pro and 3x faster, scoring higher on SWE-bench. The Gemini model to use when optimizing cost.

---

## Gemini 2.5 Flash / Flash-Lite

**Sweet spot:** High throughput, cost-effective bulk processing. Flash-Lite is the cheapest multimodal model.

**Weaknesses:** Less powerful than Pro; limited multi-step reasoning.

---

## DeepSeek V3.2

- **Pricing:** $0.28 / $0.42 per MTok | **Context:** 128K
- **Benchmarks:** SWE-bench 68.4% with thinking mode

**Sweet spot:** Best bang-for-buck on standard coding tasks. "GPT-5-High-level performance" at 90% less cost. Cost-sensitive teams or high-volume pipelines.

**Weaknesses:**
- Requires 8x H200 GPUs to self-host.
- 128K context is limiting.
- **Politically-triggered security degradation: vulnerabilities increase up to 50% with politically sensitive prompts** (CrowdStrike).
- No native tool calling (V3.x).
- "Underthinking" — switches reasoning paths without exploration.
- Outputs entire files when asked for diffs.

---

## Qwen3-Coder-Next

- **Pricing:** Free (Apache 2.0) | **Active params:** 3B (80B total MoE)

**Sweet spot:** Best local coding model in practitioner tests. Runs on consumer hardware. Produced clean project with proper src/ layout, class-based architecture, 14 passing tests on first run. "If you want something that runs correctly the first time, Qwen3 Coder Next is the better bet" vs other local models.

**Weaknesses:** Not competitive with frontier on complex tasks. Instruction following "not particularly good" — verbose blocks when asked for diffs only. TypeScript narrowing 1/10.

---

## Gemma 4

- **Pricing:** Free (Apache 2.0) | **Sizes:** 8B (E4B), 26B MoE, 31B Dense

**Sweet spot:** Local function calling and structured output. Native tool calling in 8B is significant — runs via `ollama pull gemma4`. Good for offline code review, RAG pipelines, privacy-sensitive work. Scored A- (matching paid models) on refactoring and feature implementation in head-to-head.

**Weaknesses:** VRAM demands for larger variants. Not competitive with frontier on complex tasks.

---

## gpt-oss-120b / gpt-oss-20b

- **Pricing:** ~$0.15 / $0.60 per MTok via providers, or free self-hosted | **License:** Apache 2.0

**Sweet spot (120b):** Top open-source coding model per 16x Eval (8.3/10 — surpasses GPT-4.1). Runs on single 80GB GPU. Near o4-mini parity on reasoning. Refactored 400-line React component cleanly with proper hook extraction in ~12 seconds. Deep mode identifies subtle race conditions.

**Sweet spot (20b):** Runs on 16GB consumer hardware. Matches or exceeds 120B on several tasks at 5x lower energy.

**Weaknesses:** Inherent verbosity even with "be concise" instructions. Text-only. Less suitable for multilingual or specialized domains. 8 months old — newer open-source models (Kimi K2.5, GLM-5) have advanced.

---

## GPT-5.4 Pro

- **Pricing:** ~$21 / $168 per MTok (practitioner reports) or ~$30 / $180 (LLM Decision Guide) — sources disagree
- **Context:** 1M tokens
- **Released:** Mar 5, 2026

**Sweet spot:** OpenAI's high-intelligence "Thinking" mode for the most ambitious agentic prompts: build-a-whole-feature-set, multi-module refactors that require sustained planning, complex creative coding. The "Computer Use" capability (75% OSWorld — surpasses 72.4% human baseline) lets it interact with desktop environments (terminal, browser, IDE) without external wrapper agents. Native "Responses API" supports tool search and chained `previous_response_id` for evolving thinking blocks across turns.

**Sweet spot continued:** Mid-task steering — engineers can interrupt a long-running generation to correct an architectural assumption.

**Weaknesses:**
- Extremely expensive — ~few practitioners have tested extensively at $21–30/MTok input.
- "Decently meh" for creative tasks vs Claude family's prose quality.
- Inherits all GPT-5 family failure modes (silent failures, sycophancy, role-playing tendency).

**Use when:** Architecture + multi-module implementation in one session, where mid-task steering matters AND budget allows. Otherwise prefer Opus 4.6 (cheaper) or GPT-5.4 standard.

---

## o3 / o4-mini

**Sweet spot (o3):** Multi-step logical reasoning, function calling, structured outputs, hardware debugging root cause analysis. Strong at STEM reasoning (87.7% GPQA Diamond).

**Sweet spot (o4-mini):** Quick CSS fixes, simple syntax errors, learning aid for junior developers. 300 messages/day on Pro.

**Weaknesses (o3):** Consistently behind Claude for interactive UI coding. Community describes as "mid at everything" for actual coding. Slow.

**Weaknesses (o4-mini):** Shallow reasoning. May hallucinate nonexistent libraries. Not for architecture.

---

## Codex-Spark

- **Hardware:** Cerebras
- **Throughput:** 1,000+ tokens/sec — 15x faster than standard Codex
- **SWE-bench Pro:** ~56% (correctness penalty for speed)

**Sweet spot:** Rapid prototyping, frontend iteration ("see 30 layout drafts in a single coffee break"). The drafter half of the **Drafter-Reviewer Pattern** (Rule 15): Spark drafts in 50 seconds, Opus 4.6 reviews and patches in 40 seconds — 3x faster than reasoning-only with no correctness loss.

**Weaknesses:** Significantly lower correctness than mainline Codex. Don't use for production code without a flagship reviewer pass. Don't use alone for architecture or complex debug.

**Use when:** Speed dominates the iteration loop AND a reviewer model will catch correctness issues.

---

## MiniMax M2.5

- **Pricing:** $0.30 per MTok input
- **Open-weight:** yes
- **SWE-bench:** ~80.2% (matches GPT-5.4)

**Sweet spot:** Frontier-level open-weight model for engineers who have the hardware (100GB+ VRAM) and want private, on-premise frontier performance. Cheapest path to GPT-5.4-class quality if you're self-hosting.

**Weaknesses:** Hardware requirements are steep for most teams. Less practitioner data than the closed frontier models.

**Use when:** Privacy / sovereignty constraints + hardware budget + need for frontier-class quality.

---

## Kimi K2.5

**Sweet spot:** Frontend specialist for competitive coding. Often used through platforms like Blackbox for unlimited, cheap generation. Noted as "fast and good enough" for most refactors and UI generation.

**Weaknesses:** Less practitioner data outside specific platforms. Not a general-purpose flagship.

---

## Qwen 3.5 Coder (older sibling of Qwen3-Coder-Next)

**Sweet spot:** The preferred local model for stable JSON extraction via `ollama` or `llama.cpp` — the "no-thinking" mode combined with GBNF grammars makes it the most stable local stack for simple logic + structured output.

**Use when:** You need on-device JSON / structured output and can't reach an API.

---

## Llama 4

**Status:** Practitioners uniformly report Llama 4 as a regression from Llama 3.3. **Avoid until evidence changes.**

---

## IDE / Tool-Host Considerations (relevant to routing)

These tools determine which models are practical to deploy in which workflows. Use this to inform which model your pipeline can actually call.

| Tool | Model Default | Notable Strength | Cost Model |
|---|---|---|---|
| **Claude Code** (terminal) | Opus 4.6 / Sonnet 4.6 | 1M context (Opus beta), 5.5x more token-efficient than Cursor for identical tasks | Pro $20 (rate-limited) / Max $100–200 |
| **Cursor** (IDE) | Sonnet 4.6 (Composer) | Multi-file Composer agent, Supermaven autocomplete | Usage-based credits |
| **Windsurf** (IDE) | Sonnet 4.6 (Cascade) | Persistent session context across files, $15/mo (25% cheaper than Cursor) | Subscription |
| **JetBrains AI Chat / Junie** | Gemini 3 Flash | Default for cost-efficiency | Subscription |
| **Replit / Warp / Figma / Amp** | Gemini 3 Flash | Adopted as default for coding | Varies |

**Routing implication:** When the user is in a specific tool, prefer routes that play to that tool's host model — switching models cross-tool incurs context loss and cost overhead.

---

## Cross-Model Universal Failure Modes

These apply to **every** model. Always include in failure-mode warnings on relevant units.

| Failure | Severity | Frequency | Mitigation |
|---|---|---|---|
| Hallucinated package names ("slopsquatting") | High | 200K+ fake packages detected; open-source 4x worse | Pin exact versions; verify packages exist |
| Insecure code generation | High | 12–65% of snippets non-compliant | Always run SAST/DAST; never trust unreviewed |
| Iterative "improvement" worsens security | High | 37.6% increase in critical vulns after 5 iterations | Don't iterate on security code; review each version independently |
| Test generation hits ~40% mutation kill rate | Medium | Systematic across all models | AI tests = starting point; manually verify edges |
| Context degradation (U-shaped) | High | Every model | Keep context lean; re-inject critical instructions |
| Premature assumptions in multi-turn | Medium | 39% performance drop | State assumptions; challenge model's understanding |
