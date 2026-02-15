# GraphQL Detection Patterns

Patterns for detecting GraphQL-specific security vulnerabilities including
introspection, depth limits, complexity limits, batching, and authorization.

---

## 1. Introspection Enabled in Production

**Description**: GraphQL introspection allows clients to query the full schema
including all types, fields, arguments, and deprecations. In production, this
reveals the entire API surface to attackers, enabling targeted exploitation of
poorly secured fields and hidden queries/mutations.

**Search Heuristics**:
- Grep: `introspection:\s*(true|undefined)` or absence of `introspection:\s*false`
- Grep: `ApolloServer\(|new GraphQLServer|createServer` without introspection config
- Grep: `disable_introspection|NoIntrospection|IntrospectionRule` (safe pattern presence)
- Grep: `__schema|__type` in query logs or test files
- Glob: `**/server.*`, `**/app.*`, `**/graphql/**`, `**/config/**`

**Language Examples**:

JavaScript (Apollo Server) -- VULNERABLE:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  // introspection defaults to true -- no explicit disable
});
```

JavaScript (Apollo Server) -- FIXED:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV !== 'production',
});
```

Python (Ariadne) -- VULNERABLE:
```python
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL

schema = make_executable_schema(type_defs, query)
app = GraphQL(schema)  # Introspection enabled by default
```

Python (Ariadne) -- FIXED:
```python
from ariadne import make_executable_schema
from ariadne.asgi import GraphQL
from graphql import NoSchemaIntrospectionCustomRule

schema = make_executable_schema(type_defs, query)
app = GraphQL(schema, validation_rules=[NoSchemaIntrospectionCustomRule])
```

Java (Spring GraphQL) -- VULNERABLE:
```java
@Bean
public GraphQL graphQL(GraphQLSchema schema) {
    return GraphQL.newGraphQL(schema).build();  // Introspection on by default
}
```

Java (Spring GraphQL) -- FIXED:
```java
@Bean
public GraphQL graphQL(GraphQLSchema schema) {
    return GraphQL.newGraphQL(schema)
        .instrumentation(new NoIntrospectionGraphQLInstrumentation())
        .build();
}
```

Go (gqlgen) -- VULNERABLE:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
// Introspection enabled by default in gqlgen
```

Go (gqlgen) -- FIXED:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
if os.Getenv("ENV") == "production" {
    srv.AddTransport(transport.POST{})
    srv.Use(extension.FixedComplexityLimit(100))
    // Disable introspection
    srv.AroundOperations(func(ctx context.Context, next graphql.OperationHandler) graphql.ResponseHandler {
        if graphql.GetOperationContext(ctx).Operation.Name == "__schema" {
            return graphql.OneShot(graphql.ErrorResponse(ctx, "introspection disabled"))
        }
        return next(ctx)
    })
}
```

**Scanner Coverage**: graphql-cop introspection detection; semgrep
`javascript.apollo.security.introspection-enabled`

**False Positive Guidance**: Development and staging environments commonly
enable introspection for tooling (GraphiQL, Apollo Studio). Only flag when
the configuration applies to production. Check for environment-conditional
logic.

**Severity Assessment**:
- **high**: Introspection enabled in production on APIs with sensitive data
- **medium**: Introspection enabled in production on public-facing APIs
- **low**: Introspection not explicitly disabled but behind authentication

---

## 2. Missing Query Depth Limit

**Description**: Without a depth limit, attackers can craft deeply nested
queries that cause exponential resolver execution, leading to denial of
service. A single malicious query like `{ user { friends { friends { friends
{ ... } } } } }` can exhaust server resources.

**Search Heuristics**:
- Grep: `depthLimit|depth-limit|maxDepth|max_depth|QueryDepthLimiter`
- Grep: `validationRules|validation_rules` (check if depth rule is included)
- Grep: `graphql-depth-limit|@graphql-tools|DepthLimitRule`
- Glob: `**/server.*`, `**/graphql/**`, `**/middleware/**`, `**/plugins/**`

**Language Examples**:

JavaScript (Apollo + graphql-depth-limit) -- VULNERABLE:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  // No depth limit configured
});
```

JavaScript (Apollo + graphql-depth-limit) -- FIXED:
```javascript
const depthLimit = require('graphql-depth-limit');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(10)],
});
```

Python (Strawberry) -- VULNERABLE:
```python
import strawberry
from strawberry.fastapi import GraphQLRouter

