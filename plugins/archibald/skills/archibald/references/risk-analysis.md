# Risk & Trade-off Analysis

This dimension draws from the Architecture Tradeoff Analysis Method (ATAM) and
related evaluation frameworks, adapted for code-level assessment by an AI agent
without requiring full stakeholder workshops.

## Core Concepts

### Risks

Architectural decisions that may lead to undesirable consequences. A risk is a
decision (or lack of decision) that creates potential for future problems.

**Examples:**
- Using a single database for all services (risk: single point of failure,
  schema coupling across domains).
- No caching strategy (risk: performance degradation under load).
- Synchronous communication between all services (risk: cascading failures,
  latency accumulation).

### Sensitivity Points

Parameters or decisions where small changes significantly affect quality
attributes. These are architectural "levers" with outsized impact.

**Examples:**
- Thread pool size for performance (too small = bottleneck, too large = resource
  exhaustion).
- Cache TTL for data freshness (too short = no benefit, too long = stale data).
- Dependency direction between two components for modifiability (reversing it
  changes which team can evolve independently).
- Retry count for reliability (too few = failures, too many = cascading overload).

### Trade-off Points

Decisions that affect multiple quality attributes in opposing directions. Improving
one attribute degrades another. These are not bugs to fix — they are tensions to
make explicit and manage consciously.

**Examples:**
- Caching improves performance but reduces data freshness.
- Encryption improves security but reduces performance.
- Microservice decomposition improves independent deployability but increases
  operational complexity.
- Redundancy improves availability but increases cost and consistency challenges.
- Abstraction improves modifiability but may reduce performance and readability.

## Quality Attribute Scenarios

A structured way to express quality requirements that can be evaluated against
the architecture. Each scenario has six parts:

1. **Source** — Entity generating the stimulus (user, system timer, external
   service, developer, operator).
2. **Stimulus** — Event affecting the system (request, failure, change request,
   load spike, new feature requirement).
3. **Environment** — System conditions when stimulus occurs (normal operation,
   peak load, degraded mode, development time).
4. **Artifact** — Component(s) affected by the stimulus (specific service,
   data store, API layer, entire system).
5. **Response** — How the system reacts to the stimulus (processes request,
   degrades gracefully, absorbs change, recovers).
6. **Response measure** — Quantifiable success criteria (latency < 200ms,
   recovery < 30s, change requires < 3 files, availability > 99.9%).

### Scenario Types

- **Use case scenarios**: Expected runtime behavior (normal operation).
- **Growth scenarios**: Anticipated changes and evolution (adding features,
  scaling, team growth).
- **Exploratory scenarios**: Stress cases and edge conditions (what if traffic
  10×s, what if this service goes down, what if requirements change radically).

### Example Scenarios

**Modifiability scenario:**
- Source: Developer
- Stimulus: Add new payment provider
- Environment: Design time
- Artifact: Payment processing module
- Response: New provider integrated
- Measure: < 4 hours effort, < 3 files modified

**Performance scenario:**
- Source: User
- Stimulus: Search request
- Environment: Peak load (10× normal)
- Artifact: Search service
- Response: Results returned
- Measure: 95th percentile latency < 500ms

**Availability scenario:**
- Source: Infrastructure
- Stimulus: Database primary node failure
- Environment: Normal operation
- Artifact: Data persistence layer
- Response: Failover to replica
- Measure: < 30 seconds downtime, zero data loss

## Conducting Risk Analysis from Code

When performing risk analysis on a codebase (without a full ATAM workshop):

### 1. Identify Architectural Decisions
Examine the codebase for decisions that have been made (explicitly or implicitly):
- Technology choices (database, messaging, frameworks).
- Decomposition choices (component boundaries, service splits).
- Communication patterns (sync vs. async, direct vs. event-driven).
- Data management (shared database, per-service storage, caching strategy).
- Error handling strategy (retries, circuit breakers, fallbacks).
- Deployment model (monolith, services, serverless).

### 2. Assess Each Decision for Risk
For each significant decision, ask:
- What quality attributes does this decision affect?
- What could go wrong? Under what conditions?
- How would the system behave under stress?
- What would it cost to change this decision later?

### 3. Identify Sensitivity Points
Look for configuration, parameters, or design choices where the system's
behavior would change significantly with small adjustments:
- Timeout values, pool sizes, batch sizes.
- Cache configuration (strategy, TTL, eviction).
- Dependency direction between components.
- API granularity (too fine = chatty, too coarse = inflexible).

### 4. Surface Trade-offs
Identify where quality attributes are in tension:
- Where has performance been traded for simplicity?
- Where has consistency been traded for availability?
- Where has modifiability been traded for performance?
- Are these trade-offs documented and conscious?

### 5. Evaluate Scenario Support
Generate key quality scenarios and walk them through the architecture:
- Can the architecture support 10× current load?
- What happens when [specific component] fails?
- How many files change to add [typical new feature]?
- How does the system handle a new [typical integration]?

For scenarios the architecture handles cleanly: note as **non-risks**.
For scenarios requiring architectural changes: note as **risks** with severity
based on likelihood and impact.

## Reporting Format

```
**Risk: [brief description]**
Decision: What architectural decision creates this risk
Quality Attributes Affected: Which attributes are impacted
Scenario: Specific scenario where this risk manifests
Likelihood: HIGH / MEDIUM / LOW
Impact: HIGH / MEDIUM / LOW
Recommendation: How to mitigate or accept the risk
```

```
**Trade-off: [brief description]**
Decision: What architectural decision creates this tension
Favored Attribute: What is optimized
Sacrificed Attribute: What is degraded
Current Balance: Whether the current balance is appropriate for the context
Recommendation: Adjust, accept, or monitor
```

```
**Sensitivity Point: [brief description]**
Parameter: What configuration or design choice
Affected Attribute: Which quality attribute is sensitive
Current Value/Choice: What it is now
Risk Range: What values/choices would cause problems
Recommendation: Monitor, constrain, or document
```
