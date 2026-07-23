# Comments — Chapter 4

> A comment is a failure to express yourself in code. Not always an avoidable
> one — but every comment should be interrogated before it is accepted.

## Core idea

Comments rot. Code is executed and therefore corrected; comments are not, so
they drift until they actively lie. The default position is that a comment
explaining *what* the code does should have been a better name or a smaller
function. Comments explaining *why* — intent, a non-obvious constraint, a
warning — are valuable and should be left alone.

**Owns this dimension:** findings whose fix is *adding, deleting, or rewriting a
comment*. If the fix is renaming the thing the comment apologises for, route it
to `naming`; if it is extracting the block the comment labels, route it to
`functions`.

## Violation patterns

### 1. Comments compensating for unclear code
**Look for:** a comment restating a condition in English; a comment naming what
a block does immediately above it; `// check if user is active` above
`if (u.s == 1)`.

**Fix:** name the thing. Extract the block into a function whose name is the
comment, or rename the variable. Then delete the comment.

**Reference:** `Ch.4: Comments Do Not Make Up for Bad Code`.
**Severity:** LOW to MEDIUM — the comment is a symptom, and the real cost is the
unclear code beneath it.

### 2. Redundant comments
**Look for:** `// constructor` above a constructor; `// increment i` above `i++`;
generated doc blocks with every `@param` restating the parameter name; a
docstring longer than the function that says less.

**Fix:** delete. It takes longer to read than the code it describes.

**Reference:** `C3: Redundant Comment`.
**Severity:** LOW.

### 3. Obsolete and misleading comments
**Look for:** comments referring to parameters that no longer exist, behavior
that changed, TODOs referencing closed tickets, a described algorithm that does
not match the body.

**Why it costs:** this is the failure mode that causes real defects — a reader
trusts a comment that stopped being true two refactors ago.

**Fix:** correct it, or delete it if the code is now self-explanatory.

**Reference:** `C2: Obsolete Comment`.
**Severity:** HIGH when it contradicts the code, MEDIUM when merely stale.

### 4. Journal comments and bylines
**Look for:** changelog blocks listing dated edits; `// Modified by X on
2019-04-02`; author attributions at the top of every file.

**Why it costs:** version control already has this, accurately, and the comment
version drifts immediately.

**Fix:** delete. `git log` and `git blame` are authoritative.

**Reference:** `C1: Inappropriate Information`, or `Ch.4: Journal Comments`.
**Severity:** LOW.

### 5. Commented-out code
**Look for:** blocks of disabled code, often with "keep for reference" or
"might need this later".

**Why it costs:** nobody dares delete it because nobody knows if it matters, so
it accumulates forever and misleads every reader about what the module does.

**Fix:** delete. It is in the history.

**Reference:** `C5: Commented-Out Code`.
**Severity:** MEDIUM.

### 6. Banners, position markers, and closing-brace labels
**Look for:** `////////// SECTION //////////`; `// end of loop`; `} // end if`.

**Fix:** delete. If a file needs section banners to be navigable, the real
problem is module structure — an architecture concern outside this skill's
scope; note it under Out of scope rather than analysing it here.

**Reference:** `Ch.4: Banner Comments`, `Ch.4: Position Markers`, or
`G12: Clutter`.
**Severity:** LOW.

### 7. Mumbling and poorly written comments
**Look for:** comments that trail off, assume context the reader lacks, or are
too terse to act on — `// hack`, `// don't touch`, `// fix later`.

**Fix:** rewrite to state the actual constraint, or delete.

**Reference:** `C4: Poorly Written Comment`, or `Ch.4: Mumbling`.
**Severity:** LOW, MEDIUM if it warns of a real hazard without saying what.

## Do not flag

Over-flagging comments makes a reviewer insufferable. Leave these alone:

- **Why-comments.** Anything explaining a non-obvious decision, a workaround for
  an upstream bug, a performance trade-off, or a regulatory constraint. These
  are the comments the chapter explicitly endorses.
- **Legal headers and licence blocks.** Required, not clutter.
- **Public API documentation.** Docstrings on an exported interface serve
  consumers who cannot read the body. Judge quality, not existence.
- **Warnings of consequence.** "Not thread-safe", "this test is slow",
  "mutates the argument" — these earn their place.
- **TODOs that are current and specific**, especially with a ticket reference.
- **Informative comments** giving a regex's intended match, a format's shape, or
  an example of expected input.
- **Doc comments a linter or the project's tooling requires.** Fighting the
  project's own configuration is not a clean-code finding.
