"""
Configuration utilities for the Streamlit frontend.
"""

import os


DEFAULT_API_URL = "http://localhost:8000"


def get_api_url() -> str:
    """Return the FastAPI backend URL."""

    return os.getenv("ANALYST_API_URL", DEFAULT_API_URL)