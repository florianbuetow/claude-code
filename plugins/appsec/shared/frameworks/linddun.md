# LINDDUN Privacy Threat Framework

## Overview

LINDDUN is a privacy-focused threat modeling framework developed at KU Leuven (Belgium). It systematically identifies privacy threats in software systems by analyzing data flows, stores, and processes, similar to how STRIDE identifies security threats.

**The privacy gap**: Traditional security frameworks like STRIDE and OWASP focus on confidentiality, integrity, and availability. They do not address privacy-specific concerns such as linkability, identifiability, data minimization, purpose limitation, or user consent. A system can be fully secure (encrypted, authenticated, authorized) and still violate user privacy. LINDDUN fills this gap.

**When to use LINDDUN**: Use LINDDUN when analyzing applications that collect, process, or store personal data. It is especially relevant for applications subject to GDPR, CCPA, HIPAA, or similar privacy regulations. LINDDUN is applied per-element, like STRIDE: for each component in the data flow diagram, assess which LINDDUN categories apply.

---

## Categories

### L - Linkability

**Privacy Property Violated**: Unlinkability

**Description**: Linkability occurs when an adversary can determine that two or more items of interest (data records, messages, actions, users) are related, even without knowing the identity of the data subject. If separate interactions, transactions, or data points can be correlated to the same person, the system has a linkability threat.

**Questions to Ask**:
- Can an observer link multiple actions or records to the same user?
- Do different services share user identifiers that enable cross-service correlation?
- Can pseudonymous records be linked through common attributes (timestamps, IP addresses, device fingerprints)?
- Are there unique identifiers (user IDs, session tokens, tracking cookies) that persist across contexts?
- Can data from different databases be joined to build a more complete profile?

**Common Threats**:
- Cross-service user tracking via shared identifiers
- Session correlation across multiple interactions
- Database join attacks linking pseudonymous records
- Browser fingerprinting enabling cross-site tracking
- Metadata correlation (timing, frequency, size of requests)
- Behavioral pattern linking across anonymized datasets

**Code-Level Indicators**:
- Global user IDs shared across microservices without pseudonymization
- Cookies or tokens that persist across different application contexts
- Logging that includes user identifiers alongside action details
- Analytics events that include both user ID and detailed behavior
- Database schemas with foreign keys linking user activity across tables

**Typical Mitigations**:
- Use context-specific pseudonyms (different IDs per service or context)
- Implement mix networks or anonymizing proxies
- Strip or generalize metadata before cross-system sharing
- Use k-anonymity or differential privacy for analytics
- Rotate session identifiers regularly
- Separate storage of identity data from behavioral data

**Regulatory Mapping**:
- GDPR Article 5(1)(c): Data minimization
- GDPR Article 25: Data protection by design (pseudonymization)
- CCPA Section 1798.140(o): Definition of personal information includes linkable data

---

### I - Identifiability

**Privacy Property Violated**: Anonymity / Pseudonymity

**Description**: Identifiability occurs when a person can be identified from data that is supposed to be anonymous or pseudonymous. Even without direct identifiers (name, email), a combination of quasi-identifiers (zip code, birth date, gender) can uniquely identify individuals. Re-identification attacks on "anonymized" data are a primary concern.

**Questions to Ask**:
- Can a user be identified from supposedly anonymous data?
- Are there quasi-identifiers (zip code, age, gender) that in combination become unique?
- Could external datasets be used to re-identify users in this system's data?
- Does the system collect more attributes than needed, increasing re-identification risk?
- Are anonymization techniques actually applied, or just assumed?

**Common Threats**:
- Re-identification through quasi-identifier combinations
- Inference attacks on aggregated or statistical data
- Insufficient anonymization (e.g., removing name but keeping detailed location history)
- Linkage attacks combining this dataset with external public data
- Unique behavior patterns that act as fingerprints
- Small population sizes making outliers identifiable

