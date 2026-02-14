# Vulnerable and Outdated Components Detection Patterns

Grep-based heuristics and manifest analysis patterns for detecting dependency
risks when scanners are unavailable or as supplemental checks alongside scanner
output. Each pattern includes regex search strings, ecosystem examples, scanner
coverage, and false positive guidance.

---

## Pattern 1: Unpinned Dependency Versions

**Description**: Dependency manifests using loose version constraints allow
automatic resolution to newer (potentially vulnerable or breaking) versions.
Pinning exact versions ensures reproducible builds and controlled upgrades.

**Grep Regex Heuristics**:

For `package.json`:
```
"[\^~]\d+\.\d+
"[>]=?\s*\d+\.\d+
"\*"
"latest"
```

For `requirements.txt`:
```
^[a-zA-Z][a-zA-Z0-9_-]*$
[a-zA-Z0-9_-]+>=\d+
[a-zA-Z0-9_-]+~=\d+
```

For `Cargo.toml`:
```
\s*=\s*"\d+(\.\d+)?"
```

For `go.mod` (Go uses exact versions by default -- less common issue):
```
// indirect
```

**File patterns to search**: `package.json`, `requirements*.txt`, `Pipfile`,
`pyproject.toml`, `Cargo.toml`, `Gemfile`, `composer.json`, `*.csproj`, `pom.xml`,
`build.gradle`, `build.gradle.kts`

**Language Examples**:

Node.js (vulnerable):
```json
{
  "dependencies": {
    "express": "^4.17.0",
    "lodash": "~4.17.0",
    "axios": "*",
    "debug": "latest"
  }
}
```

Node.js (fixed):
```json
{
  "dependencies": {
    "express": "4.21.2",
    "lodash": "4.17.21",
    "axios": "1.7.9",
    "debug": "4.4.0"
  }
}
```

Python (vulnerable):
```
# requirements.txt
flask
requests>=2.20
django~=4.2
sqlalchemy
```

Python (fixed):
```
# requirements.txt
flask==3.1.0
requests==2.32.3
django==4.2.17
sqlalchemy==2.0.36
```

Java/Gradle (vulnerable):
```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter:+'
    implementation 'com.google.guava:guava:31.+'
}
```

Java/Gradle (fixed):
```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter:3.4.2'
    implementation 'com.google.guava:guava:33.4.0-jre'
}
```

Rust (vulnerable):
```toml
[dependencies]
serde = "1"
tokio = "1.0"
```

Rust (fixed):
```toml
[dependencies]
serde = "=1.0.217"
tokio = "=1.43.0"
```

**Scanner Coverage**: None -- this is a manifest hygiene check that scanners do not
typically flag. This is primarily a Claude analysis pattern.

**False Positive Guidance**:
- Caret (`^`) ranges in `package.json` are the npm ecosystem default and are acceptable
  when a lockfile is committed and regularly updated. Flag only when no lockfile exists.
- Rust's `"1.0"` syntax is equivalent to `^1.0` and is idiomatic. The `Cargo.lock`
  file pins exact versions. Flag only when `Cargo.lock` is missing or gitignored for
  applications (libraries intentionally omit it).
- Python `~=` (compatible release) is considered acceptable when a lockfile
  (`Pipfile.lock`, `poetry.lock`) is committed.
- Development dependencies have lower risk than production dependencies.

**Severity Criteria**:
- **HIGH**: Unpinned production dependencies with no lockfile committed.
- **MEDIUM**: Loose version ranges in production dependencies with a lockfile present.
- **LOW**: Unpinned development-only dependencies.

---

## Pattern 2: Missing Lockfile

**Description**: Without a committed lockfile, dependency resolution happens at
install time and can produce different dependency trees on different machines or
at different times. This breaks reproducibility and makes it impossible to audit
exactly which versions are in production.

**Grep Regex Heuristics**:

Check `.gitignore` for lockfile exclusions:
```
package-lock\.json
yarn\.lock
pnpm-lock\.yaml
Pipfile\.lock
poetry\.lock
Cargo\.lock
Gemfile\.lock
composer\.lock
```

**Detection method**: For each manifest file found, check whether the corresponding
lockfile exists in the same directory. Also check `.gitignore` for lockfile entries.

| Manifest | Expected Lockfile |
|----------|------------------|
| `package.json` | `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml` |
| `Pipfile` | `Pipfile.lock` |
| `pyproject.toml` (Poetry) | `poetry.lock` |
| `Cargo.toml` (binary/app) | `Cargo.lock` |
| `Gemfile` | `Gemfile.lock` |
| `composer.json` | `composer.lock` |
| `go.mod` | `go.sum` |

**Language Examples**:

Node.js (vulnerable):
```gitignore
# .gitignore
node_modules/
package-lock.json   # <-- lockfile excluded from version control
```

Node.js (fixed):
```gitignore
# .gitignore
node_modules/
# package-lock.json is tracked in version control
```

Python (vulnerable):
```
# Project has Pipfile but no Pipfile.lock in repository
$ ls
Pipfile  src/  tests/
# No Pipfile.lock
```

