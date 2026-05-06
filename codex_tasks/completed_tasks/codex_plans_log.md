# Instruction For The Coding Agent

Build a working MVP online store for literal stones collected from Lake Baikal. The store must use the existing HTMX frontend direction in this repo, Python 3.12 with Flask for the backend, `uv` for project management, and SQLite for persistence. Do not implement real acquiring/payment processing yet; create a clean payment integration plug point so acquiring can be added later without rewriting checkout.

## Project Context

- This file is in `media/`. Treat the project root as the parent directory: `..`.
- Existing frontend files live in the project root:
  - `../index.html`
  - `../styles.css`
  - `../fragments/palette-warm-natural.html`
- The current frontend is an HTMX static prototype with the color system and component feel to preserve.
- Existing stone product images live in `media/separate_samples/`.
- There are 16 photographed stone images:
  - `stone_samples_8_stone_01.png` through `stone_samples_8_stone_08.png`
  - `stone_samples2_8_stone_01.png` through `stone_samples2_8_stone_08.png`
- The images are roughly 319-340px wide and 540-542px high. Build image containers that can handle these slight dimension differences without layout shift.

## Required Stack

- Frontend: server-rendered HTML fragments enhanced with HTMX.
- Backend: Flask on Python 3.12.
- Package/runtime management: `uv`.
- Database: SQLite.
- CSS: continue from the existing `styles.css` design language.
- Do not add a SPA framework.
- Do not add a heavy frontend build step.

## First Tasks

1. Update `pyproject.toml` so the project targets Python 3.12, not Python 3.14.
2. Add Flask as a dependency through `uv`.
3. Replace the placeholder `main.py` with a real Flask app entrypoint.
4. Keep the existing visual palette, but adapt the store brand from the furniture placeholder to a Baikal stone shop.
5. Preserve HTMX usage and make product/catalog/cart interactions happen through HTMX fragments.

## MVP Product Scope

Create a complete small-store flow:

- Home/catalog page showing all stones.
- Product cards with real stone photos from `media/separate_samples/`.
- Product detail view, preferably loaded inline or navigated to normally with server-rendered HTML.
- Filters or simple category tabs using HTMX.
- Cart drawer or cart page updated through HTMX.
- Add to cart.
- Update item quantity.
- Remove item from cart.
- Checkout form.
- Order confirmation page.
- Basic admin seed data, implemented as a local seed function or CLI command.

The user should be able to start the server, browse the catalog, add stones to cart, submit checkout details, and receive an order confirmation, all without touching external services.

## Product Data

Seed 16 products, one per image in `media/separate_samples/`.

Each product should have:

- `id`
- `slug`
- `name`
- `description`
- `price_cents`
- `image_path`
- `stock`
- `weight_grams`
- `origin`
- `finish`
- `color_family`
- `is_featured`

Use a tasteful naming system appropriate for stones from Lake Baikal, for example:

- Baikal Shoreline Pebble
- Selenga Grey Stone
- Olkhon Stripe Stone
- Listvyanka Smooth Stone
- Deep Water Granite
- Mist Vein Pebble

Do not claim supernatural, medical, investment, or scientifically unsupported properties. Keep copy grounded: texture, color, shape, origin, and decorative use.

## Database Requirements

Use SQLite with a small explicit schema. Implement schema creation in code so a fresh checkout can run without manual SQL setup.

Required tables:

- `products`
- `orders`
- `order_items`

Recommended optional table:

- `cart_items`, if you choose a server-side cart.

Session-based cart is acceptable for the MVP. If using sessions, store only product ids and quantities in the session, then read product data from SQLite.

Orders must persist:

- customer name
- email
- phone, optional
- shipping address
- order status
- payment status
- total amount
- created timestamp

Order items must persist:

- order id
- product id
- product name snapshot
- unit price snapshot
- quantity

## Payment/Acquiring Plug Point

Do not connect real acquiring yet.

Create a clear payment abstraction that can later be replaced by a real acquiring provider. For the MVP, implement a fake/manual provider with this behavior:

- On checkout submit, validate cart and customer fields.
- Create the order in SQLite with `payment_status = "pending_manual"`.
- Return an order confirmation page explaining that payment is pending and will be handled manually.

