# OWASP API Security Top 10 (2023)

## Overview

APIs expose business logic and data directly, creating a different attack surface than browser-based web apps. The OWASP API Security Top 10 targets authorization granularity, data-access patterns, and resource consumption issues unique to API architectures. While the Web Top 10 focuses on rendering-layer and session-layer risks, the API Top 10 addresses machine-consumable interfaces that lack traditional UI-based protections.

---

## API1:2023 - Broken Object Level Authorization (BOLA)

**Description**: The API does not verify that the requesting user is authorized to access the specific object. The API equivalent of IDOR.

**Common Vulnerabilities**:
- Endpoints accepting an object ID without checking ownership
- Predictable/sequential identifiers (e.g., `/api/invoices/1042`)
- Batch endpoints that skip per-object authorization
- GraphQL resolvers traversing relationships without per-node checks

**Code Example**:
```python
# VULNERABLE: no ownership check
@app.get("/api/orders/{order_id}")
def get_order(order_id: int):
    return db.orders.find_by_id(order_id)

# SECURE: verify ownership
@app.get("/api/orders/{order_id}")
def get_order(order_id: int, user: User = Depends(get_current_user)):
    order = db.orders.find_by_id(order_id)
    if order.user_id != user.id:
        raise HTTPException(status_code=403)
    return order
```

**How to Detect**: Route handlers that accept an ID and query the DB without filtering by authenticated user. Authorization only at endpoint level, not object level.

**How to Prevent**: Object-level auth checks on every resource endpoint. Use UUIDs. Test cross-user access.

**STRIDE Mapping**: Elevation of Privilege, Information Disclosure
**OWASP Top 10 Mapping**: A01:2021 Broken Access Control

---

## API2:2023 - Broken Authentication

**Description**: Authentication mechanisms are flawed, allowing token/key/password compromise.

**Common Vulnerabilities**:
- API keys in query strings (logged by proxies)
- Missing token expiration or rotation
- Accepting unsigned/weakly signed JWTs
- No rate limiting on auth endpoints

**Code Example**:
```javascript
// VULNERABLE: decode without verify
const payload = jwt.decode(token);

// SECURE: verify with explicit algorithm
const payload = jwt.verify(token, publicKey, { algorithms: ['RS256'] });
```

**How to Detect**: `jwt.decode` without `jwt.verify`. API keys in URLs. Missing rate limiting on `/login`, `/token`.

**How to Prevent**: Use OAuth 2.0/OIDC. Short-lived tokens with rotation. Explicit algorithm allowlists. Rate limit auth endpoints.

**STRIDE Mapping**: Spoofing
**OWASP Top 10 Mapping**: A07:2021 Identification and Authentication Failures

---

## API3:2023 - Broken Object Property Level Authorization

**Description**: The API exposes properties users should not read (excessive data exposure) or write (mass assignment). Merges former API3:2019 and API6:2019.

**Common Vulnerabilities**:
- Returning full DB objects including `is_admin`, `password_hash`
- Binding all client-supplied fields without an allowlist
- GraphQL types exposing every column in the backing table

**Code Example**:
```python
# VULNERABLE: mass assignment
@app.put("/api/users/{id}")
def update_user(id: int, data: dict):
    db.users.update(id, **data)  # attacker sends {"is_admin": true}

# SECURE: explicit schema
class UserUpdate(BaseModel):
    name: str
    email: str
@app.put("/api/users/{id}")
def update_user(id: int, data: UserUpdate):
    db.users.update(id, **data.dict())
```

**How to Detect**: ORM objects returned directly. `Object.assign(model, req.body)` or `**request.body` without allowlisting.

**How to Prevent**: Explicit response/update schemas. Allowlist writable properties. Field-level authorization.

**STRIDE Mapping**: Information Disclosure, Tampering, Elevation of Privilege
**OWASP Top 10 Mapping**: A01:2021 Broken Access Control, A04:2021 Insecure Design

---

## API4:2023 - Unrestricted Resource Consumption

**Description**: No limits on size or number of requested resources, causing DoS or cloud billing abuse.

**Common Vulnerabilities**:
- No rate limiting or pagination
- Unbounded file uploads
- Expensive operations per single request (regex, large joins)
- GraphQL queries with unbounded depth

