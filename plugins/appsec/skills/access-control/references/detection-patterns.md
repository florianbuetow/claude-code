# Access Control Detection Patterns

Patterns for detecting broken access control vulnerabilities (OWASP A01:2021).

---

## 1. Missing Authorization Middleware on Routes

**Description**: Route handlers that perform sensitive operations but lack
authorization middleware in their chain. This is the most common access
control flaw — the endpoint simply never checks who is calling it.

**Search Heuristics**:
- Grep: `app\.(get|post|put|patch|delete)\s*\(` then verify middleware chain
- Grep: `@(app\.route|router\.)` without `@login_required` or `@requires_auth`
- Grep: `@(Request|Get|Post|Put|Delete)Mapping` without `@PreAuthorize` or `@Secured`
- Glob: `**/routes/**`, `**/controllers/**`, `**/handlers/**`

**Language Examples**:

Python (Flask) — VULNERABLE:
```python
@app.route('/admin/users', methods=['DELETE'])
def delete_user():
    user_id = request.args.get('id')
    db.session.query(User).filter_by(id=user_id).delete()
    return jsonify({"status": "deleted"})
```

Python (Flask) — FIXED:
```python
@app.route('/admin/users', methods=['DELETE'])
@login_required
@admin_required
def delete_user():
    user_id = request.args.get('id')
    db.session.query(User).filter_by(id=user_id).delete()
    return jsonify({"status": "deleted"})
```

JavaScript (Express) — VULNERABLE:
```javascript
router.delete('/api/users/:id', async (req, res) => {
  await User.findByIdAndDelete(req.params.id);
  res.json({ status: 'deleted' });
});
```

JavaScript (Express) — FIXED:
```javascript
router.delete('/api/users/:id', authenticate, authorize('admin'), async (req, res) => {
  await User.findByIdAndDelete(req.params.id);
  res.json({ status: 'deleted' });
});
```

Java (Spring) — VULNERABLE:
```java
@DeleteMapping("/api/users/{id}")
public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
    userRepository.deleteById(id);
    return ResponseEntity.noContent().build();
}
```

Java (Spring) — FIXED:
```java
@DeleteMapping("/api/users/{id}")
@PreAuthorize("hasRole('ADMIN')")
public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
    userRepository.deleteById(id);
    return ResponseEntity.noContent().build();
}
```

Go (net/http) — VULNERABLE:
```go
mux.HandleFunc("/api/users/delete", func(w http.ResponseWriter, r *http.Request) {
    id := r.URL.Query().Get("id")
    db.Exec("DELETE FROM users WHERE id = ?", id)
    w.WriteHeader(http.StatusNoContent)
})
```

Go (net/http) — FIXED:
```go
mux.Handle("/api/users/delete", authMiddleware(adminOnly(http.HandlerFunc(
    func(w http.ResponseWriter, r *http.Request) {
        id := r.URL.Query().Get("id")
        db.Exec("DELETE FROM users WHERE id = ?", id)
        w.WriteHeader(http.StatusNoContent)
    },
))))
```

**Scanner Coverage**: semgrep `javascript.express.security.audit.missing-auth-middleware`,
semgrep `python.django.security.audit.unvalidated-method`

**False Positive Guidance**: Not every route needs authorization. Public endpoints
(health checks, login, registration, public content) are intentionally open.
Verify the endpoint handles sensitive data or mutations before flagging.

**Severity Assessment**:
- **critical**: Admin/destructive endpoints with zero auth
- **high**: Data-mutation endpoints without auth
- **medium**: Read endpoints for non-public data without auth

---

## 2. Insecure Direct Object Reference (IDOR)

**Description**: The application uses a user-supplied identifier to access a
database record without verifying the authenticated user owns or is authorized
to access that record.

**Search Heuristics**:
- Grep: `req\.params\.(id|userId|orderId)` or `request\.args\.get\(['"]id`
- Grep: `findById\(.*params` or `findOne\(.*params` without ownership filter
- Grep: `WHERE id = ` combined with user-supplied input
- Glob: `**/controllers/**`, `**/api/**`, `**/handlers/**`

**Language Examples**:

Python (Django) — VULNERABLE:
```python
def get_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    return JsonResponse(invoice.to_dict())
```

Python (Django) — FIXED:
```python
def get_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id, owner=request.user)
    return JsonResponse(invoice.to_dict())
```

