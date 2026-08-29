import pandas as pd

from app.workflows.graph import planner_graph


def test_analytics_route():

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

    result = planner_graph.invoke(
        {
            "question": "What are the top products by revenue?",
            "route": "",
            "dataframe": df,
            "sql_result": None,
            "doc_result": None,
            "analytics_result": None,
            "final_answer": "",
        }
    )

    assert result["route"] == "analytics"

    assert result["analytics_result"] is not None

    assert (
        "top_products"
        in result["analytics_result"]["analysis"]
    )