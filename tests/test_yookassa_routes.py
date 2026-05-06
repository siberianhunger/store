from app import models
from app.payments.base import PaymentResult
from app.routes import apply_yookassa_payment_status
from tests.conftest import add_to_cart


def create_pending_order(client, app):
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
        models.update_order_payment(
            1,
            status="awaiting_payment",
            payment_status="pending",
            payment_provider="yookassa",
            payment_reference="pay_123",
        )


def test_yookassa_status_marks_paid_and_decrements_stock_once(app, client):
    create_pending_order(client, app)
    payment = {
        "id": "pay_123",
        "status": "succeeded",
        "amount": {"value": "18.00", "currency": "RUB"},
        "metadata": {"order_id": "1"},
    }
    with app.app_context():
        assert apply_yookassa_payment_status(1, payment)
        assert apply_yookassa_payment_status(1, payment)
        order = models.get_order(1)
        product = models.get_product(1)
        assert order["status"] == "paid"
        assert order["payment_status"] == "succeeded"
        assert product["stock"] == 3


def test_yookassa_mismatch_does_not_mark_paid(app, client):
    create_pending_order(client, app)
    payment = {
        "id": "wrong",
        "status": "succeeded",
        "amount": {"value": "18.00", "currency": "RUB"},
        "metadata": {"order_id": "1"},
    }
    with app.app_context():
        assert not apply_yookassa_payment_status(1, payment)
        assert models.get_order(1)["status"] == "awaiting_payment"


def test_yookassa_checkout_redirects_to_confirmation(app, client, monkeypatch):
    class FakeProvider:
        provider = "yookassa"

        def create_payment(self, order):
            return PaymentResult(
                status="pending",
                payment_reference="pay_redirect",
                redirect_url="https://pay.example/confirm",
                provider="yookassa",
                order_status="awaiting_payment",
                payload={"id": "pay_redirect"},
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
        assert order["payment_reference"] == "pay_redirect"
        assert order["payment_redirect_url"] == "https://pay.example/confirm"


def test_yookassa_return_route_refreshes_status(app, client, monkeypatch):
    create_pending_order(client, app)

    class FakeProvider:
        def fetch_payment(self, payment_id):
            return {
                "id": payment_id,
                "status": "succeeded",
                "amount": {"value": "18.00", "currency": "RUB"},
                "metadata": {"order_id": "1"},
            }

    app.config.update(
        YOOKASSA_ENABLED=True,
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
    )
    monkeypatch.setattr("app.routes.YooKassaPaymentProvider", FakeProvider)
    response = client.get("/payments/yookassa/return?order_id=1")
    assert response.status_code == 302
    with app.app_context():
        assert models.get_order(1)["status"] == "paid"