**Code-Level Indicators**:
- User data exports or reports that include quasi-identifiers
- Analytics pipelines that retain granular individual-level data
- API responses that return more user attributes than the consumer needs
- Logs containing IP addresses, user agents, or device identifiers
- Database queries that can return single-user results from "anonymous" tables

**Typical Mitigations**:
- Apply k-anonymity: ensure each combination of quasi-identifiers matches at least k individuals
- Use l-diversity: ensure sensitive attributes have at least l distinct values per equivalence class
- Implement differential privacy for statistical queries
- Generalize quasi-identifiers (age ranges instead of exact ages, region instead of zip code)
- Suppress records with unique attribute combinations
- Limit API response fields to what the consumer actually needs
- Conduct re-identification risk assessments before data release

**Regulatory Mapping**:
- GDPR Recital 26: Definition of anonymous data and identifiability test
- GDPR Article 4(5): Definition of pseudonymization
- HIPAA Safe Harbor: 18 identifier categories that must be removed
- CCPA Section 1798.140(h): Definition of deidentified information

---

### N - Non-repudiation (Privacy Context)

**Privacy Property Violated**: Plausible Deniability

**Description**: In a security context, non-repudiation is desirable (users cannot deny their actions). In a privacy context, non-repudiation becomes a threat when it forces accountability in situations where users should have plausible deniability. This applies to sensitive transactions where being provably associated with an action may cause harm (medical queries, political speech, whistleblowing).

**Questions to Ask**:
- Does the system create irrefutable proof that a specific user performed a sensitive action?
- Are there contexts where users should be able to deny involvement?
- Do digital signatures or audit trails create privacy risks for sensitive activities?
- Can the system's logging be subpoenaed to prove user behavior?
- Are there whistleblowing or reporting features that require sender anonymity?

**Common Threats**:
- Audit logs proving user participation in sensitive activities
- Digital signatures on sensitive transactions that cannot be repudiated
- Transaction receipts or confirmations sent to shared email accounts
- Blockchain or immutable ledger entries linking users to sensitive actions
- Court-ordered disclosure of system logs proving user behavior
- Mandatory identity verification for activities that should be anonymous

**Code-Level Indicators**:
- Comprehensive audit logging of sensitive health, legal, or political queries
- Digital signature requirements on all transactions without sensitivity classification
- Non-repudiation mechanisms applied uniformly without privacy impact assessment
- Session recordings or screen capture functionality
- Immutable storage of user action history without retention limits

**Typical Mitigations**:
- Classify actions by sensitivity and apply non-repudiation selectively
- Use deniable encryption or plausible deniability mechanisms where appropriate
- Implement anonymous submission channels for whistleblowing or reporting
- Apply data retention limits to audit logs of sensitive activities
- Allow pseudonymous participation where accountability is not legally required
- Separate authentication from action logging where possible

**Regulatory Mapping**:
- GDPR Article 17: Right to erasure (conflicts with irrefutable audit trails)
- GDPR Article 5(1)(e): Storage limitation
- EU Whistleblower Directive 2019/1937: Protection of reporting persons
- HIPAA Privacy Rule: Minimum necessary standard for access logs

---

### D - Detectability

**Privacy Property Violated**: Undetectability / Unobservability

**Description**: Detectability occurs when an adversary can determine that an item of interest exists, even without accessing its content. If an observer can detect that a user has a record in a sensitive database, that they visited a particular service, or that encrypted communication is occurring, privacy is compromised even though the content remains secret.

**Questions to Ask**:
- Can an observer determine that a user has a record in a sensitive system?
- Does the existence of encrypted data reveal something sensitive (e.g., encrypted medical records implies a medical condition)?
- Can traffic analysis reveal which services a user accesses?
- Do system responses differ in timing or size based on whether a record exists?
- Can an observer detect patterns of usage that reveal sensitive information?

**Common Threats**:
- Existence inference: API returns different error codes for "user not found" vs. "access denied"
- Traffic analysis revealing which services are accessed
- Timing side channels indicating whether a record exists
- Database size or index patterns revealing data existence
- Push notification patterns revealing user activity
- Storage quota changes indicating new data

