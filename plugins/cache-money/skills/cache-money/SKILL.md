---
name: cache-money
description: This skill should be used when the user asks to "keep cache warm", "warm the cache", "save tokens", "reduce token usage", "cache-money", "start cache ping", "optimize peak hours", "prevent cache expiry", or mentions Anthropic prompt caching, cache TTL, peak hour throttling, token cost optimization, or keeping the context cache alive in Claude Code sessions.
---

# Cache Money

Reduce token costs and latency in Claude Code sessions by keeping the Anthropic prompt cache warm through scheduled lightweight pings.

## Why This Matters

Anthropic caches the prompt prefix for 1 hour (extended TTL) in Claude Code. Cached tokens cost approximately one tenth of the base price and arrive faster. If a session is idle for more than 60 minutes, the cache expires and the next call pays full price for the entire context — which can be up to one million tokens.

During peak hours (weekdays 5:00 AM – 11:00 AM PT / 1:00 PM – 7:00 PM GMT), session limits are consumed faster. Keeping the cache warm during these windows prevents expensive full-context rebuilds.

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
| Weekend or outside peak | **Off-peak** — cache warming optional, still saves on idle sessions longer than 60 min |

Report the status to the user in one line before proceeding.

### Step 2: Start the Cache Ping Loop

Invoke the `/loop` skill to schedule a recurring ping every 55 minutes:

```
Skill tool: skill="loop", args="55m Cache ping. Reply with only: ok"
```

The 55-minute interval provides a 5-minute safety margin within the 1-hour cache TTL.

Each ping iteration triggers one lightweight API call that renews the cached prompt prefix. The response is minimal — just "ok" — so token consumption per ping is negligible.

### Step 3: Confirm to User

After starting the loop, report:

1. **Status**: Cache ping loop is active
2. **Interval**: Every 55 minutes
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
- Off-peak sessions still benefit if idle periods exceed 60 minutes — the cache expires based on inactivity, not time of day.
- The first API call after cache expiry is always a full-price write. Every subsequent call within 60 minutes is a cache read at ~10% cost.
