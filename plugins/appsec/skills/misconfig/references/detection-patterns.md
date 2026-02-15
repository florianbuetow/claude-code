# Security Misconfiguration Detection Patterns

Grep-based heuristics and code patterns for detecting security misconfigurations
when scanners are unavailable. Each pattern includes regex search strings,
language examples, scanner coverage, and false positive guidance.

---

## Pattern 1: Debug Mode Enabled

**Description**: Application running with debug mode enabled exposes detailed error
messages, stack traces, and internal application state. In production, this gives
attackers a roadmap to exploit other vulnerabilities.

**Grep Regex Heuristics**:
```
DEBUG\s*=\s*[Tt]rue
DEBUG\s*=\s*1
FLASK_DEBUG\s*=\s*1
NODE_ENV\s*=\s*['"]?development['"]?
RAILS_ENV\s*=\s*['"]?development['"]?
DJANGO_DEBUG\s*=\s*[Tt]rue
app\.debug\s*=\s*[Tt]rue
debug:\s*true
EnableDebugging|enableDetailedErrors
SetDeveloperExceptionPage
```

**File patterns to search**: `*.env`, `*.env.*`, `*.yaml`, `*.yml`, `*.toml`, `*.json`,
`*.py`, `*.js`, `*.ts`, `*.rb`, `*.properties`, `docker-compose*.yml`, `Dockerfile`

**Language Examples**:

Python (vulnerable):
```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
```

Python (fixed):
```python
# settings.py
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
```

JS/TS (vulnerable):
```javascript
// config.js
module.exports = {
  debug: true,
  env: 'development',
  showErrors: true
};
```

JS/TS (fixed):
```javascript
// config.js
module.exports = {
  debug: process.env.NODE_ENV !== 'production',
  env: process.env.NODE_ENV || 'production',
  showErrors: false
};
```

Java (vulnerable):
```xml
<!-- application.properties -->
spring.devtools.restart.enabled=true
server.error.include-stacktrace=always
server.error.include-message=always
```

Java (fixed):
```xml
<!-- application.properties -->
spring.devtools.restart.enabled=false
server.error.include-stacktrace=never
server.error.include-message=never
```

Go (vulnerable):
```go
gin.SetMode(gin.DebugMode)
router := gin.Default() // Default includes Logger and Recovery with details
```

Go (fixed):
```go
gin.SetMode(gin.ReleaseMode)
router := gin.New()
router.Use(gin.Recovery()) // Recovery without detailed output
```

**Scanner Coverage**: semgrep (partial), checkov (IaC debug flags), trivy (Dockerfile)

**False Positive Guidance**:
- Files explicitly named `*.dev.*`, `*.local.*`, or in `test/` directories are
  expected to have debug enabled. Flag only if they could be deployed to production.
- Environment variable references like `os.environ.get('DEBUG')` are fine -- the
  concern is hardcoded `True` values.
- Docker Compose files with `NODE_ENV=development` are a finding only if the compose
  file is used in production (check filename: `docker-compose.prod.yml` vs `docker-compose.yml`).

**Severity Criteria**:
- **CRITICAL**: Debug mode hardcoded to true in a file clearly used for production deployment.
- **HIGH**: Debug mode enabled in a config file without environment-specific override.
- **MEDIUM**: Debug-like settings in non-production config that could be accidentally deployed.
- **LOW**: Verbose logging levels in development-only configurations.

---

## Pattern 2: Missing Security Headers

**Description**: HTTP security headers instruct browsers to enable protections against
XSS, clickjacking, MIME sniffing, and protocol downgrade attacks. Their absence leaves
users vulnerable to client-side attacks.

**Grep Regex Heuristics**:
```
Content-Security-Policy
X-Frame-Options
Strict-Transport-Security
X-Content-Type-Options
Referrer-Policy
Permissions-Policy
X-XSS-Protection
helmet\(
secure_headers
SecurityHeadersMiddleware
```

