import os
import sqlite3
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
    database = resolve_database_path()
    database.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        print(f"Opened SQLite database: {database}", file=sys.stderr)
        if len(sys.argv) > 1:
            execute_input(conn, " ".join(sys.argv[1:]))
            return 0
        return repl(conn)


def repl(conn):
    print("Enter SQL. Commands: .tables, .schema [table], .quit", file=sys.stderr)
    buffer = []
    while True:
        try:
            prompt = "sql> " if not buffer else "...> "
            line = input(prompt)
        except EOFError:
            print()
            return 0

        stripped = line.strip()
        if not stripped and not buffer:
            continue
        if not buffer and stripped in {".quit", ".exit"}:
            return 0
        if not buffer and stripped == ".tables":
            show_tables(conn)
            continue
        if not buffer and stripped.startswith(".schema"):
            parts = stripped.split(maxsplit=1)
            table = parts[1] if len(parts) == 2 else None
            show_schema(conn, table)
            continue

        buffer.append(line)
        statement = "\n".join(buffer).strip()
        if sqlite3.complete_statement(statement):
            try:
                execute_sql(conn, statement)
            finally:
                buffer.clear()


def show_schema(conn, table=None):
    if table:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master WHERE name = ? AND sql IS NOT NULL ORDER BY type, name",
            (table,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
            "ORDER BY type, name"
        ).fetchall()
    for row in rows:
        print(f"{row['sql']};")


def execute_input(conn, text):
    stripped = text.strip()
    if stripped == ".tables":
        show_tables(conn)
        return
    if stripped.startswith(".schema"):
        parts = stripped.split(maxsplit=1)
        show_schema(conn, parts[1] if len(parts) == 2 else None)
        return
    execute_sql(conn, text)


def show_tables(conn):
    execute_sql(
        conn,
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name",
    )


def execute_sql(conn, sql):
    cursor = conn.execute(sql)
    if cursor.description:
        rows = cursor.fetchall()
        print_rows(rows, [column[0] for column in cursor.description])
    else:
        conn.commit()
        print(f"{cursor.rowcount} row(s) affected")


def print_rows(rows, columns):
    if not rows:
        print("(no rows)")
        return

    values = [[format_value(row[column]) for column in columns] for row in rows]
    widths = [
        max(len(column), *(len(row[index]) for row in values))
        for index, column in enumerate(columns)
    ]
    print(" | ".join(column.ljust(widths[index]) for index, column in enumerate(columns)))
    print("-+-".join("-" * width for width in widths))
    for row in values:
        print(" | ".join(value.ljust(widths[index]) for index, value in enumerate(row)))


def format_value(value):
    if value is None:
        return "NULL"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
