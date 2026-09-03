"""
Chart rendering component.
"""

from typing import Any

import plotly.graph_objects as go
import streamlit as st


def render_chart(chart: dict[str, Any] | None) -> None:
    """Render a Plotly chart returned by the API."""

    if not chart:
        return

    st.markdown("### 📊 Visualization")

    with st.container(border=True):
        try:
            figure = go.Figure(chart)

            st.plotly_chart(
                figure,
                width="stretch",
                config={
                    "displaylogo": False,
                    "responsive": True,
                },
            )

        except Exception as exc:
            st.warning(
                f"Unable to render visualization: {exc}"
            )