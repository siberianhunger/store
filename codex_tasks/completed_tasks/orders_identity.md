# Orders, Identity, And YooKassa Compatibility Plan

Goal: let customers track orders without store accounts, keep YooKassa payment mapping correct, and reduce the risk of accepting money for orders the store cannot fulfill.

## Source Notes From YooKassa Docs

Official docs checked:

- https://yookassa.ru/developers/payment-acceptance/getting-started/payment-process
- https://yookassa.ru/developers/using-api/interaction-format
- https://yookassa.ru/developers/using-api/webhooks
- https://yookassa.ru/developers/payment-acceptance/receipts/54fz/yoomoney/payments
- https://yookassa.ru/developers/payment-acceptance/after-the-payment/refunds

Relevant points:

- Create payments server-side with Basic Auth, `Idempotence-Key`, `amount`, `capture`, `confirmation.return_url`, `description`, and optional `metadata`.
- `metadata` is the right place to carry local order identifiers such as internal `order_id` and a public order code.
- The customer return URL is not proof of payment. Payment status must be verified by fetching the payment and/or handling webhooks.
- Webhooks should handle `payment.succeeded` and `payment.canceled`. Add `payment.waiting_for_capture` only if two-stage capture is actually chosen.
- With HTTP Basic Auth, webhook setup is done in the YooKassa dashboard.
- YooKassa requires idempotency keys for POST/DELETE requests.
- Fiscal receipts, if required by shop/legal settings, need `receipt.customer` and `receipt.items`; customer email or phone is needed for receipt delivery.
- Refunds require `payment_id`, amount, and idempotency keys.

## Current MVP Compatibility

Already good:

- Local order is created before payment.
- YooKassa payment request includes `metadata.order_id`.
- Local order stores YooKassa payment id in `payment_reference`.
- Return route fetches YooKassa payment by stored reference.
- Webhook route applies YooKassa payment object by metadata order id.
- Payment matching checks payment id, amount, currency, and metadata order id.
- Paid transition is idempotent and stock decrement is attempted once.

Gaps to fix:

- `/orders/<int:order_id>` is guessable and exposes order details to anyone who can enumerate ids.
- Return URL uses only sequential `order_id`.
- There is no customer-facing tracking page except the direct order page.
- There is no public order code or private access key.
- Stock is not reserved before creating a YooKassa payment, so two customers can attempt to buy the same low-stock item.
- If payment succeeds but stock is gone, current code moves the order to manual review after money was accepted. That avoids silent oversell, but still creates refund/manual handling risk.
- YooKassa receipt payload is not implemented. That is acceptable only if shop settings do not require receipts from this integration.
- There is no refund workflow for paid-but-unfulfillable or customer-canceled orders.

## Accountless Tracking Model

Do not add sign-in, Google auth, passwords, or customer accounts.

Use three identifiers:

- Internal numeric `orders.id`: private database id, never enough for public access.
- Public order code: human-readable and non-sequential enough for display, for example `BSM-20260506-K7P4Q2`.
- Private access key: random secret shown to the customer, stored only as a hash.

Customer flows:

- After checkout, save order ownership in the Flask session and redirect to `/orders/<public_code>`.
- Confirmation page shows the public order code and private access key. Tell the customer to save both.
- Header/footer has a "Track order" link.
- Tracking form asks for order code + email + access key.
- If order code/email/access key do not match, show a generic failure. Do not reveal which field was wrong or whether an order exists.
- Full details require the private access key or the same checkout session that created the order.
- Do not build email magic links until the project has a real email sender. For this store, access key plus manual support is enough.

Privacy rules:

- Never expose full shipping address, phone, or email from a guessable URL.
- Store only the access key hash, not the raw key.
- Do not log raw access keys.
- Do not put raw access keys into YooKassa `metadata` or `return_url`.
- Rotate/regenerate access keys only through manual operator action or a future verified email flow.
- Add rate limiting before public launch if `/track` is exposed to the open internet.

## Database Changes

Add idempotent migrations:

