# Anthropic Prompt Cache Mechanics

## How Prompt Caching Works

When Claude Code sends a request to the Anthropic API, the full conversation context (system prompt, tool definitions, conversation history) is sent as the prompt. Anthropic stores a prefix of this prompt in a server-side cache.

### Cache Behavior

1. **First call**: The full context is processed and written to the cache. This is a "cache write" — charged at the standard input token rate.
2. **Subsequent calls**: If the next request shares the same prefix (i.e., the conversation context hasn't changed structurally), Anthropic serves the cached prefix instead of reprocessing it. This is a "cache read."
3. **Cache expiry**: The cached prefix expires after a TTL (time-to-live) period of inactivity. For Claude Code, this TTL is 1 hour.

### Cost Structure

| Token Type | Relative Cost |
|------------|--------------|
| Cache write (first call or after expiry) | 1x (base input price) |
| Cache read (within TTL) | ~0.1x (approximately 10% of base price) |
| Output tokens | Same regardless of caching |

On a session with 500K tokens of context, the difference between a cache read and a cache write is significant — roughly a 90% reduction in input token cost per call.

### TTL Details

- **Default TTL**: 5 minutes (standard API usage)
- **Extended TTL**: 1 hour (used by Claude Code)
- **Renewal**: Each API call that hits the cache resets the TTL timer. A call at minute 55 extends the cache for another full hour from that point.
- **Expiry**: If no API call is made within the TTL window, the cache is evaporated. The next call starts fresh with a full cache write.

## Peak Hours and Throttling

Anthropic applies peak-hour throttling on weekdays from 5:00 AM to 11:00 AM Pacific Time (1:00 PM to 7:00 PM GMT). During this window:

- The 5-hour rolling session limit for Free, Pro, and Max users is consumed at a faster rate
- The weekly quota remains the same, but each interaction costs more of the rolling window
- This makes cache efficiency even more important — a cache miss during peak hours is doubly expensive (higher base cost + faster quota consumption)

## Why 55 Minutes

The keep-warm interval is set to 55 minutes to provide a 5-minute safety margin:

- Cache TTL: 60 minutes
- Ping interval: 55 minutes
- Safety margin: 5 minutes

This accounts for minor timing drift, network latency, and processing delays. The ping arrives comfortably before the cache would expire, renewing it for another full hour.

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
Cache savings become noticeable. A cache miss costs 10x more on the input side. Keep-warm is worthwhile during peak hours.

### Large context (100K – 1M tokens)
Cache savings are substantial. A single cache miss on 500K tokens of context at peak rates can consume a meaningful chunk of the session budget. Keep-warm pays for itself many times over.

## Limitations

- **Per-session only**: Each Claude Code conversation has its own cache. Warming one session does not affect another.
- **Session must remain open**: Closing the terminal, ending the session, or compacting the conversation invalidates the cache.
- **Context changes**: If the system prompt or tool definitions change (e.g., installing a new plugin mid-session), the cache prefix may partially invalidate.
- **Not a guarantee**: Caching behavior is managed server-side by Anthropic and may change. The cost ratios and TTL values described here are based on current observed behavior.