Design this as replaceable code, for example:

- `payments/base.py` with a provider interface or simple protocol.
- `payments/manual.py` with `ManualPaymentProvider`.
- `create_payment(order)` returns a structured result with fields like `status`, `payment_reference`, and optional `redirect_url`.

Do not hardcode payment logic deep inside route handlers.

## Suggested File Structure

You may adjust this if the implementation stays simple and coherent, but prefer something close to:

```text
.
├── main.py
├── pyproject.toml
├── README.md
├── store.db              # generated locally; should be gitignored if git is used
├── app/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   ├── routes.py
│   ├── seed.py
│   ├── cart.py
│   ├── payments/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── manual.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── product_detail.html
│       ├── checkout.html
│       ├── order_success.html
│       └── fragments/
│           ├── product_grid.html
│           ├── product_card.html
│           ├── cart_drawer.html
│           ├── cart_line.html
│           └── cart_badge.html
├── static/
│   └── styles.css
└── media/
    └── separate_samples/
```

If you move `styles.css` into `static/`, update all references. Keep the stone images in `media/separate_samples/` and serve them through Flask with a route or static configuration.

## Frontend Requirements

Use HTMX for progressive interactions:

- Catalog filters: `hx-get` product grid fragments.
- Add to cart: `hx-post` and update cart badge/drawer.
- Quantity changes: `hx-post` or `hx-put` and swap cart contents.
- Remove item: `hx-delete` or `hx-post` and swap cart contents.
- Checkout validation errors: return the checkout form fragment/page with inline errors.

The app must work as normal server-rendered pages even if HTMX is unavailable for the core flow. HTMX should improve the interaction, not be the only way to use the store.

Use semantic HTML:

- Real forms and buttons.
- Product images with descriptive `alt`.
- Accessible labels for checkout fields.
- Header navigation with links to catalog and cart.

## Visual Design Requirements

Use the existing warm natural palette from `styles.css`:

- background `#F7F1E8`
- text `#2B2118`
- brand/walnut `#5A3E2B`
- secondary/clay `#B9825A`
- accent/sage `#7A8450`
- section/sand `#E6D6C3`
- border/taupe `#C6B49E`
- CTA/terracotta `#A65335`

Adapt the brand to Lake Baikal stones. Suggested brand name: `Baikal Stone Market`.

The UI should feel like a real small catalog store:

- Dense but readable product grid.
- Real stone photos are prominent.
- Product cards should use fixed image frames with `object-fit: contain` or `object-fit: cover`, whichever shows the stones best.
- Avoid marketing-only hero pages. The first screen should immediately show products or a hero with visible product grid content below.
- Avoid nested cards and excessive decoration.
- Keep border radii around 8px or less.
- Use responsive layouts for mobile and desktop.

## Backend Routes

Implement routes roughly like:

- `GET /` catalog/home.
- `GET /products/<slug>` product detail.
- `GET /fragments/products` filtered product grid.
- `POST /cart/add/<product_id>` add item.
- `GET /cart` cart page or drawer.
- `GET /fragments/cart` cart fragment.
- `POST /cart/update/<product_id>` update quantity.
- `POST /cart/remove/<product_id>` remove item.
- `GET /checkout` checkout form.
- `POST /checkout` validate and create order.
- `GET /orders/<order_id>` order confirmation.
- `POST /dev/seed` only if useful locally; otherwise seed automatically on first run.

Use redirects for non-HTMX requests and fragments for HTMX requests. Detect HTMX with the `HX-Request` header.

## Validation

Validate:

- Quantity is a positive integer.
- Quantity cannot exceed stock.
- Checkout cart cannot be empty.
- Customer name is required.
- Email is required and minimally valid.
- Shipping address is required.

Show validation errors in the UI without crashing.

## Development Experience

Make the app easy to run:

- `uv sync`
- `uv run python main.py`

The Flask server should start on a local port and print the URL.

Update `README.md` with:

- stack summary
- setup commands
- run command
- seed/reset instructions
- note that acquiring is intentionally a manual/pending plug point for now

If adding generated files, keep local runtime artifacts out of git:

