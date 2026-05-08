import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app


os.environ.setdefault("APP_MODE", "dev_flow")
os.environ.setdefault("DATABASE", "dev_store.db")
os.environ.setdefault("PAYMENT_PROVIDER", "fake_yookassa")
os.environ.setdefault("YOOKASSA_ENABLED", "false")

app = create_app()


if __name__ == "__main__":
    print("Baikal Stone Market dev flow running at http://127.0.0.1:5000")
    print("Fake payments enabled; Telegram dev notifications use real Telegram when configured.")
    app.run(host="127.0.0.1", port=5000, debug=True)
