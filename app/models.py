from app.db import get_db


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


def create_order(customer, cart_items, payment_result):
    total_cents = sum(item["line_total_cents"] for item in cart_items)
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO orders (
            customer_name, email, phone, shipping_address, status,
            payment_status, payment_reference, payment_provider,
            payment_redirect_url, payment_error, total_cents
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            customer["customer_name"],
            customer["email"],
            customer.get("phone", ""),
            customer["shipping_address"],
            getattr(payment_result, "order_status", "new"),
            payment_result.status,
            payment_result.payment_reference,
            payment_result.provider,
            payment_result.redirect_url,
            payment_result.error,
            total_cents,
        ),
    )
    order_id = cursor.lastrowid
    for item in cart_items:
        product = item["product"]
        db.execute(
            """
            INSERT INTO order_items (
                order_id, product_id, product_name, unit_price_cents, quantity
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (order_id, product["id"], product["name"], product["price_cents"], item["quantity"]),
        )
    db.commit()
    return order_id


def create_order_from_cart(customer, cart_items, status, payment_status, payment_provider):
    total_cents = sum(item["line_total_cents"] for item in cart_items)
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO orders (
            customer_name, email, phone, shipping_address, status,
            payment_status, payment_provider, total_cents
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
        ),
    )
    order_id = cursor.lastrowid
    for item in cart_items:
        product = item["product"]
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
                item["quantity"],
            ),
        )
    db.commit()
    return order_id


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
    }
    updates = {key: value for key, value in fields.items() if key in allowed}
    if not updates:
        return
    assignments = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [order_id]
    get_db().execute(f"UPDATE orders SET {assignments} WHERE id = ?", values)
    get_db().commit()


def get_order(order_id):
    return get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()


def get_order_items(order_id):
    return get_db().execute(
        "SELECT * FROM order_items WHERE order_id = ? ORDER BY id", (order_id,)
    ).fetchall()


def decrement_stock_for_paid_order(order_id):
    db = get_db()
    order = get_order(order_id)
    if order is None or order["stock_decremented_at"]:
        return True
    items = get_order_items(order_id)
    for item in items:
        product = get_product(item["product_id"])
        if product is None or product["stock"] < item["quantity"]:
            return False
    for item in items:
        db.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (item["quantity"], item["product_id"]),
        )
    db.execute(
        "UPDATE orders SET stock_decremented_at = CURRENT_TIMESTAMP WHERE id = ?",
        (order_id,),
    )
    db.commit()
    return True


def mark_order_paid(order_id):
    order = get_order(order_id)
    if order is None:
        return False
    if order["status"] == "paid":
        return True
    stock_ok = decrement_stock_for_paid_order(order_id)
    if not stock_ok:
        update_order_payment(
            order_id,
            status="manual_review",
            payment_status="succeeded",
            payment_error="Payment succeeded but stock is insufficient; manual handling required.",
        )
        return False
    db = get_db()
    db.execute(
        """
        UPDATE orders
        SET status = 'paid', payment_status = 'succeeded', paid_at = COALESCE(paid_at, CURRENT_TIMESTAMP)
        WHERE id = ?
        """,
        (order_id,),
    )
    db.commit()
    return True


def mark_telegram_paid_notified(order_id):
    db = get_db()
    db.execute(
        "UPDATE orders SET telegram_paid_notified_at = CURRENT_TIMESTAMP WHERE id = ?",
        (order_id,),
    )
    db.commit()


def mark_telegram_manual_notified(order_id):
    db = get_db()
    db.execute(
        "UPDATE orders SET telegram_manual_notified_at = CURRENT_TIMESTAMP WHERE id = ?",
        (order_id,),
    )
    db.commit()
