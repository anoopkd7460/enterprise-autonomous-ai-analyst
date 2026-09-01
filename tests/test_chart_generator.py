import pandas as pd
import pytest

from app.analytics.chart_generator import (
    create_bar_chart,
    create_line_chart,
    create_chart,
)


def sample_dataframe():
    return pd.DataFrame(
        {
            "region": [
                "North",
                "South",
                "West",
            ],
            "revenue": [
                1000,
                1500,
                2000,
            ],
        }
    )


def test_create_bar_chart():

    df = sample_dataframe()

    figure = create_bar_chart(
        df,
        "region",
        "revenue",
        "Revenue by Region",
    )

    assert figure is not None
    assert len(figure.data) == 1


def test_create_line_chart():

    df = pd.DataFrame(
        {
            "period": [
                "2024-01",
                "2024-02",
                "2024-03",
            ],
            "revenue": [
                1000,
                1500,
                2000,
            ],
        }
    )

    figure = create_line_chart(
        df,
        "period",
        "revenue",
        "Revenue Trend",
    )

    assert figure is not None
    assert len(figure.data) == 1


def test_create_chart_bar():

    df = sample_dataframe()

    figure = create_chart(
        df,
        "bar",
        "region",
        "revenue",
        "Revenue by Region",
    )

    assert figure is not None


def test_create_chart_line():

    df = pd.DataFrame(
        {
            "period": [
                "2024-01",
                "2024-02",
                "2024-03",
            ],
            "revenue": [
                1000,
                1500,
                2000,
            ],
        }
    )

    figure = create_chart(
        df,
        "line",
        "period",
        "revenue",
        "Revenue Trend",
    )

    assert figure is not None
    assert len(figure.data) == 1


def test_create_chart_invalid_type():

    df = sample_dataframe()

    with pytest.raises(
        ValueError,
        match="Unsupported chart type",
    ):
        create_chart(
            df,
            "pie",
            "region",
            "revenue",
            "Revenue",
        )


def test_create_chart_missing_column():

    df = sample_dataframe()

    with pytest.raises(
        ValueError,
        match="Columns not found",
    ):
        create_bar_chart(
            df,
            "category",
            "revenue",
            "Revenue",
        )


def test_create_chart_empty_dataframe():

    df = pd.DataFrame(
        columns=[
            "region",
            "revenue",
        ]
    )

    with pytest.raises(
        ValueError,
        match="empty dataset",
    ):
        create_bar_chart(
            df,
            "region",
            "revenue",
            "Revenue",
        )