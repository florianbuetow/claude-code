# Business Logic Detection Patterns

Patterns for detecting business logic vulnerabilities including workflow bypass,
numeric manipulation, coupon abuse, and state machine flaws.

---

## 1. Workflow Step Bypass

**Description**: Multi-step processes (checkout, KYC verification, approval
chains) expose individual step endpoints without verifying that all prior steps
have been completed. An attacker can skip validation, payment, or approval
by calling a later step directly.

**Search Heuristics**:
- Grep: `step|stage|phase|wizard` in route or handler names
- Grep: `checkout|verify|confirm|approve|submit|finalize` endpoint definitions
- Grep: `status.*==.*['"]completed['"]|step.*>=` (step validation checks)
- Grep: `session\[['"]step|req\.session\.step|workflow_state` (step tracking)
- Glob: `**/checkout/**`, `**/workflows/**`, `**/onboarding/**`, `**/verification/**`

**Language Examples**:

Python (Flask) -- VULNERABLE:
```python
@app.route('/checkout/payment', methods=['POST'])
@login_required
def process_payment():
    # No check that cart was validated or address was confirmed
    amount = request.json['amount']  # Client-supplied amount!
    charge_card(request.user, amount)
    create_order(request.user)
    return jsonify({"status": "success"})
```

Python (Flask) -- FIXED:
```python
@app.route('/checkout/payment', methods=['POST'])
@login_required
def process_payment():
    checkout = Checkout.objects.get(user=request.user, status='address_confirmed')
    if not checkout:
        return jsonify({"error": "Complete previous steps first"}), 400
    amount = checkout.calculated_total  # Server-calculated, not client-supplied
    charge_card(request.user, amount)
    checkout.status = 'paid'
    checkout.save()
    return jsonify({"status": "success"})
```

JavaScript (Express) -- VULNERABLE:
```javascript
router.post('/api/checkout/complete', authenticate, async (req, res) => {
  // Directly completes order -- no step validation
  const order = await Order.create({
    userId: req.user.id,
    items: req.body.items,
    total: req.body.total,  // Client-supplied total
  });
  res.json({ orderId: order.id });
});
```

JavaScript (Express) -- FIXED:
```javascript
router.post('/api/checkout/complete', authenticate, async (req, res) => {
  const checkout = await Checkout.findOne({
    userId: req.user.id,
    status: 'payment_confirmed',
  });
  if (!checkout) return res.status(400).json({ error: 'Complete previous steps' });
  const order = await Order.create({
    userId: req.user.id,
    items: checkout.items,
    total: checkout.calculatedTotal,  // Server-calculated
  });
  checkout.status = 'completed';
  await checkout.save();
  res.json({ orderId: order.id });
});
```

Java (Spring) -- VULNERABLE:
```java
@PostMapping("/api/loan/disburse")
public ResponseEntity<?> disburseLoan(@RequestBody DisbursementRequest req) {
    // No check that credit check, KYC, and approval were completed
    accountService.disburse(req.getLoanId(), req.getAmount());
    return ResponseEntity.ok().build();
}
```

Java (Spring) -- FIXED:
```java
@PostMapping("/api/loan/disburse")
public ResponseEntity<?> disburseLoan(@RequestBody DisbursementRequest req) {
    Loan loan = loanRepository.findById(req.getLoanId()).orElseThrow();
    if (loan.getStatus() != LoanStatus.APPROVED) {
        return ResponseEntity.badRequest().body("Loan not yet approved");
    }
    accountService.disburse(loan.getId(), loan.getApprovedAmount());
    loan.setStatus(LoanStatus.DISBURSED);
    loanRepository.save(loan);
    return ResponseEntity.ok().build();
}
```

Go -- VULNERABLE:
```go
func CompleteCheckout(w http.ResponseWriter, r *http.Request) {
    var req CheckoutRequest
    json.NewDecoder(r.Body).Decode(&req)
    // No workflow validation -- jumps straight to completion
    createOrder(req.UserID, req.Items, req.Total)
}
```