JavaScript (Express + Mongoose) — VULNERABLE:
```javascript
router.get('/api/orders/:id', authenticate, async (req, res) => {
  const order = await Order.findById(req.params.id);
  res.json(order);
});
```

JavaScript (Express + Mongoose) — FIXED:
```javascript
router.get('/api/orders/:id', authenticate, async (req, res) => {
  const order = await Order.findOne({ _id: req.params.id, userId: req.user.id });
  if (!order) return res.status(404).json({ error: 'Not found' });
  res.json(order);
});
```

Java (Spring) — VULNERABLE:
```java
@GetMapping("/api/documents/{id}")
public Document getDocument(@PathVariable Long id) {
    return documentRepository.findById(id)
        .orElseThrow(() -> new NotFoundException("Document not found"));
}
```

Java (Spring) — FIXED:
```java
@GetMapping("/api/documents/{id}")
public Document getDocument(@PathVariable Long id, @AuthenticationPrincipal User user) {
    return documentRepository.findByIdAndOwnerId(id, user.getId())
        .orElseThrow(() -> new NotFoundException("Document not found"));
}
```

Go — VULNERABLE:
```go
func GetProfile(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    var profile Profile
    db.First(&profile, id)
    json.NewEncoder(w).Encode(profile)
}
```

Go — FIXED:
```go
func GetProfile(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    userID := r.Context().Value("userID").(string)
    var profile Profile
    result := db.Where("id = ? AND user_id = ?", id, userID).First(&profile)
    if result.Error != nil {
        http.Error(w, "Not found", http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(profile)
}
```

**Scanner Coverage**: semgrep `generic.idor.security.direct-object-reference`

**False Positive Guidance**: Admin endpoints that intentionally allow access to
any record are not IDOR. Public resources (blog posts, product listings) accessed
by ID are not IDOR unless they contain private data. Check whether the resource
type is inherently user-scoped before flagging.

**Severity Assessment**:
- **critical**: IDOR on sensitive data (financial records, PII, medical data)
- **high**: IDOR on user-scoped data (orders, messages, documents)
- **medium**: IDOR on less sensitive data with limited impact

---

## 3. CORS Wildcard Configuration

**Description**: The application sets `Access-Control-Allow-Origin` to `*` or
reflects the request `Origin` header without validation, potentially allowing
malicious sites to read responses from the API.

**Search Heuristics**:
- Grep: `Access-Control-Allow-Origin.*\*`
- Grep: `cors\(\s*\)` (default CORS configuration, often permissive)
- Grep: `origin:\s*true` or `origin:\s*\*`
- Grep: `AllowAllOrigins.*true` or `AllowOrigins.*\*`
- Glob: `**/config/**`, `**/middleware/**`, `**/*.config.*`

**Language Examples**:

Python (Flask) — VULNERABLE:
```python
from flask_cors import CORS
CORS(app)  # allows all origins by default
```

Python (Flask) — FIXED:
```python
from flask_cors import CORS
CORS(app, origins=["https://app.example.com"], supports_credentials=True)
```

JavaScript (Express) — VULNERABLE:
```javascript
const cors = require('cors');
app.use(cors());  // allows all origins
```

JavaScript (Express) — FIXED:
```javascript
const cors = require('cors');
app.use(cors({
  origin: ['https://app.example.com'],
  credentials: true,
}));
```

Java (Spring) — VULNERABLE:
```java
@CrossOrigin(origins = "*")
@RestController
public class ApiController { }
```

Java (Spring) — FIXED:
```java
@CrossOrigin(origins = "https://app.example.com")
@RestController
public class ApiController { }
```

Go (net/http) — VULNERABLE:
```go
w.Header().Set("Access-Control-Allow-Origin", "*")
w.Header().Set("Access-Control-Allow-Credentials", "true")
```

Go (net/http) — FIXED:
```go
allowedOrigin := "https://app.example.com"
origin := r.Header.Get("Origin")
if origin == allowedOrigin {
    w.Header().Set("Access-Control-Allow-Origin", origin)
    w.Header().Set("Access-Control-Allow-Credentials", "true")
}
```

**Scanner Coverage**: semgrep `generic.cors.security.wildcard-origin`

**False Positive Guidance**: Public APIs that serve non-sensitive, read-only data
(e.g., a public CDN or open data API) may intentionally use `*`. CORS wildcard
without `Access-Control-Allow-Credentials: true` cannot leak authenticated data.
Only flag when credentials are enabled or the API handles sensitive data.

