"""CSV serialization for linked decision matrices."""
import csv
from pathlib import Path

from app.domain.models import Matrix


def write_matrix_csv(matrix: Matrix, path: str | Path) -> None:
    """Write the complete, portable import format for a matrix."""
    destination = Path(path)
    with destination.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["School / Option", *[category.name for category in matrix.categories]])
        writer.writerow(["#weight", *[f"{category.weight:g}" for category in matrix.categories]])
        writer.writerow(["#type", *[category.data_type.value for category in matrix.categories]])
        writer.writerow(["#direction", *[category.direction.value for category in matrix.categories]])
        for option in matrix.options:
            writer.writerow([option.name, *["" if option.values.get(category.id) is None else f"{option.values[category.id]:g}" for category in matrix.categories]])
