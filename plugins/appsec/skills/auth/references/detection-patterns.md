# Authentication Detection Patterns

Grep heuristics, language-specific code examples, scanner coverage, and false positive
guidance for identifying A07:2021 Identification and Authentication Failures.

---

## Pattern 1: Missing Rate Limiting on Login Endpoints

### Description

Login, registration, and password reset endpoints that lack rate limiting, account
lockout, or progressive delays are vulnerable to brute force and credential stuffing
attacks.

### Grep Heuristics

```
# Find login route handlers without adjacent rate limiting
/login|/signin|/authenticate
app\.(post|put)\(.*(login|signin|auth)
@(app\.route|router\.(post|put)).*login
handleLogin|handleSignIn|authenticateUser
func.*[Ll]ogin.*Handler
```

Then search the same file for rate-limiting indicators:
```
rate.?limit|throttle|slowDown|brute|lockout|max.?attempts|failed.?count
express-rate-limit|flask-limiter|RateLimiter|@throttle
```

If a login handler is found without nearby rate-limiting references, flag it.

### Language Examples

**Python (vulnerable)**:
```python
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = db.query(User).filter_by(username=username).first()
    if user and check_password(user.password_hash, password):
        session["user_id"] = user.id
        return redirect("/dashboard")
    return render_template("login.html", error="Invalid credentials")
```

**Python (fixed)**:
```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["100 per hour"])

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = db.query(User).filter_by(username=username).first()
    if user and check_password(user.password_hash, password):
        session["user_id"] = user.id
        return redirect("/dashboard")
    time.sleep(1)  # Constant-time response to prevent user enumeration
    return render_template("login.html", error="Invalid credentials")
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
app.post("/login", async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (user && await bcrypt.compare(password, user.passwordHash)) {
    req.session.userId = user.id;
    return res.redirect("/dashboard");
  }
  res.status(401).json({ error: "Invalid credentials" });
});
```

**JavaScript/TypeScript (fixed)**:
```typescript
import rateLimit from "express-rate-limit";

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: "Too many login attempts, please try again later",
});

app.post("/login", loginLimiter, async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });
  if (user && await bcrypt.compare(password, user.passwordHash)) {
    req.session.userId = user.id;
    return res.redirect("/dashboard");
  }
  res.status(401).json({ error: "Invalid credentials" });
});
```

**Java (vulnerable)**:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    User user = userRepository.findByUsername(request.getUsername());
    if (user != null && passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
        String token = jwtService.generateToken(user);
        return ResponseEntity.ok(new AuthResponse(token));
    }
    return ResponseEntity.status(401).body("Invalid credentials");
}
```

**Java (fixed)**:
```java
@PostMapping("/login")
@RateLimiter(name = "loginAttempts", fallbackMethod = "loginRateLimited")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    User user = userRepository.findByUsername(request.getUsername());
    if (user != null && passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
        loginAttemptService.resetAttempts(request.getUsername());
        String token = jwtService.generateToken(user);
        return ResponseEntity.ok(new AuthResponse(token));
    }
    loginAttemptService.recordFailure(request.getUsername());
    return ResponseEntity.status(401).body("Invalid credentials");
}
```

**Go (vulnerable)**:
```go
func LoginHandler(w http.ResponseWriter, r *http.Request) {
    username := r.FormValue("username")
    password := r.FormValue("password")
    user, err := store.FindUser(username)
    if err == nil && bcrypt.CompareHashAndPassword([]byte(user.Hash), []byte(password)) == nil {
        session, _ := sessionStore.Get(r, "session")
        session.Values["user_id"] = user.ID
        session.Save(r, w)
        http.Redirect(w, r, "/dashboard", http.StatusFound)
        return
    }
    http.Error(w, "Invalid credentials", http.StatusUnauthorized)
}
```

**Go (fixed)**:
```go
var loginLimiter = rate.NewLimiter(rate.Every(time.Minute/5), 5)