Go -- FIXED:
```go
func CompleteCheckout(w http.ResponseWriter, r *http.Request) {
    userID := auth.UserFromContext(r.Context()).ID
    checkout, err := getCheckout(userID, "payment_confirmed")
    if err != nil {
        http.Error(w, "Complete previous steps", http.StatusBadRequest)
        return
    }
    createOrder(userID, checkout.Items, checkout.CalculatedTotal)
    updateCheckoutStatus(checkout.ID, "completed")
}
```

**Scanner Coverage**: No direct scanner rule. Business logic flow analysis
requires manual code review.

**False Positive Guidance**: Independent endpoints that do not have prerequisite
steps are not workflow bypasses. Idempotent re-submission of a completed step
is acceptable behavior, not a bypass.

**Severity Assessment**:
- **critical**: Bypassing payment, identity verification, or approval steps
- **high**: Skipping validation steps that affect order integrity
- **medium**: Bypassing non-critical steps (e.g., optional profile completion)

---

## 2. Negative Amount Manipulation

**Description**: The application accepts numeric inputs (amounts, quantities,
prices) without validating the sign. Negative amounts in payment operations
can reverse charges (crediting instead of debiting), and negative quantities
can produce negative totals or exploit inventory systems.

**Search Heuristics**:
- Grep: `amount|price|quantity|total|credits` in request body parsing
- Grep: `req\.body\.amount|request\.json\[['"]amount|params\.get\(['"]amount`
- Grep: `> 0|>= 0|positive|abs\(` near amount validation (safe patterns)
- Grep: `charge|debit|credit|transfer|withdraw` function calls with client input
- Glob: `**/payments/**`, `**/checkout/**`, `**/cart/**`, `**/transactions/**`

**Language Examples**:

Python -- VULNERABLE:
```python
@app.route('/api/transfer', methods=['POST'])
@login_required
def transfer():
    amount = float(request.json['amount'])
    # No sign check -- negative amount reverses the transfer
    sender = Account.objects.get(user=request.user)
    receiver = Account.objects.get(id=request.json['to_account'])
    sender.balance -= amount   # Negative amount ADDS to sender
    receiver.balance += amount  # Negative amount DEDUCTS from receiver
    sender.save()
    receiver.save()
```

Python -- FIXED:
```python
@app.route('/api/transfer', methods=['POST'])
@login_required
def transfer():
    amount = float(request.json['amount'])
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
    if amount > 10000:
        return jsonify({"error": "Amount exceeds maximum"}), 400
    # ... proceed with transfer
```

JavaScript -- VULNERABLE:
```javascript
router.post('/api/cart/add', authenticate, async (req, res) => {
  const { productId, quantity } = req.body;
  // No validation -- negative quantity reduces total
  const product = await Product.findById(productId);
  const lineTotal = product.price * quantity;  // Can be negative
  await Cart.addItem(req.user.id, productId, quantity, lineTotal);
  res.json({ status: 'added' });
});
```

JavaScript -- FIXED:
```javascript
router.post('/api/cart/add', authenticate, async (req, res) => {
  const { productId, quantity } = req.body;
  if (!Number.isInteger(quantity) || quantity < 1 || quantity > 99) {
    return res.status(400).json({ error: 'Invalid quantity' });
  }
  const product = await Product.findById(productId);
  const lineTotal = product.price * quantity;  // Always positive
  await Cart.addItem(req.user.id, productId, quantity, lineTotal);
  res.json({ status: 'added' });
});
```

Java -- VULNERABLE:
```java
@PostMapping("/api/wallet/deposit")
public ResponseEntity<?> deposit(@RequestBody DepositRequest req) {
    BigDecimal amount = req.getAmount();
    // No validation -- negative deposit is a withdrawal
    walletService.credit(req.getUserId(), amount);
    return ResponseEntity.ok().build();
}
```

Java -- FIXED:
```java
@PostMapping("/api/wallet/deposit")
public ResponseEntity<?> deposit(@RequestBody @Valid DepositRequest req) {
    // DepositRequest has: @DecimalMin(value = "0.01") BigDecimal amount;
    walletService.credit(req.getUserId(), req.getAmount());
    return ResponseEntity.ok().build();
}
```

