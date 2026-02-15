# Race Conditions Detection Patterns

Patterns for detecting race condition vulnerabilities including TOCTOU,
double-spend, and concurrency flaws.

---

## 1. Time-of-Check to Time-of-Use (TOCTOU) in File Operations

**Description**: The application checks a file property (existence, permissions,
type) and then operates on the file in a separate system call. An attacker can
modify the file between the check and the use, especially in shared directories
like `/tmp`.

**Search Heuristics**:
- Grep: `os\.path\.exists\(.*\).*open\(` (Python file TOCTOU)
- Grep: `fs\.(exists|access)Sync.*fs\.(read|write|unlink)` (Node.js TOCTOU)
- Grep: `File\.(exists|isFile)\(.*\).*new File(Input|Output)Stream` (Java TOCTOU)
- Grep: `os\.Stat\(.*\).*os\.(Open|Create|Remove)` (Go TOCTOU)
- Glob: `**/storage/**`, `**/upload/**`, `**/utils/file*`

**Language Examples**:

Python -- VULNERABLE:
```python
import os
if os.path.exists(filepath):
    with open(filepath, 'r') as f:
        data = f.read()  # File could be replaced between exists() and open()
```

Python -- FIXED:
```python
try:
    with open(filepath, 'r') as f:
        data = f.read()
except FileNotFoundError:
    data = None  # Handle atomically -- no TOCTOU window
```

JavaScript (Node.js) -- VULNERABLE:
```javascript
if (fs.existsSync(filePath)) {
  const data = fs.readFileSync(filePath);  // Race window
}
```

JavaScript (Node.js) -- FIXED:
```javascript
try {
  const data = fs.readFileSync(filePath);
} catch (err) {
  if (err.code === 'ENOENT') { /* handle missing file */ }
}
```

Java -- VULNERABLE:
```java
File file = new File(path);
if (file.exists() && file.isFile()) {
    FileInputStream fis = new FileInputStream(file);  // Race window
}
```

Java -- FIXED:
```java
try (FileInputStream fis = new FileInputStream(path)) {
    // Atomic open -- no check-then-use gap
} catch (FileNotFoundException e) {
    // Handle missing file
}
```

Go -- VULNERABLE:
```go
if _, err := os.Stat(path); err == nil {
    data, _ := os.ReadFile(path)  // Race window between Stat and ReadFile
}
```

Go -- FIXED:
```go
data, err := os.ReadFile(path)
if err != nil {
    if os.IsNotExist(err) { /* handle missing */ }
    return err
}
```

**Scanner Coverage**: semgrep `python.lang.security.audit.toctou`,
bandit `B108` (insecure temp file)

**False Positive Guidance**: TOCTOU in read-only operations on files that only
the application controls (not in shared directories) are low risk. Check
whether the file path includes user input or is in a shared location like `/tmp`.

**Severity Assessment**:
- **high**: TOCTOU on files in shared directories or with user-controlled paths
- **medium**: TOCTOU on application-controlled files with no user path input
- **low**: TOCTOU in non-security-critical read operations

---

## 2. Double-Spend / Check-Then-Debit

**Description**: The application reads a balance or quota, checks whether the
operation is allowed, then performs the debit in separate non-atomic steps.
Concurrent requests can both pass the check before either debit completes,
resulting in double-spending.

**Search Heuristics**:
- Grep: `balance.*>=.*amount` followed by `balance.*-=` or `UPDATE.*SET.*balance`
- Grep: `get_balance|getBalance|check_balance|checkBalance` near `debit|withdraw|charge`
- Grep: `SELECT.*balance.*UPDATE.*balance` without `FOR UPDATE` or `SERIALIZABLE`
- Grep: `credits?\s*[><=]+\s*\d+.*credits?\s*[-+]=`
- Glob: `**/payments/**`, `**/billing/**`, `**/wallet/**`, `**/transactions/**`

**Language Examples**:

