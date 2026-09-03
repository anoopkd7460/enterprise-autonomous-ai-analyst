import requests

from streamlit_app.api_client import (
    APIClientError,
    analyze,
    health_check,
)


class FakeResponse:

    def __init__(
        self,
        status_code=200,
        payload=None,
        text="",
    ):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload

        return self._payload


def test_analyze_success(monkeypatch):

    def fake_post(
        url,
        data,
        files,
        timeout,
    ):
        assert url == (
            "http://localhost:8000/api/v1/analyze"
        )

        assert data["question"] == (
            "What are the top products?"
        )

        assert files is None

        assert timeout == 120

        return FakeResponse(
            payload={
                "question": "What are the top products?",
                "answer": "Laptop is the top product.",
                "chart": None,
            }
        )

    monkeypatch.setattr(
        requests,
        "post",
        fake_post,
    )

    result = analyze(
        "What are the top products?"
    )

    assert result["answer"] == (
        "Laptop is the top product."
    )


def test_analyze_connection_error(monkeypatch):

    def fake_post(
        *args,
        **kwargs,
    ):
        raise requests.ConnectionError(
            "Connection failed"
        )

    monkeypatch.setattr(
        requests,
        "post",
        fake_post,
    )

    try:

        analyze(
            "What are the top products?"
        )

        assert False, (
            "Expected APIClientError"
        )

    except APIClientError as exc:

        assert "Unable to connect" in str(exc)


def test_analyze_http_error(monkeypatch):

    def fake_post(
        *args,
        **kwargs,
    ):
        return FakeResponse(
            status_code=400,
            payload={
                "detail": "Unsupported file type"
            },
            text="Bad request",
        )

    monkeypatch.setattr(
        requests,
        "post",
        fake_post,
    )

    try:

        analyze(
            "What are the top products?"
        )

        assert False, (
            "Expected APIClientError"
        )

    except APIClientError as exc:

        assert "HTTP 400" in str(exc)
        assert "Unsupported file type" in str(exc)


def test_analyze_with_file(monkeypatch):

    captured = {}

    def fake_post(
        url,
        data,
        files,
        timeout,
    ):

        captured["files"] = files

        return FakeResponse(
            payload={
                "question": data["question"],
                "answer": "Analysis complete.",
                "chart": None,
            }
        )

    monkeypatch.setattr(
        requests,
        "post",
        fake_post,
    )

    from io import BytesIO

    uploaded_file = BytesIO(
        b"product,revenue\nLaptop,1000"
    )

    uploaded_file.name = "sales.csv"

    result = analyze(
        "What is the revenue?",
        file=uploaded_file,
    )

    assert result["answer"] == (
        "Analysis complete."
    )

    assert captured["files"] is not None

def test_health_check_success(monkeypatch):
    """Verify successful API health check."""

    class FakeResponse:
        ok = True

        def json(self):
            return {
                "status": "healthy",
                "service": "enterprise-autonomous-ai-analyst",
            }

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "streamlit_app.api_client.requests.get",
        fake_get,
    )

    result = health_check(
        "http://localhost:8000"
    )

    assert result["status"] == "healthy"
    assert (
        result["service"]
        == "enterprise-autonomous-ai-analyst"
    )