# Scoring Benchmarks

## Dimension Scoring (1-5)

### Cost (weight: 25%)

Based on estimated daily API-equivalent burn rate:

| Score | Daily Rate | Interpretation |
|-------|-----------|----------------|
| 5 | < $1/day | Excellent — lean and efficient |
| 4 | $1-5/day | Good — normal professional usage |
| 3 | $5-15/day | Fair — room for optimization |
| 2 | $15-50/day | Poor — significant waste |
| 1 | > $50/day | Critical — review immediately |

### Cache Efficiency (weight: 25%)

Based on cache hit ratio (`cache_read / total_context`):

| Score | Hit Rate | Interpretation |
|-------|----------|----------------|
| 5 | >= 70% | Excellent — stable context is well cached |
| 4 | 55-69% | Good — most context is cached |
| 3 | 40-54% | Fair — cache churn or frequent restarts |
| 2 | 25-39% | Poor — paying full price repeatedly |
| 1 | < 25% | Critical — almost no caching benefit |

### Conversation Sprawl (weight: 20%)

Based on average turns per session and % of sessions exceeding 15 turns:

| Score | Avg Turns | Sprawling % | Interpretation |
|-------|-----------|-------------|----------------|
| 5 | <= 10 | < 5% | Excellent — focused sessions |
| 4 | <= 15 | < 15% | Good — reasonable session length |
| 3 | <= 20 | < 30% | Fair — some sprawl |
| 2 | <= 30 | < 50% | Poor — frequent sprawl |
| 1 | > 30 | >= 50% | Critical — habitual marathon sessions |

### Model Selection (weight: 15%)

Based on model mix diversity and Opus usage percentage:

| Score | Criteria | Interpretation |
|-------|----------|----------------|
| 5 | 3 tiers used | Excellent — proper model tiering |
| 4 | 2 tiers, Opus < 50% | Good — some differentiation |
| 3 | Opus < 70% | Fair — over-relying on top tier |
| 2 | Opus < 90% | Poor — minimal tiering |
| 1 | Opus >= 90% | Critical — no model strategy |

### Output Efficiency (weight: 10%)

Based on output tokens / total input tokens ratio:

| Score | Ratio | Interpretation |
|-------|-------|----------------|
| 5 | >= 30% | Excellent — high work per context token |
| 4 | 20-29% | Good — reasonable efficiency |
| 3 | 10-19% | Fair — context-heavy workloads |
| 2 | 5-9% | Poor — lots of context, little output |
| 1 | < 5% | Critical — excessive context overhead |

### Session Patterns (weight: 5%)

Based on subagent delegation rate and average session duration:

| Score | Delegation | Avg Duration | Interpretation |
|-------|------------|--------------|----------------|
| 5 | > 15% | < 30 min | Excellent — good delegation |
| 4 | > 5% | < 60 min | Good — some parallel work |
| 3 | any | < 90 min | Fair — reasonable sessions |
| 2 | any | < 120 min | Poor — long sessions |
| 1 | any | >= 120 min | Critical — marathon sessions |

## Overall Grade

Weighted average of dimension scores to letter grade:

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 4.5 - 5.0 | Token-efficient power user |
| B | 3.5 - 4.4 | Good habits, minor optimizations available |
| C | 2.5 - 3.4 | Moderate waste, clear improvement path |
| D | 1.5 - 2.4 | Significant waste patterns |
| F | < 1.5 | Urgent attention needed |

## Clean vs Sloppy Comparison

A typical 5-hour session:

| Aspect | Sloppy | Clean | Savings |
|--------|--------|-------|---------|
| Document format | Raw PDFs | Markdown | 20x |
| Context tokens | 100K+ | 5-6K | ~17x |
| Session length | 30+ turns | 10-15 turns | 2-3x |
| Model choice | Opus for everything | Mixed tiers | 5-10x |
| Est. cost/session | $8-10 | ~$1 | 8-10x |

At team scale (10 people): $2,000/month to $250/month for the same output.
