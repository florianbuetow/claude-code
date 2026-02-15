---
name: glossary
description: >
  This skill should be used when the user asks "what is IDOR",
  "define CSRF", "security glossary", or wants quick security term
  definitions. Quick reference for security terms, acronyms, and categories.
---

# AppSec Glossary -- Security Term Reference

Quick-reference dictionary for security terms, acronyms, vulnerability
classes, and framework categories. Returns concise definitions with
cross-framework mappings and concrete examples.

Unlike `/appsec:explain` which provides deep educational content, `glossary`
is a fast lookup -- a few sentences per term, not a full lesson.

This skill runs entirely in the main agent context. It does NOT dispatch
subagents.

## Supported Modes

Detect the user's intent from their message:

| Intent | Mode |
|--------|------|
| Single term ("what is IDOR", "define XSS") | Single Term Lookup |
| Comparison ("CSRF vs SSRF", "XSS vs injection") | Term Comparison |
| "security glossary", "list all terms" | Full Glossary |

## Single Term Lookup

For a single term, output:

```
<TERM> (<full expansion if acronym>)

Definition: <2-3 sentence plain-language definition>

Framework Mappings:
  OWASP:   <category, e.g., A03:2021 Injection>
  STRIDE:  <letter(s), e.g., T (Tampering)>
  CWE:     <CWE-ID, e.g., CWE-89>
  MITRE:   <technique, e.g., T1190>

Example: <1-2 sentence concrete attack scenario>

Related: <2-3 related terms>
```

### Term Registry

Use these framework reference files to resolve mappings:

| Framework | Reference |
|-----------|-----------|
| OWASP Top 10 | [`../../shared/frameworks/owasp-top10-2021.md`](../../shared/frameworks/owasp-top10-2021.md) |
| OWASP API Top 10 | [`../../shared/frameworks/owasp-api-top10.md`](../../shared/frameworks/owasp-api-top10.md) |
| STRIDE | [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md) |
| PASTA | [`../../shared/frameworks/pasta.md`](../../shared/frameworks/pasta.md) |
| LINDDUN | [`../../shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md) |
| MITRE ATT&CK | [`../../shared/frameworks/mitre-attck.md`](../../shared/frameworks/mitre-attck.md) |
| SANS/CWE Top 25 | [`../../shared/frameworks/sans-cwe-top25.md`](../../shared/frameworks/sans-cwe-top25.md) |
| DREAD | [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md) |

Read the relevant reference file(s) to populate the mappings accurately.
Do NOT guess mappings -- if a term does not appear in a framework, omit
that mapping rather than fabricating one.

### Common Terms

This is not exhaustive. Handle any security term the user asks about using
general security knowledge plus the framework references above.

**Vulnerability classes:**
IDOR, XSS, CSRF, SSRF, SQLi, RCE, LFI, RFI, XXE, SSTI, ReDoS, CRLF,
HPP, clickjacking, open redirect, mass assignment, insecure deserialization,
broken authentication, path traversal, command injection, log injection,
race condition, TOCTOU, privilege escalation, session fixation, session
hijacking, credential stuffing, brute force, directory traversal

**Framework terms:**
OWASP, STRIDE, PASTA, LINDDUN, DREAD, CVSS, CWE, CVE, MITRE ATT&CK,
SANS Top 25, NIST, ISO 27001, SOC 2, PCI DSS, GDPR, CCPA, HIPAA

**Security concepts:**
defense in depth, least privilege, zero trust, separation of concerns,
input validation, output encoding, parameterized queries, prepared
statements, CSP, CORS, SOP, HSTS, certificate pinning, mTLS, JWT, OAuth,
OIDC, SAML, RBAC, ABAC, ACL, MFA, 2FA, TOTP, FIDO2, WebAuthn, salted
hash, key derivation, envelope encryption, secret rotation, audit trail

## Term Comparison

When the user asks to compare two or more terms, output a side-by-side
table:

```
<TERM_A> vs <TERM_B>

| Aspect      | <TERM_A>                | <TERM_B>                |
|-------------|-------------------------|-------------------------|
| Full Name   | ...                     | ...                     |
| What It Is  | ...                     | ...                     |
| Attack Type | ...                     | ...                     |
| Target      | ...                     | ...                     |
| OWASP       | ...                     | ...                     |
| CWE         | ...                     | ...                     |
| Example     | ...                     | ...                     |

Key Difference: <one sentence explaining the core distinction>
```

## Full Glossary

When the user asks for a full glossary, output an alphabetically sorted
table of the most important terms. Limit to 30-40 entries to keep it
scannable. Group by category:

```
APPSEC GLOSSARY

--- Vulnerability Classes ---
| Term   | Definition (brief)              | OWASP  | CWE     |
|--------|---------------------------------|--------|---------|
| CSRF   | Cross-site request forgery ...  | A01    | CWE-352 |
| IDOR   | Insecure direct object ref ...  | A01    | CWE-639 |
| ...    | ...                             | ...    | ...     |

--- Frameworks & Standards ---
| Term       | What It Is                           |
|------------|--------------------------------------|
| OWASP      | Open Worldwide Application Security  |
| STRIDE     | Threat modeling framework (6 cats)   |
| ...        | ...                                  |

--- Security Concepts ---
| Term              | Definition (brief)                     |
|-------------------|----------------------------------------|
| Defense in Depth  | Multiple layers of security controls   |
| Least Privilege   | Minimum necessary access               |
| ...               | ...                                    |
```

## Presentation Rules

- Keep definitions SHORT. This is a glossary, not an encyclopedia. Two to
  three sentences maximum per definition.
- Always include at least one framework mapping when one exists.
- Always include a concrete example -- "An attacker can..." not abstract
  descriptions.
- For acronyms, always expand them on first use.
- If the user asks about a term not in the registry, provide a definition
  from general security knowledge and note which frameworks it relates to.
- After any lookup, offer: "Want to learn more? Try `/appsec:explain <term>`
  for an in-depth walkthrough."
