# Unit, Transaction, And Coverage Plan

Goal: make the backend test suite more useful by first fixing transaction boundaries, then adding tests for database behavior, payment state transitions, stock safety, and failure paths.

## Current Coverage Baseline

Command run:

```bash
uv run pytest --cov=app
```

Result:

```text
17 passed
TOTAL 552 statements, 114 missed, 79% coverage
```

Weakest modules:

- `app/notifications/telegram.py`: 43%
- `app/routes.py`: 72%
- `app/payments/yookassa.py`: 78%
- `app/models.py`: 79%
- `app/cart.py`: 82%
- `app/db.py`: 89%

Targets:

- First hardening pass: 85%+ overall coverage.
- After identity/reservation/refund work lands: 90%+ overall coverage.
- `app/models.py` and `app/payments/yookassa.py` should be close to fully covered because they protect money and order state.

Do not chase coverage for its own sake. A small set of tests around transactions, payment matching, and stock safety is more valuable than many shallow template assertions.

## Transaction Work Before Deeper Testing

Do these refactors before writing rollback tests, so tests lock in the intended behavior rather than today’s partial-commit behavior.

### 1. Add A SQLite-Safe Transaction Helper

Add a transaction context manager in `app/db.py`, but make it explicit that nested transactions are not supported unless savepoints are implemented.

Sketch:

```python
@contextmanager
def transaction():
    db = get_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()
```

Rules:

- Use one transaction for one business operation.
- Do not call this helper from inside another transaction.
- Do not call `commit()` inside lower-level helpers that are meant to participate in a bigger operation.
- If nested transactional behavior is later needed, implement savepoints deliberately.

### 2. Refactor Order Creation

Wrap in one transaction:

- insert into `orders`
- insert every `order_items` row
- later: generate public order code/access key
- later: reserve stock

Must roll back the order if any order item insert fails.

Functions affected:

- `models.create_order_from_cart`
- `models.create_order`

`models.create_order` currently appears unused and has a SQL placeholder mismatch: it lists 11 inserted columns but only 10 placeholders. Verify no call sites use it, then either delete it or fix and test it.

### 3. Refactor Paid Transition

Wrap in one transaction:

- verify order exists and is not already paid
- verify stock/reservation state
- decrement/finalize stock exactly once
- update order status/payment status/paid timestamp
- set `stock_decremented_at`

Functions affected:

- `models.decrement_stock_for_paid_order`
- `models.mark_order_paid`
- `routes.apply_yookassa_payment_status`

Avoid nested commits. Prefer one model-level function owning the whole paid transition; route code should call that function and then handle notifications outside the transaction.

### 4. Make Notification Marking Idempotent

Notification sending should stay outside DB transactions. Timestamp marking should be atomic:

- update `telegram_paid_notified_at` only if null
- update `telegram_manual_notified_at` only if null
- return whether the row was actually marked

This protects against duplicate sends from return route + webhook races.

### 5. Add Reservation Transactions

Before real YooKassa production use:

- checkout re-reads stock in transaction
- reserve stock before payment creation
- release reservation on payment creation failure/canceled/expired
- finalize reservation on `payment.succeeded`

These tests matter more than broad route coverage because this is where the store can lose money.

## Database Tests To Add

Create `tests/test_db_schema.py`:

- fresh app creates `products`, `orders`, `order_items`
- migrations add missing product localization columns
- migrations add missing order payment/notification columns
- running `init_db()` twice is idempotent
- database path parent directory is created
- teardown closes DB connection
- if foreign keys are intended, `PRAGMA foreign_keys = ON` is enabled and tested

Create `tests/test_models_orders.py`:

- `create_order_from_cart` stores customer snapshot, total, payment provider/status
- `create_order_from_cart` stores product name and unit price snapshots
- order total is computed from cart line totals, not current product values after mutation
- order item insert failure rolls back the whole order
- update ignores disallowed fields
- update with no allowed fields does not change data
- `get_order_items` returns deterministic order
- obsolete `create_order` is either removed or fixed and covered

Create `tests/test_models_stock.py`:

- stock decrements once on paid transition
- repeated paid transition is idempotent
- insufficient stock moves order to manual review and does not go negative
- missing product in order item fails safely
- already paid order does not alter stock again
- paid timestamp is set once
- simulated failure mid-transition rolls back stock/order changes

Create `tests/test_models_notifications.py`:

- mark paid notification timestamp once
- mark manual notification timestamp once
- duplicate marking returns false/no-op once idempotent update exists
- missing order id does not crash

## Route Tests To Add

Create `tests/test_checkout_routes.py`:

- checkout rejects missing name/email/address with localized errors
- checkout rejects empty cart
- checkout rejects stale cart item when product disappeared
- checkout rejects quantity above stock after stock changed between cart and submit
- manual checkout clears cart only after order is persisted
- payment provider failure records `payment_error` and preserves order

