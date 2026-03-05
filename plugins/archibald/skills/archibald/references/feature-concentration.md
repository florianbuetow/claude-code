# Feature Concentration

## Definition

A single component realizes multiple architectural concerns or features that are
not closely related. The component has low cohesion — its elements serve unrelated
purposes that happen to be co-located.

## Distinction from God Component

A god component is *large*. Feature concentration is about *mixed concerns*. A
small component can exhibit feature concentration if it implements two unrelated
features. Conversely, a large component with a single well-defined concern (e.g.,
a comprehensive billing engine) is not feature-concentrated.

In practice, god components often exhibit feature concentration too, but the two
smells have different root causes and different remediation approaches.

## Why It Matters

When unrelated features share a component, changes to one feature risk breaking
another. This creates several problems: changes intended for feature A must be
tested against feature B; deployment of a fix to feature A forces redeployment
of feature B; developers working on feature A must understand (or at least avoid
breaking) feature B's code; and the component's public API conflates concerns
that different clients care about.

## Detection Heuristics

**Responsibility analysis:**
- Can the component's purpose be described with a single, specific sentence?
  If the description requires "and" to join unrelated concepts, feature
  concentration is likely.
- Does the component implement multiple distinct business capabilities?
- Do different stakeholders or teams care about different parts of the component?

**Dependency pattern analysis:**
- Different clients use non-overlapping subsets of the component's API.
- The component depends on libraries/services that serve unrelated domains
  (e.g., both payment processing and email sending).
- Internal classes within the component form separate clusters with few
  connections between them.

**Change pattern analysis (from VCS):**
- Changes cluster into groups that rarely overlap — different files within the
  component change for different business reasons.
- Different team members or different Jira/issue categories touch different parts
  of the component.

**Practical indicators:**
- Changes to one feature affect code implementing other features.
- The component has multiple unrelated configuration concerns.
- Cross-cutting concerns (logging, auth, caching) are mixed with feature logic.
- The component name is vague or compound (e.g., "OrderAndInventoryService").

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Feature distance | Completely unrelated features | Related but distinct features |
| Change interference | Changes to one feature break another | Features have separate code paths |
| Client overlap | No client uses all features | Most clients use most features |
| Coupling created | Features share internal state | Features are independent internally |

## Mitigation Strategies

### 1. Separate Features into Distinct Components
Extract each distinct feature into its own component with a clear boundary and
API. This is the most direct fix.

### 2. Apply Feature-Based Decomposition
Reorganize by business capability. Each capability gets its own component
containing everything it needs (API, logic, data access) as a vertical slice.

### 3. Use Plugin or Microservice Architecture
For features that are truly independent, extract them as separate deployable
units. This enforces the boundary at the infrastructure level.

### 4. Aspect-Oriented Approach for Cross-Cutting Concerns
If the concentration is caused by cross-cutting concerns (logging, auth,
metrics) mixed with feature logic, extract the cross-cutting concerns using
middleware, decorators, or aspect-oriented patterns.

## False Positives

- **Orchestration components**: A component whose job is to coordinate multiple
  features (e.g., an order fulfillment workflow that touches inventory, payment,
  and shipping) is not feature-concentrated — orchestration *is* its single
  responsibility.
- **Shared domain concepts**: Features that operate on the same domain entity
  may naturally live together. A `UserService` handling both profile and
  preferences is only feature-concentrated if those concerns are truly
  independent.
- **Small utility modules**: A `utils` module with a few related helper functions
  serving different features is pragmatic, not a smell, as long as it stays small.
