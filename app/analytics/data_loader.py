"""
Dataset loading utilities.

This module is responsible for loading supported CSV and Excel files.
Dataset quality validation is delegated to data_validator.py.
"""

from pathlib import Path

import pandas as pd

from app.analytics.data_validator import validate_dataset
from app.utils.logger import get_logger


logger = get_logger(__name__)


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a CSV or Excel file into a Pandas DataFrame.

    Responsibilities:
        - Verify that the file exists.
        - Verify that the file extension is supported.
        - Load the dataset using Pandas.
        - Delegate DataFrame validation to data_validator.py.

    Args:
        file_path: Path to the dataset file.

    Returns:
        A validated Pandas DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file type is unsupported, cannot be read,
            or the loaded dataset fails validation.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {SUPPORTED_EXTENSIONS}"
        )

    try:
        if extension == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

    except Exception as exc:
        logger.exception(
            "Failed to load dataset: %s",
            path,
        )
        raise ValueError(
            f"Could not read dataset: {exc}"
        ) from exc

    validate_dataset(df)

    logger.info(
        "Dataset loaded successfully: %s rows=%d columns=%d",
        path.name,
        len(df),
        len(df.columns),
    )

    return df