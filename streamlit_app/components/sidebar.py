"""
Sidebar component for the Streamlit application.
"""

import streamlit as st

from api_client import APIClientError, health_check


def render_sidebar(api_url: str) -> None:
    """Render the application sidebar."""

    with st.sidebar:

        st.title("🤖 AI Analyst")

        st.caption(
            "Enterprise Autonomous Data Analysis Platform"
        )

        st.divider()

        st.subheader("⚙️ Backend")

        try:
            health = health_check(api_url)

            if health.get("status") == "healthy":
                st.success("Backend connected")
            else:
                st.warning("Backend unhealthy")

            st.caption(
                f"Service: {health.get('service', 'Unknown')}"
            )

        except APIClientError:
            st.error("Backend unavailable")

        st.caption(
            f"Endpoint: {api_url}"
        )

        st.divider()

        st.subheader("📌 Capabilities")

        st.markdown(
            """
            - 📊 Dataset Analytics
            - 🗃️ SQL Analysis
            - 📄 Document Q&A
            - 🔎 RAG Search
            - 📈 Automated Visualization
            - 🤖 LLM-powered Insights
            """
        )

        st.divider()

        st.caption(
            "Enterprise Autonomous AI Analyst"
        )