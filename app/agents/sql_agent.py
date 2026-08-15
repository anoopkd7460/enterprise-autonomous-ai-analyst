"""
Phase 1 core agent.

Flow:
  user question (Hindi/English, natural language)
        -> LLM writes a SQL query using the schema
        -> query runs against the database
        -> LLM explains the result in plain business language + a recommendation

This is intentionally a single agent right now. In Phase 2, `planner_agent.py`
will sit above this and decide whether to call this agent, the document
agent, or both — using LangGraph.
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


@dataclass
class SQLAgentResult:
    question: str
    sql_query: str
    data: pd.DataFrame
    explanation: str


def generate_sql(question: str) -> str:
    schema = get_schema_description()
    prompt = f"Schema:\n{schema}\n\nQuestion: {question}\n\nSQL query:"
    sql = chat(SQL_SYSTEM_PROMPT, prompt)
    sql = sql.replace("```sql", "").replace("```", "").strip()
    logger.info(f"Generated SQL: {sql}")
    return sql


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
    sql_query = generate_sql(question)
    data = run_sql(sql_query)
    explanation = explain_result(question, sql_query, data)
    return SQLAgentResult(
        question=question,
        sql_query=sql_query,
        data=data,
        explanation=explanation,
    )