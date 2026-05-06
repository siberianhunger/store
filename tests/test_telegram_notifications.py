from app import models
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
