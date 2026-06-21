---
name: diagrams:mermaid
description: Produce a Mermaid diagram (flowchart, sequence, class, state, ER, gantt, pie, mindmap) inside a ```mermaid fenced code block for rendering in Markdown, docs, or the GitHub/GitLab viewer. Use when the user asks for a mermaid diagram, a flowchart/sequence/class/state/ER/gantt diagram, or a diagram to embed in Markdown.
disable-model-invocation: false
---

# Create Professional Mermaid Diagrams for Software Development

## Objective

Generate clean, maintainable Mermaid diagram code that renders professional software architecture
diagrams, flowcharts, sequence diagrams, and more. Diagrams should be version-controllable, easy
to update, and clearly communicate system design.

---

## ⚠️ Critical Requirements

1. **Start with diagram type declaration** on the first line (e.g., `flowchart TD`, `sequenceDiagram`, `classDiagram`).
2. **Use `%%` for comments** to explain complex sections.
3. **Use self-explanatory identifiers** (not `A`, `B`, `C`) for nodes.
4. **Keep diagrams focused**: one concept per diagram; split large diagrams.
5. **Maximum complexity**: ~15-20 nodes before splitting into multiple diagrams.
6. **Store as `.mmd` files** alongside code for version control.

---

## Diagram Type Selection Guide

| Use Case | Diagram Type | Direction |
|----------|--------------|-----------|
| System architecture, component relationships | `flowchart` | `TD` (top-down) or `LR` (left-right) |
| API interactions, message flows | `sequenceDiagram` | Automatic (time-based) |
| Domain models, OOP design | `classDiagram` | Automatic |
| Database schemas | `erDiagram` | Automatic |
| State machines, lifecycle | `stateDiagram` | Automatic |
| Project timelines | `gantt` | Automatic |

---

## Step-by-Step Instructions

### Step 1: Define Diagram Purpose

Choose one:
- [ ] System architecture (components + connections)
- [ ] API/request flow (sequence diagram)
- [ ] Data model (class/ER diagram)
- [ ] Process workflow (flowchart)
- [ ] State transitions (state diagram)

### Step 2: Choose Diagram Type & Direction

```mermaid
%% Flowchart directions:
flowchart TD    %% Top-down (most common)
flowchart LR    %% Left-right (good for processes)
flowchart BT    %% Bottom-top
flowchart RL    %% Right-left

%% Other diagrams auto-direction:
sequenceDiagram   %% Time-based (left to right)
classDiagram      %% Automatic hierarchy
erDiagram         %% Automatic relationships
```

### Step 3: Define All Nodes First (Best Practice)

**✅ DO** — Introduce nodes with descriptive identifiers:

```mermaid
flowchart TD
  WEBPORTAL[Web Portal]
  WEBEXPAPI[Web Portal Experience API]
  MOBILEAPP[Mobile App]
  MOBEXPAPI[Mobile App Experience API]
  MICROSERVICES[Microservices]
  DB[Database]

  %% Now define connections
  WEBPORTAL-->WEBEXPAPI
  MOBILEAPP-->MOBEXPAPI
```

**❌ DON'T** — Mix definition with connections:

```mermaid
flowchart TD
  WEBPORTAL[Web Portal]-->WEBEXPAPI[Web Portal Experience API]
  MOBILEAPP[Mobile App]-->MOBEXPAPI[Mobile App Experience API]
```

### Step 4: Use Self-Explanatory Identifiers

**✅ DO**:

```mermaid
flowchart TD
  AUTHSERVICE[Auth Service]-->DATABASE[(Database)]
  USERSERVICE[User Service]-->DATABASE[(Database)]
```

**❌ DON'T**:

```mermaid
flowchart TD
  A[Auth Service]-->B[(Database)]
  C[User Service]-->B[(Database)]
```

### Step 5: Define Connections with Labels

```mermaid
%% Basic connection
A --> B

%% With label (use pipes)
A -->|label text| B

%% Different arrow styles
A --> B      %% Solid arrow
A -.-> B     %% Dotted line
A ==> B      %% Thick arrow
A -.- B      %% Dotted without arrow

