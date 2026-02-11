---
name: explain-system-tradeoffs
version: 1.0.0
description: >
  This skill should be used when the user asks to "explain system tradeoffs",
  "analyze architecture tradeoffs", "what tradeoffs does this system make",
  "reverse-engineer design decisions", "audit distributed system design", or
  "explain the design choices in this codebase". Also triggers when the user
  mentions a tradeoff axis by name (e.g., "consistency vs availability",
  "latency vs throughput", "CAP theorem", "PACELC", "sharding tradeoffs",
  "resilience patterns", "data distribution strategy"). Supports analyzing
  all six axes at once or focusing on a single axis.
---

# Explain System Tradeoffs

Reverse-engineer distributed system tradeoffs from code, configuration, deployment
manifests, and architecture artifacts. Produce an evidence-based report that explains
what the system prioritizes, what it sacrifices, where choices appear deliberate versus
accidental, and what risks or misalignments deserve attention.

Every distributed system encodes its design tradeoffs in artifacts hiding in plain
sight — configuration files, schema definitions, deployment manifests, timeout values,
retry policies, and code patterns. This skill reads those artifacts like an
architectural blueprint.

## Evidence Tiers

When evaluating evidence, use three tiers to weigh confidence:

- **Tier A (hard commitments):** User-facing API/SLA language; explicit consistency or
  transaction guarantees; quorum/replication rules; schema invariants; wire-protocol
  requirements.
- **Tier B (mechanism evidence):** Concrete mechanisms that enforce the property —
  consensus protocols, leases, retry state machines, outbox tables, circuit breaker
  configs, compaction strategies, GC flags.
- **Tier C (operational signatures):** Dashboards, alerts, runbooks, incident
  postmortems, sampling configs, SLO definitions that reveal what engineers actually
  protect and what they sacrifice.

When indicators disagree, prefer artifacts closest to runtime behaviour (Tier C and B)
over architecture documentation that may be stale (Tier A language in old design docs).

## Subcommands

Request a full analysis or focus on a single tradeoff axis:

| Command Pattern | Axis | Reference |
|----------------|------|-----------|
| `explain-system-tradeoffs` | All six axes | All references |
| `explain-system-consistency-tradeoffs` | Consistency & Availability | `references/consistency.md` |
| `explain-system-latency-tradeoffs` | Latency & Throughput | `references/latency.md` |
| `explain-system-data-tradeoffs` | Data Distribution | `references/data-distribution.md` |
| `explain-system-transaction-tradeoffs` | Transaction Boundaries & Coordination | `references/transactions.md` |
| `explain-system-resilience-tradeoffs` | Resilience & Failure Isolation | `references/resilience.md` |
| `explain-system-operations-tradeoffs` | Observability, Security & Cost | `references/operations.md` |

When no subcommand is specified, default to analyzing all six axes.
When a tradeoff axis is mentioned by name or concept (even without the command prefix),
match it to the appropriate subcommand.

## Workflow

### Single-Axis Mode

When a single axis is requested (e.g., `explain-system-consistency-tradeoffs`),
execute the analysis directly in the main agent:

1. **Identify the target** code, configuration, or architecture to analyze.
2. **Read the reference file** for the requested axis.
3. **Scan the codebase** for indicators described in the reference.
4. **Build an evidence ledger** and report findings (see Report Format below).

### Full Analysis Mode (Parallel Subagents)

When all six axes are requested (`explain-system-tradeoffs`), use **parallel
subagents** to analyze each axis concurrently. This is faster and produces
better results because each subagent can focus deeply on one axis.

**CRITICAL — How parallel execution works:** The Task tool runs subagents in
parallel ONLY when multiple Task tool calls appear in the SAME response message.
If you emit them across separate messages, they run sequentially. You MUST
include all six Task tool calls in a single response to get concurrency.

#### Step 1. Identify Target System

Determine what code, configuration, or architecture to analyze:
- When files or a directory are provided, use those.
- When a service, module, or system is referenced by name, locate it.
- When ambiguous, ask which files, directories, or services to scan.

Resolve the target to a concrete set of paths before launching subagents.
This MUST be done before Step 2 — subagents get their own isolated context
window and cannot see the conversation history or resolve ambiguous targets.

#### Step 2. Launch Six Parallel Subagents

Emit **exactly six Task tool calls in a single response message**. This is
what triggers concurrent execution. Do NOT emit them one at a time.

Technical requirements for each Task call:
- `subagent_type`: `"general-purpose"`
- `description`: Short label (e.g., `"Analyze consistency tradeoffs"`)
- `prompt`: A **fully self-contained** prompt (see template below). Each
  subagent gets its own 200k context window and cannot see the main
  conversation, so the prompt must include everything it needs.

