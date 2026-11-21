
"""
Phase 11: Evidence-aware adapters for existing V1 agents.

Purpose:
- Reuse existing SQL, RAG, and Analytics Agents.
- Validate agent outputs before recording success.
- Prevent empty SQL results or missing RAG evidence
  from being treated as successful analysis.
"""
import json
import re
from typing import Any

import pandas as pd

from app.agents.sql_agent import answer_question as sql_answer
from app.agents.document_agent import answer_question as doc_answer

from app.workflows.graph import call_data_analyst

from app.workflows.advanced_state import AdvancedPlannerState


def validate_sql_evidence(sql_query: str) -> None:
    """
    Reject hardcoded text presented as report,
    reason, cause, or explanation evidence.

    This is a narrow Phase 11 safeguard, not
    a complete SQL syntax/security validator.
    """

    if not isinstance(sql_query, str) or not sql_query.strip():
        raise ValueError("SQL query is missing")

    misleading_literal_pattern = (
        r"""(?:'(?:''|[^'])*'|"(?:\"\"|[^"])*")"""
        r"\s+(?:AS\s+)?"
        r"(?:report|reason|cause|explanation)\b"
    )

    if re.search(
        misleading_literal_pattern,
        sql_query,
        flags=re.IGNORECASE,
    ):
        raise ValueError(
            "SQL contains hardcoded text presented "
            "as business evidence"
        )

def sql_agent_adapter(
    state: AdvancedPlannerState,
) -> dict[str, Any]:
    """
    Execute the existing SQL Agent and validate evidence.
    """

    result = sql_answer(state["question"])


    # Reject fabricated textual evidence before
    # accepting the SQL Agent's result.
    validate_sql_evidence(result.sql_query)


    data = result.data

    if not isinstance(data, pd.DataFrame):
        raise ValueError("SQL Agent returned invalid data")

    # No rows were returned.
    if data.empty:
        raise ValueError(
            "SQL query returned no matching records"
        )

    # Handles aggregate queries such as SUM(revenue)
    # returning one row whose value is NULL.
    if data.isna().all().all():
        raise ValueError(
            "SQL query returned only NULL values"
        )

    if not isinstance(result.explanation, str):
        raise ValueError("Invalid SQL explanation")

    if not result.explanation.strip():
        raise ValueError("SQL explanation was empty")

    return {
        "explanation": result.explanation,
        "sql_query": result.sql_query,

        # Preserve actual database evidence.
        # JSON conversion normalizes pandas values.
        "rows": json.loads(
            data.head(20).to_json(
                orient="records",
                date_format="iso",
            )
        ),
        "row_count": len(data),
    }


def document_agent_adapter(
    state: AdvancedPlannerState,
) -> dict[str, Any]:
    """
    Execute RAG and check whether documents were retrieved.
    """

    result = doc_answer(state["question"])

    # An answer without retrieved documents is not
    # sufficient evidence for a document-based claim.
    if not result.retrieved_chunks:
        raise ValueError(
            "No relevant document chunks were retrieved"
        )

    if not isinstance(result.answer, str):
        raise ValueError("Invalid document answer")

    if not result.answer.strip():
        raise ValueError("Document answer was empty")

    return {
        "answer": result.answer,

        # Preserve retrieved context for traceability
        "retrieved_chunks": result.retrieved_chunks[:3],
    }


def analytics_agent_adapter(
    state: AdvancedPlannerState,
) -> dict[str, Any]:
    """
    Execute the existing CSV/Excel Analytics Agent.
    """

    agent_state = dict(state)

    if agent_state.get("dataframe") is None:
        raise ValueError("No dataset was provided")

    result_state = call_data_analyst(agent_state)

    result = result_state.get("analytics_result")

    if not isinstance(result, dict):
        raise ValueError(
            "Analytics Agent returned an invalid result"
        )

    if result.get("error"):
        raise ValueError(
            "Analytics Agent reported an execution error"
        )

    if not result.get("answer"):
        raise ValueError(
            "Analytics Agent returned no answer"
        )

    return result


def get_agent_adapters() -> dict:
    """Register all available Phase 11 agents."""

    return {
        "sql": sql_agent_adapter,
        "document": document_agent_adapter,
        "analytics": analytics_agent_adapter,
    }
