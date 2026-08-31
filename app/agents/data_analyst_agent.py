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
2. Select the appropriate analytics tool.
3. Use the tool to calculate the requested result.
4. Interpret the calculated result.
5. Provide a concise business explanation.

Rules:

- Always use an analytics tool when the question requires
  a calculation.
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
    question: str
    profile: dict[str, Any]
    analysis: dict[str, Any]
    answer: str


def analyze_dataset(df: pd.DataFrame, question: str,) -> DataAnalystResult:
    """
    Analyze an uploaded dataset using LLM-driven tool selection.

    The LLM decides which analytics tools should be used.
    Python/Pandas performs the deterministic calculation.
    """

    if df.empty:
        raise ValueError("Cannot analyze an empty dataset.")

    if not question or not question.strip():
        raise ValueError("Analysis question cannot be empty.")

    logger.info("Starting LLM-driven dataset analysis: rows=%d, columns=%d",
                len(df),
                len(df.columns),)


    # Profile Dataset

    profile = profile_dataset(df)

    # Create tools bound to this dataset

    tools = create_analytics_tools(df)

    # Create LangChain chat model

    model = get_chat_model()

    # Bind analytics tools to the LLM

    model_with_tools = model.bind_tools(tools)

    # Ask the LLM to determine the required tool

    response = model_with_tools.invoke(
        [
            (
                "system",
                ANALYST_SYSTEM_PROMPT,
            ),
            (
                "user",
                (
                    f'Dataset columns:\n'
                    f'{list(df.columns)}\n\n'
                    f'User question:\n'
                    f'{question}'
                ),
            ),
        ]
    )

    # Inspect tool calls

    tool_calls = getattr(
        response,
        "tool_calls",
        [],
    )

    if not tool_calls:
        logger.warning("LLM did not select an analytics tool.")

        return DataAnalystResult(
            question=question,
            profile=profile,
            analysis={},
            answer=response.content,
        )

    # Execute selected tools

    analysis: dict[str, Any] = {}

    for tool_call in tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']

        logger.info(
            "LLM selected tool: %s with args: %s",
            tool_name,
            tool_args,
        )

        selected_tool = next(
            (
                tool for tool in tools
                if tool.name == tool_name
            ),
            None,
        )

        if selected_tool is None:
            raise ValueError(f"Unknown analytics tool: {tool_name}")

        result = selected_tool.invoke(tool_args)

        analysis[tool_name] = result

        # Ask LLM to interpret deterministic results

        interpretation_prompt = (
            f'User question:\n'
            f'{question}\n\n'
            f'Dataset profile:\n'
            f'{profile}\n\n'
            f'Deterministically calculated results:\n'
            f'{analysis}\n\n'
            f'Interpret these results and provide the business answer.'
        )

        answer = chat(
            ANALYST_SYSTEM_PROMPT,
            interpretation_prompt,
        )

        logger.info(
            "LLM-driven dataset analysis completed successfully."
        )

        return DataAnalystResult(
            question=question,
            profile=profile,
            analysis=analysis,
            answer=answer,
        )