- `store.db`
- `*.sqlite`
- `instance/`
- `__pycache__/`
- `.venv/`

## Acceptance Criteria

The MVP is done when:

- `uv sync` succeeds.
- `uv run python main.py` starts the Flask app.
- Visiting `/` shows a styled catalog using the real stone images.
- All 16 stones are present in the seeded catalog.
- Product cards match the existing warm natural visual system.
- Add/update/remove cart interactions work with HTMX.
- The cart also remains usable through normal form submits/redirects.
- Checkout creates a persistent order in SQLite.
- The fake/manual payment provider is used and isolated behind a replaceable payment interface.
- The order confirmation page displays order number, customer email, items, total, and manual payment status.
- No real acquiring/payment provider is called.
- The README explains how to run and what remains to integrate for payments.

## Implementation Notes

- Prefer simple Flask, Jinja templates, and standard library SQLite unless a dependency is clearly justified.
- Keep business logic out of templates where practical.
- Format prices from cents consistently.
- Use integer cents for money.
- Keep route handlers small by moving cart/database helpers into modules.
- Seed data should be idempotent: running it twice should not duplicate products.
- Do not overwrite the photographed stone assets.
- Do not remove the existing prototype files unless they are intentionally replaced by the working app.
- Before finishing, run at least a smoke test by starting the app and requesting `/`.
# Second Iteration Plan

Goal: add real payment-processing plumbing through YooKassa, Telegram order notifications, and RU/EN localization while keeping the current manual provider as a safe fallback for local development.

## 1. Environment Management

Add project-local `.env` file reading before implementing provider credentials. Do not hardcode payment or Telegram secrets in Python files.

Recommended dependency:

```bash
uv add python-dotenv
```

Update `.gitignore`:

```text
.env
.env.*
!.env.example
```

Create `.env.example` with safe placeholders:

```bash
SECRET_KEY=dev-change-me

STORE_CURRENCY=RUB

YOOKASSA_ENABLED=false
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL_BASE=http://127.0.0.1:5000/payments/yookassa/return

TELEGRAM_NOTIFICATIONS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Load `.env` at app startup before reading config:

```python
from dotenv import load_dotenv

