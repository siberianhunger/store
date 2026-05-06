import pytest

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


def add_to_cart(client, product_id=1):
    return client.post(f"/cart/add/{product_id}")
