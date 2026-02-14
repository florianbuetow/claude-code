---
name: explain
description: >
  This skill should be used when the user asks to "explain security concept",
  "what is OWASP", "explain this finding", "what does this vulnerability mean",
  "explain stride", "explain injection", "what is CSRF", "explain spoofing",
  "what does INJ-003 mean", "compare stride vs pasta", or asks any question
  about security terminology, frameworks, vulnerability categories, or specific
  findings. Works at framework, category, finding, and comparison levels.
---

# Security Explainer

Interactive explainer for security frameworks, threat categories, vulnerability
findings, and security concepts. Works at multiple levels of depth -- from a
broad framework overview down to a single finding ID. Always uses the user's
own codebase for concrete examples when possible.

## Explanation Levels

Detect what the user is asking about and respond at the appropriate level:

### Level 1: Framework

Triggered by framework names: STRIDE, OWASP, PASTA, LINDDUN, MITRE ATT&CK,
SANS/CWE Top 25, DREAD.

**What to cover:**
1. What the framework is, who created it, and when to use it.
2. All categories/stages within the framework (e.g., all 6 STRIDE letters,
   all 10 OWASP categories, all 7 PASTA stages).
3. For each category: one-sentence description and a real code example from
   the user's codebase if available.
4. How the framework relates to other frameworks (cross-mappings).
5. When to choose this framework over alternatives.

**Framework references to read:**
- STRIDE: [`../../shared/frameworks/stride.md`](../../shared/frameworks/stride.md)
- OWASP Top 10: [`../../shared/frameworks/owasp-top10-2021.md`](../../shared/frameworks/owasp-top10-2021.md)
- PASTA: [`../../shared/frameworks/pasta.md`](../../shared/frameworks/pasta.md)
- LINDDUN: [`../../shared/frameworks/linddun.md`](../../shared/frameworks/linddun.md)
- MITRE ATT&CK: [`../../shared/frameworks/mitre-attck.md`](../../shared/frameworks/mitre-attck.md)
- SANS/CWE Top 25: [`../../shared/frameworks/sans-cwe-top25.md`](../../shared/frameworks/sans-cwe-top25.md)
- DREAD: [`../../shared/frameworks/dread.md`](../../shared/frameworks/dread.md)
- OWASP API Top 10: [`../../shared/frameworks/owasp-api-top10.md`](../../shared/frameworks/owasp-api-top10.md)

### Level 2: Category

Triggered by category names: "spoofing", "tampering", "injection",
"broken access control", "A01", "A03", "STRIDE-S", "CWE-89", etc.

**What to cover:**
1. Full definition of the category and which framework(s) it belongs to.
2. The security property it protects (e.g., Spoofing protects Authentication).
3. Common attack techniques in this category (3-5 examples).
4. Real code patterns from the user's codebase that are relevant. Use Grep
   and Glob to find concrete examples.
5. How to detect vulnerabilities in this category.
6. How to prevent or remediate them.
7. Related categories in other frameworks (cross-mapping).

### Level 3: Finding

Triggered by finding IDs: "INJ-003", "SPOOF-001", "AC-005", "SEC-002", etc.
Also triggered by phrases like "explain this finding" or "what does this
vulnerability mean" when a finding was recently reported.

**What to cover:**
1. What the finding means in plain language.
2. Why it is dangerous -- concrete attack scenario.
3. How an attacker would exploit it step by step.
4. The severity and confidence ratings and why they were assigned.
5. Framework and CWE cross-references.
6. Step-by-step remediation with code diff.
7. How to verify the fix is correct.
8. Similar vulnerabilities to watch for in the same codebase.

### Level 4: Comparison

Triggered by "vs", "versus", "compared to", "difference between", or
listing multiple frameworks/categories.

**What to cover:**
1. Side-by-side overview of each item being compared.
2. Key differences in approach, scope, and philosophy.
3. When to use each one.
4. Overlap and complementary strengths.
5. Recommendation for the user's specific use case.

**Common comparisons:**
- STRIDE vs PASTA: Categorization vs process-oriented
- STRIDE vs LINDDUN: Security threats vs privacy threats
- OWASP Top 10 vs SANS/CWE Top 25: Web app risks vs software weaknesses
- OWASP Top 10 vs OWASP API Top 10: Web apps vs API-specific risks
- DREAD vs CVSS: Qualitative vs quantitative risk scoring

## Workflow

### 1. Parse the Query

Determine:
- **Level**: Framework, category, finding, or comparison.
- **Subject(s)**: Which specific framework(s), category(ies), or finding(s).
- **Context**: Is there a recent analysis whose findings can be referenced?

### 2. Load References

Read the relevant framework reference file(s) from `shared/frameworks/`.
For finding explanations, also read the relevant skill's SKILL.md and
detection patterns.

### 3. Search the Codebase

Use Glob and Grep to find real examples from the user's codebase that
illustrate the concept. This grounds the explanation in the user's actual
code rather than generic examples.

**Search strategy by level:**
- **Framework**: Scan for patterns relevant to each category. Show 1 example
  per category to make the framework tangible.
- **Category**: Deep search for patterns specific to that category. Show 3-5
  real examples with file paths and line numbers.
- **Finding**: Read the specific file and lines referenced in the finding.
  Also search for similar patterns elsewhere in the codebase.
- **Comparison**: Search for examples that highlight the difference between
  the compared items.

### 4. Explain

Present the explanation at the appropriate level. Use clear headings,
concrete code examples, and practical language. Avoid jargon without
definition. When referencing CWEs or other identifiers, briefly explain
what they mean.

### 5. Offer Follow-Up

Always end with a contextual follow-up offer:

| Situation | Offer |
|-----------|-------|
| Explained a framework | "Want me to run a full {framework} analysis on your codebase?" |
| Explained a category | "Want me to scan your code specifically for {category} issues?" |
| Explained a finding | "Want me to generate the fix?" or "Want me to check for similar issues?" |
| Compared frameworks | "Want me to run {recommended framework} on your codebase?" |
| Generic concept | "Want me to check your code for related vulnerabilities?" |

## Presentation Guidelines

- Start with a one-sentence plain-language summary before diving into detail.
- Use tables for structured comparisons and cross-references.
- Show code snippets from the user's codebase when available, with file paths.
- For findings, always include the attack scenario as a numbered step list.
- Keep explanations practical. Developers want to know "what do I do about
  this?" not just "what is this?".
- When explaining severity, connect it to real-world impact: "critical means
  an attacker can do X without authentication."

## Edge Cases

- **Unknown term**: If the user asks about something not in the loaded
  frameworks, provide the best explanation possible from general security
  knowledge and note which frameworks/CWEs are related.
- **Ambiguous query**: If "explain injection" could mean SQL injection,
  command injection, or the OWASP A03 category, briefly cover all and ask
  which the user wants to dive deeper into.
- **Finding not in context**: If the user references a finding ID that was
  not part of a recent analysis, explain what findings with that prefix
  typically represent (e.g., "INJ findings are injection vulnerabilities
  detected by the injection skill") and offer to run the relevant scan.
