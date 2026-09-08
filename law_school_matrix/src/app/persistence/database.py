"""SQLite setup, isolated from domain operations."""
import sqlite3
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS matrices (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, source_csv_path TEXT);
CREATE TABLE IF NOT EXISTS categories (
 id INTEGER PRIMARY KEY, matrix_id INTEGER NOT NULL REFERENCES matrices(id) ON DELETE CASCADE,
 name TEXT NOT NULL, weight REAL NOT NULL, data_type TEXT NOT NULL, direction TEXT NOT NULL,
 UNIQUE(matrix_id, name)
);
CREATE TABLE IF NOT EXISTS schools (
 id INTEGER PRIMARY KEY, matrix_id INTEGER NOT NULL REFERENCES matrices(id) ON DELETE CASCADE,
 name TEXT NOT NULL, UNIQUE(matrix_id, name)
);
CREATE TABLE IF NOT EXISTS school_values (
 school_id INTEGER NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
 category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
 raw_value REAL NOT NULL, PRIMARY KEY(school_id, category_id)
);
CREATE TABLE IF NOT EXISTS application_state (
 key TEXT PRIMARY KEY,
 value TEXT NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    """Open a SQLite database and ensure its current schema exists."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(matrices)")}
    if "source_csv_path" not in columns:
        connection.execute("ALTER TABLE matrices ADD COLUMN source_csv_path TEXT")
        connection.commit()
    return connection
