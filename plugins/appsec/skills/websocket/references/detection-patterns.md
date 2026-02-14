# WebSocket Detection Patterns

Patterns for detecting WebSocket-specific security vulnerabilities including
missing authentication, CSWSH, message validation, and transport security.

---

## 1. Missing Authentication on WebSocket Upgrade

**Description**: The WebSocket server accepts upgrade requests without verifying
the client's identity. Unlike HTTP endpoints where middleware enforces
authentication on every request, WebSocket connections are long-lived --
a single missing check grants persistent unauthenticated access.

**Search Heuristics**:
- Grep: `new WebSocket\.Server|WebSocketServer|ws\.Server` without auth in `verifyClient`
- Grep: `io\.on\(['"]connection['"]|wss\.on\(['"]connection['"]` without auth check
- Grep: `verifyClient|handleUpgrade|upgrade` to find auth implementation
- Grep: `socket\.handshake\.auth|socket\.handshake\.query` (Socket.IO auth patterns)
- Glob: `**/ws/**`, `**/websocket/**`, `**/socket/**`, `**/server.*`

**Language Examples**:

JavaScript (ws) -- VULNERABLE:
```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  // No authentication -- anyone can connect
  ws.on('message', (data) => handleMessage(ws, data));
});
```

JavaScript (ws) -- FIXED:
```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({
  port: 8080,
  verifyClient: (info, callback) => {
    const token = new URL(info.req.url, 'http://localhost').searchParams.get('token');
    try {
      const user = jwt.verify(token, SECRET);
      info.req.user = user;
      callback(true);
    } catch (err) {
      callback(false, 401, 'Unauthorized');
    }
  },
});
```

Python (websockets) -- VULNERABLE:
```python
import websockets

async def handler(websocket, path):
    async for message in websocket:
        await process(message)  # No auth check

asyncio.run(websockets.serve(handler, "0.0.0.0", 8080))
```

Python (websockets) -- FIXED:
```python
import websockets

async def handler(websocket, path):
    token = websocket.request_headers.get("Authorization", "").replace("Bearer ", "")
    try:
        user = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        await websocket.close(1008, "Unauthorized")
        return
    async for message in websocket:
        await process(message, user)

asyncio.run(websockets.serve(handler, "0.0.0.0", 8080))
```

Java (Spring) -- VULNERABLE:
```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(myHandler(), "/ws");  // No auth interceptor
    }
}
```

Java (Spring) -- FIXED:
```java
@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {
    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(myHandler(), "/ws")
            .addInterceptors(new AuthHandshakeInterceptor());
    }
}
```

Go (gorilla/websocket) -- VULNERABLE:
```go
func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)  // No auth check before upgrade
    if err != nil { return }
    for { /* handle messages */ }
}
```

Go (gorilla/websocket) -- FIXED:
```go
func wsHandler(w http.ResponseWriter, r *http.Request) {
    user, err := authenticateRequest(r)
    if err != nil {
        http.Error(w, "Unauthorized", http.StatusUnauthorized)
        return
    }
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil { return }
    // user is authenticated for this connection
}
```

**Scanner Coverage**: semgrep `javascript.ws.security.missing-auth-websocket`

**False Positive Guidance**: Public WebSocket endpoints (public chat rooms,
stock tickers, notifications that contain no sensitive data) may intentionally
skip authentication. Check whether the WebSocket handler accesses or transmits
user-specific or sensitive data.

**Severity Assessment**:
- **critical**: No auth on WebSocket serving sensitive data or accepting commands
- **high**: No auth on WebSocket with access to user-specific data
- **medium**: Weak auth (token in query string without TLS) on sensitive endpoints

---

## 2. No Origin Validation (Cross-Site WebSocket Hijacking)

**Description**: The server does not validate the `Origin` header during the
WebSocket handshake. A malicious website can open a WebSocket connection to the
target server using the victim's cookies, reading responses and sending messages
as the authenticated user (Cross-Site WebSocket Hijacking / CSWSH).

**Search Heuristics**:
- Grep: `origin|Origin|checkOrigin|allowedOrigins|cors` in WebSocket configuration
- Grep: `upgrader\.CheckOrigin\s*=\s*func.*return true` (Go -- disabling origin check)
- Grep: `verifyClient` without origin validation
- Grep: `cors:\s*\{.*origin:\s*['"]?\*` in Socket.IO configuration
- Glob: `**/ws/**`, `**/websocket/**`, `**/socket/**`