Search for the **absence** of these patterns in server configuration and middleware
setup files. If none of the above strings appear in the codebase, that is the finding.

**File patterns to search**: `*.conf`, `*.py`, `*.js`, `*.ts`, `*.rb`, `*.go`,
`*.java`, `*.cs`, `nginx.conf`, `httpd.conf`, `Caddyfile`

**Language Examples**:

Python (vulnerable):
```python
# No security headers middleware
app = Flask(__name__)
# Headers never set anywhere
```

Python (fixed):
```python
from flask_talisman import Talisman
app = Flask(__name__)
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': "'self'",
})
```

JS/TS (vulnerable):
```javascript
const app = express();
// No helmet or manual header setting
app.listen(3000);
```

JS/TS (fixed):
```javascript
const helmet = require('helmet');
const app = express();
app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: { defaultSrc: ["'self'"] }
}));
app.listen(3000);
```

Java (vulnerable):
```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    // No security headers configured
}
```

Java (fixed):
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig extends WebSecurityConfigurerAdapter {
    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.headers()
            .contentSecurityPolicy("default-src 'self'")
            .and()
            .frameOptions().deny()
            .and()
            .httpStrictTransportSecurity().maxAgeInSeconds(31536000);
    }
}
```

Go (vulnerable):
```go
func handler(w http.ResponseWriter, r *http.Request) {
    // No security headers set
    w.Write([]byte("Hello"))
}
```

Go (fixed):
```go
func handler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Security-Policy", "default-src 'self'")
    w.Header().Set("X-Frame-Options", "DENY")
    w.Header().Set("X-Content-Type-Options", "nosniff")
    w.Header().Set("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    w.Write([]byte("Hello"))
}
```

**Scanner Coverage**: semgrep (code patterns), checkov (IaC/K8s ingress annotations)

**False Positive Guidance**:
- A reverse proxy (nginx, Caddy, AWS ALB) may set headers upstream. Check proxy
  configs before flagging application code.
- API-only services without browser clients have lower priority for some headers
  (e.g., X-Frame-Options), but CSP and HSTS are still relevant.
- Single-page applications served via CDN may configure headers at the CDN level.

**Severity Criteria**:
- **HIGH**: No Content-Security-Policy or Strict-Transport-Security on a web application
  serving HTML to browsers.
- **MEDIUM**: Missing X-Frame-Options, X-Content-Type-Options, or Referrer-Policy.
- **LOW**: Missing Permissions-Policy or X-XSS-Protection (deprecated in modern browsers).

---

## Pattern 3: CORS Wildcard

**Description**: Setting `Access-Control-Allow-Origin: *` allows any website to make
authenticated cross-origin requests to your API, potentially reading sensitive data.
Reflecting the Origin header without validation is equally dangerous.

**Grep Regex Heuristics**:
```
Access-Control-Allow-Origin.*\*
cors\(\s*\)
cors\(\{[^}]*origin:\s*['"]?\*['"]?
allow_origins\s*=\s*\[?\s*['"]?\*['"]?
AllowAllOrigins|allowAll|CorsAnyOrigin
Access-Control-Allow-Credentials.*true
CORS_ALLOW_ALL_ORIGINS\s*=\s*[Tt]rue
CORS_ORIGIN_ALLOW_ALL\s*=\s*[Tt]rue
```

**File patterns to search**: `*.py`, `*.js`, `*.ts`, `*.go`, `*.java`, `*.rb`,
`*.conf`, `*.yaml`, `*.yml`

**Language Examples**:

Python (vulnerable):
```python
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

Python (fixed):
```python
CORS_ALLOWED_ORIGINS = [
    'https://app.example.com',
    'https://admin.example.com',
]
CORS_ALLOW_CREDENTIALS = True
```

JS/TS (vulnerable):
```javascript
app.use(cors()); // Allows all origins by default
// or
app.use(cors({ origin: '*', credentials: true }));
```

JS/TS (fixed):
```javascript
const allowedOrigins = ['https://app.example.com'];
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));
```

Java (vulnerable):
```java
@CrossOrigin(origins = "*")
@RestController
public class ApiController { }
```

Java (fixed):
```java
@CrossOrigin(origins = {"https://app.example.com"})
@RestController
public class ApiController { }
```

Go (vulnerable):
```go
handler := cors.AllowAll().Handler(mux)
```

Go (fixed):
```go
c := cors.New(cors.Options{
    AllowedOrigins:   []string{"https://app.example.com"},
    AllowCredentials: true,
    AllowedMethods:   []string{"GET", "POST"},
})
handler := c.Handler(mux)
```

**Scanner Coverage**: semgrep (good coverage), checkov (API Gateway CORS)

**False Positive Guidance**:
- Public APIs that serve only non-sensitive data (e.g., weather APIs, public datasets)
  may legitimately use `*`, but should NOT combine it with `credentials: true`.
- `cors()` without arguments in Express defaults to `*` -- this is often unintentional.
- CDN or static asset servers may use `*` for font/image files -- lower risk.

**Severity Criteria**:
- **CRITICAL**: Wildcard origin combined with `Access-Control-Allow-Credentials: true`.
- **HIGH**: Wildcard origin on an API that handles authenticated requests or sensitive data.
- **MEDIUM**: Wildcard origin on a semi-public API without credentials.
- **LOW**: Wildcard origin on a fully public, read-only API.

---

## Pattern 4: Default Credentials in Configuration

**Description**: Default or well-known credentials left in configuration files provide
trivial unauthorized access. These are among the first things attackers check.

**Grep Regex Heuristics**:
```
password\s*[:=]\s*['"]?(admin|password|root|123456|default|changeme|secret|test|guest)['"]?
PASSWORD\s*=\s*['"]?(admin|password|root|123456|default|changeme|secret|test)['"]?
username\s*[:=]\s*['"]?admin['"]?
POSTGRES_PASSWORD\s*=\s*['"]?(postgres|password|admin)['"]?
MYSQL_ROOT_PASSWORD\s*=\s*['"]?(root|password|admin|mysql)['"]?
REDIS_PASSWORD\s*=
api[_-]?key\s*[:=]\s*['"]?(test|demo|example|changeme|xxx)['"]?
secret[_-]?key\s*[:=]\s*['"]?(changeme|secret|default|test)['"]?
```

**File patterns to search**: `*.env`, `*.env.*`, `*.yaml`, `*.yml`, `*.toml`, `*.json`,
`*.ini`, `*.cfg`, `*.conf`, `*.properties`, `docker-compose*.yml`

**Language Examples**:

Python (vulnerable):
```python
# settings.py
SECRET_KEY = 'django-insecure-change-me-in-production'
DATABASES = {
    'default': {
        'PASSWORD': 'admin123',
    }
}
```

Python (fixed):
```python
# settings.py
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DATABASES = {
    'default': {
        'PASSWORD': os.environ['DB_PASSWORD'],
    }
}
```

JS/TS (vulnerable):
```javascript
// config.js
module.exports = {
  db: { password: 'admin' },
  jwt: { secret: 'changeme' },
};
```

JS/TS (fixed):
```javascript
// config.js
module.exports = {
  db: { password: process.env.DB_PASSWORD },
  jwt: { secret: process.env.JWT_SECRET },
};
```

Java (vulnerable):
```properties
# application.properties
spring.datasource.password=root
spring.security.user.password=admin
```

Java (fixed):
```properties
# application.properties
spring.datasource.password=${DB_PASSWORD}
spring.security.user.password=${ADMIN_PASSWORD}
```

Go (vulnerable):
```go
cfg := &DatabaseConfig{
    Password: "postgres",
    Host:     "localhost",
}
```

Go (fixed):
```go
cfg := &DatabaseConfig{
    Password: os.Getenv("DB_PASSWORD"),
    Host:     os.Getenv("DB_HOST"),
}
```

**Scanner Coverage**: gitleaks (partial -- focuses on secrets), semgrep (config patterns),
trivy (Dockerfile ENV), checkov (IaC default passwords)

**False Positive Guidance**:
- Example files (`*.example`, `*.sample`, `*.template`) are expected to have placeholder
  credentials -- flag only if the non-example version also exists with real values.
- Test fixtures and seed data may contain dummy credentials intentionally.
- Docker Compose files used only for local development may have simple passwords, but
  should still be flagged if the same file could be used in production.

**Severity Criteria**:
- **CRITICAL**: Default credentials for databases, admin panels, or API keys in
  production-bound configuration.
- **HIGH**: Default credentials in configuration files without clear environment separation.
- **MEDIUM**: Weak placeholder credentials in development configs that lack `.example` suffix.
- **LOW**: Default values in example/template files.

---

## Pattern 5: Verbose Error Handling Exposing Stack Traces

**Description**: Error handlers that return full stack traces, internal file paths,
database queries, or framework version numbers to end users leak information that
helps attackers craft targeted exploits.

**Grep Regex Heuristics**:
```
traceback\.format_exc|traceback\.print_exc
print_exception|format_exception
e\.printStackTrace\(\)
stackTrace|stack_trace
res\.send\(err\)|res\.json\(.*err
showException|displayException
include-stacktrace\s*=\s*always
include-message\s*=\s*always
PROPAGATE_EXCEPTIONS\s*=\s*[Tt]rue
errorhandler.*return.*str\(e\)
catch.*\{[^}]*res\.(send|json|status).*err(or)?\.
```

**File patterns to search**: `*.py`, `*.js`, `*.ts`, `*.java`, `*.go`, `*.rb`,
`*.cs`, `*.php`, `*.properties`, `*.yaml`, `*.yml`

**Language Examples**:

Python (vulnerable):
```python
@app.errorhandler(500)
def handle_error(e):
    return traceback.format_exc(), 500
```

Python (fixed):
```python
@app.errorhandler(500)
def handle_error(e):
    app.logger.error(f"Internal error: {traceback.format_exc()}")
    return jsonify({"error": "Internal server error"}), 500
```

JS/TS (vulnerable):
```javascript
app.use((err, req, res, next) => {
  res.status(500).json({
    message: err.message,
    stack: err.stack,
    query: err.sql
  });
});
```

JS/TS (fixed):
```javascript
app.use((err, req, res, next) => {
  logger.error('Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({ error: 'Internal server error' });
});
```

Java (vulnerable):
```java
@ExceptionHandler(Exception.class)
public ResponseEntity<String> handleException(Exception e) {
    e.printStackTrace();
    return ResponseEntity.status(500).body(e.getMessage() + "\n" + Arrays.toString(e.getStackTrace()));
}
```

Java (fixed):
```java
@ExceptionHandler(Exception.class)
public ResponseEntity<Map<String, String>> handleException(Exception e) {
    logger.error("Unhandled exception", e);
    return ResponseEntity.status(500).body(Map.of("error", "Internal server error"));
}
```

Go (vulnerable):
```go
func handler(w http.ResponseWriter, r *http.Request) {
    result, err := doWork()
    if err != nil {
        http.Error(w, fmt.Sprintf("Error: %+v", err), 500)
    }
}
```

Go (fixed):
```go
func handler(w http.ResponseWriter, r *http.Request) {
    result, err := doWork()
    if err != nil {
        log.Printf("Internal error: %+v", err)
        http.Error(w, "Internal server error", 500)
    }
}
```

**Scanner Coverage**: semgrep (good coverage for all languages), bandit (Python)

**False Positive Guidance**:
- Error details sent to logging frameworks (not HTTP responses) are correct behavior.
- Development-only error handlers guarded by `if DEBUG` or `if NODE_ENV !== 'production'`
  are acceptable, but verify the guard is reliable.
- CLI tools and batch jobs that print stack traces to stderr are not web-facing.

**Severity Criteria**:
- **HIGH**: Stack traces or internal paths returned in HTTP responses unconditionally.
- **MEDIUM**: Error details returned conditionally but the condition is weak or easily bypassed.
- **LOW**: Verbose error messages in internal/admin-only endpoints.

---

## Pattern 6: Unnecessary HTTP Methods Enabled

**Description**: Web servers configured to allow HTTP methods like TRACE, TRACK,
DELETE, or OPTIONS without restriction can enable cross-site tracing attacks,
unauthorized data modification, or information disclosure about available endpoints.

**Grep Regex Heuristics**:
```
allow_methods\s*=\s*\[.*\*.*\]
AllowMethods.*\*
methods\s*[:=]\s*\[.*TRACE
TRACE|TRACK
limit_except\s+(GET|POST)
dav_methods
WebDAV
enable-http-method-override
Access-Control-Allow-Methods.*\*
methods:\s*\[['"]?\*['"]?\]
```

**File patterns to search**: `*.conf`, `nginx.conf`, `httpd.conf`, `*.yaml`, `*.yml`,
`*.py`, `*.js`, `*.ts`, `*.go`, `*.java`, `*.xml`, `web.config`

**Language Examples**:

Python (vulnerable):
```python
@app.route('/api/data', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'TRACE'])
def data_endpoint():
    pass
```

Python (fixed):
```python
@app.route('/api/data', methods=['GET', 'POST'])
def data_endpoint():
    pass
```

JS/TS (vulnerable):
```javascript
app.all('/api/*', (req, res) => {
  // Handles ALL HTTP methods including TRACE
  handleRequest(req, res);
});
```

JS/TS (fixed):
```javascript
app.get('/api/resource', getHandler);
app.post('/api/resource', postHandler);
// Only specific methods are routed
```

Java (vulnerable):
```xml
<!-- web.xml -->
<security-constraint>
  <web-resource-collection>
    <http-method>GET</http-method>
    <!-- Only GET is constrained, all others are allowed -->
  </web-resource-collection>
</security-constraint>
```

Java (fixed):
```xml
<!-- web.xml -->
<security-constraint>
  <web-resource-collection>
    <http-method-omission>GET</http-method-omission>
    <http-method-omission>POST</http-method-omission>
    <!-- All methods except GET and POST are denied -->
  </web-resource-collection>
  <auth-constraint/> <!-- empty = deny -->
</security-constraint>
```

Go (vulnerable):
```go
http.HandleFunc("/api/", func(w http.ResponseWriter, r *http.Request) {
    // No method check -- handles TRACE, DELETE, etc.
    processRequest(w, r)
})
```

Go (fixed):
```go
http.HandleFunc("/api/", func(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet && r.Method != http.MethodPost {
        http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
        return
    }
    processRequest(w, r)
})
```

**Scanner Coverage**: semgrep (partial), checkov (IaC API Gateway methods), nikto
(runtime scanning -- not a static tool)

**False Positive Guidance**:
- RESTful APIs legitimately use PUT, PATCH, and DELETE -- the concern is TRACE/TRACK
  and catch-all handlers without method validation.
- `app.all()` in Express is common for middleware (logging, auth) applied before
  method-specific routes -- check if it terminates the request or passes through.
- OPTIONS is required for CORS preflight -- blocking it breaks cross-origin requests.
  The concern is when OPTIONS returns an overly broad Allow header.

**Severity Criteria**:
- **HIGH**: TRACE or TRACK methods explicitly enabled on a production web server.
- **MEDIUM**: Catch-all method handlers without method validation on sensitive endpoints.
- **LOW**: Overly broad Allow header in OPTIONS responses on non-sensitive endpoints.
