import os


TRUE_VALUES = {"1", "true", "yes", "on"}


def as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in TRUE_VALUES


def load_config(app):
    app.config["APP_MODE"] = os.environ.get("APP_MODE", "").strip()
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-baikal-stone-market")
    app.config["STORE_CURRENCY"] = os.environ.get("STORE_CURRENCY", "RUB").upper()
    app.config["PAYMENT_PROVIDER"] = os.environ.get("PAYMENT_PROVIDER", "").strip().lower()
    app.config["YOOKASSA_ENABLED"] = as_bool(os.environ.get("YOOKASSA_ENABLED"), False)
    app.config["YOOKASSA_SHOP_ID"] = os.environ.get("YOOKASSA_SHOP_ID", "")
    app.config["YOOKASSA_SECRET_KEY"] = os.environ.get("YOOKASSA_SECRET_KEY", "")
    app.config["YOOKASSA_RETURN_URL_BASE"] = os.environ.get(
        "YOOKASSA_RETURN_URL_BASE",
        "http://127.0.0.1:5000/payments/yookassa/return",
    )
    app.config["YOOKASSA_RECEIPTS_ENABLED"] = as_bool(
        os.environ.get("YOOKASSA_RECEIPTS_ENABLED"), False
    )
    app.config["YOOKASSA_VAT_CODE"] = os.environ.get("YOOKASSA_VAT_CODE", "")
    app.config["YOOKASSA_PAYMENT_MODE"] = os.environ.get("YOOKASSA_PAYMENT_MODE", "")
    app.config["YOOKASSA_PAYMENT_SUBJECT"] = os.environ.get("YOOKASSA_PAYMENT_SUBJECT", "")
    app.config["TELEGRAM_NOTIFICATIONS_ENABLED"] = as_bool(
        os.environ.get("TELEGRAM_NOTIFICATIONS_ENABLED"), False
    )
    app.config["TELEGRAM_DEV_MODE"] = as_bool(os.environ.get("TELEGRAM_DEV_MODE"), False)
    app.config["TELEGRAM_BOT_TOKEN"] = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    app.config["TELEGRAM_CHAT_ID"] = os.environ.get("TELEGRAM_CHAT_ID", "")
    app.config["TELEGRAM_WEBHOOK_SECRET"] = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
    app.config["TELEGRAM_ALLOWED_USER_IDS"] = os.environ.get("TELEGRAM_ALLOWED_USER_IDS", "")
    app.config["TELEGRAM_ALLOWED_CHAT_IDS"] = os.environ.get("TELEGRAM_ALLOWED_CHAT_IDS", "")


def yookassa_ready(config):
    return bool(
        config.get("YOOKASSA_ENABLED")
        and config.get("YOOKASSA_SHOP_ID")
        and config.get("YOOKASSA_SECRET_KEY")
    )


def fake_payments_ready(config):
    return (
        config.get("APP_MODE") == "dev_flow"
        and config.get("PAYMENT_PROVIDER") == "fake_yookassa"
    )


def telegram_ready(config):
    return bool(
        config.get("TELEGRAM_NOTIFICATIONS_ENABLED")
        and config.get("TELEGRAM_BOT_TOKEN")
        and config.get("TELEGRAM_CHAT_ID")
    )


def telegram_inbound_ready(config):
    return bool(
        telegram_ready(config)
        and config.get("TELEGRAM_WEBHOOK_SECRET")
    )


def _parse_csv_set(value):
    return {part.strip() for part in str(value or "").split(",") if part.strip()}


def telegram_allowed_chat_ids(config):
    allowed = _parse_csv_set(config.get("TELEGRAM_ALLOWED_CHAT_IDS"))
    if not allowed and config.get("TELEGRAM_CHAT_ID"):
        allowed.add(str(config["TELEGRAM_CHAT_ID"]))
    return allowed


def telegram_allowed_user_ids(config):
    return _parse_csv_set(config.get("TELEGRAM_ALLOWED_USER_IDS"))
