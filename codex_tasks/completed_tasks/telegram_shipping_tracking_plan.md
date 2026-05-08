# Telegram Shipping Tracking Plan

Goal: turn Telegram from a one-way owner notification channel into a practical operator workflow for updating shipping information after an order is packed and sent. The owner should be able to send a shipping carrier and tracking number through the Telegram bot, and the customer should see that tracking information on the order tracking page.

## Current Notification Situation

- The current app sends outbound Telegram notifications with `sendMessage`.
- There is no inbound Telegram webhook or polling command handler.
- Telegram notifications are currently optional and configured through:
  - `TELEGRAM_NOTIFICATIONS_ENABLED`
  - `TELEGRAM_BOT_TOKEN`
  - `TELEGRAM_CHAT_ID`
- Orders already have public order codes and protected customer tracking pages.
- Paid/manual notification timestamps are stored on the order to avoid duplicate sends.

## Desired Operator Flow

After the package is sent:

1. The owner opens the existing Telegram bot chat.
2. The owner sends a command containing:
   - order public code
   - shipping company/carrier
   - tracking number
   - optional public note
3. The Flask app receives the Telegram update.
4. The app verifies the sender/chat is authorized.
5. The app stores shipment tracking data on the matching order.
6. The app replies in Telegram with a clear success/failure message.
7. The customer can open the site tracking page and see the carrier/tracking number.

Do not build customer Telegram interactions. Telegram is for the store owner/operator only.

## Telegram Inbound Strategy

Use Telegram webhooks for production.

Add a route like:

```text
POST /webhooks/telegram/<secret>
```

Rules:

- The webhook URL must include an unguessable secret from env, for example `TELEGRAM_WEBHOOK_SECRET`.
- Only accept updates from the configured owner chat id or an allowlist.
- Ignore unknown chats and unauthorized users without exposing order data.
- Never accept shipping updates from public customer messages.
- Keep webhook processing fast and idempotent.

Optional local development:

- Prefer a real webhook even in staging/dev if the server has a public URL.
- Add a small polling script only if public webhook URLs are inconvenient during local testing.
- Example: `uv run python scripts/telegram_poll_dev.py`
- The production path should stay webhook-based.

## Configuration

Add env/config fields:

```bash
TELEGRAM_NOTIFICATIONS_ENABLED=true
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_WEBHOOK_SECRET=
TELEGRAM_ALLOWED_USER_IDS=
TELEGRAM_ALLOWED_CHAT_IDS=
```

Notes:

- `TELEGRAM_CHAT_ID` can remain the main owner notification chat.
- `TELEGRAM_ALLOWED_CHAT_IDS` should default to `TELEGRAM_CHAT_ID` if not set.
- `TELEGRAM_ALLOWED_USER_IDS` is useful for group chats where multiple people can see messages but only specific operators can update orders.
- Do not commit tokens, chat ids, or webhook secrets.

## Database Changes

Add idempotent order fields:

- `shipping_carrier TEXT`
- `shipping_tracking_number TEXT`
- `shipping_tracking_url TEXT`
- `shipping_public_note TEXT`
- `shipped_at TEXT`
- `shipping_updated_at TEXT`
- `shipping_updated_by_chat_id TEXT`
- `shipping_updated_by_user_id TEXT`

Optional later table:

```text
order_shipping_events
- id
- order_id
- carrier
- tracking_number
- tracking_url
- public_note
- source
- created_by
- created_at
```

For the first pass, order columns are enough. Add the event table only if edit history becomes important.

## Bot Command Design

Support only an explicit command in the first pass:

```text
/ship BSM-20260506-K7P4Q2 CDEK 123456789
/ship BSM-20260506-K7P4Q2 RussianPost 123456789 "Передано в доставку"
```

Do not implement reply-to-notification parsing in the first pass. It requires storing Telegram message ids and creates ambiguous failure modes. For a small store, explicit public order code in the command is clearer and safer.

Parsing rules:

- Normalize public order code to uppercase.
- Carrier is required.
- Tracking number is required.
- Optional note is public and will be visible to the customer.
- Reject ambiguous input with examples.
- Do not try to infer an order from customer name, email, or internal numeric id.
- Do not put private access keys in Telegram commands or bot replies.

