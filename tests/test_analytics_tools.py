import pandas as pd

from app.tools.analytics_tools import (create_analytics_tools,)

def sample_dataframe():
    return pd.DataFrame(
        {
            "region": [
                "North",
                "South",
                "West",
                "West"
            ],
            "product": [
                "Laptop",
                "Mobile",
                "Laptop",
                "Tablet",
            ],
            "revenue": [
                1000,
                500,
                2000,
                700,
            ],
            "units_sold": [
                10,
                20,
                15,
                8,
            ],
        }
    )


def test_top_n_tool():

    df = sample_dataframe()

    tools = create_analytics_tools(df)

    top_tool = next(
        tool
        for tool in tools
        if tool.name == "top_n_tool"
    )

    result = top_tool.invoke(
        {
            "group_column": "product",
            "metric_column": "revenue",
            "n": 2,
        }
    )

    assert result[0]["product"] == "Laptop"
    assert result[0]["revenue"] == 3000


def test_group_by_metric_tool():

    df = sample_dataframe()

    tools = create_analytics_tools(df)

    group_tool = next(
        tool
        for tool in tools
        if tool.name == "group_by_metric_tool"
    )

    result = group_tool.invoke(
        {
            "group_column": "region",
            "metric_column": "revenue",
        }
    )

    assert result[0]["region"] == "West"
    assert result[0]["revenue"] == 2700


def test_summary_statistics_tool():

    df = sample_dataframe()

    tools = create_analytics_tools(df)

    stats_tool = next(
        tool
        for tool in tools
        if tool.name == "summary_statistics_tool"
    )

    result = stats_tool.invoke(
        {
            "column": "revenue",
        }
    )

    assert result["count"] == 4
    assert result["max"] == 2000


def test_correlation_matrix_tool():

    df = sample_dataframe()

    tools = create_analytics_tools(df)

    correlation_tool = next(
        tool
        for tool in tools
        if tool.name == "correlation_matrix_tool"
    )

    result = correlation_tool.invoke({})

    assert "revenue" in result
    assert "units_sold" in result