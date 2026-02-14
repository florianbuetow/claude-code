# DREAD Risk Scoring Model

## Overview

DREAD is a qualitative risk scoring model originally developed at Microsoft for rating security threats during threat modeling. Each letter represents one factor used to evaluate the severity of a vulnerability. The five factor scores are averaged to produce a single risk rating between 0 and 10.

DREAD is useful when you need a quick, intuitive risk score that is easy to explain to non-security stakeholders. It is less formal than CVSS but faster to apply and well-suited for prioritizing findings during code review and threat modeling sessions.

**When to use DREAD**: Rapid triage during security audits, internal threat modeling, prioritizing a backlog of findings. It works well when you need relative ordering of risks rather than industry-standard scores for public advisories.

---

## The 5 Factors

### D - Damage

**What is the worst-case outcome if this vulnerability is exploited?**

| Score | Criteria | Examples |
|-------|----------|----------|
| 0 | No meaningful impact | Cosmetic defect with no security consequence |
| 1-3 | Minor impact to a subset of data or functionality | Leaking non-sensitive metadata, minor information disclosure |
| 4-6 | Significant impact to data or functionality | Unauthorized access to user PII, modification of user-owned data |
| 7-9 | Major impact, large-scale data breach or service disruption | Database dump of credentials, financial data exfiltration |
| 10 | Complete system compromise | Remote code execution, full admin takeover, destruction of all data |

**How to evaluate from code context**: Identify what data or operations the vulnerable code path touches. Trace the data flow downstream. If the code handles authentication tokens, financial records, or PII, damage is high. If it handles only public content, damage is low.

---

### R - Reproducibility

**How reliably can an attacker reproduce the exploit?**

| Score | Criteria | Examples |
|-------|----------|----------|
| 0 | Nearly impossible, requires extreme conditions | Race condition with nanosecond window, specific hardware needed |
| 1-3 | Difficult, requires specific timing or state | Race condition that succeeds ~10% of the time, specific user state required |
| 4-6 | Moderate, requires some setup but works reliably | Needs a valid user account plus specific request sequence |
| 7-9 | Easy, works most of the time with minimal setup | Send a crafted request, works on any account |
| 10 | Trivial, works every time with no special conditions | Unauthenticated endpoint, single request, always succeeds |

**How to evaluate from code context**: Check whether the vulnerability requires specific preconditions (race conditions, particular user roles, specific application state). If the vulnerable code path is deterministic and reachable via a normal request flow, reproducibility is high.

---

### E - Exploitability

**How much skill, tooling, or effort is required to execute the attack?**

| Score | Criteria | Examples |
|-------|----------|----------|
| 0 | Requires advanced custom tooling and deep expertise | Custom zero-day exploit chain, hardware-based attack |
| 1-3 | Requires significant security expertise and custom code | Writing a deserialization gadget chain, bypassing ASLR/DEP |
| 4-6 | Requires moderate skill, existing tools can be adapted | Using Burp Suite or sqlmap with some customization |
| 7-9 | Script-kiddie level, public exploit available | Known CVE with public Metasploit module, well-documented technique |
| 10 | No skill required, copy-paste from browser or exploit-db | Changing a URL parameter, using browser developer tools |

**How to evaluate from code context**: Consider the attack vector. SQL injection in a URL parameter is highly exploitable. A timing side-channel that requires statistical analysis over thousands of requests is less exploitable. Check whether public tools exist for the vulnerability class.

---

### A - Affected Users

**How many users or systems are impacted?**

| Score | Criteria | Examples |
|-------|----------|----------|
| 0 | No real users affected | Vulnerability in dead code or unused endpoint |
| 1-3 | Small subset of users under specific conditions | Affects only users of a rarely-used legacy feature |
| 4-6 | Significant portion of users or specific high-value targets | Affects all users of a particular role or region |
| 7-9 | Most users or all users of a major feature | Affects all authenticated users, all API consumers |
| 10 | All users, including unauthenticated visitors | Affects every request to the application |

**How to evaluate from code context**: Determine which user segments reach the vulnerable code path. Is it in the main authentication flow (all users) or a niche admin feature (few users)? Check route definitions and middleware to understand the reachability.

---

### D - Discoverability

**How easy is it for an attacker to find this vulnerability?**

| Score | Criteria | Examples |
|-------|----------|----------|
| 0 | Requires access to source code and deep analysis | Logic flaw buried in complex business rules, no external signals |
| 1-3 | Requires significant reverse engineering or insider knowledge | Undocumented internal endpoint, binary protocol analysis |
| 4-6 | Discoverable through systematic testing | Found via fuzzing, parameter manipulation, or directory brute-force |
| 7-9 | Easily found through standard reconnaissance | Visible in public API docs, appears in automated scanner output |
| 10 | Obvious, visible in the URL bar or public documentation | Predictable URL with sequential IDs, documented in Swagger UI |

**How to evaluate from code context**: Check whether the vulnerable endpoint is documented in OpenAPI/Swagger specs, whether it uses predictable naming conventions, and whether the vulnerability pattern would be caught by standard scanners (OWASP ZAP, Burp Suite passive scan).

---

## Score Calculation

```
DREAD Score = (Damage + Reproducibility + Exploitability + Affected Users + Discoverability) / 5
```

The result is a value between 0.0 and 10.0.

