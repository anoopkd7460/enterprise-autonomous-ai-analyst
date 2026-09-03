"""
HTTP client for communicating with the FastAPI backend.

The Streamlit application uses this module instead of
making HTTP requests directly from UI components.
"""

from typing import Any, BinaryIO

import requests


DEFAULT_API_URL = "http://localhost:8000"


class APIClientError(Exception):
    """
    Raised when the FastAPI backend cannot process a request.

    Attributes:
        message: User-facing error message.
        status_code: HTTP status code returned by the backend,
            if available.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code

        super().__init__(message)


def analyze(
    question: str,
    file: BinaryIO | None = None,
    api_url: str = DEFAULT_API_URL,
) -> dict[str, Any]:
    """
    Send an analysis request to the FastAPI backend.

    Args:
        question:
            Natural-language business question.

        file:
            Optional CSV/Excel file uploaded by the user.

        api_url:
            Base URL of the FastAPI backend.

    Returns:
        Parsed JSON response from the API.

    Raises:
        APIClientError:
            If the backend returns an HTTP error,
            cannot be reached, or returns invalid JSON.
    """

    url = f"{api_url.rstrip('/')}/api/v1/analyze"

    data = {
        "question": question,
    }

    files = None

    if file is not None:
        files = {
            "file": (
                getattr(file, "name", "dataset"),
                file,
            )
        }

    try:
        response = requests.post(
            url,
            data=data,
            files=files,
            timeout=120,
        )

    except requests.Timeout as exc:
        raise APIClientError(
            "The analysis request timed out. "
            "Please try again.",
            status_code=504,
        ) from exc

    except requests.RequestException as exc:
        raise APIClientError(
            f"Unable to connect to the analyst API: {exc}"
        ) from exc

    if not response.ok:
        try:
            detail = response.json().get(
                "detail",
                response.text,
            )

        except ValueError:
            detail = response.text

        raise APIClientError(
            str(detail),
            status_code=response.status_code,
        )

    try:
        result = response.json()

    except ValueError as exc:
        raise APIClientError(
            "The analyst API returned an invalid JSON response."
        ) from exc

    return result


def health_check(
    api_url: str = DEFAULT_API_URL,
) -> dict[str, Any]:
    """
    Check whether the FastAPI backend is healthy.

    Args:
        api_url:
            Base URL of the FastAPI backend.

    Returns:
        Parsed health response from the backend.

    Raises:
        APIClientError:
            If the backend cannot be reached,
            returns an HTTP error, or returns invalid JSON.
    """

    url = f"{api_url.rstrip('/')}/api/v1/health"

    try:
        response = requests.get(
            url,
            timeout=5,
        )

    except requests.Timeout as exc:
        raise APIClientError(
            "The backend health check timed out.",
            status_code=504,
        ) from exc

    except requests.RequestException as exc:
        raise APIClientError(
            f"Unable to connect to the analyst API: {exc}"
        ) from exc

    if not response.ok:
        raise APIClientError(
            f"Health check failed (HTTP {response.status_code}).",
            status_code=response.status_code,
        )

    try:
        return response.json()

    except ValueError as exc:
        raise APIClientError(
            "The analyst API returned invalid "
            "health-check JSON."
        ) from exc