def test_catalog_renders_all_seeded_products(client):
    response = client.get("/", headers={"Accept-Language": "en"})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert body.count('class="stone-card"') == 16
    assert "18.00 RUB" in body


def test_catalog_renders_russian_product_copy(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "Байкальская береговая галька" in body
