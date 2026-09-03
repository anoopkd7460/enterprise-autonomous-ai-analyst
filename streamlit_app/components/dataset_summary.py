"""
Dataset metadata display component.
"""

from typing import Any

import streamlit as st


def render_dataset_summary(
    metadata: dict[str, Any] | None,
) -> None:
    """Render dataset metadata as KPI cards."""

    if not metadata:
        return

    st.subheader("📊 Dataset Overview")

    filename = metadata.get("filename")
    rows = metadata.get("rows")
    columns = metadata.get("columns")
    numeric_columns = metadata.get("numeric_columns")
    missing_values = metadata.get("missing_values")

    if filename:
        st.caption(f"Analyzed dataset: **{filename}**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Rows",
            f"{rows:,}" if rows is not None else "N/A",
        )

    with col2:
        st.metric(
            "Columns",
            f"{columns:,}" if columns is not None else "N/A",
        )

    with col3:
        st.metric(
            "Numeric Columns",
            (
                f"{numeric_columns:,}"
                if numeric_columns is not None
                else "N/A"
            ),
        )

    with col4:
        st.metric(
            "Missing Values",
            (
                f"{missing_values:,}"
                if missing_values is not None
                else "N/A"
            ),
        )