Each subagent prompt must include:
1. The **concrete target paths** to analyze (resolved in Step 1).
2. The **absolute path to its reference file** to read first.
3. The **evidence tier definitions** (Tier A/B/C — copy them into the prompt).
4. The **per-axis report format** (copy it into the prompt).
5. An instruction to **return structured findings only** — no summary, no
   cross-axis commentary (the main agent handles synthesis).

The six subagents and their reference files:

| Subagent | Reference to read | Focus |
|----------|------------------|-------|
| Consistency & Availability | `references/consistency.md` | CAP/PACELC position, replication, quorum, cache freshness, conflict resolution |
| Latency & Throughput | `references/latency.md` | GC tuning, thread pools, batching, deadlines, hedging, storage engines, rate limiting |
| Data Distribution | `references/data-distribution.md` | Shard keys, partition strategies, replication topology, data sovereignty |
| Transaction Boundaries | `references/transactions.md` | Monolith vs microservices, sagas, outbox, schema evolution, API contracts, dependencies |
| Resilience & Failure Isolation | `references/resilience.md` | Circuit breakers, retries, bulkheads, chaos engineering, progressive delivery, service mesh |
| Observability, Security & Cost | `references/operations.md` | Tracing, SLOs, mTLS, audit trails, compliance, cost/reliability topology |

**Subagent prompt template** (adapt the axis name, reference path, and focus
for each of the six — but keep the structure identical):

```
Analyze the distributed system tradeoffs for the CONSISTENCY & AVAILABILITY axis
in the codebase at: <TARGET_PATHS>

STEP 1: Read the reference file at:
<ABSOLUTE_PATH_TO_SKILL_DIR>/references/consistency.md

STEP 2: Scan the target codebase for indicators described in the reference.
Search configuration files, code patterns, deployment manifests, and schema
definitions. Use Glob, Grep, and Read tools to find evidence.

STEP 3: For each piece of evidence found, classify it:
- What: The specific artifact (file path, config key, code pattern)
- Tier: A (hard commitment — SLA language, quorum rules, schema invariants),
        B (mechanism evidence — protocols, configs, GC flags, compaction),
        or C (operational signature — dashboards, alerts, SLOs, runbooks)
- Reveals: Which end of the tradeoff spectrum the system leans toward
- Deliberate vs Default: Whether intentional (asymmetric config, tuned values)
  or accidental (framework defaults, copy-pasted settings)

STEP 4: Produce your findings in EXACTLY this format:

## Consistency & Availability

**Position:** [Where the system sits on the consistency/availability spectrum]
**Confidence:** HIGH | MEDIUM | LOW

### Evidence
[Numbered list of evidence items with Tier, File, and Detail for each]

### Assessment
[1-2 paragraphs on the tradeoff position and whether it appears deliberate]

### Risks & Recommendations
[Any risks found, each with: Severity (HIGH/MEDIUM/LOW), Location, Issue,
Recommendation. If no risks found, state "No significant risks identified."]

IMPORTANT: Return ONLY the per-axis report above. Do NOT produce a cross-axis
summary or tradeoff profile — the main agent handles cross-axis synthesis.
```

#### Step 3. Wait for All Subagents

**CRITICAL — Do NOT continue analysis while subagents are running.** After
launching the six subagents, your ONLY job is to wait for their results. Do NOT:
- Scan the codebase yourself for any axis
- Produce per-axis reports yourself
- "Continue" the analysis if some subagents finish before others
- Fill idle time by doing the subagents' work

The subagents are doing the analysis. You are the synthesizer. Wait for all six
to return before proceeding to Step 4.

If a subagent fails or returns an error, note the failure and proceed with the
remaining results. Do NOT redo the failed subagent's work yourself — report that
the axis could not be analyzed and suggest re-running it as a single-axis command.

#### Step 4. Synthesize Results

After all six subagents return their results, the main agent:

1. **Collects** the six per-axis reports from the subagent results.
2. **Presents** them sequentially to the user.
3. **Produces the cross-axis synthesis** (see Summary section in Report Format).
   This is the main agent's unique contribution — it identifies tensions and
   interactions between axes that no individual subagent can see.

### Identifying the Target

Look across the **four planes** where distributed system tradeoffs surface:
- **Interface and behavioural contracts:** API docs, SLA language, consistency claims.
- **Configuration surfaces:** Replication factors, quorum sizes, timeout defaults,
  retry budgets, sampling rates, consistency levels.
- **State and background work:** Repair queues, outbox tables, dead-letter queues,
  retry schedules, leases, epochs.
- **Operational tooling and telemetry:** Tracing, context propagation, error budgets,
  SLO definitions, dashboards, alerts.

### Evidence Ledger

For each tradeoff axis, collect concrete evidence from the codebase using the indicators
in the reference files. For each piece of evidence, note:
- **What:** The specific artifact (file, config key, code pattern, API contract).
- **Tier:** A, B, or C.
- **Reveals:** Which end of the tradeoff spectrum the system leans toward.
- **Deliberate vs Default:** Whether the choice appears intentional (asymmetric config,
  tuned values, documented rationale) or accidental (framework defaults, copy-pasted
  settings, uniform config across all dimensions).

