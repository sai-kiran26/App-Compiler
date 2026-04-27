from __future__ import annotations

import sqlite3
from pathlib import Path

from models import ExecutionReport, SchemaBundle

SQL_TYPE_MAP = {
    "uuid": "TEXT",
    "string": "TEXT",
    "number": "REAL",
    "timestamp": "TEXT",
}


def _column_sql(field) -> str:
    sql_type = SQL_TYPE_MAP.get(field.type, "TEXT")
    parts = [field.name, sql_type]
    if field.required:
        parts.append("NOT NULL")
    if field.unique:
        parts.append("UNIQUE")
    return " ".join(parts)


def execute_schema(bundle: SchemaBundle, db_path: Path) -> ExecutionReport:
    tables_created = []
    errors = []

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        for table in bundle.db.tables:
            columns = ", ".join(_column_sql(col) for col in table.columns)
            sql = f"CREATE TABLE IF NOT EXISTS {table.name} ({columns});"
            cursor.execute(sql)
            tables_created.append(table.name)
        conn.commit()
    except sqlite3.Error as exc:
        errors.append(str(exc))
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return ExecutionReport(
        executed=len(errors) == 0,
        tables_created=tables_created,
        errors=errors,
    )
