
"""Phase 12 Task 6: Source-aware evidence tests."""

from unittest.mock import patch

from app.agents.document_agent import (
    DocumentAgentResult,
    answer_question,
)
from app.rag.bm25_retriever import RetrievedChunk


def test_existing_result_constructor_compatible():
    result = DocumentAgentResult(
        "Question",
        ["Evidence"],
        "Answer",
    )

    assert result.retrieved_chunks == ["Evidence"]
    assert result.source_chunks == []


def test_advanced_answer_preserves_sources(monkeypatch):
    monkeypatch.setenv("ADVANCED_RAG_ENABLED", "true")

    evidence = RetrievedChunk(
        "report-0",
        "North India faced inventory shortages.",
        "regional.pdf",
    )

    with patch(
        "app.rag.hybrid_retriever.retrieve_hybrid_chunks",
        return_value=[evidence],
    ), patch(
        "app.rag.reranker.rerank_chunks",
        return_value=[evidence],
    ), patch(
        "app.agents.document_agent.chat",
        return_value="Inventory shortages [report-0].",
    ) as chat_mock:

        result = answer_question(
            "Why did North India sales decline?"
        )

    assert result.source_chunks == [evidence]
    assert result.retrieved_chunks == [evidence.text]
    assert "Inventory shortages" in result.answer

    # The LLM receives the actual source metadata.
    llm_prompt = chat_mock.call_args.args[1]

    assert "Source ID: report-0" in llm_prompt
    assert "Source Document: regional.pdf" in llm_prompt


def test_default_mode_does_not_invent_sources(monkeypatch):
    monkeypatch.setenv("ADVANCED_RAG_ENABLED", "false")

    with patch(
        "app.agents.document_agent.retrieve_relevant_chunks",
        return_value=["Existing evidence"],
    ), patch(
        "app.agents.document_agent.chat",
        return_value="Existing answer",
    ):
        result = answer_question("Explain the report")

    assert result.retrieved_chunks == ["Existing evidence"]
    assert result.source_chunks == []


def test_fallback_does_not_invent_sources(monkeypatch):
    monkeypatch.setenv("ADVANCED_RAG_ENABLED", "true")

    with patch(
        "app.rag.hybrid_retriever.retrieve_hybrid_chunks",
        side_effect=RuntimeError("Test retrieval failure"),
    ), patch(
        "app.agents.document_agent.retrieve_relevant_chunks",
        return_value=["Fallback evidence"],
    ), patch(
        "app.agents.document_agent.chat",
        return_value="Fallback answer",
    ):
        result = answer_question("Explain the report")

    assert result.retrieved_chunks == ["Fallback evidence"]
    assert result.source_chunks == []
