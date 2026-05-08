from pathlib import Path

from app import db


def test_schema_and_migrations_are_idempotent(app):
    with app.app_context():
        db.init_db()
        db.init_db()
        conn = db.get_db()
        tables = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        assert {"products", "orders", "order_items"}.issubset(tables)
        order_columns = {
            row["name"] for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        }
        assert "public_code" in order_columns
        assert "access_token_hash" in order_columns
        assert "reservation_expires_at" in order_columns
        assert "refund_status" in order_columns
        assert "receipt_status" in order_columns
        assert "shipping_tracking_number" in order_columns
        assert "shipping_updated_by_chat_id" in order_columns
        index_names = {
            row["name"]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'index'"
            ).fetchall()
        }
        assert "idx_orders_public_code" in index_names


def test_database_parent_directory_is_created(tmp_path, monkeypatch):
    nested_db = tmp_path / "nested" / "store.sqlite"
    app = __import__("app").create_app(
        {"TESTING": True, "DATABASE": str(nested_db)}
    )
    with app.app_context():
        assert Path(app.config["DATABASE"]).exists()
        assert nested_db.parent.exists()


def test_foreign_keys_enabled(app):
    with app.app_context():
        assert db.get_db().execute("PRAGMA foreign_keys").fetchone()[0] == 1
