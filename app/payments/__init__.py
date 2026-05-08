from flask import current_app

from app.config import fake_payments_ready, yookassa_ready
from app.payments.fake_yookassa import FakeYooKassaPaymentProvider
from app.payments.manual import ManualPaymentProvider
from app.payments.yookassa import YooKassaPaymentProvider


def get_payment_provider():
    if fake_payments_ready(current_app.config):
        return FakeYooKassaPaymentProvider()
    if yookassa_ready(current_app.config):
        return YooKassaPaymentProvider()
    return ManualPaymentProvider()
