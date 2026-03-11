from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
import re

# sample comman line:
# python scripts/init_db.py --db my_database.db --sql schema.sql

def _prompt_non_empty(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Value cannot be empty. Please try again.", file=sys.stderr)


def _prompt_yes_no(prompt: str, *, default: bool | None = None) -> bool:
    if default is True:
        suffix = " [Y/n] "
    elif default is False:
        suffix = " [y/N] "
    else:
        suffix = " [y/n] "

    while True:
        raw = input(f"{prompt}{suffix}").strip().lower()
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        if raw == "" and default is not None:
            return default
        print("Please answer y or n.", file=sys.stderr)


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path):
        pass


def apply_schema(db_path: Path, sql_path: Path) -> None:
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")
    sql_text = sql_path.read_text(encoding="utf-8").strip()
    if not sql_text:
        raise ValueError(f"SQL file is empty: {sql_path}")

    with sqlite3.connect(db_path) as conn:
        buffer = ""
        for line in sql_text.splitlines(keepends=True):
            buffer += line
            if not sqlite3.complete_statement(buffer):
                continue

            statement = buffer.strip()
            buffer = ""
            if not statement:
                continue

            try:
                conn.execute(statement)
            except sqlite3.OperationalError as exc:
                message = str(exc)
                if "already exists" in message.lower() and statement.lstrip().upper().startswith("CREATE "):
                    object_info = _describe_create_statement(statement)
                    if object_info is None:
                        print(f"Already exists, skipping: {message}", file=sys.stderr)
                    else:
                        object_type, object_name = object_info
                        print(f"Already exists, skipping: {object_type} {object_name}", file=sys.stderr)
                    continue
                raise

        if buffer.strip():
            raise sqlite3.OperationalError("Incomplete SQL statement at end of file.")


def print_schema(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE sql IS NOT NULL
              AND type IN ('table', 'view', 'index', 'trigger')
            ORDER BY
              CASE type
                WHEN 'table' THEN 1
                WHEN 'view' THEN 2
                WHEN 'index' THEN 3
                WHEN 'trigger' THEN 4
                ELSE 5
              END,
              name;
            """.strip()
        ).fetchall()

    print("Current schema:")
    if not rows:
        print("(no objects found)")
        return

    for obj_type, obj_name, sql in rows:
        print(f"-- {obj_type} {obj_name}")
        print(sql.rstrip(";") + ";")
        print()


_CREATE_RE = re.compile(
    r"""
    ^\s*CREATE\s+
    (?P<type>TABLE|INDEX|UNIQUE\s+INDEX|VIEW|TRIGGER)\s+
    (?:IF\s+NOT\s+EXISTS\s+)?  # optional
    (?P<name>
        "(?:[^"]|""" + r'""' + r""")*"  # quoted identifier (SQLite-style)
        |
        [A-Za-z_][A-Za-z0-9_]*           # bare identifier
        (?:\.[A-Za-z_][A-Za-z0-9_]*)*    # optional schema qualifiers
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _describe_create_statement(statement: str) -> tuple[str, str] | None:
    match = _CREATE_RE.match(statement)
    if not match:
        return None
    object_type = " ".join(match.group("type").upper().split())
    object_name = match.group("name")
    return object_type, object_name


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]

    parser = argparse.ArgumentParser(description="Create/open a SQLite DB and optionally apply schema SQL.")
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="DB path (absolute or relative). If a bare name is given, it is created under ./data/.",
    )
    parser.add_argument(
        "--sql",
        type=Path,
        default=None,
        help="Path to a .sql file to apply (CREATE TABLE, indexes, etc).",
    )
    parser.add_argument(
        "--create-table",
        action="store_true",
        help="Apply schema from --sql (or prompt for a .sql file).",
    )
    args = parser.parse_args()

    if args.db is None:
        if not sys.stdin.isatty():
            print("Error: --db is required when running non-interactively.", file=sys.stderr)
            return 2
        raw_db = _prompt_non_empty("Enter SQLite DB path or name: ")
        db_path = Path(raw_db)
    else:
        db_path = args.db

    if not db_path.is_absolute() and db_path.parent == Path("."):
        db_path = repo_root / "data" / db_path

    init_db(db_path)
    print(f"Using DB: {db_path}")

    wants_schema = args.create_table or args.sql is not None
    if not wants_schema and sys.stdin.isatty():
        wants_schema = _prompt_yes_no("Do you want to create/apply tables from a .sql file?", default=False)

    if wants_schema:
        try:
            if args.sql is None:
                if not sys.stdin.isatty():
                    print(
                        "Error: --sql is required when running non-interactively with --create-table.",
                        file=sys.stderr,
                    )
                    return 2
                raw_sql = _prompt_non_empty("Enter path to schema .sql file: ")
                sql_path = Path(raw_sql)
            else:
                sql_path = args.sql

            if not sql_path.is_absolute():
                sql_path = (repo_root / sql_path).resolve()

            apply_schema(db_path, sql_path)
            print(f"Applied schema: {sql_path}")
        except (FileNotFoundError, ValueError, sqlite3.Error) as exc:
            print(f"Error applying schema: {exc}", file=sys.stderr)
            return 1

    print_schema(db_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
