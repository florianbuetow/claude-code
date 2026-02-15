# STRIDE Threat Modeling Framework

## Overview

STRIDE is a threat categorization framework created by Praerit Garg and Loren Kohnfelder at Microsoft in 1999. It provides a structured approach to identifying security threats by decomposing a system into its components — processes, data stores, data flows, external entities, and trust boundaries — and then systematically asking what could go wrong in each category. Each STRIDE letter maps to the violation of a specific security property.

**How it works**: Build a Data Flow Diagram (DFD) of the system. For each element in the diagram, walk through the six STRIDE categories and ask whether that type of threat applies. Document each identified threat, assess its risk, and assign mitigations. The framework is deliberately exhaustive: it favors thoroughness over speed.

**When to use STRIDE**: Use STRIDE when you need per-component threat analysis of an application's architecture. It is the most widely adopted threat modeling framework and pairs well with OWASP Top 10 (which categorizes vulnerabilities by type) and DREAD (which scores individual findings). STRIDE answers "what could go wrong" while OWASP answers "what typically goes wrong" and DREAD answers "how bad is it."

---

## Categories

### S - Spoofing

**Security Property Violated**: Authentication

**What it is**: An attacker assumes the identity of another user, service, or component. Spoofing succeeds when the system cannot distinguish a legitimate entity from an impersonator. This includes both user-level identity spoofing (logging in as someone else) and system-level spoofing (one service impersonating another).

**Questions to Ask**:
- Can an attacker obtain or forge credentials that the system accepts?
- Are service-to-service calls authenticated, or does the system trust anything on the internal network?
- Can session tokens be stolen via XSS, network interception, or predictable generation?
- Is certificate validation enforced on all TLS connections, including internal services?
- Can an attacker replay a previously valid authentication token?

**Common Threats**:
- Credential theft through phishing, keylogging, or database breach, followed by reuse
- Session hijacking via stolen cookies (XSS, network sniffing on unencrypted connections)
- Token replay where a captured JWT or OAuth token is reused before expiration
- Service impersonation on internal networks where mutual TLS is not enforced
- IP address spoofing to bypass IP-based access controls
- Certificate forgery or acceptance of self-signed certificates due to disabled validation
- OAuth redirect manipulation to intercept authorization codes

**Code-Level Indicators**:
- Login endpoints that accept credentials without rate limiting or lockout
- JWT verification that does not enforce a specific algorithm (`alg: none` attack)
- HTTP client configurations with certificate verification disabled (`verify=False`, `rejectUnauthorized: false`)
- Session tokens generated with insufficient entropy (`Math.random()`, sequential IDs)
- Missing `SameSite`, `Secure`, or `HttpOnly` attributes on authentication cookies
- Service-to-service calls over HTTP without mutual authentication

**Typical Mitigations**:
- Multi-factor authentication for user-facing access
- Strong credential storage using adaptive hashing (Argon2, bcrypt)
- Cryptographically random session token generation with sufficient entropy
- Mutual TLS (mTLS) for service-to-service communication
- Token binding and short expiration with refresh token rotation
- Strict algorithm enforcement on JWT verification (`algorithms: ['RS256']`)
- Cookie attributes: `Secure`, `HttpOnly`, `SameSite=Strict`

---

### T - Tampering

**Security Property Violated**: Integrity

**What it is**: Unauthorized modification of data, code, or configuration. Tampering attacks target data in transit (intercepting and modifying network traffic), data at rest (directly modifying database records, files, or configuration), and data in use (manipulating values in memory or request parameters). The goal is to alter the system's behavior or state without authorization.

**Questions to Ask**:
- Can request parameters, headers, or body content be modified to alter server behavior?
- Are database records protected against unauthorized writes?
- Can an attacker modify files on disk (configuration, templates, uploaded content)?
- Is data integrity verified after transmission (checksums, signatures, HMAC)?
- Can build artifacts, deployment scripts, or infrastructure configurations be altered?

**Common Threats**:
- SQL injection altering persistent data (UPDATE/DELETE through crafted input)
- Parameter tampering in HTTP requests (changing prices, quantities, user IDs, or role flags)
- Man-in-the-middle modification of unencrypted network traffic
- File system manipulation via path traversal or insecure file upload
- Configuration tampering through exposed admin interfaces or environment variable injection
- Cookie or JWT modification to change claims (role escalation, session hijacking)
- Build pipeline tampering (modifying CI/CD scripts, injecting malicious build steps)

**Code-Level Indicators**:
- String concatenation in SQL, shell commands, or template rendering with user input
- Missing input validation on request bodies, allowing unexpected fields (`is_admin: true`)
- File operations using user-supplied paths without canonicalization or chroot
- Unsigned or unencrypted data crossing trust boundaries (cookies, hidden form fields, URL parameters)
- API endpoints accepting PUT/PATCH/DELETE without authorization checks
- Missing Content-Security-Policy headers enabling inline script injection

