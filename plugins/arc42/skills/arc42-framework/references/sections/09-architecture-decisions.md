# Section 9 — Architecture Decisions

Source: 09-architecture-decisions/index.md

## Intent
Records the significant choices that shaped the architecture — especially those where the reasoning is not visible in the code itself. Each entry documents what was decided, the forces that drove the choice, and what trade-offs were accepted, so future maintainers can understand and deliberately revisit them.

## Evidence tier
code-inferable

## What to look for in the repo
- Existing ADR files in `docs/adr/`, `decisions/`, `architecture/decisions/`, or similar directories
- Commit messages or pull-request descriptions explaining technology replacements or structural changes
- TODO / FIXME / HACK comments that flag known trade-offs or deferred alternatives
- Changelogs mentioning major structural shifts
- Framework or library version pins with accompanying comments explaining why migration is deferred

## Output template

*<One ADR block per significant decision. Decisions that affect structure, quality properties, key external dependencies, or construction techniques qualify. For decisions already summarized in §4, reference that section rather than repeating the content.>*

---

**ADR `<NN>`: `<Decision Title>`**

| Field | Content |
|-------|---------|
| Title | *<Short, descriptive name including ADR number — e.g., "ADR 1: Use event sourcing for the order domain">* |
| Context | *<The situation, including technical, political, and organizational forces in play>* |
| Decision | *<What the team chose to do in response to those forces>* |
| Status | proposed \| accepted \| deprecated \| superseded |
| Consequences | *<All outcomes — positive, negative, and neutral; what the decision rules out as much as what it enables>* |

---

*<Repeat block for each architecturally significant decision>*

## Diagrams
none — prose and tables; diagrams depicting the decided structure belong in §5 or §8

## Lint (this section)
- T09-* (all five Nygard fields populated; status is set; decisions here cross-reference §4 where the same choice appears in summary form; no duplicate content between §4 and §9)

## Depends on
- §1 (quality goals and stakeholder expectations justify decisions)
- §4 (this section expands decisions summarized there)