Go -- VULNERABLE:
```go
func Transfer(w http.ResponseWriter, r *http.Request) {
    var req TransferRequest
    json.NewDecoder(r.Body).Decode(&req)
    // No sign validation
    debit(req.FromAccount, req.Amount)
    credit(req.ToAccount, req.Amount)
}
```

Go -- FIXED:
```go
func Transfer(w http.ResponseWriter, r *http.Request) {
    var req TransferRequest
    json.NewDecoder(r.Body).Decode(&req)
    if req.Amount <= 0 {
        http.Error(w, "Amount must be positive", http.StatusBadRequest)
        return
    }
    if req.Amount > 10000 {
        http.Error(w, "Amount exceeds maximum", http.StatusBadRequest)
        return
    }
    debit(req.FromAccount, req.Amount)
    credit(req.ToAccount, req.Amount)
}
```

**Scanner Coverage**: semgrep `generic.security.negative-amount-validation`

**False Positive Guidance**: Functions that intentionally handle both positive
and negative amounts (e.g., accounting adjustments, refund processing) are not
vulnerabilities. Check whether the sign has legitimate use in the business
context.

**Severity Assessment**:
- **critical**: Negative amounts in payment/transfer enabling money creation
- **high**: Negative quantities producing negative order totals
- **medium**: Negative amounts in non-financial contexts (points, credits)
- **low**: Missing sign validation where impact is cosmetic

---

## 3. Coupon/Discount Abuse

**Description**: Discount and coupon logic allows codes to be applied multiple
times, stacked beyond intended limits, used after expiration, or applied to
ineligible items. These flaws enable attackers to reduce prices to zero or
below.

**Search Heuristics**:
- Grep: `coupon|discount|promo|voucher` in model and handler code
- Grep: `apply_coupon|applyCoupon|applyDiscount|addPromoCode`
- Grep: `used_count|usage_count|max_uses|single_use` (usage limit fields)
- Grep: `expires_at|expiry|valid_until` (expiration validation)
- Glob: `**/coupons/**`, `**/discounts/**`, `**/promotions/**`, `**/checkout/**`

**Language Examples**:

Python -- VULNERABLE:
```python
@app.route('/api/cart/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    code = request.json['code']
    coupon = Coupon.objects.get(code=code)
    # No check: already applied? expired? usage limit reached?
    cart = Cart.objects.get(user=request.user)
    cart.discount += coupon.discount_amount  # Can stack infinitely
    cart.save()
    return jsonify({"discount": cart.discount})
```

Python -- FIXED:
```python
@app.route('/api/cart/apply-coupon', methods=['POST'])
@login_required
def apply_coupon():
    code = request.json['code']
    coupon = Coupon.objects.get(code=code)
    cart = Cart.objects.get(user=request.user)

    if coupon.expires_at < datetime.utcnow():
        return jsonify({"error": "Coupon expired"}), 400
    if coupon.used_count >= coupon.max_uses:
        return jsonify({"error": "Coupon usage limit reached"}), 400
    if cart.applied_coupons.filter(id=coupon.id).exists():
        return jsonify({"error": "Coupon already applied"}), 400
    if cart.applied_coupons.count() >= 1:
        return jsonify({"error": "Only one coupon per order"}), 400

    cart.applied_coupons.add(coupon)
    cart.discount = min(coupon.discount_amount, cart.subtotal)  # Cap at subtotal
    cart.save()
    coupon.used_count += 1
    coupon.save()
    return jsonify({"discount": cart.discount})
```

JavaScript -- VULNERABLE:
```javascript
router.post('/api/cart/coupon', authenticate, async (req, res) => {
  const coupon = await Coupon.findOne({ code: req.body.code });
  const cart = await Cart.findOne({ userId: req.user.id });
  cart.discount = coupon.discountPercent;  // No stacking check, no validation
  await cart.save();
  res.json({ discount: cart.discount });
});
```

