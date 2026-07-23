---
name: clean-code
version: 0.2.0
description: >
  This skill should be used when the user asks to "check clean code", "review
  code cleanliness", "find code smells", "is this function too long", "are these
  names clear", "review my error handling", "check my tests", or "clean up this
  code". Also triggers when the user mentions Clean Code, Uncle Bob, Robert
  Martin, meaningful names, function length, comment rot, F.I.R.S.T. tests, or
  names a dimension directly ("naming", "boundaries", "concurrency"). Supports
  auditing all nine dimensions at once or focusing on a single dimension.
disable-model-invocation: false
---

# Clean Code — Code-Level Cleanliness Analysis

Analyze source code against Robert C. Martin's *Clean Code* and report what to
change. Nine dimensions covering the code you read every day: names, functions,
comments, formatting, data, errors, boundaries, tests, concurrency.

This never modifies code. It reports findings; the user decides what to act on.

## What this skill is not

SOLID tells you how to structure classes. This works one level down — the
code inside them. Three concerns are **out of scope**, corresponding to the
book's chapters 10-12, and are not analyzed here:

- Class responsibility, inheritance, interface design, dependency inversion
- Package/module architecture, dependency structure, architectural smells
- System-level over-engineering and speculative generality

When target code's dominant problem is one of these, say so in one line under
**Out of scope** in the summary — naming the concern, not analyzing it — and
report only the code-level findings this skill owns. Noting an out-of-scope
concern is a valid, useful outcome; analyzing it here is not.

## The nine dimensions

| Dimension | Chapter | Covers | Reference |
|-----------|---------|--------|-----------|
| **naming** | 2 | Intention-revealing names, disinformation, noise, searchability, consistency | `references/naming.md` |
| **functions** | 3 | Size, one thing, abstraction level, arguments, flags, side effects | `references/functions.md` |
| **comments** | 4 | Comments compensating for bad code, redundancy, rot, commented-out code | `references/comments.md` |
| **formatting** | 5 | Vertical distance, proximity of caller and callee, ordering, density | `references/formatting.md` |
| **objects-data** | 6 | Data/object anti-symmetry, Law of Demeter, train wrecks, hybrids | `references/objects-data.md` |
| **error-handling** | 7 | Exceptions over codes, no null in or out, context, failure visibility | `references/error-handling.md` |
| **boundaries** | 8 | Third-party seams, wrappers, learning tests, code you don't control | `references/boundaries.md` |
| **unit-tests** | 9 | F.I.R.S.T., one concept per test, test readability and independence | `references/unit-tests.md` |
| **concurrency** | 13 | Shared state, synchronized scope, coordination, testing threaded code | `references/concurrency.md` |

`references/heuristics.md` is the **Chapter 17 citation registry**. It is not a
dimension and has no subcommand. It is the authoritative list of valid
`G`/`N`/`C`/`E`/`F`/`T` codes and is consulted on every route to attach a
verified reference to each finding.

## Subcommands

| Command | Scope |
|---------|-------|
| `cleancode` / `cleancode all` / `cleancode check` | All nine dimensions |
| `cleancode names` / `cleancode naming` | Naming only |
| `cleancode functions` | Functions only |
| `cleancode comments` | Comments only |
| `cleancode formatting` | Formatting only |
| `cleancode objects` / `cleancode data` | Objects & Data Structures only |
| `cleancode errors` / `cleancode error-handling` | Error Handling only |
| `cleancode boundaries` | Boundaries only |
| `cleancode tests` | Unit Tests only |
| `cleancode concurrency` | Concurrency only |

Default to all nine when no subcommand is given. Match a dimension named without
the `cleancode` prefix ("check my error handling").

A narrow subcommand is a **filter, not a hint**. `cleancode functions` must not
report a rename-only naming finding even when it notices one. `cleancode all`
reports both.

## Routing: which dimension owns a finding

This is the rule that keeps subcommands predictable. Without it, the same
violation surfaces or vanishes depending on what the user typed.

> **The owning dimension is the one that owns the smallest concrete refactoring
> edit that fully resolves the finding.**
>
> The chapter that discusses the problem, the section heading of whatever guide
> you learned it from, and the letter family of the Chapter 17 code **never**
> determine routing.

| The sufficient fix is to... | Dimension |
|---|---|
| Rename an identifier — variable, function, method, class, or fix its capitalization | `naming` |
| Change decomposition, signature, parameters, control flow, side effects, or body | `functions` |
| Add, delete, or rewrite a comment | `comments` |
| Move code, change ordering, proximity, blank lines, or import grouping — no behavior change | `formatting` |
| Change data representation, or what an object exposes versus hides | `objects-data` |
| Change an error path, exception, rejection, or error return | `error-handling` |
| Add or change a seam, wrapper, adapter, or learning test around an external API | `boundaries` |
| Change test structure, naming, setup, assertions, independence, or speed | `unit-tests` |
| Change shared-state access, coordination, scheduling, or synchronization | `concurrency` |

**Worked consequences of the rule:**

- A function named `addToDate` that adds a month is `naming` — the sufficient
  fix is a rename. Chapter 3 also discusses function names; that does not make
  it a `functions` finding.
- A function whose body does three things is `functions`, even though renaming
  it would also be an improvement — a rename alone does not resolve it.
