import pytest

from app import models


CUSTOMER = {
    "customer_name": "Test Buyer",
    "email": "Buyer@Example.COM",
    "phone": "+79990000000",
    "shipping_address": "Baikal street",
}


def cart_item(product, quantity=1):
    return {
        "product": product,
        "quantity": quantity,
        "line_total_cents": product["price_cents"] * quantity,
    }


def test_create_order_from_cart_stores_identity_and_snapshots(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, access_key = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product, 2)],
            status="new",
            payment_status="pending_manual",
            payment_provider="manual",
        )
        order = models.get_order(order_id)
        items = models.get_order_items(order_id)
        assert order["public_code"].startswith("BSM-")
        assert access_key
        assert order["access_token_hash"] != access_key
        assert models.access_key_matches(order, access_key)
        assert order["customer_email_normalized"] == "buyer@example.com"
        assert order["total_cents"] == product["price_cents"] * 2
        assert items[0]["product_name"] == product["name"]
        assert items[0]["unit_price_cents"] == product["price_cents"]


def test_order_insert_rolls_back_when_stock_is_insufficient(app):
    with app.app_context():
        product = models.get_product(1)
        with pytest.raises(models.InsufficientStockError):
            models.create_order_from_cart(
                CUSTOMER,
                [cart_item(product, product["stock"] + 1)],
                status="awaiting_payment",
                payment_status="pending",
                payment_provider="yookassa",
                reserve_stock=True,
            )
        assert models.get_order(1) is None


def test_update_order_payment_ignores_disallowed_fields(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, _ = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product)],
            status="new",
            payment_status="pending_manual",
            payment_provider="manual",
        )
        assert not models.update_order_payment(order_id, id=999, customer_name="Changed")
        order = models.get_order(order_id)
        assert order["id"] == order_id
        assert order["customer_name"] == "Test Buyer"
