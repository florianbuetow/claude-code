# MITRE ATT&CK for Application Security

## Overview

MITRE ATT&CK (Adversarial Tactics, Techniques, and Common Knowledge) is a knowledge base of adversary behavior based on real-world observations. Unlike vulnerability frameworks such as OWASP Top 10 or CWE, ATT&CK describes what attackers **do** rather than what code flaws exist. It catalogs attacker tactics (goals) and techniques (methods) across the entire attack lifecycle.

**Key distinction**: OWASP and CWE describe weaknesses in software. ATT&CK describes how adversaries exploit those weaknesses and what they do after gaining access. A single vulnerability (e.g., SQL injection) may enable multiple ATT&CK techniques across several tactics.

**Why ATT&CK matters for appsec**: Understanding attacker behavior helps developers anticipate how vulnerabilities will be chained together. A finding is more actionable when mapped to a kill chain showing reconnaissance through exfiltration.

---

## AppSec-Relevant Tactics

ATT&CK defines 14 tactics. The following 10 are most relevant to application security analysis. Each tactic represents an adversary goal, and techniques describe how that goal is achieved.

---

### TA0043 - Reconnaissance

**Goal**: The adversary is trying to gather information about your application to plan an attack.

**Key Techniques**:

**T1592 - Gather Victim Host Information**
Attackers enumerate technology stacks, server versions, and framework details exposed by the application.
- **Code patterns that enable this**: Verbose error pages exposing stack traces, server version headers (`X-Powered-By`, `Server`), debug endpoints left in production, publicly accessible `/info` or `/health` endpoints revealing internal details.

**T1593 - Search Open Websites/Domains**
Attackers discover API endpoints, developer documentation, and leaked credentials by searching public sources.
- **Code patterns that enable this**: API documentation served without authentication, `.env` files or config committed to public repositories, verbose robots.txt revealing internal paths, sitemap.xml exposing admin routes.

**T1595 - Active Scanning**
Attackers probe the application for vulnerabilities by sending crafted requests.
- **Code patterns that enable this**: Missing rate limiting on endpoints, no WAF or input filtering, application responds differently to valid vs. invalid input (enabling enumeration), lack of CAPTCHA on public forms.

**T1589 - Gather Victim Identity Information**
Attackers collect user emails, credentials, and account details from exposed endpoints.
- **Code patterns that enable this**: User enumeration via login error messages ("user not found" vs. "wrong password"), public user profiles leaking email addresses, password reset flows that confirm account existence.

---

### TA0001 - Initial Access

**Goal**: The adversary is trying to get into the application or its infrastructure.

**Key Techniques**:

**T1190 - Exploit Public-Facing Application**
Attackers exploit vulnerabilities in internet-facing applications to gain access. This is the most critical technique for appsec.
- **Code patterns that enable this**: SQL injection (unsanitized query construction), command injection (user input in shell commands), path traversal (unsanitized file paths), SSRF (unvalidated URL fetching), deserialization of untrusted data, template injection.
- **OWASP mapping**: A03 Injection, A10 SSRF, A08 Software Integrity Failures.

**T1078 - Valid Accounts**
Attackers use stolen, default, or brute-forced credentials to access the application as a legitimate user.
- **Code patterns that enable this**: Default credentials in deployment configs, weak password policies, missing MFA enforcement, session tokens that don't expire, API keys embedded in client-side code, lack of brute-force protection.
- **OWASP mapping**: A07 Identification and Authentication Failures.

**T1566 - Phishing**
Attackers send crafted messages to trick users into revealing credentials or executing malicious actions.
- **Code patterns that enable this**: Application does not implement SPF/DKIM/DMARC for outbound email, missing anti-phishing indicators in legitimate communications, open redirects that can be abused in phishing URLs, lack of user security awareness features.

**T1195 - Supply Chain Compromise**
Attackers compromise third-party dependencies to inject malicious code into the application.
- **Code patterns that enable this**: Unpinned dependency versions, no integrity verification (missing lock files, no checksum validation), pulling packages from untrusted registries, CI/CD pipelines without dependency scanning.
- **OWASP mapping**: A06 Vulnerable and Outdated Components, A08 Software Integrity Failures.

