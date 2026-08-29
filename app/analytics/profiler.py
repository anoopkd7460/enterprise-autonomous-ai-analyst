import pandas as pd

def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate metadata and basic statistics about a dataset.
    """

    numeric_columns = df.select_dtypes(
        include = 'number'
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=['object', 'str', 'category', 'bool']
    ).columns.tolist()

    datetime_columns = df.select_dtypes(
        include=['datetime']
    ).columns.tolist()

    missing_values = {
        column: int(count)
        for column, count in df.isnull().sum().items()
        if count > 0
    }

    return {
        'rows': int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "datetime_columns": datetime_columns,
        "missing_values": missing_values,
        "duplicate_rows": int(df.duplicated().sum()),
        "dtypes": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
    }

def get_numeric_summary(df: pd.DataFrame) -> dict:
    """
    Generate deterministic statistics for numeric columns.
    """

    if df.empty:
        return {}

    numeric_df = df.select_dtypes(include='number')

    if numeric_df.empty:
        return {}

    summary = numeric_df.describe().round(2)

    return summary.to_dict()