import pandas as pd

def group_by_metric(df: pd.DataFrame, group_column: str, metric_column: str, ascending: bool = False,) -> pd.DataFrame:
    _validate_columns(
        df, [group_column, metric_column],
    )

    result = (df.groupby(group_column, dropna=False)[metric_column].sum().sort_values(ascending=ascending).reset_index())

    return result


def top_n(df:pd.DataFrame, group_column: str, metric_column: str, n: int=5,) -> pd.DataFrame:
    result = group_by_metric(df, group_column, metric_column,)

    return result.head(n)


def summary_statistics(df:pd.DataFrame, column: str,) -> dict:

    _validate_columns(df, [column])

    series = pd.to_numeric(df[column], errors='coerce',).dropna()

    if series.empty:
        raise ValueError(f"Column '{column}' does not contain numeric values.")

    return {"count": int(series.count()),
            "mean": round(float(series.mean()), 2),
            "median": round(float(series.median()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "std": round(float(series.std()), 2),
    }

def correlation_matrix(
    df: pd.DataFrame,
) -> pd.DataFrame:

    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] < 2:
        raise ValueError(
            "At least two numeric columns are required."
        )

    return numeric_df.corr().round(3)


def _validate_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:

    missing = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Columns not found in dataset: {missing}"
        )