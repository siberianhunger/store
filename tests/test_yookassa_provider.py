import httpx

from app.payments.yookassa import YooKassaPaymentProvider


class FakeClient:
    def __init__(self):
        self.request = None

    def post(self, url, **kwargs):
        self.request = (url, kwargs)
        return httpx.Response(
            200,
            json={
                "id": "pay_123",
                "status": "pending",
                "amount": {"value": "18.00", "currency": "RUB"},
                "confirmation": {"confirmation_url": "https://pay.example/123"},
                "metadata": {"order_id": "1"},
            },
            request=httpx.Request("POST", url),
        )


def test_yookassa_payload_contains_required_fields(app):
    app.config.update(
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
        YOOKASSA_RETURN_URL_BASE="http://localhost/payments/yookassa/return",
    )
    client = FakeClient()
    provider = YooKassaPaymentProvider(client=client)
    with app.app_context():
        result = provider.create_payment({"id": 1, "total_cents": 1800})
    url, kwargs = client.request
    assert url.endswith("/payments")
    assert kwargs["headers"]["Idempotence-Key"] == "order-1-payment-v1"
    assert kwargs["json"]["amount"] == {"value": "18.00", "currency": "RUB"}
    assert kwargs["json"]["capture"] is True
    assert kwargs["json"]["confirmation"]["return_url"].endswith("?order_id=1")
    assert kwargs["json"]["metadata"]["order_id"] == "1"
    assert result.payment_reference == "pay_123"
    assert result.redirect_url == "https://pay.example/123"
