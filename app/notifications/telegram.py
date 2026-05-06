import httpx
from flask import current_app

from app.config import telegram_ready


def send_order_paid_notification(order, items):
    return _send_order_notification("paid order", order, items)


def send_manual_pending_order_notification(order, items):
    return _send_order_notification("manual pending order", order, items)


def _send_order_notification(event_type, order, items):
    if not telegram_ready(current_app.config):
        current_app.logger.info("Telegram notification skipped: disabled or missing config.")
        return False
    text = _build_message(event_type, order, items)
    url = f"https://api.telegram.org/bot{current_app.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
    try:
        response = httpx.post(
            url,
            json={
                "chat_id": current_app.config["TELEGRAM_CHAT_ID"],
                "text": text,
            },
            timeout=8,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        current_app.logger.warning("Telegram notification failed: %s", exc)
        return False
    return True


def _build_message(event_type, order, items):
    lines = [
        f"Baikal Stone Market: {event_type}",
        f"Order #{order['id']}",
        f"Status: {order['status']} / {order['payment_status']}",
        f"Customer: {order['customer_name']}",
        f"Email: {order['email']}",
    ]
    if order["phone"]:
        lines.append(f"Phone: {order['phone']}")
    lines.extend(
        [
            f"Address: {order['shipping_address']}",
            f"Total: {order['total_cents'] / 100:.2f} {current_app.config['STORE_CURRENCY']}",
            f"Provider: {order['payment_provider'] or 'manual'}",
            f"Reference: {order['payment_reference'] or '-'}",
            "Items:",
        ]
    )
    for item in items:
        lines.append(f"- {item['product_name']} x {item['quantity']}")
    return "\n".join(lines)
