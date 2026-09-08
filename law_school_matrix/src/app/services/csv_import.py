"""CSV parsing for portable, human-editable matrix imports."""
import csv
from dataclasses import dataclass
from pathlib import Path

from app.domain.models import CategoryDataType, Direction


class CsvImportError(ValueError):
    """A user-correctable issue in a matrix CSV file."""


@dataclass(frozen=True)
class ImportedCategory:
    name: str
    weight: float
    data_type: CategoryDataType
    direction: Direction


@dataclass(frozen=True)
class ImportedOption:
    name: str
    values: list[str]


@dataclass(frozen=True)
class CsvMatrixData:
    categories: list[ImportedCategory]
    options: list[ImportedOption]


def parse_matrix_csv(path: str | Path) -> CsvMatrixData:
    """Read a wide CSV with optional #weight, #type, and #direction rows.

    The first column is the option name. Without metadata, all criteria use
    equal weights, numeric data, and higher-is-better direction.
    """
    try:
        with Path(path).open("r", encoding="utf-8-sig", newline="") as source:
            rows = [[cell.strip() for cell in row] for row in csv.reader(source) if any(cell.strip() for cell in row)]
    except OSError as error:
        raise CsvImportError(f"Could not read CSV: {error}") from error
    if not rows or len(rows[0]) < 2:
        raise CsvImportError("CSV needs a header with an option column and at least one category.")
    headers = rows[0][1:]
    if any(not name for name in headers) or len(set(name.casefold() for name in headers)) != len(headers):
        raise CsvImportError("Category names in the header must be non-empty and unique.")
    metadata: dict[str, list[str]] = {}
    data_rows: list[list[str]] = []
    for line_number, row in enumerate(rows[1:], 2):
        row = row + [""] * (len(rows[0]) - len(row))
        if len(row) > len(rows[0]):
            raise CsvImportError(f"Row {line_number} has more columns than the header.")
        key = row[0].casefold()
        if key.startswith("#"):
            if key not in {"#weight", "#type", "#direction"}:
                raise CsvImportError(f"Unknown metadata row '{row[0]}' on row {line_number}.")
            if key in metadata:
                raise CsvImportError(f"Metadata row '{row[0]}' is duplicated.")
            metadata[key] = row[1:]
        elif row[0]:
            data_rows.append(row)
        else:
            raise CsvImportError(f"Row {line_number} is missing an option name.")
    if not data_rows:
        raise CsvImportError("CSV must contain at least one option row.")
    if len({row[0].casefold() for row in data_rows}) != len(data_rows):
        raise CsvImportError("Option names in the CSV must be unique.")
    count = len(headers)
    weights = _weights(metadata.get("#weight", [""] * count), count)
    data_types = _enums(metadata.get("#type", [""] * count), count, CategoryDataType, CategoryDataType.NUMERIC, "type")
    directions = _enums(metadata.get("#direction", [""] * count), count, Direction, Direction.HIGHER_IS_BETTER, "direction")
    return CsvMatrixData([ImportedCategory(name, weights[index], data_types[index], directions[index]) for index, name in enumerate(headers)], [ImportedOption(row[0], row[1:]) for row in data_rows])


def _weights(cells: list[str], count: int) -> list[float]:
    if len(cells) != count:
        raise CsvImportError("#weight must contain one value for every category.")
    if not any(cells):
        return [5.0] * count
    try:
        values = [float(cell) for cell in cells]
    except ValueError as error:
        raise CsvImportError("#weight values must be numbers.") from error
    if any(value < 1 or value > 10 or value != int(value) for value in values):
        raise CsvImportError("#weight importance values must be whole numbers from 1 to 10.")
    return values


def _enums(cells: list[str], count: int, enum_type, default, label: str):
    if len(cells) != count:
        raise CsvImportError(f"#{label} must contain one value for every category.")
    result = []
    for cell in cells:
        if not cell:
            result.append(default)
            continue
        try:
            result.append(enum_type(cell.casefold().replace(" ", "_")))
        except ValueError as error:
            choices = ", ".join(item.value for item in enum_type)
            raise CsvImportError(f"Invalid {label} '{cell}'. Use: {choices}.") from error
    return result