func LoginHandler(w http.ResponseWriter, r *http.Request) {
    if !loginLimiter.Allow() {
        http.Error(w, "Too many attempts", http.StatusTooManyRequests)
        return
    }
    username := r.FormValue("username")
    password := r.FormValue("password")
    user, err := store.FindUser(username)
    if err == nil && bcrypt.CompareHashAndPassword([]byte(user.Hash), []byte(password)) == nil {
        session, _ := sessionStore.Get(r, "session")
        session.Values["user_id"] = user.ID
        session.Save(r, w)
        http.Redirect(w, r, "/dashboard", http.StatusFound)
        return
    }
    http.Error(w, "Invalid credentials", http.StatusUnauthorized)
}
```

### Scanner Coverage

- **semgrep**: Limited coverage for missing rate limiting (structural pattern, not a code smell scanners typically detect)
- **Best detected by**: Claude analysis of route handlers and middleware chains

### False Positive Guidance

- Rate limiting may be applied at the infrastructure level (API gateway, WAF, reverse proxy) rather than in code. Check for comments or documentation referencing external rate limiting.
- Framework middleware (e.g., Django `axes`, Spring `resilience4j`) may be configured globally rather than per-route.

### Severity Criteria

- **HIGH**: Login endpoint with no rate limiting and no account lockout at any layer.
- **MEDIUM**: Rate limiting exists but is too permissive (>100 attempts per minute) or only applies to some auth endpoints.
- **LOW**: Rate limiting present but could be stricter; or password reset endpoint lacks independent limiting.

---

## Pattern 2: Weak Password Validation

### Description

Applications that accept passwords without enforcing minimum length, complexity, or
checking against known-breached password lists fail to protect users from weak
credential selection.

### Grep Heuristics

```
# Find password validation or signup handlers
password.*(valid|check|require|policy|strength|rule)
(min.?length|minLength).*(password|passwd)
(signup|register|create.?user|change.?password|reset.?password)
new.?password|confirm.?password|set.?password
```

Then check for adequate validation:
```
len\(.*password.*\)\s*[<>=]+\s*[0-9]
password\.length\s*[<>=]+\s*[0-9]
\.matches?\(.*[A-Z].*[a-z].*[0-9]
zxcvbn|haveibeenpwned|commonPasswords|blacklist|blocklist
```

If password acceptance has no length or complexity checks, flag it.

### Language Examples

**Python (vulnerable)**:
```python
def register_user(username, password):
    if not username or not password:
        raise ValueError("Username and password required")
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.users.insert({"username": username, "password": hashed})
```

**Python (fixed)**:
```python
import re

MIN_PASSWORD_LENGTH = 12

def validate_password(password):
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
    if password.lower() in COMMON_PASSWORDS:
        raise ValueError("Password is too common")
    if not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password):
        raise ValueError("Password must contain upper and lowercase letters")
    if not re.search(r'[0-9]', password):
        raise ValueError("Password must contain at least one digit")

def register_user(username, password):
    if not username or not password:
        raise ValueError("Username and password required")
    validate_password(password)
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.users.insert({"username": username, "password": hashed})
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
app.post("/register", async (req, res) => {
  const { email, password } = req.body;
  const hash = await bcrypt.hash(password, 10);
  await User.create({ email, passwordHash: hash });
  res.status(201).json({ message: "User created" });
});
```

**JavaScript/TypeScript (fixed)**:
```typescript
import { isStrongPassword } from "validator";

