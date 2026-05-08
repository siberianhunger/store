from flask import current_app, url_for

from app.payments.base import PaymentProvider, PaymentResult
from app.payments.yookassa import amount_from_minor_units


class FakeYooKassaPaymentProvider(PaymentProvider):
    provider = "yookassa"
    fake = True

    def create_payment(self, order):
        public_code = order["public_code"]
        payment_reference = f"fake-{public_code}"
        return PaymentResult(
            status="pending",
            payment_reference=payment_reference,
            redirect_url=url_for("store.fake_payment_page", public_code=public_code),
            provider=self.provider,
            order_status="awaiting_payment",
            payload=fake_payment_payload(order, payment_reference, "pending"),
        )


def fake_payment_payload(order, payment_reference, status, *, mismatch=False):
    amount_value = amount_from_minor_units(order["total_cents"])
    public_code = order["public_code"]
    return {
        "id": payment_reference,
        "status": status,
        "amount": {
            "value": "1.00" if mismatch else amount_value,
            "currency": "RUB" if mismatch else current_app.config["STORE_CURRENCY"],
        },
        "metadata": {
            "order_id": str(order["id"]),
            "public_code": "MISMATCH" if mismatch else public_code,
        },
    }