**Language Examples**:

JavaScript (ws) -- VULNERABLE:
```javascript
const wss = new WebSocket.Server({ port: 8080 });
// ws library does not check Origin by default
```

JavaScript (ws) -- FIXED:
```javascript
const ALLOWED_ORIGINS = ['https://app.example.com'];

const wss = new WebSocket.Server({
  port: 8080,
  verifyClient: (info) => {
    const origin = info.origin || info.req.headers.origin;
    return ALLOWED_ORIGINS.includes(origin);
  },
});
```

Python (websockets) -- VULNERABLE:
```python
async def handler(websocket, path):
    # No origin check
    async for message in websocket:
        await process(message)
```

Python (websockets) -- FIXED:
```python
ALLOWED_ORIGINS = {"https://app.example.com"}

async def handler(websocket, path):
    origin = websocket.request_headers.get("Origin", "")
    if origin not in ALLOWED_ORIGINS:
        await websocket.close(1008, "Origin not allowed")
        return
    async for message in websocket:
        await process(message)
```

Java (Spring) -- VULNERABLE:
```java
registry.addHandler(myHandler(), "/ws")
    .setAllowedOrigins("*");  // All origins allowed
```

Java (Spring) -- FIXED:
```java
registry.addHandler(myHandler(), "/ws")
    .setAllowedOrigins("https://app.example.com");
```

Go (gorilla/websocket) -- VULNERABLE:
```go
var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true  // Allows all origins
    },
}
```

Go (gorilla/websocket) -- FIXED:
```go
var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        origin := r.Header.Get("Origin")
        return origin == "https://app.example.com"
    },
}
```

**Scanner Coverage**: semgrep `go.gorilla.security.websocket-check-origin-disabled`

**False Positive Guidance**: WebSocket endpoints that use token-based auth
(not cookies) are not vulnerable to CSWSH because the malicious site cannot
provide the token. Only flag CSWSH when cookie-based authentication is used
without origin validation.

**Severity Assessment**:
- **critical**: CSWSH on endpoints with cookie auth and sensitive operations
- **high**: No origin check on cookie-authenticated WebSocket endpoints
- **medium**: Overly permissive origin list on authenticated endpoints
- **low**: No origin check on token-authenticated endpoints (lower CSWSH risk)

---

## 3. Missing Message Validation

**Description**: Incoming WebSocket messages are parsed (typically as JSON) and
their fields are used directly without schema validation. This enables injection
attacks, type confusion, and unexpected application behavior through malformed
or malicious messages.

**Search Heuristics**:
- Grep: `JSON\.parse\(.*message|json\.loads\(.*message` without schema validation
- Grep: `ws\.on\(['"]message['"].*JSON\.parse` without subsequent validation
- Grep: `socket\.on\(['"].*JSON\.parse` (Socket.IO custom event handling)
- Grep: `joi|zod|ajv|pydantic|validate|ValidationError` near WebSocket handlers
- Glob: `**/handlers/**`, `**/events/**`, `**/ws/**`

**Language Examples**:

JavaScript -- VULNERABLE:
```javascript
ws.on('message', (raw) => {
  const msg = JSON.parse(raw);
  // Directly use msg fields without validation
  db.query(`UPDATE users SET name = $1 WHERE id = $2`, [msg.name, msg.userId]);
});
```

JavaScript -- FIXED:
```javascript
const Joi = require('joi');
const messageSchema = Joi.object({
  type: Joi.string().valid('updateName').required(),
  name: Joi.string().max(100).required(),
  userId: Joi.number().integer().positive().required(),
});

ws.on('message', (raw) => {
  const { error, value } = messageSchema.validate(JSON.parse(raw));
  if (error) { ws.send(JSON.stringify({ error: 'Invalid message' })); return; }
  db.query(`UPDATE users SET name = $1 WHERE id = $2`, [value.name, value.userId]);
});
```

Python -- VULNERABLE:
```python
async def handler(websocket):
    async for raw in websocket:
        msg = json.loads(raw)
        await db.execute("UPDATE users SET name = %s WHERE id = %s",
                         (msg["name"], msg["userId"]))  # No validation
```

