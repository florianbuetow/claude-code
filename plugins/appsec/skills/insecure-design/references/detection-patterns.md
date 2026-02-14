# Insecure Design Detection Patterns

Detailed detection patterns for OWASP A04:2021 Insecure Design analysis. Each
pattern includes Grep regex heuristics, language-specific examples, scanner
coverage, false positive guidance, and severity criteria.

Because insecure design is fundamentally about the absence of controls rather
than the presence of vulnerable code, these patterns focus on detecting what is
missing. Grep heuristics help identify areas where controls should exist; Claude
reasoning then determines whether the controls are actually absent.

---

## Pattern 1: Missing Rate Limiting on Sensitive Endpoints

### Description

Sensitive endpoints such as login, registration, password reset, OTP/MFA
verification, and payment processing have no rate limiting, throttling, or
abuse prevention. This allows brute-force attacks, credential stuffing,
account enumeration, and resource exhaustion.

### Grep Search Heuristics

First, identify sensitive endpoints; then check for absence of rate limiting:

```
# Identify login/auth endpoints
"(route|path|endpoint|url)\s*[\(=].*(/login|/signin|/auth|/token|/register|/signup)"
"(post|put)\s*[\(].*(/login|/signin|/auth|/register|/password|/reset|/otp|/verify)"
"def\s+(login|signin|authenticate|register|signup|reset_password|verify_otp)"

# Identify rate limiting middleware/decorators (should be present)
"rate.?limit|throttle|slowdown|brute.?force|express-rate-limit|ratelimit|@throttle|@rate_limit"
"RateLimiter|ThrottleGuard|rate_limit_decorator|api_throttle"

# Identify payment/financial endpoints
"(route|path|endpoint)\s*[\(=].*(/pay|/charge|/transfer|/withdraw|/purchase)"
"(post|put)\s*[\(].*(/pay|/charge|/transfer|/order)"
```

### Language Examples

**Python (Flask) -- Vulnerable**:
```python
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect("/dashboard")
    return render_template("login.html", error="Invalid credentials")
```

**Python (Flask) -- Fixed**:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        return redirect("/dashboard")
    # Use constant-time response to prevent timing attacks
    return render_template("login.html", error="Invalid credentials")
```

**JavaScript/TypeScript (Express) -- Vulnerable**:
```javascript
app.post("/api/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user || !await user.comparePassword(password)) {
    return res.status(401).json({ error: "Invalid credentials" });
  }
  const token = generateToken(user);
  res.json({ token });
});
```

**JavaScript/TypeScript (Express) -- Fixed**:
```javascript
import rateLimit from "express-rate-limit";

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: { error: "Too many login attempts, try again later" },
  standardHeaders: true,
});

app.post("/api/login", loginLimiter, async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user || !await user.comparePassword(password)) {
    return res.status(401).json({ error: "Invalid credentials" });
  }
  const token = generateToken(user);
  res.json({ token });
});
```

**Java (Spring Boot) -- Vulnerable**:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    User user = userService.findByEmail(request.getEmail());
    if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
        return ResponseEntity.status(401).body("Invalid credentials");
    }
    String token = jwtService.generateToken(user);
    return ResponseEntity.ok(new AuthResponse(token));
}
```

**Java (Spring Boot) -- Fixed**:
```java
@PostMapping("/login")
@RateLimited(requests = 5, period = Duration.ofMinutes(15), key = "#request.email")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    User user = userService.findByEmail(request.getEmail());
    if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
        return ResponseEntity.status(401).body("Invalid credentials");
    }
    String token = jwtService.generateToken(user);
    return ResponseEntity.ok(new AuthResponse(token));
}
```

**Go -- Vulnerable**:
```go
func loginHandler(w http.ResponseWriter, r *http.Request) {
    var creds Credentials
    json.NewDecoder(r.Body).Decode(&creds)
    user, err := db.FindUser(creds.Email)
    if err != nil || !checkPassword(user.Hash, creds.Password) {
        http.Error(w, "Invalid credentials", http.StatusUnauthorized)
        return
    }
    token := generateToken(user)
    json.NewEncoder(w).Encode(map[string]string{"token": token})
}
```

