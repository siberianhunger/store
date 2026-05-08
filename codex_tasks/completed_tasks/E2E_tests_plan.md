# E2E Tests Plan

Goal: verify the real customer journey through Baikal Stone Market in a browser: browsing, cart, checkout, order tracking without accounts, YooKassa redirect/return behavior, webhooks, and failure paths that could cost money or expose customer data.

## Recommended Tooling

Use Playwright through pytest once the app has enough browser behavior to justify it.

Recommended dependencies:

```bash
uv add --dev pytest-playwright
uv run playwright install chromium
```

Keep existing Flask pytest tests. Add browser tests under:

```text
tests/e2e/
├── conftest.py
├── test_catalog_cart.py
├── test_manual_checkout_tracking.py
├── test_yookassa_checkout.py
├── test_webhooks_and_reservations.py
└── test_layout_localization.py
```

E2E tests should start the Flask app against a temporary SQLite database, seeded products, and mocked external services.

## Test Environment

Use test config:

- temporary SQLite database
- `TESTING=True`
- deterministic product seed
- fake YooKassa provider or local fake HTTP server
- fake Telegram sender only for flows that enable Telegram
- no real network calls
- no real YooKassa credentials
- fixed app URL/port allocated by test fixture

Hard guard:

- fail tests if real-looking `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, `TELEGRAM_BOT_TOKEN`, or future SMTP credentials are used.

Do not add fake email infrastructure until the app actually has email sending. Tracking should be tested with order code + email + access key.

## Scenario 1: Browse And Cart

Steps:

1. Open `/`.
2. Verify catalog renders all seeded products.
3. Switch RU/EN and verify header/catalog text changes.
4. Filter by color and verify product grid updates.
5. Open product detail page.
6. Add item to cart.
7. Update quantity.
8. Remove item.
9. Add item again and continue to checkout.

Assertions:

- Product images stay inside their card image frames and do not overlap text/buttons.
- Cart badge/drawer updates through HTMX.
- Non-HTMX fallback works for add/update/remove.
- Quantity cannot exceed stock.
- Mobile viewport shows usable 1-column catalog and cart controls.

## Scenario 2: Manual Checkout And Tracking

Steps:

1. Add product to cart.
2. Open checkout.
3. Submit invalid form and verify inline errors.
4. Submit valid customer name, email, phone, and shipping address.
5. Land on order page.
6. Save public order code and private access key.
7. Open order URL in a fresh browser context with no session.
8. Use `/track` with order code + email + access key.

Assertions:

- Order is persisted.
- Payment status is manual pending.
- Full order details require access key or original session ownership.
- Numeric `/orders/1` does not reveal private order details.
- Tracking failure responses do not reveal whether the order code or email exists.
- Customer-facing text is localized.
- Manual Telegram notification is attempted only if enabled.

## Scenario 3: YooKassa Redirect Checkout

Use a fake provider that returns:

- payment id
- pending status
- confirmation URL on a local fake payment page

Steps:

1. Enable YooKassa in test config with fake credentials.
2. Add item to cart.
3. Submit checkout.
4. Verify redirect leaves store to fake YooKassa confirmation page.
5. Fake payment page redirects back to store return URL.
6. Return route fetches fake payment status.
7. Final order page shows paid status.

Assertions:

- Local order is created before payment request.
- Stock is reserved before the YooKassa payment is created.
- YooKassa request includes amount, currency, capture, return URL, description, metadata order id/public code, and idempotence key.
- Raw access key is not sent in YooKassa metadata or return URL.
- Payment id is stored locally.
- Return route does not mark paid unless fetched payment matches id, amount, currency, and order identity.
- Cart is cleared only after a valid checkout/payment handoff.

## Scenario 4: Webhook Finalizes Payment

Steps:

1. Create pending YooKassa order from browser checkout.
2. Simulate customer not returning from YooKassa.
3. Send fake `payment.succeeded` webhook to `/webhooks/yookassa`.
4. Open order tracking page.

Assertions:

- Webhook marks order paid.
- Stock reservation is converted to sold once.
- Duplicate webhook does not double-decrement stock.
- Paid Telegram notification sends once when enabled.
- Customer tracking page updates without requiring browser return.

## Scenario 5: Payment Mismatch And Safety

Run separate cases:

- webhook wrong payment id
- webhook wrong amount
- webhook wrong currency
- webhook wrong metadata order id/public code
- canceled payment
- expired unpaid reservation

Assertions:

- Wrong payment data never marks order paid.
- Order records safe error/manual review where appropriate.
- Canceled/expired payment releases reservation.
- Customer page does not show paid/fulfillable.
- Owner notification is sent for manual review states when Telegram is enabled.

## Scenario 6: Stock Reservation Race

Use two browser contexts.

Steps:

1. Product has stock 1.
2. Browser A adds product and submits checkout.
3. Browser B tries to buy the same product before A pays.
4. Browser A payment succeeds or cancels.
5. Browser B retries after reservation release if A cancels.

Assertions:

- Browser B cannot create a payable order while stock is reserved.
- If A cancels/expires, stock becomes available again.
- If A pays, stock stays unavailable.
- Store never creates a YooKassa payment for unavailable stock.

## Scenario 7: Receipt Payload Config

This can be integration-level until receipts are implemented; it does not need browser coverage at first.

Assertions:

- Disabled: payment request has no `receipt`.
- Enabled: payment request includes customer email/phone and item lines with configured VAT/payment mode/payment subject.
- Missing receipt config fails before production payment or keeps receipts explicitly disabled, depending on chosen policy.

## Scenario 8: Refund Flow

Do not create a fake admin UI just for this test. Cover refunds at provider/service integration level until an operator UI exists.

Assertions:

- Refund request uses stored payment id, amount, and idempotence key.
- Order payment status becomes refunded after fake YooKassa success.
- Customer tracking page shows refunded/canceled state once the UI exists.
- Stock policy is explicit: either return stock to available or mark item manually controlled.

## Scenario 9: Accessibility And Layout

Run core pages at desktop, tablet, and mobile viewports:

- `/`
- product detail
- cart
- checkout
- order detail
- tracking form

Assertions:

- No product card image overlaps metadata/action content.
- Buttons and form labels are accessible.
- Keyboard can reach cart, checkout, and tracking controls.
- Text does not overflow buttons/cards.
- Language switcher works without layout shift.

## Required Commands

Recommended commands:

```bash
uv run pytest
uv run pytest tests/e2e
uv run pytest --cov=app
```

For local visual/debug run:

```bash
uv run pytest tests/e2e --headed --slowmo 100
```

## Completion Criteria

- Manual customer journey passes in browser.
- YooKassa mocked customer journey passes in browser.
- Webhook-only payment completion passes.
- Tracking without auth passes and does not leak private data.
- Stock reservation race is covered.
- Payment mismatch cases are covered.
- Receipt behavior is covered at integration level once receipts exist.
- Refund behavior is covered at integration level once refunds exist.
- Existing pytest suite still passes.
