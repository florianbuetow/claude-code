# Token Waste Taxonomy

Six categories of token waste, ordered by typical impact. Use this reference
when investigating specific findings from the analysis report.

## 1. Context Window Inflation (Sprawl Tax)

**What:** Long conversations force the model to re-read the entire history
with every turn. A 30-turn session re-processes early context 30 times.

**Detection:** `input_tokens` growing per turn within a session. Sessions
with >15 turns and context growth ratio >3x.

**Fix:** Start fresh sessions every 10-15 turns. Summarize progress before
restarting. Separate "thinking" (research) from "doing" (execution).

## 2. Cache Underutilization

**What:** Stable context (system prompts, tool definitions, CLAUDE.md) should
be cached and reused. Low cache hit rates mean paying full price for the same
content repeatedly.

**Detection:** `cache_read_input_tokens / total_context < 50%`. High
`cache_creation_input_tokens` with low `cache_read_input_tokens` = cache churn.

**Fix:** For API users, cache stable prompts explicitly. For Claude Code users,
keep sessions warm (the cache-money plugin helps). Avoid frequent session
restarts that invalidate the cache.

## 3. Model Over-Selection

**What:** Using Opus (the most expensive model) for tasks that Sonnet or Haiku
could handle equally well. "Bringing a Ferrari to the grocery store."

**Detection:** >80% of turns using Opus. Opus-only sessions doing routine
tasks (formatting, simple edits, proofreading).

**Fix:** Use model tiering:
- Opus: Complex reasoning, architectural decisions, deep analysis
- Sonnet: Standard coding, data transformation, execution
- Haiku: Proofreading, formatting, minor adjustments

## 4. Raw File Ingestion

**What:** Uploading PDFs, images, or screenshots when only text content is
needed. A 4,500-word PDF can consume 100K+ tokens due to formatting metadata.

**Detection:** Not directly measurable from session logs. Look for very large
user messages (>50K tokens in a single turn) as a proxy.

**Fix:** Convert documents to Markdown before ingestion (20x savings). Use
copy-paste for short text. Only upload images when visual analysis is needed.

## 5. Plugin Barnacles

**What:** Unused plugins and MCP connectors loading silent context overhead
before the user types anything. 50K+ tokens of "tax" per session.

**Detection:** Not directly measurable from session logs (the overhead is
part of the cached system prompt). Check via `/cost` command.

**Fix:** Audit active plugins weekly. Disable connectors not needed for the
current task. Test with zero plugins to baseline.

## 6. Inefficient Search

**What:** Using the model's native browsing capability for web searches when
dedicated tools (Perplexity MCP) are 10x cheaper and faster.

**Detection:** High WebSearch/WebFetch tool usage in sessions with large
token counts. Compare burn rate of search-heavy vs non-search sessions.

**Fix:** Use MCP connectors for dedicated search services. Pre-research in
separate sessions before executing.
