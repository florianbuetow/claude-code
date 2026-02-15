# API Security Detection Patterns

Patterns for detecting API-specific security vulnerabilities aligned with the
OWASP API Security Top 10 (2023).

---

## 1. Broken Object-Level Authorization (BOLA)

**Description**: API endpoints accept a resource ID from the client and return
or modify data without verifying the requesting user owns or has authorization
to access that resource. This is the most prevalent API vulnerability -- the
equivalent of IDOR for APIs.

**Search Heuristics**:
- Grep: `params\.id|params\.userId|params\.orderId|params\[['"]id['"]\]`
- Grep: `findById\(.*req\.|findOne\(.*req\.|get\(.*req\.params` without ownership filter
- Grep: `WHERE id = .*req\.|WHERE id = .*params` without `AND (user_id|owner)`
- Grep: `@PathVariable|@PathParam|path\(['"]<.*id>` in controller methods
- Glob: `**/controllers/**`, `**/handlers/**`, `**/api/**`, `**/routes/**`

**Language Examples**:

Python (Django REST) -- VULNERABLE:
```python
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()  # Returns any order by ID
    serializer_class = OrderSerializer
```

Python (Django REST) -- FIXED:
```python
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)  # Scoped to user
```

JavaScript (Express) -- VULNERABLE:
```javascript
router.get('/api/orders/:id', authenticate, async (req, res) => {
  const order = await Order.findById(req.params.id);  // Any user's order
  res.json(order);
});
```

JavaScript (Express) -- FIXED:
```javascript
router.get('/api/orders/:id', authenticate, async (req, res) => {
  const order = await Order.findOne({ _id: req.params.id, userId: req.user.id });
  if (!order) return res.status(404).json({ error: 'Not found' });
  res.json(order);
});
```

Java (Spring) -- VULNERABLE:
```java
@GetMapping("/api/orders/{id}")
public Order getOrder(@PathVariable Long id) {
    return orderRepository.findById(id).orElseThrow();
}
```

Java (Spring) -- FIXED:
```java
@GetMapping("/api/orders/{id}")
public Order getOrder(@PathVariable Long id, @AuthenticationPrincipal User user) {
    return orderRepository.findByIdAndUserId(id, user.getId())
        .orElseThrow(() -> new NotFoundException("Order not found"));
}
```

Go -- VULNERABLE:
```go
func GetOrder(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    var order Order
    db.First(&order, id)  // No ownership check
    json.NewEncoder(w).Encode(order)
}
```

Go -- FIXED:
```go
func GetOrder(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    userID := auth.UserFromContext(r.Context()).ID
    var order Order
    if err := db.Where("id = ? AND user_id = ?", id, userID).First(&order).Error; err != nil {
        http.Error(w, "Not found", http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(order)
}
```

**Scanner Coverage**: semgrep `generic.api.security.bola-direct-object-reference`

**False Positive Guidance**: Admin endpoints that intentionally access any
resource are not BOLA. Public resources (product listings, blog posts) accessed
by ID without auth are not BOLA unless they contain private data. Check whether
the resource type is user-scoped.

**Severity Assessment**:
- **critical**: BOLA on financial, medical, or PII resources
- **high**: BOLA on user-scoped data (orders, messages, documents)
- **medium**: BOLA on less sensitive user-scoped data

---

## 2. Mass Assignment

**Description**: The API binds request body fields directly to model attributes
without an explicit allowlist. Attackers can include extra fields (like `role`,
`isAdmin`, `price`) to modify attributes they should not control.

**Search Heuristics**:
- Grep: `Object\.assign\(.*req\.body|\.update\(req\.body\)|\.create\(req\.body\)`
- Grep: `\*\*request\.data|\*\*request\.POST|Model\(.*\*\*data\)` (Python kwargs)
- Grep: `@RequestBody.*Entity|@RequestBody.*Model` without DTO (Java)
- Grep: `fill\(.*request\(\)|update\(.*request\.all\(\)\)` (Laravel)
- Glob: `**/controllers/**`, `**/handlers/**`, `**/routes/**`

