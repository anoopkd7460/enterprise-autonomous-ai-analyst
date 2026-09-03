from fastapi.testclient import TestClient

from app.api.main import app
from app.api import routes
from app.core.exceptions import (
    AIServiceError,
    AnalysisTimeoutError,
)

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == (
        "Enterprise Autonomous AI Analyst"
    )

    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get(
        "/api/v1/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"

    assert data["service"] == (
        "enterprise-autonomous-ai-analyst"
    )


def test_analyze_endpoint(monkeypatch):
    """
    Test the API without making a real LLM/API call.
    """

    def fake_analyze_with_details(
        question,
        dataframe=None,
    ):
        return {
            "final_answer": (
                "Laptop generated the highest revenue."
            ),
            "analytics_result": None,
        }

    monkeypatch.setattr(
        routes,
        "analyze_with_details",
        fake_analyze_with_details,
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": (
                "What are the top products by revenue?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What are the top products by revenue?"
    )

    assert data["answer"] == (
        "Laptop generated the highest revenue."
    )

    assert data["chart"] is None


def test_analyze_endpoint_validation():
    """
    Question shorter than 3 characters
    should be rejected by FastAPI validation.
    """

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": "Hi"
        },
    )

    assert response.status_code == 422


def test_analyze_endpoint_returns_chart(monkeypatch):
    """
    Verify that the API converts a generated Plotly chart
    into a JSON-compatible response.
    """

    class FakeChart:
        def to_dict(self):
            return {
                "data": [
                    {
                        "type": "bar",
                        "x": ["Laptop", "Mobile"],
                        "y": [3000, 1500],
                    }
                ],
                "layout": {
                    "title": {
                        "text": "Revenue by Product"
                    }
                },
            }

    def fake_analyze_with_details(
        question,
        dataframe=None,
    ):
        return {
            "final_answer": "Laptop generated the highest revenue.",
            "analytics_result": {
                "chart": FakeChart(),
            },
        }

    monkeypatch.setattr(
        routes,
        "analyze_with_details",
        fake_analyze_with_details,
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": "What are the top products by revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "Laptop generated the highest revenue."
    )

    assert data["chart"] is not None


    assert data["chart"]["data"][0]["type"] == "bar"

    assert data["chart"]["data"][0]["x"] == [
        "Laptop",
        "Mobile",
    ]

    assert data["chart"]["data"][0]["y"] == [
        3000,
        1500,
    ]

    assert (
        data["chart"]["layout"]["title"]["text"]
        == "Revenue by Product"
    )

def test_analyze_endpoint_returns_dataset_metadata(monkeypatch):
    """
    Verify that uploaded dataset metadata is returned
    by the analysis API.
    """

    def fake_analyze_with_details(
        question,
        dataframe=None,
    ):
        return {
            "final_answer": "Dataset analyzed successfully.",
            "analytics_result": None,
        }

    monkeypatch.setattr(
        routes,
        "analyze_with_details",
        fake_analyze_with_details,
    )

    csv_content = (
        "product,revenue,quantity\n"
        "Laptop,570000,10\n"
        "Mobile,350000,20\n"
        "Tablet,255000,15\n"
        "Monitor,174000,12\n"
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": "Summarize this dataset.",
        },
        files={
            "file": (
                "test.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_metadata"] is not None

    metadata = data["dataset_metadata"]

    assert metadata["filename"] == "test.csv"
    assert metadata["rows"] == 4
    assert metadata["columns"] == 3
    assert metadata["numeric_columns"] == 2
    assert metadata["missing_values"] == 0

def test_analyze_ai_service_error(monkeypatch):
    def fake_analyze_with_details(*args, **kwargs):
        raise AIServiceError(
            "LLM service unavailable"
        )

    monkeypatch.setattr(
        "app.api.routes.analyze_with_details",
        fake_analyze_with_details,
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": "What are the top products?"
        },
    )

    assert response.status_code == 503

    assert response.json()["detail"] == (
        "The AI service is temporarily unavailable. "
        "Please try again later."
    )

def test_analyze_timeout_error(monkeypatch):
    def fake_analyze_with_details(*args, **kwargs):
        raise AnalysisTimeoutError(
            "Analysis exceeded timeout"
        )

    monkeypatch.setattr(
        "app.api.routes.analyze_with_details",
        fake_analyze_with_details,
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": "What are the top products?"
        },
    )

    assert response.status_code == 504

    assert response.json()["detail"] == (
        "The analysis request timed out. "
        "Please try again."
    )

def test_analyze_csv_upload_integration(monkeypatch):
    def fake_analyze_with_details(
        question,
        dataframe=None,
    ):
        assert dataframe is not None
        assert len(dataframe) == 3
        assert list(dataframe.columns) == [
            "product",
            "revenue",
        ]

        return {
            "final_answer": (
                "Laptop generated the highest revenue."
            ),
            "analytics_result": None,
        }

    monkeypatch.setattr(
        routes,
        "analyze_with_details",
        fake_analyze_with_details,
    )

    csv_content = (
        "product,revenue\n"
        "Laptop,3000\n"
        "Mobile,1500\n"
        "Tablet,700\n"
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": (
                "What are the top products by revenue?"
            ),
        },
        files={
            "file": (
                "sales.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "Laptop generated the highest revenue."
    )

    assert data["dataset_metadata"] is not None

    assert data["dataset_metadata"]["filename"] == (
        "sales.csv"
    )

    assert data["dataset_metadata"]["rows"] == 3

    assert data["dataset_metadata"]["columns"] == 2

    assert data["dataset_metadata"]["numeric_columns"] == 1

    assert data["dataset_metadata"]["missing_values"] == 0


def test_analyze_csv_upload_with_chart_integration(monkeypatch):
    class FakeChart:
        def to_dict(self):
            return {
                "data": [
                    {
                        "type": "bar",
                        "x": ["Laptop", "Mobile"],
                        "y": [3000, 1500],
                    }
                ],
                "layout": {
                    "title": {
                        "text": "Revenue by Product"
                    }
                },
            }

    def fake_analyze_with_details(
        question,
        dataframe=None,
    ):
        assert dataframe is not None
        assert len(dataframe) == 3

        return {
            "final_answer": (
                "Laptop generated the highest revenue."
            ),
            "analytics_result": {
                "chart": FakeChart(),
            },
        }

    monkeypatch.setattr(
        routes,
        "analyze_with_details",
        fake_analyze_with_details,
    )

    csv_content = (
        "product,revenue\n"
        "Laptop,3000\n"
        "Mobile,1500\n"
        "Tablet,700\n"
    )

    response = client.post(
        "/api/v1/analyze",
        data={
            "question": (
                "What are the top products by revenue?"
            ),
        },
        files={
            "file": (
                "sales.csv",
                csv_content.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "Laptop generated the highest revenue."
    )

    assert data["chart"] is not None

    assert data["chart"]["data"][0]["type"] == "bar"

    assert data["chart"]["data"][0]["x"] == [
        "Laptop",
        "Mobile",
    ]

    assert data["chart"]["data"][0]["y"] == [
        3000,
        1500,
    ]

    assert (
        data["chart"]["layout"]["title"]["text"]
        == "Revenue by Product"
    )

    assert data["dataset_metadata"]["rows"] == 3
    assert data["dataset_metadata"]["columns"] == 2