app.post("/register", async (req, res) => {
  const { email, password } = req.body;
  if (!isStrongPassword(password, { minLength: 12, minNumbers: 1, minUppercase: 1 })) {
    return res.status(400).json({ error: "Password does not meet strength requirements" });
  }
  const hash = await bcrypt.hash(password, 12);
  await User.create({ email, passwordHash: hash });
  res.status(201).json({ message: "User created" });
});
```

**Java (vulnerable)**:
```java
public void registerUser(String username, String password) {
    String hash = passwordEncoder.encode(password);
    userRepository.save(new User(username, hash));
}
```

**Java (fixed)**:
```java
public void registerUser(String username, String password) {
    if (password.length() < 12) {
        throw new WeakPasswordException("Password must be at least 12 characters");
    }
    if (!password.matches(".*[A-Z].*") || !password.matches(".*[a-z].*") || !password.matches(".*\\d.*")) {
        throw new WeakPasswordException("Password must contain upper, lower, and numeric characters");
    }
    if (commonPasswordService.isCommon(password)) {
        throw new WeakPasswordException("Password is too common");
    }
    String hash = passwordEncoder.encode(password);
    userRepository.save(new User(username, hash));
}
```

**Go (vulnerable)**:
```go
func RegisterHandler(w http.ResponseWriter, r *http.Request) {
    password := r.FormValue("password")
    hash, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    store.CreateUser(r.FormValue("username"), string(hash))
}
```

**Go (fixed)**:
```go
func validatePassword(password string) error {
    if len(password) < 12 {
        return errors.New("password must be at least 12 characters")
    }
    hasUpper := regexp.MustCompile(`[A-Z]`).MatchString(password)
    hasLower := regexp.MustCompile(`[a-z]`).MatchString(password)
    hasDigit := regexp.MustCompile(`[0-9]`).MatchString(password)
    if !hasUpper || !hasLower || !hasDigit {
        return errors.New("password must contain upper, lower, and numeric characters")
    }
    return nil
}

