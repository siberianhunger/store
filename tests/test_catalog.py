from pathlib import Path


def test_catalog_renders_all_seeded_products(client):
    response = client.get("/", headers={"Accept-Language": "en"})
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Natural stones for quiet interiors" in body
    assert "A small catalog of photographed stones from the Baikal region" in body
    assert "hero-stats" not in body
    assert body.count('class="stone-card"') == 16
    assert "18.00 RUB" in body


def test_catalog_css_keeps_compact_full_width_hero_without_stats():
    styles = Path("static/styles.css").read_text()

    assert ".hero-stats" not in styles
    assert "#f7f1e8" not in styles.lower()
    assert "--color-card: #12384f;" in styles
    assert "background: #082233;" in styles
    assert "background: #12384f;" in styles
    assert ".store-hero h1" in styles
    assert "max-width: none;" in styles
    assert "padding: clamp(34px, 5vw, 62px)" in styles


def test_catalog_renders_russian_product_copy(client):
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert "Береговая галька Байкала" in body


def test_product_detail_does_not_show_stock_count(client):
    response = client.get("/products/baikal-shoreline-pebble")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Наличие" not in body
    assert "Stock" not in body
