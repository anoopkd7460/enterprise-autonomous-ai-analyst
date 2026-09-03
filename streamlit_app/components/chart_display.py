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

            for trace in figure.data:
                if getattr(trace, "type", None) == "bar":
                    x_values = list(trace.x) if trace.x is not None else []

                    if x_values:
                        figure.update_xaxes(
                            type="category",
                            tickmode="array",
                            tickvals=x_values,
                            ticktext=x_values,
                            automargin=True,
                        )

            figure.update_layout(
                height=500,
                margin={
                    "l": 60,
                    "r": 30,
                    "t": 70,
                    "b": 80,
                },
            )

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