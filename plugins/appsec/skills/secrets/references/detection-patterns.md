# Secrets Detection Patterns

Patterns for detecting hardcoded secrets, credentials, API keys, and sensitive
material in source code and configuration files.

---

## 1. Cloud Provider API Keys

**Description**: Hardcoded API keys for cloud providers (AWS, GCP, Azure) in
source code or configuration. These keys provide direct access to cloud
resources and are immediately exploitable upon exposure.

**Search Heuristics**:
- Grep: `AKIA[0-9A-Z]{16}` (AWS access key ID)
- Grep: `ABIA|ACCA|AGPA|AIDA|AIPA|AKIA|ANPA|ANVA|APKA|AROA|ASCA|ASIA` (AWS key prefixes)
- Grep: `AIza[0-9A-Za-z_-]{35}` (Google API key)
- Grep: `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` in Azure context
- Glob: `**/*.py`, `**/*.js`, `**/*.ts`, `**/*.go`, `**/*.java`, `**/*.yaml`, `**/*.yml`

**Language Examples**:

Python -- VULNERABLE:
```python
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
```

Python -- FIXED:
```python
import boto3
# Uses environment variables or IAM role automatically
s3 = boto3.client('s3')
```

JavaScript -- VULNERABLE:
```javascript
const config = {
  apiKey: "AIzaSyA1b2c3d4e5f6g7h8i9j0kLmNoPqRsTuVw",
  authDomain: "myproject.firebaseapp.com",
};
```

JavaScript -- FIXED:
```javascript
const config = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
};
```

Java -- VULNERABLE:
```java
AmazonS3 s3 = AmazonS3ClientBuilder.standard()
    .withCredentials(new AWSStaticCredentialsProvider(
        new BasicAWSCredentials("AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI...")))
    .build();
```

Java -- FIXED:
```java
AmazonS3 s3 = AmazonS3ClientBuilder.standard()
    .withCredentials(new DefaultAWSCredentialsProviderChain())
    .build();
```

Go -- VULNERABLE:
```go
sess := session.Must(session.NewSession(&aws.Config{
    Credentials: credentials.NewStaticCredentials(
        "AKIAIOSFODNN7EXAMPLE", "wJalrXUtnFEMI...", ""),
}))
```

Go -- FIXED:
```go
sess := session.Must(session.NewSession())
// Uses default credential chain (env vars, shared credentials, IAM role)
```

**Scanner Coverage**: gitleaks `aws-access-key-id`, `aws-secret-access-key`;
trufflehog `AWS`, `GCP` detectors

**False Positive Guidance**: Example keys in documentation or tests (e.g.,
`AKIAIOSFODNN7EXAMPLE`) are false positives. Check for `example`, `test`,
`fake`, `dummy` in surrounding context. AWS example keys always use the
`EXAMPLE` suffix.

**Severity Assessment**:
- **critical**: AWS/GCP/Azure keys in production code or config
- **high**: Cloud keys in test files that might reference real services
- **medium**: Keys that appear to be example/placeholder values

---

## 2. Service-Specific Tokens

**Description**: API tokens for third-party services (GitHub, Stripe, Slack,
SendGrid, Twilio) hardcoded in source code. Each service has a distinctive
token format that can be matched with regex.

**Search Heuristics**:
- Grep: `ghp_[0-9a-zA-Z]{36}` (GitHub personal access token)
- Grep: `github_pat_[0-9a-zA-Z]{22}_[0-9a-zA-Z]{59}` (GitHub fine-grained PAT)
- Grep: `sk_live_[0-9a-zA-Z]{24,}` (Stripe secret key)
- Grep: `xoxb-[0-9]{10,}-[0-9a-zA-Z]{24,}` (Slack bot token)
- Grep: `SG\.[0-9A-Za-z_-]{22}\.[0-9A-Za-z_-]{43}` (SendGrid API key)
- Grep: `sk-[0-9a-zA-Z]{48}` (OpenAI API key)
- Glob: `**/*.py`, `**/*.js`, `**/*.ts`, `**/*.env`, `**/*.yaml`

**Language Examples**:

Python -- VULNERABLE:
```python
import stripe
stripe.api_key = "sk_live_EXAMPLE_DO_NOT_USE_1234567890abcdef"
```

Python -- FIXED:
```python
import os, stripe
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
```

JavaScript -- VULNERABLE:
```javascript
const octokit = new Octokit({ auth: "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" });
```

JavaScript -- FIXED:
```javascript
const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
```

Java -- VULNERABLE:
```java
Stripe.apiKey = "sk_live_EXAMPLE_DO_NOT_USE_1234567890abcdef";
```

Java -- FIXED:
```java
Stripe.apiKey = System.getenv("STRIPE_SECRET_KEY");
```

Go -- VULNERABLE:
```go
client := slack.New("xoxb-0000000000-EXAMPLE_TOKEN_DO_NOT_USE")
```

Go -- FIXED:
```go
client := slack.New(os.Getenv("SLACK_BOT_TOKEN"))
```

