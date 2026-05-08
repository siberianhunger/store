from app import models
from app.payments.base import PaymentResult
from tests.conftest import add_to_cart


def test_e2e_manual_checkout_tracking_flow(app, client):
    assert client.get("/").status_code == 200
    add_to_cart(client, 1)
    assert client.get("/cart").status_code == 200
    response = client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "phone": "+79990000000",
            "shipping_address": "Baikal street",
        },
    )
    assert response.status_code == 302
    with client.session_transaction() as sess:
        access_key = sess["last_order_access_key"]
    order_page = client.get(response.headers["Location"])
    assert "buyer@example.com" in order_page.get_data(as_text=True)
    with app.app_context():
        order = models.get_order(1)
    fresh = app.test_client()
    denied = fresh.get(f"/orders/{order['public_code']}")
    assert "buyer@example.com" not in denied.get_data(as_text=True)
    tracked = fresh.post(
        "/track",
        data={
            "public_code": order["public_code"],
            "email": "buyer@example.com",
            "access_key": access_key,
        },
        follow_redirects=True,
    )
    assert "buyer@example.com" in tracked.get_data(as_text=True)


def test_e2e_yookassa_redirect_and_webhook_flow(app, client, monkeypatch):
    class FakeProvider:
        provider = "yookassa"

        def create_payment(self, order):
            return PaymentResult(
                status="pending",
                payment_reference="pay_e2e",
                redirect_url="https://pay.example/confirm",
                provider="yookassa",
                order_status="awaiting_payment",
                payload={"id": "pay_e2e"},
            )

    monkeypatch.setattr("app.routes.get_payment_provider", lambda: FakeProvider())
    add_to_cart(client, 1)
    response = client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "https://pay.example/confirm"
    with app.app_context():
        order = models.get_order(1)
        assert models.get_product(1)["stock"] == 3
    webhook = client.post(
        "/webhooks/yookassa",
        json={
            "object": {
                "id": "pay_e2e",
                "status": "succeeded",
                "amount": {"value": "18.00", "currency": "RUB"},
                "metadata": {"order_id": "1", "public_code": order["public_code"]},
            }
        },
    )
    assert webhook.status_code == 200
    with app.app_context():
        assert models.get_order(1)["status"] == "paid"
        assert models.get_product(1)["stock"] == 3
