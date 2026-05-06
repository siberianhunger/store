from flask import session

from app import models
from app.i18n import t, tf


def _raw_cart():
    return session.setdefault("cart", {})


def get_quantity(product_id):
    return int(_raw_cart().get(str(product_id), 0))


def set_quantity(product_id, quantity):
    cart = _raw_cart()
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = int(quantity)
    session.modified = True


def add_item(product_id, quantity=1):
    product = models.get_product(product_id)
    if product is None:
        return t("product_not_found")
    next_quantity = get_quantity(product_id) + quantity
    if next_quantity > product["stock"]:
        return tf("only_available", stock=product["stock"])
    set_quantity(product_id, next_quantity)
    return None


def update_item(product_id, quantity):
    product = models.get_product(product_id)
    if product is None:
        return t("product_not_found")
    if quantity < 0:
        return t("quantity_negative")
    if quantity > product["stock"]:
        return tf("only_available", stock=product["stock"])
    set_quantity(product_id, quantity)
    return None


def clear_cart():
    session["cart"] = {}
    session.modified = True


def cart_items():
    items = []
    stale_ids = []
    for product_id, quantity in _raw_cart().items():
        product = models.get_product(int(product_id))
        if product is None:
            stale_ids.append(product_id)
            continue
        safe_quantity = min(int(quantity), product["stock"])
        items.append(
            {
                "product": product,
                "quantity": safe_quantity,
                "line_total_cents": product["price_cents"] * safe_quantity,
            }
        )
        if safe_quantity != int(quantity):
            session["cart"][product_id] = safe_quantity
            session.modified = True
    for product_id in stale_ids:
        session["cart"].pop(product_id, None)
        session.modified = True
    return items


def cart_summary():
    items = cart_items()
    return {
        "items": items,
        "item_count": sum(item["quantity"] for item in items),
        "total_cents": sum(item["line_total_cents"] for item in items),
    }
