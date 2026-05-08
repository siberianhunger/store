from app import create_app
from app.config import (
    as_bool,
    fake_payments_ready,
    telegram_allowed_chat_ids,
    telegram_allowed_user_ids,
    telegram_inbound_ready,
    telegram_ready,
    yookassa_ready,
)


def test_missing_integration_credentials_disable_providers(tmp_path, monkeypatch):
    monkeypatch.setenv("YOOKASSA_ENABLED", "true")
    monkeypatch.delenv("YOOKASSA_SHOP_ID", raising=False)
    monkeypatch.delenv("YOOKASSA_SECRET_KEY", raising=False)
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "db.sqlite")})
    assert not yookassa_ready(app.config)
    assert not telegram_ready(app.config)
    assert app.config["STORE_CURRENCY"] == "RUB"


def test_bool_parser():
    for value in ("1", "true", "yes", "on", "TRUE"):
        assert as_bool(value)
    for value in ("0", "false", "no", "off", "anything"):
        assert not as_bool(value)


def test_integration_ready_requires_all_fields(app):
    app.config.update(
        YOOKASSA_ENABLED=True,
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_CHAT_ID="chat",
    )
    assert yookassa_ready(app.config)
    assert telegram_ready(app.config)


def test_fake_payment_and_telegram_inbound_config(app):
    app.config.update(
        APP_MODE="dev_flow",
        PAYMENT_PROVIDER="fake_yookassa",
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_CHAT_ID="chat",
        TELEGRAM_WEBHOOK_SECRET="secret",
        TELEGRAM_ALLOWED_USER_IDS="11, 22",
    )
    assert fake_payments_ready(app.config)
    assert telegram_inbound_ready(app.config)
    assert telegram_allowed_chat_ids(app.config) == {"chat"}
    assert telegram_allowed_user_ids(app.config) == {"11", "22"}