**Scanner Coverage**: gitleaks `github-pat`, `stripe-api-key`, `slack-bot-token`,
`sendgrid-api-key`; trufflehog service-specific detectors with live verification

**False Positive Guidance**: Test/sandbox keys (e.g., Stripe `sk_test_*`) are
lower severity but should still not be committed. Documentation examples using
obviously fake values are false positives.

**Severity Assessment**:
- **critical**: Live/production service tokens (Stripe live, GitHub PAT with repo scope)
- **high**: Tokens with broad permissions or access to sensitive data
- **medium**: Test/sandbox tokens committed to repo

---

## 3. Hardcoded Passwords and Connection Strings

**Description**: Database credentials, connection strings, and passwords embedded
directly in source code or configuration files, rather than loaded from secure
secret management.

**Search Heuristics**:
- Grep: `password\s*[:=]\s*['"][^'"]{8,}['"]` (password assignments)
- Grep: `(mysql|postgres|mongodb|redis)://[^:]+:[^@]+@` (connection strings with credentials)
- Grep: `DB_PASSWORD\s*=\s*['"][^'"]+['"]`
- Grep: `connectionString\s*[:=].*password`
- Glob: `**/*.py`, `**/*.js`, `**/*.yaml`, `**/*.properties`, `**/*.xml`, `**/*.toml`

**Language Examples**:

Python -- VULNERABLE:
```python
DATABASE_URL = "postgresql://admin:SuperSecret123@db.example.com:5432/production"
```

Python -- FIXED:
```python
import os
DATABASE_URL = os.environ["DATABASE_URL"]
```

JavaScript -- VULNERABLE:
```javascript
const pool = new Pool({
  host: 'db.example.com',
  user: 'admin',
  password: 'SuperSecret123',
  database: 'production',
});
```

JavaScript -- FIXED:
```javascript
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});
```

Java -- VULNERABLE:
```java
String url = "jdbc:mysql://db.example.com:3306/prod?user=admin&password=SuperSecret123";
Connection conn = DriverManager.getConnection(url);
```

Java -- FIXED:
```java
String url = System.getenv("JDBC_URL");
Connection conn = DriverManager.getConnection(url);
```

Go -- VULNERABLE:
```go
db, err := sql.Open("postgres", "postgres://admin:SuperSecret123@db.example.com/prod")
```

Go -- FIXED:
```go
db, err := sql.Open("postgres", os.Getenv("DATABASE_URL"))
```

**Scanner Coverage**: gitleaks `generic-password`, `connection-string`;
trufflehog `URI` detector

**False Positive Guidance**: Connection strings pointing to `localhost`,
`127.0.0.1`, or containing `example`, `changeme`, `password` as the password
value are typically development defaults. Docker Compose files with local-only
credentials may be intentional but should still be flagged as `low`.

**Severity Assessment**:
- **critical**: Production database credentials in source code
- **high**: Connection strings with non-localhost hosts and real-looking passwords
- **medium**: Development/local credentials committed to repo
- **low**: Example/placeholder passwords in documentation or templates

---

## 4. Private Keys

**Description**: Private keys (RSA, EC, PGP, SSH) committed to the repository.
Private keys allow impersonation, decryption of data, and signing of artifacts.
Any committed private key must be considered compromised.

**Search Heuristics**:
- Grep: `-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----`
- Grep: `-----BEGIN PGP PRIVATE KEY BLOCK-----`
- Grep: `PuTTY-User-Key-File`
- Glob: `**/*.pem`, `**/*.key`, `**/*.p12`, `**/*.pfx`, `**/id_rsa`, `**/id_ed25519`

**Language Examples**:

Python -- VULNERABLE:
```python
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy...
-----END RSA PRIVATE KEY-----"""
jwt_token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
```

Python -- FIXED:
```python
import os
PRIVATE_KEY = os.environ["JWT_PRIVATE_KEY"]
# Or load from a secrets manager:
# PRIVATE_KEY = secrets_client.get_secret("jwt-private-key")
jwt_token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
```

JavaScript -- VULNERABLE:
```javascript
const privateKey = fs.readFileSync('./keys/private.pem', 'utf8');
// private.pem is committed to the repository
```

JavaScript -- FIXED:
```javascript
const privateKey = process.env.JWT_PRIVATE_KEY;
// Or: const privateKey = await secretsManager.getSecret('jwt-private-key');
```

Java -- VULNERABLE:
```java
// Private key file checked into resources/
InputStream keyStream = getClass().getResourceAsStream("/private-key.pem");
```

Java -- FIXED:
```java
// Load from environment or secrets manager
String keyPem = System.getenv("PRIVATE_KEY_PEM");
```

Go -- VULNERABLE:
```go
//go:embed keys/private.pem
var privateKeyPEM []byte
```

Go -- FIXED:
```go
privateKeyPEM := []byte(os.Getenv("PRIVATE_KEY_PEM"))
```

**Scanner Coverage**: gitleaks `private-key`; trufflehog `PrivateKey` detector

**False Positive Guidance**: Public keys (not private) are not secrets. Test
fixtures with clearly marked dummy keys generated for CI may be acceptable if
they have no access to real systems. Check `.gitignore` for `*.pem` and `*.key`.

