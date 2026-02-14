# OWASP Top 10 (2021 Edition)

## Overview

The OWASP Top 10 is a periodically updated ranking of the most impactful security risks facing web applications. The 2021 edition was built from a dataset contributed by testing organizations worldwide, covering over 500,000 applications and analyzing nearly 400 Common Weakness Enumerations (CWEs). Each category aggregates related CWEs and is ranked by a combination of incidence rate (percentage of applications exhibiting at least one instance), weighted exploit and impact scores, and total occurrence counts.

**What changed in 2021**: Three categories are new (A04 Insecure Design, A08 Software and Data Integrity Failures, A10 SSRF). Four were renamed or rescoped to target root causes rather than symptoms. XSS was absorbed into A03 Injection. XXE was absorbed into A05 Security Misconfiguration. The methodology shifted from expert survey to data-driven analysis using incidence rates rather than raw prevalence, which reshuffled the rankings significantly. Broken Access Control rose from fifth to first. Injection dropped from first to third.

**When to use this framework**: Use OWASP Top 10 as a baseline checklist for application security. It is the most widely recognized security framework and serves as a minimum standard for most compliance requirements. Apply it to any web application, API, or service that handles user input or stores sensitive data.

---

## A01:2021 - Broken Access Control

**CWE Count**: 34 mapped CWEs | **Incidence Rate**: 3.81% | **Occurrences**: 318,487

**What it is**: Authorization logic that fails to enforce who can access what. The application accepts a request, authenticates the user, but does not verify whether that specific user is permitted to perform that specific action on that specific resource. This was the number one finding in the 2021 dataset.

**Key CWEs**: CWE-200 (Exposure of Sensitive Information), CWE-284 (Improper Access Control), CWE-285 (Improper Authorization), CWE-352 (Cross-Site Request Forgery), CWE-639 (Authorization Bypass Through User-Controlled Key), CWE-863 (Incorrect Authorization), CWE-601 (Open Redirect), CWE-22 (Path Traversal).

**Code Patterns to Detect**:
- Route handlers that accept a resource ID from the URL or request body and query the database without filtering by the authenticated user's ownership or role
- Endpoints that only check authentication (is the user logged in?) but not authorization (does this user have permission?)
- Client-side-only enforcement of permissions, with the server accepting any request that arrives
- Missing CSRF tokens on state-changing operations
- Metadata in JWTs or cookies that can be modified by the client to alter role or identity claims

**Code Example**:
```python
# VULNERABLE: authenticated but no ownership check
@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user: User = Depends(require_auth)):
    return db.invoices.find_by_id(invoice_id)

# SECURE: ownership verified
@app.get("/api/invoices/{invoice_id}")
def get_invoice(invoice_id: int, user: User = Depends(require_auth)):
    invoice = db.invoices.find_by_id(invoice_id)
    if invoice.owner_id != user.id:
        raise HTTPException(status_code=404)
    return invoice
```

**How to Prevent**: Deny by default. Implement authorization once in reusable middleware or decorators and apply it consistently. Enforce record-level ownership checks. Disable directory listing. Log and alert on access control failures. Rate-limit sensitive endpoints. Invalidate tokens server-side on logout.

**STRIDE Mapping**: Elevation of Privilege, Information Disclosure
**CWE Mapping**: CWE-284, CWE-285, CWE-639, CWE-352, CWE-22, CWE-200

---

## A02:2021 - Cryptographic Failures

**CWE Count**: 29 mapped CWEs | **Incidence Rate**: 4.49%

**What it is**: Weaknesses in how an application protects data through cryptography. Previously called "Sensitive Data Exposure" (A03 in 2017), the 2021 edition refocused this category on the root cause — broken or missing cryptographic controls — rather than the symptom of data exposure. Covers data in transit and at rest.

**Key CWEs**: CWE-259 (Use of Hard-coded Password), CWE-327 (Use of Broken or Risky Cryptographic Algorithm), CWE-328 (Use of Weak Hash), CWE-330 (Use of Insufficiently Random Values), CWE-331 (Insufficient Entropy), CWE-311 (Missing Encryption of Sensitive Data), CWE-312 (Cleartext Storage of Sensitive Information).

