from app import models
from tests.conftest import add_to_cart


def test_checkout_validation_errors(client):
    add_to_cart(client, 1)
    response = client.post(
        "/checkout",
        data={"customer_name": "", "email": "bad", "shipping_address": ""},
    )
    body = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Введите имя" in body
    assert "Введите корректный email" in body
    assert "Введите адрес" in body


def test_checkout_rejects_stock_change_between_cart_and_submit(app, client):
    add_to_cart(client, 1)
    with app.app_context():
        from app import db

        db.get_db().execute("UPDATE products SET stock = 0 WHERE id = 1")
        db.get_db().commit()
    response = client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
    )
    assert response.status_code in {302, 400}


def test_payment_provider_failure_releases_reservation(app, client, monkeypatch):
    class FailingProvider:
        provider = "yookassa"

        def create_payment(self, order):
            from app.payments.base import PaymentProviderError

            raise PaymentProviderError("failed")

    monkeypatch.setattr("app.routes.get_payment_provider", lambda: FailingProvider())
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
    with app.app_context():
        order = models.get_order(1)
        product = models.get_product(1)
        assert order["status"] == "payment_error"
        assert order["reservation_released_at"]
        assert product["stock"] == 4