## Severity Mapping

| Score Range | Severity | Action |
|-------------|----------|--------|
| 8.0 - 10.0 | CRITICAL | Immediate remediation required. Stop-the-line. |
| 5.0 - 7.9 | HIGH | Remediate before next release. Escalate to security team. |
| 3.0 - 4.9 | MEDIUM | Schedule for remediation within current sprint or cycle. |
| 0.0 - 2.9 | LOW | Track and remediate as time permits. Accept risk if justified. |

---

## Example Scoring Walkthrough

**Finding**: SQL injection in a public-facing search endpoint.

The endpoint `/api/products?search=<user_input>` constructs a SQL query via string concatenation:
```python
query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
```

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Damage** | 8 | Attacker can read the entire database (all tables), potentially including user credentials and payment info. Could escalate to OS command execution via `xp_cmdshell` or `COPY TO PROGRAM` depending on DBMS. |
| **Reproducibility** | 10 | Works every time. A single crafted request triggers the injection. No special state or timing required. |
| **Exploitability** | 9 | sqlmap automates the entire attack. The attacker only needs the URL. Public tutorials abound for this exact pattern. |
| **Affected Users** | 9 | The products endpoint is unauthenticated and public-facing. A data breach from this vector would affect all users whose data is in the database. |
| **Discoverability** | 9 | The search parameter is visible in the URL and documented in the API docs. Any automated scanner would flag string concatenation in SQL. A single apostrophe in the search box reveals the vulnerability. |

**DREAD Score**: (8 + 10 + 9 + 9 + 9) / 5 = **9.0 -- CRITICAL**

**Recommendation**: Immediate remediation. Switch to parameterized queries. Deploy a WAF rule as a temporary mitigation while the code fix is tested and released.

---

## Second Example: Insecure Direct Object Reference

**Finding**: IDOR in a user profile endpoint behind authentication.

The endpoint `/api/users/{id}/profile` returns the full profile for any user ID without ownership checks:
```python
@app.get("/api/users/{id}/profile")
def get_profile(id: int, user = Depends(require_auth)):
    return db.profiles.find_by_user_id(id)
```

| Factor | Score | Rationale |
|--------|-------|-----------|
| **Damage** | 5 | Exposes user profile data (name, email, phone). No credentials or payment info in this table. |
| **Reproducibility** | 10 | Deterministic. Change the ID in the URL, get a different profile every time. |
| **Exploitability** | 10 | Trivial. Increment the user ID in the browser address bar. No tools needed. |
| **Affected Users** | 8 | All users with profiles are exposed. Requires authentication, so not fully public. |
| **Discoverability** | 8 | The endpoint is in the API docs. Sequential IDs make enumeration obvious. |

**DREAD Score**: (5 + 10 + 10 + 8 + 8) / 5 = **8.2 -- CRITICAL**

Despite the moderate damage, the extreme ease of exploitation and broad scope push this into CRITICAL.

---

## Common Scoring Pitfalls

- **Conflating damage with likelihood**: Damage should reflect the worst-case outcome, not how likely the attack is. Likelihood is captured by Reproducibility and Exploitability.
- **Defaulting Discoverability to high**: Not every vulnerability is easy to find. A logic flaw in a multi-step workflow is harder to discover than an exposed admin panel.
- **Ignoring existing mitigations**: If a WAF blocks the attack vector, Exploitability should reflect the additional effort to bypass it.
- **Scoring based on the vulnerability class rather than the instance**: A SQL injection in an internal admin tool behind VPN scores differently than one on a public search page.

---

## DREAD vs CVSS

| Aspect | DREAD | CVSS |
|--------|-------|------|
| **Complexity** | Simple, 5 intuitive factors | Detailed, 8+ metrics across 3 groups |
| **Speed** | Fast to score, good for triage | Slower, more rigorous |
| **Subjectivity** | Higher, relies on analyst judgment | Lower, more standardized definitions |
| **Industry adoption** | Internal use, threat modeling | Industry standard for CVEs and advisories |
| **Best for** | Internal audits, code review triage, threat modeling | Public vulnerability disclosure, compliance reporting |

Use DREAD when you need to rapidly prioritize a batch of findings during a security review. Use CVSS when you need an industry-standard score for a published advisory or compliance requirement.

---

## Integration with the Appsec Plugin

DREAD scoring is used by the **red team agents in expert mode** to rate findings during deep-dive analysis. When a red team agent identifies a vulnerability:

1. The agent evaluates each of the 5 DREAD factors based on the code context
2. Each factor is scored on the 0-10 scale using the criteria above
3. The average produces the overall DREAD score
4. The severity mapping determines the finding's priority level
5. The score and per-factor rationale are included in the finding report

This provides a fast, explainable risk rating that helps developers understand not just what the vulnerability is, but why it matters and how urgently it needs to be fixed.

### Scoring Template

```markdown
### DREAD Assessment

| Factor | Score | Rationale |
|--------|-------|-----------|
| Damage | X/10 | [What can be damaged and how severely] |
| Reproducibility | X/10 | [How reliably the exploit works] |
| Exploitability | X/10 | [Skill and tooling required] |
| Affected Users | X/10 | [Scope of impact] |
| Discoverability | X/10 | [How easily found] |

**DREAD Score**: X.X / 10 -- [SEVERITY]
```
