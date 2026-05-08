import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]


def resolve_database_path():
    load_dotenv(ROOT / ".env")
    configured = os.environ.get("DATABASE")
    if configured:
        return Path(configured).expanduser().resolve()
    return ROOT / "store.db"


def main():
    sqlite3_bin = shutil.which("sqlite3")
    if sqlite3_bin is None:
        print(
            "sqlite3 is not installed. Install it with: sudo apt update && sudo apt install sqlite3",
            file=sys.stderr,
        )
        return 1

    database = resolve_database_path()
    database.parent.mkdir(parents=True, exist_ok=True)
    print(f"Opening SQLite database: {database}", file=sys.stderr)
    return subprocess.call([sqlite3_bin, str(database), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
