# Anthropic Prompt Cache Mechanics

## How Prompt Caching Works

When Claude Code sends a request to the Anthropic API, the full conversation context (system prompt, tool definitions, conversation history) is sent as the prompt. Anthropic stores a prefix of this prompt in a server-side cache.

### Cache Behavior

1. **First call**: The full context is processed and written to the cache. This is a "cache write."
2. **Subsequent calls**: If the next request shares the same prefix (i.e., the conversation context hasn't changed structurally), Anthropic serves the cached prefix instead of reprocessing it. This is a "cache read."
3. **Cache expiry**: The cached prefix expires after a TTL (time-to-live) period of inactivity. The TTL depends on the configuration — see below.

### TTL Tiers

| Tier | Duration | How to Enable | Cache Write Cost | Cache Read Cost |
|------|----------|---------------|-----------------|-----------------|
| **Default** | 5 minutes | No `ttl` field in `cache_control` | 1.25x base input | 0.1x base input |
| **Extended** | 1 hour | Explicit `cache_control: {type: "ephemeral", ttl: "1h"}` | 2x base input | 0.1x base input |

**Renewal**: Each API call that hits the cache resets the TTL timer. A call at minute 55 (for 1h TTL) or minute 4 (for 5min TTL) extends the cache for another full period from that point.

**Expiry**: If no API call is made within the TTL window, the cache is evaporated. The next call starts fresh with a full cache write.

### Who Gets What

- **Claude Code UI (Max-tier plans)**: Anthropic enables 1-hour TTL server-side automatically. No explicit configuration needed.
- **Claude Code CLI / API**: Always uses the 5-minute default TTL unless the request explicitly includes `ttl: "1h"` in the `cache_control` field. This applies regardless of plan tier.
- **Lower-tier plans (Free, Pro)**: 5-minute TTL only, both in UI and CLI.

### Cost Structure

Example pricing for Claude Opus 4.6:

| Token Type | Cost per MTok | Relative to Base |
|------------|--------------|-----------------|
| Base input (uncached) | $5.00 | 1x |
| 5-min cache write | $6.25 | 1.25x |
| 1-hour cache write | $10.00 | 2x |
| Cache read (any TTL) | $0.50 | 0.1x |
| Output tokens | $25.00 | Same regardless of caching |

On a session with 500K tokens of context, the difference between a cache read ($0.25) and a 5-min cache write ($3.13) is significant — roughly a 92% reduction in input token cost per call.

## Peak Hours and Usage Limits

Anthropic applies peak-hour throttling on weekdays from 5:00 AM to 11:00 AM Pacific Time (1:00 PM to 7:00 PM GMT). During this window:

- The 5-hour rolling session limit for Free, Pro, and Max users is consumed at a faster rate
- The weekly quota remains the same, but each interaction costs more of the rolling window
- **Cache TTL is not affected** — both 5-minute and 1-hour TTLs remain identical during peak and off-peak

This makes cache efficiency more important during peak hours: a cache miss doesn't just cost more tokens, it burns more of the tighter rolling session budget. Keeping the cache warm during peak windows prevents expensive full-context rebuilds when the budget is most constrained.

## Ping Intervals

The keep-warm interval should be set based on the active TTL tier:

| TTL Tier | Cache Duration | Ping Interval | Safety Margin |
|----------|---------------|---------------|---------------|
| Extended (1h) | 60 minutes | 55 minutes | 5 minutes |
| Default (5min) | 5 minutes | 4 minutes | 1 minute |

The safety margin accounts for minor timing drift, network latency, and processing delays. The ping arrives before the cache would expire, renewing it for another full TTL period.

## What Counts as a Cache Hit

For the cache to be hit, the prompt prefix must match exactly. In Claude Code, this means:

- The system prompt (including CLAUDE.md contents, tool definitions, etc.) stays the same
- The conversation history up to the cached point hasn't been modified
- No messages have been inserted or removed before the cached prefix boundary

Normal conversation flow (appending new messages) preserves the prefix and results in cache hits. The cached prefix grows as the conversation develops — each new exchange extends the cached portion.

## Practical Impact

### Small context (< 10K tokens)
Cache savings are minimal. The cost difference between a cache read and write on 10K tokens is negligible. Keep-warm is not worth the overhead.

### Medium context (10K – 100K tokens)
Cache savings become noticeable. A cache miss costs ~10x more on the input side. Keep-warm is worthwhile during peak hours.

### Large context (100K – 1M tokens)
Cache savings are substantial. A single cache miss on 500K tokens of context can consume a meaningful chunk of the session budget. Keep-warm pays for itself many times over.

## Minimum Cacheable Length

| Model | Minimum Tokens |
|-------|---------------|
| Claude Opus 4.6, 4.5 | 4,096 |
| Claude Sonnet 4.6 | 2,048 |
| Claude Sonnet 4.5, 4, 3.7, 4.1 | 1,024 |
| Claude Opus 4.1, 4 | 1,024 |
| Claude Haiku 4.5 | 4,096 |
| Claude Haiku 3.5, 3 | 2,048 |

Prompts shorter than the minimum are processed without caching, and no error is returned. Check response `usage` fields for `cache_creation_input_tokens` and `cache_read_input_tokens` both being 0 to detect this.

## Limitations

- **Per-session only**: Each Claude Code conversation has its own cache. Warming one session does not affect another.
- **Session must remain open**: Closing the terminal, ending the session, or compacting the conversation invalidates the cache.
- **Context changes**: If the system prompt or tool definitions change (e.g., installing a new plugin mid-session), the cache prefix may partially invalidate.
- **Not a guarantee**: Caching behavior is managed server-side by Anthropic and may change. The cost ratios and TTL values described here are based on current documented behavior.