---

### TA0002 - Execution

**Goal**: The adversary is trying to run malicious code within the application context.

**Key Techniques**:

**T1059 - Command and Scripting Interpreter**
Attackers execute commands through interpreters accessible via the application.
- **Code patterns that enable this**: `eval()`, `exec()`, `system()`, `child_process.exec()` with user input; template engines with unrestricted execution; server-side JavaScript evaluation; SQL `xp_cmdshell` or similar stored procedures.
- **CWE mapping**: CWE-78 OS Command Injection, CWE-94 Code Injection.

**T1203 - Exploitation for Client Execution**
Attackers exploit vulnerabilities to execute code in the user's browser or client application.
- **Code patterns that enable this**: Cross-site scripting (XSS) — reflected, stored, or DOM-based; missing Content-Security-Policy headers; rendering user content without sanitization; loading untrusted scripts.
- **CWE mapping**: CWE-79 Cross-site Scripting.

**T1059.007 - JavaScript**
Attackers inject and execute JavaScript in the application context, often through XSS.
- **Code patterns that enable this**: `innerHTML` assignments with user data, `document.write()` with unsanitized input, `eval()` on client side, jQuery `.html()` with user content, missing output encoding.

**T1204 - User Execution**
Attackers rely on users to execute malicious actions (clicking links, uploading files, submitting forms).
- **Code patterns that enable this**: Missing CSRF protection, file upload without type validation, clickjacking-vulnerable pages (missing `X-Frame-Options`), auto-download functionality triggered by URL parameters.

---

### TA0003 - Persistence

**Goal**: The adversary is trying to maintain their foothold in the application.

**Key Techniques**:

**T1098 - Account Manipulation**
Attackers modify existing accounts to maintain access (changing passwords, adding MFA devices, elevating roles).
- **Code patterns that enable this**: Account update endpoints without re-authentication, missing verification for email/password changes, role modification APIs without proper authorization, no alerts on privilege changes.

**T1136 - Create Account**
Attackers create new accounts for persistent access, especially admin or service accounts.
- **Code patterns that enable this**: Self-registration without approval workflows, admin account creation without audit logging, API endpoints that allow role assignment during registration, service account creation without credential rotation policies.

**T1505.003 - Web Shell**
Attackers upload or inject server-side scripts that provide remote command execution.
- **Code patterns that enable this**: Unrestricted file upload (CWE-434), uploaded files stored in web-accessible directories, file extension validation on client side only, application executes uploaded files.

**T1556 - Modify Authentication Process**
Attackers alter authentication mechanisms to accept attacker-controlled credentials.
- **Code patterns that enable this**: Authentication logic in client-side code, pluggable authentication modules without integrity checks, custom auth implementations with bypass conditions, magic backdoor passwords in code.

---

### TA0004 - Privilege Escalation

**Goal**: The adversary is trying to gain higher-level permissions within the application.

**Key Techniques**:

**T1548 - Abuse Elevation Control Mechanism**
Attackers bypass access controls to gain higher privileges.
- **Code patterns that enable this**: Client-side role checks without server enforcement, JWT with `alg: none` accepted, role stored in cookies or local storage without server validation, IDOR on admin endpoints.
- **OWASP mapping**: A01 Broken Access Control.

**T1078.004 - Valid Accounts: Cloud Accounts**
Attackers use compromised cloud service accounts with elevated permissions.
- **Code patterns that enable this**: Over-privileged service accounts, cloud IAM roles with wildcard permissions, shared cloud credentials, API keys with unnecessary admin scope.

**T1068 - Exploitation for Privilege Escalation**
Attackers exploit application vulnerabilities to escalate from user to admin.
- **Code patterns that enable this**: Mass assignment vulnerabilities (setting `role=admin` in request body), parameter tampering on authorization attributes, SQL injection to modify user roles, GraphQL introspection revealing admin mutations.
- **CWE mapping**: CWE-269 Improper Privilege Management, CWE-862 Missing Authorization.

