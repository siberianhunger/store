def test_default_locale_is_russian(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Байкальские камни" in body
    assert "Корзина" in body


def test_accept_language_english_selects_english(client):
    response = client.get("/", headers={"Accept-Language": "en"})
    body = response.get_data(as_text=True)
    assert "Natural stones" in body
    assert "Cart" in body


def test_manual_locale_switch_persists_choice(client):
    client.get("/locale/en", headers={"Referer": "http://localhost/"})
    response = client.get("/", headers={"Accept-Language": "ru"})
    assert "Natural stones" in response.get_data(as_text=True)


def test_unsupported_locale_does_not_override(client):
    client.get("/locale/nope", headers={"Referer": "http://localhost/"})
    response = client.get("/", headers={"Accept-Language": "en"})
    assert "Natural stones" in response.get_data(as_text=True)
