from fastapi.testclient import TestClient

from app.api.main import app
from app.api import routes


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

    def fake_answer_question(
        question,
        dataframe=None,
    ):
        return (
            "Laptop generated the highest revenue."
        )

    monkeypatch.setattr(
        routes,
        "answer_question",
        fake_answer_question,
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