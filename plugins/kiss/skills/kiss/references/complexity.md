# Complexity

> "Debugging is twice as hard as writing the code in the first place. Therefore, if you write the code as cleverly as possible, you are, by definition, not smart enough to debug it."
> — Brian Kernighan

## Core Idea

Code complexity refers to accidental complexity in control flow, function length, and
expression density that makes code harder to read, debug, and maintain than the problem
requires. Every branch, nesting level, and clever trick adds cognitive load for the next
reader — who is often your future self.

The goal is not to eliminate all complexity but to distinguish essential complexity (inherent
to the problem domain) from accidental complexity (introduced by the implementation). When
code is more complex than the problem it solves, it is a candidate for simplification.

## Violation Patterns

### 1. Deep Nesting
**Heuristic**: Functions with 4+ levels of indentation from nested if/for/try blocks.

**Look for**:
- Arrow-shaped code that drifts steadily to the right.
- Deeply nested callbacks (especially in asynchronous code).
- Nested loops with conditions inside conditions.

**Refactoring**: Extract inner blocks into named functions, use early returns and
guard clauses to flatten the main path, use `continue`/`break` to reduce nesting
inside loops.

### 2. Long Functions/Methods
**Heuristic**: Functions exceeding ~50 lines that do too many things sequentially.

**Look for**:
- Functions that require scrolling to read in their entirety.
- Multiple sections separated by blank lines or comments acting as section headers.
- Many local variables accumulated throughout the function body.

**Refactoring**: Extract logical sections into well-named functions, each doing one
thing. The original function becomes a readable sequence of high-level steps.

### 3. Convoluted Control Flow
**Heuristic**: Nested ternaries, complex boolean expressions with 3+ conditions,
mixed early returns and late returns in the same function.

**Look for**:
- `condition ? (nested ? a : b) : c` — nested ternary expressions.
- `if (a && (b || c) && !d && e)` — dense multi-part boolean logic.
- Functions with both early returns and a final return, making it unclear which
  path reaches which exit.

**Refactoring**: Replace nested ternaries with if/else or switch, extract complex
conditions into named boolean variables (e.g., `const isEligible = ...`), pick one
return style and be consistent.

### 4. High Cyclomatic Complexity
**Heuristic**: Functions with 10+ branches making them hard to reason about and test
exhaustively.

**Look for**:
- Long if/elif/else chains handling many cases.
- Switch statements with 10+ cases.
- Multiple nested loops with break/continue.

**Refactoring**: Use strategy or dispatch patterns, extract branches into separate
functions, use lookup tables or maps to replace conditional chains.

### 5. Clever Code
**Heuristic**: Bitwise tricks, regex abuse, one-liners that sacrifice readability
for brevity.

**Look for**:
- Bitwise operations for non-bitwise problems (e.g., `n & 1` instead of `n % 2`).
- Complex list comprehensions spanning multiple lines.
- Chained method calls exceeding 4+ steps.
- Magic numbers without named constants.

**Refactoring**: Use readable alternatives, break complex expressions into steps with
named intermediates, add constants for magic values.

## Language-Specific Notes

- **Python**: List comprehensions are idiomatic but nested comprehensions are a code
  smell. Generator expressions can replace complex loops. `match` statements (3.10+)
  can simplify long if/elif chains.
- **Java/C#**: Stream/LINQ chains are idiomatic but should be broken up when exceeding
  4-5 operations. Switch expressions (Java 14+, C# 8+) can simplify conditional logic.
- **TypeScript**: Optional chaining (`?.`) and nullish coalescing (`??`) reduce nesting.
  Discriminated unions with exhaustive switches are idiomatic, not complex.
- **Go**: Explicit error handling adds lines but is idiomatic, not a complexity violation.
  Table-driven tests are preferred over long test functions.

## False Positives to Avoid

- State machines with many transitions — the complexity is essential to the domain.
- Parser/compiler code with deep recursion — tree-structured problems produce
  tree-structured code.
- Mathematical algorithms where the math itself is complex — the code reflects the
  math faithfully.
- Configuration/routing files with many entries — length does not equal complexity when
  each entry is simple and independent.