**Go -- Fixed**:
```go
import "golang.org/x/time/rate"

var loginLimiter = NewIPRateLimiter(rate.Every(time.Minute/5), 5)

func loginHandler(w http.ResponseWriter, r *http.Request) {
    if !loginLimiter.Allow(r.RemoteAddr) {
        http.Error(w, "Too many attempts", http.StatusTooManyRequests)
        return
    }
    var creds Credentials
    json.NewDecoder(r.Body).Decode(&creds)
    user, err := db.FindUser(creds.Email)
    if err != nil || !checkPassword(user.Hash, creds.Password) {
        http.Error(w, "Invalid credentials", http.StatusUnauthorized)
        return
    }
    token := generateToken(user)
    json.NewEncoder(w).Encode(map[string]string{"token": token})
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Partial | Some community rules for missing rate limiting |
| All others | No | Not detectable by SAST scanners |

**Primary detection**: Claude analysis. Identify auth endpoints, then check whether
rate limiting middleware/decorators are applied.

### False Positive Guidance

- **API gateway rate limiting**: Rate limiting may be applied at the API gateway
  or load balancer level (nginx, Kong, AWS API Gateway) rather than in application
  code. Check infrastructure configuration before flagging.
- **WAF protection**: A Web Application Firewall may provide rate limiting. This
  is valid but less reliable than application-level controls.
- **Internal-only endpoints**: Services behind a VPN or service mesh with
  authenticated callers are lower risk but should still have rate limiting.

### Severity Criteria

- **critical**: Public-facing login or payment endpoint with no rate limiting
  and no account lockout.
- **high**: Public-facing registration, password reset, or OTP endpoint with
  no rate limiting.
- **medium**: Authenticated API endpoint with no rate limiting that could
  enable data scraping or resource exhaustion.
- **low**: Internal endpoint with no rate limiting.

---

## Pattern 2: No CSRF Protection on State-Changing Operations

### Description

State-changing operations (POST, PUT, DELETE) do not validate CSRF tokens,
allowing an attacker to forge cross-site requests from a victim's authenticated
browser session. This is especially dangerous for actions like password changes,
email updates, fund transfers, and admin operations.

### Grep Search Heuristics

```
# Check for CSRF middleware/configuration
"csrf|CSRF|xsrf|XSRF|cross.?site.?request"
"csurf|csrf_protect|@csrf_exempt|CsrfViewMiddleware|AntiForgeryToken"
"csrf_token|csrfmiddlewaretoken|_csrf|X-CSRF-Token|X-XSRF-Token"

# Identify state-changing endpoints (should have CSRF protection)
"@app\.(post|put|delete|patch)|app\.(post|put|delete|patch)"
"@(Post|Put|Delete|Patch)Mapping|@RequestMapping.*method.*POST"
"router\.(post|put|delete|patch)|HandleFunc.*POST"

# Identify explicit CSRF exemptions (suspicious)
"csrf_exempt|@csrf_exempt|disable.*csrf|skip.*csrf|ignore.*csrf"
"csrfProtection.*false|csrf:\s*false|enableCsrf.*disable"
```

### Language Examples

**Python (Django) -- Vulnerable**:
```python
# In settings.py, CSRF middleware is removed or:
@csrf_exempt
def transfer_funds(request):
    amount = request.POST.get("amount")
    to_account = request.POST.get("to_account")
    perform_transfer(request.user, to_account, amount)
    return JsonResponse({"status": "success"})
```

**Python (Django) -- Fixed**:
```python
# Ensure CsrfViewMiddleware is in MIDDLEWARE (default in Django)
# Do NOT use @csrf_exempt on sensitive endpoints
def transfer_funds(request):
    amount = request.POST.get("amount")
    to_account = request.POST.get("to_account")
    perform_transfer(request.user, to_account, amount)
    return JsonResponse({"status": "success"})
