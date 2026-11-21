
"""
Phase 11: Deterministic evidence presentation.

This module avoids an extra LLM synthesis call.

It preserves the distinction between:
1. Actual SQL query results
2. Retrieved document excerpts
3. AI-generated interpretations
4. Dataset analytics output
"""

import json
from typing import Any

from app.workflows.advanced_state import AdvancedPlannerState


def synthesize_advanced_answer(
    state: AdvancedPlannerState,
) -> str:
    """
    Present successful agent results without introducing
    new LLM-generated claims.
    """

    sections: list[str] = []
    completed = state.get("completed_steps", [])

    if "sql" in completed:
        sql_result = state.get("sql_result") or {}

        sql_lines = ["### SQL Analysis"]

        # Present the executed query for traceability.
        query = sql_result.get("sql_query")

        if query:
            sql_lines.append(
                f"Executed SQL:\n```sql\n{query}\n```"
            )

        # Actual query results take precedence over
        # the LLM's textual interpretation.
        rows = sql_result.get("rows")

        if rows is not None:
            sql_lines.append(
                "Database results (up to 20 rows):\n"
                + json.dumps(
                    rows,
                    indent=2,
                    default=str,
                )
            )

            total_rows = sql_result.get("row_count")

            if total_rows is not None:
                sql_lines.append(
                    f"Total result rows: {total_rows}"
                )

        explanation = sql_result.get("explanation")

        if explanation:
            sql_lines.append(
                "AI-generated interpretation "
                "(verify against the query results):\n"
                + str(explanation)
            )

        sections.append("\n\n".join(sql_lines))

    if "document" in completed:
        doc_result = state.get("doc_result") or {}

        doc_lines = ["### Document Analysis"]

        chunks = doc_result.get("retrieved_chunks", [])

        if chunks:
            doc_lines.append(
                "Retrieved document excerpts:"
            )

            for index, chunk in enumerate(
                chunks[:3],
                start=1,
            ):
                doc_lines.append(
                    f"Excerpt {index}:\n"
                    + str(chunk)[:600]
                )

        answer = doc_result.get("answer")

        if answer:
            doc_lines.append(
                "AI-generated document interpretation "
                "(verify against the excerpts):\n"
                + str(answer)
            )

        sections.append("\n\n".join(doc_lines))

    if "analytics" in completed:
        analytics_result = (
            state.get("analytics_result") or {}
        )

        analytics_answer = analytics_result.get(
            "answer"
        )

        if analytics_answer:
            sections.append(
                "### Dataset Analysis\n\n"
                "AI-generated analytics summary "
                "(verify numerical statements against "
                "the dataset results):\n"
                + str(analytics_answer)
            )

    if not sections:
        raise ValueError(
            "No successful analysis evidence is available"
        )

    answer = "\n\n---\n\n".join(sections)

    failed = state.get("failed_steps", [])

    if failed:
        failed_names = ", ".join(failed)

        answer += (
            "\n\n### Incomplete Analysis\n\n"
            "The following analysis steps could not "
            f"be completed: {failed_names}. "
            "The available evidence does not establish "
            "findings for those steps."
        )

    return answer
