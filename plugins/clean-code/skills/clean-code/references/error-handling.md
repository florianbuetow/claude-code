# Error Handling — Chapter 7

> Error handling is important, but if it obscures logic, it is wrong. And an
> error that is silently discarded is worse than one that crashes: the crash
> tells you something.

## Core idea

Two goals in tension: failures must be impossible to ignore, and the normal path
must stay readable. The chapter's answer is exceptions carrying context, thrown
at the point of failure and handled where something can actually be done —
rather than error codes threaded through every signature, or nulls that defer
the failure to a random later line.

**Owns this dimension:** findings whose fix changes *an error path* — what is
thrown, caught, returned, logged, or propagated. If the fix is extracting a
try/catch into its own function, that is a `functions` finding.

## Violation patterns

### 1. Swallowed exceptions
**Look for:** an empty catch block; a catch containing only a comment; `catch
(e) {}`; a catch that returns a default without recording anything.

**Why it costs:** execution continues as though the operation succeeded. A loud
failure becomes silent data corruption, and the stack trace that would have
explained it is gone.

**Fix:** handle it (notify, report, retry, compensate) or let it propagate. If
the exception genuinely is ignorable, catch the *specific* type and comment why
that is safe.

**Reference:** `Ch.7: Don't Ignore Caught Errors`.
**Severity:** HIGH — always.

### 2. Logging as handling
**Look for:** `catch (e) { console.log(e) }`; a catch that logs and continues
with an object in an invalid state.

**Why it costs:** a log line nobody reads is not handling. The caller believes
the operation succeeded.

**Fix:** log *and* propagate, or log and take a real recovery action. Make sure
the caller learns the truth.

**Reference:** `Ch.7: Don't Ignore Caught Errors`.
**Severity:** MEDIUM, HIGH when execution continues in a broken state.

### 3. Returning null
**Look for:** `return null` on a not-found or failure path; methods whose
contract is "returns X or null" without saying so; null returned from something
callers will chain onto.

**Why it costs:** every caller must remember a check, and the one that forgets
fails far from the cause.

**Fix:** return an empty collection, an Optional/Maybe/Result, a null object, or
throw. Empty collections in particular remove the check entirely.

**Reference:** `Ch.7: Don't Return Null`.
**Severity:** MEDIUM, HIGH on a widely-called API.

### 4. Passing null
**Look for:** call sites passing literal `null` to select behavior; methods
defensively null-checking every parameter because callers might.

**Fix:** provide an overload or a separate function rather than a null argument.

**Reference:** `Ch.7: Don't Pass Null`.
**Severity:** MEDIUM.

### 5. Exceptions without context
**Look for:** `throw new Exception("error")`; a rethrow that drops the cause;
messages naming neither the operation nor the inputs.

**Why it costs:** the person debugging at 3am gets nothing.

**Fix:** state the operation, the relevant identifiers, and chain the original
cause.

**Reference:** `Ch.7: Provide Context with Exceptions`.
**Severity:** MEDIUM.

### 6. Error codes threaded through signatures
**Look for:** integer or enum status returns checked by every caller; an `errno`
convention in a language with exceptions; `if (result == -1)` chains.

**Fix:** throw instead, so the normal path reads normally. **Language check
first:** in Go and Rust this is the idiom, not a violation.

**Reference:** `Ch.7: Use Exceptions Rather Than Return Codes`.
**Severity:** MEDIUM where it is not idiomatic, otherwise no finding.

### 7. Error handling drowning the logic
**Look for:** a function whose body is mostly try/catch scaffolding; nested
try blocks; a duplicated error branch at every level of a callback chain.

**Fix:** extract the try/catch into its own function so the happy path is a
single readable sequence, or use the special-case pattern so callers stop
branching.

**Reference:** `Ch.7: Define the Normal Flow`, `Ch.3: Extract Try/Catch Blocks`.
**Severity:** MEDIUM.

### 8. Over-broad catches
**Look for:** `catch (Exception)` or bare `except:` wrapping a large block;
catching a base type to handle one specific failure.

**Why it costs:** it captures programming errors and interrupts too, hiding
defects the developer needed to see.

**Fix:** catch the specific type at the narrowest scope that can handle it.

**Reference:** `G4: Overridden Safeties`.
**Severity:** MEDIUM.

## Do not flag

- **Go's `if err != nil` and Rust's `Result`/`?`.** These *are* the language's
  error handling. Treating them as error-code smell is wrong.
- **Top-level catch-all handlers.** A framework error boundary, a request
  middleware, or a `main` that catches everything to log and exit cleanly is
  correct design.
- **Deliberate, documented ignores.** `catch (FileNotFound) { /* first run,
  nothing to migrate */ }` is handled, not swallowed.
- **Nullable returns in languages with enforced null-safety.** Kotlin's `String?`
  and TypeScript's `string | null` under `strictNullChecks` are checked by the
  compiler — the risk the rule guards against does not exist.
- **Retry and circuit-breaker code** that catches to back off.
- **Test code asserting on exceptions.**
- **Panics in Go used for genuinely unrecoverable states**, or `unwrap()` in a
  test or an invariant that cannot fail.