JavaScript -- FIXED:
```javascript
router.post('/api/cart/coupon', authenticate, async (req, res) => {
  const coupon = await Coupon.findOne({ code: req.body.code });
  if (!coupon || coupon.expiresAt < new Date()) {
    return res.status(400).json({ error: 'Invalid or expired coupon' });
  }
  if (coupon.usedCount >= coupon.maxUses) {
    return res.status(400).json({ error: 'Coupon limit reached' });
  }
  const cart = await Cart.findOne({ userId: req.user.id });
  if (cart.couponId) {
    return res.status(400).json({ error: 'Coupon already applied' });
  }
  cart.couponId = coupon._id;
  cart.discount = Math.min(
    cart.subtotal * (coupon.discountPercent / 100),
    cart.subtotal
  );
  await cart.save();
  await Coupon.updateOne({ _id: coupon._id }, { $inc: { usedCount: 1 } });
  res.json({ discount: cart.discount });
});
```

Java -- VULNERABLE:
```java
@PostMapping("/api/cart/coupon")
public CartDTO applyCoupon(@RequestBody CouponRequest req) {
    Coupon coupon = couponRepo.findByCode(req.getCode());
    Cart cart = cartRepo.findByUserId(getCurrentUser().getId());
    cart.setDiscount(cart.getDiscount() + coupon.getAmount());  // Stacking!
    return cartMapper.toDTO(cartRepo.save(cart));
}
```

Java -- FIXED:
```java
@PostMapping("/api/cart/coupon")
public CartDTO applyCoupon(@RequestBody CouponRequest req) {
    Coupon coupon = couponRepo.findByCode(req.getCode());
    if (coupon == null || coupon.getExpiresAt().isBefore(Instant.now())) {
        throw new BadRequestException("Invalid or expired coupon");
    }
    Cart cart = cartRepo.findByUserId(getCurrentUser().getId());
    if (cart.getCouponId() != null) {
        throw new BadRequestException("Coupon already applied");
    }
    BigDecimal discount = coupon.getAmount().min(cart.getSubtotal());
    cart.setCouponId(coupon.getId());
    cart.setDiscount(discount);
    return cartMapper.toDTO(cartRepo.save(cart));
}
```

**Scanner Coverage**: No direct scanner rule. Requires business logic analysis.

**False Positive Guidance**: Intentional stacking (e.g., loyalty + promotional
discount) is a business decision, not a vulnerability. Verify the stacking
behavior against the intended business rules. Admin-applied discounts may
intentionally bypass limits.

**Severity Assessment**:
- **critical**: Unlimited discount stacking reducing total to zero or negative
- **high**: Coupon reuse after single-use intent, bypassing expiration
- **medium**: Applying coupons to ineligible items or categories
- **low**: Minor stacking beyond intended limits with capped discount

---

## 4. Self-Referral Exploitation

**Description**: Referral and reward systems do not prevent users from referring
themselves (using different emails, or directly calling the API with their own
referral code). This enables unlimited reward farming.

**Search Heuristics**:
- Grep: `referral|refer|invite|reward|bonus` in handler and model code
- Grep: `referral_code|referredBy|invitedBy|invite_code`
- Grep: `referrer.*==.*referee|self.*refer` (self-referral checks)
- Glob: `**/referrals/**`, `**/rewards/**`, `**/invites/**`

**Language Examples**:

Python -- VULNERABLE:
```python
@app.route('/api/referral/claim', methods=['POST'])
@login_required
def claim_referral():
    code = request.json['referral_code']
    referrer = User.objects.get(referral_code=code)
    # No check: is referrer the same user? Same IP? Same payment method?
    referrer.credits += 10
    request.user.credits += 5
    referrer.save()
    request.user.save()
    return jsonify({"status": "claimed"})
```

Python -- FIXED:
```python
@app.route('/api/referral/claim', methods=['POST'])
@login_required
def claim_referral():
    code = request.json['referral_code']
    referrer = User.objects.get(referral_code=code)

    if referrer.id == request.user.id:
        return jsonify({"error": "Cannot refer yourself"}), 400
    if Referral.objects.filter(referee=request.user).exists():
        return jsonify({"error": "Already claimed a referral"}), 400
    if referrer.email.split('@')[1] == request.user.email.split('@')[1]:
        # Flag for manual review if same email domain
        flag_for_review(referrer, request.user)

    Referral.objects.create(referrer=referrer, referee=request.user)
    referrer.credits += 10
    request.user.credits += 5
    referrer.save()
    request.user.save()
    return jsonify({"status": "claimed"})
```