schema = strawberry.Schema(query=Query)
router = GraphQLRouter(schema)  # No depth limit
```

Python (Strawberry) -- FIXED:
```python
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.extensions import QueryDepthLimiter

schema = strawberry.Schema(query=Query, extensions=[QueryDepthLimiter(max_depth=10)])
router = GraphQLRouter(schema)
```

Java (graphql-java) -- VULNERABLE:
```java
GraphQL graphQL = GraphQL.newGraphQL(schema)
    .build();  // No depth limiting instrumentation
```

Java (graphql-java) -- FIXED:
```java
GraphQL graphQL = GraphQL.newGraphQL(schema)
    .instrumentation(new MaxQueryDepthInstrumentation(10))
    .build();
```

Go (gqlgen) -- VULNERABLE:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
// No depth limit middleware
```

Go (gqlgen) -- FIXED:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
srv.Use(extension.FixedComplexityLimit(200))
// Or implement custom depth limiting middleware
```

**Scanner Coverage**: graphql-cop depth limit check; no semgrep rule
(detected through absence of depth limiting configuration)

**False Positive Guidance**: Simple schemas without recursive types (no
self-referencing relations) may not be vulnerable to depth attacks. Check
whether the schema has recursive types before flagging.

**Severity Assessment**:
- **high**: No depth limit on schemas with recursive types (users->friends->friends)
- **medium**: No depth limit on schemas with limited nesting potential
- **low**: Depth limit set but arguably too high (>20)

---

## 3. Missing Query Complexity Limit

**Description**: Even with depth limits, wide queries (many fields, list
fields, computed fields) can consume excessive resources. Complexity analysis
assigns a cost to each field and rejects queries exceeding a budget. Without
it, attackers can craft expensive queries within depth limits.

**Search Heuristics**:
- Grep: `complexity|costAnalysis|cost-analysis|QueryComplexity|complexityLimit`
- Grep: `fieldConfigEstimator|simpleEstimator|directiveEstimator`
- Grep: `@cost|@complexity` in schema definitions
- Glob: `**/server.*`, `**/graphql/**`, `**/schema.*`, `**/*.graphql`

**Language Examples**:

JavaScript -- VULNERABLE:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(10)],
  // Depth limited but no complexity limit
});
```

JavaScript -- FIXED:
```javascript
const { createComplexityLimitRule } = require('graphql-validation-complexity');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(10),
    createComplexityLimitRule(1000, {
      scalarCost: 1,
      objectCost: 2,
      listFactor: 10,
    }),
  ],
});
```

Python (Graphene) -- VULNERABLE:
```python
schema = graphene.Schema(query=Query, mutation=Mutation)
# No complexity analysis configured
```

Python (Graphene) -- FIXED:
```python
from graphene import Schema
from graphql_complexity import get_complexity, SimpleEstimator

schema = Schema(query=Query, mutation=Mutation)

def validate_complexity(query_string):
    complexity = get_complexity(query_string, schema, estimator=SimpleEstimator())
    if complexity > 1000:
        raise Exception("Query too complex")
```

Java -- VULNERABLE:
```java
GraphQL.newGraphQL(schema)
    .instrumentation(new MaxQueryDepthInstrumentation(10))
    .build();  // Depth limited but no complexity limit
```

Java -- FIXED:
```java
GraphQL.newGraphQL(schema)
    .instrumentation(new ChainedInstrumentation(
        new MaxQueryDepthInstrumentation(10),
        new MaxQueryComplexityInstrumentation(200)
    ))
    .build();
```

Go -- VULNERABLE:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
// No complexity limit
```

Go -- FIXED:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
srv.Use(extension.FixedComplexityLimit(200))
```

**Scanner Coverage**: No direct scanner rule. Detected through absence of
complexity limiting configuration.

**False Positive Guidance**: APIs with only simple scalar queries and no list
fields may not need complexity limiting. Internal-only GraphQL APIs behind
authentication and trusted clients may accept higher risk.

**Severity Assessment**:
- **high**: No complexity limit on public-facing APIs with list/computed fields
- **medium**: No complexity limit on authenticated APIs with expensive resolvers
- **low**: Complexity limit present but possibly too generous

---

## 4. Batching Abuse

**Description**: GraphQL supports sending arrays of queries in a single HTTP
request. Without limits, attackers can batch thousands of queries (e.g.,
login mutations with different passwords) to bypass per-request rate limiting
and brute-force authentication or enumerate data.

**Search Heuristics**:
- Grep: `batch|allowBatchedHttpRequests|batching` in server configuration
- Grep: `Array\.isArray\(req\.body\)` (manual batch handling)
- Grep: `maxBatchSize|batchLimit|batch_limit`
- Glob: `**/server.*`, `**/graphql/**`, `**/middleware/**`

**Language Examples**:

JavaScript (Apollo Server 4) -- VULNERABLE:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  allowBatchedHttpRequests: true,  // Unlimited batching enabled
});
```

JavaScript (Apollo Server 4) -- FIXED:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  allowBatchedHttpRequests: false,  // Disable batching entirely
  // Or limit batch size via middleware:
});

// If batching needed, limit batch size:
app.use('/graphql', (req, res, next) => {
  if (Array.isArray(req.body) && req.body.length > 5) {
    return res.status(400).json({ error: 'Batch size exceeds limit' });
  }
  next();
});
```

Python (Ariadne) -- VULNERABLE:
```python
app = GraphQL(schema)  # Ariadne supports batching by default
```

Python (Ariadne) -- FIXED:
```python
from ariadne.asgi import GraphQL

class LimitedGraphQL(GraphQL):
    async def extract_data_from_request(self, request):
        data = await super().extract_data_from_request(request)
        if isinstance(data, list) and len(data) > 5:
            raise ValueError("Batch size limit exceeded")
        return data

app = LimitedGraphQL(schema)
```

Java -- VULNERABLE:
```java
// Spring GraphQL allows batched queries by default
@Bean
public RouterFunction<ServerResponse> graphqlRouterFunction(GraphQlSource source) {
    return RouterFunctions.route(POST("/graphql"), new GraphQlHttpHandler(source));
}
```

Java -- FIXED:
```java
@Bean
public WebFilter graphqlBatchLimiter() {
    return (exchange, chain) -> {
        // Parse request body and reject if array length > 5
        return chain.filter(exchange);
    };
}
```

Go -- VULNERABLE:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
srv.AddTransport(transport.POST{})
// Default allows batching with no limit
```

Go -- FIXED:
```go
srv := handler.NewDefaultServer(generated.NewExecutableSchema(cfg))
srv.AddTransport(transport.POST{})
// Implement middleware to limit batch size
```

**Scanner Coverage**: graphql-cop batching detection

**False Positive Guidance**: Batching for legitimate use cases (loading related
data efficiently) is common. The risk is when batching enables brute-force
on authentication mutations or enumeration of sensitive data. Check what
mutations are available and whether rate limiting applies per-operation.

**Severity Assessment**:
- **high**: Unlimited batching with authentication mutations available
- **medium**: Batching enabled with moderate limits or no sensitive mutations
- **low**: Batching enabled on read-only APIs with rate limiting

---

## 5. Alias-Based Denial of Service

**Description**: GraphQL aliases allow the same field to be queried multiple
times with different names in a single query. An attacker can use hundreds of
aliases to multiply the cost of an expensive resolver, bypassing naive
depth/complexity limits that do not count aliases.

**Search Heuristics**:
- Grep: `alias|aliases` in validation or complexity configuration
- Grep: `MaxAliasesRule|aliasLimit|alias-limit|countAliases`
- Grep: `operationComplexity|fieldComplexity` (check if aliases are counted)
- Glob: `**/graphql/**`, `**/validation/**`, `**/plugins/**`

**Language Examples**:

GraphQL Query -- ATTACK:
```graphql
query AliasAttack {
  a1: expensiveField(id: "1")
  a2: expensiveField(id: "1")
  a3: expensiveField(id: "1")
  # ... repeated 1000 times
  a1000: expensiveField(id: "1")
}
```

JavaScript -- VULNERABLE:
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(10)],
  // Depth limit does not prevent alias abuse at depth 1
});
```

JavaScript -- FIXED:
```javascript
const { createComplexityLimitRule } = require('graphql-validation-complexity');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(10),
    createComplexityLimitRule(1000),  // Counts aliases toward complexity
    createAliasLimitRule(20),         // Hard limit on aliases per query
  ],
});

// Custom alias limit rule:
function createAliasLimitRule(max) {
  return (context) => ({
    Field(node) {
      if (node.alias) {
        context._aliasCount = (context._aliasCount || 0) + 1;
        if (context._aliasCount > max) {
          context.reportError(new GraphQLError(`Alias limit (${max}) exceeded`));
        }
      }
    },
  });
}
```

Python -- VULNERABLE:
```python
schema = strawberry.Schema(query=Query, extensions=[QueryDepthLimiter(max_depth=10)])
# Depth limit alone does not prevent alias attacks
```

Python -- FIXED:
```python
from graphql import DocumentNode

def validate_aliases(document: DocumentNode, max_aliases: int = 20):
    alias_count = sum(
        1 for defn in document.definitions
        for sel in getattr(defn, 'selection_set', None) or []
        if hasattr(sel, 'alias') and sel.alias
    )
    if alias_count > max_aliases:
        raise Exception(f"Too many aliases: {alias_count}")
```

**Scanner Coverage**: graphql-cop alias detection

**False Positive Guidance**: A small number of aliases (under 10) is normal
GraphQL usage for querying the same field with different arguments. Only flag
when there is no limit on alias count and expensive resolvers are present.

**Severity Assessment**:
- **high**: No alias limit with expensive resolvers (database queries, external API calls)
- **medium**: No alias limit with lightweight resolvers
- **low**: Alias limit present but generous (>50)

---

## 6. Missing Per-Field Authorization

**Description**: GraphQL resolvers for sensitive fields (email, phone, SSN,
balance, salary) do not check the requesting user's authorization. Any
authenticated user (or even unauthenticated users) can query these fields
by adding them to a query.

**Search Heuristics**:
- Grep: `@auth|@authorized|@hasRole|@guard|@permission` in schema definitions
- Grep: `ctx\.user|context\.user|req\.user` in resolvers (verify it's checked, not just accessed)
- Grep: `(email|phone|ssn|salary|balance|address)` in type definitions without auth directive
- Glob: `**/resolvers/**`, `**/schema.*`, `**/*.graphql`, `**/typeDefs*`

**Language Examples**:

JavaScript -- VULNERABLE:
```javascript
const resolvers = {
  User: {
    email: (parent) => parent.email,          // No auth check
    salary: (parent) => parent.salary,        // Sensitive field, no auth
    ssn: (parent) => parent.ssn,              // Highly sensitive, no auth
  },
};
```

JavaScript -- FIXED:
```javascript
const resolvers = {
  User: {
    email: (parent, args, context) => {
      if (context.user.id !== parent.id && !context.user.isAdmin) {
        throw new ForbiddenError('Not authorized');
      }
      return parent.email;
    },
    salary: (parent, args, context) => {
      if (!context.user.roles.includes('HR') && context.user.id !== parent.id) {
        throw new ForbiddenError('Not authorized');
      }
      return parent.salary;
    },
  },
};
```

Python (Strawberry) -- VULNERABLE:
```python
@strawberry.type
class User:
    name: str
    email: str          # Exposed to any query
    salary: float       # Sensitive, no permission check