# Template must include {% csrf_token %} in form
```

**JavaScript/TypeScript (Express) -- Vulnerable**:
```javascript
// No CSRF middleware installed
app.post("/api/transfer", requireAuth, async (req, res) => {
  const { toAccount, amount } = req.body;
  await transferFunds(req.user.id, toAccount, amount);
  res.json({ status: "success" });
});
```

**JavaScript/TypeScript (Express) -- Fixed**:
```javascript
import csrf from "csurf";
const csrfProtection = csrf({ cookie: true });

// Apply CSRF protection to state-changing routes
app.post("/api/transfer", requireAuth, csrfProtection, async (req, res) => {
  const { toAccount, amount } = req.body;
  await transferFunds(req.user.id, toAccount, amount);
  res.json({ status: "success" });
});
// Or use SameSite cookies + Origin header validation for API-only apps
```

**Java (Spring Boot) -- Vulnerable**:
```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf().disable()  // CSRF disabled entirely
            .authorizeRequests()
            .anyRequest().authenticated();
    }
}
```

**Java (Spring Boot) -- Fixed**:
```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.csrf()  // CSRF enabled (default)
            .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            .and()
            .authorizeRequests()
            .anyRequest().authenticated();
    }
}
```

**Go -- Vulnerable**:
```go
// No CSRF protection middleware
http.HandleFunc("/transfer", func(w http.ResponseWriter, r *http.Request) {
    if r.Method != "POST" {
        http.Error(w, "Method not allowed", 405)
        return
    }
    amount := r.FormValue("amount")
    toAccount := r.FormValue("to_account")
    transferFunds(getUserID(r), toAccount, amount)
    json.NewEncoder(w).Encode(map[string]string{"status": "success"})
})
```

**Go -- Fixed**:
```go
import "github.com/gorilla/csrf"

// Apply CSRF middleware globally
csrfMiddleware := csrf.Protect([]byte(csrfKey), csrf.Secure(true))
http.ListenAndServe(":8080", csrfMiddleware(router))
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Partial | `*.security.audit.csrf-disabled`, framework-specific rules |
| brakeman | Yes (Rails) | CSRF warning |
| All others | No | -- |

**Primary detection**: Claude analysis. Check for CSRF middleware in the request
pipeline and explicit CSRF exemptions on sensitive endpoints.

### False Positive Guidance

- **API-only applications**: Pure JSON APIs that do not use cookies for
  authentication (using Bearer tokens instead) are not vulnerable to CSRF.
  Check the authentication mechanism before flagging.
- **SameSite cookies**: If the application uses `SameSite=Strict` or
  `SameSite=Lax` cookies, CSRF risk is significantly reduced for modern
  browsers. Still recommend explicit CSRF tokens as defense-in-depth.
- **GET endpoints**: CSRF on GET endpoints is lower risk since GET should be
  idempotent. Only flag if GET endpoints cause state changes.

### Severity Criteria

- **critical**: CSRF disabled on financial transactions, admin operations, or
  account management endpoints.
- **high**: CSRF disabled globally with state-changing endpoints present.
- **medium**: CSRF protection present but with broad exemptions on
  non-trivial endpoints.
- **low**: CSRF absent on low-impact state changes (e.g., theme preference).

---

## Pattern 3: Missing Account Lockout After Failed Authentication

### Description

Authentication systems that allow unlimited login attempts without lockout,
progressive delays, or CAPTCHA challenges. This enables brute-force and
credential stuffing attacks against user accounts.

### Grep Search Heuristics

```
# Look for login handlers WITHOUT lockout logic
"def\s+(login|authenticate|sign_in)|function\s+(login|authenticate|signIn)"
"@(Post|Put)Mapping.*login|router\.(post|put).*login"

# Look for lockout/attempt tracking (should be present)
"failed.?attempt|login.?attempt|attempt.?count|max.?attempts|lockout|locked.?out"
"brute.?force|account.?lock|login.?delay|progressive.?delay|captcha|recaptcha"
"MAX_LOGIN_ATTEMPTS|LOGIN_ATTEMPTS_LIMIT|LOCKOUT_DURATION|LOCKOUT_THRESHOLD"

# Look for failed login handling
"invalid.?(credential|password|login)|login.?fail|auth.?fail|wrong.?password"
"status.*401|Unauthorized|authentication.?failed"
```

