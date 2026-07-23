# Chapter 17 Citation Registry

**This is not a dimension.** It has no subcommand. It is the authoritative list
of heuristic codes from *Clean Code* Chapter 17, consulted on every route so
that each finding carries a reference that can be checked.

## The reference rule

Every finding's `Reference` field is filled by exactly one of two forms:

1. **A registry code**, when this file lists one that matches the violation —
   `G30`, `N5`, `C1`, `F3`, `T5`. Codes not listed here do not exist.
2. **A chapter rule**, when no code matches — written `Ch.N: <rule name>`, e.g.
   `Ch.7: Don't Ignore Caught Errors`. The canonical fallback rules are listed
   at the end of this file.

**Never synthesise a code.** The catalog stops at G36, N7, C5, E2, F4, T9 and
J3. `G47` does not exist. A fabricated code carries the same authority as a real
one to a reader who has not memorised the list, which makes it worse than no
reference at all.

If a finding fits neither a registry code nor a canonical chapter rule, treat
that as evidence the finding is not well-grounded and drop it.

## The code family says nothing about routing

A finding's dimension is decided by the smallest edit that resolves it (see
`SKILL.md`), not by the letter of its code. These are independent axes:

| Finding | Dimension | Reference |
|---|---|---|
| `DAYS_IN_WEEK` beside `daysInMonth` | `naming` | `G11` (general) |
| Callee declared far above its caller | `formatting` | `G10` (general) |
| Boolean parameter selecting behavior | `functions` | `F3` (functions) |
| Changelog block above a function | `comments` | `C1` (comments) |

`G`-codes in particular annotate findings across every dimension.

---

## G — General (G1-G36)

| Code | Rule |
|------|------|
| G1 | Multiple Languages in One Source File |
| G2 | Obvious Behavior Is Unimplemented |
| G3 | Incorrect Behavior at the Boundaries |
| G4 | Overridden Safeties |
| G5 | Duplication |
| G6 | Code at Wrong Level of Abstraction |
| G7 | Base Classes Depending on Their Derivatives |
| G8 | Too Much Information |
| G9 | Dead Code |
| G10 | Vertical Separation |
| G11 | Inconsistency |
| G12 | Clutter |
| G13 | Artificial Coupling |
| G14 | Feature Envy |
| G15 | Selector Arguments |
| G16 | Obscured Intent |
| G17 | Misplaced Responsibility |
| G18 | Inappropriate Static |
| G19 | Use Explanatory Variables |
| G20 | Function Names Should Say What They Do |
| G21 | Understand the Algorithm |
| G22 | Make Logical Dependencies Physical |
| G23 | Prefer Polymorphism to If/Else or Switch/Case |
| G24 | Follow Standard Conventions |
| G25 | Replace Magic Numbers with Named Constants |
| G26 | Be Precise |
| G27 | Structure over Convention |
| G28 | Encapsulate Conditionals |
| G29 | Avoid Negative Conditionals |
| G30 | Functions Should Do One Thing |
| G31 | Hidden Temporal Coupling |
| G32 | Don't Be Arbitrary |
| G33 | Encapsulate Boundary Conditions |
| G34 | Functions Should Descend Only One Level of Abstraction |
| G35 | Keep Configurable Data at High Levels |
| G36 | Avoid Transitive Navigation |

**Frequently applicable, easily confused:**

- **G5 Duplication** — the same knowledge expressed twice. Note that broad
  system-level DRY analysis belongs to `beyond-solid-principles`; cite G5 here
  only for local duplication whose fix is a local extraction.
- **G20 vs N1** — G20 is specifically a function name that does not describe
  what the function does. N1 is the general "choose descriptive names". Prefer
  G20 for functions and methods; it is the more precise citation.
- **G23 vs G15** — G23 is type-code dispatch that should be polymorphism. G15 is
  an argument used to select behavior inside the callee.
- **G10 Vertical Separation** — declarations distant from use, callers distant
  from callees. This is the standard citation for `formatting` findings.
- **G14 Feature Envy** — a method more interested in another object's data than
  its own. Cite for `objects-data`.
- **G36 Avoid Transitive Navigation** — train wrecks, `a.getB().getC().getD()`.
  The Law of Demeter citation.

## N — Names (N1-N7)

| Code | Rule |
|------|------|
| N1 | Choose Descriptive Names |
| N2 | Choose Names at the Appropriate Level of Abstraction |
| N3 | Use Standard Nomenclature Where Possible |
| N4 | Unambiguous Names |
| N5 | Use Long Names for Long Scopes |
| N6 | Avoid Encodings |
| N7 | Names Should Describe Side-Effects |

**N5** is the citation for a single-letter identifier spanning a long body — the
scope determines the required name length. A one-line lambda parameter named `x`
is fine; the same name across thirty lines is not.