## Report Format

### Per Tradeoff Axis

```
## [AXIS NAME]

**Position:** Where the system sits on this tradeoff spectrum.
**Confidence:** HIGH | MEDIUM | LOW (based on evidence tier and consistency)

### Evidence

1. **[Artifact]** — [What it reveals]
   Tier: A/B/C | File: `path/to/file`, lines ~XX-YY
   Detail: Specific explanation of what this artifact tells us.

### Assessment

[1-2 paragraphs explaining the tradeoff position, whether it appears deliberate,
and how it interacts with other axes.]
```

### Risks & Recommendations

After presenting each axis, flag issues using this structure:

```
**Risk — Severity: HIGH | MEDIUM | LOW**
Location: `filename` or `service/module`, lines ~XX-YY
Issue: What appears accidental, misaligned, or risky about this tradeoff position.
Recommendation: Concrete change to align the configuration with the system's
stated or inferred goals.
```

Severity guidelines:
- **HIGH**: Configuration contradicts the system's apparent goals, creates production
  risk, or indicates a misunderstood default that could cause data loss or outages.
- **MEDIUM**: Suboptimal configuration that will cause problems at scale or under
  failure conditions. Often a default that should have been tuned.
- **LOW**: Minor misalignment or missing hardening. Worth noting for maturity but
  not urgent.

### Summary (Main Agent Only — Full Analysis Mode)

After all axes, the main agent produces a cross-axis synthesis:
- **Tradeoff Profile:** A compact summary of the system's position on each axis
  (e.g., "AP-leaning with tunable consistency, throughput-optimized, shard-first
  with rack-aware replication").
- **Maturity Signals:** Whether the system shows deliberate asymmetry (different
  configs per table/service/endpoint) or uniform defaults. Deliberate asymmetry
  is the hallmark of genuine tradeoff-making.
- **Risk count table:** `| Axis | HIGH | MEDIUM | LOW |`
- **Top 3 priorities:** Which risks to address first and why.
- **Cross-axis tensions:** Where tradeoff choices on one axis conflict with choices
  on another (e.g., AP consistency with synchronous saga coordination).

## Deep Dive Mode (Optional)

When the user asks to "explain this tradeoff further", "what should we change", or
"how do we fix this", provide:
- Detailed analysis of the specific tradeoff or risk.
- Concrete configuration changes, code modifications, or architecture proposals.
- Impact assessment: what improves and what gets worse with each recommendation.
- Alternative approaches if the tradeoff could be resolved differently.

## Pragmatism Guidelines

Tradeoffs are decisions, not violations. Apply judgment:

- **Defaults are not always wrong.** A system using framework defaults may be
  correctly sized for its current scale. Flag defaults as "untuned" rather than
  "wrong" and recommend review, not immediate change.
- **Scale matters.** A single-service CRUD app doesn't need the same distributed
  systems rigor as a platform serving millions of requests. Calibrate severity
  to the system's actual scale and requirements.
- **Tradeoffs interact.** Consistency choices affect latency. Resilience patterns
  affect throughput. Data distribution affects transaction boundaries. Flag
  interactions and tensions, don't analyze axes in isolation.
- **Some "misalignments" are intentional.** A system that is AP overall but uses
  strong consistency for payment transactions is making a deliberate per-endpoint
  choice, not a mistake. Look for per-operation configuration knobs as evidence
  of intentional mixed strategies.
- **Evidence beats assumptions.** If you can't find concrete artifacts for an axis,
  say "insufficient evidence" rather than guessing. Missing configuration is itself
  a finding (the tradeoff was not explicitly considered).
- **Prefer insight over exhaustiveness.** Five well-evidenced tradeoff findings
  beat twenty speculative ones.

## Example Interactions

### Single axis (direct analysis)

**User**: `explain-system-consistency-tradeoffs` (with a codebase directory)

**Claude**:
1. Reads `references/consistency.md`
2. Scans the codebase for consistency/availability indicators (replication config,
   quorum settings, cache TTLs, schema compatibility modes, sync_commit flags)
3. Builds an evidence ledger with tiers
4. Reports the system's consistency/availability position with evidence
5. Flags any risks (e.g., default replication factor, missing quorum config)
6. Provides recommendations

### Full analysis (parallel subagents)

**User**: `explain-system-tradeoffs` (with a full system)

**Claude**:
1. Resolves the target paths from the user's input
2. Launches **six subagents in parallel** (one per axis), each reading its
   reference file and scanning the codebase independently
3. Collects the six per-axis reports as subagents complete
4. Presents the per-axis findings to the user
5. Produces the **cross-axis synthesis**: tradeoff profile, maturity signals,
   risk count table, top 3 priorities, and cross-axis tensions
