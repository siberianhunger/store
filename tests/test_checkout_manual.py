from app import models
from tests.conftest import add_to_cart


def test_empty_checkout_redirects_to_cart(client):
    response = client.get("/checkout")
    assert response.status_code == 302
    assert "/cart" in response.headers["Location"]


def test_manual_checkout_persists_pending_order(app, client):
    add_to_cart(client, 1)
    response = client.post(
        "/checkout",
        data={
            "customer_name": "Test Buyer",
            "email": "buyer@example.com",
            "shipping_address": "Baikal street",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    with app.app_context():
        order = models.get_order(1)
        assert order["payment_status"] == "pending_manual"
        assert order["payment_provider"] == "manual"
        assert order["total_cents"] == 1800