**Code Patterns to Detect**:
- Data transmitted over HTTP instead of HTTPS, or TLS configuration that accepts outdated protocols (SSLv3, TLS 1.0/1.1)
- Passwords stored with fast hashes (MD5, SHA-1, SHA-256) instead of adaptive functions (Argon2, bcrypt, scrypt)
- Use of deprecated algorithms (DES, RC4, MD5 for integrity, ECB mode)
- Hard-coded encryption keys, IVs, or salts in source code
- `Math.random()` or language equivalents used for security-sensitive values (tokens, nonces)
- Missing `Secure` and `HttpOnly` flags on session cookies
- Certificate validation disabled in HTTP client configurations

**Code Example**:
```javascript
// VULNERABLE: weak hash for passwords
const hash = crypto.createHash('sha256').update(password).digest('hex');

// SECURE: adaptive hash with salt
const hash = await bcrypt.hash(password, 12);
```

**How to Prevent**: Classify data by sensitivity and apply controls per classification. Encrypt all sensitive data at rest using AES-256 or equivalent. Enforce TLS 1.2+ for all data in transit. Use strong, salted adaptive hashing for passwords. Generate keys and IVs from cryptographically secure random sources. Disable caching for responses containing sensitive data. Do not store sensitive data longer than required.

**STRIDE Mapping**: Information Disclosure, Tampering
**CWE Mapping**: CWE-327, CWE-328, CWE-311, CWE-312, CWE-259, CWE-330

---

## A03:2021 - Injection

**CWE Count**: 33 mapped CWEs | **Incidence Rate**: 3.37% | **Occurrences**: 274,228

**What it is**: Untrusted data sent to an interpreter as part of a command or query, causing unintended execution. The 2021 edition absorbed Cross-Site Scripting (XSS) into this category, recognizing that XSS is fundamentally an injection flaw targeting the browser's HTML/JavaScript interpreter. This category dropped from first to third as frameworks increasingly provide built-in parameterization.

**Key CWEs**: CWE-79 (Cross-site Scripting), CWE-89 (SQL Injection), CWE-78 (OS Command Injection), CWE-94 (Code Injection), CWE-917 (Expression Language Injection), CWE-77 (Command Injection), CWE-611 (XXE — note: XXE was moved to A05 as a category, but the CWE itself still maps here when exploited for injection).

**Code Patterns to Detect**:
- String concatenation or template literals building SQL, NoSQL, LDAP, or OS commands from user input
- Dynamic queries without parameterized statements or prepared statements
- User input rendered into HTML without context-aware escaping (stored, reflected, or DOM-based XSS)
- `eval()`, `exec()`, `Function()`, or equivalent dynamic code execution with user-controlled input
- ORM methods that accept raw query fragments alongside user data
- Server-side template injection where user input reaches template rendering engines

**Code Example**:
```python
# VULNERABLE: string concatenation in SQL
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

# SECURE: parameterized query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**How to Prevent**: Use parameterized queries or prepared statements for all database access. Apply context-aware output encoding for HTML, JavaScript, CSS, and URL contexts. Use allowlist input validation on the server side. Escape special characters in residual dynamic queries. Use LIMIT and similar controls to bound result sets. Automate testing of all input parameters.

**STRIDE Mapping**: Tampering, Information Disclosure, Elevation of Privilege
**CWE Mapping**: CWE-79, CWE-89, CWE-78, CWE-94, CWE-917

---

## A04:2021 - Insecure Design

**CWE Count**: 40 mapped CWEs | **Incidence Rate**: 3.00%

**What it is**: A new category in 2021 that addresses flaws in the design and architecture of an application, as distinct from implementation bugs. An insecure design cannot be fixed by a perfect implementation — the flaw is in what the system was designed to do, not in how the code was written. This category calls for threat modeling, secure design patterns, and reference architectures as part of the development lifecycle.

**Key CWEs**: CWE-209 (Generation of Error Message Containing Sensitive Information), CWE-256 (Plaintext Storage of a Password), CWE-501 (Trust Boundary Violation), CWE-522 (Insufficiently Protected Credentials).

**Code Patterns to Detect**:
- Missing rate limiting on operations that should be throttled (password reset, OTP verification, coupon redemption)
- Business logic that does not enforce plausibility checks (negative quantities, prices below zero, impossible date ranges)
- Trust boundary violations where user-controlled data crosses from a lower-trust zone to a higher-trust zone without re-validation
- Missing multi-factor verification on high-value operations (wire transfers, privilege changes)
- No separation of concerns between tenant data in multi-tenant systems

**How to Prevent**: Establish a secure development lifecycle that includes threat modeling. Use secure design patterns and reference architectures. Integrate security user stories alongside functional requirements. Implement plausibility checks at every tier. Write unit and integration tests for abuse cases, not just happy paths. Limit resource consumption by user and service.

**STRIDE Mapping**: All categories (design flaws can manifest as any threat type)
**CWE Mapping**: CWE-209, CWE-256, CWE-501, CWE-522

---

## A05:2021 - Security Misconfiguration

**CWE Count**: 20 mapped CWEs | **Incidence Rate**: 4.51%

**What it is**: The application stack is not securely configured. This includes the web server, application server, database, framework, cloud services, containers, and any middleware. The 2021 edition absorbed the former A04:2017 XML External Entities (XXE) category, treating XXE as a specific type of misconfiguration (XML parsers with external entity processing enabled by default).

**Key CWEs**: CWE-16 (Configuration), CWE-611 (Improper Restriction of XML External Entity Reference), CWE-1004 (Sensitive Cookie Without HttpOnly Flag), CWE-1032 (OWASP Top 10 2017 Category A6).

**Code Patterns to Detect**:
- Default credentials left in place on databases, admin panels, or service accounts
- Unnecessary features enabled: debug mode, directory listing, stack traces in error responses, sample applications deployed
- Missing or misconfigured security headers (Content-Security-Policy, X-Frame-Options, Strict-Transport-Security)
- Cloud storage buckets or services with overly permissive access policies
- XML parsers configured to process external entities or DTDs
- CORS policies using wildcard origins with credentials

**Code Example**:
```javascript
// VULNERABLE: debug mode and permissive CORS in production
app.use(cors({ origin: '*', credentials: true }));
app.use(errorHandler({ debug: true }));

