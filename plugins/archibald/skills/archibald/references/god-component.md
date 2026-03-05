# God Component

## Definition

A component that is excessively large in terms of lines of code, number of classes,
or number of distinct responsibilities. It has grown to encompass far more
functionality than a single cohesive component should, becoming a monolith within
the system.

## Why It Matters

God components undermine modularization. They are difficult to understand (high
cognitive load), difficult to test (many interdependent behaviors), and create
bottlenecks in parallel development (multiple developers editing the same component
leads to merge conflicts). They also tend to have high coupling with many other
components, amplifying the impact of any change.

## Detection Heuristics

**Size indicators (indicative thresholds):**

| Metric | Normal | Investigate | God Component |
|--------|--------|-------------|---------------|
| LOC per component | < 5,000 | 5,000–50,000 | > 50,000 |
| Classes per component | < 30 | 30–100 | > 100 |
| Public API surface | < 20 methods/endpoints | 20–50 | > 50 |

These thresholds vary significantly by project and domain. The key diagnostic is
whether a component is **2–3× larger than the median** component in the same system.

**Structural indicators:**
- Component encompasses too many responsibilities — changes for unrelated business
  reasons affect the same component.
- Difficult to describe what the component does in a single sentence.
- High coupling with many other components (high Ca and Ce).
- Long build and test times for the component.
- Frequent merge conflicts as multiple developers work in the same area.
- New team members struggle to understand the component's boundaries.

**Naming signals:**
- Components named "core", "common", "shared", "main", "app", "utils" that
  contain business logic (not just genuine utilities).
- Components whose name doesn't constrain what goes into them.

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Size ratio | 5×+ median component size | 2–3× median |
| Responsibility count | Many unrelated features | Related features, just large |
| Change frequency | Frequently modified | Stable, rarely changes |
| Team impact | Multiple teams contribute | Single team owns it |
| Coupling | High Ca and Ce | Low coupling despite size |

## Mitigation Strategies

### 1. Domain-Based Split
Separate by business domain or bounded context. Each domain gets its own component
with clear boundaries. This is the strongest decomposition approach when domain
boundaries are clear.

**Process**: Identify distinct business domains within the god component. Extract
each domain to its own component. Define interfaces between the new components
for any cross-domain communication.

### 2. Feature-Based Split
Create vertical slices per feature. Each feature (or closely related feature group)
becomes its own component containing all layers needed for that feature.

**When to use**: The god component implements multiple end-user features that
could operate independently.

### 3. Layer-Based Split
Separate presentation, business logic, and data access into distinct components.
This works when the god component mixes architectural layers.

**When to use**: The component contains UI code, domain logic, and database access
all intermingled.

### 4. Responsibility-Based Split
Apply Single Responsibility Principle at the component level. Identify each
distinct responsibility (a "reason to change") and extract it.

**Process**:
1. List all distinct responsibilities within the component.
2. Group tightly related responsibilities.
3. Extract each group to a new focused component.
4. Define clear interfaces between new components.
5. Update dependents to use the appropriate new component.

### Incremental Approach

For large god components, avoid big-bang decomposition. Instead:
1. Introduce a Façade that wraps the god component's API.
2. Redirect all external callers to use the Façade.
3. Extract one responsibility at a time behind the Façade.
4. Once extraction is complete, remove the Façade.

## False Positives

- **Intentionally large components**: Some components (e.g., a comprehensive domain
  model, a large generated API client) are legitimately large without being god
  components. The key question is whether the component has *one* cohesive
  responsibility or *many* unrelated ones.
- **Monorepo modules**: A directory containing many sub-packages may look like a
  god component but is actually well-decomposed internally. Examine internal
  structure before flagging.
- **Generated code**: Auto-generated code (protobuf, GraphQL, ORM models) can
  produce large files that aren't god components in the architectural sense.
