# Ambiguous Interface

## Definition

A component offers only a single, general entry point rather than well-defined,
specific interfaces. Clients interact through generic method signatures with
weak typing, requiring knowledge of internal command structures or magic
constants to use the component correctly.

## Canonical Example

Instead of well-defined methods:
```
createUser(User user)
deleteUser(int id)
updateUserEmail(int id, String email)
```

The component exposes a single generic entry point:
```
execute(String command, Object[] params)
```

Clients must know that the command string is "CREATE_USER", the first param is
a User object, and so on. This knowledge is undocumented, fragile, and
error-prone.

## Why It Matters

Ambiguous interfaces reduce usability, increase coupling (clients must know
internal command structures), and make API evolution difficult. They defeat
the purpose of having an interface at all — the interface should communicate
what operations are available and what inputs they require. When the interface
is a generic passthrough, the real contract is hidden behind stringly-typed
conventions.

## Detection Heuristics

**Signature analysis:**
- Methods accepting `Object`, `Any`, `interface{}`, `Map<String, Object>`,
  or similar generic types as primary parameters.
- Method names like `execute`, `process`, `handle`, `doAction` that don't
  describe what they do.
- Single-method interfaces that dispatch internally based on a command/type
  parameter.

**Usage pattern analysis:**
- Callers pass magic strings or constants to select behavior.
- Callers must cast or extract results from generic containers.
- Complex conditional logic inside general-purpose methods dispatching to
  different behaviors based on input values.
- Documentation or comments explaining "pass X for behavior Y, pass Z for
  behavior W".

**API surface indicators:**
- Component has very few public methods relative to the number of distinct
  operations it supports.
- External clients duplicate dispatch logic because the interface doesn't
  expose operations directly.
- Difficult for clients to discover available functionality without reading
  implementation source code.

## Severity Assessment

| Factor | Higher Severity | Lower Severity |
|--------|----------------|----------------|
| Client count | Many clients use the ambiguous interface | Single internal client |
| Operation count | Many operations hidden behind generic API | Two or three operations |
| Type safety | No compile-time checking of params | Some type safety preserved |
| Documentation | Undocumented command structure | Well-documented conventions |
| Error handling | Silent failures on wrong params | Clear error messages |

## Mitigation Strategies

### 1. Apply Interface Segregation Principle (ISP)
Replace the single generic interface with multiple specific interfaces, one
per client group or concern. Each interface exposes only the operations
relevant to its clients.

### 2. Define Specific, Strongly-Typed Methods
Replace the generic entry point with individual methods for each operation.
Each method has a descriptive name, specific parameter types, and a specific
return type. The compiler can then enforce correct usage.

### 3. Create Role-Based Interfaces
Design different interfaces for different client types. An admin client sees
admin operations; a read-only client sees query operations. This reduces
the surface area each client must understand.

### 4. Use Facade Pattern
If the component legitimately handles many operations (e.g., it's an
orchestrator), introduce a Facade with multiple clear entry points. The
Facade delegates to the internal implementation but provides a discoverable,
well-typed API.

### 5. Command Pattern (if dispatch is needed)
If the generic dispatch is architecturally necessary (e.g., a message bus
or command handler), use a typed Command pattern where each command is a
specific class/type with its own validation, rather than stringly-typed
dispatch.

## False Positives

- **Intentional generic dispatch**: Message brokers, event buses, and plugin
  systems legitimately use generic interfaces because they must handle
  arbitrary message types. The key question is whether the genericness serves
  an architectural purpose (extensibility) or is just laziness.
- **Serialization boundaries**: APIs that accept JSON or serialized data are
  generic by nature. The ambiguity concern applies to the *programmatic*
  interface, not the wire format. A well-typed SDK over a JSON API is fine.
- **Internal implementation detail**: A generic internal dispatch method used
  only within a component (not exposed to clients) is an implementation
  choice, not an architectural smell.
