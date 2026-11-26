
"""Phase 12: Tests for cross-encoder reranking."""

import pytest

from app.rag.bm25_retriever import RetrievedChunk
from app.rag.reranker import CrossEncoderReranker


class FakeCrossEncoder:
    def predict(self, pairs):
        scores = []

        for question, passage in pairs:
            if "supply shortage" in passage.lower():
                scores.append(0.95)
            elif "revenue" in passage.lower():
                scores.append(0.70)
            else:
                scores.append(0.10)

        return scores


@pytest.fixture
def sample_chunks():
    return [
        RetrievedChunk(
            "doc-1",
            "Employee holiday policy",
            "policy.pdf",
        ),
        RetrievedChunk(
            "doc-2",
            "North India supply shortage caused delays",
            "regional_report.pdf",
        ),
        RetrievedChunk(
            "doc-3",
            "Regional revenue increased",
            "regional_report.pdf",
        ),
    ]


def test_reranking_changes_order(sample_chunks):
    reranker = CrossEncoderReranker(FakeCrossEncoder())

    results = reranker.rerank(
        "Why did North India sales decline?",
        sample_chunks,
    )

    assert results[0].chunk_id == "doc-2"
    assert results[1].chunk_id == "doc-3"


def test_metadata_preserved(sample_chunks):
    reranker = CrossEncoderReranker(FakeCrossEncoder())

    results = reranker.rerank(
        "Why did sales decline?",
        sample_chunks,
    )

    assert results[0].source == "regional_report.pdf"


def test_top_k(sample_chunks):
    reranker = CrossEncoderReranker(FakeCrossEncoder())

    results = reranker.rerank(
        "Explain revenue",
        sample_chunks,
        top_k=2,
    )

    assert len(results) == 2


def test_empty_chunks():
    reranker = CrossEncoderReranker(FakeCrossEncoder())

    assert reranker.rerank("Question", []) == []


def test_invalid_top_k(sample_chunks):
    reranker = CrossEncoderReranker(FakeCrossEncoder())

    with pytest.raises(ValueError):
        reranker.rerank(
            "Question",
            sample_chunks,
            top_k=0,
        )


def test_tie_preserves_original_order(sample_chunks):
    class EqualScoreModel:
        def predict(self, pairs):
            return [0.5] * len(pairs)

    reranker = CrossEncoderReranker(EqualScoreModel())

    results = reranker.rerank(
        "Question",
        sample_chunks,
    )

    assert [
        chunk.chunk_id for chunk in results
    ] == ["doc-1", "doc-2", "doc-3"]


def test_invalid_score_count(sample_chunks):
    class InvalidModel:
        def predict(self, pairs):
            return [0.5]

    reranker = CrossEncoderReranker(InvalidModel())

    with pytest.raises(ValueError):
        reranker.rerank("Question", sample_chunks)