// SECURE: restricted origin and generic errors
app.use(cors({ origin: ['https://app.example.com'], credentials: true }));
app.use((err, req, res, next) => {
  logger.error(err);
  res.status(500).json({ error: 'Internal server error' });
});
```

**How to Prevent**: Automate environment hardening with repeatable configuration management. Strip unnecessary features, components, and documentation from production builds. Review all configuration changes for security impact. Use infrastructure-as-code to enforce consistent configurations. Send security headers on every response. Scan for misconfiguration regularly.

**STRIDE Mapping**: All categories (misconfiguration can enable any threat type)
**CWE Mapping**: CWE-16, CWE-611, CWE-1004

---

## A06:2021 - Vulnerable and Outdated Components

**CWE Count**: 3 mapped CWEs

**What it is**: The application depends on libraries, frameworks, or other software components with known security vulnerabilities. This was A09 in 2017 and rose to sixth position. It is the only category in the Top 10 that does not have CVE mappings to the included CWEs, reflecting the difficulty of testing for this class of risk through traditional application scanning.

**Code Patterns to Detect**:
- Dependency manifests (package.json, requirements.txt, go.mod, Gemfile, pom.xml) with unpinned version ranges that could resolve to vulnerable versions
- Missing or uncommitted lockfiles
- Dependencies with known CVEs reported by `npm audit`, `pip-audit`, `trivy`, or similar tools
- Components that are no longer maintained (archived repositories, no releases in 2+ years)
- Nested or transitive dependencies that introduce vulnerabilities not visible at the top level

**How to Prevent**: Maintain an inventory of all component versions including transitive dependencies. Monitor vulnerability databases (NVD, OSV, GitHub Advisories) continuously. Remove unused dependencies. Pin dependency versions and use lockfiles. Obtain components only from official sources over secure channels. Prefer components that are actively maintained and provide security patches.

**STRIDE Mapping**: All categories (impact depends on what the vulnerable component does)
**CWE Mapping**: CWE-1035 (Using Software with Known Vulnerabilities)

---

## A07:2021 - Identification and Authentication Failures

**CWE Count**: 22 mapped CWEs

**What it is**: Weaknesses in confirming user identity and managing authenticated sessions. Previously "Broken Authentication" at position two in 2017, this category dropped to seventh partly because modern frameworks provide stronger defaults for authentication. The scope was broadened to include identification failures alongside authentication failures.

**Key CWEs**: CWE-287 (Improper Authentication), CWE-384 (Session Fixation), CWE-307 (Improper Restriction of Excessive Authentication Attempts), CWE-798 (Use of Hard-coded Credentials), CWE-613 (Insufficient Session Expiration).

**Code Patterns to Detect**:
- Login endpoints without rate limiting or account lockout, enabling credential stuffing and brute-force attacks
- Passwords checked against no complexity requirements or against known-breached password lists
- Session identifiers exposed in URLs
- Session tokens not rotated after successful login (session fixation)
- Sessions that persist indefinitely without inactivity timeout
- Password recovery flows that leak whether an account exists via different error messages
- Missing multi-factor authentication on sensitive accounts or operations

**Code Example**:
```python
# VULNERABLE: no rate limiting, leaks account existence
@app.post("/login")
def login(email: str, password: str):
    user = db.users.find_by_email(email)
    if not user:
        return {"error": "No account with that email"}  # reveals existence
    if not verify_password(password, user.password_hash):
        return {"error": "Wrong password"}