```

Python (Strawberry) -- FIXED:
```python
@strawberry.type
class User:
    name: str

    @strawberry.field
    def email(self, info: strawberry.types.Info) -> str:
        if info.context.user.id != self.id and not info.context.user.is_admin:
            raise PermissionError("Not authorized")
        return self._email

    @strawberry.field(permission_classes=[IsHROrOwner])
    def salary(self) -> float:
        return self._salary
```

Java (Spring GraphQL) -- VULNERABLE:
```java
@SchemaMapping(typeName = "User")
public String email(User user) {
    return user.getEmail();  // No authorization check
}
```

Java (Spring GraphQL) -- FIXED:
```java
@SchemaMapping(typeName = "User")
@PreAuthorize("@authService.canViewField(#user, authentication, 'email')")
public String email(User user) {
    return user.getEmail();
}
```

Go -- VULNERABLE:
```go
func (r *userResolver) Email(ctx context.Context, obj *model.User) (string, error) {
    return obj.Email, nil  // No auth check
}
```

Go -- FIXED:
```go
func (r *userResolver) Email(ctx context.Context, obj *model.User) (string, error) {
    user := auth.UserFromContext(ctx)
    if user.ID != obj.ID && !user.IsAdmin {
        return "", fmt.Errorf("not authorized")
    }
    return obj.Email, nil
}
```

**Scanner Coverage**: semgrep `javascript.graphql.security.missing-auth-resolver`

**False Positive Guidance**: Public profile fields (name, avatar, bio) do not
need per-field auth. Fields on types that are always fetched through an
authorization-gated parent resolver may inherit authorization. Verify the
query path to the field before flagging.

**Severity Assessment**:
- **critical**: PII fields (SSN, financial data) without authorization
- **high**: Contact information (email, phone) exposed without ownership check
- **medium**: Non-sensitive but private fields without authorization
- **low**: Fields with indirect access control via parent resolver
