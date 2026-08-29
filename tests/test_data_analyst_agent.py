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


def test_data_analyst_agent_top_products(monkeypatch):

    def fake_chat(
        system_prompt,
        user_prompt,
        temperature=0.2,
    ):
        return (
            "Key Insight:\n"
            "Laptop generated the highest revenue.\n\n"
            "Evidence:\n"
            "Laptop generated 4500 in revenue.\n\n"
            "Recommendation:\n"
            "Focus on the Laptop product category."
        )

    monkeypatch.setattr(
        data_analyst_agent,
        "chat",
        fake_chat,
    )

    df = sample_dataframe()

    result = data_analyst_agent.analyze_dataset(
        df,
        "What are the top products by revenue?",
    )

    assert result.answer
    assert "top_products" in result.analysis


def test_data_analyst_agent_region_revenue(monkeypatch):

    def fake_chat(
        system_prompt,
        user_prompt,
        temperature=0.2,
    ):
        return "Regional revenue analysis completed."

    monkeypatch.setattr(
        data_analyst_agent,
        "chat",
        fake_chat,
    )

    df = sample_dataframe()

    result = data_analyst_agent.analyze_dataset(
        df,
        "Show revenue by region.",
    )

    assert result.answer
    assert "revenue_by_region" in result.analysis