# SECURE: rate limited, generic error
@app.post("/login")
@rate_limit(max=5, per="minute", key="ip")
def login(email: str, password: str):
    user = db.users.find_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        return {"error": "Invalid credentials"}
```

**How to Prevent**: Implement multi-factor authentication. Do not deploy with default credentials. Check passwords against breached password databases (NIST SP 800-63B). Rate-limit login attempts with exponential backoff. Use a server-side session manager that generates high-entropy session IDs. Rotate session tokens on login. Set appropriate session timeouts.

**STRIDE Mapping**: Spoofing, Repudiation
**CWE Mapping**: CWE-287, CWE-384, CWE-307, CWE-798, CWE-613

---

## A08:2021 - Software and Data Integrity Failures

**CWE Count**: 10 mapped CWEs | **Incidence Rate**: 2.05%

**What it is**: A new category in 2021 that covers code and infrastructure that does not protect against integrity violations. This includes insecure deserialization (formerly its own category A08:2017) and supply chain risks such as unsigned updates, unverified dependencies, and insecure CI/CD pipelines. The focus is on assumptions of integrity without verification.

**Key CWEs**: CWE-502 (Deserialization of Untrusted Data), CWE-829 (Inclusion of Functionality from Untrusted Control Sphere), CWE-494 (Download of Code Without Integrity Check), CWE-345 (Insufficient Verification of Data Authenticity).

**Code Patterns to Detect**:
- Deserialization of user-controlled data (pickle, Java ObjectInputStream, PHP unserialize, YAML unsafe load)
- Dependency manifests pulling packages without integrity verification (missing lockfile hashes)
- CI/CD pipelines that execute code from pull requests without review gates
- Auto-update mechanisms that download and install code without signature verification
- npm install hooks or post-install scripts that execute arbitrary code from third-party packages

**Code Example**:
```python
# VULNERABLE: deserializing untrusted data
import pickle
user_data = pickle.loads(request.body)  # arbitrary code execution