---

### TA0005 - Defense Evasion

**Goal**: The adversary is trying to avoid detection by the application's security controls.

**Key Techniques**:

**T1070 - Indicator Removal**
Attackers clear or modify logs to hide their activity.
- **Code patterns that enable this**: Log files writable by the application user, no centralized logging, logs stored without integrity protection, log injection vulnerabilities (user input written directly to logs).

**T1027 - Obfuscated Files or Information**
Attackers encode or encrypt payloads to bypass input validation and WAFs.
- **Code patterns that enable this**: Validation only checks one encoding (e.g., URL encoding but not double encoding), filters that can be bypassed with case variations, blocklist-based input validation instead of allowlist, incomplete HTML entity decoding.

**T1036 - Masquerading**
Attackers disguise malicious files or requests as legitimate ones.
- **Code patterns that enable this**: File type determined by extension only (not magic bytes), MIME type trust without validation, content-type headers not verified against actual content, SVG files accepted without sanitization (can contain JavaScript).

---

### TA0006 - Credential Access

**Goal**: The adversary is trying to steal credentials such as account names and passwords.

**Key Techniques**:

**T1110 - Brute Force**
Attackers systematically try credentials to gain access.
- **Code patterns that enable this**: No account lockout or rate limiting on login, no CAPTCHA after failed attempts, timing differences between valid/invalid usernames, missing monitoring for brute-force patterns.
- **CWE mapping**: CWE-307 Improper Restriction of Excessive Authentication Attempts.

**T1552 - Unsecured Credentials**
Attackers find credentials stored insecurely within the application.
- **Code patterns that enable this**: Passwords in configuration files, API keys in source code or client bundles, credentials in environment variables logged to stdout, database connection strings in version control, secrets in Docker images.
- **CWE mapping**: CWE-798 Hard-coded Credentials, CWE-312 Cleartext Storage of Sensitive Information.

**T1539 - Steal Web Session Cookie**
Attackers steal session tokens to hijack authenticated sessions.
- **Code patterns that enable this**: Missing `HttpOnly` flag on session cookies, missing `Secure` flag, XSS vulnerabilities enabling `document.cookie` access, session tokens in URLs, missing `SameSite` attribute.

**T1111 - Multi-Factor Authentication Interception**
Attackers intercept or bypass MFA mechanisms.
- **Code patterns that enable this**: MFA codes with long validity windows, no rate limiting on MFA verification, MFA bypass through alternative authentication paths, recovery codes stored insecurely.

---

### TA0009 - Collection

**Goal**: The adversary is trying to gather data of interest from within the application.

**Key Techniques**:

**T1005 - Data from Local System**
Attackers access data stored on the application server, including databases, files, and configuration.
- **Code patterns that enable this**: Path traversal vulnerabilities, SQL injection enabling full database access, local file inclusion, directory listing enabled, backup files accessible via web.

**T1530 - Data from Cloud Storage**
Attackers access improperly secured cloud storage (S3 buckets, Azure blobs, GCS).
- **Code patterns that enable this**: Public cloud storage buckets, pre-signed URLs with long expiration, cloud storage credentials in application code, missing bucket policies.

**T1185 - Browser Session Hijacking**
Attackers exploit browser-based vulnerabilities to access data within the user's session.
- **Code patterns that enable this**: XSS enabling DOM access, missing CSP headers, exposed sensitive data in the DOM, client-side storage of sensitive data (localStorage/sessionStorage).

---

### TA0010 - Exfiltration

**Goal**: The adversary is trying to steal data from the application.

**Key Techniques**:

**T1041 - Exfiltration Over C2 Channel**
Attackers extract data through the same channel used for command and control.
- **Code patterns that enable this**: SSRF vulnerabilities allowing outbound data transfer, DNS rebinding, unrestricted outbound network access from the application server.

**T1567 - Exfiltration Over Web Service**
Attackers use legitimate web services to exfiltrate data (cloud storage, paste sites, messaging APIs).
- **Code patterns that enable this**: Application server with unrestricted internet access, SSRF to external services, blind injection with out-of-band data extraction.

