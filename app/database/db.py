"""
Database layer.
Phase 1: SQLite with a small sample sales dataset (auto-seeded on first run).
Phase 3: point DATABASE_URL at Postgres and this file barely has to change,
         since we use SQLAlchemy's engine abstraction.
"""
import os
import pandas as pd
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

os.makedirs("data/sample", exist_ok=True)
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False}
                        if settings.DATABASE_URL.startswith("sqlite") else {})


def seed_sample_data():
    """Creates a `sales` table with fake data if it doesn't already exist.
    This lets you run the whole project immediately without hooking up
    a real company database first."""
    inspector = inspect(engine)
    if "sales" in inspector.get_table_names():
        logger.info("Sample data already present, skipping seed.")
        return

    logger.info("Seeding sample sales data...")
    regions = ["North India", "South India", "East India", "West India"]
    products = ["Laptop", "Mobile", "Tablet", "Headphones", "Smartwatch"]

    import random
    from datetime import date, timedelta

    random.seed(42)
    rows = []
    start = date(2024, 1, 1)
    for i in range(1500):
        d = start + timedelta(days=random.randint(0, 700))
        region = random.choice(regions)
        product = random.choice(products)
        # deliberately dip North India sales in one quarter, so there's a
        # real pattern for the agent to find and explain
        base_units = random.randint(1, 20)
        if region == "North India" and d.month in (10, 11, 12) and d.year == 2024:
            base_units = max(1, base_units - 8)
        price = {"Laptop": 55000, "Mobile": 18000, "Tablet": 22000,
                 "Headphones": 2500, "Smartwatch": 6000}[product]
        rows.append({
            "date": d.isoformat(),
            "region": region,
            "product": product,
            "units_sold": base_units,
            "revenue": base_units * price,
        })

    df = pd.DataFrame(rows)
    df.to_sql("sales", engine, if_exists="replace", index=False)
    logger.info(f"Seeded {len(df)} sales rows.")


def get_schema_description() -> str:
    """Returns a plain-text schema description the LLM can read to write SQL."""
    inspector = inspect(engine)
    lines = []
    for table_name in inspector.get_table_names():
        cols = inspector.get_columns(table_name)
        col_desc = ", ".join(f"{c['name']} ({c['type']})" for c in cols)
        lines.append(f"Table `{table_name}`: {col_desc}")
    return "\n".join(lines)


def run_sql(query: str) -> pd.DataFrame:
    """Executes a read-only SQL query and returns a DataFrame.
    Basic safety check: only SELECT statements are allowed."""
    cleaned = query.strip().rstrip(";")
    if not cleaned.lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed for safety.")
    with engine.connect() as conn:
        return pd.read_sql(text(cleaned), conn)