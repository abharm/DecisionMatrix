"""SQLite data access; no validation policy or score calculations live here."""
import sqlite3
from pathlib import Path

from app.domain.models import Category, CategoryDataType, Direction, Matrix, Option
from app.persistence.database import connect


class MatrixRepository:
    def __init__(self, database_path: str | Path) -> None:
        self.connection = connect(database_path)

    def close(self) -> None:
        self.connection.close()

    def create_matrix(self, name: str, source_csv_path: str | None = None) -> Matrix:
        cursor = self.connection.execute("INSERT INTO matrices(name,source_csv_path) VALUES(?,?)", (name, source_csv_path))
        self.connection.commit()
        return Matrix(cursor.lastrowid, name, source_csv_path=source_csv_path)

    def rename_matrix(self, matrix_id: int, name: str) -> None:
        self.connection.execute("UPDATE matrices SET name=? WHERE id=?", (name, matrix_id))
        self.connection.commit()

    def delete_matrix(self, matrix_id: int) -> None:
        self.connection.execute("DELETE FROM matrices WHERE id=?", (matrix_id,))
        self.connection.commit()

    def list_matrices(self) -> list[Matrix]:
        return [Matrix(row["id"], row["name"], source_csv_path=row["source_csv_path"]) for row in self.connection.execute("SELECT * FROM matrices ORDER BY name")]

    def get_matrix(self, matrix_id: int) -> Matrix:
        row = self.connection.execute("SELECT * FROM matrices WHERE id=?", (matrix_id,)).fetchone()
        if row is None:
            raise KeyError(f"Matrix {matrix_id} was not found")
        categories = [Category(r["id"], r["matrix_id"], r["name"], r["weight"], CategoryDataType(r["data_type"]), Direction(r["direction"])) for r in self.connection.execute("SELECT * FROM categories WHERE matrix_id=? ORDER BY id", (matrix_id,))]
        options: list[Option] = []
        for school in self.connection.execute("SELECT * FROM schools WHERE matrix_id=? ORDER BY name", (matrix_id,)):
            values = {v["category_id"]: v["raw_value"] for v in self.connection.execute("SELECT category_id, raw_value FROM school_values WHERE school_id=?", (school["id"],))}
            options.append(Option(school["id"], matrix_id, school["name"], values))
        return Matrix(row["id"], row["name"], categories, options, row["source_csv_path"])

    def set_source_csv_path(self, matrix_id: int, path: str | None) -> None:
        self.connection.execute("UPDATE matrices SET source_csv_path=? WHERE id=?", (path, matrix_id))
        self.connection.commit()

    def get_app_setting(self, key: str) -> str | None:
        row = self.connection.execute("SELECT value FROM application_state WHERE key=?", (key,)).fetchone()
        return row["value"] if row else None

    def set_app_setting(self, key: str, value: str) -> None:
        self.connection.execute("INSERT INTO application_state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
        self.connection.commit()

    def category_matrix_id(self, category_id: int) -> int:
        row = self.connection.execute("SELECT matrix_id FROM categories WHERE id=?", (category_id,)).fetchone()
        if row is None: raise KeyError(f"Category {category_id} was not found")
        return row["matrix_id"]

    def option_matrix_id(self, option_id: int) -> int:
        row = self.connection.execute("SELECT matrix_id FROM schools WHERE id=?", (option_id,)).fetchone()
        if row is None: raise KeyError(f"Option {option_id} was not found")
        return row["matrix_id"]

    def add_category(self, category: Category) -> Category:
        cursor = self.connection.execute("INSERT INTO categories(matrix_id,name,weight,data_type,direction) VALUES(?,?,?,?,?)", (category.matrix_id, category.name, category.weight, category.data_type.value, category.direction.value))
        self.connection.commit()
        return Category(cursor.lastrowid, category.matrix_id, category.name, category.weight, category.data_type, category.direction)

    def update_category(self, category: Category) -> None:
        self.connection.execute("UPDATE categories SET name=?,weight=?,data_type=?,direction=? WHERE id=?", (category.name, category.weight, category.data_type.value, category.direction.value, category.id))
        self.connection.commit()

    def delete_category(self, category_id: int) -> None:
        self.connection.execute("DELETE FROM categories WHERE id=?", (category_id,))
        self.connection.commit()

    def add_option(self, option: Option) -> Option:
        cursor = self.connection.execute("INSERT INTO schools(matrix_id,name) VALUES(?,?)", (option.matrix_id, option.name))
        self.connection.commit()
        return Option(cursor.lastrowid, option.matrix_id, option.name)

    def update_option(self, option: Option) -> None:
        self.connection.execute("UPDATE schools SET name=? WHERE id=?", (option.name, option.id))
        self.connection.commit()

    def delete_option(self, option_id: int) -> None:
        self.connection.execute("DELETE FROM schools WHERE id=?", (option_id,))
        self.connection.commit()

    def set_value(self, option_id: int, category_id: int, value: float | None) -> None:
        if value is None:
            self.connection.execute("DELETE FROM school_values WHERE school_id=? AND category_id=?", (option_id, category_id))
        else:
            self.connection.execute("INSERT INTO school_values(school_id,category_id,raw_value) VALUES(?,?,?) ON CONFLICT(school_id,category_id) DO UPDATE SET raw_value=excluded.raw_value", (option_id, category_id, value))
        self.connection.commit()