Create `tests/test_payment_routes.py`:

- YooKassa return without `order_id` returns 400 for the legacy route
- YooKassa return for unknown order does not crash
- YooKassa return with missing payment reference does not mark paid
- webhook with invalid JSON returns safe 200/ignored
- webhook with missing metadata returns safe 200/ignored
- webhook with non-integer order id returns ignored
- pending payment updates payment status but does not mark paid
- canceled payment cannot move paid order backward
- succeeded payment with stock failure creates manual review

After public-code tracking lands, add route tests for:

- `/orders/<public_code>` requires session/access key for private data
- `/track` failure does not reveal whether order/email/access key was wrong
- legacy `/orders/<int:id>` no longer leaks private order details

## Payment Provider Tests To Add

Expand `tests/test_yookassa_provider.py`:

- `amount_from_minor_units` formats kopeks/rubles correctly for 0, 1, 1800, and larger values
- create payment sends Basic Auth shop id/secret
- create payment uses deterministic idempotence key
- create payment handles missing confirmation URL safely
- create payment raises controlled `PaymentProviderError` on HTTP 4xx/5xx
- create payment raises controlled `PaymentProviderError` on network error
- fetch payment calls `/payments/<id>`
- fetch payment raises controlled error on HTTP/network failure
- sanitized payload does not include credentials or unnecessary customer/payment data

Do not test description truncation unless the code actually accepts long descriptions. Current code uses `Order #<id>`, so a truncation test would be mostly artificial.

## Telegram Tests To Add

Expand `tests/test_telegram_notifications.py`:

- disabled config returns false and does not call HTTP
- missing token/chat id returns false and does not call HTTP
- enabled config posts expected chat id and message
- message includes order id/public code once identity work lands, status, customer, email, optional phone, address, total, provider/reference, items
- phone line is omitted when phone is blank
- HTTP failure returns false and does not crash
- timeout/network failure returns false and logs warning

## Cart Tests To Add

Expand `tests/test_cart.py`:

- adding missing product returns localized error
- negative update returns error
- zero update removes item
- stale cart product is removed from session
- cart quantity is clamped when stock drops
- line totals and item count are recomputed after clamping
- `clear_cart` empties session

## Config And Localization Tests To Add

Expand `tests/test_env_config.py` and `tests/test_i18n.py`:

- boolean parser accepts `1`, `true`, `yes`, `on`
- boolean parser rejects unknown strings
- `STORE_CURRENCY` uppercases
- YooKassa ready requires enabled + shop id + secret
- Telegram ready requires enabled + token + chat id
- unsupported locale switch falls back safely
- manual locale persists across multiple requests
- missing translation key returns safe fallback

## Test Infrastructure Changes

Improve `tests/conftest.py`:

- app fixture always uses temporary DB
- helper to create a cart with arbitrary products/quantities
- helper to create order with specific state
- helper to mutate product stock
- fake HTTP clients for YooKassa/Telegram
- autouse guard that blocks accidental real external HTTP in tests
- helper to simulate DB failures for rollback tests

Coverage config can be added later in `pyproject.toml`:

```toml
[tool.coverage.run]
branch = true
source = ["app"]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 85
```

Start with `fail_under = 85` only after the first new tests are in place. Raise to 90 after identity/reservation/refund work is covered.

## Suggested Implementation Order

1. Run current `uv run pytest --cov=app` and record baseline. Done: 79%.
2. Fix/remove unused `models.create_order`.
3. Add SQLite-safe transaction helper.
4. Refactor order creation to one transaction.
5. Refactor paid transition and stock decrement to one transaction.
6. Make notification timestamp marking idempotent.
7. Add DB schema/migration tests.
8. Add order creation rollback tests.
9. Add stock/payment transition tests.
10. Add route edge-case tests.
11. Add YooKassa provider error/fetch tests.
12. Add Telegram HTTP success/failure tests.
13. Add cart stale/negative/clamping tests.
14. Add coverage branch config with `fail_under = 85`.
15. Run `uv run pytest`.
16. Run `uv run pytest --cov=app`.
17. After identity/reservation/refund work lands, raise the target toward 90.

## Acceptance Criteria

- Multi-step database operations use explicit transactions.
- A failed order item insert cannot leave a partial order.
- A failed stock update cannot leave a half-paid order.
- Paid transition is idempotent and transaction-safe.
- Notification marking is idempotent.
- Tests cover migration behavior, order creation, stock transitions, payment route edge cases, provider errors, Telegram branches, and cart stale data.
- Coverage reaches at least 85% in the first pass and has a clear path to 90%.
- Current test suite still passes.
- No tests rely on real YooKassa, Telegram, email, or external network calls.
