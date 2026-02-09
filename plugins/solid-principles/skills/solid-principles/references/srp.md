# Single Responsibility Principle (SRP)

> "A class should have one, and only one, reason to change."
> — Robert C. Martin

## Core Idea

SRP is about **cohesion**: every module, class, or function should be responsible
to exactly one actor (stakeholder). If two different actors depend on the same class
for different reasons, changes for one actor risk breaking the other.

This is NOT simply "a class should do one thing." A class can have multiple methods
and still satisfy SRP if they all serve the same actor and change for the same reason.

## Violation Patterns

### 1. God Class / Blob Class
**Heuristic**: Class exceeds ~200 lines, has 10+ public methods, or touches 3+
unrelated domains (e.g., database access + email sending + PDF generation).

**Look for**:
- Methods that could be grouped into separate, named clusters.
- Instance variables that are only used by a subset of methods.
- Imports at the top that span unrelated domains (e.g., `import smtplib` alongside
  `import sqlalchemy` alongside `import matplotlib`).

**Refactoring**: Extract cohesive method groups into separate classes. The original
class can delegate or coordinate.

### 2. Mixed Abstraction Levels
**Heuristic**: A single class handles both high-level policy/orchestration AND
low-level detail (e.g., a `ReportService` that both decides *what* to report and
*how* to format HTML).

**Look for**:
- Methods mixing business logic with I/O, serialization, or formatting.
- A class that would need to change if either the business rules OR the
  infrastructure changes.

**Refactoring**: Separate policy from mechanism. Create a high-level class for
business rules and a low-level class for the technical details.

### 3. Feature Envy
**Heuristic**: A method in class A spends most of its body accessing data from
class B.

**Look for**:
- Long chains like `self.order.customer.address.city`.
- Methods that take another object as a parameter and then call 5+ methods on it.

**Refactoring**: Move the method to the class whose data it primarily uses.

### 4. Data Class Serving Multiple Masters
**Heuristic**: A data/model class has methods added for different consumers
(e.g., `to_api_response()`, `to_csv_row()`, `to_admin_view()`).

**Look for**:
- Serialization methods for different formats or consumers on the same class.
- Presentation logic mixed with domain logic.

**Refactoring**: Use separate serializer/presenter classes per consumer.

### 5. Utility Dumping Ground
**Heuristic**: A `Utils`, `Helpers`, or `Common` class/module that accumulates
unrelated functions over time.

**Look for**:
- Functions in the same module with zero shared state or concept.
- The file grows with every feature because "it didn't fit anywhere else."

**Refactoring**: Group related utilities into purpose-named modules
(e.g., `string_utils`, `date_utils`, `validation`).

## Language-Specific Notes

- **Python**: Modules themselves can be a unit of responsibility. A module with
  related top-level functions is fine — SRP violations happen when unrelated
  concerns are lumped together.
- **Java/C#**: Classes are the natural unit. Watch for `Service` classes that
  accumulate unrelated methods.
- **TypeScript**: Both modules and classes apply. Watch for barrel files that
  re-export unrelated functionality.
- **Go**: Packages are the unit of responsibility. A package with a clear name
  and focused purpose satisfies SRP.

## False Positives to Avoid

- A class with many methods that all operate on the same cohesive data structure
  (e.g., a `Matrix` class with `add`, `multiply`, `transpose`, `determinant`).
- A facade or coordinator class that delegates to focused collaborators — the
  coordination itself is the single responsibility.
- DTOs/value objects with multiple fields — having many fields isn't a violation.
