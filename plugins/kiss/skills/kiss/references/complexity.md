# Code Complexity — Simplification Opportunities

> "Debugging is twice as hard as writing the code in the first place. Therefore, if you
> write the code as cleverly as possible, you are, by definition, not smart enough to
> debug it."
> — Brian Kernighan

## Core Idea

Code complexity becomes a simplification opportunity when the implementation is harder
to understand than the problem it solves. The goal is to identify places where control
flow, cognitive load, function structure, or expression density can be reduced — making
code easier to read, debug, and maintain without losing capability.

Two complementary lenses from the research:

- **Cyclomatic complexity** counts independent execution paths (branches). It measures
  how many tests you need for full coverage. Threshold: functions above ~10 are
  candidates for simplification.
- **Cognitive complexity** (SonarSource model) weights constructs by how much mental
  effort they demand — nesting adds incrementally, breaks in linear flow (recursion,
  jumps) add more. This better predicts human difficulty than path counting alone.
  Threshold: functions above ~15 are candidates.

Both are proxies. The real question is always: "Can a competent developer understand
this function in one reading?"

## Simplification Patterns

### 1. Deep Nesting
**Detection heuristic:** Functions with 4+ levels of indentation from nested
if/for/try blocks. Each nesting level multiplies cognitive load — 3 levels deep means
tracking 3 simultaneous conditions.

**Metric thresholds:**
- Nesting depth ≥ 4: likely simplifiable
- Nesting depth ≥ 6: almost certainly simplifiable

**Look for:**
- Arrow-shaped code drifting steadily to the right.
- Deeply nested callbacks (especially in async code).
- Nested loops with conditions inside conditions.
- Try/catch blocks inside conditional blocks inside loops.

**Simplification approach:** Extract inner blocks into named functions. Use early
returns and guard clauses to flatten the main path. Use `continue`/`break` to reduce
nesting inside loops. In async code, use async/await to flatten callback pyramids.

### 2. Long Functions
**Detection heuristic:** Functions exceeding ~50 lines or handling more than one
logical responsibility. Length alone is a weak signal — a 100-line function doing one
clear thing sequentially is simpler than a 30-line function with tangled control flow.

**Metric thresholds:**
- Lines > 50 with multiple logical sections: likely simplifiable
- Lines > 100: almost certainly simplifiable regardless
- Parameters > 5: the function likely does too much
- Local variables > 10: accumulated state suggests multiple responsibilities

**Look for:**
- Functions requiring scrolling to read entirely.
- Blank lines or comments acting as section headers within a function.
- Many local variables accumulated throughout the body.
- Functions where the name cannot describe what they do in a few words.

**Simplification approach:** Extract logical sections into well-named functions, each
doing one thing. The original function becomes a readable sequence of high-level steps.
If parameters are many, consider whether some belong in a data structure or whether the
function is doing too much.

### 3. Convoluted Control Flow
**Detection heuristic:** Nested ternaries, complex boolean expressions with 3+
conditions, inconsistent return patterns within a single function.

**Metric thresholds:**
- Boolean conditions with 3+ operators: likely simplifiable
- Nested ternary expressions: always simplifiable
- Functions mixing early returns and a late return: inconsistent, simplifiable

**Look for:**
- `condition ? (nested ? a : b) : c` — nested ternaries.
- `if (a && (b || c) && !d && e)` — dense multi-part boolean logic.
- Functions with both early returns and a final return, making exit paths unclear.
- Switch/case fall-through patterns that require tracking state across cases.

**Simplification approach:** Replace nested ternaries with if/else or switch. Extract
complex conditions into named boolean variables (e.g., `const isEligible = ...`). Pick
one return style and be consistent. Use lookup tables or maps to replace long
conditional chains.

### 4. High Branch Density
**Detection heuristic:** Functions with 10+ branches (if/else chains, switch cases)
making exhaustive reasoning and testing difficult.