Python (fixed):
```
# Both Pipfile and Pipfile.lock are committed
$ ls
Pipfile  Pipfile.lock  src/  tests/
```

**Scanner Coverage**: trivy (partial -- warns about missing lockfiles for some ecosystems),
osv-scanner (requires lockfile to scan, so its absence is implicitly detected)

**False Positive Guidance**:
- Libraries (as opposed to applications) conventionally do NOT commit lockfiles in
  some ecosystems (Rust `Cargo.lock` for libraries, Python packages). The lockfile
  ensures consumers test against the range.
- Monorepos may have lockfiles at the root rather than in each package directory.
- Some projects use alternative lock mechanisms (e.g., `npm-shrinkwrap.json`).

**Severity Criteria**:
- **HIGH**: Application with no lockfile for production dependencies.
- **MEDIUM**: Lockfile exists but is explicitly gitignored.
- **LOW**: Library project without a lockfile (conventional in some ecosystems).

---

## Pattern 3: Known CVE in Lockfile Dependency

**Description**: Lockfiles contain exact resolved versions that may have known CVEs.
While scanners are the primary detection mechanism, Claude can perform limited
checks for widely-known critical vulnerabilities by recognizing package name and
version combinations.

**Grep Regex Heuristics**:

Search lockfiles for known-vulnerable version patterns (examples of historically
critical vulnerabilities):

```
"log4j-core".*"2\.(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16)\."
"lodash".*"4\.(17\.[0-9]|17\.1[0-6])"[^0-9]
"minimist".*"[01]\."
"node-forge".*"[0]\."
"ua-parser-js".*"0\.(7\.[0-9]|7\.2[0-8])"
"tar".*"[0-5]\."
"glob-parent".*"[0-4]\."
"express".*"[0-3]\."
"django".*"[0-2]\."
"flask".*"[01]\."
"spring-core".*"5\.[0-2]\."
```

