# Detection Patterns: Security Logging and Monitoring Failures

Patterns for detecting A09:2021 vulnerabilities. Each pattern includes search
heuristics, language examples, scanner coverage, and false positive guidance.

---

## Pattern 1: Missing Logging on Authentication Events

**Description**: Authentication operations (login, failed login, logout, password
reset, MFA challenge) that produce no audit log entry. Without logging these events,
organizations cannot detect credential stuffing, brute force, or account takeover.

**Search Heuristics**:
```
Grep for authentication functions, then verify log calls are present:
  Pattern: def (login|authenticate|sign_in|verify_password|reset_password)
  Pattern: async (login|authenticate|signIn|verifyPassword|resetPassword)
  Pattern: @(PostMapping|RequestMapping).*(/login|/auth|/signin|/reset)
  Pattern: func.*(Login|Authenticate|SignIn|VerifyPassword|ResetPassword)

Then check if the function body contains log/logger calls:
  Absence of: log\.|logger\.|logging\.|console\.log|log\.Info|log\.Warn|slog\.
```

**Language Examples**:

Python -- Vulnerable:
```python
def login(request):
    user = authenticate(request.POST['username'], request.POST['password'])
    if user is None:
        return HttpResponse('Invalid credentials', status=401)
    login_user(request, user)
    return redirect('/dashboard')
```

Python -- Fixed:
```python
def login(request):
    username = request.POST['username']
    user = authenticate(username, request.POST['password'])
    if user is None:
        logger.warning("Failed login attempt for user=%s ip=%s", username, get_client_ip(request))
        return HttpResponse('Invalid credentials', status=401)
    logger.info("Successful login for user=%s ip=%s", username, get_client_ip(request))
    login_user(request, user)
    return redirect('/dashboard')
```

JavaScript/TypeScript -- Vulnerable:
```typescript
async function login(req: Request, res: Response) {
  const user = await User.findOne({ email: req.body.email });
  if (!user || !await bcrypt.compare(req.body.password, user.passwordHash)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  const token = jwt.sign({ id: user.id }, SECRET);
  res.json({ token });
}
```

JavaScript/TypeScript -- Fixed:
```typescript
async function login(req: Request, res: Response) {
  const { email } = req.body;
  const user = await User.findOne({ email });
  if (!user || !await bcrypt.compare(req.body.password, user.passwordHash)) {
    logger.warn('Failed login attempt', { email, ip: req.ip, timestamp: new Date() });
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  logger.info('Successful login', { userId: user.id, ip: req.ip, timestamp: new Date() });
  const token = jwt.sign({ id: user.id }, SECRET);
  res.json({ token });
}
```

