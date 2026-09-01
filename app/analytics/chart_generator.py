"""
Reusable visualization utilities for the Analytics Agent.

This module is responsible only for converting already-calculated
analytics results into Plotly charts.

Business calculations remain inside analysis_tools.py.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_bar_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
) -> go.Figure:
    """
    Create a bar chart from a DataFrame.

    Args:
        df: DataFrame containing the chart data.
        x_column: Categorical/grouping column.
        y_column: Numerical metric column.
        title: Chart title.

    Returns:
        Plotly Figure.
    """

    _validate_columns(
        df,
        [x_column, y_column],
    )

    if df.empty:
        raise ValueError(
            "Cannot create a chart from an empty dataset."
        )

    figure = px.bar(
        df,
        x=x_column,
        y=y_column,
        title=title,
    )

    return figure


def create_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
) -> go.Figure:
    """
    Create a line chart from a DataFrame.

    Args:
        df: DataFrame containing the chart data.
        x_column: Time/ordering column.
        y_column: Numerical metric column.
        title: Chart title.

    Returns:
        Plotly Figure.
    """

    _validate_columns(
        df,
        [x_column, y_column],
    )

    if df.empty:
        raise ValueError(
            "Cannot create a chart from an empty dataset."
        )

    figure = px.line(
        df,
        x=x_column,
        y=y_column,
        title=title,
        markers=True,
    )

    return figure


def create_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_column: str,
    y_column: str,
    title: str,
) -> go.Figure:
    """
    Create a chart using the requested chart type.

    Supported chart types:
    - bar
    - line
    """

    if chart_type == "bar":
        return create_bar_chart(
            df,
            x_column,
            y_column,
            title,
        )

    if chart_type == "line":
        return create_line_chart(
            df,
            x_column,
            y_column,
            title,
        )

    raise ValueError(
        "Unsupported chart type. "
        "Supported types: bar, line."
    )


def _validate_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """
    Validate that required columns exist.
    """

    missing = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Columns not found in dataset: {missing}"
        )