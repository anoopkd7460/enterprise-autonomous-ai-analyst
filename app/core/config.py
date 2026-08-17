"""
Central configuration for the app.
Reads values from environment variables (.env file).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM
    OPENAI_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")

    # Database (Phase 1: SQLite, Phase 3: swap to Postgres via DATABASE_URL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/sample/sales.db")

    # App
    APP_ENV: str = os.getenv("APP_ENV", "development")


settings = Settings()