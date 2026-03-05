---
name: kiss
version: 2.0.0
description: >
  This skill should be used when the user asks to "find simplification opportunities",
  "simplify this code", "check for unnecessary complexity", "find over-engineering",
  "audit code complexity", "reduce complexity", or "what can be simplified". Also
  triggers when the user mentions KISS, "keep it simple", over-abstraction, dead code,
  redundant code, tight coupling, interface bloat, or asks about simplification
  opportunities. Supports checking all five dimensions at once or focusing on
  a single dimension.
---

# KISS — Simplification Opportunity Detection

Analyze source code and architecture for **simplification opportunities** — places where
accidental complexity can be reduced without losing capability. Produce actionable
findings with severity ratings, dimension scores, code locations, and concrete
simplification suggestions.

The framing matters: this is not about reporting what IS complex, but about identifying
what CAN be simplified. Essential complexity (inherent to the problem domain) is not
a simplification opportunity. Accidental complexity (introduced by our choices) is.

## Dimensions

Five dimensions, each targeting a different axis of simplification:

| Dimension | Question It Answers | Reference |
|-----------|-------------------|-----------|
| **Complexity** | Where can control flow, cognitive load, or function structure be simplified? | `references/complexity.md` |
| **Abstraction** | Where can unnecessary layers, interfaces, or indirection be removed? | `references/abstraction.md` |
| **Redundancy** | Where can dead, duplicated, or unused code be eliminated? | `references/redundancy.md` |
| **Coupling** | Where can dependencies be loosened or dependency chains shortened? | `references/coupling.md` |
| **Architecture** | Where can system-level infrastructure or layering be consolidated? | `references/architecture.md` |

## Subcommands

| Command Pattern | Scope | Reference |
|----------------|-------|-----------|
| `kiss` / `kiss all` / `kiss check` | All five dimensions | All references |
| `kiss complexity` | Code Complexity | `references/complexity.md` |
| `kiss abstraction` | Over-Abstraction | `references/abstraction.md` |
| `kiss redundancy` | Redundancy | `references/redundancy.md` |
| `kiss coupling` | Coupling & Dependencies | `references/coupling.md` |
| `kiss architecture` | Architecture Complexity | `references/architecture.md` |

When no subcommand is specified, default to all five dimensions.
When a dimension is mentioned by name (even without "kiss"), match it.

## Workflow

### 1. Identify Target Code

Determine what code to analyze:
- When files or a directory are provided, use those.
- When a class/module is referenced by name, locate it.
- When ambiguous, ask which files or directories to scan.

Supported languages: any (Python, Java, TypeScript, C#, C++, Kotlin, Go, Rust, etc.).
Adapt checks to the idioms of the target language — simplicity looks different across
languages and paradigms.

### 2. Load Dimension References

Before analyzing, read the reference file(s) for the requested dimension(s):

- `references/complexity.md` — code complexity simplification
- `references/abstraction.md` — over-abstraction simplification
- `references/redundancy.md` — redundancy elimination
- `references/coupling.md` — coupling reduction
- `references/architecture.md` — architecture consolidation

For a full audit (`kiss all`), read all five.

### 3. Analyze

For each target file/class, apply the simplification patterns from the loaded references.

**Per-dimension scoring:** For each dimension analyzed, assign a score from 1–5:

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Minimal | Few or no simplification opportunities. Code is as simple as the problem allows. |
| 2 | Low | Minor opportunities exist but are low-priority. |
| 3 | Moderate | Several opportunities that would meaningfully reduce cognitive load or maintenance cost. |
| 4 | High | Significant accidental complexity. Simplification would substantially improve the codebase. |
| 5 | Critical | Accidental complexity dominates. The code is harder than the problem it solves. |

Think carefully about each pattern — not every heuristic match is a true opportunity.
Consider context, project size, language idioms, and pragmatism. Essential complexity
is not a simplification target.

### 4. Report Findings

Present findings using this structure:

#### Per Finding

```
**[DIMENSION] Simplification Opportunity — Severity: HIGH | MEDIUM | LOW**
Location: `filename.py`, function `name`, lines ~XX-YY
Opportunity: What can be simplified and why simplifying it matters.
Approach: Concrete simplification with brief code sketch if helpful.
```

Severity guidelines:
- **HIGH**: Active maintenance pain, blocks understanding, or causes bugs.
  Simplifying this delivers immediate value.
- **MEDIUM**: Unnecessary complexity that will slow development as the codebase
  grows. Simplifying prevents future pain.
- **LOW**: Minor opportunity, worth noting but fine to defer.

#### Dimension Scores

After all findings, provide a dimension scorecard:

```
| Dimension     | Score | Label    |
|---------------|-------|----------|
| Complexity    | 3/5   | Moderate |
| Abstraction   | 2/5   | Low      |
| Redundancy    | 4/5   | High     |
| Coupling      | 2/5   | Low      |
| Architecture  | 1/5   | Minimal  |
```

Only include dimensions that were analyzed.

#### Summary

- **Count table**: `| Dimension | HIGH | MEDIUM | LOW |`
- **Top 3 priorities**: Which simplifications to tackle first and why.
- **Overall assessment**: One paragraph on the codebase's simplicity health —
  how much of its complexity is essential vs accidental, and the highest-leverage
  simplification theme.

### 5. Refactor Mode (Optional)

When a fix or simplification is requested (e.g., "fix this", "simplify it",
"show me the simpler version"), produce simplified code that resolves the identified
opportunities. Explain each change briefly.

## Pragmatism Guidelines

These are guidelines, not laws. Apply judgment:

- **Scale matters.** Small utility scripts and prototypes get a lighter touch. Don't
  flag a 30-line script for having a few extra lines of defensive code.
- **Conscious trade-offs are not violations.** When a rationale exists for a design
  choice, acknowledge it rather than insisting on purity.
- **Language idioms matter.** Java naturally has more layers than Python. Go repeats
  error handling by design. Functional code uses composition patterns that look complex
  but are idiomatic. Judge against the language's norms.
- **Prefer actionable over exhaustive.** Five important findings beat twenty trivial ones.
  Focus on what delivers the most simplification value.
- **Essential complexity is not a target.** Complex domains produce complex code. KISS
  targets accidental complexity — the complexity we introduced, not the complexity the
  problem demands.
- **Threshold awareness.** Use the metric thresholds in each reference as guidelines,
  not rigid cutoffs. A function with cyclomatic complexity of 11 in a state machine
  is fine; the same in a utility helper is not.

## Example Interaction

**User**: `kiss complexity` (with a file attached)

**Claude**:
1. Reads `references/complexity.md`
2. Analyzes the attached file for complexity simplification opportunities
3. Reports findings with locations, severity, and simplification approaches
4. Provides dimension score and summary with priorities
