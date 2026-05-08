from app import models
from app.payments import get_payment_provider
from tests.conftest import add_to_cart, checkout


def enable_fake_payments(app):
    app.config.update(
        APP_MODE="dev_flow",
        PAYMENT_PROVIDER="fake_yookassa",
        TELEGRAM_NOTIFICATIONS_ENABLED=False,
    )


def test_fake_payment_routes_are_disabled_without_dev_mode(client):
    response = client.get("/dev/tools/orders")
    assert response.status_code == 404


def test_fake_provider_selection(app):
    enable_fake_payments(app)
    with app.app_context():
        provider = get_payment_provider()
        assert provider.fake
        assert provider.provider == "yookassa"


def test_fake_payment_checkout_success_and_cancel(app, client):
    enable_fake_payments(app)
    add_to_cart(client, 1)
    response = checkout(client)
    assert response.status_code == 302
    assert "/dev/payments/fake/" in response.headers["Location"]
    with app.app_context():
        order = models.get_order(1)
        assert models.get_product(1)["stock"] == 3
    response = client.post(f"/dev/payments/fake/{order['public_code']}/succeed")
    assert response.status_code == 302
    with app.app_context():
        assert models.get_order(1)["status"] == "paid"
        assert models.get_product(1)["stock"] == 3


def test_fake_payment_page_and_failure(app, client):
    enable_fake_payments(app)
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
    page = client.get(f"/dev/payments/fake/{order['public_code']}")
    assert page.status_code == 200
    assert "Succeed" in page.get_data(as_text=True)
    response = client.post(f"/dev/payments/fake/{order['public_code']}/fail")
    assert response.status_code == 302
    with app.app_context():
        order = models.get_order(1)
        assert order["payment_status"] == "error"
        assert order["reservation_released_at"]
        assert models.get_product(1)["stock"] == 4


def test_fake_payment_cancel_releases_stock(app, client):
    enable_fake_payments(app)
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
    client.post(f"/dev/payments/fake/{order['public_code']}/cancel")
    with app.app_context():
        order = models.get_order(1)
        assert order["payment_status"] == "canceled"
        assert order["reservation_released_at"]
        assert models.get_product(1)["stock"] == 4


def test_dev_payment_mismatch_does_not_mark_paid(app, client):
    enable_fake_payments(app)
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
    response = client.post(f"/dev/tools/orders/{order['public_code']}/payment/mismatch")
    assert response.status_code == 302
    with app.app_context():
        order = models.get_order(1)
        assert order["status"] != "paid"
        assert "mismatch" in order["payment_error"].lower()


def test_dev_orders_page_and_payment_actions(app, client):
    enable_fake_payments(app)
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
    page = client.get("/dev/tools/orders")
    assert page.status_code == 200
    assert order["public_code"] in page.get_data(as_text=True)
    response = client.post(f"/dev/tools/orders/{order['public_code']}/payment/canceled")
    assert response.status_code == 302
    with app.app_context():
        assert models.get_order(1)["payment_status"] == "canceled"


def test_dev_telegram_test_route(app, client, monkeypatch):
    app.config.update(APP_MODE="dev_flow", TELEGRAM_DEV_MODE=True)
    monkeypatch.setattr("app.routes.send_telegram_message", lambda text: True)
    assert client.post("/dev/tools/telegram/test").get_json()["status"] == "sent"
    monkeypatch.setattr("app.routes.send_telegram_message", lambda text: False)
    assert client.post("/dev/tools/telegram/test").status_code == 502
