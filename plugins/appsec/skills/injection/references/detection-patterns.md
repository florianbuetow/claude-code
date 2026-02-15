# Injection Detection Patterns

Detailed detection patterns for OWASP A03:2021 Injection analysis. Each pattern
includes Grep regex heuristics, language-specific examples, scanner coverage,
false positive guidance, and severity criteria.

---

## Pattern 1: String Concatenation in SQL Queries

### Description

User input is concatenated directly into SQL query strings using the `+`
operator, `.concat()`, or equivalent. This is the most common and most
dangerous injection pattern.

### Grep Search Heuristics

```
# Python - string concatenation in execute calls
"execute\s*\(\s*[\"'].*\+.*\)"
"cursor\.\w+\s*\(\s*[\"']SELECT.*\+|cursor\.\w+\s*\(\s*[\"']INSERT.*\+|cursor\.\w+\s*\(\s*[\"']UPDATE.*\+|cursor\.\w+\s*\(\s*[\"']DELETE.*\+"

# JavaScript/TypeScript - string concatenation in query calls
"\.query\s*\(\s*[\"'].*\+.*\)"
"\.execute\s*\(\s*[\"'].*\+.*\)"

# Java - string concatenation in SQL
"Statement.*execute\w*\s*\(\s*\".*\+.*\)"
"createStatement|prepareStatement\s*\(\s*\".*\+.*\)"

# Go - string concatenation in SQL
"db\.(Query|Exec)\w*\s*\(\s*\".*\+.*\)"
"fmt\.Sprintf\s*\(\s*\"(SELECT|INSERT|UPDATE|DELETE)"

# General - any SQL keyword followed by concatenation
"(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE).*[\"']\s*\+\s*\w"
```

### Language Examples

**Python -- Vulnerable**:
```python
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = " + user_id)
    return cursor.fetchone()
```

**Python -- Fixed**:
```python
def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
async function getUser(userId) {
  const result = await db.query("SELECT * FROM users WHERE id = " + userId);
  return result.rows[0];
}
```

**JavaScript/TypeScript -- Fixed**:
```javascript
async function getUser(userId) {
  const result = await db.query("SELECT * FROM users WHERE id = $1", [userId]);
  return result.rows[0];
}
```

**Java -- Vulnerable**:
```java
public User getUser(String userId) {
    Statement stmt = connection.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);
    return mapUser(rs);
}
```

**Java -- Fixed**:
```java
public User getUser(String userId) {
    PreparedStatement stmt = connection.prepareStatement("SELECT * FROM users WHERE id = ?");
    stmt.setString(1, userId);
    ResultSet rs = stmt.executeQuery();
    return mapUser(rs);
}
```

**Go -- Vulnerable**:
```go
func getUser(db *sql.DB, userID string) (*User, error) {
    row := db.QueryRow("SELECT * FROM users WHERE id = " + userID)
    return scanUser(row)
}
```

**Go -- Fixed**:
```go
func getUser(db *sql.DB, userID string) (*User, error) {
    row := db.QueryRow("SELECT * FROM users WHERE id = $1", userID)
    return scanUser(row)
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Yes | `*.lang.security.audit.raw-query`, `*.lang.security.injection.sql` |
| bandit | Yes (Python) | `B608` (hardcoded_sql_expressions) |
| gosec | Yes (Go) | `G201` (SQL string concatenation) |
| brakeman | Yes (Rails) | SQL Injection warning |

### False Positive Guidance

- **Static strings only**: `"SELECT * FROM users WHERE role = " + "'admin'"` is
  not vulnerable if the concatenated value is a hardcoded string literal. Check
  whether the right-hand side of `+` comes from user input or is a constant.
- **Integer-typed variables**: In strongly-typed languages (Java, Go), if the
  variable is provably an `int`/`long` type, SQL injection is not possible.
  Still recommend parameterized queries as defense-in-depth.
- **Query builders**: Some query builders produce concatenation internally but
  handle escaping. Check if the method is part of a safe query builder API.

### Severity Criteria

- **critical**: Concatenated value comes from HTTP request (query param, body,
  header) with no validation. Directly exploitable.
- **high**: Concatenated value comes from a function parameter that could
  originate from user input but requires tracing to confirm.
- **medium**: Concatenated value is type-constrained (e.g., integer) but pattern
  is still unsafe practice.

---

## Pattern 2: Template String SQL Construction

### Description

User input is interpolated into SQL queries using template literals (JavaScript),
f-strings (Python), or string formatting functions. Functionally identical to
concatenation but uses different syntax.

### Grep Search Heuristics

```
# Python - f-strings and .format() in SQL
"f\"(SELECT|INSERT|UPDATE|DELETE)\b"
"f'(SELECT|INSERT|UPDATE|DELETE)\b"
"\"(SELECT|INSERT|UPDATE|DELETE).*\.format\s*\("