JavaScript -- VULNERABLE:
```javascript
router.post('/api/referral', authenticate, async (req, res) => {
  const referrer = await User.findOne({ referralCode: req.body.code });
  // No self-referral check, no duplicate check
  referrer.credits += 10;
  await referrer.save();
  req.user.credits += 5;
  await req.user.save();
  res.json({ status: 'claimed' });
});
```

JavaScript -- FIXED:
```javascript
router.post('/api/referral', authenticate, async (req, res) => {
  const referrer = await User.findOne({ referralCode: req.body.code });
  if (referrer._id.equals(req.user._id)) {
    return res.status(400).json({ error: 'Cannot refer yourself' });
  }
  const existing = await Referral.findOne({ refereeId: req.user._id });
  if (existing) {
    return res.status(400).json({ error: 'Already used a referral' });
  }
  await Referral.create({ referrerId: referrer._id, refereeId: req.user._id });
  await User.updateOne({ _id: referrer._id }, { $inc: { credits: 10 } });
  await User.updateOne({ _id: req.user._id }, { $inc: { credits: 5 } });
  res.json({ status: 'claimed' });
});
```

Java -- VULNERABLE:
```java
@PostMapping("/api/referral")
public ResponseEntity<?> claimReferral(@RequestBody ReferralRequest req) {
    User referrer = userRepo.findByReferralCode(req.getCode());
    User referee = getCurrentUser();
    referrer.setCredits(referrer.getCredits() + 10);
    referee.setCredits(referee.getCredits() + 5);
    userRepo.save(referrer);
    userRepo.save(referee);
    return ResponseEntity.ok().build();
}
```

Java -- FIXED:
```java
@PostMapping("/api/referral")
public ResponseEntity<?> claimReferral(@RequestBody ReferralRequest req) {
    User referrer = userRepo.findByReferralCode(req.getCode());
    User referee = getCurrentUser();
    if (referrer.getId().equals(referee.getId())) {
        return ResponseEntity.badRequest().body("Cannot refer yourself");
    }
    if (referralRepo.existsByRefereeId(referee.getId())) {
        return ResponseEntity.badRequest().body("Already claimed");
    }
    referralRepo.save(new Referral(referrer.getId(), referee.getId()));
    referrer.setCredits(referrer.getCredits() + 10);
    referee.setCredits(referee.getCredits() + 5);
    userRepo.save(referrer);
    userRepo.save(referee);
    return ResponseEntity.ok().build();
}
```

**Scanner Coverage**: No direct scanner rule. Requires business logic analysis.

**False Positive Guidance**: Referral systems that intentionally allow
multiple referrals per user (e.g., refer many friends) are not self-referral
abuse -- the concern is referring oneself. Systems with manual review for
high-volume referrers may have mitigating controls.

**Severity Assessment**:
- **high**: Self-referral enabling unlimited reward farming with financial value
- **medium**: Self-referral for non-monetary rewards (features, storage)
- **low**: Self-referral possible but rewards are limited or capped

---

## 5. State Machine Manipulation

**Description**: The application tracks entity states (order status, account
status, approval stage) but does not enforce valid transitions. An attacker
can manipulate the state by calling endpoints that set the status directly,
bypassing required intermediate states.

**Search Heuristics**:
- Grep: `status\s*=\s*['"]|setState|setStatus|update_status` in handlers
- Grep: `VALID_TRANSITIONS|allowed_transitions|transition_map|stateMachine`
- Grep: `(pending|processing|shipped|delivered|cancelled|approved|rejected)` as status values
- Glob: `**/orders/**`, `**/workflows/**`, `**/state/**`, `**/models/**`

**Language Examples**:

Python -- VULNERABLE:
```python
@app.route('/api/orders/<order_id>/status', methods=['PUT'])
@login_required
def update_status(order_id):
    new_status = request.json['status']
    order = Order.objects.get(id=order_id)
    order.status = new_status  # Any status accepted -- can go from "pending" to "delivered"
    order.save()
```

