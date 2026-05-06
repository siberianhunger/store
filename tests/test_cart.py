from tests.conftest import add_to_cart


def test_add_update_remove_cart(client):
    assert add_to_cart(client, 1).status_code == 302
    response = client.get("/cart")
    assert "Байкальская береговая галька" in response.get_data(as_text=True)
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
    assert "В наличии только" in response.get_data(as_text=True)
