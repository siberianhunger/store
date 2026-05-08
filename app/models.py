import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from flask import current_app

from app.db import get_db, transaction


class InsufficientStockError(Exception):
    pass


def row_to_dict(row):
    return dict(row) if row is not None else None


def list_products(color_family=None):
    db = get_db()
    if color_family:
        return db.execute(
            "SELECT * FROM products WHERE color_family = ? ORDER BY is_featured DESC, id",
            (color_family,),
        ).fetchall()
    return db.execute("SELECT * FROM products ORDER BY is_featured DESC, id").fetchall()


def list_color_families():
    return get_db().execute(
        "SELECT DISTINCT color_family FROM products ORDER BY color_family"
    ).fetchall()


def get_product(product_id):
    return get_db().execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()


def get_product_by_slug(slug):
    return get_db().execute("SELECT * FROM products WHERE slug = ?", (slug,)).fetchone()


def normalize_email(email):
    return (email or "").strip().casefold()


def generate_public_code():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    suffix = "".join(secrets.choice(alphabet) for _ in range(6))
    return f"BSM-{stamp}-{suffix}"


def generate_access_key():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))


def hash_access_key(access_key):
    pepper = current_app.config["SECRET_KEY"].encode("utf-8")
    normalized = (access_key or "").strip().upper().encode("utf-8")
    return hmac.new(pepper, normalized, hashlib.sha256).hexdigest()


def access_key_matches(order, access_key):
    if order is None or not order["access_token_hash"]:
        return False
    return hmac.compare_digest(order["access_token_hash"], hash_access_key(access_key))


def _unique_public_code(db):
    for _ in range(20):
        public_code = generate_public_code()
        exists = db.execute(
            "SELECT 1 FROM orders WHERE public_code = ?", (public_code,)
        ).fetchone()
        if not exists:
            return public_code
    raise RuntimeError("Could not generate unique order code.")


def _reservation_expiry(minutes=45):
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).replace(microsecond=0).isoformat()


def create_order_from_cart(
    customer,
    cart_items,
    status,
    payment_status,
    payment_provider,
    reserve_stock=False,
):
    total_cents = sum(item["line_total_cents"] for item in cart_items)
    access_key = generate_access_key()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    with transaction() as db:
        public_code = _unique_public_code(db)
        cursor = db.execute(
            """
            INSERT INTO orders (
                customer_name, email, phone, shipping_address, status,
                payment_status, payment_provider, total_cents, public_code,
                access_token_hash, access_token_created_at, customer_email_normalized,
                reserved_at, reservation_expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                customer["customer_name"],
                customer["email"],
                customer.get("phone", ""),
                customer["shipping_address"],
                status,
                payment_status,
                payment_provider,
                total_cents,
                public_code,
                hash_access_key(access_key),
                now,
                normalize_email(customer["email"]),
                now if reserve_stock else None,
                _reservation_expiry() if reserve_stock else None,
            ),
        )
        order_id = cursor.lastrowid
        for item in cart_items:
            product = item["product"]
            quantity = item["quantity"]
            current_product = db.execute(
                "SELECT stock FROM products WHERE id = ?", (product["id"],)
            ).fetchone()
            if current_product is None or current_product["stock"] < quantity:
                raise InsufficientStockError(product["id"])
            db.execute(
                """
                INSERT INTO order_items (
                    order_id, product_id, product_name, unit_price_cents, quantity
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    product["id"],
                    product["name"],
                    product["price_cents"],
                    quantity,
                ),
            )
            if reserve_stock:
                result = db.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?",
                    (quantity, product["id"], quantity),
                )
                if result.rowcount != 1:
                    raise InsufficientStockError(product["id"])
    return order_id, access_key