Python -- FIXED:
```python
VALID_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['processing', 'cancelled'],
    'processing': ['shipped', 'cancelled'],
    'shipped': ['delivered'],
    'delivered': [],
    'cancelled': [],
}

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
@login_required
def update_status(order_id):
    new_status = request.json['status']
    order = Order.objects.get(id=order_id)
    if new_status not in VALID_TRANSITIONS.get(order.status, []):
        return jsonify({"error": f"Cannot transition from {order.status} to {new_status}"}), 400
    order.status = new_status
    order.save()
```

JavaScript -- VULNERABLE:
```javascript
router.put('/api/orders/:id/status', authenticate, async (req, res) => {
  await Order.findByIdAndUpdate(req.params.id, { status: req.body.status });
  res.json({ status: 'updated' });
});
```

JavaScript -- FIXED:
```javascript
const VALID_TRANSITIONS = {
  pending: ['confirmed', 'cancelled'],
  confirmed: ['processing', 'cancelled'],
  processing: ['shipped'],
  shipped: ['delivered'],
};

router.put('/api/orders/:id/status', authenticate, async (req, res) => {
  const order = await Order.findById(req.params.id);
  const allowed = VALID_TRANSITIONS[order.status] || [];
  if (!allowed.includes(req.body.status)) {
    return res.status(400).json({ error: 'Invalid status transition' });
  }
  order.status = req.body.status;
  await order.save();
  res.json({ status: 'updated' });
});
```

Java -- VULNERABLE:
```java
@PutMapping("/api/orders/{id}/status")
public Order updateStatus(@PathVariable Long id, @RequestBody StatusUpdate update) {
    Order order = orderRepo.findById(id).orElseThrow();
    order.setStatus(update.getStatus());  // No transition validation
    return orderRepo.save(order);
}
```

Java -- FIXED:
```java
@PutMapping("/api/orders/{id}/status")
public Order updateStatus(@PathVariable Long id, @RequestBody StatusUpdate update) {
    Order order = orderRepo.findById(id).orElseThrow();
    if (!order.canTransitionTo(update.getStatus())) {
        throw new BadRequestException("Invalid state transition");
    }
    order.setStatus(update.getStatus());
    return orderRepo.save(order);
}
```

Go -- VULNERABLE:
```go
func UpdateOrderStatus(w http.ResponseWriter, r *http.Request) {
    var req StatusRequest
    json.NewDecoder(r.Body).Decode(&req)
    db.Model(&Order{}).Where("id = ?", req.OrderID).Update("status", req.Status)
}
```

Go -- FIXED:
```go
var validTransitions = map[string][]string{
    "pending":    {"confirmed", "cancelled"},
    "confirmed":  {"processing", "cancelled"},
    "processing": {"shipped"},
    "shipped":    {"delivered"},
}

func UpdateOrderStatus(w http.ResponseWriter, r *http.Request) {
    var req StatusRequest
    json.NewDecoder(r.Body).Decode(&req)
    var order Order
    db.First(&order, req.OrderID)
    allowed := validTransitions[order.Status]
    if !contains(allowed, req.Status) {
        http.Error(w, "Invalid transition", http.StatusBadRequest)
        return
    }
    db.Model(&order).Update("status", req.Status)
}
```

**Scanner Coverage**: No direct scanner rule. State machine validation requires
business logic analysis.

**False Positive Guidance**: Admin endpoints that allow status overrides for
support purposes may intentionally bypass transitions. Internal system processes
(batch jobs, migration scripts) may set status directly. Check the endpoint's
intended audience.

**Severity Assessment**:
- **critical**: State manipulation bypassing payment or verification steps
- **high**: Skipping required states in fulfillment or approval workflows
- **medium**: Invalid transitions that cause data inconsistency
- **low**: Cosmetic state issues with no business impact

---

## 6. Time-Based Logic Exploits

**Description**: Application logic depends on time comparisons (expiration
checks, promotional windows, trial periods) but uses client-supplied timestamps,
does not handle timezone edge cases, or has race conditions around deadlines.

**Search Heuristics**:
- Grep: `expires_at|valid_until|start_date|end_date|deadline`
- Grep: `new Date\(req\.|datetime\.fromisoformat\(request\.|time\.Parse\(.*req`
- Grep: `Date\.now\(\)|datetime\.utcnow|time\.Now\(\)` near comparison operators
- Grep: `timezone|tz|UTC|localtime` in business logic
- Glob: `**/promotions/**`, `**/subscriptions/**`, `**/trials/**`, `**/auctions/**`