**Code-Level Indicators**:
- Different HTTP status codes or error messages for existing vs. non-existing resources
- API endpoints that allow enumeration of user accounts or records
- Response time differences based on record existence (cache hit vs. miss patterns)
- Unpadded encrypted messages where size reveals content type
- Activity indicators (online status, typing indicators, read receipts) without opt-out

**Typical Mitigations**:
- Return consistent error responses regardless of record existence
- Implement constant-time lookups to prevent timing side channels
- Use padding to normalize encrypted message sizes
- Provide decoy traffic or dummy records to mask real data patterns
- Allow users to opt out of presence and activity indicators
- Use private information retrieval (PIR) protocols
- Rate-limit enumeration attempts

**Regulatory Mapping**:
- GDPR Article 25: Data protection by design and by default
- GDPR Article 32: Security of processing (includes protection against unauthorized disclosure)
- CCPA Section 1798.150: Private right of action for unauthorized access

---

### D - Disclosure of Information

**Privacy Property Violated**: Confidentiality of Personal Data

**Description**: Disclosure of information in the LINDDUN context refers specifically to unauthorized access to personal data. While similar to STRIDE's "Information Disclosure," the focus here is on personal and sensitive data rather than general system information. This includes both direct disclosure (data breach) and indirect disclosure (inference from aggregated data).

**Questions to Ask**:
- Can unauthorized parties access personal data at rest, in transit, or in use?
- Are there over-permissioned access controls that expose personal data beyond what is necessary?
- Can personal data be inferred from aggregated or anonymized datasets?
- Does the application transmit personal data to third-party services (analytics, advertising, logging)?
- Are there data flows where personal data crosses jurisdictional boundaries?

**Common Threats**:
- Database breaches exposing personal data
- Over-collection of personal data beyond stated purpose
- Third-party SDK or library exfiltrating personal data
- Insufficient access controls on personal data stores
- Logging personal data in application or system logs
- Cross-border data transfers without adequate protection
- Personal data in error messages, debug output, or stack traces

**Code-Level Indicators**:
- PII (names, emails, phone numbers, SSNs) stored in plaintext
- Personal data included in log statements
- Third-party analytics or tracking scripts receiving user data
- API responses exposing more personal fields than the client needs
- Personal data passed through URL query parameters (visible in logs and browser history)
- Lack of field-level encryption for sensitive personal attributes
- Database queries returning SELECT * on tables containing personal data

**Typical Mitigations**:
- Encrypt personal data at rest and in transit
- Implement field-level access controls on personal data
- Apply data minimization: only collect and return what is needed
- Redact personal data from logs
- Audit third-party libraries for data collection behavior
- Implement data loss prevention (DLP) controls
- Use tokenization for sensitive identifiers
- Apply purpose limitation controls on data access

**Regulatory Mapping**:
- GDPR Article 5(1)(f): Integrity and confidentiality
- GDPR Article 32: Security of processing
- GDPR Article 33-34: Breach notification (72-hour requirement)
- CCPA Section 1798.100: Right to know what personal data is collected
- CCPA Section 1798.150: Private right of action for data breaches
- HIPAA Security Rule 164.312: Technical safeguards for PHI

---

### U - Unawareness

**Privacy Property Violated**: Transparency / Informed Consent

**Description**: Unawareness occurs when data subjects do not know or understand how their personal data is collected, processed, stored, or shared. Even if data handling is technically lawful, failing to inform users violates the principle of transparency and may invalidate consent. This category addresses the gap between what the system actually does with data and what users understand it does.

**Questions to Ask**:
- Are users informed about all data collection before it occurs?
- Does the privacy policy accurately reflect actual data processing activities?
- Can users access, correct, and delete their personal data?
- Are users notified when data processing purposes change?
- Do users understand the consequences of consent they provide?
- Are there hidden data flows (analytics, telemetry, error reporting) that users are unaware of?

