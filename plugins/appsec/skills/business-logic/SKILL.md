---
name: business-logic
description: >
  This skill should be used when the user asks to "check business logic
  security", "find logic flaws", "audit workflow security", "check for
  coupon abuse", "detect negative amount exploits", "analyze state machine
  security", or mentions "business logic", "workflow bypass", "negative
  amount", "coupon abuse", "self-referral", "state manipulation", or
  "time-based exploit" in a security context.
---

# Business Logic Security (BIZ)

Analyze application business logic for security vulnerabilities including
workflow step bypassing, negative amount manipulation, coupon/discount abuse,
self-referral exploitation, state machine manipulation, and time-based logic
exploits. Business logic flaws are unique to each application and cannot be
detected by generic scanners -- they require understanding the intended
workflow and finding ways to subvert it.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks business rule implementations
- `--depth deep` traces full workflows from initiation through completion
- `--severity` filters output (business logic issues are often `high` or `critical`)

## Framework Context

Key CWEs in scope:
- CWE-840: Business Logic Errors
- CWE-841: Improper Enforcement of Behavioral Workflow
- CWE-799: Improper Control of Interaction Frequency
- CWE-837: Improper Enforcement of a Single, Unique Action
- CWE-20: Improper Input Validation

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain business logic:

- Payment and checkout (`**/payments/**`, `**/checkout/**`, `**/billing/**`)
- Order processing (`**/orders/**`, `**/cart/**`, `**/transactions/**`)
- Discount and coupon logic (`**/coupons/**`, `**/discounts/**`, `**/promotions/**`)
- Referral and reward systems (`**/referrals/**`, `**/rewards/**`, `**/loyalty/**`)
- Workflow and state machines (`**/workflows/**`, `**/state/**`, `**/status/**`)
- User account operations (`**/accounts/**`, `**/profiles/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- custom rules can catch some business logic patterns

Record which scanners are available. Business logic flaws are primarily
detected through manual code analysis, not automated scanners.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting business logic:
```
semgrep scan --config auto --json --quiet <target>
```
Filter for rules matching validation, state management, and numeric handling
patterns. Normalize output to the findings schema.

### 4. Claude Code Analysis

This is the primary detection method for business logic flaws:

1. **Workflow step bypass**: Map multi-step workflows (checkout, verification,
   approval) and verify each step cannot be skipped by calling later steps directly.
2. **Negative amount manipulation**: Find numeric inputs (amounts, quantities,
   prices) and verify the application rejects negative values.
3. **Coupon/discount abuse**: Find discount application logic and verify
   coupons cannot be applied multiple times, stacked beyond limits, or used
   after expiration.
4. **Self-referral exploitation**: Find referral systems and verify users
   cannot refer themselves or create circular referral chains.
5. **State machine integrity**: Map state transitions and verify invalid
   transitions are rejected (e.g., "shipped" cannot go back to "pending").
6. **Time-based logic**: Find logic depending on timestamps and verify it
   handles timezone manipulation, clock skew, and deadline race conditions.

When `--depth deep`, additionally trace:
- Full workflow paths from start to completion
- All possible state transitions and their guards
- Cross-endpoint workflow manipulation scenarios

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `BIZ` prefix
(e.g., `BIZ-001`, `BIZ-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Step-by-step exploit scenario
- Business impact (financial loss, unfair advantage)
- Concrete fix with diff when possible
- CWE references

## What to Look For

These are the high-signal patterns specific to business logic security. Each
maps to a detection pattern in `references/detection-patterns.md`.

1. **Workflow step bypass** -- Multi-step processes where a later step can be
   invoked directly without completing prior steps.

2. **Negative amount manipulation** -- Numeric inputs accepted without sign
   validation, allowing negative amounts to reverse charges or increase balances.

3. **Coupon/discount abuse** -- Discount codes applied multiple times, stacked
   beyond intended limits, or used on ineligible items.

4. **Self-referral exploitation** -- Referral reward systems that do not prevent
   users from referring themselves or creating fake referral chains.

5. **State machine manipulation** -- Invalid state transitions accepted by the
   system (e.g., marking an order as "delivered" before "shipped").

6. **Time-based logic exploits** -- Logic dependent on client-supplied
   timestamps, exploitable timezone handling, or deadline race conditions.

7. **Price manipulation** -- Client-supplied prices accepted without server-side
   verification against the product catalog.

8. **Quantity abuse** -- No limits on quantities enabling abuse (ordering
   negative quantities, exceeding stock, zero-quantity orders).

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | Numeric validation, some state patterns | `semgrep scan --config auto --json --quiet <target>` |

**Fallback (no scanner)**: Business logic flaws require manual code analysis.
Use Grep with patterns from `references/detection-patterns.md` to find
financial operations, state transitions, discount logic, and referral systems.
Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `BIZ` (e.g., `BIZ-001`)
- **metadata.tool**: `business-logic`
- **metadata.framework**: `specialized`
- **metadata.category**: `BIZ`
- **references.cwe**: `CWE-840`, `CWE-841`
- **references.owasp**: `A04:2021` (Insecure Design)
- **references.stride**: `T` (Tampering) or `E` (Elevation of Privilege)

Severity guidance for this category:
- **critical**: Direct financial loss (negative amounts in payments, price manipulation)
- **high**: Workflow bypass on security-critical processes, unlimited discount stacking
- **medium**: Self-referral abuse, state manipulation with limited business impact
- **low**: Minor workflow inconsistencies, cosmetic state issues
