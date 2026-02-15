# Cryptographic Failures Detection Patterns

Patterns for detecting cryptographic vulnerabilities (OWASP A02:2021).

---

## 1. Weak Hash Algorithms for Security Purposes

**Description**: MD5 or SHA1 used for password hashing, token generation,
integrity verification, or digital signatures. These algorithms have known
collision and preimage attacks and must not be used for security-critical
operations.

**Search Heuristics**:
- Grep: `md5\(|MD5\.|hashlib\.md5|MessageDigest\.getInstance\(["']MD5`
- Grep: `sha1\(|SHA1\.|hashlib\.sha1|MessageDigest\.getInstance\(["']SHA-1`
- Grep: `createHash\(['"]md5|createHash\(['"]sha1`
- Grep: `md5\.New\(\)|sha1\.New\(\)`
- Glob: `**/auth/**`, `**/crypto/**`, `**/utils/**`, `**/security/**`

**Language Examples**:

Python — VULNERABLE:
```python
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def verify_token(token, expected_hash):
    return hashlib.sha1(token.encode()).hexdigest() == expected_hash
```

Python — FIXED:
```python
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))

def verify_token(token, expected_hash):
    import hmac
    import hashlib
    computed = hmac.new(SECRET_KEY, token.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, expected_hash)
```

JavaScript — VULNERABLE:
```javascript
const crypto = require('crypto');

function hashPassword(password) {
  return crypto.createHash('md5').update(password).digest('hex');
}
```

JavaScript — FIXED:
```javascript
const bcrypt = require('bcrypt');

async function hashPassword(password) {
  return bcrypt.hash(password, 12);
}
```

Java — VULNERABLE:
```java
MessageDigest md = MessageDigest.getInstance("MD5");
byte[] hash = md.digest(password.getBytes(StandardCharsets.UTF_8));
String hashedPassword = Base64.getEncoder().encodeToString(hash);
```

Java — FIXED:
```java
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);
String hashedPassword = encoder.encode(password);
```

Go — VULNERABLE:
```go
import "crypto/md5"

func hashPassword(password string) string {
    h := md5.New()
    h.Write([]byte(password))
    return fmt.Sprintf("%x", h.Sum(nil))
}
```

Go — FIXED:
```go
import "golang.org/x/crypto/bcrypt"

func hashPassword(password string) (string, error) {
    bytes, err := bcrypt.GenerateFromPassword([]byte(password), 12)
    return string(bytes), err
}
```

**Scanner Coverage**: semgrep `python.cryptography.security.insecure-hash-algorithms`,
bandit `B303` (md5), `B304` (sha1), gosec `G401` (md5), `G505` (sha1)

**False Positive Guidance**: MD5 and SHA1 are acceptable for non-security uses
such as checksums for file deduplication, cache keys, ETags, or content-addressable
storage. Only flag when used in a security context: password hashing, token
generation, HMAC, or digital signatures. Check variable names and surrounding
context for clues (`password`, `token`, `secret`, `verify`, `auth`).

**Severity Assessment**:
- **high**: MD5/SHA1 for password hashing or authentication token generation
- **medium**: MD5/SHA1 for integrity verification where collision resistance matters
- **low**: SHA-256 used for password hashing directly (not broken, but bcrypt/argon2 preferred)

---

## 2. Hardcoded Encryption Keys and IVs

**Description**: Encryption keys, initialization vectors, or secret keys
embedded directly in source code. Anyone with access to the code (version
control, decompiled binaries, leaked repos) gains the ability to decrypt
all data.

**Search Heuristics**:
- Grep: `(secret_key|SECRET_KEY|encryption_key|ENCRYPTION_KEY)\s*=\s*['"][^'"]+['"]`
- Grep: `(AES|DES|Blowfish)\.(new|encrypt)\(.*['"][a-zA-Z0-9+/=]{16,}['"]`
- Grep: `iv\s*=\s*b?['"][^'"]{16,}['"]`
- Grep: `PRIVATE.KEY|BEGIN RSA|BEGIN EC` in non-test source files
- Glob: `**/*.py`, `**/*.js`, `**/*.ts`, `**/*.java`, `**/*.go` (excluding test dirs)

**Language Examples**:

Python — VULNERABLE:
```python
from Crypto.Cipher import AES

SECRET_KEY = b'my-super-secret-key-1234567890!!'
IV = b'0123456789abcdef'

def encrypt(plaintext):
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(plaintext, AES.block_size))
```

