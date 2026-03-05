# Architectural Antipatterns

Antipatterns are commonly recurring solutions that appear beneficial but create
more problems than they solve. Unlike smells (structural anomalies), antipatterns
represent flawed decision-making patterns — choosing the wrong approach for the
problem at hand.

---

## Generic Software Design Antipatterns

### Big Ball of Mud

**Description**: Software with poor or no discernible structure. The system lacks
clear component boundaries, modularity, or architectural organization.

**Causes**: Lack of architectural planning, incremental patches without
refactoring, schedule pressure prioritizing features over structure, high
developer turnover and knowledge loss.

**Symptoms**: Spaghetti code, high coupling, low cohesion, difficult to locate
functionality, unpredictable side effects from changes.

**Consequences**: Maintenance becomes prohibitively expensive. System evolution
slows dramatically. Eventually reaches a state where rewrite is the only viable
option.

**Detection**: No identifiable architectural style. Dependencies go in all
directions. No clear layering or component boundaries. New developers cannot
form a mental model of the system.

**Mitigation**: Establish architectural vision and enforce through code reviews.
Regular refactoring sessions. Automated architecture conformance checking.
Apply Strangler Fig pattern to gradually replace problematic areas.

---

### Abstraction Inversion

**Description**: Higher-level functionality reimplements capabilities already
available in lower-level components, but in less efficient or maintainable ways.

**Example**: Writing a custom HTTP client instead of using the well-tested one
provided by the platform. Building a custom ORM when the framework provides one.

**Detection**: Components that duplicate platform or library functionality.
Wrapper code that adds no value over the underlying capability. Custom solutions
to solved problems.

**Mitigation**: Leverage existing abstractions. Conduct design reviews to identify
unnecessary reinvention. Apply YAGNI to custom infrastructure.

---

### God Object

**Description**: An object that knows too much or does too much. Violates Single
Responsibility Principle at the object level.

**Architectural Impact**: Often indicates an architectural God Component smell at
a higher level. Multiple god objects in the same component confirm feature
concentration.

**Detection**: Classes with very high method count, very high field count, or
very high LOC. Classes that are injected or imported by many other classes.

**Mitigation**: Decompose into focused, cohesive objects. Apply object-oriented
design principles to distribute responsibilities.

---

### Inner Platform Effect

**Description**: System architecture attempts to replicate functionality of the
development platform or framework. Building a custom plugin system, configuration
language, or object model that duplicates platform capabilities.

**Causes**: Over-engineering, Not Invented Here syndrome, misunderstanding
platform capabilities.

**Detection**: Custom implementations of features the platform provides natively.
Internal DSLs that replicate programming language features. Configuration systems
that are effectively programming languages.

**Mitigation**: Use platform capabilities directly. Apply YAGNI.

---

### Interface Bloat

**Description**: Interface contains an excessive number of methods, many of which
clients don't need.

**Architectural Consequence**: Forces clients to depend on functionality they
don't use, increasing coupling and change risk.

**Detection**: Interfaces with many methods where typical implementations leave
some as no-ops or throw "not supported" exceptions. Clients that use only a
small subset of the interface.

**Mitigation**: Apply Interface Segregation Principle. Create multiple focused
interfaces instead of one bloated interface.

---

### Stovepipe System

**Description**: Isolated system that doesn't integrate with other systems,
creating information silos.

**Symptoms**: Duplicate data across systems, manual data transfer, inconsistent
information, lack of interoperability.

**Detection**: Same business data maintained independently in multiple systems.
Manual processes to synchronize data. No API or integration layer.

**Mitigation**: Implement integration patterns (APIs, message queues, event
streaming). Use shared databases with caution. Consider enterprise service bus
or microservices with proper integration.

---

## Object-Oriented Antipatterns

### Anemic Domain Model

**Description**: Domain objects contain data but little or no behavior. Business
logic resides in service layers instead of domain objects.

**Problem**: Violates the object-oriented principle of encapsulating data with
behavior. Often results from procedural thinking in OOP context.

**Detection**: Domain classes that are mostly getters/setters with no business
methods. Service classes that manipulate domain object fields directly.
Transaction scripts operating on data containers.

