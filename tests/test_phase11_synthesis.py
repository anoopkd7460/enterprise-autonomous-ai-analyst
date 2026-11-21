
"""Tests for Phase 11 evidence-aware synthesis."""

from unittest.mock import patch

from app.workflows.advanced_graph import build_advanced_graph


def test_sql_only_answer():
    """Successful SQL evidence should become the final answer."""

    agents = {
        "sql": lambda state: {
            "explanation": "Revenue increased by 12%.",
            "sql_query": "SELECT 1",
        }
    }

    graph = build_advanced_graph(agents)

    result = graph.invoke({
        "question": "What happened to revenue?",
        "route": "sql",
    })

    assert result["workflow_status"] == "success"
    assert result["execution_count"] == 1
    assert result["completed_steps"] == ["sql"]
    assert "12%" in result["final_answer"]


def test_partial_success():
    """Successful SQL evidence survives document failure."""

    def failing_document_agent(state):
        raise RuntimeError("Simulated document failure")

    agents = {
        "sql": lambda state: {
            "explanation": "Revenue declined by 8%.",
            "sql_query": "SELECT 1",
        },
        "document": failing_document_agent,
    }

    graph = build_advanced_graph(agents)

    result = graph.invoke({
        "question": "Why did revenue decline?",
        "route": "both",
    })

    assert result["workflow_status"] == "partial_success"
    assert result["completed_steps"] == ["sql"]
    assert result["failed_steps"] == ["document"]
    assert result["execution_count"] == 2
    assert "8%" in result["final_answer"]
    assert "could not be completed" in result["final_answer"]


def test_both_agents_success():
    """Combined evidence should be synthesized successfully."""

    agents = {
        "sql": lambda state: {
            "explanation": "Revenue declined by 8%.",
            "sql_query": "SELECT 1",
        },
        "document": lambda state: {
            "answer": "The report cited supply shortages.",
        },
    }

    with patch(
        "app.workflows.graph.chat",
        return_value=(
            "Revenue declined by 8%, and the report "
            "cited supply shortages."
        ),
    ):
        graph = build_advanced_graph(agents)

        result = graph.invoke({
            "question": "Why did revenue decline?",
            "route": "both",
        })

    assert result["workflow_status"] == "success"
    assert result["execution_count"] == 2
    assert result["failed_steps"] == []
    assert "8%" in result["final_answer"]
    assert "supply shortages" in result["final_answer"]


def test_all_agents_fail():
    """No successful evidence means no generated business answer."""

    def failing_agent(state):
        raise RuntimeError("Simulated failure")

    agents = {
        "sql": failing_agent,
        "document": failing_agent,
    }

    graph = build_advanced_graph(agents)

    result = graph.invoke({
        "question": "Analyze revenue and documents.",
        "route": "both",
    })

    assert result["workflow_status"] == "failed"
    assert result["completed_steps"] == []
    assert result["execution_count"] == 2
    assert "could not be completed" in result["final_answer"]
