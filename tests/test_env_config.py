from app import create_app
from app.config import telegram_ready, yookassa_ready


def test_missing_integration_credentials_disable_providers(tmp_path, monkeypatch):
    monkeypatch.setenv("YOOKASSA_ENABLED", "true")
    monkeypatch.delenv("YOOKASSA_SHOP_ID", raising=False)
    monkeypatch.delenv("YOOKASSA_SECRET_KEY", raising=False)
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "db.sqlite")})
    assert not yookassa_ready(app.config)
    assert not telegram_ready(app.config)
    assert app.config["STORE_CURRENCY"] == "RUB"