**Mitigation**: Move business logic into domain objects. Apply Domain-Driven
Design principles.

---

### Sequential Coupling

**Description**: Class methods must be called in a specific order for correct
operation, but this constraint is not enforced by the interface.

**Example**: Must call `connect()` before `query()`, but the interface allows
calling in any order, leading to runtime errors.

**Detection**: Methods that throw exceptions or produce wrong results if called
out of order. Comments or documentation specifying required call sequences.
Temporal coupling hidden in method contracts.

**Mitigation**: Use builder pattern, state pattern, or fluent interfaces that
enforce correct sequencing through the type system.

---

## Architectural-Scale Antipatterns

### Cargo Cult Programming

**Description**: Adopting processes, technologies, or patterns without understanding
why they work, expecting the same benefits as the role model.

**Example**: Implementing microservices because Netflix uses them, without
considering whether the problem warrants that complexity.

**Detection**: Architecture choices that don't match the problem's actual
requirements. Technologies adopted because they're trendy rather than appropriate.
Patterns applied without understanding their trade-offs.

**Mitigation**: Understand the problem first, then select appropriate solutions.
Question whether a pattern fits the specific context, team size, and scale.

---

### Technology-Driven Architecture

**Description**: Architecture designed around technology selection while treating
business domain as someone else's concern.

**Symptoms**: Architecture optimized for the technology stack rather than business
needs. Component boundaries aligned with technical layers rather than business
capabilities. Technology decisions made before requirements are understood.

**Detection**: Architecture diagrams organized by technology (database layer, cache
layer, queue layer) rather than by business domain. Business concepts split across
technical boundaries.

**Mitigation**: Start with business requirements and quality attributes. Let these
drive technology selection. Apply Domain-Driven Design for boundary identification.

---

### Golden Hammer

**Description**: Preference for specific frameworks, languages, or patterns
regardless of whether they solve the current problem.

**Example**: "Everything should be microservices" or "Always use NoSQL databases"
or "We use React for everything, including CLI tools."

**Detection**: Same architectural approach applied to very different problems.
Technology choices made before problem analysis. Resistance to evaluating
alternatives.

**Mitigation**: Maintain diverse technology knowledge. Evaluate solutions
objectively against requirements. Use Architecture Decision Records (ADRs) to
force explicit justification.

---

### Malignant Growth

**Description**: Uncontrolled or badly managed growth of software system leading
to unmaintainable, error-prone code.

**Causes**: No architectural governance, insufficient refactoring, feature addition
without structural consideration.

**Detection**: Steadily increasing build times, test times, and defect rates.
Growing number of architectural smells over time. Declining developer velocity
despite stable team size.

**Mitigation**: Establish architectural principles and review processes. Regular
architectural assessment and refactoring. Track architectural metrics over time.

---

### Over-Engineering / Under-Engineering

**Over-engineering**: Unnecessarily complex architecture. A simpler approach would
suffice for business requirements.

**Under-engineering**: Too few modules at runtime or build time, insufficient
modularization. The architecture cannot support the system's actual complexity.

**Balance**: Architecture complexity should match problem complexity. Apply
principle of simplicity while avoiding oversimplification. Start simple, add
complexity only when requirements demand it.

**Detection for over-engineering**: Abstractions that have only one implementation
and no foreseeable second. Multiple indirection layers that add no value. Complex
patterns (CQRS, event sourcing, saga) for simple CRUD operations.

**Detection for under-engineering**: Monolithic code with no internal boundaries.
Single deployment unit for a system with distinct bounded contexts. No separation
between concerns that change at different rates.

---

### Never Change a Running System

**Description**: Fear of touching existing system prevents necessary improvements
and technical debt repayment.

**Consequences**: Technical debt accumulates. System becomes increasingly fragile
and difficult to change. New features are built around existing problems rather
than fixing them.

**Detection**: Legacy code that no one dares modify. Workarounds accumulating
around known problems. "Don't touch that file" warnings in team culture.

**Mitigation**: Comprehensive test suites to enable safe refactoring. Incremental
improvement approach. Address fear through confidence-building practices
(pair programming, mob programming, feature flags).
