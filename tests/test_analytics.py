import pandas as pd

from app.analytics.analysis_tools import (
    group_by_metric,
    summary_statistics,
    top_n,
)
from app.analytics.profiler import profile_dataset


def sample_dataframe():
    return pd.DataFrame(
        {
            "region": [
                "North",
                "North",
                "South",
                "South",
                "West",
            ],
            "product": [
                "Laptop",
                "Mobile",
                "Laptop",
                "Mobile",
                "Laptop",
            ],
            "revenue": [
                1000,
                500,
                1500,
                700,
                2000,
            ],
            "units": [
                2,
                5,
                3,
                7,
                4,
            ],
        }
    )


def test_profile_dataset():

    df = sample_dataframe()

    profile = profile_dataset(df)

    assert profile["rows"] == 5
    assert profile["columns"] == 4
    assert "revenue" in profile["numeric_columns"]


def test_group_by_metric():

    df = sample_dataframe()

    result = group_by_metric(
        df,
        "region",
        "revenue",
    )

    assert result.iloc[0]["region"] == "South"
    assert result.iloc[0]["revenue"] == 2200


def test_top_n():

    df = sample_dataframe()

    result = top_n(
        df,
        "product",
        "revenue",
        n=1,
    )

    assert result.iloc[0]["product"] == "Laptop"


def test_summary_statistics():

    df = sample_dataframe()

    result = summary_statistics(
        df,
        "revenue",
    )

    assert result["min"] == 500
    assert result["max"] == 2000