func RegisterHandler(w http.ResponseWriter, r *http.Request) {
    password := r.FormValue("password")
    if err := validatePassword(password); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    hash, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    store.CreateUser(r.FormValue("username"), string(hash))
}
```

### Scanner Coverage

- **semgrep**: Can detect some missing validation patterns with custom rules
- **bandit**: Does not check password policy
- **Best detected by**: Claude analysis of registration and password change flows

### False Positive Guidance

- Password policy may be enforced on the frontend (client-side validation). This is still a finding (server must validate too) but lower severity.
- Some applications delegate password policy to an identity provider (Auth0, Okta, Cognito). If the app uses an external IdP for registration, password policy is managed there.
- NIST SP 800-63B recommends minimum 8 characters with breached-password checking, but discourages arbitrary complexity rules. Flag absent length checks and missing breach checks, not necessarily the absence of complexity rules.

### Severity Criteria

- **HIGH**: No password validation at all -- any string accepted as a password.
- **MEDIUM**: Minimum length enforced but too short (<8 characters) or no check against common passwords.
- **LOW**: Reasonable length requirement but no breach-list check.

---

## Pattern 3: Password Stored with MD5/SHA1/Plain SHA256

### Description

Passwords hashed with MD5, SHA1, unsalted SHA256, or stored in plaintext can be
reversed with rainbow tables or GPU-accelerated cracking in seconds to minutes.
Passwords must use adaptive hashing algorithms: Argon2id, bcrypt, or scrypt.

### Grep Heuristics

```
# Weak hashing of passwords
hashlib\.(md5|sha1|sha256)\(.*password
MessageDigest\.getInstance\(.*(MD5|SHA-1|SHA1|SHA-256)
md5\(.*password|sha1\(.*password|sha256\(.*password
crypto\.(createHash|MD5|SHA1)\(
hash\(.*(md5|sha1|sha256).*password
DigestUtils\.(md5|sha1|sha256)
\.update\(.*password.*\)\.digest

# Plaintext password storage
password\s*[:=]\s*(request|req|params|form|body)\b
(insert|save|store|create).*password.*[^hash]
\.password\s*=\s*.*password\b(?!.*hash|.*bcrypt|.*argon|.*scrypt)
```

### Language Examples

**Python (vulnerable)**:
```python
import hashlib

def create_user(username, password):
    password_hash = hashlib.md5(password.encode()).hexdigest()
    db.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
```

**Python (fixed)**:
```python
import bcrypt

def create_user(username, password):
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    db.execute("INSERT INTO users VALUES (?, ?)", (username, password_hash))
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
import crypto from "crypto";

function hashPassword(password: string): string {
  return crypto.createHash("sha1").update(password).digest("hex");
}
```

**JavaScript/TypeScript (fixed)**:
```typescript
import bcrypt from "bcrypt";

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12);
}
```

**Java (vulnerable)**:
```java
MessageDigest md = MessageDigest.getInstance("MD5");
byte[] hash = md.digest(password.getBytes());
String passwordHash = DatatypeConverter.printHexBinary(hash);
```

**Java (fixed)**:
```java
BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
String passwordHash = encoder.encode(password);
```

**Go (vulnerable)**:
```go
h := sha256.New()
h.Write([]byte(password))
hash := hex.EncodeToString(h.Sum(nil))
```

**Go (fixed)**:
```go
hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
if err != nil {
    return err
}
```

### Scanner Coverage

- **semgrep**: Good coverage for weak hash detection across languages
- **bandit**: Detects `hashlib.md5`, `hashlib.sha1` usage in Python (B303, B324)
- **gosec**: Detects weak crypto in Go (G401, G501)
- **gitleaks**: Not applicable (detects secrets, not hash algorithm choice)

### False Positive Guidance

- MD5/SHA1/SHA256 used for non-password purposes (checksums, cache keys, content hashing) are not authentication vulnerabilities. Check the variable name and context -- only flag when the input is clearly a password or credential.
- Some code uses weak hashing for legacy compatibility with a migration path in place. Note as lower severity if migration evidence exists.

### Severity Criteria

- **CRITICAL**: Passwords stored in plaintext or with unsalted MD5/SHA1.
- **HIGH**: Passwords hashed with SHA256 without a salt, or with a static salt.
- **MEDIUM**: Using bcrypt with a low work factor (<10) or PBKDF2 with insufficient iterations (<100,000).

---

## Pattern 4: Session ID in URL Parameters

### Description

Exposing session identifiers in URL query parameters or path segments leaks them
through browser history, referrer headers, server logs, proxy logs, and shared links.

### Grep Heuristics

```
# Session ID passed as URL parameter
[?&](session_?id|sid|token|auth_?token|jwt|access_?token)=
redirect.*[?&].*(session|token|sid)=
window\.location.*[?&].*(session|token|sid)=
url.*[?&].*(session|token|sid|jsessionid)=
href.*[?&].*(session|token|sid)=
;jsessionid=
```

### Language Examples

**Python (vulnerable)**:
```python
@app.route("/dashboard")
def dashboard():
    session_id = request.args.get("sid")
    user = get_user_by_session(session_id)
    return render_template("dashboard.html", user=user)
```

**Python (fixed)**:
```python
@app.route("/dashboard")
def dashboard():
    session_id = request.cookies.get("session_id")
    if not session_id:
        return redirect("/login")
    user = get_user_by_session(session_id)
    return render_template("dashboard.html", user=user)
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
app.get("/api/data", (req, res) => {
  const token = req.query.auth_token;
  if (!verifyToken(token)) return res.status(401).send("Unauthorized");
  res.json(getData());
});
```

**JavaScript/TypeScript (fixed)**:
```typescript
app.get("/api/data", (req, res) => {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token || !verifyToken(token)) return res.status(401).send("Unauthorized");
  res.json(getData());
});
```

**Java (vulnerable)**:
```java
@GetMapping("/dashboard")
public String dashboard(@RequestParam("jsessionid") String sessionId, Model model) {
    User user = sessionService.getUser(sessionId);
    model.addAttribute("user", user);
    return "dashboard";
}
```

**Java (fixed)**:
```java
@GetMapping("/dashboard")
public String dashboard(HttpSession session, Model model) {
    User user = (User) session.getAttribute("user");
    if (user == null) return "redirect:/login";
    model.addAttribute("user", user);
    return "dashboard";
}
```

**Go (vulnerable)**:
```go
func DashboardHandler(w http.ResponseWriter, r *http.Request) {
    sessionID := r.URL.Query().Get("sid")
    user, err := store.GetSession(sessionID)
    // ...
}
```

**Go (fixed)**:
```go
func DashboardHandler(w http.ResponseWriter, r *http.Request) {
    cookie, err := r.Cookie("session_id")
    if err != nil {
        http.Redirect(w, r, "/login", http.StatusFound)
        return
    }
    user, err := store.GetSession(cookie.Value)
    // ...
}
```

### Scanner Coverage

- **semgrep**: Can detect session-related query parameters with custom rules
- **Best detected by**: Claude analysis of URL construction and session retrieval patterns

### False Positive Guidance

- OAuth callback flows legitimately receive authorization codes and state tokens as URL parameters. These are short-lived, single-use codes, not session identifiers. Do not flag OAuth `code` or `state` parameters.
- Password reset tokens in URLs are common but should be flagged as **LOW** since they are one-time-use (though they should still use POST forms when possible).

### Severity Criteria

- **HIGH**: Long-lived session tokens or JWTs passed as URL query parameters in production routes.
- **MEDIUM**: Short-lived tokens passed as URL parameters without additional protections (referrer policy, HTTPS-only).
- **LOW**: One-time-use tokens (email verification, password reset) in URL parameters.

---

## Pattern 5: Missing Session Regeneration After Login

### Description

When a session identifier is not regenerated after successful authentication, an
attacker who knows the pre-authentication session ID (e.g., from a public terminal
or XSS) retains access after the victim logs in (session fixation).

### Grep Heuristics

```
# Find successful login code paths
(session|req\.session)\[.*(user|auth|logged)
session\.(user_?id|authenticated|logged_?in)\s*=
req\.session\.\w+\s*=.*user
login.*success|authenticated.*true
```

Then check for session regeneration nearby:
```
session\.regenerate|session\.cycle|req\.session\.regenerate
session\.invalidate|request\.changeSessionId
session_regenerate_id|regenerate_session
newSession|rotate.?session|reset.?session
```

If login success is found without session regeneration within 10 lines, flag it.

### Language Examples

**Python (vulnerable)**:
```python
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["username"], request.form["password"])
    if user:
        session["user_id"] = user.id
        session["authenticated"] = True
        return redirect("/dashboard")
```

**Python (fixed)**:
```python
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.form["username"], request.form["password"])
    if user:
        session.clear()  # Destroy old session data
        session["user_id"] = user.id
        session["authenticated"] = True
        # Flask regenerates session ID when session is modified after clear
        return redirect("/dashboard")
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body.email, req.body.password);
  if (user) {
    req.session.userId = user.id;
    return res.redirect("/dashboard");
  }
  res.status(401).send("Invalid");
});
```

**JavaScript/TypeScript (fixed)**:
```typescript
app.post("/login", async (req, res) => {
  const user = await authenticate(req.body.email, req.body.password);
  if (user) {
    req.session.regenerate((err) => {
      if (err) return res.status(500).send("Session error");
      req.session.userId = user.id;
      res.redirect("/dashboard");
    });
    return;
  }
  res.status(401).send("Invalid");
});
```

**Java (vulnerable)**:
```java
@PostMapping("/login")
public String login(@RequestParam String username, @RequestParam String password,
                    HttpSession session) {
    User user = authService.authenticate(username, password);
    if (user != null) {
        session.setAttribute("user", user);
        return "redirect:/dashboard";
    }
    return "login";
}
```

**Java (fixed)**:
```java
@PostMapping("/login")
public String login(@RequestParam String username, @RequestParam String password,
                    HttpServletRequest request) {
    User user = authService.authenticate(username, password);
    if (user != null) {
        request.changeSessionId();  // Servlet 3.1+
        HttpSession session = request.getSession();
        session.setAttribute("user", user);
        return "redirect:/dashboard";
    }
    return "login";
}
```

**Go (vulnerable)**:
```go
func LoginHandler(w http.ResponseWriter, r *http.Request) {
    user, err := authenticate(r.FormValue("username"), r.FormValue("password"))
    if err == nil {
        session, _ := sessionStore.Get(r, "session")
        session.Values["user_id"] = user.ID
        session.Save(r, w)
        http.Redirect(w, r, "/dashboard", http.StatusFound)
    }
}
```

**Go (fixed)**:
```go
func LoginHandler(w http.ResponseWriter, r *http.Request) {
    user, err := authenticate(r.FormValue("username"), r.FormValue("password"))
    if err == nil {
        oldSession, _ := sessionStore.Get(r, "session")
        oldSession.Options.MaxAge = -1  // Invalidate old session
        oldSession.Save(r, w)
        newSession, _ := sessionStore.New(r, "session")  // New session ID
        newSession.Values["user_id"] = user.ID
        newSession.Save(r, w)
        http.Redirect(w, r, "/dashboard", http.StatusFound)
    }
}
```

### Scanner Coverage

- **semgrep**: Limited. Some rules for specific frameworks (e.g., Java Servlet session fixation)
- **Best detected by**: Claude analysis tracing session lifecycle around login

### False Positive Guidance

- Some frameworks regenerate sessions automatically on login (e.g., Spring Security with `sessionFixation().changeSessionId()` configured globally, Django's `login()` function). Check framework configuration before flagging.
- If session data is entirely server-side and the session cookie has `HttpOnly + Secure + SameSite=Strict`, the risk is lower (but regeneration is still best practice).

### Severity Criteria

- **HIGH**: No session regeneration after login in a web application that uses cookie-based sessions.
- **MEDIUM**: Session regeneration missing on privilege escalation (e.g., switching from user to admin role) but present on initial login.
- **LOW**: Framework handles regeneration automatically but the explicit call is missing (defense-in-depth concern).

---

## Pattern 6: JWT with None Algorithm Accepted

### Description

JWT libraries that accept `alg: "none"` allow attackers to create unsigned tokens that
bypass signature verification entirely. The attacker simply removes the signature and
sets the algorithm to "none" to forge any claims.

### Grep Heuristics

```
# JWT verification without algorithm restriction
jwt\.(verify|decode)\(.*\{
algorithms\s*[:=]\s*\[.*none
JWT\.decode\(.*verify\s*[:=]\s*false
jwt\.decode\(.*options.*verify.*false
verify\s*[:=]\s*false.*jwt
JsonWebToken|jose|pyjwt|jwt-go|golang-jwt
nimbus-jose|java-jwt|jjwt
```

Specifically look for:
```
# Missing algorithm restriction
jwt\.verify\([^)]*\)(?!.*algorithms)
jwt\.decode\([^)]*\)(?!.*algorithms)
algorithms.*none|"none"|'none'
verify.*false|verify_signature.*false
```

### Language Examples

**Python (vulnerable)**:
```python
import jwt

def verify_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256", "none"])
    return payload
```

**Python (fixed)**:
```python
import jwt

def verify_token(token):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
import jwt from "jsonwebtoken";

function verifyToken(token: string) {
  return jwt.verify(token, SECRET_KEY, { algorithms: ["HS256", "none"] });
}
```

**JavaScript/TypeScript (fixed)**:
```typescript
import jwt from "jsonwebtoken";

function verifyToken(token: string) {
  return jwt.verify(token, SECRET_KEY, { algorithms: ["HS256"] });
}
```

**Java (vulnerable)**:
```java
// Using nimbus-jose-jwt without algorithm constraint
JWSObject jwsObject = JWSObject.parse(token);
// No algorithm verification — accepts whatever alg the token specifies
jwsObject.verify(new MACVerifier(sharedSecret));
```

**Java (fixed)**:
```java
JWSObject jwsObject = JWSObject.parse(token);
if (jwsObject.getHeader().getAlgorithm() != JWSAlgorithm.HS256) {
    throw new SecurityException("Unexpected JWT algorithm: " + jwsObject.getHeader().getAlgorithm());
}
jwsObject.verify(new MACVerifier(sharedSecret));
```

**Go (vulnerable)**:
```go
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    return secretKey, nil
})
```

**Go (fixed)**:
```go
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
        return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
    }
    return secretKey, nil
})
```

### Scanner Coverage

- **semgrep**: Good coverage. Rules for JWT `none` algorithm and missing algorithm validation in Python, JS, Java, Go
- **bandit**: Does not specifically check JWT issues

### False Positive Guidance

- Some JWT libraries have removed support for `alg: "none"` by default in recent versions. Check the library version before escalating.
- Token decoding without verification (e.g., reading claims from an already-verified token, or inspecting tokens for logging) may intentionally skip verification. Check if the token was verified earlier in the flow.

### Severity Criteria

- **CRITICAL**: JWT verification explicitly allows `alg: "none"` or skips signature verification.
- **HIGH**: JWT parsing does not restrict allowed algorithms, letting the token's own `alg` header dictate which algorithm is used (algorithm confusion attacks).
- **MEDIUM**: JWT library is outdated and known to have `none` algorithm vulnerabilities, but code does not explicitly allow it.

---

## Pattern 7: Hardcoded JWT Secrets

### Description

JWT signing secrets embedded directly in source code are exposed to anyone with
repository access. Secrets in code cannot be rotated without redeployment and
are often committed to version control history permanently.

### Grep Heuristics

```
# Hardcoded secret assignments near JWT usage
(secret|SECRET|jwt.?secret|JWT_SECRET|signing.?key|SIGNING_KEY)\s*[:=]\s*["'][^"']{8,}["']
(secret_key|SECRET_KEY|private.?key|PRIVATE_KEY)\s*[:=]\s*["'][^"']{8,}["']
jwt\.(sign|encode)\(.*["'][a-zA-Z0-9+/=]{16,}["']
\.sign\(.*["']secret["']
HMAC.*["'][a-zA-Z0-9+/=]{16,}["']
```

### Language Examples

**Python (vulnerable)**:
```python
import jwt

SECRET_KEY = "my-super-secret-jwt-key-12345"

def create_token(user_id):
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
```

**Python (fixed)**:
```python
import jwt
import os

SECRET_KEY = os.environ["JWT_SECRET_KEY"]

def create_token(user_id):
    return jwt.encode({"user_id": user_id}, SECRET_KEY, algorithm="HS256")
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
import jwt from "jsonwebtoken";

const JWT_SECRET = "change-me-in-production-please";

function signToken(userId: string): string {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: "24h" });
}
```

**JavaScript/TypeScript (fixed)**:
```typescript
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET;
if (!JWT_SECRET) throw new Error("JWT_SECRET environment variable is required");

function signToken(userId: string): string {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: "24h" });
}
```

**Java (vulnerable)**:
```java
public class JwtUtil {
    private static final String SECRET = "myHardcodedSecretKey123456789";

    public String generateToken(UserDetails user) {
        return Jwts.builder()
            .setSubject(user.getUsername())
            .signWith(SignatureAlgorithm.HS256, SECRET)
            .compact();
    }
}
```

**Java (fixed)**:
```java
@Component
public class JwtUtil {
    @Value("${jwt.secret}")
    private String secret;

    public String generateToken(UserDetails user) {
        return Jwts.builder()
            .setSubject(user.getUsername())
            .signWith(SignatureAlgorithm.HS256, secret)
            .compact();
    }
}
```

**Go (vulnerable)**:
```go
var jwtSecret = []byte("hardcoded-secret-key-for-jwt")

func GenerateToken(userID int) (string, error) {
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "user_id": userID,
    })
    return token.SignedString(jwtSecret)
}
```

**Go (fixed)**:
```go
var jwtSecret = []byte(os.Getenv("JWT_SECRET"))

