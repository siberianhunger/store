# Dev Server Full Flow Plan

Goal: make the local development server useful for manually testing the whole storefront flow: catalog browsing, cart, checkout, order tracking, fake payment approval/cancelation, webhook-like payment finalization, stock reservation/release, and real Telegram notifications through a developer-owned bot/chat.

## Current Situation

- `uv run python main.py` starts the Flask app on `http://127.0.0.1:5000`.
- Local config is loaded from `.env`.
- Manual checkout works without external services.
- YooKassa and Telegram integrations exist. YooKassa should stay fake/local for development, while Telegram should be testable with a real dev bot and dev chat.
- Tests already use fake providers, but there is no friendly dev-server flow for a human to click through fake payment success/cancelation.

## Desired Developer Experience

One command should start a safe local demo server:

```bash
uv run python scripts/dev_server.py
```

The server should:

- use a local SQLite dev database, for example `dev_store.db`
- seed deterministic products
- enable a local fake payment provider
- avoid real YooKassa, email, or other production external network calls
- allow real Telegram Bot API calls when a dev bot token and dev chat id are configured
- expose local fake payment pages/buttons for approve/cancel/fail paths
- keep order tracking realistic by using public order code + email + access key
- make it easy to reset local state

## Dev Config Profile

Add an explicit development-flow config profile instead of overloading production settings.

Suggested env/config values:

```bash
APP_MODE=dev_flow
DATABASE=dev_store.db
PAYMENT_PROVIDER=fake_yookassa
TELEGRAM_NOTIFICATIONS_ENABLED=true
TELEGRAM_BOT_TOKEN=<dev bot token>
TELEGRAM_CHAT_ID=<dev chat id>
TELEGRAM_DEV_MODE=true
YOOKASSA_ENABLED=false
```

Rules:

