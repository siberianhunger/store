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
        public_code = order["public_code"] if "public_code" in order.keys() else None
        public_code = public_code or f"order-{order_id}"
        currency = current_app.config["STORE_CURRENCY"]
        return_url = f"{current_app.config['YOOKASSA_RETURN_URL_BASE'].rstrip('/')}/{public_code}"
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
            "description": f"Order {public_code}"[:128],
            "metadata": {
                "order_id": str(order_id),
                "public_code": public_code,
            },
        }
        receipt = build_receipt(order)
        if receipt:
            payload["receipt"] = receipt
        try:
            response = self.client.post(
                f"{YOOKASSA_API}/payments",
                auth=(
                    current_app.config["YOOKASSA_SHOP_ID"],
                    current_app.config["YOOKASSA_SECRET_KEY"],
                ),
                headers={
                    "Idempotence-Key": f"pay-{public_code}-v1"[:64],
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

    def create_refund(self, order, amount_value=None):
        amount_value = amount_value or amount_from_minor_units(order["total_cents"])
        public_code = order["public_code"] or f"order-{order['id']}"
        payload = {
            "payment_id": order["payment_reference"],
            "amount": {
                "value": amount_value,
                "currency": current_app.config["STORE_CURRENCY"],
            },
        }
        try:
            response = self.client.post(
                f"{YOOKASSA_API}/refunds",
                auth=(
                    current_app.config["YOOKASSA_SHOP_ID"],
                    current_app.config["YOOKASSA_SECRET_KEY"],
                ),
                headers={
                    "Idempotence-Key": f"refund-{public_code}-v1"[:64],
                    "Content-Type": "application/json",
                },
                json=payload,
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


def build_receipt(order):
    if not current_app.config.get("YOOKASSA_RECEIPTS_ENABLED"):
        return None
    vat_code = current_app.config.get("YOOKASSA_VAT_CODE")
    payment_mode = current_app.config.get("YOOKASSA_PAYMENT_MODE")
    payment_subject = current_app.config.get("YOOKASSA_PAYMENT_SUBJECT")
    if not (vat_code and payment_mode and payment_subject):
        raise PaymentProviderError("YooKassa receipts are enabled but receipt config is incomplete.")
    return {
        "customer": {"email": order["email"]},
        "items": [
            {
                "description": f"Order {order['public_code'] or order['id']}"[:128],
                "quantity": "1.00",
                "amount": {
                    "value": amount_from_minor_units(order["total_cents"]),
                    "currency": current_app.config["STORE_CURRENCY"],
                },
                "vat_code": int(vat_code),
                "payment_mode": payment_mode,
                "payment_subject": payment_subject,
            }
        ],
    }


def dumps_payload(payload):
    return json.dumps(payload or {}, ensure_ascii=False)
