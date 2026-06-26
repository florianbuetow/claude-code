Source: 01-introduction-and-goals/tips/, 03-context-and-scope/tips/, 05-building-block-view/tips/, 06-runtime-view/tips/, 08-crosscutting-concepts/tips/, 09-architecture-decisions/tips/, 12-glossary/tips/

Machine-checkable cross-section rules derived from the arc42 tip corpus. Each RULE entry states: the invariant to check, the sections it spans, and the tip(s) it traces to. These rules are consumed by the `consistency-checker` skill (Task 9).

---

- RULE interfaces-match: Every external interface named in §3 (context diagram) MUST also appear in the §5 level-1 building block whitebox, and no external interface may appear in the level-1 diagram that is absent from §3. (from T05-4)

- RULE context-all-neighbors: Every external neighbor system or user role that interacts with the system MUST be represented in the §3 context diagram; none may be silently omitted. Abstraction via categories is allowed, but omission is not. (from T03-9, T03-5)

- RULE third-party-marked: Any third-party library, product, or framework that appears in the §5 building block view MUST be visibly distinguished from custom-built blocks by at least one of: UML stereotype, distinct color, or naming convention. (from T05-20)

- RULE qgoals-count: §1.2 (Quality Goals) MUST list between 3 and 5 quality goals, inclusive. Fewer than 3 suggests insufficient elicitation; more than 5 means the top priorities are not being filtered to §1. Remaining goals belong in §10. (from T01-16)

- RULE runtime-few: The number of runtime scenarios retained in the §6 documentation MUST be small and representative — the corpus guidance is 1–3 scenarios. Any scenario used only for design-time discovery must be removed before the document is delivered. (from T06-2)

- RULE crosscutting-not-all: §8 (Crosscutting Concepts) MUST contain only a selected subset of the arc42 concept catalog, limited to topics genuinely applicable to the system. Documenting the full catalog, or topics irrelevant to the system, violates this rule. (from T08-3)

- RULE level1-required: §5 (Building Block View) MUST contain at least a level-1 whitebox diagram of the overall system, even when all other documentation is reduced to a minimum. (from T05-3)

- RULE code-coverage: Every line of system-specific source code MUST be traceable to at least one building block in §5. No source artifact may be architecturally orphaned. Infrastructure tools may be deferred to §8 but must still be named at level-1. (from T05-18)

- RULE adr-has-timestamp: Every Architecture Decision Record in §9 MUST include a timestamp (date) indicating when the decision was made. Records without a timestamp fail this check. (from T09-8)

- RULE glossary-size: The §12 glossary MUST contain between 10 and 30 entries. Fewer than 10 suggests the important domain terms are not being captured; more than 30 suggests trivial or generic terms have been included. (from T12-5)

- RULE intro-page-limit: The §1.1 requirements summary MUST be approximately one page or less in length. Content exceeding one page should be moved to referenced requirement documents. (from T01-1)
