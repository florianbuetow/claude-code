---
name: learn
description: >
  This skill should be used when the user asks to "learn about security",
  "teach me OWASP", "security tutorial", "learn threat modeling", or
  invokes /appsec:learn. Interactive guided walkthrough using your
  codebase as teaching material.
---

# AppSec Learn -- Interactive Security Walkthrough

Guided, interactive learning experience that teaches security concepts
using the user's own codebase as teaching material. Combines explanation
with hands-on discovery -- the user finds real vulnerabilities in their
own code as they learn about each category.

This skill runs entirely in the main agent context. It does NOT dispatch
subagents. It is interactive and conversational -- ask questions, wait for
answers, then reveal findings.

## Learning Modes

Detect the topic from the user's message:

| User Says | Mode | Curriculum |
|-----------|------|------------|
| "learn owasp", "teach me owasp" | OWASP Walkthrough | All 10 categories |
| "learn stride", "teach me stride" | STRIDE Walkthrough | All 6 categories |
| "learn red-team", "learn red teaming" | Red Team Walkthrough | All 6 personas |
| "learn injection", "learn A03" | Single Category Deep Dive | One category |
| "learn security", "security tutorial" | Guided Selection | Ask what to learn |

## Framework References

Load the relevant framework reference before starting:

| Mode | Reference File |
|------|---------------|
| OWASP | [`../../shared/frameworks/owasp-top10-2021.md`](../../shared/frameworks/owasp-top10-2021.md) |
| STRIDE | [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md) |
| Red Team | [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md) + all persona files in `agents/` |
| Single Category | The relevant framework file for that category |

## Walkthrough Structure

Each learning mode follows the same 4-step pattern per category. The key
principle: NEVER just lecture. Always ground the concept in the user's own
code, and always make them think before revealing answers.

### Step 1: Explain the Concept

Present the category in plain language:
- What it is (one sentence).
- What security property it protects.
- Why it matters (real-world impact with a notable breach example).
- How it maps to other frameworks (OWASP <-> STRIDE <-> CWE).

Keep this brief. 5-8 sentences maximum. The user's code is the real teacher.

### Step 2: Show Code from the User's Codebase

Search the user's codebase for patterns relevant to this category. Use
Glob and Grep to find concrete examples. Show 2-3 code snippets with
file paths and line numbers.

Present the code WITHOUT revealing whether it is vulnerable or secure.
Frame it as: "Here is how your codebase handles [concept]. Look at these
patterns..."

**Search strategy by category:**

| Category | What to Search For |
|----------|-------------------|
| Injection (A03) | Database queries, template rendering, shell commands, user input handling |
| Access Control (A01) | Route middleware, authorization checks, role guards, IDOR-prone endpoints |
| Crypto (A02) | Hashing functions, encryption calls, TLS config, key storage |
| Auth (A07) | Login handlers, session management, password storage, token generation |
| Spoofing (S) | Authentication flows, token validation, session handling |
| Tampering (T) | Input validation, request parsing, file operations |
| Info Disclosure (I) | Error handlers, logging statements, API responses |
| DoS (D) | Regex patterns, file uploads, resource allocation, unbounded loops |
| Red Team | Attack surface entry points, auth boundaries, data flows |

If no relevant code is found for a category, use a generic example and note
that the category may not be applicable to this codebase.

### Step 3: Ask Questions

Ask the user 2-3 questions about the code you showed. These should guide
them to discover potential issues themselves:

- "What happens if [input] contains [malicious value]?"
- "Is there anything checking that the user owns this resource?"
- "What would an attacker see if they triggered this error handler?"
- "Could a malicious user bypass this check? How?"

Wait for the user to respond before proceeding. Do NOT reveal the answers
in the same message as the questions.

### Step 4: Reveal and Discuss

After the user responds (or asks to see the answer):

1. Confirm what they got right.
2. Explain what they missed and why it matters.
3. Show the specific vulnerability (if one exists) with the attack scenario.
4. Show the fix -- both the code change and the principle behind it.
5. Cross-reference to frameworks: "This is CWE-89, which OWASP categorizes
   as A03, and STRIDE classifies as Tampering (T)."