Python — FIXED:
```python
import os
from Crypto.Cipher import AES

SECRET_KEY = os.environ['ENCRYPTION_KEY'].encode()

def encrypt(plaintext):
    iv = os.urandom(16)
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    return iv + ciphertext  # prepend IV for decryption
```

JavaScript — VULNERABLE:
```javascript
const crypto = require('crypto');

const KEY = 'hardcoded-secret-key-12345678';
const IV = Buffer.from('abcdef0123456789', 'utf8');

function encrypt(text) {
  const cipher = crypto.createCipheriv('aes-256-cbc', KEY, IV);
  return cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
}
```

JavaScript — FIXED:
```javascript
const crypto = require('crypto');

const KEY = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');

function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', KEY, iv);
  const encrypted = cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}
```

Java — VULNERABLE:
```java
private static final String KEY = "MyHardcodedKey12";
private static final byte[] IV = "0123456789abcdef".getBytes();

public static byte[] encrypt(byte[] data) throws Exception {
    SecretKeySpec keySpec = new SecretKeySpec(KEY.getBytes(), "AES");
    IvParameterSpec ivSpec = new IvParameterSpec(IV);
    Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    cipher.init(Cipher.ENCRYPT_MODE, keySpec, ivSpec);
    return cipher.doFinal(data);
}
```

Java — FIXED:
```java
public static byte[] encrypt(byte[] data, SecretKey key) throws Exception {
    byte[] iv = new byte[16];
    SecureRandom.getInstanceStrong().nextBytes(iv);
    IvParameterSpec ivSpec = new IvParameterSpec(iv);
    Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    cipher.init(Cipher.ENCRYPT_MODE, key, ivSpec);
    byte[] ciphertext = cipher.doFinal(data);
    return ByteBuffer.allocate(iv.length + ciphertext.length).put(iv).put(ciphertext).array();
}
```

Go — VULNERABLE:
```go
var encryptionKey = []byte("hardcoded-key-for-aes-256-12345!")

func encrypt(plaintext []byte) ([]byte, error) {
    block, _ := aes.NewCipher(encryptionKey)
    iv := []byte("static-iv-12345!")
    stream := cipher.NewCFBEncrypter(block, iv)
    ciphertext := make([]byte, len(plaintext))
    stream.XORKeyStream(ciphertext, plaintext)
    return ciphertext, nil
}
```

Go — FIXED:
```go
func encrypt(plaintext []byte, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    iv := make([]byte, aes.BlockSize)
    if _, err := io.ReadFull(rand.Reader, iv); err != nil {
        return nil, err
    }
    stream := cipher.NewCFBEncrypter(block, iv)
    ciphertext := make([]byte, len(plaintext))
    stream.XORKeyStream(ciphertext, plaintext)
    return append(iv, ciphertext...), nil
}
```

**Scanner Coverage**: semgrep `generic.secrets.security.detected-generic-secret`,
bandit `B105` (hardcoded password), gitleaks (broad key detection),
trufflehog (credential detection with verification)

**False Positive Guidance**: Test files often contain hardcoded keys for unit
testing — these are acceptable if they never appear in production code paths.
Example/documentation keys (clearly labeled as such) are not vulnerabilities.
Default configuration files that are overridden by environment variables at
deployment may contain placeholder keys. Check the file path and context.

**Severity Assessment**:
- **critical**: Production encryption key hardcoded in source committed to VCS
- **high**: Private keys or API secrets in source code
- **medium**: Hardcoded IV/nonce (key from environment but IV static)
- **low**: Hardcoded key in test/example code not reachable in production

---

## 3. Insecure Random Number Generation

**Description**: Using non-cryptographic random number generators for
security-sensitive operations such as generating tokens, session IDs,
passwords, nonces, or encryption keys.

**Search Heuristics**:
- Grep: `Math\.random\(\)` in security contexts
- Grep: `random\.random\(\)|random\.randint\(|random\.choice\(` (Python `random` module)
- Grep: `java\.util\.Random` (not `SecureRandom`)
- Grep: `rand\.Intn\(|rand\.Int\(\)` (Go `math/rand`, not `crypto/rand`)
- Glob: `**/auth/**`, `**/token*`, `**/session*`, `**/crypto/**`

**Language Examples**:

Python — VULNERABLE:
```python
import random
import string

def generate_reset_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
```

Python — FIXED:
```python
import secrets

def generate_reset_token():
    return secrets.token_urlsafe(32)
```

