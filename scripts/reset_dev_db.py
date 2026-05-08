import os
import sys
from pathlib import Path


DEV_DB = Path(os.environ.get("DATABASE", "dev_store.db")).resolve()
ROOT = Path.cwd().resolve()


def is_safe_dev_db(path):
    try:
        path.relative_to(ROOT)
    except ValueError:
        return False
    return path.name.startswith("dev_") and path.suffix in {".db", ".sqlite", ".sqlite3"}


if __name__ == "__main__":
    if not is_safe_dev_db(DEV_DB):
        raise SystemExit(f"Refusing to delete non-dev database path: {DEV_DB}")
    if DEV_DB.exists():
        DEV_DB.unlink()
    os.environ.setdefault("APP_MODE", "dev_flow")
    os.environ["DATABASE"] = str(DEV_DB)
    os.environ.setdefault("PAYMENT_PROVIDER", "fake_yookassa")
    os.environ.setdefault("YOOKASSA_ENABLED", "false")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from app import create_app

    create_app()
    print(f"Reset dev database: {DEV_DB}")
