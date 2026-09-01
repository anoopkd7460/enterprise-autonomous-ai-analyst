"""
Central configuration for the application.

Reads configuration values from environment variables
and the .env file.
"""

import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    """Application configuration."""

    # ---------------------------------------------------------
    # LLM
    # ---------------------------------------------------------

    OPENAI_API_KEY: str = os.getenv(
        "GROQ_API_KEY",
        "",
    )

    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        "openai/gpt-oss-20b",
    )

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/sample/sales.db",
    )

    # ---------------------------------------------------------
    # Redis
    # ---------------------------------------------------------

    REDIS_ENABLED: bool = (
        os.getenv(
            "REDIS_ENABLED",
            "false",
        ).lower()
        == "true"
    )

    REDIS_HOST: str = os.getenv(
        "REDIS_HOST",
        "localhost",
    )

    REDIS_PORT: int = int(
        os.getenv(
            "REDIS_PORT",
            "6379",
        )
    )

    REDIS_CONNECT_TIMEOUT: float = float(
        os.getenv(
            "REDIS_CONNECT_TIMEOUT",
            "0.2",
        )
    )

    REDIS_SOCKET_TIMEOUT: float = float(
        os.getenv(
            "REDIS_SOCKET_TIMEOUT",
            "0.2",
        )
    )

    # ---------------------------------------------------------
    # Application
    # ---------------------------------------------------------

    APP_ENV: str = os.getenv(
        "APP_ENV",
        "development",
    )


settings = Settings()