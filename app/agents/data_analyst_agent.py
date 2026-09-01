"""
Data Analyst Agent.

Uses an LLM to select deterministic analytics tools for an uploaded
CSV/Excel dataset, executes the selected tools, and then uses the LLM
to interpret the calculated evidence into a business-friendly answer.
"""

from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.analytics.profiler import profile_dataset
from app.llm.client import chat
from app.llm.langchain_client import get_chat_model
from app.tools.analytics_tools import create_analytics_tools
from app.utils.logger import get_logger


logger = get_logger(__name__)


ANALYST_SYSTEM_PROMPT = """
You are an experienced business data analyst.

You analyze user-provided datasets using deterministic
analytics tools.

Your workflow is:

1. Understand the user's business question.
2. Select the appropriate analytics tool or tools.
3. Use the selected tools to calculate the requested results.
4. Interpret the calculated results.
5. Provide a concise business explanation.

Rules:

- Always use an analytics tool when the question requires
  a calculation.
- You may select multiple analytics tools when multiple
  calculations are required.
- Never invent numbers.
- Never perform important numerical calculations yourself
  when a tool can calculate them.
- Use only numbers returned by the analytics tools.
- Clearly distinguish facts from interpretations.
- If the available dataset cannot answer the question,
  explain why.
- Provide one actionable recommendation.
- Avoid unnecessary technical terminology.

Return:

Key Insight:
<main business finding>

Evidence:
<important numerical evidence>

Recommendation:
<one actionable recommendation>
"""


@dataclass
class DataAnalystResult:
    """
    Result returned by the Data Analyst Agent.
    """

    question: str
    profile: dict[str, Any]
    analysis: dict[str, Any]
    answer: str


def analyze_dataset(
    df: pd.DataFrame,
    question: str,
) -> DataAnalystResult:
    """
    Analyze an uploaded dataset using LLM-driven tool selection.

    The LLM decides which analytics tools should be used.
    Python/Pandas performs the deterministic calculations.
    The LLM then interprets the calculated evidence.

    Args:
        df: Uploaded Pandas DataFrame.
        question: User's business question.

    Returns:
        DataAnalystResult containing:
        - dataset profile
        - deterministic analysis results
        - final business answer

    Raises:
        ValueError:
            If the dataset is empty or the question is empty.
    """

    # ---------------------------------------------------------
    # Validate input
    # ---------------------------------------------------------

    if df.empty:
        raise ValueError(
            "Cannot analyze an empty dataset."
        )

    if not question or not question.strip():
        raise ValueError(
            "Analysis question cannot be empty."
        )

    logger.info(
        "Starting LLM-driven dataset analysis: rows=%d, columns=%d",
        len(df),
        len(df.columns),
    )

    # ---------------------------------------------------------
    # Profile dataset
    # ---------------------------------------------------------

    profile = profile_dataset(df)

    logger.info(
        "Dataset profiling completed."
    )

    # ---------------------------------------------------------
    # Create tools bound to this specific dataset
    # ---------------------------------------------------------

    tools = create_analytics_tools(df)

    logger.info(
        "Created %d analytics tools.",
        len(tools),
    )

    # ---------------------------------------------------------
    # Create LangChain chat model
    # ---------------------------------------------------------

    model = get_chat_model()

    # ---------------------------------------------------------
    # Bind analytics tools to the LLM
    # ---------------------------------------------------------

    model_with_tools = model.bind_tools(tools)

    # ---------------------------------------------------------
    # Ask LLM to determine required analytics tool(s)
    # ---------------------------------------------------------

    response = model_with_tools.invoke(
        [
            (
                "system",
                ANALYST_SYSTEM_PROMPT,
            ),
            (
                "user",
                (
                    f"Dataset columns:\n"
                    f"{list(df.columns)}\n\n"
                    f"Dataset profile:\n"
                    f"{profile}\n\n"
                    f"User question:\n"
                    f"{question}"
                ),
            ),
        ]
    )

    # ---------------------------------------------------------
    # Inspect tool calls
    # ---------------------------------------------------------

    tool_calls = getattr(
        response,
        "tool_calls",
        [],
    )

    if not tool_calls:

        logger.warning(
            "LLM did not select an analytics tool."
        )

        return DataAnalystResult(
            question=question,
            profile=profile,
            analysis={},
            answer=str(response.content),
        )

    logger.info(
        "LLM selected %d analytics tool(s).",
        len(tool_calls),
    )

    # Execute ALL selected tools

    analysis: dict[str, Any] = {}

    for tool_call in tool_calls:

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        logger.info(
            "Executing analytics tool: %s with args: %s",
            tool_name,
            tool_args,
        )

        selected_tool = next(
            (
                tool
                for tool in tools
                if tool.name == tool_name
            ),
            None,
        )

        if selected_tool is None:
            raise ValueError(
                f"Unknown analytics tool: {tool_name}"
            )

        try:

            result = selected_tool.invoke(
                tool_args
            )

        except Exception as exc:

            logger.exception(
                "Analytics tool failed: %s",
                tool_name,
            )

            raise ValueError(
                f"Analytics tool '{tool_name}' failed: {exc}"
            ) from exc

        analysis[tool_name] = result

        logger.info(
            "Analytics tool completed successfully: %s",
            tool_name,
        )

    # Interpret deterministic results

    interpretation_prompt = (
        f"User question:\n"
        f"{question}\n\n"
        f"Dataset profile:\n"
        f"{profile}\n\n"
        f"Deterministically calculated results:\n"
        f"{analysis}\n\n"
        "Interpret these results and provide the business answer."
    )

    answer = chat(
        ANALYST_SYSTEM_PROMPT,
        interpretation_prompt,
    )

    logger.info(
        "LLM-driven dataset analysis completed successfully."
    )

    # Return complete result

    return DataAnalystResult(
        question=question,
        profile=profile,
        analysis=analysis,
        answer=answer,
    )