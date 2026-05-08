from app import models
from app.notifications.telegram import parse_ship_command, send_telegram_message
from tests.conftest import add_to_cart, checkout


def configure_telegram(app):
    app.config.update(
        TELEGRAM_NOTIFICATIONS_ENABLED=True,
        TELEGRAM_BOT_TOKEN="token",
        TELEGRAM_CHAT_ID="100",
        TELEGRAM_WEBHOOK_SECRET="secret",
        TELEGRAM_ALLOWED_USER_IDS="7",
    )


def telegram_update(text, chat_id=100, user_id=7):
    return {
        "message": {
            "text": text,
            "chat": {"id": chat_id},
            "from": {"id": user_id},
        }
    }


def test_parse_ship_command():
    parsed = parse_ship_command('/ship BSM-20260506-ABC123 CDEK 123456 "Передано в доставку"')
    assert parsed == {
        "public_code": "BSM-20260506-ABC123",
        "carrier": "CDEK",
        "tracking_number": "123456",
        "note": "Передано в доставку",
    }
    assert parse_ship_command("/bad BSM CDEK 1") is None
    assert parse_ship_command('/ship "unterminated') is None


def test_shipping_update_requires_paid_order(app, client):
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
        ok, reason, _ = models.update_order_shipping(
            order["public_code"], "CDEK", "123", chat_id=100, user_id=7
        )
        assert not ok
        assert reason == "order is not paid"


def test_shipping_update_rejects_missing_unknown_and_refunded(app, client):
    with app.app_context():
        ok, reason, _ = models.update_order_shipping("NOPE", "CDEK", "123")
        assert not ok
        assert reason == "order not found"
        ok, reason, _ = models.update_order_shipping("NOPE", "", "")
        assert not ok
        assert reason == "tracking number missing"

    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        models.mark_order_paid(1)
        models.refund_order(1, "refund")
        order = models.get_order(1)
        ok, reason, _ = models.update_order_shipping(order["public_code"], "CDEK", "123")
        assert not ok
        assert reason == "order is canceled or refunded"


def test_tracking_url_unknown_and_known_carriers(app):
    with app.app_context():
        assert models.build_tracking_url("Boxberry", "abc").endswith("abc")
        assert models.build_tracking_url("Unknown", "abc") is None


def test_shipping_update_stores_tracking_and_page_privacy(app, client):
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        models.mark_order_paid(1)
        order = models.get_order(1)
        ok, reason, updated = models.update_order_shipping(
            order["public_code"], "CDEK", "123456", "Передано в доставку", chat_id=100, user_id=7
        )
        assert ok, reason
        assert updated["status"] == "shipped"
        assert "cdek.ru" in updated["shipping_tracking_url"]

    fresh = app.test_client()
    hidden = fresh.get(f"/orders/{order['public_code']}").get_data(as_text=True)
    assert "123456" not in hidden

    visible = client.get(f"/orders/{order['public_code']}").get_data(as_text=True)
    assert "123456" in visible
    assert "Передано в доставку" in visible


def test_telegram_webhook_authorization_and_success(app, client, monkeypatch):
    sent = []
    monkeypatch.setattr("app.routes.send_telegram_message", lambda text, chat_id=None: sent.append((text, chat_id)) or True)
    add_to_cart(client, 1)
    checkout(client)
    configure_telegram(app)
    with app.app_context():
        models.mark_order_paid(1)
        public_code = models.get_order(1)["public_code"]

    wrong_secret = client.post("/webhooks/telegram/wrong", json=telegram_update(f"/ship {public_code} CDEK 123"))
    assert wrong_secret.status_code == 403
    unauthorized = client.post("/webhooks/telegram/secret", json=telegram_update(f"/ship {public_code} CDEK 123", user_id=8))
    assert unauthorized.get_json()["status"] == "ignored"

    response = client.post("/webhooks/telegram/secret", json=telegram_update(f"/ship {public_code} CDEK 123"))
    assert response.get_json()["status"] == "ok"
    with app.app_context():
        order = models.get_order(1)
        assert order["shipping_tracking_number"] == "123"
        assert order["shipping_updated_by_chat_id"] == "100"
        assert order["shipping_updated_by_user_id"] == "7"
    assert "Tracking saved." in sent[-1][0]
    assert "access" not in sent[-1][0].lower()


def test_telegram_webhook_invalid_command_replies(app, client, monkeypatch):
    configure_telegram(app)
    sent = []
    monkeypatch.setattr("app.routes.send_telegram_message", lambda text, chat_id=None: sent.append(text) or True)
    response = client.post("/webhooks/telegram/secret", json=telegram_update("/ship"))
    assert response.get_json()["status"] == "invalid"
    assert "Invalid command" in sent[-1]


def test_telegram_webhook_disabled_and_failed_update(app, client, monkeypatch):
    assert client.post("/webhooks/telegram/secret", json=telegram_update("/ship BSM X 1")).status_code == 404
    configure_telegram(app)
    sent = []
    monkeypatch.setattr("app.routes.send_telegram_message", lambda text, chat_id=None: sent.append(text) or True)
    response = client.post("/webhooks/telegram/secret", json=telegram_update("/ship BSM-20000101-NOPE CDEK 123"))
    assert response.get_json()["status"] == "failed"
    assert "order not found" in sent[-1]


def test_send_telegram_message_success_disabled_and_failure(app, monkeypatch):
    with app.app_context():
        assert not send_telegram_message("hello")
        app.config.update(
            TELEGRAM_NOTIFICATIONS_ENABLED=True,
            TELEGRAM_BOT_TOKEN="token",
            TELEGRAM_CHAT_ID="chat",
        )
        sent = {}

        class Response:
            def raise_for_status(self):
                return None

        def fake_post(url, **kwargs):
            sent["url"] = url
            sent["kwargs"] = kwargs
            return Response()

        monkeypatch.setattr("app.notifications.telegram.httpx.post", fake_post)
        assert send_telegram_message("hello", chat_id="other")
        assert sent["kwargs"]["json"]["chat_id"] == "other"

        import httpx

        def fail_post(url, **kwargs):
            raise httpx.ConnectError("down", request=httpx.Request("POST", url))

        monkeypatch.setattr("app.notifications.telegram.httpx.post", fail_post)
        assert not send_telegram_message("hello")