**Typical Mitigations**:
- Parameterized queries for all database operations
- Input validation using allowlists, not blocklists
- TLS for all data in transit, including internal service communication
- HMAC or digital signatures on data that crosses trust boundaries
- Immutable infrastructure with signed artifacts and verified deployments
- Write-access controls on all data stores, enforced at the application layer
- Content Security Policy headers restricting inline scripts and external sources

---

### R - Repudiation

**Security Property Violated**: Non-repudiation

**What it is**: A user or component performs an action and the system has no way to prove it happened. Repudiation is the ability to deny having taken an action. In a security context, the absence of reliable audit trails means malicious activity cannot be attributed, investigated, or used as evidence. This applies to both intentional denial (a malicious insider claiming they did not delete records) and unintentional gaps (no logs exist to determine what happened during an incident).

**Questions to Ask**:
- Are all security-relevant operations logged with sufficient detail to reconstruct events?
- Can log entries be modified or deleted by users or administrators?
- Do logs include identity information (who), timestamp (when), action (what), target (on what), and outcome (success/failure)?
- Is there a centralized, tamper-evident log store separate from the application servers?
- Can digital signatures or transaction receipts prove that an action occurred?

**Common Threats**:
- Missing audit logs for sensitive operations (fund transfers, permission changes, data exports)
- Log entries that lack user identity, making it impossible to attribute actions
- Logs stored on the same server as the application, allowing an attacker who compromises the server to also delete the evidence
- Log injection attacks where an attacker crafts input that corrupts or forges log entries
- Insufficient log retention that destroys evidence before an incident is discovered
- Clock skew between services making event correlation unreliable

**Code-Level Indicators**:
- Sensitive operations (login, data modification, admin actions) with no corresponding log statements
- Log statements that record the action but not the actor (`logger.info("record deleted")` with no user ID)
- Logs written to local files with no rotation, forwarding, or integrity protection
- User input written directly into log messages without sanitization (log injection)
- No audit trail for configuration changes, permission grants, or data access
- Missing timestamps or use of client-supplied timestamps instead of server-generated ones

**Typical Mitigations**:
- Structured audit logging for all security-relevant events with who/what/when/where/outcome
- Centralized log aggregation with append-only storage (WORM)
- Log sanitization to prevent injection (encode special characters in log entries)
- Server-side timestamps from a trusted, synchronized time source (NTP)
- Digital signatures on high-value transactions
- Log retention policies aligned with regulatory and forensic requirements
- Tamper-evident logging (hash chains, signed log entries)

---

### I - Information Disclosure

**Security Property Violated**: Confidentiality

**What it is**: Sensitive information is exposed to parties who should not have access to it. This covers both direct exposure (a data breach, an unprotected API endpoint returning user records) and indirect leakage (error messages revealing internal paths, timing differences that reveal whether a record exists, or metadata that exposes system architecture). The key question is not just "can they see it?" but "can they learn anything they should not know?"

**Questions to Ask**:
- Do error responses reveal internal system details (stack traces, database names, file paths, version numbers)?
- Are there API endpoints that return more data than the consumer needs?
- Can sensitive data be extracted through timing side channels (different response times for valid vs. invalid inputs)?
- Is personal or financial data encrypted in transit and at rest?
- Do logs contain sensitive information that could be accessed by support staff or leaked in a breach?
- Does the application expose metadata (HTTP headers, DNS records, source maps) that reveals technology stack or internal architecture?

**Common Threats**:
- Data breaches from SQL injection, broken access control, or misconfigured storage
- Verbose error messages exposing stack traces, query details, or file system paths
- Directory traversal attacks reading files outside the intended web root
- Timing attacks revealing whether accounts exist, passwords are partially correct, or records are present
- Information leakage through HTTP headers (`Server`, `X-Powered-By`, debug headers)
- Source map files deployed to production, exposing original source code
- Cached sensitive data accessible through browser history or shared proxy caches
- Memory dumps or core files containing secrets, tokens, or PII

**Code-Level Indicators**:
- Error handlers that pass exception details to the client response
- API endpoints returning entire database objects instead of projected response schemas
- `SELECT *` queries where not all columns should be visible to the requesting user
- Sensitive data in URL query parameters (visible in browser history, server logs, referrer headers)
- Missing `Cache-Control: no-store` on responses containing sensitive data
- Debug or development endpoints accessible in production
- Source maps deployed alongside minified JavaScript bundles

