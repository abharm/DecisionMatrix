from app.calculations.normalization import normalize_numeric
from app.domain.models import Direction


def test_higher_is_better_normalization():
    assert normalize_numeric({1: 10, 2: 20}, Direction.HIGHER_IS_BETTER) == {1: 0.0, 2: 100.0}


def test_lower_is_better_normalization():
    assert normalize_numeric({1: 10, 2: 20}, Direction.LOWER_IS_BETTER) == {1: 100.0, 2: 0.0}


def test_equal_values_are_neutral():
    assert normalize_numeric({1: 10, 2: 10}, Direction.HIGHER_IS_BETTER) == {1: 100.0, 2: 100.0}