### Language Examples

**Python (Django) -- Vulnerable**:
```python
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        # No tracking of failed attempts, no lockout
        messages.error(request, "Invalid credentials")
    return render(request, "login.html")
```

**Python (Django) -- Fixed**:
```python
from axes.decorators import axes_dispatch

# Using django-axes for automatic lockout
@axes_dispatch
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("dashboard")
        # django-axes automatically tracks failures and locks accounts
        messages.error(request, "Invalid credentials")
    return render(request, "login.html")

# settings.py:
# AXES_FAILURE_LIMIT = 5
# AXES_COOLOFF_TIME = timedelta(minutes=15)
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    return res.status(401).json({ error: "Invalid credentials" });
  }
  req.session.userId = user.id;
  res.json({ success: true });
});
```

**JavaScript/TypeScript -- Fixed**:
```javascript
const MAX_ATTEMPTS = 5;
const LOCKOUT_MINUTES = 15;

app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });

  // Check if account is locked
  if (user?.lockedUntil && user.lockedUntil > new Date()) {
    return res.status(423).json({ error: "Account locked. Try again later." });
  }

  if (!user || !await bcrypt.compare(password, user.passwordHash)) {
    if (user) {
      user.failedAttempts = (user.failedAttempts || 0) + 1;
      if (user.failedAttempts >= MAX_ATTEMPTS) {
        user.lockedUntil = new Date(Date.now() + LOCKOUT_MINUTES * 60000);
      }
      await user.save();
    }
    return res.status(401).json({ error: "Invalid credentials" });
  }

  // Reset on success
  user.failedAttempts = 0;
  user.lockedUntil = null;
  await user.save();
  req.session.userId = user.id;
  res.json({ success: true });
});
```

**Java (Spring Boot) -- Vulnerable**:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    User user = userRepo.findByEmail(request.getEmail());
    if (user == null || !encoder.matches(request.getPassword(), user.getHash())) {
        return ResponseEntity.status(401).body("Invalid credentials");
    }
    return ResponseEntity.ok(tokenService.generate(user));
}
```

**Java (Spring Boot) -- Fixed**:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    User user = userRepo.findByEmail(request.getEmail());

    if (user != null && user.isLocked()) {
        return ResponseEntity.status(423).body("Account locked");
    }

    if (user == null || !encoder.matches(request.getPassword(), user.getHash())) {
        if (user != null) {
            loginAttemptService.recordFailure(user);
        }
        return ResponseEntity.status(401).body("Invalid credentials");
    }

    loginAttemptService.resetAttempts(user);
    return ResponseEntity.ok(tokenService.generate(user));
}
```

**Go -- Vulnerable**:
```go
func loginHandler(w http.ResponseWriter, r *http.Request) {
    var creds LoginRequest
    json.NewDecoder(r.Body).Decode(&creds)
    user, _ := db.FindByEmail(creds.Email)
    if user == nil || !checkHash(user.Hash, creds.Password) {
        http.Error(w, "Invalid credentials", 401)
        return
    }
    writeToken(w, user)
}
```

