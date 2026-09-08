"""Weighted multi-criteria scoring; deliberately independent of any GUI."""
from app.calculations.normalization import normalize_category
from app.calculations.ranking import rank_scores
from app.domain.models import Matrix, MatrixResult, OptionResult


def calculate_matrix(matrix: Matrix) -> MatrixResult:
    """Calculate scores for complete options, returning N/A results for incomplete ones."""
    if not matrix.categories:
        return MatrixResult({}, "Add at least one category before calculating.")
    total_weight = sum(category.weight for category in matrix.categories)
    if total_weight <= 0:
        return MatrixResult({}, "Total category weight must be greater than zero.")
    normalized: dict[int, dict[int, float]] = {option.id: {} for option in matrix.options if option.id is not None}
    for category in matrix.categories:
        assert category.id is not None
        # Normalize against every entered value in the current matrix. An option
        # with another missing value remains ineligible for an overall score.
        raw = {option.id: option.values[category.id] for option in matrix.options if option.id is not None and option.values.get(category.id) is not None}
        if not raw:
            continue
        normalized_category = normalize_category(category, raw)  # type: ignore[arg-type]
        for option_id, score in normalized_category.items():
            normalized[option_id][category.id] = score
    scores = {option_id: sum(normalized[option_id][category.id] * category.weight / total_weight for category in matrix.categories if category.id is not None) for option_id in normalized if all(option_id in normalized and category.id in normalized[option_id] for category in matrix.categories if category.id is not None)}
    ranks = rank_scores(scores)
    results: dict[int, OptionResult] = {}
    for option in matrix.options:
        assert option.id is not None
        missing = tuple(category.id for category in matrix.categories if category.id is not None and option.values.get(category.id) is None)
        results[option.id] = OptionResult(option.id, normalized.get(option.id, {}), scores.get(option.id), ranks.get(option.id), missing)
    return MatrixResult(results)