**T1048 - Exfiltration Over Alternative Protocol**
Attackers use non-standard protocols or channels to extract data.
- **Code patterns that enable this**: DNS exfiltration via crafted queries (enabled by SSRF or command injection), data embedded in HTTP headers or timing channels.

---

### TA0040 - Impact

**Goal**: The adversary is trying to manipulate, interrupt, or destroy the application and its data.

**Key Techniques**:

**T1485 - Data Destruction**
Attackers delete data to cause damage or cover their tracks.
- **Code patterns that enable this**: SQL injection enabling `DROP TABLE` or `DELETE`, missing database backups, application-level delete operations without soft-delete or audit trail, API endpoints for bulk deletion without confirmation.

**T1486 - Data Encrypted for Impact (Ransomware)**
Attackers encrypt application data and demand ransom.
- **Code patterns that enable this**: Application with write access to critical data stores, missing data backups, over-privileged database accounts, weak access controls on backup storage.

**T1498 - Network Denial of Service**
Attackers overwhelm the application with traffic.
- **Code patterns that enable this**: Missing rate limiting, no CDN or DDoS protection, resource-intensive endpoints without throttling, ReDoS-vulnerable regular expressions, algorithmic complexity vulnerabilities (e.g., hash collision attacks).

**T1565 - Data Manipulation**
Attackers modify business data to cause damage (e.g., changing prices, altering records).
- **Code patterns that enable this**: Mass assignment vulnerabilities, SQL injection enabling `UPDATE` statements, missing integrity checks on critical data, no audit trail for data modifications, TOCTOU race conditions.

---

## Cross-Framework Mappings

### ATT&CK Techniques to OWASP Top 10

| ATT&CK Technique | OWASP Top 10 Category |
|---|---|
| T1190 Exploit Public-Facing App | A03 Injection, A10 SSRF, A08 Integrity Failures |
| T1078 Valid Accounts | A07 Auth Failures, A01 Broken Access Control |
| T1195 Supply Chain Compromise | A06 Vulnerable Components, A08 Integrity Failures |
| T1059 Command/Scripting | A03 Injection |
| T1203 Client Execution | A03 Injection (XSS) |
| T1548 Abuse Elevation Control | A01 Broken Access Control |
| T1068 Exploitation for Priv Esc | A01 Broken Access Control, A04 Insecure Design |
| T1110 Brute Force | A07 Auth Failures |
| T1552 Unsecured Credentials | A02 Cryptographic Failures, A05 Misconfiguration |
| T1005 Data from Local System | A01 Broken Access Control, A03 Injection |
| T1070 Indicator Removal | A09 Logging Failures |
| T1485 Data Destruction | A03 Injection, A01 Broken Access Control |
| T1498 Network DoS | A04 Insecure Design |

### ATT&CK Techniques to STRIDE

| ATT&CK Technique | STRIDE Category |
|---|---|
| T1078 Valid Accounts | Spoofing |
| T1539 Steal Web Session Cookie | Spoofing |
| T1190 Exploit Public-Facing App | Tampering, Elevation of Privilege |
| T1059 Command/Scripting | Tampering, Elevation of Privilege |
| T1565 Data Manipulation | Tampering |
| T1070 Indicator Removal | Repudiation |
| T1005 Data from Local System | Information Disclosure |
| T1530 Data from Cloud Storage | Information Disclosure |
| T1552 Unsecured Credentials | Information Disclosure |
| T1498 Network DoS | Denial of Service |
| T1485 Data Destruction | Denial of Service |
| T1548 Abuse Elevation Control | Elevation of Privilege |
| T1068 Exploitation for Priv Esc | Elevation of Privilege |

### ATT&CK Techniques to CWE