**Go -- Fixed**:
```go
func loginHandler(w http.ResponseWriter, r *http.Request) {
    var creds LoginRequest
    json.NewDecoder(r.Body).Decode(&creds)

    if lockoutStore.IsLocked(creds.Email) {
        http.Error(w, "Account locked", 423)
        return
    }

    user, _ := db.FindByEmail(creds.Email)
    if user == nil || !checkHash(user.Hash, creds.Password) {
        lockoutStore.RecordFailure(creds.Email)
        http.Error(w, "Invalid credentials", 401)
        return
    }

    lockoutStore.Reset(creds.Email)
    writeToken(w, user)
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| All scanners | No | Account lockout is a design-level concern not detectable by SAST |

**Primary detection**: Claude analysis. Find authentication handlers and check
for failed attempt tracking and lockout logic.

### False Positive Guidance

- **External identity providers**: If authentication is delegated to an IdP
  (Auth0, Okta, Cognito, etc.), lockout is handled by the provider. Check
  whether the app uses delegated authentication.
- **Rate limiting as substitute**: Strong rate limiting on the login endpoint
  (Pattern 1) partially mitigates brute-force risk even without account lockout.
  Both are recommended but having one reduces the severity of missing the other.
- **Passwordless authentication**: Systems using magic links, SSO, or passkeys
  have different threat models for brute force. Evaluate accordingly.

### Severity Criteria

- **high**: Public login endpoint with no lockout and no rate limiting.
- **medium**: Login endpoint has rate limiting but no per-account lockout.
- **low**: Login endpoint is behind VPN or internal only.

---

## Pattern 4: Absence of Input Validation Layer

### Description

The application accepts user input without a server-side validation layer. Input
goes directly from HTTP request to business logic or database without type
checking, length limits, format validation, or sanitization. Client-side
validation alone is insufficient since it can be trivially bypassed.

### Grep Search Heuristics

```
# Direct request body usage without validation
"req\.body\.\w+|request\.form\[|request\.GET\[|request\.POST\["
"r\.FormValue|r\.URL\.Query|c\.Param|c\.Query"
"@RequestParam|@RequestBody|@PathVariable"

# Validation libraries/frameworks (should be present)
"validate|validator|joi|yup|zod|ajv|class-validator|express-validator"
"@Valid|@Validated|@NotNull|@NotBlank|@Size|@Pattern|@Email"
"cerberus|marshmallow|pydantic|WTForms|Django.?forms"
"govalidator|validator\.New|binding:\"required"

