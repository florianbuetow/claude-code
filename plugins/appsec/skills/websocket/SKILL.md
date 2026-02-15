---
name: websocket
description: >
  This skill should be used when the user asks to "check WebSocket security",
  "analyze WebSocket authentication", "find WebSocket vulnerabilities",
  "audit WebSocket handlers", "check for CSWSH", or mentions "WebSocket",
  "ws://", "wss://", "socket.io", "CSWSH", "WebSocket origin check",
  "WebSocket rate limit", or "WebSocket authentication" in a security context.
---

# WebSocket Security (WS)

Analyze WebSocket implementations for security vulnerabilities including
missing authentication on the upgrade handshake, no origin validation
(Cross-Site WebSocket Hijacking), absence of message validation, missing
rate limiting on messages, and use of unencrypted ws:// in production. WebSocket
connections are long-lived and bidirectional, making them a persistent attack
channel when not properly secured.

## Supported Flags

Read `../../shared/schemas/flags.md` for the full flag specification. This skill
supports all cross-cutting flags. Key flags for this skill:

- `--scope` determines which files to analyze (default: `changed`)
- `--depth standard` reads code and checks WebSocket handlers and configuration
- `--depth deep` traces message handling from connection through all event handlers
- `--severity` filters output (WebSocket issues are often `high` or `critical`)

## Framework Context

Key CWEs in scope:
- CWE-287: Improper Authentication (missing auth on upgrade)
- CWE-346: Origin Validation Error (CSWSH)
- CWE-20: Improper Input Validation (message validation)
- CWE-770: Allocation of Resources Without Limits (rate limiting)
- CWE-319: Cleartext Transmission of Sensitive Information (ws://)

## Detection Patterns

Read `references/detection-patterns.md` for the full catalog of code patterns,
search heuristics, language-specific examples, and false positive guidance.

## Workflow

### 1. Determine Scope

Parse flags and resolve the file list per `../../shared/schemas/flags.md`.
Filter to files likely to contain WebSocket logic:

- WebSocket server setup (`**/ws/**`, `**/websocket/**`, `**/socket/**`)
- Socket.IO / ws configuration (`**/io.*`, `**/socket.*`)
- Message handlers (`**/handlers/**`, `**/events/**`)
- Middleware for upgrade requests (`**/middleware/**`)
- Client WebSocket code (`**/client/**`, `**/frontend/**`)

### 2. Check for Available Scanners

Detect scanners per `../../shared/schemas/scanners.md`:

1. `semgrep` -- primary scanner for WebSocket patterns

Record which scanners are available and which are missing. WebSocket-specific
scanners are rare; most analysis relies on code review.

### 3. Run Scanners (If Available)

If semgrep is available, run with rules targeting WebSocket:
```
semgrep scan --config auto --json --quiet <target>
```
Filter results to rules matching WebSocket patterns. Normalize output to
the findings schema.

### 4. Claude Code Analysis

Regardless of scanner availability, perform manual code analysis:

1. **Authentication on upgrade**: Find WebSocket server creation and verify
   the upgrade/connection handler checks authentication (JWT, session cookie).
2. **Origin validation**: Check whether the server validates the `Origin` header
   during the WebSocket handshake to prevent CSWSH.
3. **Message validation**: Find message handlers and verify incoming messages
   are validated against a schema or type before processing.
4. **Rate limiting**: Check for per-connection or per-message rate limiting to
   prevent message flooding.
5. **Transport security**: Verify production configuration uses `wss://` not
   `ws://` for encrypted transport.
6. **Authorization per message type**: Verify sensitive operations sent via
   WebSocket check the user's permissions per action.

When `--depth deep`, additionally trace:
- Full message flow from receipt through handler to side effects
- Broadcast authorization (who receives which messages)
- Reconnection/resumption authentication

### 5. Report Findings

Format output per `../../shared/schemas/findings.md` using the `WS` prefix
(e.g., `WS-001`, `WS-002`).

Include for each finding:
- Severity and confidence
- Exact file location with code snippet
- Attack scenario for the WebSocket vulnerability
- Concrete fix with diff when possible
- CWE references

## What to Look For

These are the high-signal patterns specific to WebSocket security. Each maps
to a detection pattern in `references/detection-patterns.md`.

1. **Missing authentication on upgrade** -- WebSocket server accepts connections
   without verifying the client's identity during the HTTP upgrade handshake.

2. **No origin validation (CSWSH)** -- The server does not check the `Origin`
   header, allowing malicious websites to open WebSocket connections to the
   server using the victim's cookies.

3. **No message validation** -- Incoming WebSocket messages are parsed and
   processed without schema validation, enabling injection attacks.

4. **No rate limiting** -- No limit on message frequency, allowing a single
   client to flood the server with messages.

5. **Unencrypted transport (ws://)** -- Production WebSocket connections use
   `ws://` instead of `wss://`, exposing data in transit.

## Scanner Integration

| Scanner | Coverage | Command |
|---------|----------|---------|
| semgrep | WebSocket auth patterns, origin checks | `semgrep scan --config auto --json --quiet <target>` |

**Fallback (no scanner)**: Use Grep with patterns from `references/detection-patterns.md`
to find WebSocket server configuration, connection handlers, message handlers,
and origin checking logic. Report findings with `confidence: medium`.

## Output Format

Use the findings schema from `../../shared/schemas/findings.md`.

- **ID prefix**: `WS` (e.g., `WS-001`)
- **metadata.tool**: `websocket`
- **metadata.framework**: `specialized`
- **metadata.category**: `WS`
- **references.cwe**: `CWE-287`, `CWE-346`, `CWE-20`
- **references.owasp**: `A07:2021` (Identification and Authentication Failures)
- **references.stride**: `S` (Spoofing) or `T` (Tampering)

Severity guidance for this category:
- **critical**: No authentication on upgrade for sensitive APIs, CSWSH on authenticated endpoints
- **high**: Missing origin validation on cookie-authenticated endpoints, no message validation
- **medium**: No rate limiting, ws:// in production configuration
- **low**: Overly permissive origin allowlist, missing secondary validation