| ATT&CK Technique | Related CWEs |
|---|---|
| T1190 Exploit Public-Facing App | CWE-89, CWE-78, CWE-22, CWE-918, CWE-502 |
| T1059 Command/Scripting | CWE-78, CWE-94, CWE-77 |
| T1203 Client Execution | CWE-79 |
| T1110 Brute Force | CWE-307, CWE-287 |
| T1552 Unsecured Credentials | CWE-798, CWE-312, CWE-256 |
| T1505.003 Web Shell | CWE-434 |
| T1068 Exploitation for Priv Esc | CWE-269, CWE-862, CWE-863 |
| T1565 Data Manipulation | CWE-20, CWE-352 |

---

## Using ATT&CK for Application Security

### Mapping Findings to Techniques

When a vulnerability is identified during code review, map it to ATT&CK techniques to understand:

1. **How the vulnerability will be discovered** (Reconnaissance tactics)
2. **How it will be exploited** (Initial Access or Execution)
3. **What the attacker does next** (post-exploitation tactics)
4. **What the ultimate impact is** (Collection, Exfiltration, Impact)

This mapping transforms a single finding into a full attack narrative, making it easier for stakeholders to understand the risk.

### Building Kill Chains

Chain techniques across tactics to model realistic attack scenarios:

```
Reconnaissance → Initial Access → Execution → Collection → Exfiltration
```

Each step uses a specific technique. The kill chain shows how a vulnerability leads to business impact.

### Prioritizing Findings

Use ATT&CK mapping to prioritize:
- **Critical**: Finding enables Initial Access (T1190) or Credential Access (T1552) — attacker gets in
- **High**: Finding enables Execution (T1059) or Privilege Escalation (T1068) — attacker gains control
- **Medium**: Finding enables Collection (T1005) or Defense Evasion (T1070) — attacker operates undetected
- **Low**: Finding enables Reconnaissance (T1592) — attacker gathers information

---

## Example: SQL Injection Kill Chain

A SQL injection vulnerability maps to a multi-tactic attack chain:

```
Step 1: Reconnaissance (TA0043)
  T1595 Active Scanning — Attacker discovers injectable parameter
  via automated scanning tools (sqlmap, Burp Suite).

Step 2: Initial Access (TA0001)
  T1190 Exploit Public-Facing Application — Attacker exploits
  SQL injection to bypass authentication or access the database.

Step 3: Execution (TA0002)
  T1059 Command and Scripting Interpreter — If database supports
  it (e.g., xp_cmdshell in MSSQL), attacker executes OS commands.

Step 4: Collection (TA0009)
  T1005 Data from Local System — Attacker dumps database tables
  containing user credentials, PII, and business data.

Step 5: Credential Access (TA0006)
  T1552 Unsecured Credentials — Attacker extracts password hashes
  or plaintext credentials stored in the database.

Step 6: Exfiltration (TA0010)
  T1041 Exfiltration Over C2 Channel — Attacker extracts stolen
  data through the same SQL injection channel or out-of-band (DNS).
```

**Vulnerable code**:
```python
# BAD: String concatenation in SQL query
query = f"SELECT * FROM users WHERE id = {request.args['id']}"
cursor.execute(query)
```

**Mitigated code**:
```python
# GOOD: Parameterized query
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (request.args['id'],))
```

**Mappings for this finding**:
- **OWASP**: A03:2021 Injection
- **CWE**: CWE-89 SQL Injection
- **STRIDE**: Tampering, Information Disclosure, Elevation of Privilege
- **ATT&CK**: T1190 → T1059 → T1005 → T1041

---

## Compliance Mapping Template

```json
{
  "framework": "MITRE ATT&CK",
  "tactic_id": "TA0001",
  "tactic_name": "Initial Access",
  "technique_id": "T1190",
  "technique_name": "Exploit Public-Facing Application",
  "finding": "SQL injection in /api/users endpoint",
  "kill_chain": ["T1595", "T1190", "T1059", "T1005", "T1041"],
  "owasp_mapping": "A03:2021",
  "cwe_mapping": "CWE-89",
  "stride_mapping": ["Tampering", "Information Disclosure"],
  "severity": "critical",
  "mitigations": ["Parameterized queries", "Input validation", "WAF rules"]
}
```
