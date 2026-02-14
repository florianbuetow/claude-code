# STRIDE Threat Framework

## Overview

STRIDE is a threat modeling framework developed by Microsoft. Each letter represents a category of security threat that maps to a security property violation.

## Categories

### S - Spoofing Identity

**Security Property Violated**: Authentication

**Description**: Pretending to be something or someone other than yourself.

**Questions to Ask**:
- Can an attacker impersonate a legitimate user?
- Can an attacker impersonate another system component?
- Are credentials properly protected?
- Is session management secure?

**Common Threats**:
- Credential theft/reuse
- Session hijacking
- Token theft
- IP spoofing
- Email spoofing
- Certificate spoofing

**Typical Mitigations**:
- Strong authentication (MFA)
- Secure credential storage
- Session management controls
- Certificate validation
- Input validation on identity claims

---

### T - Tampering with Data

**Security Property Violated**: Integrity

**Description**: Modifying data or code without authorization.

**Questions to Ask**:
- Can an attacker modify data in transit?
- Can an attacker modify data at rest?
- Can an attacker modify configuration?
- Can an attacker modify code or binaries?

**Common Threats**:
- SQL injection
- Parameter tampering
- Man-in-the-middle attacks
- File modification
- Configuration tampering
- Code injection

**Typical Mitigations**:
- Input validation
- Parameterized queries
- Encryption in transit (TLS)
- Integrity checks (HMAC, signatures)
- Access controls on data stores
- Code signing

---

### R - Repudiation

**Security Property Violated**: Non-repudiation

**Description**: Claiming to not have performed an action when you actually did.

**Questions to Ask**:
- Can users deny performing actions?
- Are all security-relevant actions logged?
- Are logs tamper-proof?
- Is there sufficient evidence for forensics?

**Common Threats**:
- Missing audit logs
- Log tampering
- Log injection
- Insufficient logging detail
- Log deletion

**Typical Mitigations**:
- Comprehensive audit logging
- Tamper-evident logs
- Centralized log management
- Digital signatures on transactions
- Timestamps from trusted sources

---

### I - Information Disclosure

**Security Property Violated**: Confidentiality

**Description**: Exposing information to unauthorized parties.

**Questions to Ask**:
- Can an attacker access sensitive data?
- Does the system leak information in errors?
- Is data properly encrypted?
- Are there side-channel leaks?

**Common Threats**:
- Data breaches
- Directory traversal
- Error message information leaks
- Timing attacks
- Memory dumps
- Improper access controls
- Cleartext transmission

**Typical Mitigations**:
- Encryption at rest and in transit
- Access controls
- Data classification
- Secure error handling
- Memory protection
- Data minimization

---

### D - Denial of Service

**Security Property Violated**: Availability

**Description**: Denying or degrading service to legitimate users.

**Questions to Ask**:
- Can an attacker exhaust resources?
- Are there algorithmic complexity issues?
- Can an attacker crash the system?
- Are there single points of failure?

**Common Threats**:
- Resource exhaustion (CPU, memory, disk, network)
- Algorithmic complexity attacks
- Application crashes
- Distributed denial of service (DDoS)
- Zip bombs / decompression bombs

**Typical Mitigations**:
- Rate limiting
- Resource quotas
- Input size limits
- Redundancy and failover
- DDoS protection services
- Circuit breakers

---

### E - Elevation of Privilege

**Security Property Violated**: Authorization

**Description**: Gaining capabilities without proper authorization.

**Questions to Ask**:
- Can an attacker bypass authorization?
- Can an attacker escalate to higher privileges?
- Are permissions properly enforced?
- Can an attacker exploit trust boundaries?

**Common Threats**:
- Privilege escalation
- Broken access control (IDOR)
- Missing function-level access control
- Insecure direct object references
- JWT manipulation
- Role confusion

**Typical Mitigations**:
- Principle of least privilege
- Role-based access control (RBAC)
- Object-level authorization
- Trust boundary enforcement
- Secure defaults (deny by default)

---

## Applying STRIDE

### Per-Element Analysis

Apply STRIDE to each element in your data flow diagram:

| Element Type | Applicable STRIDE Categories |
|--------------|------------------------------|
| External Entity | S, R |
| Process | S, T, R, I, D, E |
| Data Store | T, R, I, D |
| Data Flow | T, I, D |
| Trust Boundary | (analyze elements crossing it) |

### Per-Interaction Analysis

For each data flow crossing a trust boundary:
1. Identify the source and destination
2. Consider each STRIDE category
3. Document applicable threats
4. Assess risk and priority
5. Identify mitigations

### Risk Assessment Matrix

| Likelihood / Impact | Low | Medium | High | Critical |
|---------------------|-----|--------|------|----------|
| Almost Certain (5) | Medium | High | Critical | Critical |
| Likely (4) | Low | Medium | High | Critical |
| Possible (3) | Low | Medium | Medium | High |
| Unlikely (2) | Low | Low | Medium | Medium |
| Rare (1) | Low | Low | Low | Medium |

### Documentation Template

For each threat identified:

```markdown
### [THREAT-ID]: Threat Title

**Category**: [STRIDE letter]
**Target**: [Component/Flow affected]
**Risk Score**: [1-25]

**Description**:
[What the threat is and how it could be exploited]

**Prerequisites**:
- [What attacker needs]

**Impact**:
- Confidentiality: [Low/Medium/High]
- Integrity: [Low/Medium/High]
- Availability: [Low/Medium/High]

**Existing Controls**:
- [Current mitigations]

**Gaps**:
- [Missing controls]

**Recommended Mitigations**:
1. [Mitigation 1]
2. [Mitigation 2]
```
