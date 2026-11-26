
"""Phase 12: Document Agent integration tests."""

from unittest.mock import patch

from app.agents.document_agent import (
    is_advanced_rag_enabled,
    retrieve_document_context,
)

from app.rag.bm25_retriever import RetrievedChunk


def test_advanced_rag_disabled_by_default(monkeypatch):
    """Advanced RAG must be disabled by default."""

    monkeypatch.delenv(
        "ADVANCED_RAG_ENABLED",
        raising=False,
    )

    assert is_advanced_rag_enabled() is False


def test_original_retrieval_when_disabled(monkeypatch):
    """V1 dense retrieval must remain unchanged."""

    monkeypatch.setenv(
        "ADVANCED_RAG_ENABLED",
        "false",
    )

    with patch(
        "app.agents.document_agent.retrieve_relevant_chunks",
        return_value=["Original document evidence"],
    ) as dense_mock:

        chunks = retrieve_document_context(
            "What caused the decline?"
        )

    assert chunks == ["Original document evidence"]
    dense_mock.assert_called_once()


def test_advanced_retrieval_when_enabled(monkeypatch):
    """Advanced RAG must use hybrid retrieval and reranking."""

    monkeypatch.setenv(
        "ADVANCED_RAG_ENABLED",
        "true",
    )

    candidates = [
        RetrievedChunk(
            "doc-0",
            "North India experienced supply delays.",
            "regional_report.pdf",
        ),
        RetrievedChunk(
            "doc-1",
            "Q4 marketing spend declined.",
            "regional_report.pdf",
        ),
    ]

    with patch(
        "app.rag.hybrid_retriever.retrieve_hybrid_chunks",
        return_value=candidates,
    ) as hybrid_mock, patch(
        "app.rag.reranker.rerank_chunks",
        return_value=[
            candidates[1],
            candidates[0],
        ],
    ) as rerank_mock:

        chunks = retrieve_document_context(
            "Why did North India sales decline?",
            top_k=2,
        )

    assert chunks == [
        "Q4 marketing spend declined.",
        "North India experienced supply delays.",
    ]

    hybrid_mock.assert_called_once()
    rerank_mock.assert_called_once()


def test_fallback_when_reranker_fails(monkeypatch):
    """Dense retrieval must work if reranking fails."""

    monkeypatch.setenv(
        "ADVANCED_RAG_ENABLED",
        "true",
    )

    candidates = [
        RetrievedChunk(
            "doc-0",
            "Supply shortages affected sales.",
            "regional_report.pdf",
        ),
    ]

    with patch(
        "app.rag.hybrid_retriever.retrieve_hybrid_chunks",
        return_value=candidates,
    ), patch(
        "app.rag.reranker.rerank_chunks",
        side_effect=RuntimeError("Simulated failure"),
    ), patch(
        "app.agents.document_agent.retrieve_relevant_chunks",
        return_value=["Dense fallback evidence"],
    ) as dense_mock:

        chunks = retrieve_document_context(
            "Why did sales decline?"
        )

    assert chunks == ["Dense fallback evidence"]
    dense_mock.assert_called_once()
