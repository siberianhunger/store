from flask import current_app

from app.config import yookassa_ready
from app.payments.manual import ManualPaymentProvider
from app.payments.yookassa import YooKassaPaymentProvider


def get_payment_provider():
    if yookassa_ready(current_app.config):
        return YooKassaPaymentProvider()
    return ManualPaymentProvider()
