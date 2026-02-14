# OWASP Top 10 2021 Reference

## Overview

The OWASP Top 10 is a standard awareness document for developers and web application security. It represents a broad consensus about the most critical security risks to web applications.

---

## A01:2021 - Broken Access Control

**Description**: Restrictions on what authenticated users are allowed to do are not properly enforced.

**Common Vulnerabilities**:
- Bypassing access control checks by modifying URL, internal state, or HTML page
- Viewing or editing someone else's account by providing its unique identifier (IDOR)
- Accessing APIs without access controls for POST, PUT, DELETE
- Elevation of privilege (acting as user without login, acting as admin when logged in as user)
- Metadata manipulation (replay/tamper with JWT, cookies, hidden fields)
- CORS misconfiguration allowing unauthorized API access

**How to Prevent**:
- Deny by default (except for public resources)
- Implement access control mechanisms once and reuse
- Model access controls should enforce record ownership
- Disable web server directory listing
- Log access control failures, alert admins
- Rate limit API and controller access
- Invalidate JWT tokens on the server after logout

**STRIDE Mapping**: Elevation of Privilege, Information Disclosure

---

## A02:2021 - Cryptographic Failures

**Description**: Failures related to cryptography which often lead to exposure of sensitive data.

**Common Vulnerabilities**:
- Data transmitted in cleartext (HTTP, SMTP, FTP)
- Old or weak cryptographic algorithms
- Default or weak crypto keys
- Improper certificate validation
- Passwords stored without hashing or with weak hashes
- Cryptographic randomness not used properly

**How to Prevent**:
- Classify data and apply controls per classification
- Don't store sensitive data unnecessarily
- Encrypt all sensitive data at rest
- Use strong standard algorithms and protocols
- Encrypt all data in transit with TLS
- Disable caching for responses with sensitive data
- Store passwords using strong salted hashing (Argon2, bcrypt, scrypt)

**STRIDE Mapping**: Information Disclosure, Tampering

---

## A03:2021 - Injection

**Description**: User-supplied data is not validated, filtered, or sanitized by the application.

**Common Vulnerabilities**:
- SQL, NoSQL, OS command injection
- LDAP injection
- Expression Language (EL) injection
- Object Graph Navigation Library (OGNL) injection
- User-supplied data not validated/sanitized
- Dynamic queries without parameterization
- Hostile data in ORM search parameters

**How to Prevent**:
- Use safe APIs that parameterize queries
- Use positive server-side input validation
- Escape special characters for residual dynamic queries
- Use LIMIT and other SQL controls to prevent mass disclosure
- Automated testing of all parameters

**STRIDE Mapping**: Tampering, Information Disclosure, Elevation of Privilege

---

## A04:2021 - Insecure Design

**Description**: Missing or ineffective security controls as a result of missing threat modeling.

**Common Vulnerabilities**:
- Missing security requirements
- No threat modeling during design
- Failing to determine required security controls
- Not using secure design patterns
- Insufficient business logic security

**How to Prevent**:
- Establish secure development lifecycle with security specialists
- Use threat modeling for critical authentication, access control, business logic
- Integrate security language in user stories
- Implement plausibility checks at each tier
- Write unit and integration tests for security flows
- Segregate tenants by design
- Limit resource consumption by user/service

**STRIDE Mapping**: All categories

---

## A05:2021 - Security Misconfiguration

**Description**: Missing appropriate security hardening or improperly configured permissions.

**Common Vulnerabilities**:
- Missing security hardening
- Improperly configured cloud service permissions
- Unnecessary features enabled or installed
- Default accounts with unchanged passwords
- Overly informative error messages
- Disabled or misconfigured security features
- Out of date software

**How to Prevent**:
- Repeatable hardening process, automated
- Minimal platform without unnecessary features
- Review and update configurations
- Segmented application architecture
- Automated verification of configurations
- Send security directives to clients (e.g., security headers)

**STRIDE Mapping**: All categories

---

