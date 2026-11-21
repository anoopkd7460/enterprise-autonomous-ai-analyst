
"""Phase 11: Tests for reporting-period clarification."""

from unittest.mock import patch

import pytest

from app.workflows.graph import run_advanced_workflow


@pytest.mark.parametrize(
    "question",
    [
        "What was revenue in Q4?",
        "Why did North India sales decline in Q3?",
        "Compare revenue in the first quarter",
        "Analyze sales in the fourth quarter",
    ],
)
def test_missing_year_requests_clarification(question):
    """Quarter questions without a year must not execute agents."""

    with patch(
        "app.workflows.graph.route_question"
    ) as mock_router, patch(
        "app.workflows.graph.get_advanced_graph"
    ) as mock_graph:

        result = run_advanced_workflow(question)

    assert result["workflow_status"] == "needs_clarification"
    assert result["execution_count"] == 0
    assert "year" in result["final_answer"].lower()

    mock_router.assert_not_called()
    mock_graph.assert_not_called()


def test_explicit_year_allows_workflow():
    """A specified year should allow normal routing."""

    question = "What was North India revenue in Q4 2024?"

    with patch(
        "app.workflows.graph.route_question"
    ) as mock_router, patch(
        "app.workflows.graph.get_advanced_graph"
    ) as mock_graph:

        mock_router.side_effect = lambda state: {
            **state,
            "route": "sql",
        }

        mock_graph.return_value.invoke.return_value = {
            "workflow_status": "success",
            "final_answer": "Revenue analysis completed.",
        }

        result = run_advanced_workflow(question)

    assert result["workflow_status"] == "success"
    mock_router.assert_called_once()
    mock_graph.return_value.invoke.assert_called_once()


def test_question_without_quarter():
    """Ordinary business questions should remain unaffected."""

    question = "What is total revenue?"

    with patch(
        "app.workflows.graph.route_question"
    ) as mock_router, patch(
        "app.workflows.graph.get_advanced_graph"
    ) as mock_graph:

        mock_router.side_effect = lambda state: {
            **state,
            "route": "sql",
        }

        mock_graph.return_value.invoke.return_value = {
            "workflow_status": "success",
            "final_answer": "Total revenue calculated.",
        }

        result = run_advanced_workflow(question)

    assert result["workflow_status"] == "success"
    mock_router.assert_called_once()
    mock_graph.return_value.invoke.assert_called_once()