func init() {
    if len(jwtSecret) == 0 {
        log.Fatal("JWT_SECRET environment variable is required")
    }
}

func GenerateToken(userID int) (string, error) {
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
        "user_id": userID,
    })
    return token.SignedString(jwtSecret)
}
```

### Scanner Coverage

- **gitleaks**: Excellent. Detects hardcoded secrets, tokens, and keys using entropy + pattern matching
- **trufflehog**: Excellent. Detects with optional live verification
- **semgrep**: Good. Rules for hardcoded secrets in JWT contexts
- **bandit**: Detects hardcoded passwords in Python (B105, B106, B107)

### False Positive Guidance

- Test files and example/documentation code often contain placeholder secrets like `"test-secret"` or `"changeme"`. Flag as **LOW** with a note unless the file is clearly production code.
- Environment variable fallbacks with a default value (e.g., `os.getenv("SECRET", "dev-fallback")`) should be flagged as **MEDIUM** -- the fallback may leak into production.
- Configuration template files (`.env.example`, `config.sample.yaml`) with placeholder values are not findings.

### Severity Criteria

- **CRITICAL**: Production JWT secret hardcoded in non-test source code, especially if the repository is public or has broad access.
- **HIGH**: Secret hardcoded as a default/fallback value that could reach production.
- **MEDIUM**: Secret in test files but identical to or suggesting the production secret pattern.
- **LOW**: Obvious placeholder in example or test code (e.g., `"test"`, `"secret"`, `"changeme"`).
