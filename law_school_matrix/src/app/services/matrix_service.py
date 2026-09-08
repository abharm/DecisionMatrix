"""Application use cases and input validation."""
import sqlite3
from pathlib import Path

from app.calculations.scoring import calculate_matrix
from app.domain.models import Category, CategoryDataType, Direction, Matrix, Option
from app.persistence.repositories import MatrixRepository
from app.services.csv_import import CsvImportError, parse_matrix_csv
from app.services.csv_export import write_matrix_csv


class ValidationError(ValueError):
    pass


class MatrixService:
    def __init__(self, repository: MatrixRepository) -> None:
        self.repository = repository

    def create_matrix(self, name: str) -> Matrix:
        return self._write(lambda: self.repository.create_matrix(self._required_name(name, "Matrix")))

    def load(self, matrix_id: int) -> Matrix:
        return self.repository.get_matrix(matrix_id)

    def rename_matrix(self, matrix_id: int, name: str) -> None:
        self._write(lambda: self.repository.rename_matrix(matrix_id, self._required_name(name, "Project")))

    def delete_matrix(self, matrix_id: int) -> None:
        self._write(lambda: self.repository.delete_matrix(matrix_id))

    def add_category(self, matrix_id: int, name: str, weight: float, data_type: CategoryDataType, direction: Direction) -> Category:
        self._validate_weight(weight)
        category = self._write(lambda: self.repository.add_category(Category(None, matrix_id, self._required_name(name, "Category"), weight, data_type, direction)))
        self._sync_csv(matrix_id)
        return category

    def update_category(self, category: Category) -> None:
        self._validate_weight(category.weight)
        self._write(lambda: self.repository.update_category(Category(category.id, category.matrix_id, self._required_name(category.name, "Category"), category.weight, category.data_type, category.direction)))
        self._sync_csv(category.matrix_id or 0)

    def delete_category(self, category_id: int) -> None:
        matrix_id = self.repository.category_matrix_id(category_id)
        self.repository.delete_category(category_id)
        self._sync_csv(matrix_id)

    def add_option(self, matrix_id: int, name: str) -> Option:
        option = self._write(lambda: self.repository.add_option(Option(None, matrix_id, self._required_name(name, "School/option"))))
        self._sync_csv(matrix_id)
        return option

    def update_option(self, option: Option) -> None:
        self._write(lambda: self.repository.update_option(Option(option.id, option.matrix_id, self._required_name(option.name, "School/option"), option.values)))
        self._sync_csv(option.matrix_id or 0)

    def delete_option(self, option_id: int) -> None:
        matrix_id = self.repository.option_matrix_id(option_id)
        self.repository.delete_option(option_id)
        self._sync_csv(matrix_id)

    def set_value(self, option_id: int, category: Category, raw: str) -> None:
        if not raw.strip():
            self.repository.set_value(option_id, category.id or 0, None)
            self._sync_csv(category.matrix_id or 0)
            return
        try:
            value = float(raw)
        except ValueError as error:
            raise ValidationError("Values must be valid numbers.") from error
        if category.data_type == CategoryDataType.RATING and not 0 <= value <= 100:
            raise ValidationError("Ratings must be between 0 and 100.")
        self.repository.set_value(option_id, category.id or 0, value)
        self._sync_csv(category.matrix_id or 0)

    def calculate(self, matrix: Matrix):
        return calculate_matrix(matrix)

    def import_csv(self, path: str | Path, matrix_name: str | None = None) -> Matrix:
        """Create a new matrix from a validated CSV file, preserving raw values."""
        try:
            parsed = parse_matrix_csv(path)
        except CsvImportError as error:
            raise ValidationError(str(error)) from error
        default_name = Path(path).stem.replace("_", " ")
        name = matrix_name or self._next_import_name(default_name)
        matrix = self.create_matrix(name)
        try:
            categories = [self.add_category(matrix.id or 0, item.name, item.weight, item.data_type, item.direction) for item in parsed.categories]
            for imported_option in parsed.options:
                option = self.add_option(matrix.id or 0, imported_option.name)
                for category, raw in zip(categories, imported_option.values):
                    self.set_value(option.id or 0, category, raw)
        except Exception:
            # The matrix is new and isolated, so cleanup avoids a partial import.
            self.repository.connection.execute("DELETE FROM matrices WHERE id=?", (matrix.id,))
            self.repository.connection.commit()
            raise
        self.repository.set_source_csv_path(matrix.id or 0, str(Path(path).resolve()))
        imported = self.load(matrix.id or 0)
        self._sync_csv(imported.id or 0)
        return imported

    def export_and_link_csv(self, matrix_id: int, path: str | Path) -> None:
        """Write a matrix to CSV and enable automatic updates to that file."""
        destination = str(Path(path).resolve())
        self.repository.set_source_csv_path(matrix_id, destination)
        self._sync_csv(matrix_id)

    def _sync_csv(self, matrix_id: int) -> None:
        if matrix_id <= 0:
            return
        matrix = self.load(matrix_id)
        if not matrix.source_csv_path:
            return
        try:
            write_matrix_csv(matrix, matrix.source_csv_path)
        except OSError as error:
            raise ValidationError(f"Changes were saved in the app, but the linked CSV could not be updated: {error}") from error

    @staticmethod
    def _required_name(name: str, label: str) -> str:
        if not name.strip():
            raise ValidationError(f"{label} name cannot be empty.")
        return name.strip()

    def _next_import_name(self, base_name: str) -> str:
        """Keep repeated imports non-destructive by choosing a fresh matrix name."""
        existing = {matrix.name.casefold() for matrix in self.repository.list_matrices()}
        if base_name.casefold() not in existing:
            return base_name
        number = 2
        while f"{base_name} ({number})".casefold() in existing:
            number += 1
        return f"{base_name} ({number})"

    @staticmethod
    def _validate_weight(weight: float) -> None:
        if not 1 <= weight <= 10:
            raise ValidationError("Category importance must be a whole-number scale from 1 to 10.")

    @staticmethod
    def _write(operation):
        try:
            return operation()
        except sqlite3.IntegrityError as error:
            raise ValidationError("Names must be unique within a matrix.") from error
