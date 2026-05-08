import httpx
import pytest

from app.payments.base import PaymentProviderError
from app.payments.yookassa import YooKassaPaymentProvider, amount_from_minor_units


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
        result = provider.create_payment(
            {
                "id": 1,
                "public_code": "BSM-20260507-ABC123",
                "total_cents": 1800,
                "email": "buyer@example.com",
            }
        )
    url, kwargs = client.request
    assert url.endswith("/payments")
    assert kwargs["headers"]["Idempotence-Key"] == "pay-BSM-20260507-ABC123-v1"
    assert kwargs["json"]["amount"] == {"value": "18.00", "currency": "RUB"}
    assert kwargs["json"]["capture"] is True
    assert kwargs["json"]["confirmation"]["return_url"].endswith("/BSM-20260507-ABC123")
    assert kwargs["json"]["metadata"]["order_id"] == "1"
    assert kwargs["json"]["metadata"]["public_code"] == "BSM-20260507-ABC123"
    assert "access" not in str(kwargs["json"]["metadata"]).lower()
    assert result.payment_reference == "pay_123"
    assert result.redirect_url == "https://pay.example/123"


def test_amount_from_minor_units_formats_kopeks():
    assert amount_from_minor_units(0) == "0.00"
    assert amount_from_minor_units(1) == "0.01"
    assert amount_from_minor_units(1800) == "18.00"
    assert amount_from_minor_units(123456789) == "1234567.89"


def test_yookassa_create_payment_raises_controlled_error(app):
    class FailingClient:
        def post(self, url, **kwargs):
            raise httpx.ConnectError("network down", request=httpx.Request("POST", url))

    app.config.update(YOOKASSA_SHOP_ID="shop", YOOKASSA_SECRET_KEY="secret")
    provider = YooKassaPaymentProvider(client=FailingClient())
    with app.app_context(), pytest.raises(PaymentProviderError):
        provider.create_payment(
            {
                "id": 1,
                "public_code": "BSM-20260507-ABC123",
                "total_cents": 1800,
                "email": "buyer@example.com",
            }
        )


def test_yookassa_fetch_payment_and_refund(app):
    class Client:
        def __init__(self):
            self.calls = []

        def get(self, url, **kwargs):
            self.calls.append(("GET", url, kwargs))
            return httpx.Response(
                200,
                json={"id": "pay_123", "status": "succeeded"},
                request=httpx.Request("GET", url),
            )

        def post(self, url, **kwargs):
            self.calls.append(("POST", url, kwargs))
            return httpx.Response(
                200,
                json={"id": "refund_123", "status": "succeeded"},
                request=httpx.Request("POST", url),
            )

    app.config.update(YOOKASSA_SHOP_ID="shop", YOOKASSA_SECRET_KEY="secret")
    client = Client()
    provider = YooKassaPaymentProvider(client=client)
    order = {
        "id": 1,
        "public_code": "BSM-20260507-ABC123",
        "total_cents": 1800,
        "payment_reference": "pay_123",
    }
    with app.app_context():
        assert provider.fetch_payment("pay_123")["id"] == "pay_123"
        assert provider.create_refund(order)["id"] == "refund_123"
    assert client.calls[0][1].endswith("/payments/pay_123")
    assert client.calls[1][1].endswith("/refunds")
    assert client.calls[1][2]["headers"]["Idempotence-Key"] == "refund-BSM-20260507-ABC123-v1"


def test_yookassa_receipt_payload_requires_explicit_config(app):
    client = FakeClient()
    provider = YooKassaPaymentProvider(client=client)
    order = {
        "id": 1,
        "public_code": "BSM-20260507-ABC123",
        "total_cents": 1800,
        "email": "buyer@example.com",
    }
    app.config.update(
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
        YOOKASSA_RECEIPTS_ENABLED=True,
    )
    with app.app_context(), pytest.raises(PaymentProviderError):
        provider.create_payment(order)
    app.config.update(
        YOOKASSA_VAT_CODE="1",
        YOOKASSA_PAYMENT_MODE="full_payment",
        YOOKASSA_PAYMENT_SUBJECT="commodity",
    )
    with app.app_context():
        provider.create_payment(order)
    receipt = client.request[1]["json"]["receipt"]
    assert receipt["customer"]["email"] == "buyer@example.com"
    assert receipt["items"][0]["vat_code"] == 1