Python (Django) -- VULNERABLE:
```python
def withdraw(request, amount):
    account = Account.objects.get(user=request.user)
    if account.balance >= amount:       # Check
        account.balance -= amount       # Act -- race window!
        account.save()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Insufficient funds"}, status=400)
```

Python (Django) -- FIXED:
```python
from django.db import transaction
from django.db.models import F

def withdraw(request, amount):
    with transaction.atomic():
        rows = Account.objects.filter(
            user=request.user, balance__gte=amount
        ).update(balance=F('balance') - amount)  # Atomic check-and-debit
        if rows == 0:
            return JsonResponse({"error": "Insufficient funds"}, status=400)
        return JsonResponse({"status": "ok"})
```

JavaScript (Node.js + SQL) -- VULNERABLE:
```javascript
const account = await db.query('SELECT balance FROM accounts WHERE user_id = $1', [userId]);
if (account.rows[0].balance >= amount) {
  await db.query('UPDATE accounts SET balance = balance - $1 WHERE user_id = $2', [amount, userId]);
}
```

JavaScript (Node.js + SQL) -- FIXED:
```javascript
const result = await db.query(
  'UPDATE accounts SET balance = balance - $1 WHERE user_id = $2 AND balance >= $1 RETURNING balance',
  [amount, userId]
);
if (result.rowCount === 0) throw new Error('Insufficient funds');
```

Java (Spring) -- VULNERABLE:
```java
Account account = accountRepo.findByUserId(userId);
if (account.getBalance().compareTo(amount) >= 0) {
    account.setBalance(account.getBalance().subtract(amount));
    accountRepo.save(account);
}
```

Java (Spring) -- FIXED:
```java
@Transactional
public void withdraw(Long userId, BigDecimal amount) {
    int rows = accountRepo.debitIfSufficient(userId, amount);
    // SQL: UPDATE accounts SET balance = balance - :amount WHERE user_id = :userId AND balance >= :amount
    if (rows == 0) throw new InsufficientFundsException();
}
```

Go -- VULNERABLE:
```go
var balance float64
db.QueryRow("SELECT balance FROM accounts WHERE user_id = $1", userID).Scan(&balance)
if balance >= amount {
    db.Exec("UPDATE accounts SET balance = balance - $1 WHERE user_id = $2", amount, userID)
}
```

Go -- FIXED:
```go
result, err := db.Exec(
    "UPDATE accounts SET balance = balance - $1 WHERE user_id = $2 AND balance >= $1",
    amount, userID)
if rows, _ := result.RowsAffected(); rows == 0 {
    return errors.New("insufficient funds")
}
```

**Scanner Coverage**: No direct scanner rule. Detected through code pattern
analysis of financial operations.

**False Positive Guidance**: Read-only balance checks (displaying balance) are
not double-spend. Operations protected by external distributed locks (Redis,
ZooKeeper) may be safe even without database-level atomicity. Verify the full
transaction context before flagging.

**Severity Assessment**:
- **critical**: Double-spend in payment, withdrawal, or credit operations
- **high**: Race in quota enforcement (API rate limits, resource allocation)
- **medium**: Race in non-financial counters with business impact

---

## 3. Check-Then-Act Without Lock