**Severity Assessment**:
- **high**: Wildcard origin with `credentials: true` on an API handling sensitive data
- **medium**: Overly permissive origin list or origin reflection without credentials
- **low**: Wildcard on a genuinely public, non-authenticated API

---

## 4. JWT Claims Not Verified

**Description**: The application reads JWT payload data (claims) without
verifying the token signature, or trusts client-editable claims for
authorization decisions without server-side validation.

**Search Heuristics**:
- Grep: `jwt\.decode\(.*verify\s*=\s*False` or `jwt\.decode\(.*algorithms\s*=\s*\[\]`
- Grep: `jwt_decode\(.*options.*verify` with verification disabled
- Grep: `atob\(.*split\(['"]\.['"]` (manual base64 decode of JWT payload)
- Grep: `JSON\.parse\(.*Buffer\.from\(.*base64` (manual JWT payload parsing)
- Glob: `**/auth/**`, `**/middleware/**`, `**/utils/jwt*`

**Language Examples**:

Python — VULNERABLE:
```python
import jwt
payload = jwt.decode(token, options={"verify_signature": False})
user_role = payload["role"]
```

Python — FIXED:
```python
import jwt
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_role = payload["role"]
```

JavaScript — VULNERABLE:
```javascript
// Manual decode without verification
const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
if (payload.role === 'admin') { /* grant access */ }
```

JavaScript — FIXED:
```javascript
const jwt = require('jsonwebtoken');
const payload = jwt.verify(token, process.env.JWT_SECRET);
if (payload.role === 'admin') { /* grant access */ }
```

Java — VULNERABLE:
```java
// Parsing without signature verification
String[] parts = token.split("\\.");
String payload = new String(Base64.getDecoder().decode(parts[1]));
JSONObject claims = new JSONObject(payload);
String role = claims.getString("role");
```

Java — FIXED:
```java
Claims claims = Jwts.parserBuilder()
    .setSigningKey(secretKey)
    .build()
    .parseClaimsJws(token)
    .getBody();
String role = claims.get("role", String.class);
```

Go — VULNERABLE:
```go
token, _ := jwt.Parse(tokenString, nil) // no key function
claims := token.Claims.(jwt.MapClaims)
role := claims["role"].(string)
```

Go — FIXED:
```go
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
    }
    return []byte(secretKey), nil
})
if err != nil {
    return err
}
claims := token.Claims.(jwt.MapClaims)
role := claims["role"].(string)
```

**Scanner Coverage**: semgrep `python.jwt.security.unverified-jwt-decode`,
semgrep `javascript.jsonwebtoken.security.jwt-none-alg`

**False Positive Guidance**: Some code intentionally decodes JWT without
verification for non-security purposes (e.g., extracting the `exp` claim to
display session time remaining in the UI, or logging). Only flag when the
decoded claims drive authorization decisions.

**Severity Assessment**:
- **critical**: Unverified JWT used for admin/role-based authorization
- **high**: Unverified JWT used for any authorization decision
- **medium**: Algorithm not pinned (vulnerable to `alg: none` attack)

---

## 5. Forced Browsing / Predictable Resource URLs

**Description**: Resources are accessible via predictable, sequential, or
guessable identifiers (e.g., `/invoices/1001`, `/invoices/1002`) without
authorization checks. Attackers enumerate valid IDs to access unauthorized data.

**Search Heuristics**:
- Grep: `/:id` or `/<int:id>` in route definitions without auth middleware
- Grep: `auto_increment` or `SERIAL` in schema (indicates sequential IDs)
- Grep: `uuid` absence in model ID fields (sequential integers are predictable)
- Glob: `**/models/**`, `**/schema/**`, `**/migrations/**`

**Language Examples**:

Python (Django) — VULNERABLE:
```python
class Invoice(models.Model):
    id = models.AutoField(primary_key=True)  # sequential, predictable
    data = models.TextField()

# URL pattern: /invoices/<int:pk>/
```

Python (Django) — FIXED:
```python
import uuid
class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()

# View still checks ownership:
def get_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user)
    return JsonResponse(model_to_dict(invoice))
```

JavaScript (Sequelize) — VULNERABLE:
```javascript
const Invoice = sequelize.define('Invoice', {
  id: { type: DataTypes.INTEGER, autoIncrement: true, primaryKey: true },
  data: DataTypes.TEXT,
});
// GET /invoices/:id — no ownership check
```

