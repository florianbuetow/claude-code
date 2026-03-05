---
name: kiss
version: 1.0.0
description: >
  This skill should be used when the user asks to "check for unnecessary complexity",
  "simplify this code", "find over-engineering", "audit code complexity", or
  "reduce complexity". Also triggers when the user mentions KISS, "keep it simple",
  over-abstraction, dead code, redundant code, or asks about simplification
  opportunities. Supports checking all four categories at once or focusing on
  a single category.
---

# KISS — Keep It Simple

Analyze source code and architecture for unnecessary complexity, over-abstraction,
and redundancy. Produce actionable findings with severity ratings, code locations,
and concrete simplification suggestions — without modifying code.

## Subcommands

Request a full audit or focus on a single category:

| Command Pattern | Category | Reference |
|----------------|----------|-----------|
| `kiss all` / `kiss check` / `kiss` | All four categories | All references |
| `kiss complexity` | Code Complexity | `references/complexity.md` |
| `kiss abstraction` | Over-Abstraction | `references/abstraction.md` |
| `kiss redundancy` | Redundancy | `references/redundancy.md` |
| `kiss architecture` | Architecture Complexity | `references/architecture.md` |

When no subcommand is specified, default to checking all four categories.
When a category is mentioned by name (even without saying "kiss"), match it to
the appropriate subcommand.

## Workflow

### 1. Identify Target Code

Determine what code to analyze:
- When files or a directory are provided, use those.
- When a class/module is referenced by name, locate it.
- When ambiguous, ask which files or directories to scan.

Supported languages: any language (Python, Java, TypeScript, C#, C++, Kotlin,
Go, Rust, etc.). Adapt the checks to the idioms of the target language —
simplicity looks different across languages and paradigms.

### 2. Load Category References

Before analyzing, read the reference file(s) for the requested category(s):

- [`references/complexity.md`](references/complexity.md) for code complexity checks
- [`references/abstraction.md`](references/abstraction.md) for over-abstraction checks
- [`references/redundancy.md`](references/redundancy.md) for redundancy checks
- [`references/architecture.md`](references/architecture.md) for architecture complexity checks

For a full audit (`kiss all`), read all four.

### 3. Analyze

For each target file/class, apply the violation patterns from the loaded references.
Think carefully about each pattern — not every heuristic match is a true violation.
Consider context, project size, and pragmatism. A 50-line script doesn't need the
same simplicity scrutiny as a large production system.

### 4. Report Findings

Present findings using this structure:

#### Per Violation

```
**[CATEGORY] Violation — Severity: HIGH | MEDIUM | LOW**
Location: `filename.py`, function `name`, lines ~XX-YY
Issue: Clear description of what is unnecessarily complex and why it matters.
Suggestion: Concrete simplification approach with brief code sketch if helpful.
```

Severity guidelines:
- **HIGH**: Active maintenance pain, blocks understanding, or causes bugs due to complexity.
- **MEDIUM**: Unnecessary complexity that will slow development as the codebase grows.
- **LOW**: Minor simplification opportunity, worth noting but fine to defer.

#### Summary

After all findings, provide:
- A count table: `| Category | HIGH | MEDIUM | LOW |`
- Top 3 priorities: which violations to simplify first and why.
- Overall assessment: one paragraph on the code's simplicity health.

### 5. Refactor Mode (Optional)

When a fix or simplification is requested (e.g., "fix this", "simplify it",
"show me the simpler version"), produce simplified code that resolves the identified
violations. Explain each change briefly.

## Pragmatism Guidelines

These are guidelines, not laws. Apply judgment:

- Small utility scripts and prototypes get a lighter touch. Don't flag a 30-line
  script for having a few extra lines of defensive code.
- Some complexity is conscious trade-offs. When a rationale is provided for
  a design choice, acknowledge it rather than insisting on purity.
- Language idioms matter. A Java enterprise application will naturally have more
  layers than a Python script. Go code repeats error handling by design.
  Functional code uses composition patterns that look complex but are idiomatic.
- Prefer actionable findings over exhaustive catalogs. Five important findings
  beat twenty trivial ones.
- Essential complexity is not a violation. Complex domains produce complex code —
  KISS targets accidental complexity introduced by our choices, not inherent
  problem difficulty.

## Example Interaction

**User**: `kiss complexity` (with a file attached)

**Claude**:
1. Reads `references/complexity.md`
2. Analyzes the attached file for code complexity violations
3. Reports findings with locations, severity, and suggestions
4. Provides a summary with priorities
