# Redundancy

> "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."
> — Antoine de Saint-Exupery

## Core Idea

Redundancy adds weight without value. Every line of code is a liability — it must be
read, understood, maintained, and can harbor bugs. Redundant code misleads readers into
thinking it serves a purpose, wastes time during reviews, and increases the surface area
for defects. The simplest codebase is one where removing any line would break something.

This is distinct from DRY (Don't Repeat Yourself). DRY is about knowledge duplication —
the same business rule expressed in multiple places. Redundancy is about unnecessary
code — things that could be removed entirely without changing behavior or losing
capability.

## Violation Patterns

### 1. Dead Code
**Heuristic**: Code that no execution path reaches or no caller invokes.

**Look for**:
- Functions with zero call sites (check tests too).
- `if False:` or `if (false)` blocks.
- Large commented-out code blocks with notes like "might need this later."
- Variables assigned but never read.
- Exception handlers that catch impossible exceptions.

**Refactoring**: Delete it. Version control preserves history — commented-out code is
not a backup strategy. For functions that "might be needed later," delete and retrieve
from git history when that day comes.

### 2. Redundant Validation
**Heuristic**: Null/type/range checks repeated at 3+ layers for the same data.

**Look for**:
- Null checks at controller, service, and repository levels for the same field.
- Type assertions after TypeScript/Java has already enforced the type.
- Range checks that the database constraint already enforces.
- Permission checks duplicated at API gateway, controller, and service.

**Refactoring**: Validate once at the system boundary (API entry point, user input,
external data). Trust internal code — if a function is called only from validated
contexts, it doesn't need its own validation.

### 3. Duplicate Logic
**Heuristic**: Two or more code blocks sharing 80%+ of their logic with minor
variations.

**Look for**:
- Copy-pasted functions with small parameter differences.
- Similar error handling blocks repeated across methods.
- Test setup code duplicated across test functions.
- Query builders with the same structure but different fields.

**Refactoring**: Extract the common logic into a shared function with parameters for
the varying parts. But only if the duplication is true knowledge duplication — not
coincidental similarity.

### 4. Unnecessary Comments
**Heuristic**: Comments that could be deleted without losing information not already
in the code.

**Look for**:
- `i++; // increment i`, `return result; // return the result`.
- Comments describing what a well-named function does.
- Outdated comments that contradict the current code.
- TODO comments older than 6 months with no associated issue.
- Commented-out code with "just in case" notes.

**Refactoring**: Delete comments that restate the code. Rename unclear code instead of
commenting it. Convert TODOs to tracked issues, then delete the comment. Keep comments
that explain *why*, not *what*.

### 5. Unused Parameters and Imports
**Heuristic**: Parameters/imports not referenced in the function body or file.

**Look for**:
- Function parameters prefixed with `_` or not referenced at all.
- Imports only used in commented-out code.
- Type definitions or interfaces never referenced.
- Class fields set in constructor but never read.
- Environment variables loaded but never used.

**Refactoring**: Remove unused parameters (update callers), remove unused imports,
remove unused types. If a parameter is needed for an interface contract, document why
it is intentionally unused.

## Language-Specific Notes

- **Python**: `# type: ignore` comments may indicate unnecessary complexity rather
  than unavoidable type issues. `__all__` exports should match actual usage.
  `pylint: disable` on entire files suggests deeper issues.
- **Java/C#**: IDE-generated getters/setters for fields that are only read or only
  written are redundant. `@SuppressWarnings` should be targeted, not blanket.
- **TypeScript**: `@ts-ignore` and `any` casts may indicate unnecessary type
  gymnastics. Re-exported types that could be imported directly. Barrel files that
  re-export everything including unused items.
- **Go**: `_` parameters in interface implementations are expected (satisfying the
  interface). Blank identifier imports (`_ "package"`) for side effects are
  intentional, not redundant.

## False Positives to Avoid

- Defensive validation at trust boundaries (external APIs, user input, deserialized
  data) — even if the caller validates too, the boundary should not trust its callers.
- Code that appears unused but is called via reflection, decorators, event systems, or
  framework conventions (e.g., Django signal handlers, Spring `@Scheduled` methods).
- Comments explaining *why* a non-obvious decision was made, not *what* the code does.
- Parameters required by an interface/protocol contract even if the specific
  implementation doesn't use them.
- Seemingly similar code that handles genuinely different business cases that may
  diverge in the future (coincidental duplication).