**Description**: A general pattern where code checks a condition (e.g., "is this
username taken?") and then acts on the assumption the condition still holds. Without
a lock or atomic operation, a concurrent request can invalidate the check.

**Search Heuristics**:
- Grep: `if.*not.*exists.*\n.*create|insert` (check-then-create)
- Grep: `findOne|find_one|SELECT.*WHERE.*INSERT` without transaction
- Grep: `if.*status\s*==.*\n.*status\s*=` (check-then-update-status)
- Grep: `get_or_create|findOrCreate|upsert` (safe alternatives to check-then-create)
- Glob: `**/services/**`, `**/handlers/**`, `**/controllers/**`

**Language Examples**:

Python (Django) -- VULNERABLE:
```python
def register(request, username):
    if not User.objects.filter(username=username).exists():  # Check
        User.objects.create(username=username, ...)           # Act -- race!
```

Python (Django) -- FIXED:
```python
from django.db import IntegrityError

def register(request, username):
    try:
        User.objects.create(username=username, ...)  # Atomic with unique constraint
    except IntegrityError:
        return JsonResponse({"error": "Username taken"}, status=409)
```

JavaScript (Mongoose) -- VULNERABLE:
```javascript
const existing = await User.findOne({ email });
if (!existing) {
  await User.create({ email, ... });  // Race: two requests pass findOne
}
```

JavaScript (Mongoose) -- FIXED:
```javascript
try {
  await User.create({ email, ... });  // Relies on unique index on email
} catch (err) {
  if (err.code === 11000) { /* duplicate key -- handle conflict */ }
}
```

Java -- VULNERABLE:
```java
if (userRepository.findByEmail(email) == null) {
    userRepository.save(new User(email, ...));  // Race window
}
```

Java -- FIXED:
```java
try {
    userRepository.save(new User(email, ...));  // Unique constraint enforces atomicity
} catch (DataIntegrityViolationException e) {
    throw new ConflictException("Email already registered");
}
```

Go -- VULNERABLE:
```go
var count int
db.QueryRow("SELECT COUNT(*) FROM users WHERE email = $1", email).Scan(&count)
if count == 0 {
    db.Exec("INSERT INTO users (email) VALUES ($1)", email)  // Race window
}
```

Go -- FIXED:
```go
_, err := db.Exec("INSERT INTO users (email) VALUES ($1) ON CONFLICT DO NOTHING", email)
```

**Scanner Coverage**: semgrep `generic.toctou.check-then-act`

**False Positive Guidance**: Operations protected by database unique constraints
that properly handle constraint violations are not vulnerable. Check whether the
database schema enforces the invariant even if the application code has a race.

**Severity Assessment**:
- **critical**: Check-then-act on security operations (auth, access grants)
- **high**: Check-then-act on business-critical unique constraints (payments, user registration)
- **medium**: Check-then-act on non-critical data with potential for duplicates

---

## 4. Shared State Across Await Points

**Description**: In async code, mutable state is read before an `await` (or
`yield`) point and assumed to still be valid after the await resumes. During the
suspension, other coroutines or requests can modify the shared state.

**Search Heuristics**:
- Grep: `(let|var|const)\s+\w+\s*=.*await.*\n.*\1` (state read then used after await)
- Grep: `self\.\w+.*=.*\n.*await.*\n.*self\.\w+` (Python instance state across await)
- Grep: `this\.\w+.*await.*this\.\w+` (JS class state across await)
- Glob: `**/services/**`, `**/handlers/**`, `**/controllers/**`

**Language Examples**:

Python (asyncio) -- VULNERABLE:
```python
class OrderService:
    async def process_order(self, order_id):
        self.current_order = await self.db.get_order(order_id)
        await self.validate_inventory()  # Another coroutine can change self.current_order
        await self.charge_payment(self.current_order)  # May operate on wrong order
```

Python (asyncio) -- FIXED:
```python
class OrderService:
    async def process_order(self, order_id):
        order = await self.db.get_order(order_id)  # Local variable, not shared state
        await self.validate_inventory(order)
        await self.charge_payment(order)
```

JavaScript -- VULNERABLE:
```javascript
class CartService {
  async checkout() {
    this.total = await this.calculateTotal();
    await this.applyDiscounts();  // Another request could modify this.total
    await this.chargePayment(this.total);  // Stale value
  }
}
```

JavaScript -- FIXED:
```javascript
class CartService {
  async checkout() {
    const total = await this.calculateTotal();
    const discountedTotal = await this.applyDiscounts(total);
    await this.chargePayment(discountedTotal);  // All local
  }
}
```

Java (CompletableFuture) -- VULNERABLE:
```java
private BigDecimal pendingAmount;

public CompletableFuture<Void> processPayment(String orderId) {
    return getOrder(orderId)
        .thenAccept(order -> this.pendingAmount = order.getTotal())
        .thenCompose(v -> chargeCard(this.pendingAmount));  // Shared mutable field
}
```

Java (CompletableFuture) -- FIXED:
```java
public CompletableFuture<Void> processPayment(String orderId) {
    return getOrder(orderId)
        .thenCompose(order -> chargeCard(order.getTotal()));  // No shared state
}
```

Go -- VULNERABLE:
```go
type Handler struct {
    lastPrice float64
}

func (h *Handler) ProcessOrder(w http.ResponseWriter, r *http.Request) {
    h.lastPrice = fetchPrice(r.Context())  // Shared across goroutines
    // Other goroutine can overwrite h.lastPrice
    charge(h.lastPrice)
}
```

Go -- FIXED:
```go
func (h *Handler) ProcessOrder(w http.ResponseWriter, r *http.Request) {
    price := fetchPrice(r.Context())  // Local to this goroutine
    charge(price)
}
```

**Scanner Coverage**: No direct scanner rule. Requires manual code analysis
of async patterns and shared state.

**False Positive Guidance**: Immutable shared state (constants, configuration
loaded once at startup) is safe. Read-only access to shared state without
mutation is not a race. Single-threaded event loops (Node.js) do not have
true parallel execution, but await points allow interleaving.

**Severity Assessment**:
- **critical**: Shared state across await in payment or authorization logic
- **high**: Shared mutable state in request handlers serving concurrent users
- **medium**: Instance variables mutated across await in non-critical paths

---

## 5. Non-Atomic Read-Modify-Write

**Description**: A value is read, modified in application code, and written back
without atomic guarantees. Concurrent operations can read the same original
value and both write back the same modified value, losing one update.

**Search Heuristics**:
- Grep: `counter\s*[+\-]=\s*1|count\s*=\s*count\s*[+\-]` (non-atomic increment)
- Grep: `UPDATE.*SET.*=.*\+\s*1` without `FOR UPDATE` (SQL increment race)
- Grep: `\.update\(.*\$inc` (MongoDB atomic increment -- safe pattern for reference)
- Grep: `AtomicInteger|atomic\.Add|sync/atomic` (safe patterns to verify usage)
- Glob: `**/counters/**`, `**/analytics/**`, `**/metrics/**`, `**/inventory/**`

**Language Examples**:

Python (Django) -- VULNERABLE:
```python
def increment_view_count(article_id):
    article = Article.objects.get(id=article_id)
    article.views = article.views + 1  # Read-modify-write race
    article.save()
```

Python (Django) -- FIXED:
```python
from django.db.models import F

def increment_view_count(article_id):
    Article.objects.filter(id=article_id).update(views=F('views') + 1)  # Atomic
```

JavaScript (Mongoose) -- VULNERABLE:
```javascript
const product = await Product.findById(id);
product.stock = product.stock - quantity;  // Race: two requests decrement from same value
await product.save();
```

JavaScript (Mongoose) -- FIXED:
```javascript
await Product.findByIdAndUpdate(id, { $inc: { stock: -quantity } });
```

Java -- VULNERABLE:
```java
private int requestCount = 0;

public void handleRequest() {
    requestCount++;  // Not atomic, lost updates under concurrency
}
```

Java -- FIXED:
```java
private final AtomicInteger requestCount = new AtomicInteger(0);

public void handleRequest() {
    requestCount.incrementAndGet();  // Atomic
}
```

Go -- VULNERABLE:
```go
var counter int64

func handleRequest() {
    counter++  // Race condition: not atomic
}
```

Go -- FIXED:
```go
var counter int64

func handleRequest() {
    atomic.AddInt64(&counter, 1)  // Atomic
}
```

**Scanner Coverage**: `go vet -race` detects Go race conditions at build time;
semgrep `go.concurrency.non-atomic-increment`

**False Positive Guidance**: Counters that are only accessed from a single
thread or goroutine are not races. Approximate counters (analytics, metrics)
where occasional lost updates are acceptable may be intentional. Verify whether
accuracy matters for the use case.

**Severity Assessment**:
- **critical**: Non-atomic operations on financial balances or inventory
- **high**: Non-atomic operations on security counters (rate limits, login attempts)
- **medium**: Non-atomic counters for analytics or metrics
- **low**: Non-atomic counters for cosmetic/display purposes

---

## 6. Missing Database Transaction Isolation

**Description**: Financial or state-changing database operations use the default
isolation level (typically READ COMMITTED) when they require SERIALIZABLE or
at least use of `SELECT ... FOR UPDATE` to prevent concurrent modification.

**Search Heuristics**:
- Grep: `BEGIN|transaction\.atomic|@Transactional` without isolation level
- Grep: `SELECT.*FROM.*(account|balance|inventory|stock)` without `FOR UPDATE`
- Grep: `isolation_level|IsolationLevel|SERIALIZABLE|READ_COMMITTED`
- Grep: `set_isolation_level|setTransactionIsolation`
- Glob: `**/repositories/**`, `**/services/**`, `**/dao/**`

**Language Examples**:

Python (Django) -- VULNERABLE:
```python
with transaction.atomic():  # Default READ COMMITTED
    order = Order.objects.get(id=order_id)
    if order.status == 'pending':
        order.status = 'processing'  # Race: two workers process same order
        order.save()
```

Python (Django) -- FIXED:
```python
with transaction.atomic():
    order = Order.objects.select_for_update().get(id=order_id)  # Row lock
    if order.status == 'pending':
        order.status = 'processing'
        order.save()
```

JavaScript (Knex) -- VULNERABLE:
```javascript
await knex.transaction(async (trx) => {
  const order = await trx('orders').where('id', orderId).first();
  if (order.status === 'pending') {
    await trx('orders').where('id', orderId).update({ status: 'processing' });
  }
});
```

JavaScript (Knex) -- FIXED:
```javascript
await knex.transaction(async (trx) => {
  const order = await trx('orders').where('id', orderId).forUpdate().first();
  if (order.status === 'pending') {
    await trx('orders').where('id', orderId).update({ status: 'processing' });
  }
});
```

Java (Spring) -- VULNERABLE:
```java
@Transactional
public void processOrder(Long orderId) {
    Order order = orderRepo.findById(orderId).orElseThrow();
    if (order.getStatus() == Status.PENDING) {
        order.setStatus(Status.PROCESSING);
        orderRepo.save(order);
    }
}
```

Java (Spring) -- FIXED:
```java
@Transactional(isolation = Isolation.SERIALIZABLE)
public void processOrder(Long orderId) {
    Order order = orderRepo.findByIdForUpdate(orderId).orElseThrow();
    // @Query("SELECT o FROM Order o WHERE o.id = :id FOR UPDATE")
    if (order.getStatus() == Status.PENDING) {
        order.setStatus(Status.PROCESSING);
        orderRepo.save(order);
    }
}
```

Go -- VULNERABLE:
```go
tx, _ := db.Begin()
var status string
tx.QueryRow("SELECT status FROM orders WHERE id = $1", orderID).Scan(&status)
if status == "pending" {
    tx.Exec("UPDATE orders SET status = 'processing' WHERE id = $1", orderID)
}
tx.Commit()
```

Go -- FIXED:
```go
tx, _ := db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelSerializable})
var status string
tx.QueryRow("SELECT status FROM orders WHERE id = $1 FOR UPDATE", orderID).Scan(&status)
if status == "pending" {
    tx.Exec("UPDATE orders SET status = 'processing' WHERE id = $1", orderID)
}
tx.Commit()
```

**Scanner Coverage**: No direct scanner rule. Requires analysis of transaction
boundaries and isolation levels.

**False Positive Guidance**: Read-only transactions do not need higher isolation.
Operations on data that is not accessed concurrently (e.g., single-user setup
wizards) are not vulnerable. Idempotent operations are safe even without strict
isolation.

**Severity Assessment**:
- **critical**: Missing isolation on financial transactions (payments, transfers)
- **high**: Missing isolation on order/state machine transitions
- **medium**: Missing isolation on non-critical status updates
- **low**: Default isolation on read-heavy operations with rare writes