## A06:2021 - Vulnerable and Outdated Components

**Description**: Using components with known vulnerabilities.

**Common Vulnerabilities**:
- Not knowing versions of all components
- Using vulnerable, unsupported, or out of date software
- Not scanning for vulnerabilities regularly
- Not fixing or upgrading platforms timely
- Not testing compatibility of updated libraries
- Not securing component configurations

**How to Prevent**:
- Remove unused dependencies, features, components
- Continuously inventory component versions
- Monitor CVE and NVD for vulnerabilities
- Use software composition analysis tools
- Only obtain components from official sources
- Monitor for unmaintained libraries

**STRIDE Mapping**: All categories (depends on vulnerable component)

---

## A07:2021 - Identification and Authentication Failures

**Description**: Confirmation of the user's identity, authentication, and session management is weak.

**Common Vulnerabilities**:
- Permits automated attacks (credential stuffing, brute force)
- Permits default, weak, or well-known passwords
- Uses weak credential recovery
- Uses plain text, encrypted, or weakly hashed passwords
- Missing or ineffective MFA
- Exposes session identifier in URL
- Reuses session identifier after login
- Doesn't invalidate sessions properly

**How to Prevent**:
- Implement MFA
- Don't deploy with default credentials
- Implement weak password checks
- Align password policies with NIST guidelines
- Harden registration, credential recovery, API pathways
- Limit or delay failed login attempts
- Use server-side, secure session manager

**STRIDE Mapping**: Spoofing, Repudiation

---

## A08:2021 - Software and Data Integrity Failures

**Description**: Code and infrastructure that doesn't protect against integrity violations.

**Common Vulnerabilities**:
- Relying on plugins, libraries, or modules from untrusted sources
- Insecure CI/CD pipeline
- Auto-update without integrity verification
- Insecure deserialization

**How to Prevent**:
- Use digital signatures to verify software/data
- Ensure libraries are from trusted repositories
- Use software composition analysis tools
- Ensure there's review for code and config changes
- Ensure CI/CD pipeline has proper segregation and access control
- Don't send unsigned or unencrypted serialized data

**STRIDE Mapping**: Tampering, Elevation of Privilege

---

## A09:2021 - Security Logging and Monitoring Failures

**Description**: Not detecting, escalating, or responding to active breaches in a timely manner.

**Common Vulnerabilities**:
- Auditable events not logged
- Warnings and errors generate unclear log messages
- Logs not monitored for suspicious activity
- Logs only stored locally
- Appropriate alerting thresholds not in place
- Penetration testing doesn't trigger alerts
- Application can't detect or alert on active attacks

**How to Prevent**:
- Log all login, access control, and input validation failures
- Ensure logs are in a format consumable by log management solutions
- Ensure high-value transactions have audit trail with integrity controls
- Establish effective monitoring and alerting
- Establish incident response and recovery plan

**STRIDE Mapping**: Repudiation

---

## A10:2021 - Server-Side Request Forgery (SSRF)

**Description**: Application fetches a remote resource without validating the user-supplied URL.

**Common Vulnerabilities**:
- Fetching URLs from user input without validation
- Accepting full URLs or partial URLs from users
- Not enforcing URL schema, port, and destination
- Allowing redirects

**How to Prevent**:
- Segment remote resource access functionality
- Enforce deny by default firewall policies
- Sanitize and validate all client-supplied input
- Don't send raw responses to clients
- Disable HTTP redirections
- Use allowlist for URL schema, ports, destinations

**STRIDE Mapping**: Information Disclosure, Elevation of Privilege

---

## Compliance Mapping Template

```json
{
  "framework": "OWASP Top 10 2021",
  "requirement_id": "A01:2021",
  "requirement_name": "Broken Access Control",
  "threats": ["threat-001", "threat-002"],
  "controls": ["control-001", "control-002"],
  "status": "partial|compliant|non-compliant",
  "gaps": ["gap-001"],
  "evidence": ["RBAC implemented", "Missing object-level checks"]
}
```