%% With text label
A -->|POST /login| B
A -->|200 OK| B
```

### Step 6: Use Node Shapes for Clarity

```mermaid
flowchart TD
  A[Hard text]        %% Rectangle (default)
  B(Round edge)       %% Rounded rectangle
  C([Stadium])        %% Stadium shape
  D{Decision}         %% Diamond (for decisions)
  E[(Database)]       %% Cylinder (database)
  F[/Input or Output/] %% Parallelogram
  Start([Start])      %% Circle (start/end)
```

### Step 7: Add Subgraphs for Logical Grouping

```mermaid
flowchart TD
  subgraph CLIENTS["Client Layer"]
    WEBPORTAL[Web Portal]
    MOBILEAPP[Mobile App]
  end

  subgraph BACKEND["Backend Layer"]
    subgraph API["API Gateway"]
      WEBEXPAPI[Web API]
      MOBEXPAPI[Mobile API]
    end

    MICROSERVICES[Microservices]
    DB[(Database)]
  end

  WEBPORTAL-->WEBEXPAPI
  MOBILEAPP-->MOBEXPAPI
  WEBEXPAPI-->MICROSERVICES
  MOBEXPAPI-->MICROSERVICES
  MICROSERVICES-->DB
```

### Step 8: Add Comments for Complex Flows

```mermaid
flowchart TD
  %% Mobile App authentication flow
  MOBILEAPP[Mobile App]-->AUTHAPI[Auth API]

  %% Auth API validates against Identity Provider
  AUTHAPI-->IDENTITYPROVIDER[Identity Provider]

  %% On success, return JWT token
  IDENTITYPROVIDER-->|JWT token| MOBILEAPP
```

### Step 9: Handle Shared Nodes Properly

**✅ DO** — Define shared node on its own line:

```mermaid
flowchart TD
  WEBPORTAL[Web Portal]-->MICROSERVICES[Microservices]
  MOBILEAPP[Mobile App]-->MICROSERVICES[Microservices]
  MICROSERVICES[Microservices]-->DB[(Database)]
```

**❌ DON'T** — Repeat shared node:

```mermaid
flowchart TD
  WEBPORTAL[Web Portal]-->MICROSERVICES[Microservices]-->DB[(Database)]
  MOBILEAPP[Mobile App]-->MICROSERVICES[Microservices]
```

---

## Diagram Type Syntax Guides

### A. Flowchart (System Architecture)

```mermaid
flowchart TD
  %% Define all nodes first
  CLIENT[Client Application]
  APIGATEWAY[API Gateway]
  AUTHSERVICE[Auth Service]
  USERSERVICE[User Service]
  DATABASE[(User Database)]
  CACHE[(Redis Cache)]

  %% Define connections with labels
  CLIENT -->|HTTPS Request| APIGATEWAY
  APIGATEWAY -->|Validate JWT| AUTHSERVICE
  APIGATEWAY -->|Get User| USERSERVICE

  %% Service dependencies
  USERSERVICE -->|Read| DATABASE
  USERSERVICE -->|Check| CACHE

  %% Horizontal alignment for clarity
  APIGATEWAY -->|Route| USERSERVICE
  USERSERVICE -->DATABASE
```

### B. Sequence Diagram (API Flow)

```mermaid
sequenceDiagram
  %% Define participants
  participant User
  participant Client as Client App
  participant API as API Gateway
  participant Auth as Auth Service
  participant DB as Database

  %% Message flow
  User->>Client: Enter credentials
  Client->>API: POST /login
  API->>Auth: Validate credentials
  Auth->>DB: Query user
  DB-->>Auth: Return user data

  %% Alt/else blocks for conditions
  alt Valid credentials
    Auth-->>API: 200 OK + JWT
    API-->>Client: 200 OK + token
    Client-->>User: Show dashboard
  else Invalid credentials
    Auth-->>API: 401 Unauthorized
    API-->>Client: 401 Error
    Client-->>User: Show error
  end