def update_order_payment(order_id, **fields):
    allowed = {
        "status",
        "payment_status",
        "payment_reference",
        "payment_redirect_url",
        "payment_error",
        "payment_payload_json",
        "paid_at",
        "stock_decremented_at",
        "telegram_paid_notified_at",
        "telegram_manual_notified_at",
        "reservation_released_at",
        "canceled_at",
        "refunded_at",
        "refund_reference",
        "refund_status",
        "refund_error",
        "receipt_status",
        "receipt_error",
        "shipping_carrier",
        "shipping_tracking_number",
        "shipping_tracking_url",
        "shipping_public_note",
        "shipped_at",
        "shipping_updated_at",
        "shipping_updated_by_chat_id",
        "shipping_updated_by_user_id",
    }
    updates = {key: value for key, value in fields.items() if key in allowed}
    if not updates:
        return False
    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [order_id]
    get_db().execute(f"UPDATE orders SET {assignments} WHERE id = ?", values)
    get_db().commit()
    return True


def get_order(order_id):
    return get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()


def get_order_by_public_code(public_code):
    return get_db().execute(
        "SELECT * FROM orders WHERE public_code = ?", (public_code,)
    ).fetchone()


def list_orders(limit=50):
    return get_db().execute(
        "SELECT * FROM orders ORDER BY created_at DESC, id DESC LIMIT ?", (limit,)
    ).fetchall()


def get_order_items(order_id):
    return get_db().execute(
        "SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order_id,)
    ).fetchall()


def _restore_reserved_stock(db, order_id):
    items = db.execute(
        "SELECT product_id, quantity FROM order_items WHERE order_id = ? ORDER BY id",
        (order_id,),
    ).fetchall()
    for item in items:
        db.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )


def release_order_reservation(order_id, *, status=None, payment_status=None, payment_error=None):
    with transaction() as db:
        order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if order is None:
            return False
        if order["reserved_at"] and not order["reservation_released_at"] and order["status"] != "paid":
            _restore_reserved_stock(db, order_id)
            db.execute(
                "UPDATE orders SET reservation_released_at = CURRENT_TIMESTAMP WHERE id = ?",
                (order_id,),
            )
        updates = {}
        if status is not None:
            updates["status"] = status
        if payment_status is not None:
            updates["payment_status"] = payment_status
        if payment_error is not None:
            updates["payment_error"] = payment_error
        if updates:
            assignments = ", ".join(f"{key} = ?" for key in updates)
            db.execute(
                f"UPDATE orders SET {assignments} WHERE id = ?",
                list(updates.values()) + [order_id],
            )
    return True


def release_expired_reservations(now=None):
    now = now or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    released = 0
    db = get_db()
    candidates = db.execute(
        """
        SELECT id FROM orders
        WHERE reserved_at IS NOT NULL
          AND reservation_released_at IS NULL
          AND paid_at IS NULL
          AND status != 'paid'
          AND reservation_expires_at IS NOT NULL
          AND reservation_expires_at <= ?
        ORDER BY id
        """,
        (now,),
    ).fetchall()
    for row in candidates:
        if release_order_reservation(
            row["id"],
            status="payment_failed",
            payment_status="canceled",
            payment_error="Payment reservation expired.",
        ):
            released += 1
    return released


def mark_order_paid(order_id):
    with transaction() as db:
        order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if order is None:
            return False
        if order["status"] == "paid":
            return True
        if not order["reserved_at"] and not order["stock_decremented_at"]:
            items = db.execute(
                "SELECT product_id, quantity FROM order_items WHERE order_id = ? ORDER BY id",
                (order_id,),
            ).fetchall()
            for item in items:
                product = db.execute(
                    "SELECT stock FROM products WHERE id = ?", (item["product_id"],)
                ).fetchone()
                if product is None or product["stock"] < item["quantity"]:
                    db.execute(
                        """
                        UPDATE orders
                        SET status = 'manual_review',
                            payment_status = 'succeeded',
                            payment_error = ?
                        WHERE id = ?
                        """,
                        (
                            "Payment succeeded but stock is insufficient; manual handling required.",
                            order_id,
                        ),
                    )
                    return False
            for item in items:
                db.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    (item["quantity"], item["product_id"]),
                )
        db.execute(
            """
            UPDATE orders
            SET status = 'paid',
                payment_status = 'succeeded',
                paid_at = COALESCE(paid_at, CURRENT_TIMESTAMP),
                stock_decremented_at = COALESCE(stock_decremented_at, CURRENT_TIMESTAMP)
            WHERE id = ?
            """,
            (order_id,),
        )
    return True


