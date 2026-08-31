from typing import Callable

import pandas as pd
from langchain_core.tools import tool

from app.analytics.analysis_tools import(
    top_n,
    group_by_metric,
    summary_statistics,
    correlation_matrix,
)

def create_analytics_tools(df: pd.DataFrame,) -> list[Callable]:
    """
    Create LangChain tools bound to a specific DataFrame.

    The LLM choose the operation and provides arguments.
    The DataFrame itself is controlled by the application.
    """

    @tool
    def top_n_tool(group_column: str, metric_column: str, n: int = 5,) -> list[dict]:
        """
        Return the top N groups ranked by a numerical metric.

        Use this when the user asks for:
        - top products
        - best-selling products
        - highest-revenue products
        - top regions
        - best-performing categories

        Args:
            group_column: Column used to group the data.
            metric_column: Numerical column to aggregate.
            n: Number of top groups to return.
        """

        if n < 1:
            raise ValueError("n must be greater than or equal to 1.")

        result = top_n(df, group_column, metric_column, n,)

        return result.to_dict(orient="records")


    @tool
    def group_by_metric_tool(group_column: str, metric_column: str, ascending: bool = False,) -> list[dict]:
        """
        Aggregate a numerical metric by a categorical column.

        Use this when the user asks for:
        - revenue by region
        - sales by product
        - units by category
        - profit by region

        Args:
            group_column: Column used for grouping.
            metric_column: Numerical metric to aggregate.
            ascending: Whether to sort from lowest to highest.
        """

        result = group_by_metric(df, group_column, metric_column, ascending,) 

        return result.to_dict(orient="records")


    @tool
    def summary_statistics_tool(column: str,) -> dict:
        """
        Calculate descriptive statistics for a numerical column.

        Use this when the user asks about:
        - average
        - mean
        - median
        - minimum
        - maximum
        - standard deviation
        - statistical summary

        Args:
            column: Numerical column to analyze.
        """
        return summary_statistics(df, column,)


    @tool
    def correlation_matrix_tool() -> dict:
        """
        Calculate correlations between numerical columns.

        Use this when the user asks about:
        - correlation
        - relationships between numerical variables
        - variables moving together
        """

        return correlation_matrix(df).to_dict()

    return [top_n_tool, group_by_metric_tool, summary_statistics_tool, correlation_matrix_tool,]