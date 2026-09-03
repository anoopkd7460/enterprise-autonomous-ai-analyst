"""
Main Streamlit application for the Enterprise Autonomous AI Analyst.
"""

import streamlit as st

from components.sidebar import render_sidebar
from api_client import APIClientError, analyze
from components.answer_display import render_answer
from components.chart_display import render_chart
from components.question_input import render_question_input
from components.dataset_summary import render_dataset_summary
from components.upload import render_upload
from utils.config import get_api_url


st.set_page_config(
    page_title="Enterprise AI Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Run the Streamlit application."""

    api_url = get_api_url()

    render_sidebar(api_url)

    st.title("🤖 Enterprise Autonomous AI Analyst")

    st.caption("Natural-language analytics for business data")
    st.markdown(
        """
        Ask business questions about your datasets using
        natural language.
        """
    )

    st.divider()

    uploaded_file = render_upload()

    question = render_question_input()

    st.divider()

    analyze_clicked = st.button(
        "🔍 Analyze",
        type="primary",
        width="stretch",
    )

    if not analyze_clicked:
        return

    if not question:
        st.warning("Please enter a business question.")
        return

    with st.spinner("🤖 AI Analyst is analyzing your request..."):

        try:
            result = analyze(
                question=question,
                file=uploaded_file,
                api_url=api_url,
            )

        except APIClientError as exc:

            if exc.status_code == 400:
                st.error(
                    f"⚠️ Request error: {exc.message}"
                )

            elif exc.status_code == 503:
                st.error(
                    "🤖 The AI service is temporarily unavailable. "
                    "Please try again later."
                )

            elif exc.status_code == 504:
                st.error(
                    "⏱️ The analysis request timed out. "
                    "Please try again."
                )

            elif exc.status_code == 500:
                st.error(
                    "⚠️ The server encountered an unexpected error. "
                    "Please try again later."
                )

            else:
                st.error(
                    f"⚠️ {exc.message}"
                )

            return

    st.success("Analysis completed successfully.")

    render_dataset_summary(result.get("dataset_metadata"))

    render_answer(result.get("answer"))

    render_chart(result.get("chart"))


if __name__ == "__main__":
    main()