load_dotenv()
```

Config rules:

- `.env` is for local development only.
- Production should provide real environment variables directly.
- `.env.example` documents required keys but contains no secrets.
- If integration keys are missing, disable that integration and keep checkout working through manual mode.
- Log missing optional integration config clearly, but do not crash local checkout.

## 2. Currency And Pricing Cleanup

YooKassa quick start uses `RUB`, and the current app visually formats prices as dollars. Fix that before connecting payments.

Required decision for this iteration:

- Treat stored integer prices as kopeks, not USD cents.
- Rename helpers conceptually in code/comments where practical: `price_cents` can stay temporarily for migration simplicity, but UI/payment code must treat it as minor units for `STORE_CURRENCY`.
- Set `STORE_CURRENCY=RUB` by default.
- Display prices as Russian rubles in RU locale and a clear RUB display in EN locale.
- YooKassa amount must be decimal rubles, for example integer `1800` -> `"18.00"` with currency `"RUB"`.

Do not send `$` prices to the UI once localization/payment work starts.

## 3. YooKassa Payment Processing

Reference: https://yookassa.ru/developers/payment-acceptance/getting-started/quick-start?lang=en

YooKassa quick-start flow:

- Create a payment server-side with shop id, secret key, amount, idempotence key, `capture: true`, redirect confirmation, `return_url`, and order description.
- YooKassa returns a payment object in `pending` status.
- Redirect the customer to `confirmation.confirmation_url`.
- Payment is successful only after payment status becomes `succeeded`.
- Payment may become `canceled`.
- Status should be handled through YooKassa notifications/webhooks and optionally verified by fetching payment status after return.

### Required Configuration

Environment variables:

```bash
YOOKASSA_ENABLED=false
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL_BASE=http://127.0.0.1:5000/payments/yookassa/return
```

Rules:

- If `YOOKASSA_ENABLED=true` and credentials exist, use YooKassa.
- If credentials are missing, fall back to the current manual provider and show/log a clear local-development message.
- Never commit real credentials.

### Dependency

Preferred simple option:

```bash
uv add httpx
```

Alternative: use YooKassa official Python SDK if it fits the project cleanly. Do not use both.

### Payment Provider Structure

Extend existing payment abstraction:

```text
app/payments/
├── base.py
├── manual.py
└── yookassa.py
```

`YooKassaPaymentProvider.create_payment(order)` should:

- accept persisted order data
- build amount from order total minor units
- convert minor units to a RUB decimal string like `"1234.00"`
- set `capture: true`
- set `confirmation.type = "redirect"`
- set `confirmation.return_url = "<YOOKASSA_RETURN_URL_BASE>?order_id=<local_order_id>"`
- set `description = "Order #<id>"`, max 128 characters
- include metadata with local `order_id`
- send `Idempotence-Key`, for example deterministic `order-<id>-payment-v1`
- return a `PaymentResult` with:
  - `status`
  - `payment_reference` as YooKassa payment id
  - `redirect_url` as YooKassa confirmation URL

### Checkout Flow Changes

Current flow creates an order and immediately shows confirmation. Change it to:

1. Validate checkout form and cart.
2. Create local order with:
   - `status = "awaiting_payment"`
   - `payment_status = "pending"`
   - `payment_provider = "yookassa"` when enabled, otherwise `"manual"`
3. Create YooKassa payment.
4. Save YooKassa payment id and redirect URL.
5. If YooKassa payment creation succeeds and `redirect_url` exists, redirect customer to YooKassa.
6. If YooKassa payment creation fails after local order creation:
   - mark order `status = "payment_error"`
   - mark `payment_status = "error"`
   - keep enough order/cart context for retry
   - render order page with a retry/continue message
7. If using manual provider, redirect to existing local order page with manual pending status.

### Database Changes

Add idempotent lightweight migrations in `app/db.py` using `PRAGMA table_info` before adding new columns.

Add columns to `orders`:

- `payment_provider`
- `payment_redirect_url`
- `paid_at`
- `payment_error`
- `telegram_paid_notified_at`
- `telegram_manual_notified_at`

Current `payment_reference` already exists in the table. Keep using it for YooKassa payment id.

Optional debug column:

- `payment_payload_json`

If adding `payment_payload_json`, store only sanitized provider data. Do not persist unnecessary customer/payment details by default.

### Return Route

Add:

```text
GET /payments/yookassa/return?order_id=<local_order_id>
```

Behavior:

- Require `order_id`.
- Load local order by `order_id`.
- Read stored `payment_reference`.
- Fetch YooKassa payment status by payment id if credentials exist.
- Verify fetched payment matches local order:
  - payment id matches `payment_reference`
  - metadata order id matches local order id when present
  - amount and currency match local order total and `STORE_CURRENCY`
- Update local order status:
  - YooKassa `succeeded` -> `status = "paid"`, `payment_status = "succeeded"`, set `paid_at`
  - YooKassa `canceled` -> `status = "payment_failed"`, `payment_status = "canceled"`
  - otherwise keep `awaiting_payment`
- Render order page with a localized status message.

### Webhook Route

Add:

```text
POST /webhooks/yookassa
```

Behavior:

- Parse YooKassa event payload.
- For `payment.succeeded`, update order to paid.
- For `payment.canceled`, mark payment failed.
- Use metadata/local order id from the payment object to find the order.
- Match payment id, amount, and currency against the local order before changing status.
- Treat webhook handling as idempotent.
- Only allow forward status transitions. Never move a paid order back to pending.
- Return `200` for handled/repeated events.

Security note:

- Before production launch, configure and verify YooKassa notifications according to YooKassa’s current account/docs flow.
- For MVP, keep the route narrow, validate expected fields, and do not trust unknown order ids or mismatched amounts.

### Receipt / Fiscalization Caveat

YooKassa production accounts may require receipt/fiscalization handling depending on shop settings and legal setup.

For this iteration:

- Do not implement fiscal receipt payloads unless the shop settings require them.
- Add a README note: confirm YooKassa receipt/54-FZ settings before real production payments.
- If receipt data is required, add a later task to send YooKassa receipt details for items, quantities, VAT, customer email/phone, and payment subject/mode.

### Stock Policy

Current MVP does not decrement stock. Real payment flow needs a policy.

For this iteration:

- Re-check stock before creating the order.
- Do not decrement stock at `awaiting_payment`.
- Decrement product stock only once when order becomes `paid`.
- Make paid transition idempotent so repeated return/webhook calls do not double-decrement.
- If stock is no longer available when payment succeeds, flag the order for manual handling instead of silently overselling.

### Order Page Updates

Show payment state clearly:

- awaiting payment
- paid
- failed/canceled
- payment error
- manual pending

If order has a `payment_redirect_url` and payment is still pending/error, show a localized “Continue payment” button.

## 4. Telegram Bot Notifications

Goal: notify the store owner when an order is paid, and optionally when a manual unpaid order is created.

### Required Configuration

Environment variables:

```bash
TELEGRAM_NOTIFICATIONS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Rules:

- If disabled or credentials are missing, do not fail checkout/payment flow.
- Log a clear message instead.
- Never commit token/chat id.

### Telegram Module

Add:

```text
app/notifications/
├── __init__.py
└── telegram.py
```

Implement two distinct notification events:

```python
send_order_paid_notification(order, items)
send_manual_pending_order_notification(order, items)
```

Use Telegram Bot API:

```text
POST https://api.telegram.org/bot<token>/sendMessage
```

Message should include:

- event type: paid order or manual pending order
- order id
- payment status
- customer name
- email
- phone if provided
- shipping address
- item list with quantity
- order total
- payment provider/reference

Use plain text unless HTML formatting is truly needed. Escape user-provided values if using HTML.

### When To Send Notifications

- For YooKassa: send `order_paid` only when payment becomes `succeeded`.
- For manual fallback: send `manual_pending_order` after local order creation, clearly marked as unpaid/manual pending.

Avoid duplicate notifications:

- Use `telegram_paid_notified_at` for paid notifications.
- Use `telegram_manual_notified_at` for manual pending notifications.
- Before sending, check whether that event was already sent.
- After successful send, persist timestamp.

Telegram failure must not break checkout, return route, or webhook handling.

## 5. Localization

Goal: make the storefront available in Russian and English, with Russian as the default language.

### Locale Rules

- Supported locales: `ru`, `en`.
- Default locale: `ru`.
- Browser detection uses `request.accept_languages.best_match(["ru", "en"], default="ru")`.
- If the header is absent or ambiguous, use `ru`.
- If English is the best match, use `en`.
- Add a manual language switcher in the header so the customer can switch between RU and EN.
- Persist manual language choice in session or a small cookie.
- Manual choice overrides browser detection.

Recommended priority:

1. language switch route, for example `POST /locale/<locale>` or `GET /locale/<locale>`
2. saved session/cookie locale
3. browser `Accept-Language`
4. default `ru`

Avoid requiring every form/action URL to carry `?lang=...`. The switch route should save the locale and redirect back to the previous page where practical.

### Implementation Options

Use one of:

- Simple in-app translation dictionaries for MVP.
- `Flask-Babel` if the project needs more scalable gettext files.

For this MVP, a simple dictionary is acceptable if it stays organized.

Suggested structure:

```text
app/
├── i18n.py
└── translations/
    ├── ru.py
    └── en.py
```

Expose template helpers:

```python
{{ t("catalog") }}
{{ localized_product_name(product) }}
{{ localized_product_description(product) }}
```

### Content To Localize

Localize all customer-facing copy:

- navigation
- hero headline and description
- catalog heading
- filter labels
- product names
- product descriptions
- product metadata labels
- buttons
- cart
- checkout form labels and validation errors
- order status text
- YooKassa payment messages
- manual payment messages
- order confirmation page
- price/currency formatting

Product data should support both languages.

Preferred for MVP:

- Add `name_ru`, `name_en`, `description_ru`, `description_en` columns to SQLite.
- Seed both RU and EN product text.
- Keep product slugs stable and language-neutral enough for URLs.

### Russian Copy Requirement

The Russian site must be a real localized version, not machine-looking placeholders.

Examples:

- `Natural stones for quiet interiors` -> `Природные камни для спокойного интерьера`
- `Choose your stone` -> `Выберите свой камень`
- `Add` -> `Добавить`
- `Cart` -> `Корзина`
- `Checkout` -> `Оформление`
- `Order confirmed` -> `Заказ оформлен`
- `Payment pending` -> `Ожидает оплаты`

### Language Switcher

Add compact header control:

```text
RU | EN
```

Requirements:

- current language is visually active
- switching preserves current path where practical
- no layout shift on mobile
- accessible labels

### Acceptance Criteria

- Default fresh visit shows Russian.
- Browser `Accept-Language: en` shows English unless a manual locale is saved.
- User can switch RU/EN from the header.
- Cart, checkout, validation errors, order confirmation, and payment status are localized.
- Product names and descriptions are localized.
- No user-facing hardcoded English remains in templates/routes.

## 6. Pytest Test Stack

Goal: every second-iteration feature should be covered by automated tests. Use pytest as the project test runner.

### Dependencies

Add:

```bash
uv add --dev pytest pytest-cov
```

If HTTP requests are mocked at the transport layer, also add one of:

```bash
uv add --dev respx
```

or use `httpx.MockTransport` without an extra dependency.

### Test Structure

Suggested layout:

```text
tests/
├── conftest.py
├── test_env_config.py
├── test_i18n.py
├── test_catalog.py
├── test_cart.py
├── test_checkout_manual.py
├── test_yookassa_provider.py
├── test_yookassa_routes.py
├── test_telegram_notifications.py
└── test_order_status.py
```

### Fixtures

`tests/conftest.py` should provide:

- Flask app configured for testing.
- Temporary SQLite database path through `tmp_path`.
- Test client.
- Seeded products.
- Helper to create a cart session.
- Helper to create orders in specific payment states.
- Monkeypatched env vars for YooKassa and Telegram.

Tests must not use the developer’s real `store.db`.

### Required Coverage

Environment/config:

- `.env` loading does not crash without a `.env`.
- missing YooKassa credentials disable YooKassa cleanly.
- missing Telegram credentials disable notifications cleanly.
- test config can override database path and env vars.

Localization:

- default locale is `ru`.
- `Accept-Language: en` selects English.
- saved manual locale overrides browser header.
- language switcher persists choice.
- key templates render localized navigation/cart/checkout text.
- price formatting uses RUB and locale-appropriate display.

Catalog/cart:

- all seeded products render.
- localized product names/descriptions render.
- add/update/remove cart works.
- quantity cannot exceed stock.
- empty checkout is rejected.

Manual checkout:

- manual mode works without YooKassa credentials.
- manual order is persisted with manual pending status.
- manual pending Telegram event is attempted only when enabled.

YooKassa provider:

- create-payment request payload includes amount, currency, capture, redirect confirmation, return URL with `order_id`, description, metadata, and idempotence key.
- successful mocked response returns payment id and confirmation URL.
- API failure returns/raises a controlled provider error that checkout can display.

YooKassa return/webhook routes:

- return route requires `order_id`.
- return route fetches payment by stored reference.
- `succeeded` marks order paid.
- `canceled` marks payment failed.
- mismatched payment id, amount, currency, or order metadata does not mark order paid.
- repeated webhook does not duplicate stock decrement.
- paid transition decrements stock once.

Telegram:

- paid notification message includes order/customer/items/total/provider reference.
- manual pending message is clearly marked unpaid/manual.
- duplicate notifications are skipped based on persisted timestamps.
- Telegram API failure is logged/handled and does not break payment flow.

### Commands

Document and support:

```bash
uv run pytest
uv run pytest --cov=app
```

## 7. README Technical Documentation

Update `README.md` into a technical project guide, not just a short run note.

Required sections:

- Project overview.
- Stack: Flask, HTMX, SQLite, uv, pytest.
- Directory structure.
- Local setup.
- `.env` setup using `.env.example`.
- Run command.
- Test commands.
- Database/seed/reset instructions.
- Localization behavior and how RU/EN detection works.
- Payment architecture:
  - manual provider
  - YooKassa provider
  - required env vars
  - return URL
  - webhook URL
  - receipt/fiscalization caveat