**Code Example**:
```javascript
// VULNERABLE: no limit
app.get('/api/transactions', async (req, res) => {
  res.json(await db.transactions.findAll());
});

// SECURE: paginated and rate-limited
app.get('/api/transactions', rateLimit({ max: 100 }), async (req, res) => {
  const limit = Math.min(parseInt(req.query.limit) || 20, 100);
  res.json(await db.transactions.findAll({ limit }));
});
```

**How to Detect**: DB queries without LIMIT. Missing rate-limiting middleware. Upload handlers without size checks.

**How to Prevent**: Server-side pagination with max page size. Per-client rate limiting. Timeouts on all calls. GraphQL depth limits.

**STRIDE Mapping**: Denial of Service
**OWASP Top 10 Mapping**: A04:2021 Insecure Design, A05:2021 Security Misconfiguration

---

## API5:2023 - Broken Function Level Authorization (BFLA)

**Description**: No authorization at the function/operation level. Users invoke admin functions by calling the endpoint.

**Common Vulnerabilities**:
- Admin endpoints with predictable names (`/api/admin/users`)
- Regular users calling PUT/DELETE on admin-only resources
- Relying on client-side UI hiding instead of server enforcement

**Code Example**:
```python
# VULNERABLE: authenticated but no role check
@app.delete("/api/admin/users/{id}")
def delete_user(id: int, user: User = Depends(get_current_user)):
    db.users.delete(id)

# SECURE: role enforcement
@app.delete("/api/admin/users/{id}")
@require_role("admin")
def delete_user(id: int, user: User = Depends(get_current_user)):
    db.users.delete(id)
```

**How to Detect**: Admin endpoints checking authentication but not authorization. Inconsistent method-level access controls.

**How to Prevent**: Deny by default. Role-based middleware on every function. Audit routes for missing authorization.

**STRIDE Mapping**: Elevation of Privilege
**OWASP Top 10 Mapping**: A01:2021 Broken Access Control

---

## API6:2023 - Unrestricted Access to Sensitive Business Flows

**Description**: Business flows exposed without anti-automation controls. The risk is abuse of legitimate functionality at scale, not a technical flaw.

**Common Vulnerabilities**:
- Purchase flows accessible to bots (scalping)
- Review/comment endpoints without CAPTCHA
- Referral/coupon abuse via scripting
- Account creation without device fingerprinting

**How to Detect**: Identify high-value flows (purchase, signup, voting). Check for rate limiting, CAPTCHA, velocity checks.

**How to Prevent**: Multi-layered anti-automation. Per-user/session limits. Anomalous usage monitoring.

**STRIDE Mapping**: Tampering, Denial of Service
**OWASP Top 10 Mapping**: A04:2021 Insecure Design

---

## API7:2023 - Server Side Request Forgery

**Description**: API fetches a resource from a user-supplied URL without destination validation.

**Common Vulnerabilities**:
- Webhook registration with arbitrary callback URLs
- URL preview/unfurling features
- File import from URL, PDF generation from user URLs

**Code Example**:
```python
# VULNERABLE: attacker registers http://169.254.169.254/latest/meta-data/
@app.post("/api/webhooks")
def register_webhook(url: str):
    requests.get(url)

# SECURE: validate scheme and block internal networks
@app.post("/api/webhooks")
def register_webhook(url: str):
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise HTTPException(400)
    ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    if ipaddress.ip_address(ip).is_private:
        raise HTTPException(400)
```

**How to Detect**: HTTP client calls where URL originates from user input. Webhook/callback features. Missing URL allowlists.

**How to Prevent**: Allowlist schemes, hosts, ports. Block private IP ranges and cloud metadata. Disable redirects.

**STRIDE Mapping**: Information Disclosure, Elevation of Privilege
**OWASP Top 10 Mapping**: A10:2021 Server-Side Request Forgery

---

## API8:2023 - Security Misconfiguration

**Description**: Improper configuration of the API stack leaves defaults, debug features, or permissive policies active.

**Common Vulnerabilities**:
- CORS wildcard with credentials (`origin: '*', credentials: true`)
- Stack traces in error responses
- Default gateway credentials
- Debug endpoints in production

**Code Example**:
```javascript
// VULNERABLE
app.use(cors({ origin: '*', credentials: true }));
app.use((err, req, res, next) => res.status(500).json({ stack: err.stack }));

// SECURE
app.use(cors({ origin: ['https://app.example.com'], credentials: true }));
app.use((err, req, res, next) => { logger.error(err); res.status(500).json({ error: 'Internal error' }); });
```

