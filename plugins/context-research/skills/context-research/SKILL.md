<!--
  The API reference in Part 2 is derived from the huggingface-papers skill
  in the huggingface/skills repository (https://github.com/huggingface/skills),
  originally licensed under the Apache License, Version 2.0.
  See LICENSE-APACHE and NOTICE in the plugin root for details.
-->
---
name: context-research
description: An autonomous research pipeline that identifies, analyzes, and synthesizes SOTA AI research via Hugging Face and ArXiv. Designed for engineering-grade deep dives into AI topics (e.g., "KV-cache optimization," "model merging").
---

# PART 1: Research Pipeline Logic

## Phase 1: Intelligent Discovery & Ranking
1.  **Parallel Search**: Execute `GET /api/papers/search?q={query}&limit=20`.
2.  **Ranking Heuristic**: Rank results using a weighted score:
    - **Relevance (50%)**: Keyword density in title/abstract.
    - **Recency (25%)**: Prioritize papers from the last 12-18 months.
    - **Impact (25%)**: Upvotes and author/organization affiliation.
3.  **Sparse Result Fallback**: If < 5 papers are found on HF, the agent MUST use its web search tool to find ArXiv IDs or project pages, then use `GET /api/papers/{ID}` to ingest them.

## Phase 2: Parallel Deep Extraction
To maximize speed, execute metadata and content fetches for the top 3-5 papers **in parallel**.

1.  **Depth Check**: Fetch the `.md` content via `GET /papers/{ID}.md`.
    - **If Shallow (< 3000 chars)**: The markdown is likely just an abstract. Fall back to `https://arxiv.org/pdf/{ID}` to parse the full text for tables, benchmarks, and "Limitations" sections.
2.  **Metric Mining**: Specifically extract quantitative data:
    - Performance deltas (e.g., "26–54% reduction").
    - Hardware requirements and compute costs.
    - Benchmarks used (e.g., Needle-in-a-Haystack, AppWorld).
3.  **Artifact Audit**: Check `githubRepo` and `linkedModels`. If a repo exists, check the README for production implementation details.

## Phase 3: Thematic Synthesis
Avoid individual paper summaries. Organize the report by **Technical Taxonomy**:
1.  **Architectural Shifts**: How does this research change how we build?
2.  **Universal Bottlenecks/Patterns**: Identify cross-paper themes (e.g., "Information Loss," "Latency-Accuracy Trade-offs," or "Context Saturation").
3.  **Production Trade-offs**: Analyze the cost of implementation (e.g., KV-cache invalidation, API overhead).

---

# PART 2: Technical Specifications

## Filename & Slugification
All reports MUST be saved using the following convention:
- **Format**: `research_{topic-lowercase-kebab-case}.md`
- **Example**: `research_kv_cache_optimization.md`

## Core API Knowledge (Retained)
- **Search**: `GET /api/papers/search?q={query}`
- **Metadata**: `GET /api/papers/{ID}` (Authors, Upvotes, Links).
- **Content**: `GET /papers/{ID}.md` (Markdown version).
- **Model Links**: `GET /api/models?filter=arxiv:{ID}`.

## Error Handling & Fallbacks
- **404/Empty MD**: Always check `https://arxiv.org/abs/{ID}` as the source of truth if HF indexing is incomplete.
- **Multi-ID Support**: Handle both HF internal IDs and arXiv IDs (e.g., `2602.08025`).

## When to Use
- Deep-dive technical requests requiring more than a surface-level summary.
- Requests for "State of the Art" (SOTA) analysis.
- Identifying implementation risks for new AI architectures.
