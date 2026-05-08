import httpx
from flask import current_app, url_for

from app.config import (
    telegram_allowed_chat_ids,
    telegram_allowed_user_ids,
    telegram_ready,
)


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


def send_telegram_message(text, chat_id=None):
    if not telegram_ready(current_app.config):
        current_app.logger.info("Telegram message skipped: disabled or missing config.")
        return False
    url = f"https://api.telegram.org/bot{current_app.config['TELEGRAM_BOT_TOKEN']}/sendMessage"
    try:
        response = httpx.post(
            url,
            json={
                "chat_id": chat_id or current_app.config["TELEGRAM_CHAT_ID"],
                "text": text,
            },
            timeout=8,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        current_app.logger.warning("Telegram message failed: %s", exc)
        return False
    return True


def telegram_update_authorized(update):
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    sender = message.get("from") or {}
    chat_id = str(chat.get("id", ""))
    user_id = str(sender.get("id", ""))
    allowed_chats = telegram_allowed_chat_ids(current_app.config)
    allowed_users = telegram_allowed_user_ids(current_app.config)
    if allowed_chats and chat_id not in allowed_chats:
        return False
    if allowed_users and user_id not in allowed_users:
        return False
    return bool(chat_id)


def parse_ship_command(text):
    import shlex

    try:
        parts = shlex.split(text or "")
    except ValueError:
        return None
    if len(parts) < 4 or parts[0].split("@", 1)[0].casefold() != "/ship":
        return None
    return {
        "public_code": parts[1].strip().upper(),
        "carrier": parts[2].strip(),
        "tracking_number": parts[3].strip(),
        "note": " ".join(parts[4:]).strip(),
    }


def build_shipping_success_reply(order):
    public_code = order["public_code"]
    lines = [
        "Tracking saved.",
        f"Order: {public_code}",
        f"Carrier: {order['shipping_carrier']}",
        f"Tracking: {order['shipping_tracking_number']}",
        f"Customer page: {url_for('store.order_success', public_code=public_code, _external=True)}",
    ]
    return "\n".join(lines)


def _build_message(event_type, order, items):
    public_code = order["public_code"] if "public_code" in order.keys() and order["public_code"] else f"#{order['id']}"
    lines = [
        f"Baikal Stone Market: {event_type}",
        f"Order {public_code}",
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