- Telegram notification architecture:
  - required env vars
  - paid vs manual pending notification distinction
  - duplicate notification prevention
- Operational notes:
  - no real secrets in git
  - production should use real env vars, not `.env`
  - public webhook URL is required for real YooKassa notifications

## 8. User-Facing Flow

### With YooKassa Enabled

1. Customer fills checkout.
2. Local order is created as `awaiting_payment`.
3. YooKassa payment is created.
4. Customer is redirected to YooKassa.
5. YooKassa processes payment.
6. Customer returns to `/payments/yookassa/return?order_id=<id>`.
7. Return route and/or webhook marks order paid.
8. Stock is decremented once.
9. Telegram paid notification is sent once.
10. Order page shows paid status.

### With YooKassa Disabled

1. Customer fills checkout.
2. Local order is created as manual pending.
3. Customer sees existing confirmation page.
4. Telegram manual pending notification may be sent if enabled.

## 9. Implementation Order

1. Add `python-dotenv`.
2. Add `.env` loading at app startup.
3. Add `.env.example` with placeholders.
4. Update `.gitignore` so real `.env` files are not committed.
5. Add config helpers that read currency, YooKassa, Telegram, and locale settings from environment/session/request.
6. Add pytest stack and baseline test fixtures.
7. Add a general idempotent DB migration helper.
8. Add localization columns to products.
9. Add payment/notification columns to orders.
10. Add localization helpers and locale detection.
11. Add RU/EN language switcher.
12. Localize templates, validation errors, cart, checkout, order pages, and price formatting.
13. Seed localized product names/descriptions.
14. Add localization tests.
15. Refine `PaymentResult` and base payment provider interface.
16. Implement `YooKassaPaymentProvider`.
17. Add YooKassa provider tests with mocked HTTP.
18. Update checkout route to create local order first, then create payment.
19. Add payment creation failure handling.
20. Add YooKassa return route with `order_id`.
21. Add YooKassa webhook route with payment id/amount/currency checks.
22. Add order status UI updates and continue-payment action.
23. Add paid-order stock decrement logic, idempotently.
24. Add YooKassa route/status/stock tests.
25. Add Telegram notification module.
26. Trigger Telegram notification on paid/manual-pending order, idempotently.
27. Add Telegram notification tests.
28. Update README with the full technical documentation described above.
29. Run `uv run pytest`.
30. Run `uv run pytest --cov=app`.
31. Run smoke tests for manual mode without credentials.
32. Run locale tests for default RU and browser EN.
33. If credentials are provided, run YooKassa test payment flow.

## 10. Acceptance Criteria

- App still works without YooKassa credentials.
- Manual provider remains usable for local development.
- Russian is the default locale.
- English is selected when browser metadata clearly prefers English.
- Manual RU/EN switcher works and persists choice.
- UI displays RUB prices instead of dollars.
- With YooKassa env vars enabled, checkout redirects to YooKassa confirmation URL.
- YooKassa return URL includes local `order_id`.
- Orders persist YooKassa payment id and pending status.
- Return route can refresh payment status.
- Webhook route updates paid/canceled status idempotently.
- Webhook/return checks payment id, amount, and currency before updating order.
- Product stock is decremented once when an order becomes paid.
- YooKassa payment creation failures are visible and retryable.
- Telegram paid notification sends once per paid order.
- Telegram manual pending notification is distinct from paid notification.
- Telegram failure does not break checkout or webhook handling.
- pytest stack exists and `uv run pytest` passes.
- tests cover env config, localization, cart, checkout, YooKassa provider/routes, Telegram notifications, order status, and stock decrement.
- README contains the required technical project documentation.
- README documents all required env vars.
- README notes YooKassa receipt/fiscalization caveat before production.
- `.env.example` exists and real `.env` files are ignored.
- No real secrets are committed.

## 11. Open Questions / Credentials Needed Later

Needed for real YooKassa testing:

- `YOOKASSA_SHOP_ID`
- `YOOKASSA_SECRET_KEY`
- public reachable webhook URL for `/webhooks/yookassa`
- confirmation of YooKassa receipt/fiscalization settings

Needed for Telegram testing:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Until these are provided, implement and verify the plug points using disabled/manual mode plus mocked or logged responses.
Fix the product card image layout and improve the overall visual design.

