
"""Phase 11: Supervisor and failure recovery tests."""

from unittest.mock import patch

from app.workflows.advanced_graph import build_advanced_graph


def sql_agent(state):
    return {
        "explanation": "Revenue declined by 8%.",
        "sql_query": "SELECT 1",
    }


def document_agent(state):
    return {
        "answer": "The report identified supply shortages.",
    }


def failing_agent(state):
    raise RuntimeError("Simulated agent failure")


def test_multi_agent_execution():
    """SQL and Document Agents should both execute."""

    agents = {
        "sql": sql_agent,
        "document": document_agent,
    }

    with patch(
        "app.workflows.graph.chat",
        return_value=(
            "Revenue declined by 8%. "
            "The report identified supply shortages."
        ),
    ):
        graph = build_advanced_graph(agents)

        result = graph.invoke({
            "question": "Why did revenue decline?",
            "route": "both",
        })

    assert result["workflow_status"] == "success"
    assert result["completed_steps"] == [
        "sql", "document"
    ]
    assert result["execution_count"] == 2
    assert result["failed_steps"] == []

    assert "8%" in result["final_answer"]
    assert "supply shortages" in result["final_answer"]


def test_partial_failure_recovery():
    """Preserve SQL evidence after Document Agent failure."""

    graph = build_advanced_graph({
        "sql": sql_agent,
        "document": failing_agent,
    })

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


def test_all_agents_failure():
    """Do not generate findings when all agents fail."""

    graph = build_advanced_graph({
        "sql": failing_agent,
        "document": failing_agent,
    })

    result = graph.invoke({
        "question": "Analyze revenue and reports",
        "route": "both",
    })

    assert result["workflow_status"] == "failed"
    assert result["completed_steps"] == []
    assert result["execution_count"] == 2
    assert "8%" not in result["final_answer"]


def test_missing_agent():
    """Supervisor must handle an unavailable planned agent."""

    graph = build_advanced_graph({
        "sql": sql_agent,
    })

    result = graph.invoke({
        "question": "Analyze SQL and document data",
        "route": "both",
    })

    assert result["workflow_status"] == "partial_success"
    assert result["completed_steps"] == ["sql"]
    assert result["failed_steps"] == ["document"]
    assert result["execution_count"] == 1


def test_missing_dataset():
    """Analytics must not run without an uploaded dataset."""

    graph = build_advanced_graph({
        "analytics": lambda state: {
            "answer": "Dataset analyzed"
        },
    })

    result = graph.invoke({
        "question": "Analyze uploaded dataset",
        "route": "analytics",
        "dataframe": None,
    })

    assert result["workflow_status"] == "invalid_plan"
    assert result["execution_count"] == 0


def test_execution_budget():
    """Supervisor should not exceed its execution limit."""

    graph = build_advanced_graph({
        "sql": sql_agent,
        "document": document_agent,
    })

    with patch(
        "app.workflows.graph.chat",
        return_value="Combined answer",
    ):
        result = graph.invoke({
            "question": "Analyze SQL and documents",
            "route": "both",
        })

    assert result["execution_count"] <= 3
