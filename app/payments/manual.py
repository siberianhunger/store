from .base import PaymentProvider, PaymentResult


class ManualPaymentProvider(PaymentProvider):
    provider = "manual"

    def create_payment(self, order):
        order_id = order["id"] if hasattr(order, "keys") else order.get("id")
        return PaymentResult(
            status="pending_manual",
            payment_reference=f"manual-{order_id}",
            redirect_url=None,
            provider=self.provider,
            order_status="new",
        )
