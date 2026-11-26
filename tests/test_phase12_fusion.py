
"""Tests for Phase 12 Reciprocal Rank Fusion."""

import pytest

from app.rag.fusion import reciprocal_rank_fusion


def test_fusion_prioritizes_shared_results():
    dense = [
        "North India sales",
        "Supply chain delays",
        "Q4 market performance",
    ]

    sparse = [
        "Supply chain delays",
        "North India sales",
        "Inventory shortages",
    ]

    result = reciprocal_rank_fusion(
        [dense, sparse],
        top_k=3,
    )

    assert result[0] == "North India sales"
    assert result[1] == "Supply chain delays"
    assert len(result) == 3


def test_fusion_removes_duplicate_chunks():
    result = reciprocal_rank_fusion([
        ["Revenue decline", "Revenue decline"],
        ["Revenue decline", "Inventory shortage"],
    ])

    assert result.count("Revenue decline") == 1


def test_fusion_respects_top_k():
    result = reciprocal_rank_fusion(
        [["A", "B", "C", "D"]],
        top_k=2,
    )

    assert len(result) == 2


def test_fusion_handles_empty_results():
    result = reciprocal_rank_fusion(
        [[], []],
        top_k=5,
    )

    assert result == []


def test_fusion_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion(
            [["A"]],
            top_k=0,
        )


def test_fusion_rejects_invalid_rrf_k():
    with pytest.raises(ValueError):
        reciprocal_rank_fusion(
            [["A"]],
            rrf_k=0,
        )
