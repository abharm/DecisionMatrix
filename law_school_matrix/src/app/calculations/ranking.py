"""Ranking helpers."""


def rank_scores(scores: dict[int, float]) -> dict[int, int]:
    """Return competition ranks: 90, 90, 80 becomes 1, 1, 3."""
    ranks: dict[int, int] = {}
    previous: float | None = None
    rank = 0
    for position, (option_id, score) in enumerate(sorted(scores.items(), key=lambda item: (-item[1], item[0])), 1):
        if previous is None or score != previous:
            rank = position
            previous = score
        ranks[option_id] = rank
    return ranks