**Metric thresholds:**
- Cyclomatic complexity > 10: likely simplifiable
- Cyclomatic complexity > 20: almost certainly simplifiable
- Cognitive complexity > 15: likely simplifiable

**Look for:**
- Long if/elif/else chains handling many cases.
- Switch statements with 10+ cases and non-trivial logic per case.
- Multiple nested loops with break/continue.
- Mixed exception handling interleaved with business logic.

**Simplification approach:** Use strategy or dispatch patterns. Extract branches into
separate functions. Use lookup tables or maps to replace conditional chains. For switch
statements with complex per-case logic, extract each case into a named function.

### 5. Clever Code
**Detection heuristic:** Bitwise tricks, regex abuse, one-liners that sacrifice
readability for brevity. Code that requires a comment to explain what it does (not
why — the what should be self-evident).

**Look for:**
- Bitwise operations for non-bitwise problems (e.g., `n & 1` instead of `n % 2`).
- Complex list comprehensions spanning multiple lines.
- Chained method calls exceeding 4+ steps with transformations.
- Magic numbers without named constants.
- Regular expressions used for parsing that would be clearer as string operations.

**Simplification approach:** Use readable alternatives. Break complex expressions into
steps with named intermediates. Add constants for magic values. Replace regex with
string operations when the pattern is simple. A few extra lines of clear code beats
one line of clever code.

### 6. Data Flow Complexity
**Detection heuristic:** Variables with long lifetimes (declared far from use),
reassigned multiple times, or involved in complex dependency chains where understanding
a value requires tracing through many assignments.

**Metric thresholds:**
- Variable lifetime > 30 lines: likely simplifiable
- Variable reassigned > 3 times: likely simplifiable
- Mutable state shared across 3+ functions: likely simplifiable

**Look for:**
- Variables declared at the top of a function but not used until the bottom.
- Variables reassigned multiple times with different meanings.
- Data transformations spread across many functions that could be pipelined.
- Mutable state passed through long call chains.

**Simplification approach:** Move declarations close to first use. Use `const`/`final`
where possible — immutability reduces mental tracking. Extract transformation sequences
into a pipeline or named steps. Reduce variable lifetime by extracting blocks into
functions.

## Language-Specific Notes

- **Python**: List comprehensions are idiomatic but nested comprehensions are a code
  smell. Generator expressions can replace complex loops. `match` (3.10+) simplifies
  long if/elif chains. `walrus operator` (:=) can reduce nesting but can also reduce
  readability — use with care.
- **Java/C#**: Stream/LINQ chains are idiomatic but should be broken up past 4-5
  operations. Switch expressions (Java 14+, C# 8+) simplify conditional logic. Pattern
  matching in recent versions can flatten type-checking logic.
- **TypeScript**: Optional chaining (`?.`) and nullish coalescing (`??`) reduce nesting.
  Discriminated unions with exhaustive switches are idiomatic, not complex. Type
  narrowing replaces manual type checks.
- **Go**: Explicit error handling adds lines but is idiomatic, not a complexity issue.
  Table-driven tests are preferred over long test functions. The `if err != nil` pattern
  is not a simplification target.
- **Rust**: Pattern matching with `match` is idiomatic even when lengthy. The `?`
  operator for error propagation is the simplification — not a sign of complexity.
  Lifetime annotations add syntax but not accidental complexity.

## False Positives to Avoid

- State machines with many transitions — the complexity is essential to the domain.
- Parser/compiler code with deep recursion — tree-structured problems produce
  tree-structured code.
- Mathematical algorithms where the math itself is complex — the code reflects the
  math faithfully.
- Configuration/routing files with many entries — length is not complexity when each
  entry is simple and independent.
- Go's explicit error handling — `if err != nil` is repetitive but idiomatic and clear.
- Exhaustive switch statements over a discriminated union — they may be long but each
  case is simple and the compiler enforces completeness.
