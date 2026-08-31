import pandas as pd

from app.agents import data_analyst_agent


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
        }
    )


class FakeResponse:

    def __init__(self, tool_name, args):
        self.tool_calls = [
            {
                "name": tool_name,
                "args": args,
            }
        ]

        self.content = ""


class FakeModel:

    def __init__(self, tool_name, args):
        self.tool_name = tool_name
        self.args = args

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):

        return FakeResponse(
            self.tool_name,
            self.args,
        )


def test_data_analyst_agent_top_products(monkeypatch):

    fake_model = FakeModel(
        "top_n_tool",
        {
            "group_column": "product",
            "metric_column": "revenue",
            "n": 5,
        },
    )

    monkeypatch.setattr(
        data_analyst_agent,
        "get_chat_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        data_analyst_agent,
        "chat",
        lambda *args, **kwargs: (
            "Key Insight:\n"
            "Laptop generated the highest revenue.\n\n"
            "Evidence:\n"
            "Laptop generated 4500 in revenue.\n\n"
            "Recommendation:\n"
            "Focus on Laptop."
        ),
    )

    df = sample_dataframe()

    result = data_analyst_agent.analyze_dataset(
        df,
        "What are the top products by revenue?",
    )

    assert result.answer

    assert "top_n_tool" in result.analysis

    assert (
        result.analysis["top_n_tool"][0]["product"]
        == "Laptop"
    )

    assert (
        result.analysis["top_n_tool"][0]["revenue"]
        == 4500
    )


def test_data_analyst_agent_region_revenue(monkeypatch):

    fake_model = FakeModel(
        "group_by_metric_tool",
        {
            "group_column": "region",
            "metric_column": "revenue",
        },
    )

    monkeypatch.setattr(
        data_analyst_agent,
        "get_chat_model",
        lambda: fake_model,
    )

    monkeypatch.setattr(
        data_analyst_agent,
        "chat",
        lambda *args, **kwargs: (
            "Regional revenue analysis completed."
        ),
    )

    df = sample_dataframe()

    result = data_analyst_agent.analyze_dataset(
        df,
        "Show revenue by region.",
    )

    assert result.answer

    assert "group_by_metric_tool" in result.analysis

    assert (
        result.analysis[
            "group_by_metric_tool"
        ][0]["region"]
        == "South"
    )

    assert (
        result.analysis[
            "group_by_metric_tool"
        ][0]["revenue"]
        == 2200
    )