# JavaScript/TypeScript - template literals in SQL
"`(SELECT|INSERT|UPDATE|DELETE)\b.*\$\{"

# Java - String.format in SQL
"String\.format\s*\(\s*\"(SELECT|INSERT|UPDATE|DELETE)"

# Go - fmt.Sprintf in SQL
"fmt\.Sprintf\s*\(\s*\"(SELECT|INSERT|UPDATE|DELETE)"
```

### Language Examples

**Python -- Vulnerable**:
```python
def search_users(name):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    cursor.execute(query)
    return cursor.fetchall()
```

**Python -- Fixed**:
```python
def search_users(name):
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    return cursor.fetchall()
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
async function searchUsers(name) {
  const query = `SELECT * FROM users WHERE name = '${name}'`;
  return await db.query(query);
}
```

**JavaScript/TypeScript -- Fixed**:
```javascript
async function searchUsers(name) {
  return await db.query("SELECT * FROM users WHERE name = $1", [name]);
}
```

**Java -- Vulnerable**:
```java
public List<User> searchUsers(String name) {
    String query = String.format("SELECT * FROM users WHERE name = '%s'", name);
    return jdbcTemplate.query(query, userRowMapper);
}
```

**Java -- Fixed**:
```java
public List<User> searchUsers(String name) {
    return jdbcTemplate.query("SELECT * FROM users WHERE name = ?", userRowMapper, name);
}
```

**Go -- Vulnerable**:
```go
func searchUsers(db *sql.DB, name string) ([]User, error) {
    query := fmt.Sprintf("SELECT * FROM users WHERE name = '%s'", name)
    rows, err := db.Query(query)
    return scanUsers(rows, err)
}
```

**Go -- Fixed**:
```go
func searchUsers(db *sql.DB, name string) ([]User, error) {
    rows, err := db.Query("SELECT * FROM users WHERE name = $1", name)
    return scanUsers(rows, err)
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Yes | `*.lang.security.audit.formatted-sql-query` |
| bandit | Yes (Python) | `B608` |
| gosec | Yes (Go) | `G201`, `G202` |
| brakeman | Yes (Rails) | SQL Injection warning |

### False Positive Guidance

- **Table/column names**: Using f-strings for table or column names that are
  not user-controlled (e.g., from an enum or config) is less dangerous but
  still a bad pattern. Flag as `medium`.
- **Logging/debugging**: SQL strings built for logging or debugging that are
  never executed are not vulnerabilities.
- **Constants in interpolation**: `f"SELECT * FROM {TABLE_NAME}"` where
  `TABLE_NAME` is a module-level constant is low risk.

### Severity Criteria

- **critical**: Interpolated variable comes from user input and query is executed.
- **high**: Variable origin is unclear but pattern is in an HTTP handler context.
- **medium**: Interpolation uses constants or enum values but pattern should be
  refactored for consistency and defense-in-depth.

---

## Pattern 3: Raw ORM Queries with User Input

### Description

ORMs provide safe query builders, but most also expose a "raw SQL" escape hatch.
When user input flows into raw ORM queries, the ORM's protections are bypassed.

### Grep Search Heuristics

```
# Python Django
"\.raw\s*\(\s*f\"|\.raw\s*\(\s*[\"'].*\+|\.raw\s*\(\s*[\"'].*\.format|\.extra\s*\("

# Python SQLAlchemy
"text\s*\(\s*f\"|text\s*\(\s*[\"'].*\+|text\s*\(\s*[\"'].*\.format"
"from_statement\s*\(\s*text\s*\("

# JavaScript Sequelize
"sequelize\.query\s*\(\s*`|sequelize\.query\s*\(\s*[\"'].*\+"
"\.literal\s*\("

# JavaScript TypeORM
"\.query\s*\(\s*`|\.query\s*\(\s*[\"'].*\+"
"createQueryBuilder.*\.where\s*\(\s*`"

# Java Hibernate/JPA
"createNativeQuery\s*\(\s*\".*\+|createQuery\s*\(\s*\".*\+"
"nativeQuery\s*=\s*true"

# Go GORM
"\.Raw\s*\(\s*\".*\+|\.Raw\s*\(\s*fmt\.Sprintf|\.Exec\s*\(\s*\".*\+"
```

### Language Examples

**Python (Django) -- Vulnerable**:
```python
def search(request):
    query = request.GET.get("q")
    results = User.objects.raw(f"SELECT * FROM auth_user WHERE username LIKE '%{query}%'")
    return render(request, "results.html", {"results": results})
```

**Python (Django) -- Fixed**:
```python
def search(request):
    query = request.GET.get("q")
    results = User.objects.filter(username__icontains=query)
    return render(request, "results.html", {"results": results})
```

**JavaScript/TypeScript (Sequelize) -- Vulnerable**:
```javascript
app.get("/search", async (req, res) => {
  const results = await sequelize.query(
    `SELECT * FROM users WHERE name LIKE '%${req.query.q}%'`
  );
  res.json(results);
});
```

**JavaScript/TypeScript (Sequelize) -- Fixed**:
```javascript
app.get("/search", async (req, res) => {
  const results = await User.findAll({
    where: { name: { [Op.iLike]: `%${req.query.q}%` } }
  });
  res.json(results);
});
```

**Java (JPA) -- Vulnerable**:
```java
public List<User> search(String name) {
    String jpql = "SELECT u FROM User u WHERE u.name LIKE '%" + name + "%'";
    return em.createQuery(jpql, User.class).getResultList();
}
```

**Java (JPA) -- Fixed**:
```java
public List<User> search(String name) {
    return em.createQuery("SELECT u FROM User u WHERE u.name LIKE :name", User.class)
             .setParameter("name", "%" + name + "%")
             .getResultList();
}
```

**Go (GORM) -- Vulnerable**:
```go
func search(db *gorm.DB, name string) ([]User, error) {
    var users []User
    db.Raw(fmt.Sprintf("SELECT * FROM users WHERE name LIKE '%%%s%%'", name)).Scan(&users)
    return users, nil
}
```

**Go (GORM) -- Fixed**:
```go
func search(db *gorm.DB, name string) ([]User, error) {
    var users []User
    db.Where("name LIKE ?", "%"+name+"%").Find(&users)
    return users, nil
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Yes | `python.django.security.injection.sql.sql-injection-using-raw`, `javascript.sequelize.security.audit.raw-query` |
| bandit | Partial (Python) | `B608` catches some raw query patterns |
| brakeman | Yes (Rails) | SQL Injection in ActiveRecord |

### False Positive Guidance

- **Parameterized raw queries**: `Model.objects.raw("SELECT * FROM t WHERE id = %s", [id])`
  is safe. Check if the raw query uses parameter placeholders with a separate args list.
- **Schema migrations**: Raw SQL in migration files is typically not user-facing.
  Flag as `low` unless the migration dynamically constructs SQL from runtime data.
- **Admin-only endpoints**: Raw queries in admin-only tools with proper
  authentication are lower risk but should still be flagged.

### Severity Criteria

- **critical**: Raw ORM query in a public-facing endpoint with user input.
- **high**: Raw ORM query in an authenticated endpoint with user input.
- **medium**: Raw ORM query with parameterized placeholders but using
  string construction for table/column names.

---

## Pattern 4: OS Command Injection via system/exec/subprocess

### Description

User input is passed to operating system command execution functions, allowing
an attacker to inject additional commands using shell metacharacters (`;`, `|`,
`&&`, `$()`, backticks).

### Grep Search Heuristics

```
# Python
"os\.system\s*\(|os\.popen\s*\("
"subprocess\.(call|run|Popen|check_output|check_call)\s*\(.*shell\s*=\s*True"
"commands\.getoutput\s*\("

# JavaScript/TypeScript
"child_process\.(exec|execSync|spawn|spawnSync)\s*\("
"require\s*\(\s*[\"']child_process[\"']\s*\)"
"exec\s*\(\s*`|exec\s*\(\s*[\"'].*\+"

# Java
"Runtime\.getRuntime\s*\(\s*\)\.exec\s*\("
"ProcessBuilder\s*\(\s*.*\+|ProcessBuilder\s*\("

# Go
"exec\.Command\s*\(\s*\"(sh|bash|cmd)\"|exec\.Command\s*\(.*\+|exec\.CommandContext"
"os\.StartProcess\s*\("
```

### Language Examples

**Python -- Vulnerable**:
```python
def ping_host(host):
    os.system("ping -c 4 " + host)
```

**Python -- Fixed**:
```python
def ping_host(host):
    # Validate input
    if not re.match(r'^[a-zA-Z0-9.\-]+$', host):
        raise ValueError("Invalid hostname")
    subprocess.run(["ping", "-c", "4", host], check=True)
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
app.get("/lookup", (req, res) => {
  const { domain } = req.query;
  exec(`nslookup ${domain}`, (err, stdout) => {
    res.send(stdout);
  });
});
```

**JavaScript/TypeScript -- Fixed**:
```javascript
app.get("/lookup", (req, res) => {
  const { domain } = req.query;
  if (!/^[a-zA-Z0-9.\-]+$/.test(domain)) {
    return res.status(400).send("Invalid domain");
  }
  execFile("nslookup", [domain], (err, stdout) => {
    res.send(stdout);
  });
});
```

**Java -- Vulnerable**:
```java
public String runDiagnostic(String host) {
    Process p = Runtime.getRuntime().exec("ping -c 4 " + host);
    return readStream(p.getInputStream());
}
```

**Java -- Fixed**:
```java
public String runDiagnostic(String host) {
    if (!host.matches("[a-zA-Z0-9.\\-]+")) {
        throw new IllegalArgumentException("Invalid hostname");
    }
    ProcessBuilder pb = new ProcessBuilder("ping", "-c", "4", host);
    Process p = pb.start();
    return readStream(p.getInputStream());
}
```

**Go -- Vulnerable**:
```go
func pingHost(host string) (string, error) {
    cmd := exec.Command("sh", "-c", "ping -c 4 "+host)
    out, err := cmd.Output()
    return string(out), err
}
```

**Go -- Fixed**:
```go
func pingHost(host string) (string, error) {
    matched, _ := regexp.MatchString(`^[a-zA-Z0-9.\-]+$`, host)
    if !matched {
        return "", fmt.Errorf("invalid hostname")
    }
    cmd := exec.Command("ping", "-c", "4", host)
    out, err := cmd.Output()
    return string(out), err
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Yes | `*.lang.security.audit.dangerous-exec-cmd`, `*.lang.security.injection.command` |
| bandit | Yes (Python) | `B605` (start_process_with_a_shell), `B602` (subprocess_popen_with_shell_equals_true) |
| gosec | Yes (Go) | `G204` (subprocess launched with variable) |
| brakeman | Yes (Rails) | Command Injection warning |

### False Positive Guidance

- **Array form (no shell)**: `subprocess.run(["ping", "-c", "4", host])` without
  `shell=True` does not invoke a shell, so metacharacters are not interpreted.
  Still validate input but severity is lower.
- **Hardcoded commands**: `os.system("echo hello")` with no dynamic input is safe.
- **Allowlisted input**: If the variable is validated against a strict allowlist
  before use, the risk is mitigated. Verify the allowlist is actually strict.

### Severity Criteria

- **critical**: User input passed to shell command with no validation. Enables
  remote code execution.
- **high**: User input passed to command execution with partial validation that
  could be bypassed.
- **medium**: Command execution uses array form (no shell) but still
  incorporates user input without validation.

---

## Pattern 5: eval/exec with User Input

### Description

Dynamic code evaluation functions (`eval()`, `exec()`, `new Function()`) are
called with data that could originate from user input. This allows arbitrary
code execution in the application's runtime environment.

### Grep Search Heuristics

```
# Python
"eval\s*\(\s*(request|req|input|data|params|args|body|payload)"
"exec\s*\(\s*(request|req|input|data|params|args|body|payload)"
"compile\s*\(.*exec|compile\s*\(.*eval"

# JavaScript/TypeScript
"eval\s*\("
"new\s+Function\s*\("
"setTimeout\s*\(\s*[\"'`]|setInterval\s*\(\s*[\"'`]"
"vm\.(runInNewContext|runInThisContext|runInContext)\s*\("

# Java
"ScriptEngine.*eval\s*\("
"javax\.script.*eval\s*\("
"GroovyShell.*evaluate\s*\("

# Go (less common, but template injection)
"template\.(Must\s*\(\s*)?New\s*\(.*Parse\s*\("
```

### Language Examples

**Python -- Vulnerable**:
```python
@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.form.get("expr")
    result = eval(expression)
    return jsonify({"result": result})
```

**Python -- Fixed**:
```python
import ast

@app.route("/calculate", methods=["POST"])
def calculate():
    expression = request.form.get("expr")
    # Use ast.literal_eval for safe evaluation of literals only
    try:
        result = ast.literal_eval(expression)
    except (ValueError, SyntaxError):
        return jsonify({"error": "Invalid expression"}), 400
    return jsonify({"result": result})
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
app.post("/run", (req, res) => {
  const code = req.body.code;
  const result = eval(code);
  res.json({ result });
});
```

**JavaScript/TypeScript -- Fixed**:
```javascript
// Use a safe expression parser instead of eval
import { evaluate } from "mathjs";

app.post("/run", (req, res) => {
  try {
    const result = evaluate(req.body.expression);
    res.json({ result });
  } catch (err) {
    res.status(400).json({ error: "Invalid expression" });
  }
});
```

**Java -- Vulnerable**:
```java
@PostMapping("/eval")
public ResponseEntity<String> evaluate(@RequestBody String script) {
    ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");
    Object result = engine.eval(script);
    return ResponseEntity.ok(result.toString());
}
```

**Java -- Fixed**:
```java
// Avoid script evaluation entirely. If required, use a sandboxed evaluator
// with strict allowlisting of permitted operations.
@PostMapping("/eval")
public ResponseEntity<String> evaluate(@RequestBody MathRequest request) {
    double result = safeMathEvaluator.evaluate(request.getExpression());
    return ResponseEntity.ok(String.valueOf(result));
}
```

**Go -- Vulnerable**:
```go
func renderTemplate(w http.ResponseWriter, r *http.Request) {
    userTemplate := r.FormValue("template")
    t, _ := template.New("page").Parse(userTemplate)
    t.Execute(w, data)
}
```

**Go -- Fixed**:
```go
func renderTemplate(w http.ResponseWriter, r *http.Request) {
    // Use predefined templates, never parse user input as a template
    t := templates.Lookup("page")
    if t == nil {
        http.Error(w, "Template not found", 404)
        return
    }
    t.Execute(w, data)
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Yes | `*.lang.security.audit.eval-detected`, `*.lang.security.injection.code` |
| bandit | Yes (Python) | `B307` (eval), `B102` (exec_used) |
| gosec | Partial (Go) | Template injection patterns |

### False Positive Guidance

- **eval() on constants**: `eval("2 + 2")` with a hardcoded literal is safe
  but still a code smell. Flag as `low`.
- **Development/test code**: eval in test fixtures or REPL tooling is lower risk.
  Check the file path and context.
- **Safe alternatives in use**: `ast.literal_eval()` in Python is safe for
  evaluating literal expressions. Do not flag as injection.

### Severity Criteria

- **critical**: User input flows directly into eval/exec. Enables full RCE.
- **high**: User input flows into eval/exec after partial sanitization that
  could be bypassed.
- **medium**: eval/exec is used but input source is indirect or constrained.
- **low**: eval/exec on hardcoded strings or in test code.

---

## Pattern 6: LDAP Query String Construction

### Description

User input is interpolated into LDAP search filters without proper escaping,
allowing an attacker to modify the filter logic. This can lead to unauthorized
data access or authentication bypass.

### Grep Search Heuristics

```
# Python (ldap3, python-ldap)
"search\w*\s*\(.*\(\s*[\"'].*\+|search_s\s*\(.*\(\s*f\""
"ldap.*filter.*\+|ldap.*filter.*format|ldap.*filter.*f\""

# JavaScript/TypeScript (ldapjs)
"search\s*\(\s*\{.*filter.*\+|search\s*\(\s*\{.*filter.*\$\{"
"ldap.*filter.*\+|ldap.*filter.*`"

# Java (JNDI, Spring LDAP)
"search\s*\(.*\"\\(.*\+|DirContext.*search.*\+|LdapTemplate.*search"
"NamingEnumeration.*search\s*\("

# General
"\(uid=.*\+|\(cn=.*\+|\(mail=.*\+|\(sAMAccountName=.*\+"
"\(&\(.*=.*\+|\(\|.*=.*\+"
```

### Language Examples

**Python -- Vulnerable**:
```python
def authenticate(username, password):
    search_filter = "(uid=" + username + ")"
    conn.search("dc=example,dc=com", search_filter)
    if conn.entries:
        user_dn = conn.entries[0].entry_dn
        return conn.rebind(user_dn, password)
    return False
```

**Python -- Fixed**:
```python
from ldap3.utils.conv import escape_filter_chars

def authenticate(username, password):
    safe_username = escape_filter_chars(username)
    search_filter = f"(uid={safe_username})"
    conn.search("dc=example,dc=com", search_filter)
    if conn.entries:
        user_dn = conn.entries[0].entry_dn
        return conn.rebind(user_dn, password)
    return False
```

**JavaScript/TypeScript -- Vulnerable**:
```javascript
async function findUser(username) {
  const filter = `(uid=${username})`;
  const result = await ldapClient.search("dc=example,dc=com", { filter });
  return result.searchEntries[0];
}
```

**JavaScript/TypeScript -- Fixed**:
```javascript
import { EqualityFilter } from "ldapjs";

async function findUser(username) {
  const filter = new EqualityFilter({ attribute: "uid", value: username });
  const result = await ldapClient.search("dc=example,dc=com", { filter });
  return result.searchEntries[0];
}
```

**Java -- Vulnerable**:
```java
public User findUser(String username) {
    String filter = "(uid=" + username + ")";
    NamingEnumeration<?> results = ctx.search("dc=example,dc=com", filter, controls);
    return mapUser(results);
}
```

**Java -- Fixed**:
```java
import javax.naming.ldap.LdapName;

public User findUser(String username) {
    // Use Spring LDAP's LdapQueryBuilder for safe filter construction
    String safeUsername = LdapEncoder.filterEncode(username);
    String filter = "(uid=" + safeUsername + ")";
    NamingEnumeration<?> results = ctx.search("dc=example,dc=com", filter, controls);
    return mapUser(results);
}
```

**Go -- Vulnerable**:
```go
func findUser(conn *ldap.Conn, username string) (*ldap.Entry, error) {
    filter := "(uid=" + username + ")"
    req := ldap.NewSearchRequest("dc=example,dc=com", ldap.ScopeWholeSubtree,
        ldap.NeverDerefAliases, 0, 0, false, filter, []string{"*"}, nil)
    sr, err := conn.Search(req)
    return sr.Entries[0], err
}
```

**Go -- Fixed**:
```go
func findUser(conn *ldap.Conn, username string) (*ldap.Entry, error) {
    filter := fmt.Sprintf("(uid=%s)", ldap.EscapeFilter(username))
    req := ldap.NewSearchRequest("dc=example,dc=com", ldap.ScopeWholeSubtree,
        ldap.NeverDerefAliases, 0, 0, false, filter, []string{"*"}, nil)
    sr, err := conn.Search(req)
    return sr.Entries[0], err
}
```

### Scanner Coverage

| Scanner | Detects This Pattern | Rule ID |
|---------|---------------------|---------|
| semgrep | Yes | `*.lang.security.injection.ldap` |
| bandit | No (no LDAP-specific rules) | -- |
| spotbugs | Yes (Java, with Find Security Bugs) | `LDAP_INJECTION` |

### False Positive Guidance

- **Escaped input**: If the code uses `ldap.EscapeFilter()`, `escape_filter_chars()`,
  `LdapEncoder.filterEncode()`, or equivalent before interpolation, the pattern
  is safe. Verify the escaping function is actually called on the user input.
- **Internal-only filters**: LDAP queries constructed from internal system data
  (e.g., group names from config) are lower risk. Still recommend escaping.
- **Read-only LDAP**: If the LDAP connection is read-only and the directory
  contains no sensitive data, impact is reduced but the vulnerability remains.

### Severity Criteria

- **critical**: LDAP filter injection in an authentication path. Attacker can
  bypass login (e.g., `*)(uid=*))(|(uid=*` returns all users).
- **high**: LDAP filter injection in a search/lookup function. Attacker can
  enumerate directory entries or access unauthorized data.
- **medium**: LDAP filter injection in an internal/admin-only endpoint.