JavaScript — VULNERABLE:
```javascript
function generateToken() {
  return Math.random().toString(36).substring(2) +
         Math.random().toString(36).substring(2);
}

function generateOTP() {
  return Math.floor(Math.random() * 900000 + 100000).toString();
}
```

JavaScript — FIXED:
```javascript
const crypto = require('crypto');

function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

function generateOTP() {
  return crypto.randomInt(100000, 999999).toString();
}
```

Java — VULNERABLE:
```java
import java.util.Random;

public String generateSessionId() {
    Random random = new Random();
    byte[] bytes = new byte[32];
    random.nextBytes(bytes);
    return Base64.getEncoder().encodeToString(bytes);
}
```

Java — FIXED:
```java
import java.security.SecureRandom;

public String generateSessionId() {
    SecureRandom random = SecureRandom.getInstanceStrong();
    byte[] bytes = new byte[32];
    random.nextBytes(bytes);
    return Base64.getEncoder().encodeToString(bytes);
}
```

Go — VULNERABLE:
```go
import "math/rand"

func generateToken() string {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    token := make([]byte, 32)
    for i := range token {
        token[i] = chars[rand.Intn(len(chars))]
    }
    return string(token)
}
```

Go — FIXED:
```go
import "crypto/rand"

func generateToken() (string, error) {
    bytes := make([]byte, 32)
    if _, err := rand.Read(bytes); err != nil {
        return "", err
    }
    return base64.URLEncoding.EncodeToString(bytes), nil
}
```

**Scanner Coverage**: semgrep `javascript.math-random.security.insecure-random`,
bandit `B311` (random), gosec `G404` (math/rand)

**False Positive Guidance**: Non-cryptographic RNGs are fine for non-security
uses: shuffling UI elements, generating test data, sampling for analytics,
load balancing jitter, or game mechanics. Only flag when the random value is used
for authentication, authorization, cryptographic operations, or anything an
attacker could benefit from predicting. Check variable names and usage context
(`token`, `secret`, `session`, `nonce`, `key`, `otp`, `reset`, `password`).

**Severity Assessment**:
- **high**: `Math.random()` or equivalent for session tokens, password reset tokens, or OTPs
- **medium**: Weak RNG for CSRF tokens or API keys
- **low**: Weak RNG for non-critical randomness that has some security relevance

---

## 4. Password Storage Without Proper Hashing

**Description**: Passwords stored in plaintext, with reversible encryption,
or with fast hash functions (MD5, SHA-family) instead of purpose-built
password hashing functions (bcrypt, argon2, scrypt) that incorporate salting
and work factors.

**Search Heuristics**:
- Grep: `password\s*=.*encrypt\(|password\s*=.*encode\(` (reversible storage)
- Grep: `hashlib\.(md5|sha1|sha256)\(.*password` or `createHash.*password`
- Grep: `SET password\s*=` in SQL without hashing function
- Grep: `bcrypt|argon2|scrypt|pbkdf2` (presence indicates correct approach)
- Glob: `**/auth/**`, `**/models/user*`, `**/registration*`, `**/signup*`

**Language Examples**:

Python (Django) — VULNERABLE:
```python
class User(models.Model):
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        import hashlib
        self.password = hashlib.sha256(raw_password.encode()).hexdigest()
```

Python (Django) — FIXED:
```python
from django.contrib.auth.hashers import make_password, check_password

class User(models.Model):
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # uses PBKDF2 by default

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
```

JavaScript — VULNERABLE:
```javascript
const crypto = require('crypto');

async function registerUser(email, password) {
  const hashedPassword = crypto.createHash('sha256').update(password).digest('hex');
  await db.query('INSERT INTO users (email, password) VALUES (?, ?)', [email, hashedPassword]);
}
```

JavaScript — FIXED:
```javascript
const bcrypt = require('bcrypt');

async function registerUser(email, password) {
  const hashedPassword = await bcrypt.hash(password, 12);
  await db.query('INSERT INTO users (email, password) VALUES (?, ?)', [email, hashedPassword]);
}
```

Java — VULNERABLE:
```java
public void saveUser(String username, String password) {
    String hash = DigestUtils.sha256Hex(password);
    userRepository.save(new User(username, hash));
}
```

Java — FIXED:
```java
import org.springframework.security.crypto.argon2.Argon2PasswordEncoder;

private final Argon2PasswordEncoder encoder = Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8();

public void saveUser(String username, String password) {
    String hash = encoder.encode(password);
    userRepository.save(new User(username, hash));
}
```

