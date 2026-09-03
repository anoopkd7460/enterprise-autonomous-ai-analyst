from pathlib import Path

import pandas as pd
import pytest

from app.analytics.data_loader import load_dataset


def test_load_csv_success(tmp_path: Path):
    file_path = tmp_path / "sales.csv"

    pd.DataFrame(
        {
            "Product": ["A", "B"],
            "Revenue": [100, 200],
        }
    ).to_csv(file_path, index=False)

    df = load_dataset(str(file_path))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["Product", "Revenue"]


def test_load_excel_success(tmp_path: Path):
    file_path = tmp_path / "sales.xlsx"

    pd.DataFrame(
        {
            "Product": ["A", "B"],
            "Revenue": [100, 200],
        }
    ).to_excel(file_path, index=False)

    df = load_dataset(str(file_path))

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_load_dataset_file_not_found(tmp_path: Path):
    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        load_dataset(str(file_path))


def test_load_dataset_unsupported_file_type(tmp_path: Path):
    file_path = tmp_path / "sales.json"
    file_path.write_text('{"Product": "A"}')

    with pytest.raises(ValueError, match="Unsupported file type"):
        load_dataset(str(file_path))


def test_load_dataset_empty_csv(tmp_path: Path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")

    with pytest.raises(ValueError):
        load_dataset(str(file_path))


def test_load_dataset_completely_empty_column(tmp_path: Path):
    file_path = tmp_path / "invalid.csv"

    pd.DataFrame(
        {
            "Product": ["A", "B"],
            "Revenue": [None, None],
        }
    ).to_csv(file_path, index=False)

    with pytest.raises(ValueError, match="completely empty columns"):
        load_dataset(str(file_path))