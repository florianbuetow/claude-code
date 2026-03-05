# Software Architecture Quality Metrics

Metrics provide quantitative assessment of architectural characteristics. They
enable objective comparison, trend tracking, and threshold-based quality gates.
No single metric tells the full story — use them in combination and always
interpret in context.

---

## Coupling Metrics

Coupling measures interdependence between components. **Goal**: Low coupling for
modularity, testability, and independent evolution.

### Types of Coupling (worst to best)

1. **Content coupling** — One module modifies another's internal data. Worst form.
2. **Common coupling** — Modules share global data (global variables, shared state).
3. **External coupling** — Dependencies on external formats/protocols.
4. **Control coupling** — One module controls another's flow (passing flags/modes).
5. **Stamp coupling** — Modules share complex data structures (passing entire objects
   when only a field is needed).
6. **Data coupling** — Modules share simple data parameters. Best form.

When assessing, identify which *type* of coupling exists, not just how much.
Content coupling between two components is far worse than data coupling between ten.

### Coupling Between Objects (CBO)

**Definition**: Number of other classes a given class is connected to (depends on
or is depended upon).

**Calculation**: `CBO(Class) = |Efferent| + |Afferent|`

**Thresholds (indicative):**

| CBO Value | Assessment |
|-----------|------------|
| 0–5 | Excellent — loosely coupled |
| 6–10 | Good — acceptable coupling |
| 11–20 | Moderate — monitor closely |
| 21+ | High — refactoring candidate |

**Impact of high CBO**: Maintenance difficulty (ripple effects), testing complexity
(many dependencies to mock), change risk (modifications affect many classes).

### Afferent and Efferent Coupling

**Afferent Coupling (Ca)**: Number of classes outside a package that depend on
classes inside the package. Measures incoming dependencies — how "popular" or
"depended-upon" the package is.

**Efferent Coupling (Ce)**: Number of classes inside a package that depend on
classes outside the package. Measures outgoing dependencies — how much the
package depends on others.

### Instability Metric

**Calculation**: `I = Ce / (Ca + Ce)`

| I Value | Character |
|---------|-----------|
| I = 0 | Maximally stable (only incoming dependencies) |
| I ≈ 0.5 | Balanced |
| I = 1 | Maximally unstable (only outgoing dependencies) |

**Application**: Stable packages (I ≈ 0) should contain abstract interfaces.
Unstable packages (I ≈ 1) should contain concrete implementations. Dependencies
should flow toward stability. See `unstable-dependency.md` for full analysis.

### Structural vs. Dynamic Coupling

**Structural coupling**: Detectable through static code analysis — imports,
inheritance, method calls, type references.

**Dynamic coupling**: Occurs at runtime — polymorphism, dependency injection,
dynamic binding, reflection, message passing.

**Insight**: Static analysis misses runtime patterns. Dynamic analysis reveals
actual execution dependencies and "hot spots" of interaction. For a complete
coupling picture, complement static analysis with runtime profiling or
distributed tracing data when available.

### Logical Coupling

**Definition**: Files or modules frequently changed together even without direct
structural dependency.

**Detection**: Analyze version control history. Files modified in the same commits
are logically coupled.

**Significance**: Indicates hidden dependencies or shared concerns. Often reveals
DRY violations — same knowledge in multiple locations.

**Mitigation**: Merge logically coupled modules to increase cohesion and make the
dependency explicit.

---

## Cohesion Metrics

Cohesion measures how closely elements within a module relate to each other.
**Goal**: High cohesion for maintainability and single responsibility.

### Lack of Cohesion of Methods (LCOM)

**Concept**: Measures the degree to which methods in a class share instance
variables. High LCOM indicates the class may have multiple responsibilities.

**Calculation (simplified)**:
```
LCOM = 1 - Average_Method_Similarity
```
Where method similarity is based on shared instance variable access.

**Thresholds (indicative):**