Go — VULNERABLE:
```go
func registerUser(username, password string) error {
    h := sha256.New()
    h.Write([]byte(password))
    hash := fmt.Sprintf("%x", h.Sum(nil))
    _, err := db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", username, hash)
    return err
}
```

Go — FIXED:
```go
import "golang.org/x/crypto/bcrypt"

func registerUser(username, password string) error {
    hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
    if err != nil {
        return err
    }
    _, err = db.Exec("INSERT INTO users (username, password) VALUES (?, ?)", username, string(hash))
    return err
}
```

**Scanner Coverage**: semgrep `python.cryptography.security.insecure-hash-algorithms-md5`,
bandit `B303`, `B304`

**False Positive Guidance**: Not all hashing of password-like values is password
storage. Hashing a password to use as a cache key, or hashing for comparison in
a migration script, is not the same as storing credentials. Look for database
write operations and user registration/update flows to confirm this is actual
password storage.

**Severity Assessment**:
- **critical**: Plaintext password storage (no hashing at all)
- **high**: MD5 or SHA-family for password storage
- **medium**: bcrypt/argon2/scrypt with low work factor (e.g., bcrypt cost < 10)
- **low**: Using PBKDF2 with SHA-256 (acceptable but argon2 preferred for new systems)

---

## 5. ECB Mode Usage

**Description**: Using Electronic Codebook (ECB) mode for block cipher
encryption. ECB encrypts identical plaintext blocks to identical ciphertext
blocks, revealing patterns in the data. This is famously demonstrated by the
ECB penguin image.

**Search Heuristics**:
- Grep: `MODE_ECB|AES/ECB|DES/ECB|ECB_MODE`
- Grep: `Cipher\.getInstance\(["']AES["']\)` (Java defaults to ECB when no mode specified)
- Grep: `createCipheriv\(.*ecb|createCipher\(` (`createCipher` uses ECB by default)
- Grep: `aes\.NewCipher\(` without subsequent `cipher.NewCBC` or other mode
- Glob: `**/crypto/**`, `**/encryption/**`, `**/utils/**`

**Language Examples**:

Python — VULNERABLE:
```python
from Crypto.Cipher import AES

def encrypt(key, plaintext):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(plaintext, AES.block_size))
```

Python — FIXED:
```python
import os
from Crypto.Cipher import AES

def encrypt(key, plaintext):
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(pad(plaintext, AES.block_size))
    return iv + tag + ciphertext
```

JavaScript — VULNERABLE:
```javascript
const crypto = require('crypto');

function encrypt(key, text) {
  const cipher = crypto.createCipheriv('aes-256-ecb', key, null);
  return cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
}
```

JavaScript — FIXED:
```javascript
const crypto = require('crypto');

function encrypt(key, text) {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
  const encrypted = cipher.update(text, 'utf8', 'hex') + cipher.final('hex');
  const tag = cipher.getAuthTag();
  return iv.toString('hex') + ':' + tag.toString('hex') + ':' + encrypted;
}
```

Java — VULNERABLE:
```java
// Java defaults to ECB when no mode is specified
Cipher cipher = Cipher.getInstance("AES");
cipher.init(Cipher.ENCRYPT_MODE, keySpec);
byte[] encrypted = cipher.doFinal(data);
```

Java — FIXED:
```java
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
byte[] iv = new byte[12];
SecureRandom.getInstanceStrong().nextBytes(iv);
GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
byte[] encrypted = cipher.doFinal(data);
```

Go — VULNERABLE:
```go
block, _ := aes.NewCipher(key)
// Using block cipher directly = ECB mode
dst := make([]byte, aes.BlockSize)
block.Encrypt(dst, src)
```

Go — FIXED:
```go
block, _ := aes.NewCipher(key)
nonce := make([]byte, 12)
io.ReadFull(rand.Reader, nonce)
aesgcm, _ := cipher.NewGCM(block)
ciphertext := aesgcm.Seal(nonce, nonce, plaintext, nil)
```

**Scanner Coverage**: semgrep `python.cryptography.security.insecure-cipher-mode-ecb`,
bandit `B413` (pycrypto ECB), gosec `G405` (DES/ECB)

**False Positive Guidance**: ECB mode is acceptable for encrypting a single
block (exactly 16 bytes for AES) in specific protocols such as key wrapping or
SIV construction. Also acceptable in test code. Flag only when ECB is used for
general-purpose encryption of multi-block data.

