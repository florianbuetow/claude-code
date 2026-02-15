# Detection Patterns: Server-Side Request Forgery

Patterns for detecting A10:2021 vulnerabilities. Each pattern includes search
heuristics, language examples, scanner coverage, and false positive guidance.

---

## Pattern 1: URL from User Input Passed to HTTP Client

**Description**: An HTTP request function (fetch, requests.get, http.Get, axios,
HttpClient) is called with a URL that originates entirely or partially from
user-controlled input (query parameters, request body, headers, path segments).
This is the root cause of all SSRF vulnerabilities.

**Search Heuristics**:
```
Grep for HTTP client calls near user input:
  Pattern: (requests\.(get|post|put|delete|head|patch|request)|urllib\.request\.urlopen|http\.client\.HTTPConnection)\(.*req
  Pattern: (fetch|axios|got|node-fetch|undici\.request)\(.*req\.(query|body|params|headers)
  Pattern: (HttpClient|WebClient|RestTemplate)\..*(get|post|put|exchange)\(.*request\.getParameter
  Pattern: http\.(Get|Post|Head|Do)\(.*r\.(URL|Form|Body|Header)
  Pattern: (fetch|axios|got)\(.*(url|uri|href|link|src|target|callback|webhook|redirect)
```

**Language Examples**:

Python -- Vulnerable:
```python
@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    response = requests.get(url)
    return response.content

@app.route('/fetch-avatar')
def fetch_avatar():
    avatar_url = request.json['avatar_url']
    img = urllib.request.urlopen(avatar_url).read()
    return img
```

Python -- Fixed:
```python
@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not is_safe_url(url):
        abort(400, 'URL not allowed')
    response = requests.get(url, allow_redirects=False, timeout=5)
    return response.content

def is_safe_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    try:
        ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
        return not ipaddress.ip_address(ip).is_private
    except (socket.gaierror, ValueError):
        return False
```

JavaScript/TypeScript -- Vulnerable:
```typescript
app.get('/preview', async (req, res) => {
  const { url } = req.query;
  const response = await fetch(url as string);
  const html = await response.text();
  res.send(html);
});

app.post('/webhook', async (req, res) => {
  const { callbackUrl } = req.body;
  await axios.post(callbackUrl, { status: 'complete' });
  res.json({ ok: true });
});
```

JavaScript/TypeScript -- Fixed:
```typescript
import { isAllowedUrl } from './url-validator';

app.get('/preview', async (req, res) => {
  const { url } = req.query;
  if (!isAllowedUrl(url as string)) {
    return res.status(400).json({ error: 'URL not allowed' });
  }
  const response = await fetch(url as string, { redirect: 'error' });
  const html = await response.text();
  res.send(html);
});
```

Java -- Vulnerable:
```java
@GetMapping("/fetch")
public ResponseEntity<byte[]> fetchUrl(@RequestParam String url) throws IOException {
    URL target = new URL(url);
    byte[] content = target.openStream().readAllBytes();
    return ResponseEntity.ok(content);
}
```

Java -- Fixed:
```java
@GetMapping("/fetch")
public ResponseEntity<byte[]> fetchUrl(@RequestParam String url) throws IOException {
    URL target = new URL(url);
    if (!UrlValidator.isSafeUrl(target)) {
        return ResponseEntity.badRequest().build();
    }
    HttpURLConnection conn = (HttpURLConnection) target.openConnection();
    conn.setInstanceFollowRedirects(false);
    conn.setConnectTimeout(5000);
    byte[] content = conn.getInputStream().readAllBytes();
    return ResponseEntity.ok(content);
}
```

Go -- Vulnerable:
```go
func proxyHandler(w http.ResponseWriter, r *http.Request) {
    targetURL := r.URL.Query().Get("url")
    resp, err := http.Get(targetURL)
    if err != nil {
        http.Error(w, err.Error(), http.StatusBadGateway)
        return
    }
    defer resp.Body.Close()
    io.Copy(w, resp.Body)
}
```

