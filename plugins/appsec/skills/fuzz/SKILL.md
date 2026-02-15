---
name: fuzz
description: >
  This skill should be used when the user asks to "generate fuzz inputs",
  "create fuzz tests", "fuzz test generation", "generate test payloads",
  "create security test cases", or "generate edge case inputs". Also
  triggers when the user wants intelligent test inputs for input parsers,
  API endpoints, file format handlers, or needs context-aware injection
  payloads for security testing.
---

# Fuzz Input Generation

Generate intelligent, context-aware fuzz test inputs by analyzing input
parsing code. Produces boundary values, type confusion inputs, encoding
edge cases, format-specific attacks, and injection payloads tailored to the
specific parser and data types in scope. Output is structured JSON test
case sets ready for integration with test harnesses.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification.

| Flag | Fuzz Behavior |
|------|-------------|
| `--scope` | Identifies which input handlers to generate fuzz inputs for. Default `changed`. |
| `--depth quick` | Standard boundary values and common injection strings only. |
| `--depth standard` | Context-aware inputs based on code analysis of the parser. |
| `--depth deep` | Standard + format-specific attacks, encoding mutations, and chained payloads. |
| `--depth expert` | Deep + adversarial inputs designed to bypass specific validation logic found in code. |
| `--severity` | Generate inputs targeting vulnerabilities at or above this severity. |
| `--format` | Default `json`. Use `text` for human-readable listing. |

## Workflow

### Step 1: Identify Input Handlers

Locate input parsing and processing code in scope:

1. **API endpoint handlers**: Functions that read request body, query params, headers.
2. **File parsers**: Functions that parse uploaded files, config files, data imports.
3. **CLI argument parsers**: Argument parsing with `argparse`, `commander`, `cobra`, `clap`.
4. **Message consumers**: Functions processing messages from queues, WebSockets, SSE.
5. **Deserialization points**: JSON.parse, XML parsing, YAML loading, protobuf decoding.
6. **Database query builders**: Functions constructing queries from user input.

For each handler, identify:
- Expected input type (string, number, array, object, file).
- Validation rules (regex, schema, type checks, length limits).
- How the input is used downstream (SQL, shell, HTML, file path, URL, regex).

### Step 2: Analyze Input Constraints

Read the code to understand what the parser expects and what it guards against:

1. **Type expectations**: What types does the code assume? Where are type coercions?
2. **Length limits**: Are there explicit length checks? What happens at max length?
3. **Character restrictions**: Are certain characters filtered or escaped? Which ones?
4. **Format requirements**: Does the input need to match a pattern (email, URL, date)?
5. **Range constraints**: Numeric bounds, enum values, allowed file extensions.
6. **Nested structure**: How deep can objects/arrays nest? Are there recursion limits?

### Step 3: Generate Boundary Value Inputs

For each input field, generate boundary value test cases:

| Input Type | Boundary Values |
|-----------|----------------|
| String | Empty `""`, single char `"a"`, max length, max length + 1, unicode BOM, null bytes `"\x00"` |
| Number | 0, -1, MAX_INT, MIN_INT, MAX_INT+1, NaN, Infinity, -Infinity, float precision edge cases |
| Array | Empty `[]`, single element, very large array (10000+), nested arrays, mixed types |
| Object | Empty `{}`, deeply nested (100+ levels), circular reference attempt, prototype keys |
| Boolean | `true`, `false`, `0`, `1`, `""`, `"false"`, `null`, `undefined` |
| Date | Epoch 0, negative timestamp, far future, invalid dates (Feb 30), timezone edge cases |
| File | Empty file, 0-byte, huge file, wrong extension, polyglot file, symlink |

### Step 4: Generate Type Confusion Inputs

Inputs designed to exploit type coercion and type assumption bugs:

Generate inputs that send the wrong type: string where number expected, array where string expected, object with `toString` override, deeply nested arrays, null where required, boolean where string expected, numeric string where number expected, and prototype/constructor pollution objects (`__proto__`, `constructor.prototype`).

### Step 5: Generate Encoding Edge Cases

Inputs exploiting encoding and character set handling:

