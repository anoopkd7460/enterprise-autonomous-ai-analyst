
"""Tests for deterministic Phase 11 evidence synthesis."""

from app.workflows.evidence_synthesis import (
    synthesize_advanced_answer,
)


def test_sql_evidence_is_preserved():
    state = {
        "completed_steps": ["sql"],
        "failed_steps": [],
        "sql_result": {
            "sql_query": "SELECT SUM(revenue) FROM sales",
            "rows": [{"total_revenue": 5000}],
            "row_count": 1,
            "explanation": "Total revenue is 5000.",
        },
    }

    answer = synthesize_advanced_answer(state)

    assert "5000" in answer
    assert "SELECT SUM(revenue)" in answer
    assert "Database results" in answer


def test_document_evidence_is_preserved():
    state = {
        "completed_steps": ["document"],
        "failed_steps": [],
        "doc_result": {
            "answer": "The report discusses supply delays.",
            "retrieved_chunks": [
                "Supply delays affected Q4 deliveries."
            ],
        },
    }

    answer = synthesize_advanced_answer(state)

    assert "Supply delays affected" in answer
    assert "document interpretation" in answer


def test_partial_failure_is_disclosed():
    state = {
        "completed_steps": ["sql"],
        "failed_steps": ["document"],
        "sql_result": {
            "sql_query": "SELECT COUNT(*) FROM sales",
            "rows": [{"total": 20}],
            "row_count": 1,
            "explanation": "20 records found.",
        },
    }

    answer = synthesize_advanced_answer(state)

    assert "20 records found" in answer
    assert "Incomplete Analysis" in answer
    assert "document" in answer


def test_no_new_causal_claim_is_added():
    state = {
        "completed_steps": ["sql", "document"],
        "failed_steps": [],
        "sql_result": {
            "sql_query": "SELECT SUM(revenue) FROM sales",
            "rows": [{"revenue": 5000}],
            "row_count": 1,
            "explanation": "Revenue was 5000.",
        },
        "doc_result": {
            "answer": "The report mentions supply delays.",
            "retrieved_chunks": [
                "Supply delays were observed."
            ],
        },
    }

    answer = synthesize_advanced_answer(state)

    assert "Revenue was 5000" in answer
    assert "supply delays" in answer.lower()

    # The presenter must not invent an explanation
    # that neither source provided.
    assert "logging error" not in answer.lower()
    assert "caused the revenue decline" not in answer.lower()