Then offer to continue to the next category or dive deeper.

## OWASP Walkthrough Curriculum

Walk through all 10 categories in priority order (most commonly exploited
first, not numerical order):

1. **A03: Injection** -- SQL, NoSQL, OS command, template injection
2. **A07: Auth Failures** -- Credential stuffing, weak passwords, sessions
3. **A01: Broken Access Control** -- IDOR, missing deny-by-default, CORS
4. **A02: Cryptographic Failures** -- Weak hashing, cleartext, key mgmt
5. **A05: Security Misconfiguration** -- Defaults, verbose errors, headers
6. **A10: SSRF** -- Unvalidated URLs, internal network access
7. **A08: Integrity Failures** -- Deserialization, CI/CD, unsigned updates
8. **A06: Vulnerable Components** -- Known CVEs, unmaintained packages
9. **A09: Logging Failures** -- Missing audit trail, log injection
10. **A04: Insecure Design** -- Missing threat modeling, business logic flaws

## STRIDE Walkthrough Curriculum

Walk through all 6 categories mapping each to the security property it
protects:

1. **S -- Spoofing** (Authentication) -- Identity impersonation, session hijack
2. **T -- Tampering** (Integrity) -- Input manipulation, data modification
3. **R -- Repudiation** (Non-repudiation) -- Missing audit trail, log gaps
4. **I -- Information Disclosure** (Confidentiality) -- Data leaks, error messages
5. **D -- Denial of Service** (Availability) -- Resource exhaustion, ReDoS
6. **E -- Elevation of Privilege** (Authorization) -- Horizontal/vertical escalation

## Red Team Walkthrough Curriculum

Teach offensive security thinking by walking through each attacker persona:

1. **Script Kiddie** -- Automated tools, known CVEs, low-hanging fruit.
   "What can an attacker with zero skill but lots of tools find?"
2. **Insider** -- Privilege escalation, data exfiltration, audit gaps.
   "What can a disgruntled employee with a valid account do?"
3. **Organized Crime** -- Financial fraud, account takeover, payment abuse.
   "What if the attacker's goal is money?"
4. **Hacktivist** -- Data leaks, defacement, public embarrassment.
   "What if the goal is to make the news?"
5. **Nation State** -- APT chains, persistent access, supply chain.
   "What if the attacker has unlimited time and resources?"
6. **Supply Chain** -- Dependency poisoning, build pipeline, artifact integrity.
   "What if the attack comes through your dependencies?"

For each persona, load the persona file from `agents/` and use its
checklist to search the user's codebase for exploitable patterns.

## Interaction Guidelines

- Keep the tone conversational and encouraging, not lecturing.
- Celebrate correct answers. Build on incorrect answers -- do not just say
  "wrong."
- If the user wants to skip a category, skip it without judgment.
- If the user wants to stop, summarize what was covered and suggest what
  to learn next time.
- After completing a full walkthrough, offer to run the corresponding
  analysis: "Want me to run a full OWASP scan now? /appsec:owasp"
- Adjust complexity based on the user's responses. If they immediately
  spot the SQL injection, skip the basics and go deeper. If they are
  struggling, add more context and simpler examples.

## Progress Tracking

After each category, provide a brief progress indicator:

```
[3/10] OWASP Walkthrough
  Completed: A03 Injection, A07 Auth, A01 Access Control
  Next: A02 Cryptographic Failures
  Continue? (or type 'skip' to move on, 'stop' to finish)
```

## Edge Cases

- **Empty codebase**: Use generic examples and note that hands-on practice
  requires a codebase with relevant patterns.
- **No relevant patterns found**: "Your code does not appear to have
  [pattern]. This is good! Let me show you what to watch for if you add
  [feature] in the future."
- **User asks a tangential question**: Answer it briefly, then guide back
  to the curriculum. If the question deserves depth, suggest
  `/appsec:explain <topic>` for a full explanation.