**Language Examples**:

Python -- VULNERABLE:
```python
@app.route('/api/promo/claim', methods=['POST'])
def claim_promo():
    client_time = datetime.fromisoformat(request.json['timestamp'])
    promo = Promo.objects.get(id=request.json['promo_id'])
    if client_time <= promo.expires_at:  # Trusts client timestamp!
        apply_discount(request.user, promo)
```

Python -- FIXED:
```python
@app.route('/api/promo/claim', methods=['POST'])
def claim_promo():
    now = datetime.utcnow()  # Server timestamp only
    promo = Promo.objects.get(id=request.json['promo_id'])
    if now <= promo.expires_at:
        apply_discount(request.user, promo)
    else:
        return jsonify({"error": "Promotion expired"}), 400
```

JavaScript -- VULNERABLE:
```javascript
router.post('/api/auction/bid', authenticate, async (req, res) => {
  const auction = await Auction.findById(req.body.auctionId);
  const bidTime = new Date(req.body.timestamp);  // Client-supplied time
  if (bidTime <= auction.endTime) {
    await placeBid(auction, req.user, req.body.amount);
  }
});
```

JavaScript -- FIXED:
```javascript
router.post('/api/auction/bid', authenticate, async (req, res) => {
  const auction = await Auction.findById(req.body.auctionId);
  if (new Date() > auction.endTime) {  // Server time only
    return res.status(400).json({ error: 'Auction ended' });
  }
  await placeBid(auction, req.user, req.body.amount);
});
```

Java -- VULNERABLE:
```java
@PostMapping("/api/trial/extend")
public ResponseEntity<?> extendTrial(@RequestBody TrialRequest req) {
    Instant clientTime = Instant.parse(req.getTimestamp());  // Client timestamp
    Subscription sub = subRepo.findByUserId(getCurrentUser().getId());
    if (clientTime.isBefore(sub.getTrialEnd())) {
        sub.setTrialEnd(sub.getTrialEnd().plus(7, ChronoUnit.DAYS));
        subRepo.save(sub);
    }
}
```

Java -- FIXED:
```java
@PostMapping("/api/trial/extend")
public ResponseEntity<?> extendTrial() {
    Subscription sub = subRepo.findByUserId(getCurrentUser().getId());
    if (Instant.now().isBefore(sub.getTrialEnd())) {
        sub.setTrialEnd(sub.getTrialEnd().plus(7, ChronoUnit.DAYS));
        subRepo.save(sub);
    } else {
        return ResponseEntity.badRequest().body("Trial already expired");
    }
}
```

Go -- VULNERABLE:
```go
func ClaimOffer(w http.ResponseWriter, r *http.Request) {
    var req OfferRequest
    json.NewDecoder(r.Body).Decode(&req)
    clientTime, _ := time.Parse(time.RFC3339, req.Timestamp)  // Client time
    offer := getOffer(req.OfferID)
    if clientTime.Before(offer.ExpiresAt) {
        applyOffer(req.UserID, offer)
    }
}
```

Go -- FIXED:
```go
func ClaimOffer(w http.ResponseWriter, r *http.Request) {
    var req OfferRequest
    json.NewDecoder(r.Body).Decode(&req)
    offer := getOffer(req.OfferID)
    if time.Now().UTC().Before(offer.ExpiresAt) {  // Server time
        applyOffer(req.UserID, offer)
    } else {
        http.Error(w, "Offer expired", http.StatusBadRequest)
    }
}
```

**Scanner Coverage**: No direct scanner rule. Detected by finding client-supplied
timestamps used in business logic comparisons.

**False Positive Guidance**: Client timestamps used for logging, analytics, or
display purposes (not business decisions) are not vulnerabilities. Timezone
conversion for display is different from timezone exploitation for deadline
bypass.

**Severity Assessment**:
- **critical**: Client timestamp bypassing payment deadlines or auction endings
- **high**: Expired promotion/trial exploitation via timestamp manipulation
- **medium**: Timezone edge cases in deadline enforcement
- **low**: Minor timing discrepancies with no financial impact
