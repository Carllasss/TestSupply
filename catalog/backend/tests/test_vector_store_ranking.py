from app.services.vector_store import rank_hits_by_supplier


def test_keeps_only_hits_within_margin_of_top_score():
    hits = [(1, 0.90), (2, 0.85), (3, 0.60), (4, 0.50)]
    # top=0.90, margin=0.15 -> cutoff 0.75
    assert rank_hits_by_supplier(hits, relative_margin=0.15) == [1, 2]


def test_dedupes_multiple_chunk_hits_per_supplier_keeping_best_score():
    # Supplier 1 has three chunk hits; only the best should decide its rank.
    hits = [(1, 0.40), (1, 0.95), (1, 0.70), (2, 0.90)]
    assert rank_hits_by_supplier(hits, relative_margin=0.1) == [1, 2]


def test_empty_hits_returns_empty_list():
    assert rank_hits_by_supplier([]) == []


def test_respects_limit_after_ranking():
    hits = [(i, 1.0 - i * 0.01) for i in range(10)]
    result = rank_hits_by_supplier(hits, limit=3, relative_margin=1.0)
    assert result == [0, 1, 2]


def test_results_are_sorted_best_first():
    hits = [(1, 0.7), (2, 0.9), (3, 0.8)]
    assert rank_hits_by_supplier(hits, relative_margin=0.5) == [2, 3, 1]
