
"""Test Phase 11 SQL evidence provenance checks."""

import pytest

from app.workflows.agent_adapters import (
    validate_sql_evidence,
)


def test_reject_fabricated_report_column():
    sql = """
    SELECT
        SUM(revenue) AS revenue,
        'Business report: No data available' AS report
    FROM sales
    WHERE region = 'North India';
    """

    with pytest.raises(
        ValueError,
        match="hardcoded text",
    ):
        validate_sql_evidence(sql)


def test_allow_real_revenue_query():
    sql = """
    SELECT SUM(revenue) AS revenue
    FROM sales
    WHERE region = 'North India'
      AND date BETWEEN '2024-10-01' AND '2024-12-31';
    """

    validate_sql_evidence(sql)


def test_allow_string_filter():
    sql = """
    SELECT product, SUM(revenue) AS total_revenue
    FROM sales
    WHERE region = 'North India'
    GROUP BY product;
    """

    validate_sql_evidence(sql)


def test_reject_hardcoded_reason():
    sql = """
    SELECT
        SUM(revenue) AS revenue,
        'Supply shortage' AS reason
    FROM sales;
    """

    with pytest.raises(ValueError):
        validate_sql_evidence(sql)


def test_reject_missing_sql():
    with pytest.raises(ValueError):
        validate_sql_evidence("")