## Carrier Tracking URLs

Add a small mapping helper for common carriers.

Example:

```text
CDEK -> https://www.cdek.ru/ru/tracking?order_id=<number>
RussianPost -> https://www.pochta.ru/tracking#<number>
Boxberry -> https://boxberry.ru/tracking-page?id=<number>
Other -> no generated URL unless explicitly supported
```

Rules:

- Store the raw carrier and tracking number exactly enough for operator/customer use.
- Generate `shipping_tracking_url` only for known carriers.
- If carrier is unknown, show carrier and number without a link.
- Keep the helper easily extendable.

## Order Page And Tracking UI

Update the protected order page to show shipping information when available:

- fulfillment status
- carrier
- tracking number
- tracking link when available
- public shipping note
- shipped date/time if present

Privacy:

- Shipping information should only appear when the customer has order access through session or access key.
- The public unauthenticated order URL should not reveal shipping address, email, phone, carrier, or tracking number.

Customer text:

- RU/EN localized labels.
- Clear states:
  - preparing
  - paid
  - shipped
  - canceled/refunded where applicable

## Order Status Updates

When a valid shipping command is accepted:

- set `status = 'shipped'` unless the order is canceled/refunded
- set `shipped_at` if empty
- set/update carrier/tracking fields
- set `shipping_updated_at`
- store Telegram chat/user identity in `shipping_updated_by_chat_id` and `shipping_updated_by_user_id`

Safety:

- Refuse shipping updates for unknown orders.
- Refuse shipping updates for canceled/refunded orders unless a future explicit override exists.
- Require the order to be paid before accepting shipping data. If manual payment orders need shipping before online status is available, add an explicit later operator override instead of silently allowing it.

## Telegram Replies

On success, reply:

```text
Tracking saved.
Order: BSM-...
Carrier: CDEK
Tracking: 123456789
Customer page: <site order URL>
```

The customer page URL is acceptable because the public order URL does not expose private details without the checkout session or access key. Still, the reply must not include email, phone, address, or access key.

On failure, reply with a short reason:

- order not found
- unauthorized chat/user
- invalid command format
- order is canceled/refunded
- tracking number missing

Do not include private access key in any Telegram reply.

## Tests Required

Add tests for:

- config readiness for inbound Telegram webhook
- webhook rejects wrong secret
- webhook ignores unauthorized chat/user
- `/ship` command parses valid input
- invalid command returns helpful failure
- unknown public order code does not update anything
- valid command stores carrier/tracking fields
- valid command moves paid order to `shipped`
- pending/manual order cannot be shipped by default
- canceled/refunded order cannot be shipped by default
- generated tracking URL for known carrier
- unknown carrier stores text but no URL
- order page shows tracking only to authenticated customer
- unauthenticated order page does not reveal tracking info
- Telegram success reply does not include access key

## Implementation Order

1. Add shipping tracking columns through idempotent migrations.
2. Add model helpers:
   - `update_order_shipping(public_code, carrier, tracking_number, note, updated_by)`
   - `build_tracking_url(carrier, tracking_number)`
3. Add Telegram inbound config helpers.
4. Add Telegram update parser for `/ship`.
5. Add Telegram webhook route guarded by secret/chat/user allowlist.
6. Add Telegram reply helper using existing bot token.
7. Update outbound Telegram order notifications to include `public_code`; stop relying on internal numeric id in operator-facing text.
8. Update order page template and i18n.
9. Add README instructions for registering the bot, setting webhook, and using `/ship`.
10. Add tests for parsing, authorization, DB updates, and UI privacy.
11. Run:

```bash
uv run pytest
uv run pytest --cov=app
```

## Acceptance Criteria

- Owner can send carrier/tracking number through Telegram and update an order by public code.
- Telegram inbound updates are authorized by secret and chat/user allowlist.
- Customer tracking page shows shipping carrier/tracking number only after access verification.
- Shipping updates require a paid order by default.
- Canceled/refunded orders are protected from accidental shipping updates.
- Telegram replies are useful and never include private access keys.
- Existing outbound paid/manual Telegram notifications still work.
- Existing tests pass and new shipping tracking tests cover the main safety paths.