- `orders.public_code TEXT UNIQUE`
- `orders.access_token_hash TEXT`
- `orders.access_token_created_at TEXT`
- `orders.customer_email_normalized TEXT`
- `orders.reserved_at TEXT`
- `orders.reservation_expires_at TEXT`
- `orders.reservation_released_at TEXT`
- `orders.canceled_at TEXT`
- `orders.refunded_at TEXT`
- `orders.refund_reference TEXT`
- `orders.refund_status TEXT`
- `orders.refund_error TEXT`
- `orders.receipt_required INTEGER DEFAULT 0`
- `orders.receipt_status TEXT`
- `orders.receipt_error TEXT`

Optional later table for operator workflow:

```text
order_events
- id
- order_id
- event_type
- public_message_ru
- public_message_en
- private_note
- created_at
```

Do not add `order_events` in the next pass unless it is needed by an operator UI or customer timeline. Plain order columns are enough for the current store.

## Status Model

Keep status simple, but separate payment from fulfillment.

Customer-visible fulfillment status:

- `new`
- `awaiting_payment`
- `paid`
- `packing`
- `shipped`
- `canceled`
- `manual_review`

Payment status:

- `pending`
- `succeeded`
- `canceled`
- `refund_pending`
- `refunded`
- `refund_failed`

Order page should show:

- order code
- current payment status
- current fulfillment status
- items and total
- continue payment button if payment is pending and `payment_redirect_url` exists
- contact/support instruction for manual review
- no raw YooKassa internals except useful payment state

## Stock And Money Safety

Recommended first version for this small catalog:

1. On checkout submit, re-read products inside one DB transaction.
2. If stock is insufficient, reject checkout before creating payment.
3. Reserve stock before creating YooKassa payment.
4. For the first implementation, decrement visible `products.stock` during reservation and restore it if payment creation fails, payment is canceled, or reservation expires.
5. Store `reserved_at` and `reservation_expires_at` on the order.
6. If YooKassa payment is `succeeded`, convert the reservation to paid without decrementing twice.
7. Add a cleanup command that releases expired unpaid reservations.

Do not add `reserved_quantity` yet unless the simple reservation model becomes painful. The current app is a small souvenir catalog, not a warehouse system.

Later option:

- Use YooKassa two-stage payment with `capture=false`.
- On `payment.waiting_for_capture`, verify stock/reservation and then capture.
- If reservation cannot be honored, cancel the payment before capture.
- This is safer for one-of-one/high-value stock, but adds capture deadlines and operational complexity. Do not choose it for the next pass unless refund/manual handling risk is unacceptable.

Operational rule:

- Do not pack, ship, or notify "paid ready" until local payment matching has verified payment id, amount, currency, order identity, and final `succeeded` status.

## YooKassa Payment Payload Changes

Keep:

- `amount.value`
- `amount.currency = RUB`
- `capture`
- `confirmation.type = redirect`
- `confirmation.return_url`
- `description`
- `metadata.order_id`

Add or adjust:

- `metadata.public_code`
- `return_url` should use public code and no raw access key:
  `/payments/yookassa/return/<public_code>`
- On return, refresh payment status and redirect to `/orders/<public_code>`. If the session is gone, show the tracking form rather than exposing details.
- `description` should use the public order code, max 128 chars.
- Idempotence key should be deterministic per payment attempt and short enough for YooKassa, for example `pay-<public_code>-v1`.

Receipt payload decision:

- Add config flags only when receipts are actually implemented:
  - `YOOKASSA_RECEIPTS_ENABLED=false`
  - `YOOKASSA_VAT_CODE`
  - `YOOKASSA_PAYMENT_MODE`
  - `YOOKASSA_PAYMENT_SUBJECT`
- If receipts are enabled, include `receipt.customer.email` or `receipt.customer.phone` and item lines.
- Confirm legal/54-FZ settings before production. Do not guess VAT or fiscalization settings.

## Routes

Customer routes:

- `GET /orders/<public_code>`: access-key/session-aware order detail page.
- `GET /track`: tracking form.
- `POST /track`: validate order code + email + access key, then show order details or a generic failure.

