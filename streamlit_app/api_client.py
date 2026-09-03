"""
HTTP client for communicating with the FastAPI backend.

The Streamlit application uses this module instead of
making HTTP requests directly from UI components.
"""

from typing import BinaryIO, Any

import requests


DEFAULT_API_URL = "http://localhost:8000"


class APIClientError(Exception):
    """Raised when the FastAPI backend cannot process a request."""


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
            If the backend returns an HTTP error or
            an unexpected response.
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
            f"API request failed "
            f"(HTTP {response.status_code}): {detail}"
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

    Returns
    -------
    dict[str, Any]
        Health response from the backend.
    """

    url = f"{api_url.rstrip('/')}/api/v1/health"

    try:
        response = requests.get(
            url,
            timeout=5,
        )
    except requests.RequestException as exc:
        raise APIClientError(
            f"Unable to connect to the analyst API: {exc}"
        ) from exc

    if not response.ok:
        raise APIClientError(
            f"Health check failed (HTTP {response.status_code})."
        )

    try:
        return response.json()
    except ValueError as exc:
        raise APIClientError(
            "The analyst API returned invalid health-check JSON."
        ) from exc