**Severity Assessment**:
- **high**: ECB mode encrypting sensitive multi-block data (PII, credentials, messages)
- **medium**: ECB mode on less sensitive data or limited block counts
- **low**: ECB used in a context where single-block encryption is intentional

---

## 6. Missing TLS Enforcement

**Description**: The application communicates over unencrypted channels (HTTP),
disables certificate validation, or allows outdated TLS versions (1.0, 1.1),
exposing data in transit to interception and tampering.

**Search Heuristics**:
- Grep: `http://` in API endpoint URLs (not localhost/127.0.0.1)
- Grep: `verify\s*=\s*False` or `rejectUnauthorized.*false` or `InsecureSkipVerify.*true`
- Grep: `TLSv1[^.]|SSLv3|TLS_1_0|TLS_1_1|MinVersion.*tls\.VersionTLS10`
- Grep: `CURLOPT_SSL_VERIFYPEER.*false|CURLOPT_SSL_VERIFYHOST.*0`
- Glob: `**/config/**`, `**/*.env*`, `**/http*`, `**/client*`

**Language Examples**:

Python — VULNERABLE:
```python
import requests

response = requests.get('https://api.example.com/data', verify=False)

# or using HTTP for sensitive API
response = requests.post('http://api.example.com/login', json=credentials)
```

Python — FIXED:
```python
import requests

response = requests.get('https://api.example.com/data', verify=True)  # default

# or with custom CA bundle
response = requests.get('https://api.example.com/data', verify='/path/to/ca-bundle.crt')
```

JavaScript — VULNERABLE:
```javascript
const https = require('https');

const agent = new https.Agent({ rejectUnauthorized: false });
const response = await fetch('https://api.example.com/data', { agent });

// or disabling globally
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
```

JavaScript — FIXED:
```javascript
const response = await fetch('https://api.example.com/data');

// With custom CA:
const https = require('https');
const agent = new https.Agent({ ca: fs.readFileSync('/path/to/ca.pem') });
const response = await fetch('https://api.example.com/data', { agent });
```

Java — VULNERABLE:
```java
// Accepting all certificates
TrustManager[] trustAll = new TrustManager[] {
    new X509TrustManager() {
        public X509Certificate[] getAcceptedIssuers() { return null; }
        public void checkClientTrusted(X509Certificate[] certs, String type) {}
        public void checkServerTrusted(X509Certificate[] certs, String type) {}
    }
};
SSLContext sc = SSLContext.getInstance("TLS");
sc.init(null, trustAll, new SecureRandom());
```

Java — FIXED:
```java
// Use default trust manager with system CA certificates
SSLContext sc = SSLContext.getInstance("TLS");
sc.init(null, null, new SecureRandom());

// Or for custom CA:
KeyStore ks = KeyStore.getInstance(KeyStore.getDefaultType());
ks.load(new FileInputStream("/path/to/truststore.jks"), password);
TrustManagerFactory tmf = TrustManagerFactory.getInstance("PKIX");
tmf.init(ks);
sc.init(null, tmf.getTrustManagers(), new SecureRandom());
```

Go — VULNERABLE:
```go
tr := &http.Transport{
    TLSClientConfig: &tls.Config{
        InsecureSkipVerify: true,
        MinVersion:         tls.VersionTLS10,
    },
}
client := &http.Client{Transport: tr}
```

Go — FIXED:
```go
tr := &http.Transport{
    TLSClientConfig: &tls.Config{
        MinVersion: tls.VersionTLS12,
    },
}
client := &http.Client{Transport: tr}
```

**Scanner Coverage**: semgrep `python.requests.security.no-verify-ssl`,
bandit `B501` (requests verify=False), gosec `G402` (TLS InsecureSkipVerify)

**False Positive Guidance**: Disabling TLS verification is common in local
development and test environments. Check whether the code is gated behind a
development/test flag or environment check. `http://localhost` and `http://127.0.0.1`
are not vulnerabilities. Internal service-mesh traffic that terminates TLS at
the sidecar (e.g., Istio) may intentionally use HTTP between containers.

**Severity Assessment**:
- **critical**: Disabled certificate validation in production code path
- **high**: Sensitive data sent over HTTP to external services, TLS 1.0/1.1 in production
- **medium**: HTTP used for internal APIs not behind a service mesh
- **low**: TLS 1.2 enforced but TLS 1.3 not required (defense-in-depth)