Go -- Fixed:
```go
func proxyHandler(w http.ResponseWriter, r *http.Request) {
    targetURL := r.URL.Query().Get("url")
    if !isAllowedURL(targetURL) {
        http.Error(w, "URL not allowed", http.StatusBadRequest)
        return
    }
    client := &http.Client{
        CheckRedirect: func(req *http.Request, via []*http.Request) error {
            return http.ErrUseLastResponse // do not follow redirects
        },
        Timeout: 5 * time.Second,
    }
    resp, err := client.Get(targetURL)
    if err != nil {
        http.Error(w, "Fetch failed", http.StatusBadGateway)
        return
    }
    defer resp.Body.Close()
    io.Copy(w, resp.Body)
}
```

**Scanner Coverage**: semgrep provides good coverage for this pattern through taint
analysis rules. Bandit detects Python requests/urllib with user input. Coverage is
strong for direct flows but weaker for indirect flows through variables or helper
functions.

**False Positive Guidance**: URLs that come from a database, configuration file, or
hardcoded allowlist are not user-controlled. Check the data flow to confirm the URL
actually originates from request input. Also, internal microservice-to-microservice
calls where the URL is constructed from service discovery (not user input) are safe.

**Severity Criteria**:
- **critical**: Unauthenticated endpoint that fetches arbitrary URLs with no validation
- **high**: Authenticated endpoint with user-supplied URL and no validation
- **medium**: URL partially constructed from user input (e.g., path appended to a base URL)
- **low**: URL from user input in an internal-only service not exposed externally

---

## Pattern 2: Missing URL Scheme Whitelist

**Description**: URL validation that does not restrict the scheme (protocol),
allowing dangerous schemes like `file://`, `gopher://`, `dict://`, `ftp://`, or
`data:`. These schemes can read local files, interact with internal services via
non-HTTP protocols, or bypass network-level protections.

**Search Heuristics**:
```
Grep for URL parsing without scheme checks:
  Pattern: (urlparse|URL\(|new URL|url\.Parse)\((?!.*scheme)
  Pattern: (requests\.(get|post)|fetch|http\.(Get|Post)|axios)\(.*(?!https?://)
  Pattern: (startswith|startsWith|HasPrefix)\(.*(http|https)\)  (partial: check if both http AND https are required)

Look for absence of scheme validation near URL usage:
  Negative pattern (should be present): (scheme|protocol)\s*(==|===|!=|!==|in|\.includes|\.contains).*(http|https)
```

**Language Examples**:

Python -- Vulnerable:
```python
def fetch_resource(url):
    parsed = urllib.parse.urlparse(url)
    # Only checks hostname, not scheme
    if parsed.hostname in BLOCKED_HOSTS:
        raise ValueError("Blocked host")
    return requests.get(url)
```

Python -- Fixed:
```python
ALLOWED_SCHEMES = {'http', 'https'}

def fetch_resource(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Scheme '{parsed.scheme}' not allowed")
    if parsed.hostname in BLOCKED_HOSTS:
        raise ValueError("Blocked host")
    return requests.get(url, allow_redirects=False)
```

JavaScript/TypeScript -- Vulnerable:
```typescript
function fetchUrl(url: string): Promise<Response> {
  const parsed = new URL(url);
  if (BLOCKED_HOSTS.includes(parsed.hostname)) {
    throw new Error('Blocked host');
  }
  return fetch(url);  // allows file://, data:, etc.
}
```

JavaScript/TypeScript -- Fixed:
```typescript
const ALLOWED_PROTOCOLS = new Set(['http:', 'https:']);

function fetchUrl(url: string): Promise<Response> {
  const parsed = new URL(url);
  if (!ALLOWED_PROTOCOLS.has(parsed.protocol)) {
    throw new Error(`Protocol '${parsed.protocol}' not allowed`);
  }
  if (BLOCKED_HOSTS.includes(parsed.hostname)) {
    throw new Error('Blocked host');
  }
  return fetch(url, { redirect: 'error' });
}
```

Java -- Vulnerable:
```java
public byte[] fetchContent(String urlString) throws IOException {
    URL url = new URL(urlString);  // accepts any scheme
    return url.openStream().readAllBytes();
}
```

Java -- Fixed:
```java
private static final Set<String> ALLOWED_SCHEMES = Set.of("http", "https");

public byte[] fetchContent(String urlString) throws IOException {
    URL url = new URL(urlString);
    if (!ALLOWED_SCHEMES.contains(url.getProtocol())) {
        throw new SecurityException("Scheme not allowed: " + url.getProtocol());
    }
    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
    conn.setInstanceFollowRedirects(false);
    return conn.getInputStream().readAllBytes();
}
```

