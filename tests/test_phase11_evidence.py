
"""Phase 11: Evidence validation tests."""

from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest

from app.workflows.agent_adapters import (
    sql_agent_adapter,
    document_agent_adapter,
)


def test_sql_valid_result():
    """Accept SQL output with actual numerical evidence."""

    mock_result = SimpleNamespace(
        data=pd.DataFrame({"revenue": [5000]}),
        sql_query="SELECT SUM(revenue) FROM sales",
        explanation="Total revenue is 5000.",
    )

    with patch(
        "app.workflows.agent_adapters.sql_answer",
        return_value=mock_result,
    ):
        result = sql_agent_adapter({
            "question": "What is total revenue?"
        })

    assert "5000" in result["explanation"]


def test_sql_empty_result():
    """Reject a query returning no records."""

    mock_result = SimpleNamespace(
        data=pd.DataFrame(columns=["revenue"]),
        sql_query="SELECT revenue FROM sales",
        explanation="No revenue found.",
    )

    with patch(
        "app.workflows.agent_adapters.sql_answer",
        return_value=mock_result,
    ):
        with pytest.raises(ValueError):
            sql_agent_adapter({
                "question": "Show revenue"
            })


def test_sql_null_result():
    """Reject SQL aggregate output containing only NULL."""

    mock_result = SimpleNamespace(
        data=pd.DataFrame({"total_revenue": [None]}),
        sql_query="SELECT SUM(revenue) FROM sales",
        explanation="Revenue was zero.",
    )

    with patch(
        "app.workflows.agent_adapters.sql_answer",
        return_value=mock_result,
    ):
        with pytest.raises(ValueError):
            sql_agent_adapter({
                "question": "What was Q4 revenue?"
            })


def test_document_missing_evidence():
    """Reject RAG answers when no chunks were retrieved."""

    mock_result = SimpleNamespace(
        retrieved_chunks=[],
        answer="No indexed documents found.",
    )

    with patch(
        "app.workflows.agent_adapters.doc_answer",
        return_value=mock_result,
    ):
        with pytest.raises(ValueError):
            document_agent_adapter({
                "question": "What does the report say?"
            })


def test_document_valid_evidence():
    """Accept a nonempty answer with retrieved chunks."""

    mock_result = SimpleNamespace(
        retrieved_chunks=[
            "North India sales declined due to supply delays."
        ],
        answer="The report identifies supply delays.",
    )

    with patch(
        "app.workflows.agent_adapters.doc_answer",
        return_value=mock_result,
    ):
        result = document_agent_adapter({
            "question": "Why did sales decline?"
        })

    assert "supply delays" in result["answer"]
