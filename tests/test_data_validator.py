import pandas as pd
import pytest

from app.analytics.data_validator import validate_dataset


def test_validate_valid_dataset():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mobile"],
            "revenue": [1000, 500],
        }
    )

    validate_dataset(df)


def test_validate_empty_dataset():
    df = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="empty",
    ):
        validate_dataset(df)


def test_validate_duplicate_columns():
    df = pd.DataFrame(
        [
            ["Laptop", 1000, 1000],
            ["Mobile", 500, 500],
        ],
        columns=[
            "product",
            "revenue",
            "revenue",
        ],
    )

    with pytest.raises(
        ValueError,
        match="duplicate column names",
    ):
        validate_dataset(df)


def test_validate_completely_empty_columns():
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Mobile"],
            "revenue": [1000, 500],
            "customer_age": [None, None],
        }
    )

    with pytest.raises(
        ValueError,
        match="completely empty columns",
    ):
        validate_dataset(df)


def test_validate_rejects_non_dataframe():
    with pytest.raises(
        ValueError,
        match="Pandas DataFrame",
    ):
        validate_dataset(
            {"product": ["Laptop"]}
        )