- Prefer `PAYMENT_PROVIDER=fake_yookassa` over a second fake-payment flag. The current app already chooses a provider in `app/payments/__init__.py`; extend that decision point instead of adding parallel config paths.
- If `PAYMENT_PROVIDER=fake_yookassa`, never instantiate the real YooKassa HTTP provider and do not require YooKassa credentials.
- Telegram is the one intentional real external integration in dev-flow mode. Use a separate dev bot and dev chat, never a production bot/chat.
- If fake payment mode is active and real-looking YooKassa credentials are present, either ignore them with a clear startup warning or fail fast.
- If Telegram is enabled in dev-flow mode, require `TELEGRAM_DEV_MODE=true` plus explicit `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
- Keep fake mode opt-in. Production must never use fake providers accidentally.
- Print a startup banner that says fake payments are active and Telegram dev notifications are real if configured.

## Fake Payment Provider

Add a local payment provider that implements the same app-level interface as YooKassa.

Suggested module:

```text
app/payments/fake_yookassa.py
```

Behavior:

- `create_payment(order)` creates a fake payment reference, stores a pending status, and returns a redirect URL to a local fake payment page.
- Redirect URL example:
  `/dev/payments/fake/<public_code>`
- The checkout route currently decides reservation/redirect behavior from `provider.provider == "yookassa"`. Either make the fake provider expose `provider = "yookassa"` with a clearly fake class/config path, or refactor the route to use a capability flag such as `requires_stock_reservation` / `uses_redirect_payment`. Do not let `fake_yookassa` accidentally fall through to manual-payment behavior.
- Metadata should mirror real YooKassa expectations:
  - internal `order_id`
  - `public_code`
  - expected amount/currency
- Never expose or store the raw order access key in fake payment metadata.
- Use deterministic idempotence-like keys in fake records so retry behavior can be inspected.

## Fake Payment UI

Add dev-only routes guarded by fake mode:

```text
GET  /dev/payments/fake/<public_code>
POST /dev/payments/fake/<public_code>/succeed
POST /dev/payments/fake/<public_code>/cancel
POST /dev/payments/fake/<public_code>/fail
```

The fake payment page should show:

- order code
- amount
- payment reference
- buttons for success, cancel, and failure
- a link back to the storefront

Actions:

- `succeed`: apply the same finalization path as a real YooKassa `succeeded` payment.
- `cancel`: release reservation and mark the order canceled/payment canceled.
- `fail`: simulate provider/payment error and leave a clear order state for manual inspection.

Important: reuse the same route/service logic that real YooKassa return/webhook handling uses where possible. Do not create a separate fake-only paid transition that skips payment matching, reservation finalization, or notification behavior.

## Dev Payment Tools

Add a small dev-only order/payment tools page. Keep it focused on manual flow testing, not a full admin panel.

Suggested routes:

```text
GET  /dev/tools/orders
POST /dev/tools/orders/<public_code>/payment/succeeded
POST /dev/tools/orders/<public_code>/payment/canceled
POST /dev/tools/orders/<public_code>/payment/mismatch
```

This lets a developer test:

- customer never returns from payment page, but webhook succeeds
- duplicate webhook does not double-decrement stock
- mismatched payment id/amount/currency/public code does not mark paid
- canceled webhook releases reserved stock

Keep these routes unavailable unless fake/dev-flow mode is active.

Implementation note: these actions should build fake YooKassa-shaped payloads and call `apply_yookassa_payment_status()` where possible, so the real matching and stock logic is still exercised.

## Real Telegram Dev Notifications

Use the actual Telegram integration in dev-flow mode so the developer can verify real owner notifications end to end.

Developer setup:

- register a separate Telegram bot for local/dev testing
- create a private dev chat or group for store notifications
- put only the dev bot token and dev chat id in local `.env`
- never commit `.env` or real Telegram credentials

Dev behavior:

- manual checkout should send the real manual pending Telegram notification when enabled
- fake YooKassa success/webhook success should send the real paid Telegram notification when enabled
- duplicate return/webhook flows should still mark notification timestamps idempotently and avoid duplicate Telegram messages
- Telegram failures should be visible in logs but should not break checkout/payment finalization
- startup should clearly show whether Telegram dev notifications are enabled

The real dev Telegram messages should let the developer verify:

- manual pending notification
- paid notification
- notification idempotency
- public order code is included
- no private access key is included

Optional helper route:

```text
POST /dev/tools/telegram/test
```

This route should be guarded by dev-flow mode and send a small real test message to the configured dev chat. It should never be available in production mode.

## Dev Reset And Seed Commands

Add scripts or CLI commands:

```bash
uv run python scripts/dev_server.py
uv run python scripts/reset_dev_db.py
```

`reset_dev_db.py` should:

- delete only the configured dev database, never production-looking paths
- recreate schema
- seed deterministic products
- optionally set one product to stock `1` for reservation/race testing

Add README instructions for:

- starting fake-flow dev server
- resetting dev database
- manual checkout flow
- fake YooKassa success/cancel/fail flow
- tracking order from a fresh browser session
- simulating webhook-only success
- configuring a real Telegram dev bot/chat
- sending a Telegram test notification

## Manual Test Checklist

The dev server should let a human verify these flows:

1. Manual checkout:
   - add product to cart
   - checkout
   - see public order code and access key
   - open order URL in private session and confirm private details are hidden
   - use tracking form with order code + email + access key

2. Fake YooKassa success:
   - enable fake payment provider
   - checkout redirects to local fake payment page
   - click success
   - return to order page
   - order shows paid
   - stock reservation is finalized once

3. Fake YooKassa cancel:
   - checkout reserves stock
   - click cancel on fake payment page
   - order shows canceled/payment canceled
   - stock is restored

4. Fake webhook success:
   - checkout and stop on fake payment page
   - trigger webhook success from `/dev/tools/orders`
   - order becomes paid without browser return
   - duplicate webhook keeps stock unchanged

5. Mismatch safety:
   - trigger fake mismatched webhook
   - order does not become paid
   - payment error/manual state is visible enough for debugging

6. Stock reservation:
   - reset dev DB with one product at stock `1`
   - first browser starts fake YooKassa checkout
   - second browser cannot create a payable order for the same item
   - cancel first payment
   - second browser can retry

7. Localization:
   - switch RU/EN
   - run checkout/tracking pages in both locales
   - verify fake dev pages are clear enough for local use

8. Real Telegram dev notifications:
   - configure a dev Telegram bot token and dev chat id
   - start dev-flow server with Telegram enabled
   - send a dev Telegram test message
   - complete manual checkout and verify the manual pending notification arrives
   - complete fake payment success and verify the paid notification arrives
   - repeat webhook/return action and verify duplicate Telegram messages are not sent
   - verify messages include public order code and never include the private access key

## Implementation Order

1. Add explicit config flags for `APP_MODE`, `PAYMENT_PROVIDER`, and `TELEGRAM_DEV_MODE`.
2. Add fake YooKassa provider class implementing the existing payment provider interface.
3. Update payment provider selection to return fake provider only in dev-flow mode.
4. Add dev-only fake payment routes and templates.
5. Reuse real payment application logic for fake success/cancel/mismatch.
6. Keep the real Telegram notifier active in dev-flow mode when dev Telegram credentials are configured.
7. Add `scripts/dev_server.py` and `scripts/reset_dev_db.py`.
8. Update `.env.example` with commented fake-flow settings.
9. Update `README.md` with a local full-flow testing section.
10. Add tests proving dev-only routes are disabled outside fake mode.
11. Add tests for fake payment success/cancel/mismatch and reset safety.
12. Add tests proving Telegram dev mode requires explicit dev config and does not expose test-send routes outside dev-flow mode.
13. Run:

```bash
uv run pytest
uv run pytest tests/e2e
uv run pytest --cov=app
```

## Acceptance Criteria

- A developer can test full purchase, tracking, fake payment, and real Telegram notification flows locally without real YooKassa accounts.
- Fake payment pages can mark orders succeeded, canceled, failed, and webhook-succeeded.
- Fake payment success/cancel paths use the same order/payment/stock transition logic as real YooKassa handling.
- Dev-only fake payment routes cannot be accessed unless dev-flow mode and `PAYMENT_PROVIDER=fake_yookassa` are enabled.
- Real YooKassa credentials are never required for local full-flow testing.
- Telegram dev credentials are supported and documented for real notification testing.
- Fake payment mode never sends real network requests to payment services.
- Telegram network requests go only through the real Telegram notifier and only when explicit dev Telegram config is enabled.
- Dev reset command cannot delete arbitrary or production-looking database paths.
- README documents the exact commands and manual click paths.
- Existing tests and E2E tests still pass.