| LCOM Range | Assessment |
|------------|------------|
| 0–10% | Excellent cohesion |
| 10–30% | Good cohesion |
| 30–50% | Moderate cohesion |
| 50–75% | Low cohesion — refactor |
| 75–100% | Poor cohesion — urgent refactor |

**Action**: High LCOM (>50%) suggests splitting the class into multiple cohesive
classes, each with related methods and data.

### Cohesion Types (best to worst)

1. **Functional cohesion** — Elements contribute to a single well-defined task.
   **Best.** Example: a `TemperatureConverter` class.
2. **Sequential cohesion** — Output of one element is input to the next.
   Example: a data processing pipeline.
3. **Communicational cohesion** — Elements operate on the same data.
   Example: functions that all read/write the same database record.
4. **Procedural cohesion** — Elements execute in a specific sequence.
   Example: initialization steps that must happen in order.
5. **Temporal cohesion** — Elements are executed at the same time.
   Example: startup or shutdown routines.
6. **Logical cohesion** — Elements perform similar operations but are unrelated.
   Example: a utility class with `parseDate()`, `parseInt()`, `parseJson()`.
7. **Coincidental cohesion** — No meaningful relationship. **Worst.**
   Example: a `Misc` or `Helpers` class with unrelated functions.

**Goal**: Functional cohesion for all modules. Sequential and communicational
cohesion are acceptable. Anything below procedural cohesion indicates a
component that should be split.

---

## Complexity Metrics

### Cyclomatic Complexity (CC)

**Definition**: Number of linearly independent paths through code.

**Simplified calculation**: `CC = decision points + 1`

Decision points: `if`, `else if`, `case`, `while`, `for`, `&&`, `||`, `catch`,
ternary operators.

**Thresholds:**

| CC Value | Risk Level |
|----------|------------|
| 1–10 | Low risk, simple |
| 11–20 | Moderate risk, medium complexity |
| 21–50 | High risk, complex |
| 50+ | Very high risk, untestable |

**Interpretation**: CC represents the minimum number of test cases needed for
full branch coverage. A method with CC = 25 needs at least 25 tests for
complete coverage, which is a strong signal to decompose it.

### Lines of Code (LOC)

**Simple but effective metric**: Modules with high LOC are potentially complex and
may violate Single Responsibility Principle.

**Usage**: Identify outliers. Modules with LOC 2–3× above the median warrant
investigation. LOC alone doesn't capture complexity nuances — use alongside
other metrics.

### Code Shape / Nesting Depth

**Concept**: Indentation patterns reveal nesting depth and complexity.

**Detection**: Deeply nested code (>4 levels) indicates high complexity and
potential for refactoring.

**Interpretation**: Wide, shallow code (many sequential statements) is generally
easier to understand than narrow, deep code (many nested conditionals or loops).

---

## Using Metrics in Assessment

### Metric Triangulation

No single metric is definitive. Use triangulation:
- High CBO + High LCOM → A class that is both highly coupled and incohesive.
  Strong refactoring candidate.
- High Ca + Low I → A stable, heavily-depended-upon component. Should be
  abstract. If concrete, it's a risk.
- High CC + High LOC → A complex, large method. Almost certainly needs
  decomposition.
- High Ce + Low LCOM → A component with many dependencies but high cohesion.
  May be an appropriate orchestrator/coordinator.

### Threshold Calibration

The thresholds in this document are general guidelines. Calibrate them to the
project:
- Compute the **median and standard deviation** for each metric across the
  codebase.
- Flag components that are **>2 standard deviations** above the median.
- Use absolute thresholds as a secondary check for industry-standard limits.

### Trend Analysis

When historical data is available, trend matters more than snapshot:
- **Improving trend** (metrics moving toward thresholds): healthy direction,
  lower severity for current values.
- **Stable trend** (metrics holding steady): assess against thresholds normally.
- **Deteriorating trend** (metrics moving away from thresholds): higher severity,
  even if current values are within limits.
