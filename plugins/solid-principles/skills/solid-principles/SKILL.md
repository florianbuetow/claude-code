---
name: solid-principles
version: 1.0.0
description: >
  This skill should be used when the user asks to "check SOLID violations",
  "audit class design", "review code quality", "find design smells", or
  "improve object-oriented architecture". Also triggers when the user
  mentions a principle by name (e.g., "check SRP", "is this violating LSP?",
  "dependency inversion"), or asks about coupling, cohesion, or class
  responsibilities. Supports checking all five principles at once or
  focusing on a single principle.
---

# SOLID Principles

Analyze source code for violations of Robert C. Martin's SOLID principles of
object-oriented design. Produce actionable findings with severity ratings,
code locations, and concrete refactoring suggestions.

## Subcommands

Request a full audit or focus on a single principle:

| Command Pattern | Principle | Reference |
|----------------|-----------|-----------|
| `solid all` / `solid check` / `solid` | All five principles | All references |
| `solid srp` | Single Responsibility | `references/srp.md` |
| `solid ocp` | Open/Closed | `references/ocp.md` |
| `solid lsp` | Liskov Substitution | `references/lsp.md` |
| `solid isp` | Interface Segregation | `references/isp.md` |
| `solid dip` | Dependency Inversion | `references/dip.md` |

When no subcommand is specified, default to checking all five principles.
When a principle is mentioned by name (even without saying "solid"), match it to
the appropriate subcommand.

## Workflow

### 1. Identify Target Code

Determine what code to analyze:
- When files or a directory are provided, use those.
- When a class/module is referenced by name, locate it.
- When ambiguous, ask which files or directories to scan.

Supported languages: any OO language (Python, Java, TypeScript, C#, C++, Kotlin,
Go with struct methods, Rust with impl blocks, etc.). Adapt the principle checks
to the idioms of the target language — not every principle manifests identically
across languages.

### 2. Load Principle References

Before analyzing, read the reference file(s) for the requested principle(s):

- [`references/srp.md`](references/srp.md) for SRP checks
- [`references/ocp.md`](references/ocp.md) for OCP checks
- [`references/lsp.md`](references/lsp.md) for LSP checks
- [`references/isp.md`](references/isp.md) for ISP checks
- [`references/dip.md`](references/dip.md) for DIP checks

For a full audit (`solid all`), read all five.

### 3. Analyze

For each target file/class, apply the violation patterns from the loaded references.
Think carefully about each pattern — not every heuristic match is a true violation.
Consider context, project size, and pragmatism. A 50-line script doesn't need the
same architectural rigor as a large production system.

### 4. Report Findings

Present findings using this structure:

#### Per Violation

```
**[PRINCIPLE] Violation — Severity: HIGH | MEDIUM | LOW**
Location: `filename.py`, class `ClassName`, lines ~XX-YY
Issue: Clear description of what violates the principle and why it matters.
Suggestion: Concrete refactoring approach with brief code sketch if helpful.
```

Severity guidelines:
- **HIGH**: Active maintenance pain, bug risk, or blocks extensibility.
- **MEDIUM**: Code smell that will cause problems as the codebase grows.
- **LOW**: Minor design impurity, worth noting but fine to defer.

#### Summary

After all findings, provide:
- A count table: `| Principle | HIGH | MEDIUM | LOW |`
- Top 3 priorities: which violations to fix first and why.
- Overall assessment: one paragraph on the code's structural health.

### 5. Refactor Mode (Optional)

When a fix or refactoring is requested (e.g., "fix this", "refactor it",
"show me the clean version"), produce refactored code that resolves the identified
violations. Explain each change briefly.

## Pragmatism Guidelines

These are guidelines, not laws. Apply judgment:

- Small utility scripts and prototypes get a lighter touch. Don't flag a 30-line
  script for lacking dependency injection.
- Some "violations" are conscious trade-offs. When a rationale is provided for
  a trade-off, acknowledge it rather than insisting on purity.
- Language idioms matter. A Python module with top-level functions isn't violating
  SRP just because it's not a class. Go interfaces are implicitly satisfied, so
  ISP looks different there.
- Prefer actionable findings over exhaustive catalogs. Five important findings
  beat twenty trivial ones.

## Example Interaction

**User**: `solid srp` (with a file attached)

**Claude**:
1. Reads `references/srp.md`
2. Analyzes the attached file for SRP violations
3. Reports findings with locations, severity, and suggestions
4. Provides a summary with priorities
