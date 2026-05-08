import sqlite3
from contextlib import contextmanager
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    name_ru TEXT,
    name_en TEXT,
    description_ru TEXT,
    description_en TEXT,
    price_cents INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    stock INTEGER NOT NULL,
    weight_grams INTEGER NOT NULL,
    origin TEXT NOT NULL,
    finish TEXT NOT NULL,
    color_family TEXT NOT NULL,
    is_featured INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    shipping_address TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    payment_status TEXT NOT NULL DEFAULT 'pending_manual',
    payment_reference TEXT,
    payment_provider TEXT,
    payment_redirect_url TEXT,
    payment_error TEXT,
    payment_payload_json TEXT,
    paid_at TEXT,
    stock_decremented_at TEXT,
    telegram_paid_notified_at TEXT,
    telegram_manual_notified_at TEXT,
    public_code TEXT UNIQUE,
    access_token_hash TEXT,
    access_token_created_at TEXT,
    customer_email_normalized TEXT,
    reserved_at TEXT,
    reservation_expires_at TEXT,
    reservation_released_at TEXT,
    canceled_at TEXT,
    refunded_at TEXT,
    refund_reference TEXT,
    refund_status TEXT,
    refund_error TEXT,
    receipt_required INTEGER NOT NULL DEFAULT 0,
    receipt_status TEXT,
    receipt_error TEXT,
    shipping_carrier TEXT,
    shipping_tracking_number TEXT,
    shipping_tracking_url TEXT,
    shipping_public_note TEXT,
    shipped_at TEXT,
    shipping_updated_at TEXT,
    shipping_updated_by_chat_id TEXT,
    shipping_updated_by_user_id TEXT,
    total_cents INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
"""


MIGRATIONS = {
    "products": {
        "name_ru": "TEXT",
        "name_en": "TEXT",
        "description_ru": "TEXT",
        "description_en": "TEXT",
    },
    "orders": {
        "payment_provider": "TEXT",
        "payment_redirect_url": "TEXT",
        "payment_error": "TEXT",
        "payment_payload_json": "TEXT",
        "paid_at": "TEXT",
        "stock_decremented_at": "TEXT",
        "telegram_paid_notified_at": "TEXT",
        "telegram_manual_notified_at": "TEXT",
        "public_code": "TEXT",
        "access_token_hash": "TEXT",
        "access_token_created_at": "TEXT",
        "customer_email_normalized": "TEXT",
        "reserved_at": "TEXT",
        "reservation_expires_at": "TEXT",
        "reservation_released_at": "TEXT",
        "canceled_at": "TEXT",
        "refunded_at": "TEXT",
        "refund_reference": "TEXT",
        "refund_status": "TEXT",
        "refund_error": "TEXT",
        "receipt_required": "INTEGER NOT NULL DEFAULT 0",
        "receipt_status": "TEXT",
        "receipt_error": "TEXT",
        "shipping_carrier": "TEXT",
        "shipping_tracking_number": "TEXT",
        "shipping_tracking_url": "TEXT",
        "shipping_public_note": "TEXT",
        "shipped_at": "TEXT",
        "shipping_updated_at": "TEXT",
        "shipping_updated_by_chat_id": "TEXT",
        "shipping_updated_by_user_id": "TEXT",
    },
}


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


@contextmanager
def transaction():
    db = get_db()
    if db.in_transaction:
        raise RuntimeError("Nested transactions are not supported.")
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
    except Exception:
        db.rollback()
        raise
    else:
        db.commit()


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    Path(current_app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    get_db().executescript(SCHEMA)
    migrate_db()
    get_db().commit()


def migrate_db():
    db = get_db()
    for table_name, columns in MIGRATIONS.items():
        existing = {
            row["name"] for row in db.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        for column_name, column_type in columns.items():
            if column_name not in existing:
                db.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
    db.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_public_code ON orders(public_code)"
    )


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
