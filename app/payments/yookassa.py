import json
from decimal import Decimal

import httpx
from flask import current_app

from app.payments.base import PaymentProvider, PaymentProviderError, PaymentResult


YOOKASSA_API = "https://api.yookassa.ru/v3"


def amount_from_minor_units(total_cents):
    return f"{Decimal(total_cents) / Decimal(100):.2f}"


class YooKassaPaymentProvider(PaymentProvider):
    provider = "yookassa"

    def __init__(self, client=None):
        self.client = client or httpx.Client(timeout=10)

    def create_payment(self, order):
        order_id = order["id"]
        currency = current_app.config["STORE_CURRENCY"]
        return_url = f"{current_app.config['YOOKASSA_RETURN_URL_BASE']}?order_id={order_id}"
        payload = {
            "amount": {
                "value": amount_from_minor_units(order["total_cents"]),
                "currency": currency,
            },
            "capture": True,
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "description": f"Order #{order_id}"[:128],
            "metadata": {
                "order_id": str(order_id),
            },
        }
        try:
            response = self.client.post(
                f"{YOOKASSA_API}/payments",
                auth=(
                    current_app.config["YOOKASSA_SHOP_ID"],
                    current_app.config["YOOKASSA_SECRET_KEY"],
                ),
                headers={
                    "Idempotence-Key": f"order-{order_id}-payment-v1",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise PaymentProviderError(str(exc)) from exc
        data = response.json()
        confirmation = data.get("confirmation") or {}
        return PaymentResult(
            status=data.get("status", "pending"),
            payment_reference=data.get("id"),
            redirect_url=confirmation.get("confirmation_url"),
            provider=self.provider,
            order_status="awaiting_payment",
            payload=_sanitize_payload(data),
        )

    def fetch_payment(self, payment_id):
        try:
            response = self.client.get(
                f"{YOOKASSA_API}/payments/{payment_id}",
                auth=(
                    current_app.config["YOOKASSA_SHOP_ID"],
                    current_app.config["YOOKASSA_SECRET_KEY"],
                ),
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise PaymentProviderError(str(exc)) from exc
        return response.json()


def _sanitize_payload(data):
    allowed = {
        "id": data.get("id"),
        "status": data.get("status"),
        "paid": data.get("paid"),
        "amount": data.get("amount"),
        "confirmation": data.get("confirmation"),
        "metadata": data.get("metadata"),
        "created_at": data.get("created_at"),
    }
    return allowed


def dumps_payload(payload):
    return json.dumps(payload or {}, ensure_ascii=False)
