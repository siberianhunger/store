from tests.conftest import add_to_cart


def test_add_update_remove_cart(client):
    assert add_to_cart(client, 1).status_code == 302
    response = client.get("/cart")
    assert "Береговая галька Байкала" in response.get_data(as_text=True)
    assert client.post("/cart/update/1", data={"quantity": "2"}).status_code == 302
    response = client.get("/cart")
    assert "36.00" in response.get_data(as_text=True)
    assert client.post("/cart/remove/1").status_code == 302
    response = client.get("/cart")
    assert "Корзина пуста" in response.get_data(as_text=True)


def test_quantity_cannot_exceed_stock(client):
    add_to_cart(client, 1)
    response = client.post(
        "/cart/update/1",
        data={"quantity": "999"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 400
    body = response.get_data(as_text=True)
    assert "Запрошенное количество сейчас недоступно" in body
    assert "999" not in body
    assert "В наличии только" not in body


def test_missing_product_and_negative_quantity_errors(client):
    response = client.post("/cart/add/999", headers={"HX-Request": "true"})
    assert response.status_code == 400
    assert "Товар не найден" in response.get_data(as_text=True)
    response = client.post(
        "/cart/update/1",
        data={"quantity": "-1"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 400
    assert "Количество не может быть отрицательным" in response.get_data(as_text=True)


def test_cart_clamps_when_stock_drops(app, client):
    add_to_cart(client, 1)
    client.post("/cart/update/1", data={"quantity": "2"})
    with app.app_context():
        from app import db

        db.get_db().execute("UPDATE products SET stock = 1 WHERE id = 1")
        db.get_db().commit()
    response = client.get("/cart")
    body = response.get_data(as_text=True)
    assert "18.00" in body
    assert "36.00" not in body


def test_cart_quantity_input_does_not_expose_exact_stock(client):
    add_to_cart(client, 1)
    body = client.get("/cart").get_data(as_text=True)
    assert 'max="' not in body


def test_zero_update_removes_item(client):
    add_to_cart(client, 1)
    client.post("/cart/update/1", data={"quantity": "0"})
    assert "Корзина пуста" in client.get("/cart").get_data(as_text=True)