**Severity Assessment**:
- **critical**: Any real private key committed to the repository
- **high**: Private key files present but possibly test/development keys
- **medium**: Missing .gitignore patterns for private key file extensions

---

## 5. Committed .env Files

**Description**: Environment files (`.env`, `.env.production`, `.env.local`)
committed to version control. These files typically contain all application
secrets in one place and should never be checked in.

**Search Heuristics**:
- Grep: `^[A-Z_]+\s*=\s*[^\s]+` inside `.env` files
- Glob: `**/.env`, `**/.env.*`, `**/.env.local`, `**/.env.production`
- Grep: `.env` absence in `.gitignore`
- Glob: `**/.gitignore` (check for `.env` pattern)

**Language Examples**:

VULNERABLE -- `.env` committed to repo:
```
DATABASE_URL=postgresql://admin:RealPassword@prod-db.example.com:5432/app
STRIPE_SECRET_KEY=sk_live_EXAMPLE_DO_NOT_USE_1234567890abcdef
JWT_SECRET=my-super-secret-jwt-signing-key-do-not-share
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

FIXED -- `.env.example` committed (no real values), `.env` in `.gitignore`:
```
# .env.example (committed)
DATABASE_URL=postgresql://user:password@localhost:5432/app_dev
STRIPE_SECRET_KEY=sk_test_your_test_key_here
JWT_SECRET=change-me-in-production
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# .gitignore includes:
# .env
# .env.*
# !.env.example
```

**Scanner Coverage**: gitleaks `dotenv`; trufflehog scans `.env` file contents
for known credential patterns

**False Positive Guidance**: `.env.example` or `.env.template` files with
placeholder values are intentionally committed and are not findings. Check
whether the values look real (high entropy, matching known key formats) vs
obvious placeholders.

**Severity Assessment**:
- **critical**: `.env.production` or `.env` with production credentials committed
- **high**: `.env` with real-looking secrets committed
- **medium**: `.env` missing from `.gitignore` (even if no .env file exists yet)
- **low**: `.env.example` with slightly too-realistic placeholder values

---

## 6. High-Entropy Strings

**Description**: Strings with high Shannon entropy in contexts suggesting they
are secrets (assigned to variables named `key`, `secret`, `token`, etc.). This
pattern catches custom or proprietary secrets that do not match any known format.

**Search Heuristics**:
- Grep: `(secret|token|key|password|credential|api_key)\s*[:=]\s*['"][A-Za-z0-9+/=_-]{20,}['"]`
- Grep: `Bearer\s+[A-Za-z0-9._~+/=-]{20,}`
- Grep: `[A-Fa-f0-9]{40,}` assigned to secret-like variables
- Grep: `[A-Za-z0-9+/]{40,}={0,2}` (base64 strings over 40 chars)
- Glob: `**/*.py`, `**/*.js`, `**/*.ts`, `**/*.go`, `**/*.java`, `**/*.yaml`

**Language Examples**:

Python -- VULNERABLE:
```python
SIGNING_SECRET = "a3f4b8c9d2e1f0a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9"
INTERNAL_API_KEY = "dGhpcyBpcyBhIHNlY3JldCBrZXkgdGhhdCBzaG91bGQgbm90"
```

Python -- FIXED:
```python
import os
SIGNING_SECRET = os.environ["SIGNING_SECRET"]
INTERNAL_API_KEY = os.environ["INTERNAL_API_KEY"]
```

JavaScript -- VULNERABLE:
```javascript
const WEBHOOK_SECRET = "whsec_a3f4b8c9d2e1f0a5b6c7d8e9f0a1b2c3";
const ENCRYPTION_KEY = "7f2dcba1e4c93f6a8b5d0e7c2a1f4b8d";
```

JavaScript -- FIXED:
```javascript
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;
```

Java -- VULNERABLE:
```java
private static final String HMAC_KEY = "a3f4b8c9d2e1f0a5b6c7d8e9f0a1b2c3d4e5f6a7";
```

Java -- FIXED:
```java
private static final String HMAC_KEY = System.getenv("HMAC_KEY");
```

Go -- VULNERABLE:
```go
const webhookSecret = "whsec_a3f4b8c9d2e1f0a5b6c7d8e9f0a1b2c3"
```

Go -- FIXED:
```go
var webhookSecret = os.Getenv("WEBHOOK_SECRET")
```

**Scanner Coverage**: gitleaks `generic-api-key` (entropy-based); trufflehog
entropy analysis with contextual scoring

**False Positive Guidance**: Hash constants (SHA-256 checksums for integrity
verification), test fixtures with random-looking but non-secret data, and
cryptographic constants (IVs, salts that are not secret) may trigger false
positives. Check variable naming and usage context. If the string is used for
verification (comparing against) rather than authentication (sending to a
service), it may not be a secret.

**Severity Assessment**:
- **critical**: High-entropy string in a variable named `secret`, `password`, or `key` with production context
- **high**: High-entropy string assigned to credential-like variable
- **medium**: High-entropy string without clear context (needs manual verification)
