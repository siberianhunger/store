# Baikal Stone Market

Baikal Stone Market is a Flask and HTMX storefront for decorative stones from the Lake Baikal region. The app is server-rendered, uses SQLite for persistence, supports RU/EN localization, and has payment/notification plug points for YooKassa and Telegram.

## Stack

- Python 3.12
- Flask
- HTMX
- SQLite
- uv
- pytest / pytest-cov
- YooKassa via HTTP API
- Telegram Bot API

## Directory Structure

```text
app/
  payments/          Payment provider interfaces and implementations
  notifications/     Telegram notification code
  templates/         Jinja pages and HTMX fragments
  db.py              Schema and lightweight migrations
  routes.py          Store, cart, checkout, payment, webhook routes
  i18n.py            RU/EN translations and locale helpers
media/
  catalog_samples/   Normalized product images used by the catalog
static/
  styles.css         Store styling
tests/               pytest suite
```

## Local Setup

```bash
uv sync
cp .env.example .env
uv run python main.py
```

Open `http://127.0.0.1:5000`.

The app creates `store.db` automatically and idempotently seeds the product catalog.

## Environment

Local development reads `.env` through `python-dotenv`. Production should provide real environment variables directly.

Required/local keys are documented in `.env.example`:

```bash
SECRET_KEY=dev-change-me
APP_MODE=
DATABASE=
STORE_CURRENCY=RUB
PAYMENT_PROVIDER=
YOOKASSA_ENABLED=false
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL_BASE=http://127.0.0.1:5000/payments/yookassa/return
YOOKASSA_RECEIPTS_ENABLED=false
YOOKASSA_VAT_CODE=
YOOKASSA_PAYMENT_MODE=
YOOKASSA_PAYMENT_SUBJECT=
TELEGRAM_NOTIFICATIONS_ENABLED=false
TELEGRAM_DEV_MODE=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_ALLOWED_USER_IDS=
TELEGRAM_ALLOWED_CHAT_IDS=
```

Never commit real `.env` files or credentials.

## Tests

```bash
uv run pytest
uv run pytest --cov=app
```

The suite covers config, localization, catalog/cart behavior, manual checkout, YooKassa provider payloads, payment status transitions, stock decrement idempotency, and Telegram notification idempotency.

## Database Reset

```bash
rm -f store.db
uv run python main.py
```

## Local Full-Flow Dev Server

Use the fake YooKassa flow when you want to click through checkout, fake payment success/cancel/failure, order tracking, and stock reservation without real YooKassa credentials:

```bash
uv run python scripts/dev_server.py
```

For a clean dev database:

```bash
uv run python scripts/reset_dev_db.py
```

The dev server uses `dev_store.db`, `APP_MODE=dev_flow`, and `PAYMENT_PROVIDER=fake_yookassa`. Checkout redirects to a local fake payment page where you can mark a payment succeeded, canceled, or failed. Dev payment tools are available at `/dev/tools/orders` only in dev-flow fake-payment mode.

Telegram notification testing can use a real development bot and private dev chat:

```bash
TELEGRAM_NOTIFICATIONS_ENABLED=true
TELEGRAM_DEV_MODE=true
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Send a test message with:

```bash
curl -X POST http://127.0.0.1:5000/dev/tools/telegram/test
```

## Localization

Russian is the default locale. Browser `Accept-Language` can select English when it is the best match. A header switcher persists manual RU/EN choice in the session.

Product names/descriptions and customer-facing templates are localized. Prices are displayed as RUB.

## Payments

The app keeps the manual payment provider as a local fallback. If `YOOKASSA_ENABLED=true` and both YooKassa credentials are present, checkout creates a local order, creates a YooKassa payment, stores the YooKassa payment id, and redirects to the confirmation URL.

YooKassa routes:

- return URL: `/payments/yookassa/return?order_id=<id>`
- webhook URL: `/webhooks/yookassa`

The return/webhook handling verifies payment id, order metadata, amount, and currency before marking an order paid. Stock is decremented once when an order becomes paid.

YooKassa receipt/fiscalization requirements depend on shop settings and legal setup. Confirm YooKassa receipt/54-FZ settings before production payments. Receipt payloads are disabled by default and require explicit `YOOKASSA_RECEIPTS_ENABLED`, VAT, payment mode, and payment subject configuration.

## Telegram Notifications

Telegram notifications are optional. Configure:

```bash
TELEGRAM_NOTIFICATIONS_ENABLED=true
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

Two event types are intentionally separate:

- paid order notification after YooKassa `succeeded`
- manual pending notification for unpaid/manual fallback orders

Notification timestamps are stored on the order to avoid duplicate sends. Telegram failures are logged and do not break checkout or payment webhook handling.

Telegram can also accept owner shipping updates when a webhook secret is configured:

```bash
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_ALLOWED_CHAT_IDS=
TELEGRAM_ALLOWED_USER_IDS=
```

Set the Telegram webhook to `/webhooks/telegram/<TELEGRAM_WEBHOOK_SECRET>`, then send:

```text
/ship BSM-20260506-K7P4Q2 CDEK 123456789
```

The command stores the carrier and tracking number on a paid order. Customers can see shipping data only after opening their protected order page with the checkout session or access key.