**File patterns to search**: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`,
`Pipfile.lock`, `poetry.lock`, `Cargo.lock`, `Gemfile.lock`, `composer.lock`, `go.sum`

**Important**: This pattern is a rough heuristic only. Scanners with up-to-date
vulnerability databases are far more reliable. These regex patterns cover only a
handful of historically critical vulnerabilities and will quickly become outdated.

**Scanner Coverage**: npm audit, pip-audit, trivy, osv-scanner, cargo-audit -- all
provide comprehensive CVE detection. **Prefer scanner results over regex matching.**

**False Positive Guidance**:
- Version matching is imprecise. A regex match does not confirm a CVE -- the actual
  vulnerability may affect only specific minor/patch versions.
- Some packages have the same name across ecosystems but are different software.
- Vulnerabilities may not be exploitable in the project's specific usage context.
- Always recommend running a proper scanner for confirmation.

**Severity Criteria**:
- **CRITICAL**: Match for a known RCE vulnerability (e.g., Log4Shell).
- **HIGH**: Match for a known data exposure or privilege escalation vulnerability.
- **MEDIUM**: Match for a known DoS or limited-impact vulnerability.
- **LOW**: Version is old enough to likely have known issues but no specific CVE matched.

---

## Pattern 4: Abandoned Packages

**Description**: Dependencies that are no longer maintained do not receive security
patches. When a CVE is discovered in an abandoned package, no fix will be released,
leaving the application permanently vulnerable until the dependency is replaced.

**Grep Regex Heuristics**:

There are no direct regex patterns for detecting abandonment in source code. Instead,
use these indicators:

1. Check for known deprecated packages by name:
```
request['":\s]
moment['":\s]
tslint['":\s]
bower['":\s]
istanbul['":\s]
nomnom['":\s]
node-uuid['":\s]
optimist['":\s]
coffee-script['":\s]
```

2. Check for deprecation notices in lockfiles:
```
deprecated
DEPRECATED
```

**File patterns to search**: `package.json`, `package-lock.json`, `yarn.lock`,
`requirements*.txt`, `Pipfile`, `pyproject.toml`, `Cargo.toml`, `Gemfile`,
`composer.json`

**Language Examples**:

Node.js (vulnerable):
```json
{
  "dependencies": {
    "request": "^2.88.0",
    "moment": "^2.29.0",
    "tslint": "^6.1.0"
  }
}
```

Node.js (fixed):
```json
{
  "dependencies": {
    "undici": "^6.0.0",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "eslint": "^9.0.0",
    "@typescript-eslint/eslint-plugin": "^8.0.0"
  }
}
```

Python (vulnerable):
```
# requirements.txt
nose==1.3.7
pycrypto==2.6.1
optparse-pretty==0.1.0
```

Python (fixed):
```
# requirements.txt
pytest==8.3.4
pycryptodome==3.21.0
argparse==1.4.0
```

**Scanner Coverage**: npm audit (flags deprecated packages), trivy (partial),
osv-scanner (via OSV database)

**False Positive Guidance**:
- A package being old does not mean it is abandoned. Stable, feature-complete packages
  (e.g., `inherits`, `ms`) may simply not need updates.
- Check whether the package's functionality is security-sensitive. An abandoned date
  formatting library is lower risk than an abandoned crypto library.
- Forks or spiritual successors may exist -- recommend alternatives when flagging.

**Severity Criteria**:
- **HIGH**: Abandoned security-sensitive package (crypto, auth, network, serialization).
- **MEDIUM**: Abandoned package with known unpatched CVEs.
- **LOW**: Abandoned package with no known CVEs but no future security support.

---

## Pattern 5: Typosquatting Candidates

**Description**: Attackers publish malicious packages with names similar to popular
packages (e.g., `coffe-script` instead of `coffee-script`, `crossenv` instead of
`cross-env`). Developers who mistype a package name during installation may pull
in malware.

**Grep Regex Heuristics**:

Look for package names that are one character different from popular packages:

```
crossenv|cross-env\.
cros-env|crosss-env
loadsh|lodahs|lodas
exress|expresss|expres[^s]
requets|reqeusts|requsets
colrs|collors|colour[^s]
babelcli|babel_cli
event-stream|eventstream
flatmap-stream
eslint-scope|eslint_scope
```

Also look for suspicious install scripts:
```
"preinstall":\s*"
"postinstall":\s*"(curl|wget|node\s|python|bash|sh\s)"
```

**File patterns to search**: `package.json`, `requirements*.txt`, `Pipfile`,
`pyproject.toml`, `Cargo.toml`, `Gemfile`, `composer.json`

**Language Examples**:

Node.js (vulnerable):
```json
{
  "dependencies": {
    "loadsh": "^4.17.0",
    "crossenv": "^7.0.0"
  }
}
```

Node.js (fixed):
```json
{
  "dependencies": {
    "lodash": "^4.17.21",
    "cross-env": "^7.0.3"
  }
}
```

Python (vulnerable):
```
# requirements.txt
reqeusts==2.31.0
python-dateuti==2.8.2
```

Python (fixed):
```
# requirements.txt
requests==2.32.3
python-dateutil==2.9.0
```

**Scanner Coverage**: npm audit (known malicious packages), osv-scanner (known
malicious packages), socket.dev (specialized -- not in standard scanner list)

**False Positive Guidance**:
- Some legitimately-named packages look like typos but are real, distinct packages.
  Verify by checking the package registry.
- Regex-based typo detection is inherently noisy. Flag only names that closely
  match the top 100 most popular packages in each ecosystem.
- Packages with significant download counts are less likely to be typosquatting.

**Severity Criteria**:
- **CRITICAL**: Package name is a known typosquatting malware package.
- **HIGH**: Package name is one edit distance from a top-100 package and has
  suspicious install scripts.
- **MEDIUM**: Package name is one edit distance from a popular package but has
  no other indicators.
- **LOW**: Package name is unusual but does not closely match any popular package.

---

## Pattern 6: Excessive Transitive Dependencies

**Description**: A project with a small number of direct dependencies that resolves
to hundreds or thousands of transitive packages has a large attack surface. Each
transitive dependency is a potential vector for supply chain attacks, and auditing
them all is impractical.

**Grep Regex Heuristics**:

Count entries in lockfiles to estimate total dependency count:

For `package-lock.json`:
```
"resolved":
```

For `yarn.lock`:
```
^[a-zA-Z@"'].*:$
```

For `Pipfile.lock`:
```
"hashes":
```

For `Cargo.lock`:
```
\[\[package\]\]
```

**Detection method**: Count the number of resolved packages in the lockfile and
compare to the number of direct dependencies in the manifest. Flag when the ratio
is unusually high (e.g., 10 direct dependencies resolving to 500+ transitive
packages).

**Thresholds** (approximate, ecosystem-dependent):

| Ecosystem | Direct Deps | Concerning Transitive Count |
|-----------|-------------|-----------------------------|
| Node.js | < 20 | > 500 |
| Node.js | < 50 | > 1000 |
| Python | < 20 | > 100 |
| Rust | < 20 | > 200 |
| Go | < 20 | > 100 |

**Language Examples**:

Node.js (vulnerable):
```json
{
  "dependencies": {
    "create-react-app": "^5.0.0"
  }
}
// package-lock.json contains 1,400+ resolved packages
```

Node.js (fixed):
```json
{
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-scripts": "^5.0.0"
  }
}
// Prefer specific packages over meta-packages when possible
// Regularly audit with: npm ls --all | wc -l
```

**Scanner Coverage**: None directly. Some tools like `npm ls --all`, `pipdeptree`,
or `cargo tree` can enumerate the tree but do not flag excessive size.

**False Positive Guidance**:
- Some ecosystems (notably npm) naturally have large dependency trees due to small,
  single-purpose packages. Absolute counts should be interpreted relative to
  ecosystem norms.
- Monorepos and workspaces may have a single lockfile for many packages, inflating
  the apparent count.
- The concern is disproportionate growth. A project with 5 direct dependencies and
  800 transitive packages deserves scrutiny; a project with 50 direct dependencies
  and 800 transitive packages is more expected.

**Severity Criteria**:
- **MEDIUM**: Transitive dependency count exceeds ecosystem thresholds relative to
  direct dependency count.
- **LOW**: Large but proportionate dependency tree in a framework-heavy project.