# Schema validation patterns
"schema\.validate|validate\(|isValid\(|parse\(|safeParse\("
```

### Language Examples

**Python (Flask) -- Vulnerable**:
```python
@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()
    # No validation: directly using request data
    user = User(
        name=data["name"],
        email=data["email"],
        age=data["age"],
        role=data["role"]  # User can set their own role!
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

**Python (Flask) -- Fixed**:
```python
from pydantic import BaseModel, EmailStr, conint, validator

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: conint(ge=0, le=150)
    # role is NOT accepted from user input

    @validator("name")
    def name_must_be_alphanumeric(cls, v):
        if not v.replace(" ", "").isalnum():
            raise ValueError("Name must be alphanumeric")
        return v.strip()

@app.route("/api/users", methods=["POST"])
def create_user():
    data = CreateUserRequest(**request.get_json())
    user = User(name=data.name, email=data.email, age=data.age, role="user")
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
app.post("/api/orders", async (req, res) => {
  // No validation: directly using request data
  const order = await Order.create({
    productId: req.body.productId,
    quantity: req.body.quantity,
    price: req.body.price,  // User can set their own price!
    userId: req.body.userId  // User can set any user ID!
  });
  res.json(order);
});
```

**JavaScript/TypeScript -- Fixed**:
```javascript
import { z } from "zod";

const createOrderSchema = z.object({
  productId: z.string().uuid(),
  quantity: z.number().int().min(1).max(100),
  // price comes from server, not client
  // userId comes from session, not client
});

app.post("/api/orders", async (req, res) => {
  const result = createOrderSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.issues });
  }
  const product = await Product.findByPk(result.data.productId);
  const order = await Order.create({
    productId: result.data.productId,
    quantity: result.data.quantity,
    price: product.price,     // Server-side price lookup
    userId: req.user.id,      // From authenticated session
  });
  res.json(order);
});
```

**Java (Spring Boot) -- Vulnerable**:
```java
@PostMapping("/api/orders")
public Order createOrder(@RequestBody Map<String, Object> body) {
    // No validation: raw map from request
    Order order = new Order();
    order.setProductId((String) body.get("productId"));
    order.setQuantity((Integer) body.get("quantity"));
    order.setPrice((Double) body.get("price"));  // Client-supplied price
    return orderRepo.save(order);
}
```

**Java (Spring Boot) -- Fixed**:
```java
@PostMapping("/api/orders")
public Order createOrder(@Valid @RequestBody CreateOrderRequest request,
                         @AuthenticationPrincipal UserDetails user) {
    Product product = productRepo.findById(request.getProductId()).orElseThrow();
    Order order = new Order();
    order.setProductId(request.getProductId());
    order.setQuantity(request.getQuantity());
    order.setPrice(product.getPrice());   // Server-side price
    order.setUserId(user.getId());        // From auth context
    return orderRepo.save(order);
}
// CreateOrderRequest uses @NotNull, @Min, @Max, @UUID annotations
```

**Go -- Vulnerable**:
```go
func createOrder(w http.ResponseWriter, r *http.Request) {
    var order Order
    json.NewDecoder(r.Body).Decode(&order) // No validation
    db.Create(&order)
    json.NewEncoder(w).Encode(order)
}
```

**Go -- Fixed**:
```go
func createOrder(w http.ResponseWriter, r *http.Request) {
    var req CreateOrderRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, "Invalid JSON", 400)
        return
    }
    if err := validate.Struct(req); err != nil {
        http.Error(w, err.Error(), 400)
        return
    }
    product, _ := db.FindProduct(req.ProductID)
    order := Order{
        ProductID: req.ProductID,
        Quantity:  req.Quantity,
        Price:     product.Price,
        UserID:    getUserID(r),
    }
    db.Create(&order)
    json.NewEncoder(w).Encode(order)
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Partial | Some rules for mass assignment patterns |
| All others | No | Input validation is a design-level concern |

**Primary detection**: Claude analysis. Examine how request data flows into
business logic and check for validation steps in between.

### False Positive Guidance

- **Framework auto-validation**: Some frameworks (e.g., Spring with `@Valid`,
  Rails strong parameters) apply validation through annotations or configuration.
  Check framework setup before flagging.
- **Middleware validation**: Validation may occur in middleware or interceptors
  rather than in the handler itself. Check the request pipeline.
- **DTO/schema patterns**: If the application uses typed DTOs, Pydantic models,
  or Zod schemas, validation may be implicit in the deserialization step.

### Severity Criteria

- **high**: User input directly used to set sensitive fields (price, role,
  permissions, other users' IDs) with no validation.
- **medium**: User input used without type/length validation but no sensitive
  field manipulation.
- **low**: Validation exists but is incomplete (e.g., missing length limits
  on string fields).

---

## Pattern 5: No Security Headers Middleware

### Description

The application does not set security response headers, leaving users vulnerable
to clickjacking (missing X-Frame-Options), MIME sniffing attacks (missing
X-Content-Type-Options), cross-site scripting (missing Content-Security-Policy),
protocol downgrade attacks (missing Strict-Transport-Security), and information
leakage (missing Referrer-Policy, Permissions-Policy).

### Grep Search Heuristics

```
# Security header middleware libraries
"helmet|secure_headers|django-csp|flask-talisman|spring.security.headers"
"SecureHeaders|SecurityHeaders|ContentSecurityPolicy"

# Individual header settings
"Content-Security-Policy|CSP|content.security.policy"
"Strict-Transport-Security|HSTS|strict.transport"
"X-Frame-Options|x.frame.options|DENY|SAMEORIGIN"
"X-Content-Type-Options|nosniff"
"Referrer-Policy|referrer.policy"
"Permissions-Policy|Feature-Policy"
"X-XSS-Protection"

# Response header setting patterns
"setHeader|set_header|Header\(\)|header\[|add_header|response\.headers"
"@Header|SecurityFilterChain|WebSecurityConfigurer"
```

### Language Examples

**Python (Flask) -- Vulnerable**:
```python
app = Flask(__name__)
# No security headers configured
# Responses go out with default headers only
```

**Python (Flask) -- Fixed**:
```python
from flask_talisman import Talisman

app = Flask(__name__)
Talisman(app, content_security_policy={
    "default-src": "'self'",
    "script-src": "'self'",
    "style-src": "'self' 'unsafe-inline'",
})
# Talisman sets HSTS, X-Content-Type-Options, X-Frame-Options, CSP
```

**JavaScript/TypeScript (Express) -- Vulnerable**:
```javascript
const app = express();
app.use(express.json());
// No security headers middleware
app.listen(3000);
```

**JavaScript/TypeScript (Express) -- Fixed**:
```javascript
import helmet from "helmet";

const app = express();
app.use(helmet());  // Sets 11 security headers by default
app.use(express.json());
app.listen(3000);
```

**Java (Spring Boot) -- Vulnerable**:
```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.headers().disable()  // All security headers disabled
            .authorizeRequests().anyRequest().authenticated();
    }
}
```

**Java (Spring Boot) -- Fixed**:
```java
@Configuration
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.headers()
                .contentSecurityPolicy("default-src 'self'")
                .and()
                .referrerPolicy(ReferrerPolicyHeaderWriter.ReferrerPolicy.STRICT_ORIGIN)
                .and()
                .permissionsPolicy(p -> p.policy("camera=(), microphone=()"))
            .and()
            .authorizeRequests().anyRequest().authenticated();
    }
}
```

**Go -- Vulnerable**:
```go
func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("/", homeHandler)
    // No security headers middleware
    http.ListenAndServe(":8080", mux)
}
```

**Go -- Fixed**:
```go
import "github.com/unrolled/secure"