Current issue:
The stone product images are overflowing/overfitting their product card fields. The images are too large and are being cropped by the card boundaries, causing the selling item details, title, price, weight, and Add button to overlap with the image area. Product cards should feel clean, contained, and intentional.

Required image/card fixes:
1. Make every product image live inside a dedicated image container with a fixed, consistent aspect ratio.
2. Prevent images from covering or overlapping text/content.
3. Use object-fit: cover only inside the image container, not across the whole card.
4. Add overflow-hidden to the image container, not to the whole card content area.
5. Ensure the card has a clear structure:
   - image area on top
   - product metadata below
   - footer row with price and Add button
6. Keep title, description, tag, weight, price, and button fully visible at all screen sizes.
7. Use consistent image heights across product cards.
8. Add responsive behavior:
   - desktop: 4-column grid
   - tablet: 2-column grid
   - mobile: 1-column grid
9. Add enough padding and spacing so the cards do not feel cramped.
10. Make sure no text sits on top of product images unless it is a small intentional badge.

Suggested card structure:
- Card container: rounded corners, subtle border, soft shadow, clean background.
- Image wrapper: width 100%, aspect-ratio 4 / 3 or 1 / 1, border-radius on top corners, overflow hidden.
- Image: width 100%, height 100%, object-fit: cover, display block.
- Content section: padding 16–20px.
- Badge + weight row above title or near title.
- Title: readable serif or semi-bold display style.
- Description: muted text, 2–3 line clamp.
- Footer: price left, Add button right.

Frontend style direction:
Make the site feel more premium, calm, and natural. Shift the color palette away from the current beige/brown-heavy look toward a “foresty and clean lake” aesthetic.

Color scheme:
- Background: very pale lake mist / off-white with a cool tint
  Example: #F4F8F6 or #F2F7F5
- Section background: soft lake clay / light sage
  Example: #DDE8DF or #E3ECE7
- Primary text: deep forest green
  Example: #183A2E or #1F3D34
- Secondary text: muted slate-green
  Example: #5F746B
- Primary button: pine green
  Example: #2F5D50
- Button hover: deeper evergreen
  Example: #21473D
- Accent: clean lake blue
  Example: #6FA7B8 or #8BBFCC
- Badge background: moss green
  Example: #6F8557
- Border: pale reed / misty green-gray
  Example: #C8D6CF
- Card background: warm white / lake foam
  Example: #FBFCFA

Design improvements:
1. Redesign the hero section so it feels spacious and balanced.
2. The giant headline is currently cropped at the top; fix vertical spacing and ensure the full heading is visible.
3. Use a cleaner layout with more intentional whitespace.
4. Use a refined serif for large headings and a clean sans-serif for body text.
5. Make the stat card on the right more elegant with a softer shadow, rounded corners, and forest/lake colors.
6. Make the filter buttons cleaner:
   - pill-shaped
   - active state in pine green
   - inactive state white or mist green
   - subtle border
7. Make product cards feel like premium catalog items:
   - consistent card heights
   - restrained shadows
   - soft borders
   - clear hierarchy
8. Add subtle hover states:
   - card lifts slightly
   - image gently scales inside its container
   - Add button darkens
9. Keep the design calm, minimal, and natural — no loud colors or heavy shadows.

Implementation details:
Use CSS grid for the catalog layout. Use a robust product card component structure similar to:

.card {
  background: #FBFCFA;
  border: 1px solid #C8D6CF;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(24, 58, 46, 0.08);
  display: flex;
  flex-direction: column;
}

.imageWrap {
  width: 100%;
  aspect-ratio: 4 / 3;
  overflow: hidden;
  background: #DDE8DF;
}

.imageWrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 220ms ease;
}

.card:hover .imageWrap img {
  transform: scale(1.035);
}

.cardBody {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}

.metaRow,
.footerRow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.description {
  color: #5F746B;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.footerRow {
  margin-top: auto;
}

Primary goal:
No product image should ever overlap or crop into the text/action area. The UI should look like a polished, premium stone catalog inspired by forest green, clean lake water, mist, moss, and natural stone.