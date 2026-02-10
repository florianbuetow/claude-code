# Principle of Least Surprise (POLA)

> "A component of a system should behave in a way that most users will expect it to behave." — PL/I Bulletin, 1967

## Core Idea

Also known as the Principle of Least Astonishment, POLA centers on predictability. The "user" can be an end-user, a fellow programmer, or a future maintainer. Joshua Bloch applied it extensively in *Effective Java* and his influential talk "How to Design a Good API & Why it Matters."

At architecture scale, POLA violations are especially costly because they amplify across distributed boundaries and affect multiple teams. A team migrating a 180k-line Rails monolith suffered 30% data loss in production because `record.metadata = filtered_array` on an ActiveRecord CollectionProxy silently performed a database DELETE — four experienced developers missed it because no one expected an assignment operator to have destructive side effects.

Surprising behavior increases bugs, onboarding cost, and misuse. DevIQ connects POLA to code structure, API design, and error handling: make systems predictable to reduce cognitive load and prevent costly integration errors.

## Violation Patterns

### 1. Inconsistent API Semantics

**Heuristic:** APIs whose HTTP semantics are inconsistent or violate protocol expectations.

**Look for:**
- GET endpoints that perform destructive actions or modify state
- HTTP 200 returned on errors with `{"error": "Not found"}` in the body
- REST APIs using POST for everything instead of appropriate HTTP verbs
- JavaScript's `fetch()` resolving successfully on 404/500 (common source of bugs)
- Different status code conventions across endpoints in the same API

**Refactoring/Remedy:** Follow HTTP semantics correctly and consistently. Use 200 for retrieval, 201 Created for POST with Location header, 204 No Content for DELETE, 400/422 for validation errors. Adopt Microsoft REST API Guidelines, Google API Design Guide, or JSON:API specification and enforce uniformly across all service boundaries.

### 2. Naming and Convention Inconsistencies

**Heuristic:** Different naming conventions, patterns, or response formats across the same system.

**Look for:**
- camelCase in some endpoints, snake_case in others
- Different pagination patterns across the same API surface
- Inconsistent error response structures
- CreateUser, AddCustomer, RegisterAccount that all do slightly different things
- Different authentication mechanisms for different services

**Refactoring/Remedy:** Adopt and enforce a single style guide across all services. Standardize error response format with consistent fields. Use API linting tools (Spectral, Vacuum) to enforce naming conventions automatically in CI/CD pipelines.

### 3. Silent Side Effects and Destructive Operations

**Heuristic:** Operations that appear innocuous but trigger expensive or destructive side effects.

**Look for:**
- Assignment operators that delete data (the Rails CollectionProxy example)
- Methods that modify state despite having query-like names
- "Simple" reads that cause writes
- APIs that trigger cascading background jobs undocumented by callers
- Operations that do more than their name suggests

**Refactoring/Remedy:** Apply Command-Query Separation: methods either return a result or modify state, never both. Method names must accurately describe ALL behavior including side effects. If a method does more than its name suggests, rename or split it. Document side effects prominently.

### 4. Silent Breaking Changes

**Heuristic:** Behavior changes without a contract signal, causing client failures that are hard to diagnose.

**Look for:**
- API field removals or renames without deprecation warnings
- Recurrent integration bugs at boundaries after "minor" updates
- Same user intent behaving differently depending on which service path is hit
- No versioning strategy
- Schema modifications that silently break downstream clients

**Refactoring/Remedy:** Treat API versions as behavioral contracts. Additive changes (new fields with defaults) are safe; removals and renames are breaking and require version bumps. Use consumer-driven contract testing (Pact) to catch behavioral deviations before they reach production.

### 5. Tribal Knowledge Requirements

**Heuristic:** Using the system correctly requires undocumented knowledge only learned from experienced team members.

**Look for:**
- High levels of tribal knowledge required to use an API correctly
- Developers needing to learn undocumented quirks
- Surprising performance characteristics (a "list" endpoint that takes 30 seconds)
- Non-obvious preconditions or operation ordering requirements
- Log analysis showing spikes in client retries or 4xx errors from competent consumers

**Refactoring/Remedy:** Publish API specs (OpenAPI, AsyncAPI) and keep them current. Describe side effects, idempotency, and performance expectations explicitly. Perform DX reviews — treat internal developers as users of your APIs. Use convention over configuration to provide sensible defaults.

## System-Scale Notes

- Microsoft uses an "Azure REST API Stewardship Board" — dedicated architects who review API designs for consistency before implementation
- Consumer-driven testing (Pact) reveals surprising behavior from the consumer's perspective and prevents integration failures
- Developer experience (DX) testing: observe new developers' first attempts to use an API and track where they make incorrect assumptions
- Log analysis reveals POLA violations: spikes in client retries, clients calling endpoints in wrong order, unusual 4xx frequencies from competent consumers
- Convention over configuration (Rails, Spring Boot) reduces surprise by providing sensible defaults matching common use cases
- POLA and KISS reinforce each other: surprising complexity is often a symptom of unnecessary complexity
- At architecture level, inconsistent behavior across services for the "same" concept often stems from under-DRY patterns

## False Positives to Avoid

- A deliberately different API style for a different audience (e.g., public API vs. internal admin API) is not a POLA violation as long as each is internally consistent
- Documented breaking changes with proper versioning and migration guides are not violations — the surprise is managed and communicated
- Performance characteristics that are inherent to the operation (e.g., a report generation endpoint that takes time) are not POLA violations if documented
- An API that follows its platform's conventions even when those conventions seem odd is usually better than an API that breaks platform conventions to be "more intuitive"