**Typical Mitigations**:
- Generic error responses to clients with detailed errors logged server-side only
- Explicit response schemas that project only the fields the consumer needs
- Encryption at rest (AES-256) and in transit (TLS 1.2+) for all sensitive data
- Constant-time comparison functions for secrets to prevent timing attacks
- Removal of server version headers, debug endpoints, and source maps in production
- Data classification and access controls based on sensitivity level
- Redaction of sensitive fields in logs, metrics, and traces

---

### D - Denial of Service

**Security Property Violated**: Availability

**What it is**: Degrading or destroying the ability of legitimate users to access the system. At the application level, this includes attacks that exhaust CPU, memory, disk, or network resources, as well as logic-level attacks that trigger expensive operations, lock accounts, corrupt state, or crash processes. Application-layer DoS is often more efficient than network-layer flooding because a single crafted request can consume disproportionate resources.

**Questions to Ask**:
- Are there endpoints that perform expensive operations (large queries, file processing, report generation) without rate limiting?
- Can an attacker trigger algorithmic complexity attacks (regex backtracking, hash collision flooding, deeply nested JSON)?
- Are there single points of failure where one crashed component takes down the entire system?
- Can an attacker lock out legitimate users by triggering account lockout mechanisms?
- Are file upload endpoints bounded by size and count limits?
- Can WebSocket or long-polling connections be opened in bulk to exhaust connection pools?

**Common Threats**:
- Resource exhaustion via unbounded queries (missing LIMIT, no pagination, full table scans)
- Regular expression denial of service (ReDoS) through crafted input that triggers catastrophic backtracking
- Zip bombs, XML bombs (billion laughs), or decompression bombs that expand to consume all memory
- Hash collision attacks against hash maps with predictable hashing functions
- Account lockout abuse — locking out legitimate users by deliberately failing their login attempts
- Connection pool exhaustion via slow-read or slow-write attacks (Slowloris)
- Disk exhaustion through unlimited log output, file uploads, or temp file creation

**Code-Level Indicators**:
- Database queries without `LIMIT` or pagination parameters
- Regular expressions with nested quantifiers or overlapping alternations applied to user input
- File upload handlers without size limits or file count limits
- No timeout on external HTTP calls, database queries, or background jobs
- Synchronous processing of expensive operations on the main request thread
- Missing circuit breakers on calls to downstream services
- Unbounded in-memory collections built from user input (reading a request body into a list without size check)

**Typical Mitigations**:
- Rate limiting per client, per endpoint, and globally
- Server-side pagination with enforced maximum page sizes
- Input size limits on request bodies, file uploads, and URL parameters
- Timeouts on all I/O operations (database queries, HTTP calls, file operations)
- Circuit breakers on calls to external dependencies
- ReDoS-safe regular expressions (use RE2 or bounded backtracking engines)
- Async processing for expensive operations with queue-based throttling
- Resource quotas per tenant or user in multi-tenant systems

---

### E - Elevation of Privilege

**Security Property Violated**: Authorization