func main() {
    secureMiddleware := secure.New(secure.Options{
        STSSeconds:            31536000,
        STSIncludeSubdomains:  true,
        FrameDeny:             true,
        ContentTypeNosniff:    true,
        ContentSecurityPolicy: "default-src 'self'",
        ReferrerPolicy:        "strict-origin-when-cross-origin",
    })
    mux := http.NewServeMux()
    mux.HandleFunc("/", homeHandler)
    http.ListenAndServe(":8080", secureMiddleware.Handler(mux))
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Partial | `*.security.audit.missing-helmet`, framework-specific rules |
| All others | No | Response headers are a deployment/configuration concern |

**Primary detection**: Claude analysis. Check the middleware/configuration for
security header setup. Also check reverse proxy configs (nginx, Apache).

### False Positive Guidance

- **Reverse proxy headers**: Security headers may be set at the reverse proxy
  (nginx, Apache, Cloudflare) rather than in application code. Check deployment
  configuration if accessible.
- **CDN/PaaS headers**: Platforms like Vercel, Netlify, and Cloudflare may
  inject security headers automatically. Check platform configuration.
- **API-only services**: Services that never serve HTML to browsers have reduced
  need for some headers (CSP, X-Frame-Options) but should still set
  X-Content-Type-Options and HSTS.

### Severity Criteria

- **high**: No security headers on a web application serving HTML to browsers.
  Missing CSP and HSTS together.
- **medium**: Some security headers present but missing critical ones (CSP or
  HSTS absent while others are set).
- **low**: API-only service missing non-critical headers, or minor header
  misconfiguration (e.g., CSP too permissive but present).

---

## Pattern 6: Trust-the-Client Design Patterns

### Description

Security-critical decisions (authorization, pricing, validation) are enforced
only in client-side code (JavaScript in the browser) without corresponding
server-side enforcement. Any client-side check can be bypassed by sending
requests directly to the API. This is a fundamental design flaw, not an
implementation bug.

### Grep Search Heuristics

```
# Client-side role/permission checks (should also be on server)
"(if|&&)\s*\(\s*(user|currentUser|auth)\.role\s*===?\s*[\"'](admin|moderator|manager)"
"(if|&&)\s*\(\s*(user|currentUser|auth)\.(isAdmin|isModerator|hasPermission|canEdit)"
"v-if=\".*role.*admin|ng-if=\".*role.*admin|\{.*role.*admin.*&&"

# Client-side price/amount calculations without server validation
"total\s*=\s*(price|amount|cost)\s*\*\s*(quantity|qty|count)"
"discount\s*=|coupon\s*=|promo.?code"

# Hidden form fields for sensitive data
"type=\"hidden\".*name=\"(price|amount|role|userId|discount|admin)\""
"input.*hidden.*value=.*\{|(price|amount|role|userId|discount)"

# Client-side-only routing guards
"canActivate|authGuard|PrivateRoute|RequireAuth|ProtectedRoute"
# (These are fine IF the API also enforces auth -- the concern is when ONLY the client checks)

# API calls without server-side auth middleware
"fetch\(|axios\.(get|post|put|delete)|\.ajax\("
```

### Language Examples

**JavaScript (React) -- Vulnerable**:
```javascript
// Frontend: Client-side-only admin check
function AdminPanel() {
  const { user } = useAuth();
  if (user.role !== "admin") {
    return <Navigate to="/" />;
  }
  return <AdminDashboard />;
}

// Backend: No role check on admin API
app.delete("/api/users/:id", requireAuth, async (req, res) => {
  // Anyone authenticated can delete any user!
  await User.destroy({ where: { id: req.params.id } });
  res.json({ success: true });
});
```

**JavaScript (React) -- Fixed**:
```javascript
// Frontend: Client-side check for UX (still needed for good UX)
function AdminPanel() {
  const { user } = useAuth();
  if (user.role !== "admin") {
    return <Navigate to="/" />;
  }
  return <AdminDashboard />;
}

// Backend: Server-side role enforcement
app.delete("/api/users/:id", requireAuth, requireRole("admin"), async (req, res) => {
  await User.destroy({ where: { id: req.params.id } });
  res.json({ success: true });
});
```

**JavaScript (Frontend) -- Vulnerable**:
```javascript
// Client-side price calculation sent to server
function checkout() {
  const total = cart.items.reduce((sum, item) => sum + item.price * item.qty, 0);
  const discount = promoCode ? total * 0.2 : 0;
  fetch("/api/checkout", {
    method: "POST",
    body: JSON.stringify({
      items: cart.items,
      total: total - discount,  // Server trusts this!
      promoCode,
    }),
  });
}
```

**JavaScript (Frontend) -- Fixed**:
```javascript
// Client calculates for display only; server recalculates
function checkout() {
  fetch("/api/checkout", {
    method: "POST",
    body: JSON.stringify({
      items: cart.items.map(i => ({ productId: i.id, quantity: i.qty })),
      promoCode,
    }),
    // Server looks up prices, validates promo code, calculates total
  });
}
```

**Python (Server) -- Vulnerable**:
```python
@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    # Trusting client-supplied total!
    charge_customer(request.user, data["total"])
    create_order(request.user, data["items"], data["total"])
    return jsonify({"status": "success"})
```

**Python (Server) -- Fixed**:
```python
@app.route("/api/checkout", methods=["POST"])
def checkout():
    data = request.get_json()
    # Server-side price calculation
    total = 0
    for item in data["items"]:
        product = Product.query.get(item["productId"])
        if not product:
            return jsonify({"error": "Invalid product"}), 400
        total += product.price * item["quantity"]
    if data.get("promoCode"):
        total = apply_promo(data["promoCode"], total)  # Server validates
    charge_customer(request.user, total)
    create_order(request.user, data["items"], total)
    return jsonify({"status": "success"})
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| All scanners | No | Trust boundary analysis requires architectural reasoning |

**Primary detection**: Claude analysis. This is the hardest pattern to detect
automatically. It requires understanding the relationship between frontend
validation and backend enforcement, which spans multiple files and layers.

### False Positive Guidance

- **Duplicate validation is intentional**: Client-side validation for UX is
  perfectly fine and expected -- the issue is when it is the ONLY validation.
  Check whether corresponding server-side validation exists.
- **Static site generators**: If the "backend" is a static site with no server
  logic, client-side checks may be the only option. The risk depends on what
  the checks protect.
- **BFF (Backend-for-Frontend)**: Some architectures place validation in a BFF
  layer between the frontend and microservices. Check whether a BFF exists.

### Severity Criteria

- **critical**: Server accepts client-supplied price, total, or discount
  without recalculation. Direct financial impact.
- **high**: Server trusts client-supplied role or permission data for
  authorization decisions.
- **medium**: Client-side form validation with no server-side equivalent for
  non-sensitive fields.
- **low**: Client-side UI guards (route protection) without sensitive server
  operations exposed.
