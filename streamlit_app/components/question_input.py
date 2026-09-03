"""
Business question input component.
"""

import streamlit as st


def render_question_input() -> str:
    """Render the business question input."""

    st.subheader("💬 Ask the AI Analyst")

    st.caption(
        "Describe your business question in natural language."
    )

    question = st.text_area(
        "Business question",
        placeholder=(
            "Example: What are the top 5 products by revenue?"
        ),
        height=120,
        label_visibility="collapsed",
    )

    return question.strip()