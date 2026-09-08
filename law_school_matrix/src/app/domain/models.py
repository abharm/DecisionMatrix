"""Typed, GUI-independent domain entities."""
from dataclasses import dataclass, field
from enum import StrEnum


class CategoryDataType(StrEnum):
    NUMERIC = "numeric"
    RATING = "rating"


class Direction(StrEnum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


@dataclass(frozen=True)
class Category:
    id: int | None
    matrix_id: int | None
    name: str
    weight: float
    data_type: CategoryDataType
    direction: Direction


@dataclass(frozen=True)
class Option:
    id: int | None
    matrix_id: int | None
    name: str
    values: dict[int, float | None] = field(default_factory=dict)


@dataclass(frozen=True)
class Matrix:
    id: int | None
    name: str
    categories: list[Category] = field(default_factory=list)
    options: list[Option] = field(default_factory=list)
    source_csv_path: str | None = None


@dataclass(frozen=True)
class OptionResult:
    option_id: int
    normalized_scores: dict[int, float]
    overall_score: float | None
    rank: int | None
    missing_category_ids: tuple[int, ...] = ()


@dataclass(frozen=True)
class MatrixResult:
    option_results: dict[int, OptionResult]
    error: str | None = None