Go -- Vulnerable:
```go
func fetchResource(rawURL string) ([]byte, error) {
    u, err := url.Parse(rawURL)
    if err != nil {
        return nil, err
    }
    // Only checks host, not scheme
    if isBlockedHost(u.Host) {
        return nil, fmt.Errorf("blocked host")
    }
    resp, err := http.Get(rawURL)
    // ...
}
```

Go -- Fixed:
```go
var allowedSchemes = map[string]bool{"http": true, "https": true}

func fetchResource(rawURL string) ([]byte, error) {
    u, err := url.Parse(rawURL)
    if err != nil {
        return nil, err
    }
    if !allowedSchemes[u.Scheme] {
        return nil, fmt.Errorf("scheme %q not allowed", u.Scheme)
    }
    if isBlockedHost(u.Host) {
        return nil, fmt.Errorf("blocked host")
    }
    resp, err := http.Get(rawURL)
    // ...
}
```

**Scanner Coverage**: semgrep can detect some missing scheme checks in its SSRF
rules, particularly when taint analysis tracks a URL from input to fetch. Coverage
is moderate. Most scanners flag the fetch call itself rather than the missing
scheme validation specifically.

**False Positive Guidance**: Some HTTP client libraries (e.g., Go's net/http) only
support http/https schemes and will error on file:// or gopher://. Check the
library documentation before flagging. However, lower-level APIs (Python's urllib,
Java's URL.openStream) do support multiple schemes and need explicit validation.

**Severity Criteria**:
- **high**: User-supplied URL with no scheme restriction, using a library that supports file://
- **medium**: URL validation present but scheme check is missing among other checks
- **low**: Library that only supports http/https natively (defense-in-depth concern)

---

## Pattern 3: No Blocking of Internal IP Ranges

**Description**: Outbound HTTP requests to user-supplied URLs without validating
that the resolved IP address is not in a private or reserved range. This allows
attackers to scan internal networks, access internal services, and read cloud
metadata endpoints.

**Search Heuristics**:
```
Grep for URL validation that does NOT include IP checks:
  Pattern: (requests\.(get|post)|fetch|http\.(Get|Post)|axios)\(.*(?!(is_private|isPrivate|isInternal|checkIP|validateIP))
  Pattern: (127\.0\.0\.1|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|169\.254\.|0\.0\.0\.0)

Look for absence of IP validation near URL fetching:
  Negative pattern (should be present): (is_private|isPrivate|private|internal|reserved|loopback|link.local)
  Negative pattern: ipaddress\.(ip_address|IPv4Address|IPv6Address)
  Negative pattern: (InetAddress|NetworkInterface)\..*(isSiteLocal|isLoopback|isLinkLocal)
```

**Language Examples**:

Python -- Vulnerable:
```python
def proxy_request(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Invalid scheme")
    # Scheme validated but no IP check - can access 127.0.0.1, 10.x, 169.254.x
    return requests.get(url)
```

Python -- Fixed:
```python
import ipaddress
import socket

def proxy_request(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Invalid scheme")
    # Resolve hostname to IP and validate
    try:
        ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
        addr = ipaddress.ip_address(ip)
        if addr.is_private or addr.is_reserved or addr.is_loopback or addr.is_link_local:
            raise ValueError(f"Internal IP {ip} not allowed")
    except socket.gaierror:
        raise ValueError("Cannot resolve hostname")
    return requests.get(url, allow_redirects=False, timeout=5)
```

JavaScript/TypeScript -- Vulnerable:
```typescript
app.post('/webhook-test', async (req, res) => {
  const { url } = req.body;
  const parsed = new URL(url);
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return res.status(400).json({ error: 'Invalid protocol' });
  }
  // No IP validation - internal hosts reachable
  const response = await fetch(url);
  res.json({ status: response.status });
});
```

JavaScript/TypeScript -- Fixed:
```typescript
import { lookup } from 'dns/promises';
import { isIP } from 'net';
import ipRangeCheck from 'ip-range-check';

const BLOCKED_RANGES = [
  '127.0.0.0/8', '10.0.0.0/8', '172.16.0.0/12',
  '192.168.0.0/16', '169.254.0.0/16', '0.0.0.0/8', '::1/128', 'fc00::/7'
];

app.post('/webhook-test', async (req, res) => {
  const { url } = req.body;
  const parsed = new URL(url);
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    return res.status(400).json({ error: 'Invalid protocol' });
  }
  const { address } = await lookup(parsed.hostname);
  if (ipRangeCheck(address, BLOCKED_RANGES)) {
    return res.status(400).json({ error: 'Internal addresses not allowed' });
  }
  const response = await fetch(url, { redirect: 'error' });
  res.json({ status: response.status });
});
```

Java -- Vulnerable:
```java
@PostMapping("/check-url")
public ResponseEntity<String> checkUrl(@RequestParam String url) throws Exception {
    URL target = new URL(url);
    // No IP validation
    HttpURLConnection conn = (HttpURLConnection) target.openConnection();
    return ResponseEntity.ok("Status: " + conn.getResponseCode());
}
```

Java -- Fixed:
```java
@PostMapping("/check-url")
public ResponseEntity<String> checkUrl(@RequestParam String url) throws Exception {
    URL target = new URL(url);
    InetAddress addr = InetAddress.getByName(target.getHost());
    if (addr.isSiteLocalAddress() || addr.isLoopbackAddress() ||
        addr.isLinkLocalAddress() || addr.isAnyLocalAddress()) {
        return ResponseEntity.badRequest().body("Internal addresses not allowed");
    }
    HttpURLConnection conn = (HttpURLConnection) target.openConnection();
    conn.setInstanceFollowRedirects(false);
    return ResponseEntity.ok("Status: " + conn.getResponseCode());
}
```

Go -- Vulnerable:
```go
func checkURL(w http.ResponseWriter, r *http.Request) {
    targetURL := r.FormValue("url")
    u, _ := url.Parse(targetURL)
    if u.Scheme != "http" && u.Scheme != "https" {
        http.Error(w, "Invalid scheme", http.StatusBadRequest)
        return
    }
    // No IP check
    resp, _ := http.Get(targetURL)
    fmt.Fprintf(w, "Status: %d", resp.StatusCode)
}
```

Go -- Fixed:
```go
func checkURL(w http.ResponseWriter, r *http.Request) {
    targetURL := r.FormValue("url")
    u, _ := url.Parse(targetURL)
    if u.Scheme != "http" && u.Scheme != "https" {
        http.Error(w, "Invalid scheme", http.StatusBadRequest)
        return
    }
    ips, err := net.LookupIP(u.Hostname())
    if err != nil || len(ips) == 0 {
        http.Error(w, "Cannot resolve host", http.StatusBadRequest)
        return
    }
    for _, ip := range ips {
        if ip.IsLoopback() || ip.IsPrivate() || ip.IsLinkLocalUnicast() || ip.IsLinkLocalMulticast() {
            http.Error(w, "Internal addresses not allowed", http.StatusBadRequest)
            return
        }
    }
    client := &http.Client{CheckRedirect: func(r *http.Request, via []*http.Request) error {
        return http.ErrUseLastResponse
    }}
    resp, _ := client.Get(targetURL)
    fmt.Fprintf(w, "Status: %d", resp.StatusCode)
}
```

**Scanner Coverage**: semgrep SSRF rules check for the overall taint flow from user
input to fetch, but generally do not specifically verify IP range validation.
Coverage is weak for this specific pattern; scanners flag the fetch call but do not
confirm whether IP validation is present.

**False Positive Guidance**: Some infrastructure-level protections (e.g., AWS VPC
configurations, egress firewall rules, or network policies) may block internal
access independently. If documented infrastructure controls exist, reduce severity.
Also, if the service runs outside a cloud environment with no sensitive internal
services, the impact is lower.

**Severity Criteria**:
- **critical**: No IP validation on user-supplied URLs in a cloud-hosted application
- **high**: Partial IP validation (blocks 127.0.0.1 but not 169.254.169.254 or 10.x)
- **medium**: IP validation present but bypassable via IPv6 mapping (::ffff:127.0.0.1)
- **low**: Internal-only service with no external user access

---

## Pattern 4: Redirect Following on User-Supplied URLs

**Description**: HTTP client configured to follow redirects (the default behavior
in most libraries) when fetching user-supplied URLs. Attackers can host a redirect
on an allowed domain that points to an internal IP or cloud metadata endpoint,
bypassing URL validation that only checks the initial URL.

**Search Heuristics**:
```
Grep for HTTP client usage without redirect disabling:
  Pattern: requests\.(get|post|put|delete)\((?!.*allow_redirects\s*=\s*False)
  Pattern: fetch\((?!.*redirect.*manual|.*redirect.*error)
  Pattern: axios\.(get|post)\((?!.*maxRedirects.*0)
  Pattern: http\.Client\{(?!.*CheckRedirect)
  Pattern: HttpURLConnection(?!.*setInstanceFollowRedirects\(false\))

Look for explicit redirect disabling (positive signal):
  Pattern: allow_redirects\s*=\s*False
  Pattern: redirect:\s*['"]?(manual|error)['"]?
  Pattern: maxRedirects:\s*0
  Pattern: setInstanceFollowRedirects\(false\)
  Pattern: CheckRedirect.*ErrUseLastResponse
```

**Language Examples**:

Python -- Vulnerable:
```python
def fetch_url(url):
    validate_url(url)  # validates initial URL only
    return requests.get(url)  # follows redirects by default
```

Python -- Fixed:
```python
def fetch_url(url):
    validate_url(url)
    response = requests.get(url, allow_redirects=False, timeout=5)
    if response.is_redirect:
        redirect_url = response.headers.get('Location')
        validate_url(redirect_url)  # validate each redirect target
        return requests.get(redirect_url, allow_redirects=False, timeout=5)
    return response
```

JavaScript/TypeScript -- Vulnerable:
```typescript
async function fetchPreview(url: string): Promise<string> {
  validateUrl(url);
  const response = await fetch(url);  // follows redirects by default
  return response.text();
}
```

JavaScript/TypeScript -- Fixed:
```typescript
async function fetchPreview(url: string): Promise<string> {
  validateUrl(url);
  const response = await fetch(url, { redirect: 'manual' });
  if (response.status >= 300 && response.status < 400) {
    const redirectUrl = response.headers.get('location');
    if (redirectUrl) {
      validateUrl(redirectUrl);  // validate redirect target
      const finalResponse = await fetch(redirectUrl, { redirect: 'error' });
      return finalResponse.text();
    }
  }
  return response.text();
}
```

Java -- Vulnerable:
```java
public String fetchContent(String url) throws IOException {
    validateUrl(url);
    URL target = new URL(url);
    HttpURLConnection conn = (HttpURLConnection) target.openConnection();
    // follows redirects by default (HttpURLConnection.setFollowRedirects(true))
    return new String(conn.getInputStream().readAllBytes());
}
```

Java -- Fixed:
```java
public String fetchContent(String url) throws IOException {
    validateUrl(url);
    URL target = new URL(url);
    HttpURLConnection conn = (HttpURLConnection) target.openConnection();
    conn.setInstanceFollowRedirects(false);
    if (conn.getResponseCode() >= 300 && conn.getResponseCode() < 400) {
        String redirectUrl = conn.getHeaderField("Location");
        validateUrl(redirectUrl);  // validate redirect target
        URL redirectTarget = new URL(redirectUrl);
        HttpURLConnection redirectConn = (HttpURLConnection) redirectTarget.openConnection();
        redirectConn.setInstanceFollowRedirects(false);
        return new String(redirectConn.getInputStream().readAllBytes());
    }
    return new String(conn.getInputStream().readAllBytes());
}
```

Go -- Vulnerable:
```go
func fetchURL(targetURL string) ([]byte, error) {
    if err := validateURL(targetURL); err != nil {
        return nil, err
    }
    resp, err := http.Get(targetURL)  // default client follows redirects
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}
```

Go -- Fixed:
```go
func fetchURL(targetURL string) ([]byte, error) {
    if err := validateURL(targetURL); err != nil {
        return nil, err
    }
    client := &http.Client{
        CheckRedirect: func(req *http.Request, via []*http.Request) error {
            // Validate each redirect target
            if err := validateURL(req.URL.String()); err != nil {
                return err
            }
            if len(via) >= 3 {
                return fmt.Errorf("too many redirects")
            }
            return nil
        },
        Timeout: 5 * time.Second,
    }
    resp, err := client.Get(targetURL)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    return io.ReadAll(resp.Body)
}
```

**Scanner Coverage**: semgrep has some rules that check for redirect following in
SSRF contexts, but coverage is limited. Most scanners flag the SSRF taint flow
rather than specifically checking the redirect configuration.

**False Positive Guidance**: If the URL validation function is applied inside a
custom redirect handler (e.g., Go's CheckRedirect, or a requests Session with a
redirect hook), then redirect following may be safe. Check for validation at each
redirect hop. Also, if the application only fetches from a strict allowlist of
domains, redirect-based bypass is less likely (though still possible if an allowed
domain has an open redirect).

**Severity Criteria**:
- **high**: User-supplied URL fetched with default redirect following, URL validation only on initial URL
- **medium**: Redirects followed with a limit (e.g., max 3) but no validation of targets
- **low**: Redirects followed but strong URL validation applied via CheckRedirect handler

---

## Pattern 5: DNS Rebinding Vulnerability

**Description**: The application validates a URL by resolving the hostname and
checking the IP, then makes a separate HTTP request that resolves the hostname
again. An attacker can configure a DNS record with a short TTL that returns a safe
IP during validation but resolves to an internal IP (e.g., 127.0.0.1) during the
actual request. This is a TOCTOU (time-of-check-time-of-use) vulnerability.

**Search Heuristics**:
```
Grep for DNS resolution followed by separate HTTP call:
  Pattern: (gethostbyname|getaddrinfo|resolve|lookup|InetAddress\.getByName|net\.LookupIP).*\n.*\n.*(requests\.|fetch|http\.|axios)
  Pattern: socket\.getaddrinfo.*\n.*requests\.(get|post)
  Pattern: dns\.lookup.*\n.*fetch\(
  Pattern: InetAddress\.getByName.*\n.*openConnection
  Pattern: net\.LookupIP.*\n.*http\.(Get|Post)
```

**Language Examples**:

Python -- Vulnerable:
```python
def safe_fetch(url):
    parsed = urllib.parse.urlparse(url)
    # Resolve and check IP
    ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    if ipaddress.ip_address(ip).is_private:
        raise ValueError("Private IP not allowed")
    # Second resolution happens inside requests.get - may get different IP
    return requests.get(url)
```

Python -- Fixed:
```python
def safe_fetch(url):
    parsed = urllib.parse.urlparse(url)
    # Resolve once and connect to that specific IP
    ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    if ipaddress.ip_address(ip).is_private:
        raise ValueError("Private IP not allowed")
    # Connect directly to the resolved IP, passing Host header
    resolved_url = urllib.parse.urlunparse(
        parsed._replace(netloc=f"{ip}:{parsed.port or 443}")
    )
    return requests.get(resolved_url, headers={'Host': parsed.hostname},
                        verify=True, allow_redirects=False, timeout=5)
```

JavaScript/TypeScript -- Vulnerable:
```typescript
async function safeFetch(url: string): Promise<Response> {
  const parsed = new URL(url);
  const { address } = await dns.lookup(parsed.hostname);
  if (isPrivateIP(address)) {
    throw new Error('Private IP not allowed');
  }
  // fetch() resolves DNS again independently
  return fetch(url);
}
```

JavaScript/TypeScript -- Fixed:
```typescript
import { Agent } from 'undici';

async function safeFetch(url: string): Promise<Response> {
  const parsed = new URL(url);
  const { address } = await dns.lookup(parsed.hostname);
  if (isPrivateIP(address)) {
    throw new Error('Private IP not allowed');
  }
  // Pin DNS resolution by connecting to the resolved IP
  const agent = new Agent({
    connect: { hostname: address, servername: parsed.hostname }
  });
  return fetch(url, { dispatcher: agent, redirect: 'error' });
}
```

Java -- Vulnerable:
```java
public byte[] safeFetch(String urlString) throws Exception {
    URL url = new URL(urlString);
    InetAddress addr = InetAddress.getByName(url.getHost());
    if (addr.isSiteLocalAddress() || addr.isLoopbackAddress()) {
        throw new SecurityException("Private IP not allowed");
    }
    // openConnection resolves DNS again
    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
    return conn.getInputStream().readAllBytes();
}
```

Java -- Fixed:
```java
public byte[] safeFetch(String urlString) throws Exception {
    URL url = new URL(urlString);
    InetAddress addr = InetAddress.getByName(url.getHost());
    if (addr.isSiteLocalAddress() || addr.isLoopbackAddress()) {
        throw new SecurityException("Private IP not allowed");
    }
    // Connect to resolved IP directly
    URL resolvedUrl = new URL(url.getProtocol(), addr.getHostAddress(), url.getPort(), url.getFile());
    HttpURLConnection conn = (HttpURLConnection) resolvedUrl.openConnection();
    conn.setRequestProperty("Host", url.getHost());
    conn.setInstanceFollowRedirects(false);
    return conn.getInputStream().readAllBytes();
}
```

Go -- Vulnerable:
```go
func safeFetch(rawURL string) ([]byte, error) {
    u, _ := url.Parse(rawURL)
    ips, _ := net.LookupIP(u.Hostname())
    for _, ip := range ips {
        if ip.IsPrivate() || ip.IsLoopback() {
            return nil, fmt.Errorf("private IP not allowed")
        }
    }
    // http.Get resolves DNS again
    resp, err := http.Get(rawURL)
    // ...
}
```

Go -- Fixed:
```go
func safeFetch(rawURL string) ([]byte, error) {
    u, _ := url.Parse(rawURL)
    ips, _ := net.LookupIP(u.Hostname())
    for _, ip := range ips {
        if ip.IsPrivate() || ip.IsLoopback() {
            return nil, fmt.Errorf("private IP not allowed")
        }
    }
    // Pin DNS resolution using a custom dialer
    dialer := &net.Dialer{}
    transport := &http.Transport{
        DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
            _, port, _ := net.SplitHostPort(addr)
            return dialer.DialContext(ctx, network, net.JoinHostPort(ips[0].String(), port))
        },
    }
    client := &http.Client{Transport: transport, Timeout: 5 * time.Second}
    resp, err := client.Get(rawURL)
    // ...
}
```

**Scanner Coverage**: No scanner reliably detects DNS rebinding vulnerabilities.
This requires understanding the temporal relationship between DNS resolution and
HTTP request, which is beyond current static analysis capabilities.

**False Positive Guidance**: If the application uses a DNS cache with a minimum TTL
floor (e.g., Java's default 30-second positive cache), DNS rebinding is harder but
not impossible. Also, if requests go through a corporate proxy or egress gateway
that validates IPs independently, the risk is mitigated at the infrastructure level.
Some HTTP clients cache DNS internally, which also reduces (but does not eliminate)
the risk.

**Severity Criteria**:
- **high**: Separate DNS resolution and HTTP request in cloud-hosted application with no DNS pinning
- **medium**: DNS rebinding possible but application has partial mitigations (DNS cache, short timeout)
- **low**: Application runs in an environment with infrastructure-level SSRF protections

---

## Pattern 6: Cloud Metadata Endpoint Accessible via SSRF

**Description**: No specific blocking of cloud provider metadata endpoints
(169.254.169.254 for AWS/Azure/GCP, metadata.google.internal, 169.254.170.2 for
ECS task metadata). These endpoints expose instance credentials, configuration,
user data scripts, and other sensitive information. SSRF to a metadata endpoint
is the most impactful SSRF variant in cloud environments.

**Search Heuristics**:
```
Grep for metadata endpoint references (positive: blocking is implemented):
  Pattern: 169\.254\.169\.254
  Pattern: metadata\.google\.internal
  Pattern: 169\.254\.170\.2
  Pattern: metadata\.azure\.com
  Pattern: (IMDS|imds|metadata.endpoint|instance.metadata)

Grep for user-supplied URL fetch WITHOUT metadata blocking (negative: should be present):
  Absence of 169.254.169.254 blocking near URL fetch functions.
```

**Language Examples**:

Python -- Vulnerable:
```python
def fetch_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Invalid scheme")
    ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    if ipaddress.ip_address(ip).is_loopback:
        raise ValueError("Loopback not allowed")
    # Missing: no check for 169.254.169.254 (link-local metadata)
    return requests.get(url)
```

Python -- Fixed:
```python
METADATA_IPS = {
    ipaddress.ip_address('169.254.169.254'),
    ipaddress.ip_address('169.254.170.2'),
}
METADATA_HOSTS = {'metadata.google.internal', 'metadata.azure.com'}

def fetch_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError("Invalid scheme")
    if parsed.hostname in METADATA_HOSTS:
        raise ValueError("Metadata endpoint not allowed")
    ip = socket.getaddrinfo(parsed.hostname, None)[0][4][0]
    addr = ipaddress.ip_address(ip)
    if addr.is_loopback or addr.is_private or addr.is_link_local or addr in METADATA_IPS:
        raise ValueError("Blocked IP")
    return requests.get(url, allow_redirects=False, timeout=5)
```

JavaScript/TypeScript -- Vulnerable:
```typescript
function isBlockedIP(ip: string): boolean {
  return ip.startsWith('127.') || ip.startsWith('10.') || ip.startsWith('192.168.');
  // Missing: 169.254.x.x (link-local, includes cloud metadata)
}
```

JavaScript/TypeScript -- Fixed:
```typescript
const BLOCKED_RANGES = [
  '127.0.0.0/8', '10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16',
  '169.254.0.0/16',  // link-local: covers 169.254.169.254 (metadata) and 169.254.170.2 (ECS)
  '0.0.0.0/8', '::1/128', 'fc00::/7'
];
const BLOCKED_HOSTS = ['metadata.google.internal', 'metadata.azure.com'];

function isBlockedTarget(hostname: string, ip: string): boolean {
  if (BLOCKED_HOSTS.includes(hostname)) return true;
  return ipRangeCheck(ip, BLOCKED_RANGES);
}
```

Java -- Vulnerable:
```java
private boolean isInternalIP(InetAddress addr) {
    return addr.isLoopbackAddress() || addr.isSiteLocalAddress();
    // Missing: isLinkLocalAddress() which covers 169.254.x.x
}
```

Java -- Fixed:
```java
private static final Set<String> METADATA_HOSTS = Set.of(
    "metadata.google.internal", "metadata.azure.com"
);

private boolean isBlockedTarget(String hostname, InetAddress addr) {
    if (METADATA_HOSTS.contains(hostname)) return true;
    return addr.isLoopbackAddress() || addr.isSiteLocalAddress() ||
           addr.isLinkLocalAddress() || addr.isAnyLocalAddress();
    // isLinkLocalAddress() covers 169.254.0.0/16 including metadata endpoints
}
```

Go -- Vulnerable:
```go
func isBlocked(ip net.IP) bool {
    return ip.IsLoopback() || ip.IsPrivate()
    // Missing: IsLinkLocalUnicast() which covers 169.254.x.x
}
```

Go -- Fixed:
```go
var metadataHosts = map[string]bool{
    "metadata.google.internal": true,
    "metadata.azure.com":      true,
}

func isBlocked(hostname string, ip net.IP) bool {
    if metadataHosts[hostname] {
        return true
    }
    return ip.IsLoopback() || ip.IsPrivate() ||
        ip.IsLinkLocalUnicast() || ip.IsLinkLocalMulticast() ||
        ip.IsUnspecified()
    // IsLinkLocalUnicast() covers 169.254.0.0/16
}
```

**Scanner Coverage**: semgrep has specific rules for detecting access to metadata
endpoints in some languages. Coverage is moderate for cases where 169.254.169.254
appears in code but weak for detecting the absence of metadata blocking in URL
validation logic.

**False Positive Guidance**: Applications that enforce IMDSv2 on AWS (requiring a
PUT request with a token before metadata access) have some protection, but SSRF can
still obtain the token if the attacker can control both the PUT and GET requests.
Check for infrastructure-level IMDSv2 enforcement (instance metadata options) as a
mitigating factor. Also, applications not running in cloud environments (on-premise
or local development) are not vulnerable to cloud metadata SSRF.

**Severity Criteria**:
- **critical**: No metadata IP blocking in a cloud-hosted application with SSRF vectors
- **high**: Partial blocking (covers 127.0.0.1, 10.x, 192.168.x but not 169.254.x.x)
- **medium**: Metadata blocking present but bypassable via DNS rebinding or redirects
- **low**: Application not deployed in cloud infrastructure