**Language Examples**:

Python (Django) -- VULNERABLE:
```python
@api_view(['PATCH'])
def update_user(request, user_id):
    user = User.objects.get(id=user_id)
    for key, value in request.data.items():
        setattr(user, key, value)  # Attacker can set is_admin=True
    user.save()
```

Python (Django) -- FIXED:
```python
@api_view(['PATCH'])
def update_user(request, user_id):
    user = User.objects.get(id=user_id, id=request.user.id)
    ALLOWED_FIELDS = {'name', 'email', 'bio'}
    for key, value in request.data.items():
        if key in ALLOWED_FIELDS:
            setattr(user, key, value)
    user.save()
```

JavaScript (Express + Mongoose) -- VULNERABLE:
```javascript
router.put('/api/users/:id', authenticate, async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
  // req.body = { name: "Alice", role: "admin" } -- role is set!
  res.json(user);
});
```

JavaScript (Express + Mongoose) -- FIXED:
```javascript
router.put('/api/users/:id', authenticate, async (req, res) => {
  const { name, email, bio } = req.body;  // Explicit allowlist
  const user = await User.findByIdAndUpdate(
    req.params.id, { name, email, bio }, { new: true }
  );
  res.json(user);
});
```

Java (Spring) -- VULNERABLE:
```java
@PutMapping("/api/users/{id}")
public User updateUser(@PathVariable Long id, @RequestBody User user) {
    // Binds directly to entity -- attacker can set role, permissions
    user.setId(id);
    return userRepository.save(user);
}
```

Java (Spring) -- FIXED:
```java
@PutMapping("/api/users/{id}")
public User updateUser(@PathVariable Long id, @RequestBody @Valid UpdateUserDTO dto) {
    User user = userRepository.findById(id).orElseThrow();
    user.setName(dto.getName());
    user.setEmail(dto.getEmail());
    return userRepository.save(user);
}
```

Go -- VULNERABLE:
```go
func UpdateUser(w http.ResponseWriter, r *http.Request) {
    var updates map[string]interface{}
    json.NewDecoder(r.Body).Decode(&updates)
    db.Model(&User{}).Where("id = ?", userID).Updates(updates)  // Any field
}
```

Go -- FIXED:
```go
type UpdateUserRequest struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

func UpdateUser(w http.ResponseWriter, r *http.Request) {
    var req UpdateUserRequest
    json.NewDecoder(r.Body).Decode(&req)
    db.Model(&User{}).Where("id = ?", userID).Updates(User{Name: req.Name, Email: req.Email})
}
```

**Scanner Coverage**: semgrep `generic.api.security.mass-assignment`;
brakeman `MassAssignment`

**False Positive Guidance**: Admin endpoints that intentionally allow setting
any field are not mass assignment. DTO/serializer patterns with explicit field
lists are the fix -- verify the allowlist does not include sensitive fields.

**Severity Assessment**:
- **critical**: Mass assignment allowing role/privilege escalation
- **high**: Mass assignment on price, status, or security-relevant fields
- **medium**: Mass assignment on non-critical fields (potential data integrity issue)

---

## 3. Missing Rate Limiting

**Description**: API endpoints lack rate limiting, allowing attackers to
perform brute-force attacks on authentication, enumerate valid accounts,
scrape large datasets, or cause denial of service through high request volume.

**Search Heuristics**:
- Grep: `rateLimit|rate-limit|throttle|RateLimiter|limiter` in middleware
- Grep: `express-rate-limit|django-ratelimit|@RateLimiter|golang.org/x/time/rate`
- Grep: `/login|/auth|/token|/verify|/reset` routes without rate limit middleware
- Glob: `**/middleware/**`, `**/config/**`, `**/routes/**`, `**/app.*`

**Language Examples**:

JavaScript (Express) -- VULNERABLE:
```javascript
router.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  // No rate limiting -- brute-force possible
  const user = await authenticate(email, password);
  res.json({ token: generateToken(user) });
});
```

