---
name: cache-money
description: This skill should be used when the user asks to "keep cache warm", "warm the cache", "save tokens", "reduce token usage", "cache-money", "start cache ping", "optimize peak hours", "prevent cache expiry", or mentions Anthropic prompt caching, cache TTL, peak hour throttling, token cost optimization, or keeping the context cache alive in Claude Code sessions.
---

# Cache Money

Keep the Anthropic prompt cache warm during Claude Code sessions — especially during peak hours when usage limits are tighter — by scheduling lightweight pings tuned to your cache TTL.

## Why This Matters

Claude Code sends the full conversation context with every API call. Anthropic caches this prefix server-side and serves subsequent calls from cache at ~10% of the base input price. But the cache expires after a TTL period of inactivity:

| TTL Tier | Duration | Cache Write Cost | Who Gets It |
|----------|----------|-----------------|-------------|
| **Default** | 5 minutes | 1.25x base input | All plans (no `ttl` field specified) |
| **Extended** | 1 hour | 2x base input | Max-tier plans (server-side in Claude Code), or explicit `ttl: "1h"` via API |

Cache reads cost **0.1x base input** regardless of TTL tier — that's the 90% saving.

If a session sits idle past its TTL, the next call pays full cache-write price for the entire context — up to 1M tokens. During **peak hours** (weekdays 5:00 AM – 11:00 AM PT), Anthropic's rolling session limits are consumed faster, making every cache miss doubly expensive: higher rebuild cost plus faster quota burn.

For detailed technical background, consult **`references/cache-mechanics.md`**.

## Workflow

### Step 1: Assess Timing

Determine the current time and day of week in Pacific Time (PT) using:

```bash
TZ=America/Los_Angeles date "+%A %H:%M PT"
```

Classify the current window:

| Condition | Status |
|-----------|--------|
| Weekday, 5:00 AM – 11:00 AM PT | **Peak hours active** — cache warming strongly recommended |
| Weekday, 4:47 AM – 4:59 AM PT | **Peak approaching** — pre-warming recommended |
| Weekend or outside peak | **Off-peak** — cache warming optional, still saves on idle sessions longer than the TTL |

Report the status to the user in one line before proceeding.

### Step 2: Detect Cache TTL

Determine which TTL tier is active. Ask the user:

> Are you on a **Max-tier plan** (which enables 1-hour cache TTL in Claude Code), or the **default** (5-minute cache TTL)?

Use the answer to set the ping interval:

| TTL Tier | Cache Duration | Ping Interval | Safety Margin |
|----------|---------------|---------------|---------------|
| **Extended (1h)** | 60 minutes | **55 minutes** | 5 minutes |
| **Default (5min)** | 5 minutes | **4 minutes** | 1 minute |

If the user is unsure, default to the **5-minute TTL** (4-minute ping interval) — it's safe for all plans and the overhead is minimal.

### Step 3: Start the Cache Ping Loop

Invoke the `/loop` skill to schedule the recurring ping at the determined interval:

**For 1-hour TTL (Max-tier):**
```
Skill tool: skill="loop", args="55m Cache ping. Reply with only: ok"
```

**For 5-minute TTL (default):**
```
Skill tool: skill="loop", args="4m Cache ping. Reply with only: ok"
```

Each ping triggers one lightweight API call that renews the cached prompt prefix. The response is minimal — just "ok" — so token consumption per ping is negligible.

### Step 4: Confirm to User

After starting the loop, report:

1. **TTL tier**: Which cache duration was detected (5-min or 1-hour)
2. **Interval**: The chosen ping interval and why
3. **Peak window**: Whether currently in peak hours
4. **How to stop**: End the session or cancel the loop
5. **Savings**: Cached tokens cost ~90% less than uncached — on a large context this adds up fast

## Timing Reference

| Timezone | Peak Start | Peak End |
|----------|-----------|----------|
| PT (Pacific) | 5:00 AM | 11:00 AM |
| MT (Mountain) | 6:00 AM | 12:00 PM |
| CT (Central) | 7:00 AM | 1:00 PM |
| ET (Eastern) | 8:00 AM | 2:00 PM |
| GMT / UTC | 1:00 PM | 7:00 PM |
| CET (Central Europe) | 2:00 PM | 8:00 PM |
| IST (India) | 6:30 PM | 12:30 AM |
| JST (Japan) | 10:00 PM | 4:00 AM (+1) |
| AEST (Sydney) | 11:00 PM | 5:00 AM (+1) |

## Important Notes

- The cache is per-session. Each active Claude Code conversation has its own cached prefix. The ping must happen within the same session to renew it.
- The ping only works while the session is open. Closing the terminal or ending the session invalidates the cache regardless of the loop.
- Off-peak sessions still benefit if idle periods exceed the TTL — the cache expires based on inactivity, not time of day.
- The first API call after cache expiry is always a full-price write. Every subsequent call within the TTL is a cache read at ~10% cost.