- `DAYS_IN_WEEK` beside `daysInMonth` is `naming` (a rename fixes it) and cites
  `G11 Inconsistency`, a *general* heuristic. Dimension and code family are
  different axes and are allowed to differ.
- Callers separated from callees is `formatting` — moving code fixes it.

**If two independent edits are required, emit two findings.** Do not force a
composite problem into one arbitrary winner. On `cleancode all`, deduplicate by
location plus root cause so one defect is not reported twice.

## Workflow

### 1. Identify target code

Use the files or directory given. If a symbol is named, locate it. If nothing is
specified and the request is not obviously about the whole repo, ask which files
to scan rather than guessing — scanning everything produces unusable volume.

Any language: Python, Java, TypeScript, C#, Go, Rust, PHP, Kotlin, C++. Apply
each rule to the target language's idioms rather than transliterating the book's
Java examples. Go's explicit error returns are not an error-handling violation.
Python's duck typing is not a missing interface.

### 2. Load references

Read the reference file for each requested dimension, plus
`references/heuristics.md` always. For `cleancode all`, read all ten.

### 3. Analyze — and exercise restraint

Apply the patterns from the loaded references. **The dominant failure mode of a
code reviewer is flagging everything.** A reviewer that reports something about
every file is one users stop running.

Before reporting, each candidate must clear all four:

1. **Is it real?** Would a competent developer reading this agree it is worse
   than the alternative — not merely different?
2. **Is it in scope?** If the fix is a class-responsibility, architecture, or
   system-complexity change, defer to the sibling plugin instead.
3. **Can you name the edit?** If you cannot state the specific change, you do
   not understand the problem well enough to report it.
4. **Does it survive context?** A 30-line script, a test fixture, generated
   code, and a vendored file are not held to production-module standards. Code
   elided with placeholder markers (`// ...`, `# ...`, a bare `...`) is a
   fragment: never report on what the elision hides — a test body of `// ...`
   is an elided example, not a test without assertions.

Code that is clean enough gets no finding. Reporting "no significant findings"
is a valid and frequently correct result.

### 4. Report

Every finding carries exactly five fields:

```
**[DIMENSION] — Severity: HIGH | MEDIUM | LOW**
Location:  `path/file.ext`, symbol `name`, lines ~XX-YY
Reference: G30: Functions Should Do One Thing
Issue:     What is wrong and what it costs the reader or the next change.
Fix:       The specific edit. Not a restatement of the principle.
```

**The Reference field is governed by a hard rule.** Every reference is a
**verbatim quote from `references/heuristics.md`** — that file is the closed
vocabulary, and there are exactly two legal forms:

1. A registry code with its rule name, exactly as the registry's tables give
   them: `G30: Functions Should Do One Thing`, `N5: Use Long Names for Long
   Scopes`.
2. A canonical chapter rule, exactly as the registry's fallback list gives it:
   `Ch.7: Don't Ignore Caught Errors`, `Ch.9: F.I.R.S.T.`.

Copy the entry character-for-character. Do not paraphrase a rule name, do not
merge two rules, and do not append qualifiers — `Ch.9: F.I.R.S.T.
(Self-validating)` is **invalid** because the parenthetical is not in the
registry; the finding's Issue text is the place to say which letter is
violated.

**Never invent a code or a rule name.** `G47` does not exist, and neither does
any chapter rule you cannot point to in the registry. A fabricated reference is
indistinguishable from a real one to the reader, which makes it worse than no
reference. If no registry entry fits, that is a signal the finding is not
solid — drop it.

Before emitting a report, re-check every Reference against the registry file.
One unverifiable reference invalidates trust in all of them.

**Fix quality.** "Consider making this function do one thing" is a restatement,
not a fix. "Extract lines 12-19 into `isEligibleForShipping(order)` and call it
from the filter" is a fix. Name the symbols.

### Severity

Severity is the **cost of leaving it alone**, not how much it offends:

- **HIGH** — actively misleads readers or hides defects. Names that state
  something false, swallowed exceptions, nulls returned into unsuspecting
  callers, public mutable state with an invariant to protect, a data race.
- **MEDIUM** — compounding friction. Long functions, mixed abstraction levels,
  train wrecks, a test asserting four concepts, duplicated error paths.
- **LOW** — polish. Formatting, redundant comments, mild naming inconsistency.

If nearly everything is HIGH, the severity axis has stopped carrying
information. Re-check against cost of inaction.

### Summary

After the findings:

- **Count table**: `| Dimension | HIGH | MEDIUM | LOW |`
- **Top 3**: which to fix first, and why those.
- **Out of scope**: any class-design, architecture, or system-complexity
  concern noticed along the way, named in one line each — not analyzed.

On a large target, rank by severity and cap the report at the ~15 findings that
matter most, stating how many were omitted. An unranked wall of 200 findings is
not a review.

### 5. Fix mode (optional)

When the user asks to "fix it" or "clean it up" after an audit, produce the
revised code implementing the reported fixes. Change only what the findings
identified. Explain each edit in one line.

## Pragmatism

- **Scale matters.** A prototype gets a lighter touch than a payments module.
- **Deliberate trade-offs are not violations.** If a comment or commit explains
  why, engage with the reason instead of asserting the rule.
- **Language idioms win.** Judge against the norms of the language in front of
  you.
- **Essential complexity is not a smell.** Hard domains produce demanding code.
- **Five real findings beat twenty trivial ones.**
