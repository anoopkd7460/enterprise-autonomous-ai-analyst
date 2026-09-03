import pandas as pd
import pytest

from app.agents import data_analyst_agent
from app.core.exceptions import AIServiceError


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

def test_visualization_created_for_top_n(monkeypatch):

    from app.agents import data_analyst_agent

    class FakeResponse:
        tool_calls = [
            {
                "name": "top_n_tool",
                "args": {
                    "group_column": "product",
                    "metric_column": "revenue",
                    "n": 2,
                },
            }
        ]
        content = ""

    class FakeModel:

        def bind_tools(self, tools):
            return self

        def invoke(self, messages):
            return FakeResponse()

    monkeypatch.setattr(
        data_analyst_agent,
        "get_chat_model",
        lambda: FakeModel(),
    )

    monkeypatch.setattr(
        data_analyst_agent,
        "chat",
        lambda *args, **kwargs: "Business answer",
    )

    df = pd.DataFrame(
        {
            "product": [
                "Laptop",
                "Mobile",
                "Tablet",
            ],
            "revenue": [
                3000,
                1500,
                700,
            ],
        }
    )

    result = data_analyst_agent.analyze_dataset(
        df,
        "What are the top products by revenue?",
    )

    assert result.chart is not None


def test_visualization_created_for_trend(monkeypatch):

    from app.agents import data_analyst_agent

    class FakeResponse:
        tool_calls = [
            {
                "name": "trend_analysis_tool",
                "args": {
                    "period_column": "date",
                    "metric_column": "revenue",
                    "frequency": "month",
                },
            }
        ]
        content = ""

    class FakeModel:

        def bind_tools(self, tools):
            return self

        def invoke(self, messages):
            return FakeResponse()

    monkeypatch.setattr(
        data_analyst_agent,
        "get_chat_model",
        lambda: FakeModel(),
    )

    monkeypatch.setattr(
        data_analyst_agent,
        "chat",
        lambda *args, **kwargs: "Trend answer",
    )

    df = pd.DataFrame(
        {
            "date": [
                "2024-01-01",
                "2024-02-01",
                "2024-03-01",
                "2024-04-01",
            ],
            "revenue": [
                1000,
                1500,
                2000,
                2500,
            ],
        }
    )

    result = data_analyst_agent.analyze_dataset(
        df,
        "Show the revenue trend.",
    )

    assert result.chart is not None

def test_data_analyst_agent_llm_failure(monkeypatch):

    class FailingModel:

        def bind_tools(self, tools):
            return self

        def invoke(self, messages):
            raise RuntimeError("Groq service unavailable")

    monkeypatch.setattr(
        data_analyst_agent,
        "get_chat_model",
        lambda: FailingModel(),
    )

    df = sample_dataframe()

    with pytest.raises(AIServiceError):
        data_analyst_agent.analyze_dataset(
            df,
            "What are the top products by revenue?",
        )