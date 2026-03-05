# Redundancy — Simplification Opportunities

> "Perfection is achieved, not when there is nothing more to add, but when there is
> nothing left to take away."
> — Antoine de Saint-Exupéry

## Core Idea

Redundancy is the most direct simplification opportunity: code that can be removed
entirely without changing behavior or losing capability. Every line of code is a
liability — it must be read, understood, maintained, and can harbor bugs. Redundant
code misleads readers into thinking it serves a purpose, wastes time during reviews,
and increases the surface area for defects.

This is distinct from DRY (Don't Repeat Yourself). DRY addresses knowledge
duplication — the same business rule expressed in multiple places. Redundancy
addresses unnecessary code — things that could be removed entirely. Both are
simplification opportunities, but the approach differs: DRY means consolidate,
redundancy means delete.

The research identifies three tiers of code duplication (clone types) that form a
spectrum from obvious to subtle:

- **Type 1 — Exact clones**: Identical code fragments (ignoring whitespace/comments).
- **Type 2 — Parameterized clones**: Structurally identical but with renamed variables,
  changed literals, or altered types.
- **Type 3 — Near-miss clones**: Similar fragments with statement additions, deletions,
  or modifications. Roughly 80%+ structural similarity.

Higher-type clones are harder to detect but often represent the largest simplification
opportunities because they indicate a missing abstraction.

## Simplification Patterns

### 1. Dead Code
**Detection heuristic:** Code that no execution path reaches or no caller invokes.

**Look for:**
- Functions with zero call sites (check tests too — but test-only functions in
  production code may themselves be a smell).
- `if False:` or `if (false)` blocks.
- Large commented-out code blocks with notes like "might need this later."
- Variables assigned but never read.
- Exception handlers catching impossible exceptions.
- Feature flags that have been permanently on or off for months.
- Imports of modules never referenced.
- Dead branches behind feature toggles that shipped long ago.

**Simplification approach:** Delete it. Version control preserves history —
commented-out code is not a backup strategy. For functions that "might be needed
later," delete and retrieve from git history when that day comes. For feature flags,
clean up after the flag decision is permanent.

### 2. Code Duplication (Clone Detection)
**Detection heuristic:** Two or more code blocks sharing 80%+ of their logic with
minor variations. The three clone types help calibrate severity.

**Metric thresholds:**
- Type 1 (exact clones): always simplifiable — extract immediately.
- Type 2 (parameterized clones): almost always simplifiable — extract with parameters.
- Type 3 (near-miss, ~80%+ similar): likely simplifiable — extract common logic, pass
  the varying parts as parameters or callbacks.
- Duplication across 3+ locations: high-priority simplification.

**Look for:**
- Copy-pasted functions with small parameter differences (Type 2).
- Similar error handling blocks repeated across methods.
- Test setup code duplicated across test functions.
- Query builders with the same structure but different fields.
- Similar validation logic in multiple API endpoints.
- Multiple implementations of the same algorithm with minor variations (Type 3).

**Simplification approach:** For Type 1/2, extract the common logic into a shared
function parameterized over the varying parts. For Type 3, identify the true common
core and extract it, passing divergent behavior as parameters or callbacks. But verify
the duplication is true knowledge duplication — not coincidental similarity that may
diverge.

### 3. Redundant Validation
**Detection heuristic:** The same data validated at 3+ layers for the same conditions.

**Metric thresholds:**
- Same null/range/type check at 3+ layers: simplifiable
- Validation that the type system already enforces: simplifiable

**Look for:**
- Null checks at controller, service, and repository levels for the same field.
- Type assertions after TypeScript/Java has already enforced the type.
- Range checks that the database constraint already enforces.
- Permission checks duplicated at API gateway, controller, and service.
- Schema validation repeated at API boundary and business logic layer.

**Simplification approach:** Validate once at the system boundary (API entry point,
user input, external data). Trust internal code — if a function is called only from
validated contexts, it doesn't need its own validation. The boundary should not trust
its callers, but internals can trust the boundary.

### 4. Unnecessary Comments
**Detection heuristic:** Comments that could be deleted without losing information
not already expressed by the code.

**Look for:**
- `i++; // increment i`, `return result; // return the result`.
- Comments describing what a well-named function does.
- Outdated comments that contradict the current code.
- TODO comments older than 6 months with no associated issue tracker entry.
- Commented-out code with "just in case" notes.
- Javadoc/docstring that merely restates the method signature.

**Simplification approach:** Delete comments that restate the code. Rename unclear
code instead of commenting it. Convert TODOs to tracked issues, then delete the
comment. Keep comments that explain *why*, not *what*.

### 5. Unused Parameters, Imports, and Declarations
**Detection heuristic:** Parameters, imports, types, or declarations not referenced
in the function body or file.

**Look for:**
- Function parameters prefixed with `_` or not referenced at all.
- Imports only used in commented-out code.
- Type definitions or interfaces never referenced.
- Class fields set in constructor but never read.
- Environment variables loaded but never used.
- Constants defined but never referenced.
- Re-exports in barrel files for modules never imported by consumers.

**Simplification approach:** Remove unused parameters (update callers), remove unused
imports, remove unused types. If a parameter is needed for an interface contract,
document why it is intentionally unused.

### 6. Redundant Configuration
**Detection heuristic:** Configuration that duplicates defaults, specifies values that
are never varied, or exists across environments without meaningful differences.

**Look for:**
- Config files that are identical across environments except for one value.
- Environment variables that are always set to the same value.
- Configuration for features that are always on or always off.
- Settings files that duplicate framework defaults verbatim.
- Multiple config formats for the same information (YAML + JSON + env vars).

**Simplification approach:** Remove configuration that matches defaults — rely on the
defaults. Consolidate config formats. Use environment-specific overrides rather than
full copies per environment. Delete config for features that are no longer toggled.

## Language-Specific Notes

- **Python:** `# type: ignore` comments may indicate unnecessary complexity rather
  than unavoidable type issues. `__all__` exports should match actual usage.
  `pylint: disable` on entire files suggests deeper issues. f-strings with no
  interpolation are redundant (just use a string).
- **Java/C#:** IDE-generated getters/setters for fields that are only read or only
  written are redundant. `@SuppressWarnings` should be targeted, not blanket.
  Records (Java 16+) eliminate boilerplate for data carriers.
- **TypeScript:** `@ts-ignore` and `any` casts may indicate unnecessary type
  gymnastics. Re-exported types that could be imported directly. Barrel files that
  re-export everything including unused items. `as const` assertions on values that
  are already const.
- **Go:** `_` parameters in interface implementations are expected (satisfying the
  interface). Blank identifier imports (`_ "package"`) for side effects are
  intentional, not redundant. But unused error returns (`_ = f()`) should be examined.
- **Rust:** `#[allow(dead_code)]` annotations may mask legitimate simplification
  opportunities. `use` imports in modules with `pub use` re-exports should be checked
  for actual usage. `todo!()` and `unimplemented!()` macros left in shipped code are
  dead code signals.

## False Positives to Avoid

- Defensive validation at trust boundaries (external APIs, user input, deserialized
  data) — even if the caller validates too, the boundary should not trust its callers.
- Code that appears unused but is called via reflection, decorators, event systems, or
  framework conventions (e.g., Django signal handlers, Spring `@Scheduled` methods).
- Comments explaining *why* a non-obvious decision was made, not *what* the code does.
- Parameters required by an interface/protocol contract even if the specific
  implementation doesn't use them.
- Seemingly similar code that handles genuinely different business cases that may
  diverge in the future (coincidental duplication, not knowledge duplication).
- Feature flags for features in active A/B testing or gradual rollout — they're
  temporary but not dead.
