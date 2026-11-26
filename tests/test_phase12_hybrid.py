
"""Tests for Phase 12 hybrid retrieval."""

import pytest

from app.rag.hybrid_retriever import HybridRetriever


class FakeCollection:
    """Minimal test replacement for ChromaDB."""

    def __init__(self):
        self.ids = ["report-0", "report-1", "policy-0"]

        self.documents = [
            "North India Q4 inventory shortages",
            "South India recorded sales growth",
            "Employee leave and holiday policy",
        ]

        self.metadatas = [
            {"source": "regional.pdf"},
            {"source": "regional.pdf"},
            {"source": "policy.pdf"},
        ]

    def get(self, include, limit, offset):
        return {
            "ids": self.ids[offset:offset + limit],
            "documents": self.documents[
                offset:offset + limit
            ],
            "metadatas": self.metadatas[
                offset:offset + limit
            ],
        }

    def query(self, query_texts, n_results, include):
        # Simulated semantic ranking.
        return {
            "ids": [
                ["report-1", "report-0", "policy-0"][
                    :n_results
                ]
            ]
        }


def test_hybrid_retrieval_returns_chunks():
    retriever = HybridRetriever(FakeCollection())

    results = retriever.retrieve(
        "North India Q4 shortages",
        top_k=2,
    )

    assert len(results) == 2
    assert all(result.chunk_id for result in results)


def test_hybrid_preserves_metadata():
    retriever = HybridRetriever(FakeCollection())

    results = retriever.retrieve(
        "North India inventory",
        top_k=3,
    )

    assert any(
        chunk.source == "regional.pdf"
        for chunk in results
    )


def test_hybrid_results_are_unique():
    retriever = HybridRetriever(FakeCollection())

    results = retriever.retrieve(
        "India sales",
        top_k=3,
    )

    ids = [chunk.chunk_id for chunk in results]

    assert len(ids) == len(set(ids))


def test_hybrid_handles_empty_index():
    collection = FakeCollection()
    collection.ids = []
    collection.documents = []
    collection.metadatas = []

    retriever = HybridRetriever(collection)

    assert retriever.retrieve("revenue") == []


def test_hybrid_rejects_invalid_top_k():
    retriever = HybridRetriever(FakeCollection())

    with pytest.raises(ValueError):
        retriever.retrieve(
            "revenue",
            top_k=0,
        )


def test_hybrid_rejects_invalid_candidate_k():
    retriever = HybridRetriever(FakeCollection())

    with pytest.raises(ValueError):
        retriever.retrieve(
            "revenue",
            candidate_k=0,
        )