1. **Unicode**: Normalization forms (NFC, NFD, NFKC, NFKD), homoglyphs, right-to-left override, zero-width characters.
2. **URL encoding**: Double encoding (`%2527`), mixed encoding, overlong UTF-8.
3. **HTML entities**: Named (`&amp;`), numeric (`&#38;`), hex (`&#x26;`), surrogate pairs.
4. **Null bytes**: Mid-string null bytes for truncation attacks.
5. **Line endings**: `\r\n`, `\r`, `\n`, `\x0b`, `\x0c`, `\x85`, `\u2028`, `\u2029`.
6. **Case mapping**: Turkish locale `I`/`i` dotless variants, German `ß`/`SS`.

### Step 6: Generate Context-Aware Injection Payloads

Based on how the input is used downstream (identified in Step 1), generate targeted payloads:

| Sink Context | Payload Category |
|-------------|-----------------|
| SQL query | SQL injection: UNION, boolean blind, time blind, stacked queries, comment-based |
| Shell command | Command injection: semicolons, pipes, backticks, `$()`, newlines |
| HTML output | XSS: script tags, event handlers, SVG/MathML, template injection |
| File path | Path traversal: `../`, null bytes, long paths, reserved names (CON, NUL) |
| URL construction | SSRF: localhost variants, IPv6, DNS rebinding, scheme confusion |
| Regex input | ReDoS: catastrophic backtracking patterns, exponential quantifiers |
| XML parser | XXE: external entity, parameter entity, SSRF via DTD |
| LDAP query | LDAP injection: wildcards, boolean operators, null bytes |
| Header value | Header injection: CRLF, response splitting |
| JSON parser | JSON interoperability: duplicate keys, large numbers, deep nesting |

### Step 7: Generate Format-Specific Attacks

At `--depth deep` and above, generate inputs targeting specific file/data formats:

1. **JSON**: Duplicate keys (parser-dependent behavior), comments, trailing commas, BOM prefix.
2. **XML**: Billion laughs, quadratic blowup, external entities, CDATA abuse.
3. **YAML**: Anchor bombs, merge keys, tag deserialization (`!!python/object`).
4. **CSV**: Formula injection (`=CMD()`), field separator in values, newlines in quoted fields.
5. **JWT**: Algorithm none, key confusion (RS256/HS256), expired but valid signature.
6. **GraphQL**: Deep nesting, alias flooding, batch query abuse, introspection.
7. **Multipart**: Boundary manipulation, filename traversal, content-type mismatch.

### Step 8: Output Test Case Sets

Organize all generated inputs into structured JSON test case sets:

```json
{
  "target": {
    "file": "src/api/users.ts",
    "function": "createUser",
    "input_field": "email",
    "expected_type": "string",
    "downstream_use": ["sql_query", "html_email"]
  },
  "generated_at": "2026-02-14T10:30:00Z",
  "total_cases": 85,
  "test_cases": [
    {
      "id": "FUZZ-001",
      "category": "boundary",
      "label": "empty_string",
      "input": "",
      "expected_behavior": "validation_error",
      "targets_cwe": "CWE-20"
    },
    {
      "id": "FUZZ-002",
      "category": "injection_sql",
      "label": "union_select",
      "input": "test@test.com' UNION SELECT * FROM users--",
      "expected_behavior": "parameterized_query_prevents_injection",
      "targets_cwe": "CWE-89"
    }
  ]
}
```

Write test case files to `.appsec/fuzz/` organized by target.

## Output Format

Fuzz inputs are not findings themselves but may reference CWEs they target.

Finding ID prefix: **FUZZ** (e.g., `FUZZ-001`) for test case identification.

- `metadata.tool`: `"fuzz"`

If fuzz testing reveals an actual vulnerability (input causes unexpected behavior), emit a finding using `../../shared/schemas/findings.md`.

## Pragmatism Notes

- Generate inputs relevant to the actual technology. Do not generate SQL injection payloads for code that never touches a database.
- Respect the `--depth` flag. Quick depth should produce 10-20 inputs. Expert depth can produce hundreds.
- Label each input clearly so testers understand what it targets and what behavior to expect.
- Mark intentionally dangerous inputs (e.g., billion laughs XML) with a warning about resource consumption.
- These are test inputs, not exploit code. Frame output as defensive testing material.
- If the code already has strong validation visible in the source, generate inputs that specifically test the validation boundaries.
- Include both inputs that should be rejected (malicious) and inputs that should be accepted (edge case valid) to test for false positives in validation.
