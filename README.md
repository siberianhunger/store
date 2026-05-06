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
STORE_CURRENCY=RUB
YOOKASSA_ENABLED=false
YOOKASSA_SHOP_ID=
YOOKASSA_SECRET_KEY=
YOOKASSA_RETURN_URL_BASE=http://127.0.0.1:5000/payments/yookassa/return
TELEGRAM_NOTIFICATIONS_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
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

## Localization

Russian is the default locale. Browser `Accept-Language` can select English when it is the best match. A header switcher persists manual RU/EN choice in the session.

Product names/descriptions and customer-facing templates are localized. Prices are displayed as RUB.

## Payments

The app keeps the manual payment provider as a local fallback. If `YOOKASSA_ENABLED=true` and both YooKassa credentials are present, checkout creates a local order, creates a YooKassa payment, stores the YooKassa payment id, and redirects to the confirmation URL.

YooKassa routes:

- return URL: `/payments/yookassa/return?order_id=<id>`
- webhook URL: `/webhooks/yookassa`

The return/webhook handling verifies payment id, order metadata, amount, and currency before marking an order paid. Stock is decremented once when an order becomes paid.

YooKassa receipt/fiscalization requirements depend on shop settings and legal setup. Confirm YooKassa receipt/54-FZ settings before production payments; receipt payloads are not implemented unless required by the shop configuration.

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