# SECURE: use safe serialization
import json
user_data = json.loads(request.body)  # only parses data, no code execution
```

**How to Prevent**: Use digital signatures to verify software and data integrity. Ensure dependency resolution uses lockfiles with integrity hashes. Use software composition analysis to detect known-vulnerable components. Require code review for all CI/CD configuration changes. Do not send serialized objects to untrusted clients. Implement integrity checks on all serialized data accepted from external sources.

**STRIDE Mapping**: Tampering, Elevation of Privilege
**CWE Mapping**: CWE-502, CWE-829, CWE-494, CWE-345

---

## A09:2021 - Security Logging and Monitoring Failures

**CWE Count**: 4 mapped CWEs

**What it is**: Insufficient logging, monitoring, and alerting that delays or prevents detection of breaches. This was A10 in 2017 and was elevated to ninth. Without adequate logging, attackers can persist undetected, escalate access, and exfiltrate data over extended periods. The average time to detect a breach exceeds 200 days in many industry studies.

**Key CWEs**: CWE-117 (Improper Output Neutralization for Logs), CWE-223 (Omission of Security-relevant Information), CWE-532 (Insertion of Sensitive Information into Log File), CWE-778 (Insufficient Logging).

**Code Patterns to Detect**:
- Login attempts, access control failures, and input validation failures that produce no log entries
- Log messages that lack context: no timestamp, no user identifier, no source IP, no action description
- Logs stored only on the local filesystem with no centralized aggregation
- No alerting rules for suspicious patterns (repeated auth failures, access from unusual locations, privilege escalation attempts)
- Sensitive data (passwords, tokens, PII) included in log messages
- Log injection vulnerabilities where user input is written directly into log entries without sanitization

**How to Prevent**: Log all authentication events, access control decisions, and input validation failures with sufficient context for forensic analysis. Use structured logging (JSON) that integrates with log management platforms. Ensure logs are tamper-evident (append-only, centralized). Establish alerting thresholds for security-relevant events. Create an incident response plan. Sanitize log content to prevent log injection and exclude sensitive data.

**STRIDE Mapping**: Repudiation
**CWE Mapping**: CWE-117, CWE-223, CWE-532, CWE-778

---

## A10:2021 - Server-Side Request Forgery (SSRF)

**CWE Count**: 1 mapped CWE (CWE-918) | **Incidence Rate**: 2.72% | **Occurrences**: 9,503

**What it is**: A new entry in 2021, added based on community survey data rather than incidence data alone. SSRF occurs when a server-side application fetches a remote resource using a URL that is fully or partially controlled by the attacker. The server becomes a proxy, allowing the attacker to reach internal services, cloud metadata endpoints, or other resources that are not directly accessible from the internet.

**Code Patterns to Detect**:
- HTTP client calls where the URL or hostname originates from user input (webhook registration, URL preview, file import from URL, PDF generation from user-supplied URLs)
- Missing validation of URL scheme, host, port, or destination before server-side fetch
- Allowing HTTP redirects that can route to internal addresses after initial URL validation passes
- No blocklist for private IP ranges (10.x, 172.16-31.x, 192.168.x, 169.254.x, 127.x) and cloud metadata endpoints (169.254.169.254)

**Code Example**:
```python
# VULNERABLE: user controls the URL, server fetches it
@app.post("/api/preview")
def preview_url(url: str):
    response = requests.get(url)
    return {"content": response.text}

# SECURE: validate scheme and block internal networks
@app.post("/api/preview")
def preview_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(400, "Invalid scheme")
    resolved_ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    if ipaddress.ip_address(resolved_ip).is_private:
        raise HTTPException(400, "Internal addresses not allowed")
    response = requests.get(url, allow_redirects=False, timeout=5)
    return {"content": response.text[:10000]}
```

**How to Prevent**: Segment remote resource access into an isolated network layer. Enforce deny-by-default firewall rules for outbound server traffic. Validate and sanitize all user-supplied URLs: allowlist schemes (https only where possible), block private and link-local IP ranges, block cloud metadata IPs. Disable HTTP redirects on server-side fetches. Do not return raw responses to clients.

**STRIDE Mapping**: Information Disclosure, Elevation of Privilege
**CWE Mapping**: CWE-918

---

## Cross-Framework Mappings

| OWASP Top 10 | STRIDE | CWE (Primary) | OWASP API Top 10 |
|---|---|---|---|
| A01 Broken Access Control | Elevation of Privilege, Info Disclosure | CWE-284, CWE-639 | API1 BOLA, API5 BFLA |
| A02 Cryptographic Failures | Info Disclosure, Tampering | CWE-327, CWE-311 | — |
| A03 Injection | Tampering, Info Disclosure, EoP | CWE-89, CWE-79 | API3 Object Property Auth |
| A04 Insecure Design | All | CWE-209, CWE-501 | API4 Resource Consumption, API6 Business Flows |
| A05 Security Misconfiguration | All | CWE-16, CWE-611 | API8 Misconfiguration |
| A06 Vulnerable Components | All | CWE-1035 | API9 Inventory Management |
| A07 Auth Failures | Spoofing, Repudiation | CWE-287, CWE-307 | API2 Broken Authentication |
| A08 Integrity Failures | Tampering, EoP | CWE-502, CWE-829 | API10 Unsafe Consumption |
| A09 Logging Failures | Repudiation | CWE-778, CWE-117 | — |
| A10 SSRF | Info Disclosure, EoP | CWE-918 | API7 SSRF |

---

## Compliance Mapping Template

```json
{
  "framework": "OWASP Top 10 2021",
  "requirement_id": "A01:2021",
  "requirement_name": "Broken Access Control",
  "cwe_ids": ["CWE-284", "CWE-639", "CWE-352"],
  "threats": ["threat-001", "threat-002"],
  "controls": ["control-001", "control-002"],
  "status": "partial|compliant|non-compliant",
  "gaps": ["gap-001"],
  "evidence": ["RBAC implemented in middleware", "Missing object-level checks in InvoiceController"]
}
```
