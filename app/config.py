import os


TRUE_VALUES = {"1", "true", "yes", "on"}


def as_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in TRUE_VALUES


def load_config(app):
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-baikal-stone-market")
    app.config["STORE_CURRENCY"] = os.environ.get("STORE_CURRENCY", "RUB").upper()
    app.config["YOOKASSA_ENABLED"] = as_bool(os.environ.get("YOOKASSA_ENABLED"), False)
    app.config["YOOKASSA_SHOP_ID"] = os.environ.get("YOOKASSA_SHOP_ID", "")
    app.config["YOOKASSA_SECRET_KEY"] = os.environ.get("YOOKASSA_SECRET_KEY", "")
    app.config["YOOKASSA_RETURN_URL_BASE"] = os.environ.get(
        "YOOKASSA_RETURN_URL_BASE",
        "http://127.0.0.1:5000/payments/yookassa/return",
    )
    app.config["TELEGRAM_NOTIFICATIONS_ENABLED"] = as_bool(
        os.environ.get("TELEGRAM_NOTIFICATIONS_ENABLED"), False
    )
    app.config["TELEGRAM_BOT_TOKEN"] = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    app.config["TELEGRAM_CHAT_ID"] = os.environ.get("TELEGRAM_CHAT_ID", "")


def yookassa_ready(config):
    return bool(
        config.get("YOOKASSA_ENABLED")
        and config.get("YOOKASSA_SHOP_ID")
        and config.get("YOOKASSA_SECRET_KEY")
    )


def telegram_ready(config):
    return bool(
        config.get("TELEGRAM_NOTIFICATIONS_ENABLED")
        and config.get("TELEGRAM_BOT_TOKEN")
        and config.get("TELEGRAM_CHAT_ID")
    )