def mark_telegram_paid_notified(order_id):
    db = get_db()
    cursor = db.execute(
        """
        UPDATE orders
        SET telegram_paid_notified_at = CURRENT_TIMESTAMP
        WHERE id = ? AND telegram_paid_notified_at IS NULL
        """,
        (order_id,),
    )
    db.commit()
    return cursor.rowcount == 1


def mark_telegram_manual_notified(order_id):
    db = get_db()
    cursor = db.execute(
        """
        UPDATE orders
        SET telegram_manual_notified_at = CURRENT_TIMESTAMP
        WHERE id = ? AND telegram_manual_notified_at IS NULL
        """,
        (order_id,),
    )
    db.commit()
    return cursor.rowcount == 1


TRACKING_URLS = {
    "cdek": "https://www.cdek.ru/ru/tracking?order_id={tracking_number}",
    "сдэк": "https://www.cdek.ru/ru/tracking?order_id={tracking_number}",
    "russianpost": "https://www.pochta.ru/tracking#{tracking_number}",
    "почтароссии": "https://www.pochta.ru/tracking#{tracking_number}",
    "boxberry": "https://boxberry.ru/tracking-page?id={tracking_number}",
}


def build_tracking_url(carrier, tracking_number):
    key = "".join(ch for ch in (carrier or "").casefold() if ch.isalnum())
    template = TRACKING_URLS.get(key)
    if not template:
        return None
    return template.format(tracking_number=(tracking_number or "").strip())


def update_order_shipping(
    public_code,
    carrier,
    tracking_number,
    note="",
    chat_id=None,
    user_id=None,
):
    carrier = (carrier or "").strip()
    tracking_number = (tracking_number or "").strip()
    note = (note or "").strip()
    if not carrier or not tracking_number:
        return False, "tracking number missing", None
    with transaction() as db:
        order = db.execute(
            "SELECT * FROM orders WHERE public_code = ?", ((public_code or "").strip().upper(),)
        ).fetchone()
        if order is None:
            return False, "order not found", None
        if order["status"] in {"canceled", "payment_failed"} or order["payment_status"] in {
            "canceled",
            "refunded",
            "refund_pending",
        }:
            return False, "order is canceled or refunded", order
        if order["status"] != "paid" or order["payment_status"] != "succeeded":
            return False, "order is not paid", order
        db.execute(
            """
            UPDATE orders
            SET status = 'shipped',
                shipping_carrier = ?,
                shipping_tracking_number = ?,
                shipping_tracking_url = ?,
                shipping_public_note = ?,
                shipped_at = COALESCE(shipped_at, CURRENT_TIMESTAMP),
                shipping_updated_at = CURRENT_TIMESTAMP,
                shipping_updated_by_chat_id = ?,
                shipping_updated_by_user_id = ?
            WHERE id = ?
            """,
            (
                carrier,
                tracking_number,
                build_tracking_url(carrier, tracking_number),
                note,
                str(chat_id) if chat_id is not None else None,
                str(user_id) if user_id is not None else None,
                order["id"],
            ),
        )
        updated = db.execute("SELECT * FROM orders WHERE id = ?", (order["id"],)).fetchone()
    return True, "tracking saved", updated


def refund_order(order_id, refund_reference, status="succeeded"):
    fields = {
        "refund_reference": refund_reference,
        "refund_status": status,
        "payment_status": "refunded" if status == "succeeded" else "refund_pending",
    }
    if status == "succeeded":
        fields["refunded_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return update_order_payment(order_id, **fields)