Python -- FIXED:
```python
from pydantic import BaseModel, validator

class UpdateNameMsg(BaseModel):
    type: str
    name: str
    userId: int

    @validator('name')
    def name_length(cls, v):
        if len(v) > 100: raise ValueError('Name too long')
        return v

async def handler(websocket):
    async for raw in websocket:
        try:
            msg = UpdateNameMsg(**json.loads(raw))
        except (json.JSONDecodeError, ValidationError):
            await websocket.send(json.dumps({"error": "Invalid message"}))
            continue
        await db.execute("UPDATE users SET name = %s WHERE id = %s",
                         (msg.name, msg.userId))
```

Java -- VULNERABLE:
```java
@Override
public void handleTextMessage(WebSocketSession session, TextMessage message) {
    JsonNode msg = objectMapper.readTree(message.getPayload());
    String name = msg.get("name").asText();  // No validation
    userRepo.updateName(msg.get("userId").asLong(), name);
}
```

Java -- FIXED:
```java
@Override
public void handleTextMessage(WebSocketSession session, TextMessage message) {
    UpdateNameRequest req = objectMapper.readValue(message.getPayload(), UpdateNameRequest.class);
    // UpdateNameRequest uses @Valid annotations
    Set<ConstraintViolation<UpdateNameRequest>> violations = validator.validate(req);
    if (!violations.isEmpty()) { session.sendMessage(new TextMessage("Invalid")); return; }
    userRepo.updateName(req.getUserId(), req.getName());
}
```

Go -- VULNERABLE:
```go
func handleMessage(conn *websocket.Conn) {
    var msg map[string]interface{}
    conn.ReadJSON(&msg)  // No validation
    db.Exec("UPDATE users SET name = $1 WHERE id = $2", msg["name"], msg["userId"])
}
```

Go -- FIXED:
```go
type UpdateNameMsg struct {
    Type   string `json:"type" validate:"required,eq=updateName"`
    Name   string `json:"name" validate:"required,max=100"`
    UserID int64  `json:"userId" validate:"required,gt=0"`
}

func handleMessage(conn *websocket.Conn) {
    var msg UpdateNameMsg
    if err := conn.ReadJSON(&msg); err != nil { return }
    if err := validate.Struct(msg); err != nil { return }
    db.Exec("UPDATE users SET name = $1 WHERE id = $2", msg.Name, msg.UserID)
}
```

**Scanner Coverage**: No direct scanner rule. Detected by checking for absence
of validation libraries in WebSocket message handlers.

**False Positive Guidance**: Simple ping/pong or status messages that do not
drive data operations may not need strict validation. Check whether message
content affects database state, authorization, or business logic.

**Severity Assessment**:
- **critical**: No validation on messages driving financial or auth operations
- **high**: No validation on messages that modify database state
- **medium**: Partial validation (type check but no field constraints)
- **low**: Missing validation on read-only notification messages

---

## 4. No Rate Limiting on WebSocket Messages

**Description**: Without rate limiting, a single client can flood the server
with messages, causing denial of service or exhausting resources. Unlike HTTP
where each request is independent, WebSocket connections are persistent and
can send thousands of messages per second without connection overhead.

**Search Heuristics**:
- Grep: `rateLimit|rate.limit|throttle|maxMessages|messageRate`
- Grep: `setInterval|setTimeout` in message handlers (manual rate limiting)
- Grep: `ws\.on\(['"]message|socket\.on\(` without rate limit middleware
- Glob: `**/ws/**`, `**/websocket/**`, `**/middleware/**`

**Language Examples**:

JavaScript -- VULNERABLE:
```javascript
ws.on('message', (data) => {
  processMessage(data);  // No rate limiting -- client can flood
});
```

JavaScript -- FIXED:
```javascript
const messageTimestamps = new Map();

ws.on('message', (data) => {
  const now = Date.now();
  const timestamps = messageTimestamps.get(ws) || [];
  const recent = timestamps.filter(t => now - t < 1000);
  if (recent.length >= 10) {
    ws.send(JSON.stringify({ error: 'Rate limit exceeded' }));
    return;
  }
  recent.push(now);
  messageTimestamps.set(ws, recent);
  processMessage(data);
});
```

Python -- VULNERABLE:
```python
async def handler(websocket):
    async for message in websocket:
        await process(message)  # No rate limit
```

Python -- FIXED:
```python
import time

async def handler(websocket):
    timestamps = []
    async for message in websocket:
        now = time.time()
        timestamps = [t for t in timestamps if now - t < 1.0]
        if len(timestamps) >= 10:
            await websocket.send(json.dumps({"error": "rate limit"}))
            continue
        timestamps.append(now)
        await process(message)
```

