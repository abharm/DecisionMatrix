"""Normalization functions for individual categories."""
from app.domain.models import Category, CategoryDataType, Direction


def normalize_numeric(values: dict[int, float], direction: Direction) -> dict[int, float]:
    """Normalize numeric values to 0-100, avoiding division by zero."""
    minimum, maximum = min(values.values()), max(values.values())
    if minimum == maximum:
        return {option_id: 100.0 for option_id in values}
    span = maximum - minimum
    if direction == Direction.HIGHER_IS_BETTER:
        return {option_id: 100 * (value - minimum) / span for option_id, value in values.items()}
    return {option_id: 100 * (maximum - value) / span for option_id, value in values.items()}


def normalize_category(category: Category, values: dict[int, float]) -> dict[int, float]:
    """Apply the appropriate current strategy for a category."""
    if category.data_type == CategoryDataType.RATING:
        return values.copy()
    return normalize_numeric(values, category.direction)
