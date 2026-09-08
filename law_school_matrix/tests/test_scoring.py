from app.calculations.scoring import calculate_matrix
from app.domain.models import Category, CategoryDataType, Direction, Matrix, Option


def matrix_with(values_a, values_b, weights=(20, 80)):
    categories = [Category(1, 1, "A", weights[0], CategoryDataType.RATING, Direction.HIGHER_IS_BETTER), Category(2, 1, "B", weights[1], CategoryDataType.RATING, Direction.HIGHER_IS_BETTER)]
    return Matrix(1, "test", categories, [Option(1, 1, "one", values_a), Option(2, 1, "two", values_b)])


def test_weighted_score_and_weight_normalization():
    result = calculate_matrix(matrix_with({1: 100, 2: 50}, {1: 0, 2: 50}, weights=(2, 8)))
    assert result.option_results[1].overall_score == 60
    assert result.option_results[2].overall_score == 40


def test_missing_value_is_na():
    result = calculate_matrix(matrix_with({1: 100, 2: None}, {1: 0, 2: 50}))
    assert result.option_results[1].overall_score is None
    assert result.option_results[1].missing_category_ids == (2,)


def test_invalid_total_weight_returns_error():
    result = calculate_matrix(matrix_with({1: 100, 2: 50}, {1: 0, 2: 50}, weights=(0, 0)))
    assert "greater than zero" in (result.error or "")
