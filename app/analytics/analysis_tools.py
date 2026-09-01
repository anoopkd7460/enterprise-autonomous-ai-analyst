"""
Deterministic analytics operations.

This module contains the actual Pandas-based calculations used by
the Analytics Agent. The LLM selects the operation, but Python/Pandas
performs the numerical computation.
"""

import pandas as pd


def group_by_metric(
    df: pd.DataFrame,
    group_column: str,
    metric_column: str,
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Aggregate a numerical metric by a grouping column.
    """

    _validate_columns(
        df,
        [group_column, metric_column],
    )

    result = (
        df.groupby(
            group_column,
            dropna=False,
        )[metric_column]
        .sum()
        .sort_values(
            ascending=ascending,
        )
        .reset_index()
    )

    return result


def top_n(
    df: pd.DataFrame,
    group_column: str,
    metric_column: str,
    n: int = 5,
) -> pd.DataFrame:
    """
    Return the top N groups ranked by a numerical metric.
    """

    if n < 1:
        raise ValueError(
            "n must be greater than or equal to 1."
        )

    result = group_by_metric(
        df,
        group_column,
        metric_column,
    )

    return result.head(n)


def summary_statistics(
    df: pd.DataFrame,
    column: str,
) -> dict:
    """
    Calculate descriptive statistics for a numerical column.
    """

    _validate_columns(
        df,
        [column],
    )

    series = pd.to_numeric(
        df[column],
        errors="coerce",
    ).dropna()

    if series.empty:
        raise ValueError(
            f"Column '{column}' does not contain numeric values."
        )

    return {
        "count": int(series.count()),
        "mean": round(
            float(series.mean()),
            2,
        ),
        "median": round(
            float(series.median()),
            2,
        ),
        "min": round(
            float(series.min()),
            2,
        ),
        "max": round(
            float(series.max()),
            2,
        ),
        "std": round(
            float(series.std()),
            2,
        ),
    }


def correlation_matrix(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate correlations between numerical columns.
    """

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.shape[1] < 2:
        raise ValueError(
            "At least two numeric columns are required."
        )

    return numeric_df.corr().round(3)


def trend_analysis(
    df: pd.DataFrame,
    period_column: str,
    metric_column: str,
    frequency: str = "month",
) -> pd.DataFrame:
    """
    Aggregate a numerical metric across chronological periods.

    Supported frequencies:
    - month
    - quarter
    - year

    The function performs historical trend analysis only.
    It does not forecast future values.

    Args:
        df: Input DataFrame.
        period_column: Column containing date/time values.
        metric_column: Numerical column to aggregate.
        frequency: Time aggregation level.

    Returns:
        DataFrame containing chronological periods and
        aggregated metric values.
    """

    _validate_columns(
        df,
        [period_column, metric_column],
    )

    if frequency not in {
        "month",
        "quarter",
        "year",
    }:
        raise ValueError(
            "frequency must be one of: "
            "month, quarter, year."
        )

    # ---------------------------------------------------------
    # Convert period column to datetime.
    # ---------------------------------------------------------

    period_values = pd.to_datetime(
        df[period_column],
        errors="coerce",
        format="mixed",
    )

    valid_periods = period_values.notna()

    if not valid_periods.any():
        raise ValueError(
            f"Column '{period_column}' does not contain "
            "valid date or time values."
        )

    # ---------------------------------------------------------
    # Convert metric column to numeric.
    # ---------------------------------------------------------

    metric_values = pd.to_numeric(
        df[metric_column],
        errors="coerce",
    )

    valid_rows = (
        valid_periods
        & metric_values.notna()
    )

    if not valid_rows.any():
        raise ValueError(
            f"Column '{metric_column}' does not contain "
            "valid numeric values."
        )

    trend_df = pd.DataFrame(
        {
            "period": period_values[valid_rows],
            "metric": metric_values[valid_rows],
        }
    )

    # ---------------------------------------------------------
    # Create the requested time period.
    # ---------------------------------------------------------

    if frequency == "month":
        trend_df["period"] = (
            trend_df["period"]
            .dt.to_period("M")
        )

    elif frequency == "quarter":
        trend_df["period"] = (
            trend_df["period"]
            .dt.to_period("Q")
        )

    else:
        trend_df["period"] = (
            trend_df["period"]
            .dt.to_period("Y")
        )

    # ---------------------------------------------------------
    # Aggregate metric by time period.
    # ---------------------------------------------------------

    result = (
        trend_df.groupby(
            "period",
            as_index=False,
        )["metric"]
        .sum()
        .sort_values("period")
        .reset_index(drop=True)
    )

    # ---------------------------------------------------------
    # A single period cannot establish a trend.
    # ---------------------------------------------------------

    if len(result) < 2:
        raise ValueError(
            "Trend analysis requires at least two "
            "distinct time periods."
        )

    # ---------------------------------------------------------
    # Convert periods into readable strings.
    # ---------------------------------------------------------

    if frequency == "month":
        result["period"] = (
            result["period"]
            .astype(str)
        )

    elif frequency == "quarter":
        result["period"] = (
            result["period"]
            .astype(str)
        )

    else:
        result["period"] = (
            result["period"]
            .astype(str)
        )

    result = result.rename(
        columns={
            "metric": metric_column,
        }
    )

    return result


def _validate_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """
    Validate that required columns exist in the DataFrame.
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