JavaScript (Sequelize) — FIXED:
```javascript
const { v4: uuidv4 } = require('uuid');
const Invoice = sequelize.define('Invoice', {
  id: { type: DataTypes.UUID, defaultValue: uuidv4, primaryKey: true },
  userId: { type: DataTypes.UUID, allowNull: false },
  data: DataTypes.TEXT,
});
// GET /invoices/:id — always filter by userId
```

**Scanner Coverage**: No direct scanner rule. This is detected through code
analysis of ID generation strategy combined with route authorization patterns.

**False Positive Guidance**: Sequential IDs are not inherently vulnerable if
every access path enforces authorization. UUIDs reduce enumeration risk but are
not a substitute for access checks. Public resources (blog posts, product pages)
with sequential IDs are not a vulnerability.

**Severity Assessment**:
- **high**: Sequential IDs on sensitive resources with no authorization
- **medium**: Sequential IDs on sensitive resources with authorization (defense-in-depth concern)
- **low**: Sequential IDs on non-sensitive public resources

---

## 6. Missing Function-Level Access Control

**Description**: The application enforces access control at the page or
top-level route but fails to check authorization on specific functions
or API actions. For example, a regular user cannot see the admin panel
but can call the admin API endpoints directly.

**Search Heuristics**:
- Grep: `isAdmin|is_admin|hasRole|has_role` to find existing role checks, then verify coverage
- Grep: `@admin_required|@roles_required|@Secured|@PreAuthorize` to map protected endpoints
- Grep: route definitions for `/admin/` paths and verify each has role checks
- Glob: `**/admin/**`, `**/management/**`, `**/internal/**`

**Language Examples**:

Python (Flask) — VULNERABLE:
```python
# Admin page is protected, but API endpoint is not
@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_template('admin.html')

@app.route('/api/admin/promote-user', methods=['POST'])
@login_required  # any authenticated user can promote!
def promote_user():
    user = User.query.get(request.json['user_id'])
    user.role = 'admin'
    db.session.commit()
    return jsonify({"status": "promoted"})
```

Python (Flask) — FIXED:
```python
@app.route('/api/admin/promote-user', methods=['POST'])
@login_required
@admin_required
def promote_user():
    user = User.query.get(request.json['user_id'])
    user.role = 'admin'
    db.session.commit()
    return jsonify({"status": "promoted"})
```

JavaScript (Express) — VULNERABLE:
```javascript
// UI route is protected
router.get('/admin', authenticate, requireAdmin, renderAdminPanel);

// API route only checks authentication, not admin role
router.post('/api/admin/settings', authenticate, async (req, res) => {
  await Settings.update(req.body);
  res.json({ status: 'updated' });
});
```

JavaScript (Express) — FIXED:
```javascript
router.post('/api/admin/settings', authenticate, requireAdmin, async (req, res) => {
  await Settings.update(req.body);
  res.json({ status: 'updated' });
});
```

Java (Spring) — VULNERABLE:
```java
// SecurityConfig protects /admin/** pages but not /api/admin/**
http.authorizeRequests()
    .antMatchers("/admin/**").hasRole("ADMIN")
    .antMatchers("/api/**").authenticated()  // any authenticated user
    .anyRequest().permitAll();
```

Java (Spring) — FIXED:
```java
http.authorizeRequests()
    .antMatchers("/admin/**").hasRole("ADMIN")
    .antMatchers("/api/admin/**").hasRole("ADMIN")
    .antMatchers("/api/**").authenticated()
    .anyRequest().permitAll();
```

Go — VULNERABLE:
```go
// Admin middleware only on UI routes
adminMux := http.NewServeMux()
adminMux.HandleFunc("/admin/", adminPageHandler)
mux.Handle("/admin/", adminMiddleware(adminMux))

// API admin routes have no admin check
mux.HandleFunc("/api/admin/config", authMiddleware(configHandler))
```

Go — FIXED:
```go
mux.Handle("/admin/", adminMiddleware(adminMux))
mux.Handle("/api/admin/", adminMiddleware(http.HandlerFunc(configHandler)))
```

**Scanner Coverage**: semgrep `generic.security.audit.missing-function-level-access-control`

**False Positive Guidance**: Some `/admin/` paths may be intentionally public
(e.g., admin login page). Internal microservices behind a service mesh may rely
on network-level access control rather than application-level checks. Verify the
deployment context before flagging inter-service calls.

**Severity Assessment**:
- **critical**: Unauthenticated access to admin functionality
- **high**: Authenticated non-admin users can access admin functions
- **medium**: Inconsistent role checks across related endpoints (partial coverage)