Java -- Vulnerable:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request) {
    Authentication auth = authManager.authenticate(
        new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword()));
    String token = jwtUtil.generateToken(auth);
    return ResponseEntity.ok(new AuthResponse(token));
}
```

Java -- Fixed:
```java
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginRequest request, HttpServletRequest httpRequest) {
    try {
        Authentication auth = authManager.authenticate(
            new UsernamePasswordAuthenticationToken(request.getUsername(), request.getPassword()));
        String token = jwtUtil.generateToken(auth);
        logger.info("Successful login: user={} ip={}", request.getUsername(), httpRequest.getRemoteAddr());
        return ResponseEntity.ok(new AuthResponse(token));
    } catch (AuthenticationException e) {
        logger.warn("Failed login attempt: user={} ip={}", request.getUsername(), httpRequest.getRemoteAddr());
        return ResponseEntity.status(401).body("Invalid credentials");
    }
}
```

Go -- Vulnerable:
```go
func LoginHandler(w http.ResponseWriter, r *http.Request) {
    var creds Credentials
    json.NewDecoder(r.Body).Decode(&creds)
    user, err := db.AuthenticateUser(creds.Username, creds.Password)
    if err != nil {
        http.Error(w, "Invalid credentials", http.StatusUnauthorized)
        return
    }
    token := generateJWT(user.ID)
    json.NewEncoder(w).Encode(map[string]string{"token": token})
}
```

Go -- Fixed:
```go
func LoginHandler(w http.ResponseWriter, r *http.Request) {
    var creds Credentials
    json.NewDecoder(r.Body).Decode(&creds)
    user, err := db.AuthenticateUser(creds.Username, creds.Password)
    if err != nil {
        slog.Warn("Failed login attempt", "user", creds.Username, "ip", r.RemoteAddr)
        http.Error(w, "Invalid credentials", http.StatusUnauthorized)
        return
    }
    slog.Info("Successful login", "user_id", user.ID, "ip", r.RemoteAddr)
    token := generateJWT(user.ID)
    json.NewEncoder(w).Encode(map[string]string{"token": token})
}
```

**Scanner Coverage**: No scanner reliably detects missing logging. This is an
architectural gap that requires Claude analysis of function bodies.

**False Positive Guidance**: Some applications use event-driven architectures where
authentication events are published to a bus and logged by a separate subscriber.
Check for event emission (e.g., `emit('auth.login.success')`) as an alternative to
direct logging. Also check for decorator-based or AOP-based logging that wraps the
function externally.

**Severity Criteria**:
- **high**: No logging on any authentication path (login, failed login, password reset)
- **medium**: Partial logging (e.g., successful logins logged but failures are not)
- **low**: Logging present but missing context (no IP address, no timestamp)

---

## Pattern 2: Sensitive Data in Log Statements

**Description**: Passwords, authentication tokens, API keys, credit card numbers,
Social Security numbers, or other PII written into log output. This data persists
in log storage and may be accessible to operations staff, log aggregation systems,
or attackers who gain access to log files.

**Search Heuristics**:
```
Grep for log calls containing sensitive variable names:
  Pattern: (log|logger|logging|console)\..*(password|passwd|pwd|secret|token|api.?key|credit.?card|ssn|authorization)
  Pattern: (log|logger|logging|console)\..*(request\.body|req\.body|request\.headers)
  Pattern: (log|logger)\.(debug|info|warn|error).*(%s|%v|\{}).*password
  Pattern: print\(.*password
```

**Language Examples**:

Python -- Vulnerable:
```python
logger.debug("User login attempt: username=%s password=%s", username, password)
logger.info("API request: headers=%s", request.headers)
```

Python -- Fixed:
```python
logger.debug("User login attempt: username=%s", username)
logger.info("API request: endpoint=%s method=%s", request.path, request.method)
```

JavaScript/TypeScript -- Vulnerable:
```typescript
console.log('Auth request body:', JSON.stringify(req.body));
logger.info(`Token generated: ${token}`);
logger.debug('Request headers:', req.headers);
```

JavaScript/TypeScript -- Fixed:
```typescript
console.log('Auth request for:', req.body.email);
logger.info('Token generated for userId:', userId);
logger.debug('Request path:', req.path);
```

Java -- Vulnerable:
```java
logger.info("Processing payment for card: {}", creditCardNumber);
logger.debug("User details: {}", userDto);  // toString() includes password
```

Java -- Fixed:
```java
logger.info("Processing payment for card ending: {}", maskCard(creditCardNumber));
logger.debug("User details: id={} email={}", userDto.getId(), userDto.getEmail());
```

Go -- Vulnerable:
```go
slog.Info("Authenticating user", "credentials", creds)  // struct includes password
log.Printf("Request: %+v", req)  // logs full request including auth headers
```

Go -- Fixed:
```go
slog.Info("Authenticating user", "username", creds.Username)
log.Printf("Request: method=%s path=%s", req.Method, req.URL.Path)
```

**Scanner Coverage**: semgrep has some rules for detecting sensitive data in log
statements. Bandit detects `logging.debug()` with sensitive variable names in Python.
Coverage is partial -- scanners catch obvious cases but miss indirect references.

**False Positive Guidance**: Variables named `password_policy`, `token_expiry`, or
`secret_version` are not sensitive data. Check whether the variable actually holds
a credential value or merely references a credential-related configuration. Also,
masked/redacted values (e.g., `****last4`) are safe to log.

**Severity Criteria**:
- **critical**: Plaintext passwords or full tokens logged at INFO or higher in production
- **high**: API keys, credit card numbers, or SSNs in logs
- **medium**: Full request bodies or headers logged (may contain auth data)
- **low**: Sensitive data in DEBUG-level logs that are disabled in production

---

## Pattern 3: Log Injection via User Input

**Description**: User-controlled input passed directly into log format strings or
log messages without sanitization. Attackers can inject fake log entries, newlines
to forge log records, or special characters to exploit log parsing systems.

**Search Heuristics**:
```
Grep for log calls using user input directly:
  Pattern: logger\..*(req\.(body|params|query|headers)\[|request\.(GET|POST|args|form)\[)
  Pattern: log\.(info|warn|error|debug)\(.*\+.*(req|request|input|user)
  Pattern: logger\..*(format|sprintf|f").*request
  Pattern: log\.Printf\(.*%s.*(r\.(Form|URL|Header|Body))
```

**Language Examples**:

Python -- Vulnerable:
```python
logger.info(f"Search query: {request.GET['q']}")
logger.info("User-Agent: %s" % request.headers['User-Agent'])
```

Python -- Fixed:
```python
logger.info("Search query: %s", sanitize_log(request.GET.get('q', '')))
# Or use structured logging that auto-encodes:
structlog.get_logger().info("search_query", query=request.GET.get('q', ''))
```

JavaScript/TypeScript -- Vulnerable:
```typescript
logger.info(`User search: ${req.query.q}`);
logger.info('User input: ' + req.body.comment);
```

JavaScript/TypeScript -- Fixed:
```typescript
logger.info('User search', { query: sanitizeForLog(req.query.q) });
// Or use structured logging (pino, winston with JSON format):
logger.info({ query: req.query.q }, 'User search');
```

Java -- Vulnerable:
```java
logger.info("Search: " + request.getParameter("q"));
logger.info(String.format("User input: %s", request.getParameter("comment")));
```

Java -- Fixed:
```java
logger.info("Search: {}", LogSanitizer.sanitize(request.getParameter("q")));
// SLF4J parameterized logging is safer but still needs newline sanitization
```

Go -- Vulnerable:
```go
log.Printf("Query: %s", r.URL.Query().Get("q"))
slog.Info("User input", "data", r.FormValue("comment"))
```

Go -- Fixed:
```go
log.Printf("Query: %s", sanitizeLog(r.URL.Query().Get("q")))
slog.Info("User input", "data", sanitizeLog(r.FormValue("comment")))
```

**Scanner Coverage**: semgrep has rules for log injection in several languages,
particularly for Java (CWE-117) and Python. Coverage is moderate -- catches direct
string concatenation but may miss indirect injection through variables.

**False Positive Guidance**: Structured logging frameworks (e.g., structlog, pino,
slog, logback with JSON layout) that encode values as JSON fields are generally safe
from CRLF-based log injection, though they can still produce excessively large log
entries from user input. If the project uses structured logging throughout, lower
confidence on log injection findings.

**Severity Criteria**:
- **high**: User input in log format strings in authentication/authorization paths
- **medium**: User input logged without sanitization in general application code
- **low**: User input in structured logging fields (lower injection risk)

---

## Pattern 4: Missing Logging on Access Control Failures

**Description**: Authorization denials, forbidden access attempts, and permission
check failures that are not logged. Without these logs, organizations cannot detect
privilege escalation attempts, enumeration attacks, or unauthorized access patterns.

**Search Heuristics**:
```
Grep for authorization check patterns and verify logging is present:
  Pattern: (403|Forbidden|Unauthorized|AccessDenied|PermissionDenied)
  Pattern: (is_authorized|has_permission|check_permission|authorize|canAccess).*return false
  Pattern: if.*(!|not).*(authorized|permitted|allowed|has_role|has_permission)
  Pattern: @(PreAuthorize|Secured|RolesAllowed)

Then check if the denial branch contains a log call.
```

**Language Examples**:

Python -- Vulnerable:
```python
def delete_user(request, user_id):
    if not request.user.is_admin:
        return HttpResponseForbidden()
    # ... delete logic
```

Python -- Fixed:
```python
def delete_user(request, user_id):
    if not request.user.is_admin:
        logger.warning(
            "Access denied: user=%s attempted admin action=delete_user target=%s ip=%s",
            request.user.id, user_id, get_client_ip(request)
        )
        return HttpResponseForbidden()
    # ... delete logic
```

JavaScript/TypeScript -- Vulnerable:
```typescript
if (!user.roles.includes('admin')) {
  return res.status(403).json({ error: 'Forbidden' });
}
```

JavaScript/TypeScript -- Fixed:
```typescript
if (!user.roles.includes('admin')) {
  logger.warn('Access denied', {
    userId: user.id, requiredRole: 'admin', action: req.method + ' ' + req.path, ip: req.ip
  });
  return res.status(403).json({ error: 'Forbidden' });
}
```

Java -- Vulnerable:
```java
if (!SecurityContext.hasRole(user, Role.ADMIN)) {
    throw new AccessDeniedException("Insufficient privileges");
}
```

Java -- Fixed:
```java
if (!SecurityContext.hasRole(user, Role.ADMIN)) {
    logger.warn("Access denied: user={} role_required=ADMIN action={}", user.getId(), actionName);
    throw new AccessDeniedException("Insufficient privileges");
}
```

Go -- Vulnerable:
```go
if !user.HasPermission("admin") {
    http.Error(w, "Forbidden", http.StatusForbidden)
    return
}
```

Go -- Fixed:
```go
if !user.HasPermission("admin") {
    slog.Warn("Access denied", "user_id", user.ID, "required_perm", "admin", "path", r.URL.Path)
    http.Error(w, "Forbidden", http.StatusForbidden)
    return
}
```

**Scanner Coverage**: No scanner reliably detects missing logging in authorization
denial paths. This requires Claude analysis of the control flow.

**False Positive Guidance**: Some frameworks (e.g., Spring Security, Django REST
Framework) have built-in logging for access denials at the middleware level. Check
for framework-level audit logging configuration before flagging individual handlers.
Also check for global exception handlers that log AccessDeniedException.

**Severity Criteria**:
- **high**: No logging on any access control denial path across the application
- **medium**: Some authorization paths log denials but others do not
- **low**: Logging present but missing context (no user identity, no target resource)

---

## Pattern 5: No Centralized Logging Configuration

**Description**: Logging set up ad-hoc per file with inconsistent format, level, or
destination configuration. Without centralized logging, log output is fragmented,
difficult to search, and likely to miss security events.

**Search Heuristics**:
```
Check for centralized logging setup:
  Pattern: logging\.config|logging\.basicConfig|winston\.createLogger|pino\(|bunyan\.createLogger
  Pattern: logback\.xml|log4j2?\.(xml|properties|yaml)|logging\.properties
  Pattern: LOG_LEVEL|LOGGING|log_config|logger_config

Check for ad-hoc logging (negative signal):
  Pattern: print\(|console\.log\(|System\.out\.print|fmt\.Print
  Pattern: logging\.getLogger\(__name__\)  (many instances = no centralized config)
```

**Language Examples**:

Python -- Vulnerable:
```python
# scattered across multiple files with no config
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
```

Python -- Fixed:
```python
# config/logging.py - centralized configuration
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'json': {'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                 'format': '%(asctime)s %(name)s %(levelname)s %(message)s'}
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'json'},
        'remote': {'class': 'logging.handlers.SysLogHandler',
                   'address': ('logs.example.com', 514), 'formatter': 'json'}
    },
    'root': {'level': 'INFO', 'handlers': ['console', 'remote']}
}
logging.config.dictConfig(LOGGING_CONFIG)
```

JavaScript/TypeScript -- Vulnerable:
```typescript
// Different files using different approaches
console.log('User logged in');                    // file1.ts
const debug = require('debug')('app');            // file2.ts
const logger = new winston.Logger({ /* ... */ }); // file3.ts
```

JavaScript/TypeScript -- Fixed:
```typescript
// lib/logger.ts - single shared logger
import pino from 'pino';
export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'production'
    ? { target: 'pino-transport-cloud-logging' }
    : { target: 'pino-pretty' }
});
```

Java -- Vulnerable:
```java
// No logback.xml or log4j2.xml present
// Multiple files using System.out:
System.out.println("User logged in: " + username);
```

Java -- Fixed:
```java
// src/main/resources/logback.xml
// Centralized config with JSON format and remote appender
// All classes use: private static final Logger logger = LoggerFactory.getLogger(MyClass.class);
```

Go -- Vulnerable:
```go
// Scattered across files
log.Println("User logged in")          // file1.go
fmt.Fprintf(os.Stderr, "Error: %v", e) // file2.go
```

Go -- Fixed:
```go
// internal/logger/logger.go - centralized structured logger
var Logger = slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
}))
```

**Scanner Coverage**: No scanner detects the absence of centralized logging
configuration. This is an architectural concern that requires codebase-level analysis.

**False Positive Guidance**: Microservices and small CLI tools may legitimately use
simple logging (e.g., Go's `log` package with defaults). Scale expectations to
project size. Also, some frameworks provide centralized logging by convention (e.g.,
Rails logger, Django logging settings) even without an explicit config file.

**Severity Criteria**:
- **medium**: No centralized logging configuration in a production web application
- **low**: Inconsistent logging across modules but some configuration exists

---

## Pattern 6: Silent Error Swallowing in Catch Blocks

**Description**: Exception/error catch blocks that discard errors without logging,
re-throwing, or otherwise recording them. Silent error swallowing hides security
failures and can mask active attacks.

**Search Heuristics**:
```
Grep for empty or comment-only catch blocks:
  Pattern: except.*:\s*$\s*(pass|\.\.\.|\s*#)
  Pattern: catch\s*\(.*\)\s*\{\s*\}
  Pattern: catch\s*\(.*\)\s*\{\s*//
  Pattern: catch\s*\(.*\)\s*\{\s*/\*
  Pattern: if err != nil \{\s*\}
  Pattern: if err != nil \{\s*return nil
  Pattern: _ = someFunction\(\)  (Go: discarding error)
```

**Language Examples**:

Python -- Vulnerable:
```python
try:
    verify_user_token(token)
except Exception:
    pass

try:
    check_permissions(user, resource)
except PermissionError:
    ...  # TODO: handle this later
```

Python -- Fixed:
```python
try:
    verify_user_token(token)
except Exception as e:
    logger.error("Token verification failed: %s", e, exc_info=True)
    raise AuthenticationError("Invalid token") from e

try:
    check_permissions(user, resource)
except PermissionError as e:
    logger.warning("Permission denied: user=%s resource=%s", user.id, resource.id)
    raise
```

JavaScript/TypeScript -- Vulnerable:
```typescript
try {
  await validateApiKey(apiKey);
} catch (e) {
  // ignore
}

try {
  await processPayment(order);
} catch (err) {}
```

JavaScript/TypeScript -- Fixed:
```typescript
try {
  await validateApiKey(apiKey);
} catch (e) {
  logger.error('API key validation failed', { error: e.message, key: maskKey(apiKey) });
  throw new UnauthorizedError('Invalid API key');
}

try {
  await processPayment(order);
} catch (err) {
  logger.error('Payment processing failed', { orderId: order.id, error: err.message });
  throw err;
}
```

Java -- Vulnerable:
```java
try {
    authenticateUser(credentials);
} catch (AuthenticationException e) {
    // do nothing
}
```

Java -- Fixed:
```java
try {
    authenticateUser(credentials);
} catch (AuthenticationException e) {
    logger.warn("Authentication failed for user: {}", credentials.getUsername(), e);
    throw e;
}
```

Go -- Vulnerable:
```go
token, _ := jwt.Parse(tokenString, keyFunc)  // error discarded
_ = db.RecordAuditEvent(event)                // audit failure silenced
```

Go -- Fixed:
```go
token, err := jwt.Parse(tokenString, keyFunc)
if err != nil {
    slog.Error("JWT parse failed", "error", err)
    return nil, fmt.Errorf("invalid token: %w", err)
}
if err := db.RecordAuditEvent(event); err != nil {
    slog.Error("Audit event recording failed", "event", event.Type, "error", err)
    // Consider whether to fail the operation or continue
}
```

**Scanner Coverage**: semgrep and bandit can detect some empty catch blocks.
Go linters (errcheck, golangci-lint) detect discarded errors. Coverage is moderate
for the syntactic pattern but does not assess whether the swallowed error is
security-relevant.

**False Positive Guidance**: Some errors are legitimately ignored (e.g., closing
a response body, optional telemetry). Focus on catch blocks in security-critical
paths: authentication, authorization, payment, data access. Also consider whether
the error is handled by a return value or alternative mechanism rather than logging.

**Severity Criteria**:
- **high**: Silent catch in authentication, authorization, or audit logging code
- **medium**: Silent catch in data access or business logic code
- **low**: Silent catch in non-security utility code
