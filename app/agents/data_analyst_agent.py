from dataclasses import dataclass
from typing import Any

import pandas as pd

from app.analytics.analysis_tools import (
    correlation_matrix,
    group_by_metric,
    summary_statistics,
    top_n,
)
from app.analytics.profiler import (
    get_numeric_summary,
    profile_dataset,
)
from app.llm.client import chat
from app.utils.logger import get_logger


logger = get_logger(__name__)


ANALYST_SYSTEM_PROMPT = """
You are an experienced business data analyst.

Your task is to interpret deterministic analysis results
calculated using Python/Pandas and convert them into useful
business insights.

You will receive:

1. The user's business question.
2. Dataset profile information.
3. Deterministically calculated analysis results.

Rules:

- Never invent numbers.
- Use only information present in the supplied analysis results.
- Do not perform complex calculations yourself.
- Clearly distinguish facts from interpretations.
- Identify the most important business insight.
- If the available analysis is insufficient, explicitly say so.
- Provide an actionable business recommendation.
- Keep the explanation concise and executive-friendly.
- Avoid unnecessary technical terminology.

Structure your response as:

Key Insight:
<main business finding>

Evidence:
<important evidence supporting the finding>

Recommendation:
<one actionable recommendation>
"""


@dataclass
class DataAnalystResult:
    question: str
    profile: dict[str, Any]
    analysis: dict[str, Any]
    answer: str


def analyze_dataset(
    df: pd.DataFrame,
    question: str,
) -> DataAnalystResult:
    """
    Analyze an uploaded dataset and generate business insights.

    Python/Pandas performs deterministic calculations.
    The LLM interprets those calculations.
    """

    if df.empty:
        raise ValueError("Cannot analyze an empty dataset.")

    if not question or not question.strip():
        raise ValueError("Analysis question cannot be empty.")

    logger.info(
        "Starting dataset analysis: rows=%d, columns=%d",
        len(df),
        len(df.columns),
    )

    # ---------------------------------------------------------
    # 1. Profile the dataset
    # ---------------------------------------------------------

    profile = profile_dataset(df)

    # ---------------------------------------------------------
    # 2. Generate deterministic numerical summary
    # ---------------------------------------------------------

    analysis: dict[str, Any] = {
        "numeric_summary": get_numeric_summary(df),
    }

    # ---------------------------------------------------------
    # 3. Determine which deterministic analysis is required
    #
    # NOTE:
    # This is intentionally rule-based in Phase 2.
    # We will replace this with LLM tool calling later.
    # ---------------------------------------------------------

    question_lower = question.lower()

    if "top" in question_lower and "product" in question_lower:

        if "product" in df.columns and "revenue" in df.columns:

            logger.info(
                "Running top-product revenue analysis."
            )

            analysis["top_products"] = top_n(
                df=df,
                group_column="product",
                metric_column="revenue",
                n=5,
            ).to_dict(orient="records")

    elif (
        "region" in question_lower
        and "revenue" in question_lower
    ):

        if "region" in df.columns and "revenue" in df.columns:

            logger.info(
                "Running regional revenue analysis."
            )

            analysis["revenue_by_region"] = group_by_metric(
                df=df,
                group_column="region",
                metric_column="revenue",
            ).to_dict(orient="records")

    elif "correlation" in question_lower:

        logger.info(
            "Running correlation analysis."
        )

        analysis["correlation"] = (
            correlation_matrix(df).to_dict()
        )

    else:

        logger.info(
            "No specialized analysis requested; using dataset summary."
        )

    # ---------------------------------------------------------
    # 4. Send calculated results to the LLM
    # ---------------------------------------------------------

    prompt = (
        f"User question:\n"
        f"{question}\n\n"
        f"Dataset profile:\n"
        f"{profile}\n\n"
        f"Deterministically calculated analysis:\n"
        f"{analysis}\n\n"
        f"Business analysis:"
    )

    answer = chat(
        ANALYST_SYSTEM_PROMPT,
        prompt,
    )

    # ---------------------------------------------------------
    # 5. Return structured result
    # ---------------------------------------------------------

    logger.info(
        "Dataset analysis completed successfully."
    )

    return DataAnalystResult(
        question=question,
        profile=profile,
        analysis=analysis,
        answer=answer,
    )