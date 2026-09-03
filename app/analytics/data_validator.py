"""
Dataset validation utilities.

This module validates an already-loaded Pandas DataFrame.
File loading responsibilities remain inside data_loader.py.
"""

import pandas as pd

from app.utils.logger import get_logger


logger = get_logger(__name__)


def validate_dataset(df: pd.DataFrame) -> None:
    """
    Validate whether a DataFrame is suitable for analysis.

    Responsibilities:
        - Verify that the input is a Pandas DataFrame.
        - Reject empty datasets.
        - Reject duplicate column names.
        - Reject completely empty columns.

    Args:
        df: Pandas DataFrame to validate.

    Raises:
        ValueError: If the dataset fails a validation check.
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError(
            "Invalid dataset. Expected a Pandas DataFrame."
        )

    if df.empty:
        raise ValueError(
            "The uploaded dataset is empty."
        )

    if df.columns.duplicated().any():
        duplicated_columns = (
            df.columns[df.columns.duplicated()]
            .tolist()
        )

        raise ValueError(
            "The dataset contains duplicate column names: "
            f"{duplicated_columns}"
        )

    completely_empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if completely_empty_columns:
        raise ValueError(
            "The dataset contains completely empty columns: "
            f"{completely_empty_columns}"
        )

    logger.info(
        "Dataset validation successful: rows=%d columns=%d",
        len(df),
        len(df.columns),
    )