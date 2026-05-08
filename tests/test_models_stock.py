from app import db, models

from tests.test_models_orders import CUSTOMER, cart_item


def test_reserved_stock_is_finalized_once_when_paid(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, _ = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product)],
            status="awaiting_payment",
            payment_status="pending",
            payment_provider="yookassa",
            reserve_stock=True,
        )
        assert models.get_product(1)["stock"] == product["stock"] - 1
        assert models.mark_order_paid(order_id)
        assert models.mark_order_paid(order_id)
        order = models.get_order(order_id)
        assert order["status"] == "paid"
        assert order["stock_decremented_at"]
        assert models.get_product(1)["stock"] == product["stock"] - 1


def test_payment_creation_failure_releases_reservation(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, _ = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product)],
            status="awaiting_payment",
            payment_status="pending",
            payment_provider="yookassa",
            reserve_stock=True,
        )
        assert models.get_product(1)["stock"] == product["stock"] - 1
        assert models.release_order_reservation(
            order_id,
            status="payment_error",
            payment_status="error",
            payment_error="failed",
        )
        order = models.get_order(order_id)
        assert order["reservation_released_at"]
        assert order["status"] == "payment_error"
        assert models.get_product(1)["stock"] == product["stock"]


def test_expired_reservation_cleanup_releases_unpaid_stock(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, _ = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product)],
            status="awaiting_payment",
            payment_status="pending",
            payment_provider="yookassa",
            reserve_stock=True,
        )
        db.get_db().execute(
            "UPDATE orders SET reservation_expires_at = '2000-01-01T00:00:00+00:00' WHERE id = ?",
            (order_id,),
        )
        db.get_db().commit()
        assert models.release_expired_reservations() == 1
        order = models.get_order(order_id)
        assert order["reservation_released_at"]
        assert order["payment_status"] == "canceled"
        assert models.get_product(1)["stock"] == product["stock"]


def test_unreserved_paid_transition_manual_review_on_insufficient_stock(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, _ = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product, product["stock"])],
            status="awaiting_payment",
            payment_status="pending",
            payment_provider="yookassa",
        )
        db.get_db().execute("UPDATE products SET stock = 0 WHERE id = 1")
        db.get_db().commit()
        assert not models.mark_order_paid(order_id)
        order = models.get_order(order_id)
        assert order["status"] == "manual_review"
        assert order["payment_status"] == "succeeded"


def test_notification_marking_is_idempotent(app):
    with app.app_context():
        product = models.get_product(1)
        order_id, _ = models.create_order_from_cart(
            CUSTOMER,
            [cart_item(product)],
            status="new",
            payment_status="pending_manual",
            payment_provider="manual",
        )
        assert models.mark_telegram_manual_notified(order_id)
        assert not models.mark_telegram_manual_notified(order_id)
        assert models.mark_telegram_paid_notified(order_id)
        assert not models.mark_telegram_paid_notified(order_id)
