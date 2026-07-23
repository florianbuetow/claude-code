# Boundaries — Chapter 8

> Code at the boundary needs clear separation and tests that define expectations.
> You will change the third party eventually; the question is how many of your
> files find out.

## Core idea

A boundary is any seam between code you control and code you do not: a vendor
SDK, an HTTP API, the platform, a package that will have a breaking major
release. The chapter's advice is to keep knowledge of the third party in as few
places as possible, and to learn its behavior through tests rather than by
reading documentation and hoping.

This is the least mechanical dimension. Whether a wrapper is warranted depends
on the client, the dependency, and how likely it is to change — so the bar for
reporting is higher here than anywhere else.

**Owns this dimension:** findings whose fix *adds or changes a seam* — a
wrapper, adapter, interface, or learning test around something external. If the
fix is only renaming the wrapper it is `naming`; if it is only restructuring the
call it is `functions`.

## Violation patterns

### 1. A third-party type spread across the codebase
**Look for:** a vendor class, SDK response object, or ORM entity appearing in
dozens of files; an external type in the signature of your own domain
interfaces; imports of a library in layers that should not know it exists.

**Why it costs:** the vendor's next major version becomes a change across every
one of those files, and none of them can be tested without the vendor.

**Fix:** define your own type at the seam and convert once, at the boundary.
Name the adapter and where it lives.

**Reference:** `Ch.8: Clean Boundaries`.
**Severity:** MEDIUM, HIGH when the dependency is known to be volatile or the
spread is wide.

### 2. No seam at an unstable dependency
**Look for:** direct calls to a beta or pre-1.0 SDK from business logic; a
payment, auth, or messaging provider called inline; API responses consumed as
untyped maps deep inside the domain.

**Fix:** introduce a narrow interface expressing *what your code needs*, not
what the vendor offers, and implement it once.

**Reference:** `Ch.8: Using Third-Party Code`.
**Severity:** MEDIUM.

### 3. A wrapper that is not actually a boundary
**Look for:** an "adapter" that re-exports the vendor's exact signatures; a
wrapper leaking vendor types through its own interface; a facade that passes
through vendor exceptions unchanged.

**Why it costs:** all of the indirection, none of the insulation — callers are
still coupled to the vendor.

**Fix:** make the interface express your needs, and translate vendor errors into
your own at the seam.

**Reference:** `Ch.8: Clean Boundaries`.
**Severity:** MEDIUM.

### 4. Boundary behavior learned by assumption
**Look for:** no tests exercising the third party at all; comments speculating
about its behavior ("I think this returns null when empty"); defensive code
guarding against cases nobody verified; a version bump with no test that would
notice a change.

**Fix:** add learning tests that assert what the library actually does for the
cases you rely on. They document your assumptions and fail loudly on upgrade.

**Reference:** `Ch.8: Exploring and Learning Boundaries`, `Ch.8: Learning Tests
Are Better Than Free`.
**Severity:** MEDIUM when the dependency is critical, LOW otherwise.

### 5. Blocking on an interface that does not exist yet
**Look for:** work stalled awaiting another team's API; a half-built client
guessing at a contract; TODOs waiting on an upstream decision.

**Fix:** define the interface you *wish* you had, code against it, and adapt
when the real thing lands.

**Reference:** `Ch.8: Using Code That Does Not Yet Exist`.
**Severity:** LOW — this is advice more than a defect.

## Do not flag

This dimension produces the most false positives, because "wrap it" always
sounds prudent. It usually is not:

- **The standard library.** `List`, `String`, `Path`, `time` — wrapping these is
  ceremony. The chapter is about volatile third parties.
- **Stable, ubiquitous dependencies** with a long compatibility record and a
  large blast radius if replaced. Nobody should wrap their web framework, test
  runner, or logging facade "just in case".
- **A dependency used in one or two places.** The seam already exists. Wrapping
  adds a layer to insulate two call sites.
- **Small scripts and prototypes.** They will be deleted before the vendor
  changes.
- **Framework integration points.** Controllers *should* know the web framework;
  repositories *should* know the ORM. That is their job.
- **Speculative wrapping.** "You might want to swap this out" with no evidence
  the swap is plausible is speculative generality — a system-level concern
  outside this skill's scope. Note it under Out of scope if it dominates.
- **Generated clients** from OpenAPI or protobuf, which are already a
  regenerable seam.
