from app.calculations.ranking import rank_scores


def test_ranking_descending():
    assert rank_scores({1: 50, 2: 100, 3: 75}) == {2: 1, 3: 2, 1: 3}


def test_ties_use_same_rank():
    assert rank_scores({1: 90, 2: 90, 3: 80}) == {1: 1, 2: 1, 3: 3}
