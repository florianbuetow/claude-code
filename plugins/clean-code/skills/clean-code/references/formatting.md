# Formatting — Chapter 5

> Code should read like a newspaper: the headline first, then the broad strokes,
> with detail further down. You should be able to stop reading at any point and
> have understood something complete.

## Core idea

Formatting here means **where code sits relative to other code** — not
whitespace pedantry. Vertical distance, ordering, and grouping are what let a
reader follow a file without jumping. Character-level concerns (indent width,
comma spacing, line length) belong to the project's formatter, not to a review.

**Owns this dimension:** findings whose fix is *moving code, changing order, or
adjusting grouping, with no behavior change*. If the fix renames something it is
`naming`; if it extracts or merges functions it is `functions`.

## Violation patterns

### 1. Callers far from callees
**Look for:** a private helper declared at the top of a class, its only caller
two hundred lines below; a chain of small functions in an order unrelated to how
they call each other.

**The rule:** a function should appear just below its caller. Reading top to
bottom should descend the call graph, so the reader meets the policy before the
mechanism.

**Fix:** reorder. Name the sequence explicitly in the finding — `perfReview`,
`getPeerReviews`, `lookupPeers`, `getManagerReview`, `lookupManager`.

**Reference:** `G10: Vertical Separation`, or `Ch.5: Vertical Distance`.
**Severity:** LOW, MEDIUM in a large file where the jump is long.

### 2. Declarations far from use
**Look for:** all locals declared at the top of a long function in C89 style;
a variable assigned forty lines before it is read; instance fields used by only
one method, declared far from it.

**Fix:** move each declaration adjacent to its first use.

**Reference:** `G10: Vertical Separation`.
**Severity:** LOW.

### 3. Conceptually related code scattered
**Look for:** overloads of the same operation separated by unrelated members;
a getter and its setter pages apart; related constants spread across a file.

**Fix:** group by affinity — things that change together should sit together.

**Reference:** `Ch.5: Conceptual Affinity`.
**Severity:** LOW.

### 4. Missing or excessive vertical openness
**Look for:** a wall of statements with no blank lines separating distinct
thoughts; or the opposite — a blank line between every statement, destroying the
sense that lines form a group.

**Fix:** one blank line between concepts, none within them.

**Reference:** `Ch.5: Vertical Openness Between Concepts`, `Ch.5: Vertical
Density`.
**Severity:** LOW.

### 5. Disorganised imports and file preamble
**Look for:** imports in no order and regrouped arbitrarily on every edit; a
mix of grouped and ungrouped; unused imports left behind.

**Fix:** adopt the project's convention; delete unused.

**Reference:** `G24: Follow Standard Conventions`, or `G12: Clutter`.
**Severity:** LOW. Skip only when the project *visibly* has an import-sorting
tool (a formatter config, lint rule, or consistently machine-sorted imports
elsewhere) — then it is that tool's job. Absent such evidence, disordered
imports are a reportable LOW finding, not "left to tooling".

### 6. Inconsistency with the file's own conventions
**Look for:** one method braced differently from every other; a single
snake_case member in a camelCase file; a lone tab in a spaces file.

**The test:** does this code disagree with *the code around it*? Local
consistency beats any external style preference.

**Reference:** `G11: Inconsistency`, `Ch.5: Team Rules`.
**Severity:** LOW.

## Do not flag

Formatting is the easiest dimension to become annoying in. The bar is high:

- **Anything an auto-formatter owns.** Indentation, line length, comma spacing,
  brace position, trailing commas. If the project has Prettier, gofmt, Black,
  rustfmt, or an `.editorconfig`, that tool is the authority and formatting
  findings against it are noise. Check for a config before reporting anything in
  this dimension.
- **A style that is consistent but not your preference.** Consistency is the
  standard; there is no house style to impose.
- **Generated files, vendored code, lockfiles, migrations.**
- **Language conventions that look odd elsewhere.** Go's tabs, Python's
  significant indentation, Lisp's trailing parens.
- **Long lines containing a URL, a regex, a hash, or a long string literal** —
  breaking them makes them worse.
- **File length.** "This file is too long" is a module-structure concern
  outside this skill's scope. Note it under Out of scope rather than filing it
  here.
