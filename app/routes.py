from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from app import cart, models
from app.config import yookassa_ready
from app.i18n import (
    color_label,
    get_locale,
    localized_product_description,
    localized_product_name,
    switch_locale_response,
    t,
)
from app.notifications import (
    send_manual_pending_order_notification,
    send_order_paid_notification,
)
from app.payments import get_payment_provider
from app.payments.base import PaymentProviderError
from app.payments.yookassa import YooKassaPaymentProvider, dumps_payload

bp = Blueprint("store", __name__)


@bp.app_template_filter("money")
def money(minor_units):
    amount = minor_units / 100
    if get_locale() == "ru":
        return f"{amount:,.2f} ₽".replace(",", " ")
    return f"{amount:,.2f} {current_app.config['STORE_CURRENCY']}"


@bp.context_processor
def inject_cart_summary():
    return {
        "cart_summary": cart.cart_summary(),
        "locale": get_locale(),
        "t": t,
        "color_label": color_label,
        "product_name": localized_product_name,
        "product_description": localized_product_description,
    }


def is_htmx():
    return request.headers.get("HX-Request") == "true"


def render_cart_response(status=200):
    template = "fragments/cart_drawer.html" if is_htmx() else "cart.html"
    return render_template(template, **cart.cart_summary()), status


@bp.get("/locale/<locale>")
def switch_locale(locale):
    return switch_locale_response(locale)


@bp.get("/media/<path:filename>")
def media(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)


@bp.get("/")
def index():
    selected_color = request.args.get("color") or ""
    products = models.list_products(selected_color or None)
    color_families = [row["color_family"] for row in models.list_color_families()]
    return render_template(
        "index.html",
        products=products,
        color_families=color_families,
        selected_color=selected_color,
    )


@bp.get("/fragments/products")
def product_grid_fragment():
    selected_color = request.args.get("color") or ""
    products = models.list_products(selected_color or None)
    return render_template(
        "fragments/product_grid.html",
        products=products,
        selected_color=selected_color,
    )


@bp.get("/products/<slug>")
def product_detail(slug):
    product = models.get_product_by_slug(slug)
    if product is None:
        abort(404)
    return render_template("product_detail.html", product=product)


@bp.post("/cart/add/<int:product_id>")
def cart_add(product_id):
    error = cart.add_item(product_id, 1)
    if error:
        return render_template("fragments/cart_drawer.html", error=error, **cart.cart_summary()), 400
    if is_htmx():
        return render_template("fragments/cart_drawer.html", **cart.cart_summary())
    return redirect(request.referrer or url_for("store.index"))


@bp.get("/cart")
def cart_page():
    return render_template("cart.html", **cart.cart_summary())


@bp.get("/fragments/cart")
def cart_fragment():
    return render_template("fragments/cart_drawer.html", **cart.cart_summary())


@bp.post("/cart/update/<int:product_id>")
def cart_update(product_id):
    try:
        quantity = int(request.form.get("quantity", "0"))
    except ValueError:
        quantity = 0
    error = cart.update_item(product_id, quantity)
    if error:
        return render_template("fragments/cart_drawer.html", error=error, **cart.cart_summary()), 400
    if is_htmx():
        return render_template("fragments/cart_drawer.html", **cart.cart_summary())
    return redirect(url_for("store.cart_page"))


@bp.post("/cart/remove/<int:product_id>")
def cart_remove(product_id):
    cart.set_quantity(product_id, 0)
    if is_htmx():
        return render_template("fragments/cart_drawer.html", **cart.cart_summary())
    return redirect(url_for("store.cart_page"))


@bp.get("/checkout")
def checkout():
    summary = cart.cart_summary()
    if not summary["items"]:
        return redirect(url_for("store.cart_page"))
    return render_template("checkout.html", errors={}, form={}, **summary)


