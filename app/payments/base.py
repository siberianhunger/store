from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PaymentResult:
    status: str
    payment_reference: str | None = None
    redirect_url: str | None = None
    provider: str = "manual"
    order_status: str = "new"
    error: str | None = None
    payload: dict | None = None


class PaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, order):
        raise NotImplementedError


class PaymentProviderError(Exception):
    pass
