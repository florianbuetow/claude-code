# Scattered Functionality

## Definition

Multiple components are responsible for realizing the same high-level concern or
feature. The same logic is duplicated or fragmented across components rather than
consolidated in one authoritative location.

This is the inverse of Feature Concentration. Instead of one component doing too
much, multiple components duplicate the same concern.

## Why It Matters

Scattered functionality violates DRY (Don't Repeat Yourself) at the architecture
level. When business logic for a single concern exists in multiple places, feature
changes require coordinating modifications across all those components. This creates
several risks: inconsistent behavior when one copy is updated but others are
missed; higher maintenance cost from finding and modifying all instances; divergence
over time as copies evolve independently; and difficulty understanding the
authoritative implementation of a concern.

## Detection Heuristics

**Code duplication analysis:**
- Similar logic, data structures, or algorithms appearing in multiple components.
- Multiple implementations of the same business rule (e.g., discount calculation
  in both the order service and the invoice service).
- Same validation rules implemented independently in different components.

**Naming analysis:**
- Multiple components with overlapping names or responsibilities
  (e.g., `UserValidator` in three different packages).
- Same database table accessed and queried by multiple components with
  component-specific query logic.

**Change pattern analysis (from VCS):**
- Same logical change requires modifying multiple components simultaneously.
- Bug fixes that must be applied in multiple places.
- Files in different components that frequently change in the same commit
  (logical coupling indicating shared responsibility).

**Practical indicators:**
- Same feature logic duplicated across components.
- Inconsistent implementation of common functionality.
- Difficult to modify a feature because it requires changes in multiple places.
- Team members disagree about which component is the "source of truth" for
  a concern.
- Schema or data format definitions exist in multiple places.

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Duplication scope | Same logic in many components | Two components share logic |
| Divergence risk | Copies have already diverged | Copies are still identical |
| Change frequency | Frequently modified concern | Stable, rarely changes |
| Consistency requirement | Business-critical logic (billing, auth) | Convenience logic (formatting) |
| Discovery difficulty | Scattered copies are hard to find | Copies are well-known |

## Mitigation Strategies

### 1. Consolidate into Single Component
Create a single authoritative component for the concern. All other components
delegate to it rather than implementing their own version.

### 2. Create Shared Library or Service
Extract the common logic into a shared library (for in-process use) or a shared
service (for cross-process use). All components that need the logic depend on
this single implementation.

**Caution**: Shared libraries create coupling between all consumers. If the
concern evolves differently per consumer, a shared library may be worse than
controlled duplication. Apply the Rule of Three — only consolidate when you've
seen the same logic in three or more places.

### 3. Apply Extract Component Refactoring
Identify all instances of the scattered logic, design a clean consolidated
interface, migrate consumers one at a time, and retire the duplicated
implementations.

### 4. Use Architectural Patterns
- **Event-driven architecture**: Instead of each component implementing its own
  version, publish events and let a single handler implement the concern.
- **Middleware/interceptor pattern**: For cross-cutting concerns (auth, logging,
  validation), centralize in middleware rather than scattering across handlers.
- **Layered architecture**: Ensure concerns live at the appropriate layer and
  higher layers delegate rather than reimplement.

## False Positives

- **Intentional duplication across service boundaries**: In microservices, some
  duplication is deliberate to maintain service independence. Duplicating a data
  transfer object (DTO) across services is often preferable to creating a shared
  library that couples them. This is a conscious trade-off between DRY and
  loose coupling.
- **Interface adapters**: Multiple components may implement the same interface
  differently because they adapt to different external systems. This isn't
  scattered functionality — it's the Strategy or Adapter pattern.
- **Test code**: Test utilities and helpers may appear duplicated across test
  suites. This is usually acceptable unless the test infrastructure is complex
  enough to warrant its own shared module.