**How to Detect**: CORS wildcards with credentials. Error handlers returning stack traces. Debug flags in production config.

**How to Prevent**: Repeatable hardening. Restrict CORS origins. Generic client errors. Automate config audits.

**STRIDE Mapping**: Information Disclosure, Tampering, Elevation of Privilege
**OWASP Top 10 Mapping**: A05:2021 Security Misconfiguration

---

## API9:2023 - Improper Inventory Management

**Description**: Old, deprecated, or shadow API versions remain accessible without security controls.

**Common Vulnerabilities**:
- Old versions running in production (`/api/v1/` alongside `/api/v3/`)
- Debug/staging endpoints accessible publicly
- Deprecated endpoints missing patches applied to newer versions
- Shadow endpoints unknown to security teams

**How to Detect**: Version prefixes with old versions still registered. Routes containing `debug`, `test`, `internal`. Endpoints bypassing auth middleware.

**How to Prevent**: Maintain endpoint inventory. Decommission old versions on schedule. Uniform security controls across versions.

**STRIDE Mapping**: Information Disclosure, Elevation of Privilege
**OWASP Top 10 Mapping**: A05:2021 Security Misconfiguration, A06:2021 Vulnerable and Outdated Components

---

## API10:2023 - Unsafe Consumption of APIs

**Description**: The application trusts third-party API data without validation, extending the trust boundary to external systems.

**Common Vulnerabilities**:
- Third-party responses consumed without validation
- Following external redirects blindly
- No timeouts on third-party calls
- External data stored without sanitization (second-order injection)

**Code Example**:
```python
# VULNERABLE: trusting third-party data
products = requests.get("https://partner.example.com/products").json()
for p in products:
    db.execute(f"INSERT INTO products VALUES ('{p['name']}')")

# SECURE: validate and parameterize
resp = requests.get("https://partner.example.com/products", timeout=10, verify=True)
for p in resp.json():
    validated = PartnerSchema(**p)
    db.execute("INSERT INTO products VALUES (%s)", (validated.name,))
```

**How to Detect**: HTTP calls to external domains with responses used unvalidated. External data in SQL/templates. Missing timeouts.

**How to Prevent**: Validate against strict schemas. Parameterized queries. TLS on all outbound. Timeouts and circuit breakers.

**STRIDE Mapping**: Tampering, Information Disclosure
**OWASP Top 10 Mapping**: A03:2021 Injection, A08:2021 Software and Data Integrity Failures

---

## Cross-Framework Mapping

| API Top 10 | OWASP Top 10 2021 | STRIDE | CWE |
|---|---|---|---|
| API1:2023 BOLA | A01 Broken Access Control | Elevation of Privilege, Info Disclosure | CWE-284, CWE-639 |
| API2:2023 Broken Auth | A07 Auth Failures | Spoofing | CWE-287, CWE-307 |
| API3:2023 Object Property Auth | A01, A04 | Info Disclosure, Tampering, EoP | CWE-213, CWE-915 |
| API4:2023 Resource Consumption | A04, A05 | Denial of Service | CWE-770, CWE-400 |
| API5:2023 BFLA | A01 Broken Access Control | Elevation of Privilege | CWE-285, CWE-862 |
| API6:2023 Business Flow Abuse | A04 Insecure Design | Tampering, DoS | CWE-799, CWE-837 |
| API7:2023 SSRF | A10 SSRF | Info Disclosure, EoP | CWE-918 |
| API8:2023 Misconfiguration | A05 Misconfiguration | Info Disclosure, Tampering, EoP | CWE-16, CWE-209 |
| API9:2023 Inventory Mgmt | A05, A06 | Info Disclosure, EoP | CWE-1059 |
| API10:2023 Unsafe Consumption | A03, A08 | Tampering, Info Disclosure | CWE-20, CWE-502 |

## Compliance Mapping Template

```json
{
  "framework": "OWASP API Security Top 10 2023",
  "requirement_id": "API1:2023",
  "requirement_name": "Broken Object Level Authorization",
  "threats": ["threat-001"],
  "controls": ["control-001"],
  "status": "partial|compliant|non-compliant",
  "gaps": ["gap-001"],
  "evidence": ["Object-level checks in OrderService", "Missing checks in InvoiceController"]
}
```
