# SANS/CWE Top 25 Most Dangerous Software Weaknesses (2023)

> **Note:** This reference is based on the 2023 edition. The CWE Top 25 is published annually — check the [official MITRE CWE Top 25 page](https://cwe.mitre.org/top25/) for the current list.

## Overview

The CWE Top 25 is a list of the most dangerous software weaknesses, published annually by MITRE in collaboration with SANS. Unlike the OWASP Top 10, which focuses on web application risk categories, the CWE Top 25 identifies specific, code-level weakness types ranked by prevalence and severity using real-world CVE data from the National Vulnerability Database (NVD).

**How it's calculated**: Each CWE is scored by analyzing CVEs published in the previous two calendar years. The score combines frequency (how many CVEs map to the CWE) and severity (average CVSS score of those CVEs). This data-driven approach makes the list an objective measure of what weaknesses are actually being exploited.

**How it differs from OWASP Top 10**: OWASP categories are broad risk groupings (e.g., "Injection" covers SQL, OS command, LDAP, and more). CWE entries are specific, enumerated weakness types (e.g., CWE-89 is specifically SQL injection). Multiple CWE entries may fall under a single OWASP category.

---

## Memory Safety Weaknesses

### Rank 1: CWE-787 — Out-of-bounds Write

**Description**: The software writes data past the end or before the beginning of an allocated buffer. This can cause data corruption, crashes, or arbitrary code execution.

**Code-Level Indicators**:
- Buffer operations without bounds checking in C/C++
- `memcpy()`, `strcpy()`, `strcat()` without size validation
- Array index from user input without bounds check
- Off-by-one errors in loop bounds

**Cross-Framework Mappings**:
- OWASP: A03 Injection (when exploited for code execution)
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1190 Exploit Public-Facing App

**Severity**: Critical — commonly leads to remote code execution.

---

### Rank 7: CWE-125 — Out-of-bounds Read

**Description**: The software reads data past the end or before the beginning of an allocated buffer. This can leak sensitive information from memory (e.g., Heartbleed).

**Code-Level Indicators**:
- Reading array elements with unchecked index
- String operations on non-null-terminated strings in C/C++
- Buffer reads using externally supplied length values
- Pointer arithmetic without bounds validation

**Cross-Framework Mappings**:
- OWASP: A02 Cryptographic Failures (information exposure)
- STRIDE: Information Disclosure
- ATT&CK: T1005 Data from Local System

**Severity**: High — enables information disclosure and can bypass ASLR.

---

### Rank 4: CWE-416 — Use After Free

**Description**: The software references memory after it has been freed, leading to undefined behavior, crashes, or code execution.

**Code-Level Indicators**:
- Pointer used after `free()` or `delete`
- Dangling references to deallocated objects
- Callback functions referencing freed context
- Race conditions between deallocation and use

**Cross-Framework Mappings**:
- OWASP: A04 Insecure Design
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1190 Exploit Public-Facing App, T1068 Exploitation for Privilege Escalation

**Severity**: Critical — commonly leads to arbitrary code execution.

---

### Rank 12: CWE-476 — NULL Pointer Dereference

**Description**: The software dereferences a pointer that is expected to be valid but is NULL, causing a crash or denial of service.

**Code-Level Indicators**:
- Missing null checks after memory allocation
- Return values from functions not checked for null
- Pointer access after error conditions
- Chained method calls without null guards

**Cross-Framework Mappings**:
- OWASP: A04 Insecure Design
- STRIDE: Denial of Service
- ATT&CK: T1498 Network Denial of Service (application-level)

**Severity**: Medium — typically causes denial of service, rarely code execution.

---

### Rank 14: CWE-190 — Integer Overflow or Wraparound

**Description**: An integer value is incremented past its maximum value, wrapping around to a small or negative value. This often leads to buffer overflows when the result is used for memory allocation or bounds checking.

**Code-Level Indicators**:
- Arithmetic on integer types without overflow checks
- User-supplied values used in size calculations
- Multiplication of two user-controlled values for buffer allocation
- Implicit type conversions between signed and unsigned integers

**Cross-Framework Mappings**:
- OWASP: A03 Injection (when leading to buffer overflow)
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1190 Exploit Public-Facing App

**Severity**: High — often a prerequisite for buffer overflow exploitation.

---

### Rank 17: CWE-119 — Improper Restriction of Operations within the Bounds of a Memory Buffer

**Description**: Parent category for buffer errors. The software performs operations on a memory buffer without properly restricting read/write to intended boundaries.

**Code-Level Indicators**:
- All indicators from CWE-787 and CWE-125
- Any C/C++ code handling raw buffers without bounds enforcement
- Use of unsafe string functions (`gets()`, `sprintf()`, `scanf()`)
- Stack-based buffers receiving variable-length input

**Cross-Framework Mappings**:
- OWASP: A03 Injection
- STRIDE: Tampering, Elevation of Privilege, Information Disclosure
- ATT&CK: T1190 Exploit Public-Facing App

**Severity**: Critical — foundational weakness underlying many exploits.

---

## Injection Weaknesses

### Rank 2: CWE-79 — Improper Neutralization of Input During Web Page Generation (Cross-site Scripting)

**Description**: The application includes user-controlled data in web page output without proper neutralization, allowing attackers to execute scripts in victims' browsers.

**Code-Level Indicators**:
- `innerHTML`, `outerHTML`, `document.write()` with user data
- Template variables rendered without escaping (`{!! $var !!}` in Blade, `| safe` in Jinja2)
- Reflected URL parameters in page output
- User content stored and rendered to other users (stored XSS)
- jQuery `.html()`, `.append()` with unsanitized input
- Missing Content-Security-Policy headers

**Cross-Framework Mappings**:
- OWASP: A03 Injection
- STRIDE: Tampering, Information Disclosure, Elevation of Privilege
- ATT&CK: T1203 Exploitation for Client Execution, T1185 Browser Session Hijacking

**Severity**: High — enables session hijacking, credential theft, defacement.

---

### Rank 3: CWE-89 — Improper Neutralization of Special Elements used in an SQL Command (SQL Injection)

**Description**: The application constructs SQL statements using user-controlled input without proper sanitization or parameterization.

**Code-Level Indicators**:
- String concatenation or interpolation in SQL queries
- `f"SELECT ... WHERE id = {user_input}"` patterns
- ORM raw query methods with unsanitized parameters
- Dynamic table or column names from user input
- Stored procedures constructed with string concatenation

**Cross-Framework Mappings**:
- OWASP: A03 Injection
- STRIDE: Tampering, Information Disclosure, Elevation of Privilege
- ATT&CK: T1190 Exploit Public-Facing App, T1059 Command and Scripting

**Severity**: Critical — enables data theft, modification, deletion, and sometimes OS command execution.

---

### Rank 5: CWE-78 — Improper Neutralization of Special Elements used in an OS Command (OS Command Injection)

**Description**: The application constructs OS commands using user-controlled input without proper sanitization.

**Code-Level Indicators**:
- `os.system()`, `subprocess.call(shell=True)` with user input (Python)
- `Runtime.exec()` with concatenated user input (Java)
- `child_process.exec()` with user input (Node.js)
- Backtick execution with user data (Ruby, Perl, PHP)
- `system()`, `popen()`, `exec()` in C/C++ with user input

**Cross-Framework Mappings**:
- OWASP: A03 Injection
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1059 Command and Scripting Interpreter

**Severity**: Critical — enables full system compromise.

---

### Rank 23: CWE-94 — Improper Control of Generation of Code (Code Injection)

**Description**: The application constructs code segments using user-controlled input, allowing attackers to inject and execute arbitrary code.

**Code-Level Indicators**:
- `eval()` with user input in any language
- `Function()` constructor with user data (JavaScript)
- Template injection (`{{ user_input }}` in server-side templates)
- Dynamic class loading or reflection with user-controlled class names
- `exec()` or `compile()` with user input (Python)

**Cross-Framework Mappings**:
- OWASP: A03 Injection
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1059 Command and Scripting Interpreter

**Severity**: Critical — enables arbitrary code execution in application context.

---

### Rank 16: CWE-77 — Improper Neutralization of Special Elements used in a Command (Command Injection)

**Description**: General command injection where user input is incorporated into a command without neutralization. Broader than CWE-78 (OS-specific).

**Code-Level Indicators**:
- User input passed to any command interpreter
- LDAP queries constructed with user input
- Mail commands with user-controlled headers
- Application-specific command languages with user input
- Build/deployment scripts parameterized with user data

**Cross-Framework Mappings**:
- OWASP: A03 Injection
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1059 Command and Scripting Interpreter

**Severity**: Critical — scope depends on the target command interpreter.

---

## Authentication and Authorization Weaknesses

### Rank 11: CWE-862 — Missing Authorization

**Description**: The software does not perform an authorization check when a user attempts to access a resource or perform an action.

**Code-Level Indicators**:
- API endpoints without authorization middleware or decorators
- Direct object references without ownership validation
- Admin functionality accessible without role checks
- Missing `@authorize`, `@login_required`, or equivalent annotations
- Horizontal privilege escalation (accessing other users' data)

**Cross-Framework Mappings**:
- OWASP: A01 Broken Access Control
- STRIDE: Elevation of Privilege, Information Disclosure
- ATT&CK: T1548 Abuse Elevation Control Mechanism

**Severity**: High — enables unauthorized access to data and functionality.

---

### Rank 24: CWE-863 — Incorrect Authorization

**Description**: The software performs authorization checks but does so incorrectly, allowing attackers to bypass intended access restrictions.

**Code-Level Indicators**:
- Authorization based on client-supplied role claims
- JWT `alg` field not validated (allowing `none` algorithm)
- Role checks comparing strings case-insensitively when case matters
- Authorization decisions based on request path (bypassable via path traversal or encoding)
- Incomplete graph traversal in permission checks

**Cross-Framework Mappings**:
- OWASP: A01 Broken Access Control
- STRIDE: Elevation of Privilege
- ATT&CK: T1548 Abuse Elevation Control Mechanism

**Severity**: High — the application believes it is protected but is not.

---

### Rank 20: CWE-306 — Missing Authentication for Critical Function

**Description**: The software does not require authentication for functionality that requires a verified identity.

**Code-Level Indicators**:
- Admin panels accessible without login
- API endpoints performing sensitive operations without authentication middleware
- Password reset or account modification without re-authentication
- Internal/debug endpoints exposed without auth
- Microservice-to-microservice calls without authentication

**Cross-Framework Mappings**:
- OWASP: A07 Identification and Authentication Failures
- STRIDE: Spoofing
- ATT&CK: T1078 Valid Accounts (bypassing the need for them)

**Severity**: Critical — eliminates the primary security boundary.

---

### Rank 13: CWE-287 — Improper Authentication

**Description**: The software does not properly verify that a user is who they claim to be.

**Code-Level Indicators**:
- Authentication bypass via parameter manipulation
- Weak password comparison (timing-safe comparison not used)
- Custom authentication schemes with logic flaws
- Session fixation (accepting pre-set session IDs)
- Missing brute-force protection
- MFA bypass through alternative paths

**Cross-Framework Mappings**:
- OWASP: A07 Identification and Authentication Failures
- STRIDE: Spoofing
- ATT&CK: T1078 Valid Accounts, T1110 Brute Force

**Severity**: Critical — undermines all identity-based access controls.

---

## Data Handling Weaknesses

### Rank 6: CWE-20 — Improper Input Validation

**Description**: The software does not validate or incorrectly validates input, allowing attackers to craft input that is not expected by the rest of the application.

**Code-Level Indicators**:
- Missing validation on request parameters, headers, or body
- Type coercion without explicit validation
- Numeric inputs not checked for range or sign
- String inputs not checked for length, format, or allowed characters
- File names or paths accepted without sanitization
- Blocklist-based validation instead of allowlist

**Cross-Framework Mappings**:
- OWASP: A03 Injection (enabler for many injection types)
- STRIDE: Tampering
- ATT&CK: T1190 Exploit Public-Facing App

**Severity**: High — root cause of many other weaknesses; severity depends on downstream use.

---

### Rank 8: CWE-22 — Improper Limitation of a Pathname to a Restricted Directory (Path Traversal)

**Description**: The software uses user-controlled input to construct file paths without properly neutralizing sequences like `../` that can resolve outside the intended directory.

**Code-Level Indicators**:
- File operations with user-supplied filenames
- `../` sequences not stripped or detected
- Path construction using string concatenation
- `os.path.join()` with user input (does not prevent absolute paths)
- File download/upload endpoints with user-controlled paths
- Archive extraction without path validation (zip slip)

**Cross-Framework Mappings**:
- OWASP: A01 Broken Access Control
- STRIDE: Information Disclosure, Tampering
- ATT&CK: T1005 Data from Local System

**Severity**: High — enables reading sensitive files (e.g., `/etc/passwd`, application config).

---

### Rank 15: CWE-502 — Deserialization of Untrusted Data

**Description**: The application deserializes data from untrusted sources without verification, potentially allowing attackers to execute arbitrary code or manipulate application state.

**Code-Level Indicators**:
- `pickle.loads()`, `yaml.load()` (without `SafeLoader`) in Python
- `ObjectInputStream.readObject()` in Java
- `unserialize()` in PHP
- `Marshal.load()` in Ruby
- `JSON.parse()` with reviver functions that instantiate classes
- Any deserialization of data from cookies, headers, or request parameters

**Cross-Framework Mappings**:
- OWASP: A08 Software and Data Integrity Failures
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1190 Exploit Public-Facing App, T1059 Command and Scripting

**Severity**: Critical — commonly leads to remote code execution.

---

### Rank 19: CWE-918 — Server-Side Request Forgery (SSRF)

**Description**: The application fetches a URL provided by the user without validating that the destination is permitted, allowing attackers to reach internal services.

**Code-Level Indicators**:
- URL parameters passed to HTTP client libraries (`requests.get(user_url)`)
- Image/document fetching from user-supplied URLs
- Webhook URLs without destination validation
- URL parsers with inconsistent behavior (bypass via `http://127.0.0.1` variants)
- PDF generators or HTML renderers that fetch external resources

**Cross-Framework Mappings**:
- OWASP: A10 Server-Side Request Forgery
- STRIDE: Information Disclosure, Elevation of Privilege
- ATT&CK: T1190 Exploit Public-Facing App, T1005 Data from Local System

**Severity**: High to Critical — enables access to internal services, cloud metadata endpoints, and internal networks.

---

## Configuration Weaknesses

### Rank 18: CWE-798 — Use of Hard-coded Credentials

**Description**: The software contains hard-coded credentials such as passwords, API keys, or cryptographic keys embedded in source code.

**Code-Level Indicators**:
- String literals matching password/key patterns in source code
- `password = "..."`, `api_key = "..."`, `secret = "..."` in code
- Connection strings with embedded credentials
- Default credentials in configuration files
- SSH keys or certificates bundled in the application
- Base64-encoded credentials in source files

**Cross-Framework Mappings**:
- OWASP: A07 Identification and Authentication Failures
- STRIDE: Spoofing, Information Disclosure
- ATT&CK: T1552 Unsecured Credentials, T1078 Valid Accounts

**Severity**: Critical — credentials are discoverable by anyone with access to the code or binary.

---

### Rank 25: CWE-276 — Incorrect Default Permissions

**Description**: The software sets insecure default permissions during installation or file creation, allowing unauthorized access.

**Code-Level Indicators**:
- File creation with world-readable/writable permissions (`chmod 777`, `0o777`)
- `umask(0)` before file operations
- Directories created with overly permissive access
- Configuration files with sensitive data readable by all users
- Docker containers running as root
- Cloud storage buckets with public access by default

**Cross-Framework Mappings**:
- OWASP: A05 Security Misconfiguration
- STRIDE: Information Disclosure, Tampering, Elevation of Privilege
- ATT&CK: T1552 Unsecured Credentials

**Severity**: Medium to High — depends on the sensitivity of the exposed resources.

---

### Rank 25 (cont.): CWE-732 — Incorrect Permission Assignment for Critical Resource

**Note**: While not in the 2023 Top 25 list, this is closely related to CWE-276 and frequently encountered. It covers cases where permissions are explicitly set incorrectly (not just defaults).

---

## Other Weaknesses

### Rank 9: CWE-352 — Cross-Site Request Forgery (CSRF)

**Description**: The application does not verify that a state-changing request was intentionally submitted by the authenticated user, allowing attackers to forge requests.

**Code-Level Indicators**:
- State-changing operations using GET requests
- POST endpoints without CSRF tokens
- Missing `SameSite` attribute on session cookies
- CSRF tokens not validated server-side
- CORS configured with `Access-Control-Allow-Origin: *` on authenticated endpoints
- AJAX requests without anti-CSRF headers

**Cross-Framework Mappings**:
- OWASP: A01 Broken Access Control
- STRIDE: Elevation of Privilege (acting as another user)
- ATT&CK: T1204 User Execution

**Severity**: High — enables attackers to perform any action the victim can perform.

---

### Rank 10: CWE-434 — Unrestricted Upload of File with Dangerous Type

**Description**: The application allows file uploads without properly restricting file types, enabling attackers to upload executable content.

**Code-Level Indicators**:
- File upload without server-side type validation
- Type validation based on file extension only (not content/magic bytes)
- Uploaded files stored in web-accessible directories
- Missing file size limits
- File names not sanitized (path traversal in filenames)
- MIME type from `Content-Type` header trusted without verification

**Cross-Framework Mappings**:
- OWASP: A04 Insecure Design, A05 Security Misconfiguration
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1505.003 Web Shell

**Severity**: Critical — can lead to remote code execution via web shell upload.

---

### Rank 21: CWE-362 — Concurrent Execution Using Shared Resource with Improper Synchronization (Race Condition)

**Description**: The software contains a sequence of operations that requires exclusive access to a shared resource, but a timing window exists where another process can modify the resource.

**Code-Level Indicators**:
- Check-then-act patterns without locking (TOCTOU)
- Shared mutable state without synchronization
- File operations that check existence before create/write
- Financial operations without transaction isolation
- Counter increments without atomic operations
- Session state modified by concurrent requests

**Cross-Framework Mappings**:
- OWASP: A04 Insecure Design
- STRIDE: Tampering, Elevation of Privilege
- ATT&CK: T1068 Exploitation for Privilege Escalation

**Severity**: Medium to High — often exploitable in financial transactions and authentication flows.

---

### Rank 22: CWE-269 — Improper Privilege Management

**Description**: The software does not properly manage the assignment, modification, tracking, or revocation of privileges.

**Code-Level Indicators**:
- Applications running with elevated privileges unnecessarily
- Service accounts with more permissions than needed
- Missing privilege drop after initialization
- Role changes not requiring re-authentication
- Privilege inheritance through object relationships not reviewed
- Missing separation of duties in critical operations

**Cross-Framework Mappings**:
- OWASP: A01 Broken Access Control, A04 Insecure Design
- STRIDE: Elevation of Privilege
- ATT&CK: T1548 Abuse Elevation Control Mechanism

**Severity**: High — excess privileges amplify the impact of any compromise.

---

## Cross-Framework Mapping Table

| CWE | Name | OWASP Top 10 | STRIDE | ATT&CK |
|-----|------|-------------|--------|--------|
| CWE-787 | Out-of-bounds Write | A03 Injection | T, E | T1190 |
| CWE-79 | Cross-site Scripting | A03 Injection | T, I, E | T1203, T1185 |
| CWE-89 | SQL Injection | A03 Injection | T, I, E | T1190, T1059 |
| CWE-416 | Use After Free | A04 Insecure Design | T, E | T1190, T1068 |
| CWE-78 | OS Command Injection | A03 Injection | T, E | T1059 |
| CWE-20 | Improper Input Validation | A03 Injection | T | T1190 |
| CWE-125 | Out-of-bounds Read | A02 Crypto Failures | I | T1005 |
| CWE-22 | Path Traversal | A01 Access Control | I, T | T1005 |
| CWE-352 | Cross-Site Request Forgery | A01 Access Control | E | T1204 |
| CWE-434 | Unrestricted Upload | A04 Insecure Design | T, E | T1505.003 |
| CWE-862 | Missing Authorization | A01 Access Control | E, I | T1548 |
| CWE-476 | NULL Pointer Dereference | A04 Insecure Design | D | T1498 |
| CWE-287 | Improper Authentication | A07 Auth Failures | S | T1078, T1110 |
| CWE-190 | Integer Overflow | A03 Injection | T, E | T1190 |
| CWE-502 | Deserialization | A08 Integrity Failures | T, E | T1190, T1059 |
| CWE-77 | Command Injection | A03 Injection | T, E | T1059 |
| CWE-119 | Memory Buffer Errors | A03 Injection | T, E, I | T1190 |
| CWE-798 | Hard-coded Credentials | A07 Auth Failures | S, I | T1552, T1078 |
| CWE-918 | SSRF | A10 SSRF | I, E | T1190, T1005 |
| CWE-306 | Missing Authentication | A07 Auth Failures | S | T1078 |
| CWE-362 | Race Condition | A04 Insecure Design | T, E | T1068 |
| CWE-269 | Improper Privilege Mgmt | A01 Access Control | E | T1548 |
| CWE-94 | Code Injection | A03 Injection | T, E | T1059 |
| CWE-863 | Incorrect Authorization | A01 Access Control | E | T1548 |
| CWE-276 | Incorrect Default Perms | A05 Misconfiguration | I, T, E | T1552 |

**STRIDE key**: S=Spoofing, T=Tampering, R=Repudiation, I=Information Disclosure, D=Denial of Service, E=Elevation of Privilege

---

## Compliance Mapping Template

```json
{
  "framework": "CWE Top 25 (2023)",
  "cwe_id": "CWE-89",
  "cwe_name": "SQL Injection",
  "rank": 3,
  "finding": "Unsanitized user input in database query",
  "owasp_mapping": "A03:2021",
  "stride_mapping": ["Tampering", "Information Disclosure", "Elevation of Privilege"],
  "attck_mapping": ["T1190", "T1059"],
  "severity": "critical",
  "code_location": "src/api/users.py:42",
  "remediation": "Use parameterized queries via ORM or prepared statements"
}
```