**What it is**: An attacker gains capabilities beyond what they are authorized to have. This is distinct from spoofing (pretending to be someone else) — elevation of privilege means acting as yourself but gaining permissions you should not have. This includes vertical escalation (regular user gains admin access), horizontal escalation (user A accesses user B's data), and exploitation of trust boundaries (code running in a sandbox escapes to the host).

**Questions to Ask**:
- Can a user perform actions that should require a higher privilege level?
- Are authorization checks enforced on every operation, or only at the UI layer?
- Can an attacker modify their own role or permissions through the application's interface?
- Are there default accounts with elevated privileges that are not disabled?
- Can trust boundaries be bypassed (escaping a container, breaking out of a sandbox, exploiting kernel vulnerabilities from user space)?

**Common Threats**:
- Insecure direct object references (IDOR) — accessing resources belonging to other users by manipulating IDs
- Missing function-level access control — admin endpoints accessible to regular users
- JWT manipulation — changing the `role` claim in an unsigned or weakly signed token
- Mass assignment — sending unexpected fields in a request body that the server binds to the data model (`{"is_admin": true}`)
- SQL injection used for privilege escalation (reading the admin password hash, modifying role tables)
- Container escape from a compromised application to the host system
- Insecure deserialization leading to arbitrary code execution with the application's privileges

**Code-Level Indicators**:
- Authorization checks present on some endpoints but missing on others (inconsistent enforcement)
- Role checks implemented in client-side code only (JavaScript that hides admin buttons but the API accepts the request)
- Request body bound directly to database models without field allowlisting (mass assignment)
- Route definitions for admin functionality that only check authentication, not authorization
- Docker containers running as root or with excessive Linux capabilities
- `sudo` or `setuid` binaries invoked from application code
- Missing `@require_role` or equivalent authorization decorators on privileged endpoints

**Typical Mitigations**:
- Principle of least privilege applied to all accounts, services, and processes
- Centralized authorization enforcement in middleware or framework interceptors
- Object-level authorization checks on every resource access (not just endpoint-level)
- Explicit field allowlists for all data binding operations (reject unknown fields)
- Container security hardening (non-root user, minimal capabilities, read-only filesystem)
- Regular privilege audits comparing defined RBAC policies against actual access patterns
- Deny by default with explicit grants rather than deny with explicit denials

---

## Applying STRIDE

### Per-Element Threat Analysis

Apply STRIDE to each element in the Data Flow Diagram. The table below shows which threat categories are most relevant to each element type. All six categories can technically apply to any element, but the highlighted mappings represent the primary threats to analyze.

| Element Type | Primary STRIDE Threats | Notes |
|---|---|---|
| External Entity | **S**, **R** | External entities are the primary source of spoofing (impersonation) and repudiation (denying actions). They cannot typically be tampering targets themselves but they can be the source of tampering attacks. |
| Process | **S**, **T**, **R**, **I**, **D**, **E** | Processes are subject to all six categories. They are where most application logic vulnerabilities manifest. |
| Data Store | **T**, **I**, **D** | Data stores are primarily concerned with integrity (unauthorized modification), confidentiality (unauthorized read), and availability (corruption or exhaustion). Repudiation may also apply if the data store holds audit logs. |
| Data Flow | **T**, **I**, **D** | Data flows are vulnerable to interception (information disclosure), modification (tampering), and disruption (denial of service). Encryption and authentication of the channel are the primary defenses. |
| Trust Boundary | All categories | Trust boundaries are not elements themselves but markers where the threat profile changes. Analyze every element and flow that crosses a trust boundary with heightened scrutiny. |

### Per-Interaction Analysis

For each data flow that crosses a trust boundary:

1. **Identify participants**: What is sending and what is receiving? What trust level does each have?
2. **Walk through STRIDE**: For each of the six categories, ask whether this specific interaction is vulnerable.
3. **Document threats**: Record each identified threat with its target element, category, and a description of how it could be exploited.
4. **Assess risk**: Use a risk scoring method (DREAD, likelihood-impact matrix, or CVSS) to prioritize.
5. **Assign mitigations**: For each threat, identify specific technical controls that reduce the risk.

### Risk Assessment Matrix

| Likelihood / Impact | Low | Medium | High | Critical |
|---|---|---|---|---|
| Almost Certain (5) | Medium | High | Critical | Critical |
| Likely (4) | Low | Medium | High | Critical |
| Possible (3) | Low | Medium | Medium | High |
| Unlikely (2) | Low | Low | Medium | Medium |
| Rare (1) | Low | Low | Low | Medium |

### Documentation Template

For each threat identified:

```markdown
### [THREAT-ID]: Threat Title

**Category**: [STRIDE letter and name]
**Element**: [DFD element affected]
**Trust Boundary**: [Which boundary is relevant, if any]
**Risk Score**: [1-25 from matrix, or DREAD score]

**Description**:
[What the threat is, what the attacker does, and what the consequence is]

**Attack Scenario**:
1. [Step 1 of the attack]
2. [Step 2 of the attack]
3. [Resulting impact]

**Existing Controls**:
- [What mitigations are already in place]

**Gaps**:
- [What is missing]

**Recommended Mitigations**:
1. [Specific mitigation with implementation guidance]
2. [Additional mitigation]

**OWASP Mapping**: [A01-A10 category, if applicable]
**CWE**: [Most relevant CWE ID]
```

---

## Cross-Framework Mappings

### STRIDE to OWASP Top 10

| STRIDE | Primary OWASP Top 10 Categories |
|---|---|
| S: Spoofing | A07 Identification and Authentication Failures |
| T: Tampering | A03 Injection, A08 Software and Data Integrity Failures |
| R: Repudiation | A09 Security Logging and Monitoring Failures |
| I: Information Disclosure | A01 Broken Access Control, A02 Cryptographic Failures |
| D: Denial of Service | A04 Insecure Design, A05 Security Misconfiguration |
| E: Elevation of Privilege | A01 Broken Access Control |

### STRIDE to Security Properties

| STRIDE | Security Property | Control Family |
|---|---|---|
| Spoofing | Authentication | Identity management, MFA, credential storage |
| Tampering | Integrity | Input validation, encryption, signing, checksums |
| Repudiation | Non-repudiation | Audit logging, digital signatures, timestamps |
| Information Disclosure | Confidentiality | Encryption, access control, data classification |
| Denial of Service | Availability | Rate limiting, redundancy, circuit breakers |
| Elevation of Privilege | Authorization | RBAC, least privilege, object-level authorization |
