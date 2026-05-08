from app import models
from tests.conftest import add_to_cart
from tests.test_yookassa_routes import create_pending_order


def test_yookassa_return_requires_order_id(client):
    assert client.get("/payments/yookassa/return").status_code == 400


def test_yookassa_webhook_ignores_bad_payloads(client):
    assert client.post("/webhooks/yookassa", data="not-json").status_code == 200
    assert client.post("/webhooks/yookassa", json={"object": {"metadata": {}}}).status_code == 200
    assert client.post(
        "/webhooks/yookassa",
        json={"object": {"metadata": {"order_id": "nope"}}},
    ).json == {"status": "ignored"}


def test_pending_payment_updates_status_without_paid(app, client):
    create_pending_order(client, app)
    response = client.post(
        "/webhooks/yookassa",
        json={
            "object": {
                "id": "pay_123",
                "status": "pending",
                "amount": {"value": "18.00", "currency": "RUB"},
                "metadata": {"order_id": "1"},
            }
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert models.get_order(1)["status"] == "awaiting_payment"


def test_canceled_payment_releases_reserved_stock(app, client, monkeypatch):
    class FakeProvider:
        provider = "yookassa"

        def create_payment(self, order):
            from app.payments.base import PaymentResult

            return PaymentResult(
                status="pending",
                payment_reference="pay_cancel",
                redirect_url="https://pay.example",
                provider="yookassa",
                order_status="awaiting_payment",
                payload={"id": "pay_cancel"},
            )

    monkeypatch.setattr("app.routes.get_payment_provider", lambda: FakeProvider())
    add_to_cart(client, 1)
    client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    response = client.post(
        "/webhooks/yookassa",
        json={
            "object": {
                "id": "pay_cancel",
                "status": "canceled",
                "amount": {"value": "18.00", "currency": "RUB"},
                "metadata": {"order_id": "1"},
            }
        },
    )
    assert response.status_code == 200
    with app.app_context():
        order = models.get_order(1)
        assert order["status"] == "payment_failed"
        assert order["reservation_released_at"]
        assert models.get_product(1)["stock"] == 4