Do not add resend-link routes until email delivery exists.

Payment routes:

- `GET /payments/yookassa/return/<public_code>`: refresh YooKassa payment by stored payment reference, then redirect to the order page.
- Keep old `/payments/yookassa/return?order_id=` only temporarily for backward compatibility during migration.
- `POST /webhooks/yookassa`: server-to-server only, no customer access key. Use metadata to find local order and strict payment matching.

Admin/operator routes can come later. For now, manual support can be handled through database/admin shell plus Telegram notifications.

## Notifications

Customer email is required at checkout for contact and possible fiscal receipts. It should not become an authentication system by itself.

Telegram owner notifications should include public order code, not only numeric id.

Email notification can be a later task:

- `send_order_created_tracking_info(order)`
- `send_payment_succeeded(order)`
- `send_order_shipped(order)`

## Tests Required

Unit/model tests:

- public order code generated and unique
- access key generated once, raw key not stored
- access key hash validates correct key and rejects wrong key
- sequential numeric id no longer exposes private details
- order code + wrong email does not reveal whether an order exists
- order code + correct email but wrong access key does not reveal private details
- access-key-authenticated order page shows full order details
- unauthenticated order page shows only safe limited state or requires verification

YooKassa provider tests:

- payment payload includes `metadata.order_id` and `metadata.public_code`
- payment payload never includes raw access key in metadata
- return URL uses public code and never includes raw access key
- receipt payload is absent when disabled
- receipt payload includes customer/items when enabled and configured
- idempotence key is stable for the same payment attempt and within YooKassa length limits

Route/payment tests:

- checkout reserves stock before payment creation
- payment creation failure releases reservation
- canceled payment releases reservation
- succeeded payment converts reservation to sold exactly once
- webhook with mismatched id/amount/currency/public_code does not mark paid
- duplicate webhook does not double-decrement or double-notify
- old integer order URL does not leak private order info
- tracking form requires order code + email + access key and does not leak private data on failure

Refund tests:

- paid order can create refund request with payment id and amount
- refund idempotence key is stable per refund attempt
- refund success updates local status
- refund failure leaves order in manual review and records error

Operational tests:

- expired pending reservations are released by cleanup command
- cleanup does not release paid reservations
- manual review is created if an impossible state occurs

## Implementation Order

1. Add public order code and access key generation helpers.
2. Add DB migrations for public code, access key hash, reservation/refund/receipt fields.
3. Update order creation to generate public code and access key.
4. Replace customer-facing `/orders/<int:id>` redirects/templates with `/orders/<public_code>`.
5. Add access-key-aware order page and tracking form.
6. Add tests proving integer order enumeration no longer reveals private data.
7. Add stock reservation transaction before payment creation.
8. Add reservation release on payment creation failure/canceled/expired.
9. Update YooKassa payload with public code metadata and return URL without access key.
10. Add optional receipt payload builder behind config if production settings require receipts through this integration.
11. Add refund provider methods and local refund status model.
12. Add customer email notification provider only if email delivery is actually being introduced.
13. Add order timeline/events only when operator workflow needs it.
14. Add rate limiting before public launch.
15. Run unit, integration, and E2E tests.

## Acceptance Criteria

- Customers can track orders without accounts.
- A sequential numeric id is never enough to view private order details.
- Every order has a public code and private access key.
- Customer can access tracking through order code + email + access key, or through the original checkout session.
- YooKassa payment is still connected to local order through metadata and stored payment id.
- YooKassa return route and webhook both verify payment id, amount, currency, and order identity.
- Store does not create a YooKassa payment unless stock has been reserved.
- Store does not ship or mark fulfillable until payment is verified as final.
- Duplicate YooKassa callbacks are harmless.
- Canceled/expired payments release stock reservation.
- Refund path exists for paid orders that cannot be fulfilled.
- Receipt behavior is explicitly configured; production cannot silently assume fiscal settings.
- Tests cover identity, tracking, stock reservation, YooKassa matching, receipt payload config, refunds, and duplicate callbacks.