Java -- VULNERABLE:
```java
@Override
public void handleTextMessage(WebSocketSession session, TextMessage message) {
    process(message);  // No rate limiting
}
```

Java -- FIXED:
```java
private final Map<String, RateLimiter> limiters = new ConcurrentHashMap<>();

@Override
public void handleTextMessage(WebSocketSession session, TextMessage message) {
    RateLimiter limiter = limiters.computeIfAbsent(session.getId(),
        k -> RateLimiter.create(10.0));  // 10 messages/sec
    if (!limiter.tryAcquire()) {
        session.sendMessage(new TextMessage("{\"error\":\"rate limited\"}"));
        return;
    }
    process(message);
}
```

Go -- VULNERABLE:
```go
for {
    _, msg, err := conn.ReadMessage()
    if err != nil { break }
    handleMessage(msg)  // No rate limit
}
```

Go -- FIXED:
```go
limiter := rate.NewLimiter(rate.Every(100*time.Millisecond), 10)
for {
    _, msg, err := conn.ReadMessage()
    if err != nil { break }
    if !limiter.Allow() {
        conn.WriteJSON(map[string]string{"error": "rate limited"})
        continue
    }
    handleMessage(msg)
}
```

**Scanner Coverage**: No direct scanner rule. Detected through absence of rate
limiting in message handlers.

**False Positive Guidance**: Low-frequency WebSocket connections (periodic
heartbeats, rare notifications) may not need rate limiting. Check message
volume expectations and whether the handler performs expensive operations.

**Severity Assessment**:
- **high**: No rate limit on WebSocket handlers that trigger DB writes or API calls
- **medium**: No rate limit on WebSocket handlers with moderate processing cost
- **low**: No rate limit on lightweight handlers (ping/pong, status)

---

## 5. Unencrypted WebSocket Transport (ws://)

**Description**: Production WebSocket connections use `ws://` instead of
`wss://`, transmitting data in cleartext. Attackers on the network path can
intercept messages, steal authentication tokens, and inject malicious messages.

**Search Heuristics**:
- Grep: `ws://` in client-side or server configuration code (excluding `wss://`)
- Grep: `new WebSocket\(['"]ws://` in client code
- Grep: `WebSocket\.connect\(['"]ws://`
- Grep: `WEBSOCKET_URL.*ws://|WS_URL.*ws://`
- Glob: `**/client/**`, `**/config/**`, `**/env/**`, `**/.env*`

**Language Examples**:

JavaScript (Client) -- VULNERABLE:
```javascript
const ws = new WebSocket('ws://api.example.com/ws');  // Unencrypted
```

JavaScript (Client) -- FIXED:
```javascript
const ws = new WebSocket('wss://api.example.com/ws');  // TLS encrypted
```

Python (Client) -- VULNERABLE:
```python
async with websockets.connect("ws://api.example.com/ws") as ws:
    await ws.send(json.dumps({"token": user_token}))  # Token sent in cleartext
```

Python (Client) -- FIXED:
```python
async with websockets.connect("wss://api.example.com/ws") as ws:
    await ws.send(json.dumps({"token": user_token}))
```

Java -- VULNERABLE:
```java
WebSocketClient client = new StandardWebSocketClient();
client.doHandshake(handler, "ws://api.example.com/ws");
```

Java -- FIXED:
```java
WebSocketClient client = new StandardWebSocketClient();
client.doHandshake(handler, "wss://api.example.com/ws");
```

Go -- VULNERABLE:
```go
conn, _, err := websocket.DefaultDialer.Dial("ws://api.example.com/ws", nil)
```

Go -- FIXED:
```go
conn, _, err := websocket.DefaultDialer.Dial("wss://api.example.com/ws", nil)
```

**Scanner Coverage**: semgrep `generic.websocket.security.unencrypted-websocket`

**False Positive Guidance**: `ws://localhost` and `ws://127.0.0.1` for local
development are expected and not findings. Check whether the URL points to a
production or external host. Environment variable references like
`${WS_URL}` need manual verification.

**Severity Assessment**:
- **high**: ws:// to production hosts transmitting auth tokens or sensitive data
- **medium**: ws:// to production hosts for non-sensitive data
- **low**: ws:// in development configuration (localhost/127.0.0.1)
