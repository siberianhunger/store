import pytest
import httpx

from app import create_app


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("YOOKASSA_ENABLED", "false")
    monkeypatch.setenv("TELEGRAM_NOTIFICATIONS_ENABLED", "false")
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "store.sqlite"),
            "WTF_CSRF_ENABLED": False,
        }
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def block_external_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("External HTTP is blocked in tests; use a fake client.")

    monkeypatch.setattr(httpx, "get", blocked)
    monkeypatch.setattr(httpx, "post", blocked)
    monkeypatch.setattr(httpx.Client, "request", blocked)


def add_to_cart(client, product_id=1):
    return client.post(f"/cart/add/{product_id}")


def checkout(client, **overrides):
    data = {
        "customer_name": "Test Buyer",
        "email": "buyer@example.com",
        "phone": "+79990000000",
        "shipping_address": "Baikal street",
    }
    data.update(overrides)
    return client.post("/checkout", data=data)
