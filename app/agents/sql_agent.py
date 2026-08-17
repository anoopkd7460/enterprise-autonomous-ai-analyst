"""
Phase 1 core agent.

Flow:
  user question -> LLM writes SQL -> run it (retry+self-fix on error) ->
  LLM explains the result in plain business language + a recommendation
"""
from dataclasses import dataclass

import pandas as pd

from app.database.db import get_schema_description, run_sql
from app.llm.client import chat
from app.utils.logger import get_logger

logger = get_logger(__name__)

SQL_SYSTEM_PROMPT = """You are a senior data analyst. You convert business
questions into a single valid SQLite SELECT query.

Rules:
- Only output the SQL query, nothing else. No markdown, no explanation.
- Only use SELECT statements.
- Use the exact table and column names given in the schema.
- Always put a space between SQL keywords and identifiers (e.g. "THEN units_sold", never "THENunits_sold").
- If the question implies a time period (e.g. "last quarter"), infer reasonable
  date filters based on the data you have access to.
"""

EXPLAIN_SYSTEM_PROMPT = """You are a business analyst presenting findings to a
non-technical executive. Given a user's question, the SQL query that was run,
and the resulting data, write:
1. A direct answer to their question (2-3 sentences)
2. One concrete, actionable recommendation

Keep it concise and avoid technical jargon (no SQL/column talk).
"""

MAX_SQL_RETRIES = 2


@dataclass
class SQLAgentResult:
    question: str
    sql_query: str
    data: pd.DataFrame
    explanation: str


def _clean_sql(raw: str) -> str:
    return raw.replace("```sql", "").replace("```", "").strip()


def generate_sql(question: str) -> str:
    schema = get_schema_description()
    prompt = f"Schema:\n{schema}\n\nQuestion: {question}\n\nSQL query:"
    sql = _clean_sql(chat(SQL_SYSTEM_PROMPT, prompt))
    logger.info(f"Generated SQL: {sql}")
    return sql


def generate_sql_with_retry(question: str) -> tuple[str, pd.DataFrame]:
    """Generates SQL and runs it. If it fails (bad syntax, etc.), sends the
    error back to the LLM and asks it to fix the query — up to MAX_SQL_RETRIES times.
    This is a common agentic pattern: act -> observe failure -> self-correct."""
    schema = get_schema_description()
    sql = generate_sql(question)

    for attempt in range(MAX_SQL_RETRIES + 1):
        try:
            data = run_sql(sql)
            return sql, data
        except Exception as e:
            logger.warning(f"SQL failed (attempt {attempt + 1}): {e}")
            if attempt == MAX_SQL_RETRIES:
                raise
            fix_prompt = (
                f"Schema:\n{schema}\n\nQuestion: {question}\n\n"
                f"This SQL query failed:\n{sql}\n\n"
                f"Error: {e}\n\n"
                f"Fix the query. Only output the corrected SQL query, nothing else."
            )
            sql = _clean_sql(chat(SQL_SYSTEM_PROMPT, fix_prompt))
            logger.info(f"Retry SQL: {sql}")


def explain_result(question: str, sql_query: str, data: pd.DataFrame) -> str:
    preview = data.head(20).to_string(index=False)
    prompt = (
        f"Question: {question}\n\n"
        f"SQL used: {sql_query}\n\n"
        f"Result data (first 20 rows):\n{preview}\n\n"
        f"Total rows returned: {len(data)}"
    )
    return chat(EXPLAIN_SYSTEM_PROMPT, prompt)


def answer_question(question: str) -> SQLAgentResult:
    """Main entry point for the SQL agent."""
    sql_query, data = generate_sql_with_retry(question)
    explanation = explain_result(question, sql_query, data)
    return SQLAgentResult(
        question=question,
        sql_query=sql_query,
        data=data,
        explanation=explanation,
    )