JavaScript (Express) -- FIXED:
```javascript
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { error: 'Too many login attempts' },
});

router.post('/api/auth/login', loginLimiter, async (req, res) => {
  const { email, password } = req.body;
  const user = await authenticate(email, password);
  res.json({ token: generateToken(user) });
});
```

Python (Django) -- VULNERABLE:
```python
@api_view(['POST'])
def login(request):
    # No rate limiting
    user = authenticate(request.data['email'], request.data['password'])
    return Response({'token': generate_token(user)})
```

Python (Django) -- FIXED:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/15m', method='POST', block=True)
@api_view(['POST'])
def login(request):
    user = authenticate(request.data['email'], request.data['password'])
    return Response({'token': generate_token(user)})
```

Java (Spring) -- VULNERABLE:
```java
@PostMapping("/api/auth/login")
public TokenResponse login(@RequestBody LoginRequest request) {
    // No rate limiting
    return authService.authenticate(request);
}
```

Java (Spring) -- FIXED:
```java
@PostMapping("/api/auth/login")
@RateLimiter(name = "login", fallbackMethod = "loginRateLimited")
public TokenResponse login(@RequestBody LoginRequest request) {
    return authService.authenticate(request);
}
```

Go -- VULNERABLE:
```go
mux.HandleFunc("/api/auth/login", loginHandler)  // No rate limiting
```

Go -- FIXED:
```go
limiter := rate.NewLimiter(rate.Every(time.Second/5), 5)
mux.HandleFunc("/api/auth/login", rateLimitMiddleware(limiter, loginHandler))
```

**Scanner Coverage**: No direct scanner rule. Detected by checking for absence
of rate limiting middleware on sensitive endpoints.

**False Positive Guidance**: Internal microservice endpoints behind a service
mesh may rely on infrastructure-level rate limiting. Check the deployment
architecture before flagging internal APIs.

**Severity Assessment**:
- **high**: No rate limiting on authentication/login endpoints
- **medium**: No rate limiting on data enumeration or expensive endpoints
- **low**: Rate limiting present but limits are generous

---

## 4. Broken Function-Level Authorization

**Description**: Admin or privileged API endpoints check that the user is
authenticated but do not verify the user's role or permissions. Any
authenticated user can access admin functionality by calling the endpoints
directly.

**Search Heuristics**:
- Grep: `@admin|@roles|hasRole|isAdmin|requireAdmin` to map protected endpoints
- Grep: `router\.(post|put|delete|patch).*admin|/api/admin/` without role check
- Grep: `@PreAuthorize|@Secured|@RolesAllowed` on admin endpoints
- Grep: `authenticate|isAuthenticated` without `authorize|isAdmin|hasPermission`
- Glob: `**/routes/**`, `**/controllers/**`, `**/admin/**`

**Language Examples**:

Python (Flask) -- VULNERABLE:
```python
@app.route('/api/admin/users', methods=['DELETE'])
@login_required  # Authenticated but not admin-checked
def delete_user():
    user_id = request.json['user_id']
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return jsonify({"status": "deleted"})
```

Python (Flask) -- FIXED:
```python
@app.route('/api/admin/users', methods=['DELETE'])
@login_required
@admin_required
def delete_user():
    user_id = request.json['user_id']
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return jsonify({"status": "deleted"})
```

JavaScript (Express) -- VULNERABLE:
```javascript
router.delete('/api/admin/users/:id', authenticate, async (req, res) => {
  // authenticate checks token, but no role check
  await User.findByIdAndDelete(req.params.id);
  res.json({ status: 'deleted' });
});
```

JavaScript (Express) -- FIXED:
```javascript
router.delete('/api/admin/users/:id', authenticate, requireRole('admin'), async (req, res) => {
  await User.findByIdAndDelete(req.params.id);
  res.json({ status: 'deleted' });
});
```

Java (Spring) -- VULNERABLE:
```java
@DeleteMapping("/api/admin/users/{id}")
public void deleteUser(@PathVariable Long id, Authentication auth) {
    // auth is present but role is not checked
    userRepository.deleteById(id);
}
```

Java (Spring) -- FIXED:
```java
@DeleteMapping("/api/admin/users/{id}")
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(@PathVariable Long id) {
    userRepository.deleteById(id);
}
```

Go -- VULNERABLE:
```go
// Auth middleware applied but no role check
mux.Handle("/api/admin/users", authMiddleware(http.HandlerFunc(deleteUserHandler)))
```

Go -- FIXED:
```go
mux.Handle("/api/admin/users", authMiddleware(adminOnly(http.HandlerFunc(deleteUserHandler))))
```

**Scanner Coverage**: semgrep `generic.api.security.missing-function-level-auth`

**False Positive Guidance**: Endpoints that use path-based authorization
(e.g., all `/api/admin/**` routes are behind an admin middleware at the
router level) may appear unprotected at the handler level but are actually
secured. Trace the full middleware chain.

**Severity Assessment**:
- **critical**: Unauthenticated access to admin functions
- **high**: Authenticated non-admin users can access admin functions
- **medium**: Inconsistent role checks across related admin endpoints

---

## 5. Excessive Data Exposure

**Description**: API responses include more data than the client needs,
exposing sensitive fields like password hashes, internal IDs, tokens, or
metadata. Unlike web UIs where rendering controls visibility, API consumers
receive the raw data and can inspect all fields.

**Search Heuristics**:
- Grep: `\.toJSON|to_dict|to_json|serialize|as_dict` without field filtering
- Grep: `res\.json\(user\)|Response\(serializer\.data\)` returning full model
- Grep: `exclude.*password|fields.*__all__` in serializer definitions
- Grep: `select\s*\*|SELECT \*` in queries backing API responses
- Glob: `**/serializers/**`, `**/dto/**`, `**/controllers/**`, `**/handlers/**`

**Language Examples**:

Python (Django REST) -- VULNERABLE:
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # Includes password_hash, internal fields
```

Python (Django REST) -- FIXED:
```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'avatar_url']  # Explicit allowlist
```

JavaScript (Express + Mongoose) -- VULNERABLE:
```javascript
router.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);  // Includes passwordHash, resetToken, etc.
});
```

JavaScript (Express + Mongoose) -- FIXED:
```javascript
router.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id)
    .select('name email avatarUrl -_id');  // Explicit projection
  res.json(user);
});
```

Java (Spring) -- VULNERABLE:
```java
@GetMapping("/api/users/{id}")
public User getUser(@PathVariable Long id) {
    return userRepository.findById(id).orElseThrow();  // Full entity
}
```

Java (Spring) -- FIXED:
```java
@GetMapping("/api/users/{id}")
public UserDTO getUser(@PathVariable Long id) {
    User user = userRepository.findById(id).orElseThrow();
    return new UserDTO(user.getName(), user.getEmail());  // DTO limits exposure
}
```

Go -- VULNERABLE:
```go
func GetUser(w http.ResponseWriter, r *http.Request) {
    var user User
    db.First(&user, id)
    json.NewEncoder(w).Encode(user)  // Includes PasswordHash, InternalNotes
}
```

Go -- FIXED:
```go
type UserResponse struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

func GetUser(w http.ResponseWriter, r *http.Request) {
    var user User
    db.First(&user, id)
    json.NewEncoder(w).Encode(UserResponse{Name: user.Name, Email: user.Email})
}
```

**Scanner Coverage**: semgrep `generic.api.security.excessive-data-exposure`

**False Positive Guidance**: Admin APIs that intentionally return full objects
for management purposes may not need field filtering. Internal microservice
APIs where both sides are trusted may expose more data. Check the API consumer
context.

**Severity Assessment**:
- **critical**: API exposes password hashes, auth tokens, or encryption keys
- **high**: API exposes PII (SSN, financial data) not needed by the client
- **medium**: API exposes internal metadata (created_at, internal IDs, debug info)
- **low**: API returns slightly more fields than the UI uses
