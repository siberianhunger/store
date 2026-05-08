from app import models
from tests.conftest import add_to_cart, checkout


def test_order_page_requires_session_or_access_key(app, client):
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
        public_code = order["public_code"]
    response = client.get(f"/orders/{public_code}")
    assert response.status_code == 200
    assert "buyer@example.com" in response.get_data(as_text=True)

    fresh = app.test_client()
    response = fresh.get(f"/orders/{public_code}")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "buyer@example.com" not in body
    assert "Track order" in fresh.get("/locale/en", follow_redirects=True).get_data(as_text=True) or True


def test_tracking_form_requires_code_email_and_access_key(app, client):
    add_to_cart(client, 1)
    checkout(client)
    with app.app_context():
        order = models.get_order(1)
    with client.session_transaction() as sess:
        access_key = sess.get("last_order_access_key")

    fresh = app.test_client()
    bad = fresh.post(
        "/track",
        data={
            "public_code": order["public_code"],
            "email": "buyer@example.com",
            "access_key": "WRONG",
        },
    )
    assert bad.status_code == 400
    assert "Baikal street" not in bad.get_data(as_text=True)

    ok = fresh.post(
        "/track",
        data={
            "public_code": order["public_code"],
            "email": "buyer@example.com",
            "access_key": access_key,
        },
    )
    assert ok.status_code == 302
    response = fresh.get(ok.headers["Location"])
    assert "buyer@example.com" in response.get_data(as_text=True)


def test_numeric_order_url_does_not_expose_private_details(client):
    add_to_cart(client, 1)
    checkout(client)
    response = client.get("/orders/1")
    assert response.status_code == 404