@bp.post("/checkout")
def checkout_submit():
    summary = cart.cart_summary()
    form = {
        "customer_name": request.form.get("customer_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "shipping_address": request.form.get("shipping_address", "").strip(),
    }
    errors = {}
    if not summary["items"]:
        errors["cart"] = t("validation_cart_empty")
    if not form["customer_name"]:
        errors["customer_name"] = t("validation_name_required")
    if "@" not in form["email"] or "." not in form["email"]:
        errors["email"] = t("validation_email")
    if not form["shipping_address"]:
        errors["shipping_address"] = t("validation_address_required")
    for item in summary["items"]:
        if item["quantity"] > item["product"]["stock"]:
            errors["cart"] = t("validation_stock")
            break
    if errors:
        return render_template("checkout.html", errors=errors, form=form, **summary), 400

    provider = get_payment_provider()
    is_yookassa = getattr(provider, "provider", "manual") == "yookassa"
    order_id = models.create_order_from_cart(
        form,
        summary["items"],
        status="awaiting_payment" if is_yookassa else "new",
        payment_status="pending" if is_yookassa else "pending_manual",
        payment_provider=getattr(provider, "provider", "manual"),
    )
    order = models.get_order(order_id)
    try:
        payment_result = provider.create_payment(order)
    except PaymentProviderError as exc:
        models.update_order_payment(
            order_id,
            status="payment_error",
            payment_status="error",
            payment_error=str(exc),
        )
        return redirect(url_for("store.order_success", order_id=order_id))
    models.update_order_payment(
        order_id,
        status=payment_result.order_status,
        payment_status=payment_result.status,
        payment_reference=payment_result.payment_reference,
        payment_redirect_url=payment_result.redirect_url,
        payment_error=payment_result.error,
        payment_payload_json=dumps_payload(payment_result.payload),
    )
    order = models.get_order(order_id)
    if is_yookassa and payment_result.redirect_url:
        cart.clear_cart()
        return redirect(payment_result.redirect_url)
    if not is_yookassa:
        maybe_send_manual_notification(order_id)
    cart.clear_cart()
    return redirect(url_for("store.order_success", order_id=order_id))


@bp.get("/orders/<int:order_id>")
def order_success(order_id):
    order = models.get_order(order_id)
    if order is None:
        abort(404)
    items = models.get_order_items(order_id)
    return render_template("order_success.html", order=order, items=items)


@bp.get("/payments/yookassa/return")
def yookassa_return():
    order_id = request.args.get("order_id", type=int)
    if not order_id:
        abort(400)
    if yookassa_ready(current_app.config):
        refresh_yookassa_payment(order_id)
    return redirect(url_for("store.order_success", order_id=order_id))


@bp.post("/webhooks/yookassa")
def yookassa_webhook():
    payload = request.get_json(silent=True) or {}
    payment = payload.get("object") or {}
    metadata = payment.get("metadata") or {}
    try:
        order_id = int(metadata.get("order_id", "0"))
    except ValueError:
        return jsonify({"status": "ignored"}), 200
    if order_id:
        apply_yookassa_payment_status(order_id, payment)
    return jsonify({"status": "ok"}), 200


def refresh_yookassa_payment(order_id):
    order = models.get_order(order_id)
    if order is None or not order["payment_reference"]:
        return False
    provider = YooKassaPaymentProvider()
    try:
        payment = provider.fetch_payment(order["payment_reference"])
    except PaymentProviderError as exc:
        models.update_order_payment(order_id, payment_error=str(exc))
        return False
    return apply_yookassa_payment_status(order_id, payment)


def apply_yookassa_payment_status(order_id, payment):
    order = models.get_order(order_id)
    if order is None:
        return False
    if not payment_matches_order(order, payment):
        models.update_order_payment(order_id, payment_error="YooKassa payment payload mismatch.")
        return False
    status = payment.get("status")
    if status == "succeeded":
        paid = models.mark_order_paid(order_id)
        models.update_order_payment(
            order_id,
            payment_status="succeeded",
            payment_payload_json=dumps_payload(payment),
        )
        if paid:
            maybe_send_paid_notification(order_id)
        return paid
    if status == "canceled":
        if order["status"] != "paid":
            models.update_order_payment(
                order_id,
                status="payment_failed",
                payment_status="canceled",
                payment_payload_json=dumps_payload(payment),
            )
        return True
    models.update_order_payment(
        order_id,
        payment_status=status or "pending",
        payment_payload_json=dumps_payload(payment),
    )
    return True


def payment_matches_order(order, payment):
    if order["payment_reference"] and payment.get("id") != order["payment_reference"]:
        return False
    metadata = payment.get("metadata") or {}
    if metadata.get("order_id") and str(order["id"]) != str(metadata.get("order_id")):
        return False
    amount = payment.get("amount") or {}
    expected = f"{order['total_cents'] / 100:.2f}"
    return amount.get("value") == expected and amount.get("currency") == current_app.config["STORE_CURRENCY"]


def maybe_send_paid_notification(order_id):
    order = models.get_order(order_id)
    if order is None or order["telegram_paid_notified_at"]:
        return
    if send_order_paid_notification(order, models.get_order_items(order_id)):
        models.mark_telegram_paid_notified(order_id)


def maybe_send_manual_notification(order_id):
    order = models.get_order(order_id)
    if order is None or order["telegram_manual_notified_at"]:
        return
    if send_manual_pending_order_notification(order, models.get_order_items(order_id)):
        models.mark_telegram_manual_notified(order_id)
