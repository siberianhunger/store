import re

from app import models
from app.payments.base import PaymentResult


def _block_cdn(page):
    page.route("https://unpkg.com/**", lambda route: route.abort())


def _fill_checkout(page, email="buyer@example.com"):
    page.get_by_label(re.compile("Имя|Name")).fill("Browser Buyer")
    page.get_by_label(re.compile("Email")).fill(email)
    page.get_by_label(re.compile("Телефон|Phone")).fill("+79990000000")
    page.get_by_label(re.compile("Адрес|Shipping address")).fill("Baikal street")


def test_browser_manual_checkout_and_tracking(page, live_server):
    _block_cdn(page)
    page.goto(f"{live_server}/")
    page.locator(".stone-card form button").first.click()
    page.goto(f"{live_server}/checkout")
    _fill_checkout(page)
    page.get_by_role("button", name=re.compile("Оформить|Place order")).click()

    page.wait_for_url(re.compile(r"/orders/"))
    public_code = page.locator("h1").inner_text().split()[-1]
    access_key = page.locator(".order-access-box code").inner_text()
    assert page.get_by_text("buyer@example.com").is_visible()

    page.context.clear_cookies()
    page.goto(f"{live_server}/orders/{public_code}")
    assert not page.get_by_text("buyer@example.com").is_visible()
    page.get_by_role("main").get_by_role("link", name=re.compile("Отследить|Track order")).click()
    page.get_by_label(re.compile("Код заказа|Order code")).fill(public_code)
    page.get_by_label(re.compile("Email")).fill("buyer@example.com")
    page.get_by_label(re.compile("Ключ доступа|Access key")).fill(access_key)
    page.get_by_role("button", name=re.compile("Отследить|Track order")).click()

    page.wait_for_url(re.compile(r"/orders/"))
    assert page.get_by_text("buyer@example.com").is_visible()


def test_browser_yookassa_return_marks_order_paid(app, page, live_server, monkeypatch):
    _block_cdn(page)
    app.config.update(
        YOOKASSA_ENABLED=True,
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
    )

    class FakeCheckoutProvider:
        provider = "yookassa"

        def create_payment(self, order):
            return PaymentResult(
                status="pending",
                payment_reference="browser-pay",
                redirect_url=f"{live_server}/payments/yookassa/return/{order['public_code']}",
                provider="yookassa",
                order_status="awaiting_payment",
                payload={"id": "browser-pay"},
            )

    class FakeYooKassaProvider:
        def fetch_payment(self, payment_reference):
            return {
                "id": payment_reference,
                "status": "succeeded",
                "amount": {"value": "18.00", "currency": "RUB"},
                "metadata": {"order_id": "1"},
            }

    monkeypatch.setattr("app.routes.get_payment_provider", lambda: FakeCheckoutProvider())
    monkeypatch.setattr("app.routes.YooKassaPaymentProvider", FakeYooKassaProvider)

    page.goto(f"{live_server}/")
    page.locator(".stone-card form button").first.click()
    page.goto(f"{live_server}/checkout")
    _fill_checkout(page, email="paid@example.com")
    page.get_by_role("button", name=re.compile("Оформить|Place order")).click()

    page.wait_for_url(re.compile(r"/orders/"))
    assert page.get_by_text(re.compile("Оплачено|Paid")).is_visible()
    with app.app_context():
        assert models.get_order(1)["status"] == "paid"