```

### C. Class Diagram (Domain Model)

```mermaid
classDiagram
  %% Define classes with attributes/methods
  class User {
    +string id
    +string email
    +string name
    +register()
    +login()
  }

  class Title {
    +string name
    +int releaseYear
    +play()
  }

  class Genre {
    +string name
    +getTopTitles()
  }

  class Review {
    +string content
    +datetime createdAt
    +submit()
  }

  %% Define relationships
  User --> Review : creates
  Title *-- Season : has
  Title *-- Review : has
  Title -- Genre : belongs to

  %% Relationship types
  %% *-- : Composition (strong ownership)
  %% --> : Association (weak relationship)
  %% -- : Aggregation
  %% <|-- : Inheritance
```

### D. Entity Relationship Diagram (Database Schema)

```mermaid
erDiagram
  %% Define entities with keys
  USER ||--o{ ORDER : places
  ORDER ||--|{ LINE_ITEM : contains
  PRODUCT ||--o{ LINE_ITEM : includes

  USER {
    int id PK
    string email UK
    string name
    datetime created_at
  }

  ORDER {
    int id PK
    int user_id FK
    decimal total
    datetime created_at
  }

  LINE_ITEM {
    int id PK
    int order_id FK
    int product_id FK
    int quantity
    decimal price
  }

  PRODUCT {
    int id PK
    string name
    decimal price
    int stock
  }

  %% Cardinality
  %% ||--o{ : One-to-many (optional)
  %% ||--|{ : One-to-many (mandatory)
  %% }o--o{ : Many-to-many
```

### E. State Diagram (State Machine)

```mermaid
stateDiagram-v2
  %% Define states
  [*] --> Idle

  Idle --> Loading: Start
  Loading --> Processing: Data ready
  Processing --> Complete: Success
  Processing --> Error: Failure

  Error --> Idle: Retry
  Complete --> [*]

  %% Nested states
  state Authentication {
    [*] --> Unauthenticated
    Unauthenticated --> Authenticating: Login
    Authenticating --> Authenticated: Success
    Authenticating --> Unauthenticated: Fail
  }

  %% Notes
  note right of Processing
    Validate input
    Update database
  end note
```

---

## Styling & Configuration

### Add Theme Configuration

```mermaid
---
config:
  theme: base
  themeVariables:
    primaryColor: "#ff6b6b"
    secondaryColor: "#4ecdc4"
    tertiaryColor: "#ffe66d"
  look: classic
---
flowchart TD
  A[Node A] --> B[Node B]
```

### Available Themes

- `default` — Standard blue/grey
- `forest` — Green tones
- `dark` — Dark mode
- `neutral` — Grey tones
- `base` — Customizable

### Style Specific Nodes

```mermaid
flowchart TD
  classDef success fill:#4ecdc4,stroke:#333,stroke-width:2px
  classDef error fill:#ff6b6b,stroke:#333,stroke-width:2px

  A[Success] --> B[Error]
  class A success
  class B error
```

---

## Quality Checklist

Before finalizing, verify:
- ✅ Diagram type declared on first line
- ✅ All nodes defined before connections
- ✅ Self-explanatory identifiers (not A, B, C)
- ✅ Comments (`%%`) explain complex sections
- ✅ Subgraphs used for logical grouping
- ✅ ~15-20 nodes max (split if larger)
- ✅ Labels on arrows describe actions
- ✅ Test renders in Mermaid Live Editor

---

## Common Pitfalls

| ❌ Wrong | ✅ Right |
|----------|----------|
| `A --> B` with unclear `A`, `B` | `AUTHSERVICE[Auth Service] --> DATABASE[(Database)]` |
| No comments | `%% Auth flow validates JWT token` |
| One giant diagram | Split into `architecture.mmd`, `api-flow.mmd`, `data-model.mmd` |
| Missing node definitions | Define all nodes first, then connections |
| Using `#` in comments | Use `%%` not `#` for comments |

---

## When to Create Mermaid Diagrams

**Always diagram when:**
- Starting new projects/features
- Documenting complex systems
- Explaining architecture decisions
- Designing database schemas
- Onboarding new team members

**Reserve for:**
- Non-obvious flows
- Multi-service interactions
- Failure modes worth documenting
- Complex data relationships

---

**Now create your Mermaid diagram following these instructions.** Start by choosing the right
diagram type, define all nodes with descriptive identifiers, then add connections with clear
labels. Use comments and subgraphs to improve readability.