**Common Threats**:
- Data collection without informed consent
- Privacy policy that does not match actual data practices
- No mechanism for users to access their own data
- No mechanism to withdraw consent or request deletion
- Hidden data sharing with third parties not disclosed to users
- Consent fatigue leading to uninformed acceptance
- Dark patterns that manipulate users into sharing more data

**Code-Level Indicators**:
- Data collection occurring before consent flow completes
- No consent management system or preference storage
- No data export or portability endpoint (GDPR Article 20)
- No data deletion endpoint or soft-delete mechanism (GDPR Article 17)
- Third-party scripts loaded without corresponding privacy policy disclosure
- Analytics or telemetry initialized before user consent check
- No consent version tracking (can't prove what user agreed to)

**Typical Mitigations**:
- Implement consent management with granular opt-in/opt-out controls
- Ensure consent is collected before data processing begins
- Provide clear, accessible privacy notices at point of collection
- Build data subject access request (DSAR) endpoints
- Implement right to deletion (data erasure) functionality
- Track consent versions and timestamps
- Audit third-party integrations against privacy policy claims
- Implement privacy dashboards for user self-service

**Regulatory Mapping**:
- GDPR Article 7: Conditions for consent
- GDPR Article 12-14: Transparent information and communication
- GDPR Article 15: Right of access by the data subject
- GDPR Article 17: Right to erasure
- GDPR Article 20: Right to data portability
- CCPA Section 1798.100: Right to know
- CCPA Section 1798.105: Right to delete
- CCPA Section 1798.120: Right to opt-out of sale

---

### N - Non-compliance

**Privacy Property Violated**: Regulatory Compliance

**Description**: Non-compliance occurs when the application's data processing activities violate applicable privacy regulations. This is both a legal risk and a privacy threat. Non-compliance can result from missing technical controls, incorrect legal bases for processing, or failure to implement required data subject rights.

**Questions to Ask**:
- What privacy regulations apply to this application (GDPR, CCPA, HIPAA, LGPD, PIPA)?
- Is there a lawful basis for each category of data processing?
- Are all required data subject rights implemented (access, correction, deletion, portability)?
- Is a Data Protection Impact Assessment (DPIA) required?
- Are cross-border data transfers handled in compliance with applicable law?
- Are data processing agreements in place with all processors and sub-processors?
- Are data retention periods defined and enforced?

**Common Threats**:
- Processing personal data without valid legal basis
- Missing or non-functional data subject rights endpoints
- Cross-border data transfer without adequacy decision or safeguards
- Exceeding stated data retention periods
- Missing Data Protection Impact Assessment for high-risk processing
- Lack of records of processing activities (GDPR Article 30)
- Using personal data beyond the originally stated purpose
- Missing breach notification capability within regulatory timeframes

**Code-Level Indicators**:
- No data retention enforcement (no TTL on records, no cleanup jobs)
- No implementation of data deletion across all storage systems (database, backups, caches, logs)
- Personal data flowing to servers in non-adequate jurisdictions without transfer safeguards
- No age verification for services with age restrictions (COPPA, GDPR Article 8)
- No mechanism to restrict processing (GDPR Article 18)
- Missing data processing audit trail
- No consent withdrawal mechanism that stops ongoing processing
- Hardcoded data retention periods that do not match privacy policy

**Typical Mitigations**:
- Implement automated data retention enforcement with configurable TTLs
- Build comprehensive data deletion across all storage layers
- Implement data residency controls for cross-border compliance
- Create records of processing activities (ROPA) as system documentation
- Implement age gating and parental consent where required
- Build breach detection and notification workflows within regulatory timeframes
- Implement purpose limitation controls (data tagging by processing purpose)
- Create Data Protection Impact Assessment documentation for high-risk features

**Regulatory Mapping**:
- GDPR Article 5: Principles of processing (lawfulness, purpose limitation, minimization)
- GDPR Article 6: Lawful bases for processing
- GDPR Article 8: Child's consent
- GDPR Article 13-14: Information to data subjects
- GDPR Article 18: Right to restriction of processing
- GDPR Article 28: Data processor requirements
- GDPR Article 30: Records of processing activities
- GDPR Article 35-36: Data Protection Impact Assessment
- GDPR Article 44-49: Cross-border data transfers
- CCPA Section 1798.120: Right to opt-out of sale
- CCPA Section 1798.135: Notice of right to opt-out
- HIPAA Privacy Rule 45 CFR 164.530: Administrative requirements
- HIPAA Breach Notification Rule 45 CFR 164.404: Notification to individuals

---

## Cross-Framework Mappings

### LINDDUN to STRIDE

| LINDDUN Category | Closest STRIDE Category | Relationship |
|---|---|---|
| L: Linkability | Information Disclosure | Linkability extends beyond data access to correlation analysis |
| I: Identifiability | Information Disclosure | Identifiability focuses on re-identification of anonymized data |
| N: Non-repudiation | Repudiation (inverse) | LINDDUN treats forced accountability as a privacy threat; STRIDE treats deniability as a security threat |
| D: Detectability | Information Disclosure | Detectability focuses on existence proofs, not content access |
| D: Disclosure | Information Disclosure | Most direct overlap; LINDDUN narrows focus to personal data |
| U: Unawareness | (no equivalent) | Unique to LINDDUN; no STRIDE counterpart |
| N: Non-compliance | (no equivalent) | Unique to LINDDUN; no STRIDE counterpart |

### LINDDUN to OWASP Top 10

| LINDDUN Category | OWASP Top 10 Categories |
|---|---|
| L: Linkability | A01 Broken Access Control (cross-context data leakage) |
| I: Identifiability | A02 Cryptographic Failures (weak anonymization) |
| N: Non-repudiation | A09 Logging & Monitoring (excessive audit trail) |
| D: Detectability | A05 Security Misconfiguration (information leakage in responses) |
| D: Disclosure | A01 Broken Access Control, A02 Cryptographic Failures |
| U: Unawareness | A04 Insecure Design (missing privacy by design) |
| N: Non-compliance | A04 Insecure Design (missing regulatory controls) |

### LINDDUN to CWE

| LINDDUN Category | Relevant CWE Entries |
|---|---|
| L: Linkability | CWE-359 (Exposure of Private Information), CWE-212 (Improper Removal of Sensitive Data Before Storage or Transfer) |
| I: Identifiability | CWE-359 (Exposure of Private Information), CWE-200 (Exposure of Sensitive Information) |
| N: Non-repudiation | CWE-779 (Logging of Excessive Data) |
| D: Detectability | CWE-203 (Observable Discrepancy), CWE-208 (Observable Timing Discrepancy) |
| D: Disclosure | CWE-200 (Exposure of Sensitive Information), CWE-311 (Missing Encryption), CWE-532 (Information Exposure Through Log Files) |
| U: Unawareness | CWE-1021 (Improper Restriction of Rendered UI Layers) |
| N: Non-compliance | CWE-359 (Exposure of Private Information) |

---

## Applying LINDDUN

### Per-Element Analysis

Apply LINDDUN to each element in the data flow diagram, similar to STRIDE:

| Element Type | Applicable LINDDUN Categories |
|---|---|
| External Entity (Data Subject) | L, I, U, N(compliance) |
| External Entity (Third Party) | D(disclosure), N(compliance) |
| Process | L, I, N(non-repudiation), D(detectability), D(disclosure) |
| Data Store | L, I, D(detectability), D(disclosure), N(compliance) |
| Data Flow | L, I, D(detectability), D(disclosure) |
| Trust Boundary | (analyze elements crossing it for all categories) |

### Per-Interaction Analysis

For each data flow involving personal data:
1. Identify what personal data is transmitted
2. Assess each LINDDUN category
3. Document the privacy threat and the data subjects affected
4. Map to applicable regulatory requirements
5. Identify Privacy Enhancing Technologies (PETs) as mitigations

### Privacy Impact Scoring

| Likelihood / Impact | Low | Medium | High | Critical |
|---|---|---|---|---|
| Almost Certain (5) | Medium | High | Critical | Critical |
| Likely (4) | Low | Medium | High | Critical |
| Possible (3) | Low | Medium | Medium | High |
| Unlikely (2) | Low | Low | Medium | Medium |
| Rare (1) | Low | Low | Low | Medium |

Impact should consider: number of data subjects affected, sensitivity of data, reversibility of harm, and regulatory penalties.

---

## GDPR Article Mapping Table

| GDPR Article | LINDDUN Category | Requirement Summary |
|---|---|---|
| Art. 4(5) | I: Identifiability | Pseudonymization definition |
| Art. 5(1)(a) | U: Unawareness | Lawfulness, fairness, transparency |
| Art. 5(1)(b) | N: Non-compliance | Purpose limitation |
| Art. 5(1)(c) | L: Linkability | Data minimization |
| Art. 5(1)(e) | N: Non-compliance | Storage limitation |
| Art. 5(1)(f) | D: Disclosure | Integrity and confidentiality |
| Art. 6 | N: Non-compliance | Lawful bases for processing |
| Art. 7 | U: Unawareness | Conditions for valid consent |
| Art. 12-14 | U: Unawareness | Transparency obligations |
| Art. 15 | U: Unawareness | Right of access |
| Art. 17 | N: Non-repudiation, N: Non-compliance | Right to erasure |
| Art. 20 | U: Unawareness | Right to data portability |
| Art. 25 | D: Detectability, L: Linkability | Data protection by design and default |
| Art. 30 | N: Non-compliance | Records of processing activities |
| Art. 32 | D: Disclosure | Security of processing |
| Art. 33-34 | N: Non-compliance | Breach notification |
| Art. 35 | N: Non-compliance | Data Protection Impact Assessment |
| Art. 44-49 | N: Non-compliance | Cross-border data transfers |

---

## Documentation Template

For each privacy threat identified:

```markdown
### [PRIVACY-ID]: Threat Title

**Category**: [LINDDUN letter and name]
**Target**: [Component/Flow/Store affected]
**Data Subjects Affected**: [Users, employees, customers, minors, etc.]
**Personal Data Involved**: [Categories of personal data]
**Risk Score**: [1-25]

**Description**:
[What the privacy threat is and how it manifests]

**Regulatory Impact**:
- GDPR: [Applicable articles]
- CCPA: [Applicable sections]
- HIPAA: [Applicable rules, if health data]

**Existing Controls**:
- [Current privacy measures]

**Gaps**:
- [Missing privacy controls]

**Recommended Mitigations**:
1. [Mitigation 1 with Privacy Enhancing Technology reference]
2. [Mitigation 2]

**Residual Risk**:
[Risk remaining after mitigations]
```

---

## Compliance Mapping Template

```json
{
  "framework": "LINDDUN",
  "category": "L",
  "category_name": "Linkability",
  "finding_id": "LINDDUN-001",
  "data_subjects": ["end_users"],
  "personal_data_categories": ["behavioral_data", "device_identifiers"],
  "threat": "Cross-service user tracking via shared global user ID",
  "component": "UserService, AnalyticsService, RecommendationService",
  "risk_score": 18,
  "regulatory_mapping": {
    "gdpr": ["Art. 5(1)(c)", "Art. 25"],
    "ccpa": ["1798.140(o)"]
  },
  "mitigations": [
    {"action": "Implement context-specific pseudonyms per service", "effort": "medium", "risk_reduction": "high"},
    {"action": "Remove user ID from analytics events, use anonymous session tokens", "effort": "low", "risk_reduction": "medium"}
  ],
  "residual_risk": "low"
}
```
