import pytest

from evaluate import first_hit_rank, summarise


def test_first_hit_rank_counts_from_one():
    results = [("a.pdf", 1), ("b.pdf", 2), ("c.pdf", 3)]

    assert first_hit_rank(results, {("b.pdf", 2), ("c.pdf", 3)}) == 2


def test_first_hit_rank_without_a_hit_is_none():
    assert first_hit_rank([("a.pdf", 1)], {("b.pdf", 2)}) is None


def test_summarise_matches_the_worked_example():
    scores = summarise([1, 3, None])

    assert scores["hit@1"] == pytest.approx(1 / 3)
    assert scores["hit@5"] == pytest.approx(2 / 3)
    assert scores["hit@10"] == pytest.approx(2 / 3)
    assert scores["MRR"] == pytest.approx((1 + 1 / 3 + 0) / 3)