## C — Comments (C1-C5)

| Code | Rule |
|------|------|
| C1 | Inappropriate Information |
| C2 | Obsolete Comment |
| C3 | Redundant Comment |
| C4 | Poorly Written Comment |
| C5 | Commented-Out Code |

**C1** covers information better held in another system — a changelog, an
author list, or a ticket history in a comment belongs in version control. This
is the correct citation for journal comments.

## F — Functions (F1-F4)

| Code | Rule |
|------|------|
| F1 | Too Many Arguments |
| F2 | Output Arguments |
| F3 | Flag Arguments |
| F4 | Dead Function |

## E — Environment (E1-E2)

| Code | Rule |
|------|------|
| E1 | Build Requires More Than One Step |
| E2 | Tests Require More Than One Step |

Rarely applicable to a source-file review; cite only when analyzing build or
test tooling directly.

## T — Tests (T1-T9)

| Code | Rule |
|------|------|
| T1 | Insufficient Tests |
| T2 | Use a Coverage Tool! |
| T3 | Don't Skip Trivial Tests |
| T4 | An Ignored Test Is a Question about an Ambiguity |
| T5 | Test Boundary Conditions |
| T6 | Exhaustively Test Near Bugs |
| T7 | Patterns of Failure Are Revealing |
| T8 | Test Coverage Patterns Can Be Revealing |
| T9 | Tests Should Be Fast |

Note the gap: the catalog has **no code for "one concept per test"**, which is a
Chapter 9 rule. Cite `Ch.9: One Concept per Test` rather than stretching T1.

## J — Java-specific (J1-J3)

| Code | Rule |
|------|------|
| J1 | Avoid Long Import Lists by Using Wildcards |
| J2 | Don't Inherit Constants |
| J3 | Constants versus Enums |

Cite only when analyzing Java. J1 in particular conflicts with the house style
of most modern Java projects and their linters — prefer to stay silent unless
the project's own configuration agrees.

---

## Canonical chapter fallbacks

When no code above matches, cite one of these. This list is closed: do not
invent new rule names.

**Ch.2 — Meaningful Names**
`Use Intention-Revealing Names` · `Avoid Disinformation` · `Make Meaningful
Distinctions` · `Use Pronounceable Names` · `Use Searchable Names` · `Class
Names` · `Method Names` · `Pick One Word per Concept` · `Don't Pun` · `Add
Meaningful Context` · `Don't Add Gratuitous Context`

**Ch.3 — Functions**
`Small!` · `Do One Thing` · `One Level of Abstraction per Function` · `Use
Descriptive Names` · `Function Arguments` · `Have No Side Effects` · `Command
Query Separation` · `Prefer Exceptions to Returning Error Codes` · `Extract Try/
Catch Blocks`

**Ch.4 — Comments**
`Comments Do Not Make Up for Bad Code` · `Explain Yourself in Code` · `Legal
Comments` · `Informative Comments` · `Explanation of Intent` · `Warning of
Consequences` · `TODO Comments` · `Mumbling` · `Noise Comments` · `Position
Markers` · `Banner Comments` · `Journal Comments` · `Attributions and Bylines`

**Ch.5 — Formatting**
`The Newspaper Metaphor` · `Vertical Openness Between Concepts` · `Vertical
Density` · `Vertical Distance` · `Conceptual Affinity` · `Horizontal
Formatting` · `Team Rules`

**Ch.6 — Objects and Data Structures**
`Data Abstraction` · `Data/Object Anti-Symmetry` · `The Law of Demeter` · `Train
Wrecks` · `Hybrids` · `Hiding Structure` · `Data Transfer Objects`

**Ch.7 — Error Handling**
`Use Exceptions Rather Than Return Codes` · `Provide Context with Exceptions` ·
`Define Exception Classes in Terms of a Caller's Needs` · `Define the Normal
Flow` · `Don't Return Null` · `Don't Pass Null` · `Don't Ignore Caught Errors`

**Ch.8 — Boundaries**
`Using Third-Party Code` · `Exploring and Learning Boundaries` · `Learning
Tests Are Better Than Free` · `Using Code That Does Not Yet Exist` · `Clean
Boundaries`

**Ch.9 — Unit Tests**
`Keep Tests Clean` · `Tests Enable the -ilities` · `Clean Tests` · `One Assert
per Test` · `One Concept per Test` · `F.I.R.S.T.`

**Ch.13 — Concurrency**
`Limit the Scope of Data` · `Use Copies of Data` · `Threads Should Be as
Independent as Possible` · `Know Your Library` · `Know Your Execution Models` ·
`Beware Dependencies Between Synchronized Methods` · `Keep Synchronized
Sections Small` · `Writing Correct Shut-Down Code Is Hard` · `Testing Threaded
Code`
