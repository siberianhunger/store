from app import models
from app.notifications.telegram import send_order_paid_notification
from app.routes import maybe_send_manual_notification, maybe_send_paid_notification
from tests.conftest import add_to_cart


def test_manual_notification_is_distinct_and_idempotent(app, client, monkeypatch):
    calls = []
    monkeypatch.setattr("app.routes.send_manual_pending_order_notification", lambda order, items: calls.append(order["id"]) or True)
    add_to_cart(client, 1)
    client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    with app.app_context():
        maybe_send_manual_notification(1)
        maybe_send_manual_notification(1)
        assert calls == [1]
        assert models.get_order(1)["telegram_manual_notified_at"]


def test_paid_notification_is_idempotent(app, client, monkeypatch):
    calls = []
    monkeypatch.setattr("app.routes.send_order_paid_notification", lambda order, items: calls.append(order["id"]) or True)
    add_to_cart(client, 1)
    client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    with app.app_context():
        models.update_order_payment(1, status="paid", payment_status="succeeded")
        maybe_send_paid_notification(1)
        maybe_send_paid_notification(1)
        assert calls == [1]
        assert models.get_order(1)["telegram_paid_notified_at"]


def test_telegram_disabled_does_not_call_http(app, client, monkeypatch):
    called = []
    monkeypatch.setattr("app.notifications.telegram.httpx.post", lambda *a, **k: called.append(True))
    add_to_cart(client, 1)
    client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    with app.app_context():
        order = models.get_order(1)
        assert not send_order_paid_notification(order, models.get_order_items(1))
    assert called == []


def test_telegram_enabled_posts_message(app, client, monkeypatch):
    sent = {}

    class Response:
        def raise_for_status(self):
            return None

    def fake_post(url, **kwargs):
        sent["url"] = url
        sent["kwargs"] = kwargs
        return Response()

    monkeypatch.setattr("app.notifications.telegram.httpx.post", fake_post)
    app.config.update(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_CHAT_ID="chat",
    )
    add_to_cart(client, 1)
    client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "phone": "+79990000000",
            "shipping_address": "Baikal street",
        },
    )
    with app.app_context():
        order = models.get_order(1)
        assert send_order_paid_notification(order, models.get_order_items(1))
    assert sent["url"].endswith("/bottoken/sendMessage")
    assert sent["kwargs"]["json"]["chat_id"] == "chat"
    text = sent["kwargs"]["json"]["text"]
    assert "Order BSM-" in text
    assert "Order #1" not in text
    assert "Test Buyer" in text
    assert "buyer@example.com" in text
    assert "+79990000000" in text


def test_telegram_http_failure_returns_false(app, client, monkeypatch):
    import httpx

    def fake_post(url, **kwargs):
        raise httpx.ConnectError("down", request=httpx.Request("POST", url))

    monkeypatch.setattr("app.notifications.telegram.httpx.post", fake_post)
    app.config.update(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_CHAT_ID="chat",
    )
    add_to_cart(client, 1)
    client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    with app.app_context():
        assert not send_order_paid_notification(models.get_order(1), models.get_order_items(1))
