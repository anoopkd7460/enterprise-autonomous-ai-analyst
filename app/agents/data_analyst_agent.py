from dataclasses import dataclass

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

You receive:
1. A user's business question.
2. Dataset metadata.
3. Deterministically calculated analysis results.

Your job is to interpret the results and produce a concise,
executive-friendly answer.

Rules:
- Do not invent numbers.
- Only use numbers present in the analysis results.
- Clearly distinguish facts from interpretations.
- Identify the most important business insight.
- If the evidence is insufficient, say so.
- Provide one actionable recommendation.
- Avoid technical jargon.

Return:

Key Insight:
<answer>

Evidence:
<important numerical evidence>

Recommendation:
<one actionable recommendation>
"""


@dataclass
class DataAnalystResult:
    question: str
    profile: dict
    analysis: dict
    answer: str


def analyze_dataset(
    df: pd.DataFrame,
    question: str,
) -> DataAnalystResult:

    profile = profile_dataset(df)

    analysis = {
        "numeric_summary": get_numeric_summary(df),
    }

    question_lower = question.lower()

    # Basic deterministic analysis for the first version.
    if "top" in question_lower and "product" in question_lower:
        if "product" in df.columns and "revenue" in df.columns:
            analysis["top_products"] = top_n(
                df,
                "product",
                "revenue",
                n=5,
            ).to_dict(orient="records")

    elif "region" in question_lower and "revenue" in question_lower:
        if "region" in df.columns and "revenue" in df.columns:
            analysis["revenue_by_region"] = group_by_metric(
                df,
                "region",
                "revenue",
            ).to_dict(orient="records")

    elif "correlation" in question_lower:
        analysis["correlation"] = correlation_matrix(
            df
        ).to_dict()

    prompt = (
        f"User question:\n{question}\n\n"
        f"Dataset profile:\n{profile}\n\n"
        f"Calculated analysis:\n{analysis}\n\n"
        f"Business analysis:"
    )

    answer = chat(
        ANALYST_SYSTEM_PROMPT,
        prompt,
    )

    return DataAnalystResult(
        question=question,
        profile=profile,
        analysis=analysis,
        answer=answer,
    )