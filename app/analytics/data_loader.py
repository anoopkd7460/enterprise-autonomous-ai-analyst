from pathlib import Path

import pandas as pd

from app.utils.logger import get_logger

logger = get_logger(__name__)


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a CSV or Excel file into a Pandas DataFrame.
    The loader is intentionally responsible only for loading data.
    Analysis and validation are handled by separate modules.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f'File not found: {file_path}')

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f'Unsupported file type: {extension}. '
            f'Supported types: {SUPPORTED_EXTENSIONS}'
        )

    try:
        if extension == ".csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

    except Exception as exc:
        logger.exception("Failed to load dataset: %s", path)
        raise ValueError(f'Could not read dataset: {exc}') from exc

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    logger.info(
        "Dataset loaded successfully: %s rows=%d columns=%d",
        path.name,
        len(df),
        len(df.columns),
    )

    return df