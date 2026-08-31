import pandas as pd

from app.workflows import graph


class FakeAnalyticsResult:

    profile = {
        "rows": 4,
        "columns": 2,
        "column_names": [
            "product",
            "revenue",
        ],
        "numeric_columns": [
            "revenue",
        ],
        "categorical_columns": [
            "product",
        ],
        "datetime_columns": [],
        "missing_values": {},
        "duplicate_rows": 0,
    }

    analysis = {
        "top_n_tool": [
            {
                "product": "Laptop",
                "revenue": 2500,
            },
            {
                "product": "Tablet",
                "revenue": 700,
            },
            {
                "product": "Mobile",
                "revenue": 500,
            },
        ]
    }

    answer = (
        "Key Insight:\n"
        "Laptop generated the highest revenue.\n\n"
        "Evidence:\n"
        "Laptop generated 2500 in revenue.\n\n"
        "Recommendation:\n"
        "Focus on Laptop."
    )


def fake_analyze_dataset(
    dataframe,
    question,
):
    return FakeAnalyticsResult()


def test_analytics_route(monkeypatch):

    # ---------------------------------------------------------
    # Mock the dependency where graph.py looks it up.
    # ---------------------------------------------------------

    monkeypatch.setattr(
        graph,
        "analyze_dataset",
        fake_analyze_dataset,
    )

    df = pd.DataFrame(
        {
            "product": [
                "Laptop",
                "Mobile",
                "Laptop",
                "Tablet",
            ],
            "revenue": [
                1000,
                500,
                1500,
                700,
            ],
        }
    )

    result = graph.planner_graph.invoke(
        {
            "question": (
                "What are the top products by revenue?"
            ),
            "route": "",
            "dataframe": df,
            "sql_result": None,
            "doc_result": None,
            "analytics_result": None,
            "final_answer": "",
        }
    )

    # ---------------------------------------------------------
    # Verify router
    # ---------------------------------------------------------

    assert result["route"] == "analytics"

    # ---------------------------------------------------------
    # Verify Analytics Agent executed
    # ---------------------------------------------------------

    assert result["analytics_result"] is not None

    # ---------------------------------------------------------
    # Verify analysis
    # ---------------------------------------------------------

    analysis = (
        result["analytics_result"]["analysis"]
    )

    assert "top_n_tool" in analysis

    top_products = analysis["top_n_tool"]

    assert (
        top_products[0]["product"]
        == "Laptop"
    )

    assert (
        top_products[0]["revenue"]
        == 2500
    )

    # ---------------------------------------------------------
    # Verify final answer
    # ---------------------------------------------------------

    assert result["final_answer"]